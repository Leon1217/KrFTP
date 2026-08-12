from __future__ import annotations

import ipaddress
import json
from datetime import datetime
from pathlib import Path
from typing import Iterable

from config import DEFAULT_SETTINGS
from database.models import AuditLog, IpRule, Setting, SystemUser, User, UserRoot, database
from utils.crypto import hash_password, verify_password

ALL_PERMISSIONS = {
    "list", "read", "write", "append", "delete_file", "rename_file",
    "create_dir", "delete_dir", "rename_dir", "compress", "decompress",
}


class DatabaseManager:
    def __init__(self, database_path: Path):
        self.database_path = Path(database_path)

    def initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        database.init(str(self.database_path))
        database.connect(reuse_if_open=True)
        database.create_tables([SystemUser, User, UserRoot, IpRule, AuditLog, Setting], safe=True)
        with database.atomic():
            for key, value in DEFAULT_SETTINGS.items():
                Setting.get_or_create(key=key, defaults={"value": value})
            if not SystemUser.select().exists():
                SystemUser.create(
                    username="admin",
                    password_hash=hash_password("admin123"),
                    must_change_password=True,
                )
            # Earlier builds stored the console's untouched bootstrap account
            # in the transfer-user table. It has no service roots and is safe
            # to remove once the dedicated SystemUser table exists.
            legacy_admin = User.get_or_none((User.username == "admin") & (User.must_change_password == True))
            if legacy_admin and not UserRoot.select().where(UserRoot.user == legacy_admin).exists():
                legacy_admin.delete_instance(recursive=True)
        self.close()

    def connect(self) -> None:
        database.connect(reuse_if_open=True)

    def close(self) -> None:
        if not database.is_closed():
            database.close()

    def authenticate_admin(self, username: str, password: str) -> SystemUser | None:
        self.connect()
        try:
            user = SystemUser.get_or_none(SystemUser.username == username)
            if not user or not user.is_active or not verify_password(password, user.password_hash):
                self.audit(username, "LOCAL", "127.0.0.1", "LOGIN", "", "FAIL")
                return None
            self.audit(username, "LOCAL", "127.0.0.1", "LOGIN", "", "SUCCESS")
            return user
        finally:
            self.close()

    @staticmethod
    def is_expired(user: User) -> bool:
        return user.expires_at is not None and user.expires_at <= datetime.now()

    def is_user_current(self, username: str) -> bool:
        self.connect()
        try:
            user = User.get_or_none(User.username == username)
            return bool(user and user.is_active and not user.must_change_password and not self.is_expired(user))
        finally:
            self.close()

    def change_system_password(self, user_id: int, password: str) -> None:
        self.connect()
        try:
            SystemUser.update(password_hash=hash_password(password), must_change_password=False, updated_at=datetime.now()).where(SystemUser.id == user_id).execute()
        finally:
            self.close()

    def update_system_account(self, user_id: int, username: str, password: str | None = None) -> SystemUser:
        username = username.strip()
        if not username:
            raise ValueError("系统账号不能为空")
        self.connect()
        try:
            values = {SystemUser.username: username, SystemUser.updated_at: datetime.now()}
            if password:
                if len(password) < 8:
                    raise ValueError("密码至少 8 个字符")
                values[SystemUser.password_hash] = hash_password(password)
                values[SystemUser.must_change_password] = False
            SystemUser.update(values).where(SystemUser.id == user_id).execute()
            return SystemUser.get_by_id(user_id)
        finally:
            self.close()

    def users(self) -> list[User]:
        self.connect()
        try:
            return list(User.select().order_by(User.username))
        finally:
            self.close()

    def create_user(self, username: str, password: str, expires_at: datetime | None = None) -> User:
        self.connect()
        try:
            if SystemUser.select().where(SystemUser.username == username).exists():
                raise ValueError("服务用户名不能与系统账户相同")
            return User.create(username=username, password_hash=hash_password(password), expires_at=expires_at)
        finally:
            self.close()

    def set_user_active(self, user_id: int, active: bool) -> None:
        self.connect()
        try:
            User.update(is_active=active, updated_at=datetime.now()).where(User.id == user_id).execute()
        finally:
            self.close()

    def change_service_user_password(self, user_id: int, password: str) -> None:
        if len(password) < 8:
            raise ValueError("密码至少 8 个字符")
        self.connect()
        try:
            User.update(password_hash=hash_password(password), updated_at=datetime.now()).where(User.id == user_id).execute()
        finally:
            self.close()

    def delete_user(self, user_id: int) -> None:
        self.connect()
        try:
            user = User.get_by_id(user_id)
            user.delete_instance(recursive=True)
        finally:
            self.close()

    def user_roots(self, user_id: int) -> list[UserRoot]:
        self.connect()
        try:
            return list(UserRoot.select().where(UserRoot.user == user_id))
        finally:
            self.close()

    def protocol_root(self, username: str, protocol: str) -> UserRoot | None:
        self.connect()
        try:
            user = User.get_or_none(User.username == username)
            if not user:
                return None
            return UserRoot.get_or_none((UserRoot.user == user) & ((UserRoot.protocol == protocol) | (UserRoot.protocol == "BOTH")))
        finally:
            self.close()

    def save_root(self, user_id: int, protocol: str, root_path: str, permissions: Iterable[str]) -> UserRoot:
        normalized = sorted(set(permissions) & ALL_PERMISSIONS)
        self.connect()
        try:
            root, _ = UserRoot.get_or_create(user=user_id, protocol=protocol, root_path=str(Path(root_path).resolve()))
            root.permissions = json.dumps(normalized)
            root.save()
            return root
        finally:
            self.close()

    def permissions_for(self, username: str, protocol: str, path: str) -> tuple[str, set[str]] | None:
        self.connect()
        try:
            user = User.get_or_none(User.username == username)
            if not user or not user.is_active or self.is_expired(user):
                return None
            roots = UserRoot.select().where((UserRoot.user == user) & ((UserRoot.protocol == protocol) | (UserRoot.protocol == "BOTH")))
            requested = Path(path).resolve()
            for root in roots:
                root_path = Path(root.root_path).resolve()
                try:
                    requested.relative_to(root_path)
                    return str(root_path), set(json.loads(root.permissions))
                except ValueError:
                    continue
            return None
        finally:
            self.close()

    def settings(self) -> dict[str, str]:
        self.connect()
        try:
            return {item.key: item.value for item in Setting.select()}
        finally:
            self.close()

    def update_settings(self, values: dict[str, str]) -> None:
        self.connect()
        try:
            with database.atomic():
                for key, value in values.items():
                    Setting.insert(key=key, value=str(value), updated_at=datetime.now()).on_conflict(
                        conflict_target=[Setting.key], update={Setting.value: str(value), Setting.updated_at: datetime.now()}
                    ).execute()
        finally:
            self.close()

    def ip_rules(self) -> list[IpRule]:
        self.connect()
        try:
            return list(IpRule.select().order_by(IpRule.created_at.desc()))
        finally:
            self.close()

    def add_ip_rule(self, network: str, reason: str = "") -> None:
        normalized = str(ipaddress.ip_network(network, strict=False))
        self.connect()
        try:
            IpRule.insert(network=normalized, reason=reason).on_conflict_replace().execute()
        finally:
            self.close()

    def is_blocked_ip(self, ip: str) -> bool:
        address = ipaddress.ip_address(ip)
        self.connect()
        try:
            return any(address in ipaddress.ip_network(rule.network) for rule in IpRule.select())
        finally:
            self.close()

    def audit(self, username: str, protocol: str, client_ip: str, action: str, path: str, result: str = "SUCCESS", detail: str = "") -> None:
        AuditLog.create(username=username, protocol=protocol, client_ip=client_ip, action=action, path=path, result=result, detail=detail)

    def audit_logs(
        self, username: str = "", client_ip: str = "", protocol: str = "", action: str = "",
        start_at: datetime | None = None, end_at: datetime | None = None, page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[AuditLog], int]:
        self.connect()
        try:
            query = AuditLog.select()
            if username:
                query = query.where(AuditLog.username == username)
            if client_ip:
                query = query.where(AuditLog.client_ip.contains(client_ip))
            if protocol:
                query = query.where(AuditLog.protocol == protocol)
            if action:
                query = query.where(AuditLog.action == action)
            if start_at:
                query = query.where(AuditLog.occurred_at >= start_at)
            if end_at:
                query = query.where(AuditLog.occurred_at <= end_at)
            total = query.count()
            page = max(1, page)
            page_size = max(1, page_size)
            return list(query.order_by(AuditLog.occurred_at.desc()).paginate(page, page_size)), total
        finally:
            self.close()

    def audit_filter_values(self) -> tuple[list[str], list[str], list[str]]:
        self.connect()
        try:
            usernames = [row.username for row in AuditLog.select(AuditLog.username).distinct().order_by(AuditLog.username) if row.username]
            protocols = [row.protocol for row in AuditLog.select(AuditLog.protocol).distinct().order_by(AuditLog.protocol) if row.protocol]
            actions = [row.action for row in AuditLog.select(AuditLog.action).distinct().order_by(AuditLog.action) if row.action]
            return usernames, protocols, actions
        finally:
            self.close()
