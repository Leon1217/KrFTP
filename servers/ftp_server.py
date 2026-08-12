from __future__ import annotations

import threading
from pathlib import Path

from pyftpdlib.authorizers import AuthenticationFailed, DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from database.db_manager import DatabaseManager
from database.models import User, UserRoot
from utils.crypto import verify_password
from utils.zip_utils import create_zip, extract_zip


class DatabaseAuthorizer(DummyAuthorizer):
    def __init__(self, db: DatabaseManager):
        self.db = db

    def validate_authentication(self, username, password, handler):
        if self.db.is_blocked_ip(handler.remote_ip):
            raise AuthenticationFailed("IP is blocked")
        self.db.connect()
        try:
            user = User.get_or_none(User.username == username)
            if not user or not user.is_active or user.must_change_password or self.db.is_expired(user) or not verify_password(password, user.password_hash):
                self.db.audit(username, "FTP", handler.remote_ip, "LOGIN", "", "FAIL")
                raise AuthenticationFailed("Invalid credentials")
        finally:
            self.db.close()

    def has_user(self, username):
        self.db.connect()
        try:
            return User.select().where(User.username == username).exists()
        finally:
            self.db.close()

    def _root(self, username):
        self.db.connect()
        try:
            user = User.get(User.username == username)
            root = UserRoot.get_or_none((UserRoot.user == user) & ((UserRoot.protocol == "FTP") | (UserRoot.protocol == "BOTH")))
            if not root:
                raise AuthenticationFailed("No FTP root configured")
            return root
        finally:
            self.db.close()

    def get_home_dir(self, username):
        return self._root(username).root_path

    def get_perms(self, username):
        permissions = set(__import__("json").loads(self._root(username).permissions))
        mapping = {"list": "el", "read": "r", "write": "w", "append": "a", "delete_file": "d", "rename_file": "f", "create_dir": "m", "delete_dir": "R", "rename_dir": "f"}
        return "".join(value for key, value in mapping.items() if key in permissions)

    def has_perm(self, username, perm, path=None):
        """pyftpdlib calls this for every filesystem command.

        DummyAuthorizer's implementation looks up an in-memory user_table,
        while krFTP stores permissions in SQLite.
        """
        return perm in self.get_perms(username)

    def get_msg_login(self, username):
        return "krFTP login successful."

    def get_msg_quit(self, username):
        return "Goodbye."

    def impersonate_user(self, username, password):
        return None

    def terminate_impersonation(self, username):
        return None


class KrFTPHandler(FTPHandler):
    db: DatabaseManager | None = None
    sessions = None
    proto_cmds = FTPHandler.proto_cmds.copy()
    proto_cmds.update({
        "SITE ZIP": {"perm": None, "auth": True, "arg": True, "help": "Syntax: SITE ZIP <source> <archive.zip>"},
        "SITE UNZIP": {"perm": None, "auth": True, "arg": True, "help": "Syntax: SITE UNZIP <archive.zip> <destination>"},
    })

    def on_login(self, username):
        self._session_id = self.sessions.add(username, "FTP", self.remote_ip, self.close_when_done)
        self.db.audit(username, "FTP", self.remote_ip, "LOGIN", "", "SUCCESS")

    def on_logout(self, username):
        if hasattr(self, "_session_id"):
            self.sessions.remove(self._session_id)

    def _audit(self, action, path, result="SUCCESS"):
        self.db.audit(getattr(self, "username", ""), "FTP", self.remote_ip, action, path, result)

    def on_file_received(self, file): self._audit("UPLOAD", file)
    def on_file_sent(self, file): self._audit("DOWNLOAD", file)
    def on_file_deleted(self, path): self._audit("DELETE", path)
    def on_file_renamed(self, src, dst): self._audit("RENAME", f"{src} -> {dst}")

    def _archive_paths(self, argument, permission):
        if " " not in argument:
            self.respond("501 Command requires source and destination paths.")
            return None
        source, destination = argument.split(" ", 1)
        root = self.authorizer._root(self.username)
        permissions = set(__import__("json").loads(root.permissions))
        if permission not in permissions:
            self.respond("550 Not enough privileges.")
            self._audit(permission.upper(), argument, "FAIL")
            return None
        source_path = self.fs.ftp2fs(source)
        destination_path = self.fs.ftp2fs(destination)
        if not self.fs.validpath(source_path) or not self.fs.validpath(destination_path):
            self.respond("550 Path is outside the authorized root.")
            return None
        return root.root_path, source_path, destination_path

    def ftp_SITE_ZIP(self, argument):
        paths = self._archive_paths(argument, "compress")
        if not paths:
            return
        try:
            _, source, archive = paths
            create_zip(paths[0], source, archive)
            self._audit("COMPRESS", argument)
            self.respond("200 Archive created.")
        except Exception as exc:
            self._audit("COMPRESS", argument, "FAIL")
            self.respond(f"550 Compression failed: {exc}")

    def ftp_SITE_UNZIP(self, argument):
        paths = self._archive_paths(argument, "decompress")
        if not paths:
            return
        try:
            _, archive, destination = paths
            extract_zip(paths[0], archive, destination)
            self._audit("DECOMPRESS", argument)
            self.respond("200 Archive extracted.")
        except Exception as exc:
            self._audit("DECOMPRESS", argument, "FAIL")
            self.respond(f"550 Extraction failed: {exc}")


class FtpService:
    def __init__(self, db: DatabaseManager, sessions):
        self.db = db
        self.sessions = sessions
        self.server: FTPServer | None = None
        self.thread: threading.Thread | None = None
        self.error = ""

    @property
    def running(self) -> bool:
        return self.server is not None

    def start(self, bind_ip: str, port: int) -> None:
        if self.running:
            return
        handler = KrFTPHandler
        handler.authorizer = DatabaseAuthorizer(self.db)
        handler.db = self.db
        handler.sessions = self.sessions
        self.server = FTPServer((bind_ip, port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"timeout": 0.5, "blocking": True}, daemon=True, name="krftp-ftp")
        self.thread.start()

    def stop(self) -> None:
        server, thread = self.server, self.thread
        if server:
            server.close_all()
        if thread and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=3)
        self.server = None
        self.thread = None
