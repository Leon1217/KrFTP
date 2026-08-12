from __future__ import annotations

import asyncio
import shlex
import threading

import asyncssh

from database.db_manager import DatabaseManager
from database.models import User
from utils.crypto import verify_password
from utils.zip_utils import create_zip, extract_zip


class KrSshServer(asyncssh.SSHServer):
    database_manager: DatabaseManager | None = None
    sessions = None

    def connection_made(self, conn):
        self.conn = conn
        peer = conn.get_extra_info("peername")
        self.client_ip = peer[0] if peer else ""

    def begin_auth(self, username):
        return True

    def password_auth_supported(self):
        return True

    def validate_password(self, username, password):
        db = self.database_manager
        if db.is_blocked_ip(self.client_ip):
            return False
        db.connect()
        try:
            user = User.get_or_none(User.username == username)
            root = db.protocol_root(username, "SFTP")
            valid = bool(user and root and user.is_active and not user.must_change_password and not db.is_expired(user) and verify_password(password, user.password_hash))
            db.audit(username, "SFTP", self.client_ip, "LOGIN", "", "SUCCESS" if valid else "FAIL")
            if valid:
                self.conn.set_extra_info(username=username)
                self._session_id = self.sessions.add(username, "SFTP", self.client_ip, self.conn.close)
            return valid
        finally:
            db.close()

    def connection_lost(self, exc):
        if hasattr(self, "_session_id"):
            self.sessions.remove(self._session_id)


class KrSftpServer(asyncssh.SFTPServer):
    database_manager: DatabaseManager | None = None

    def __init__(self, chan):
        self.username = chan.get_extra_info("username")
        root = self.database_manager.protocol_root(self.username, "SFTP") if self.username else None
        if not root:
            raise asyncssh.SFTPPermissionDenied("No SFTP root configured")
        self.permissions = set(__import__("json").loads(root.permissions))
        super().__init__(chan, chroot=str(root.root_path).encode())

    def _require(self, permission: str):
        if permission not in self.permissions:
            raise asyncssh.SFTPPermissionDenied("Permission denied")

    def open(self, path, pflags, attrs):
        if pflags & (asyncssh.FXF_WRITE | asyncssh.FXF_CREAT | asyncssh.FXF_TRUNC):
            self._require("write")
        elif pflags & asyncssh.FXF_APPEND:
            self._require("append")
        else:
            self._require("read")
        return super().open(path, pflags, attrs)

    def remove(self, path):
        self._require("delete_file")
        return super().remove(path)

    def mkdir(self, path, attrs):
        self._require("create_dir")
        return super().mkdir(path, attrs)

    def rmdir(self, path):
        self._require("delete_dir")
        return super().rmdir(path)

    def rename(self, oldpath, newpath):
        self._require("rename_file")
        return super().rename(oldpath, newpath)

    async def scandir(self, path):
        self._require("list")
        async for item in super().scandir(path):
            yield item


class SftpService:
    def __init__(self, db: DatabaseManager, sessions):
        self.db = db
        self.sessions = sessions
        self.loop: asyncio.AbstractEventLoop | None = None
        self.listener = None
        self.thread: threading.Thread | None = None
        self.error = ""

    @property
    def running(self) -> bool:
        return self.listener is not None

    def start(self, bind_ip: str, port: int) -> None:
        if self.running:
            return
        started = threading.Event()
        failure: list[Exception] = []

        def run():
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            KrSshServer.database_manager = self.db
            KrSshServer.sessions = self.sessions
            KrSftpServer.database_manager = self.db
            try:
                host_key = asyncssh.generate_private_key("ssh-rsa")
                self.listener = self.loop.run_until_complete(asyncssh.listen(bind_ip, port, server_factory=KrSshServer, server_host_keys=[host_key], sftp_factory=KrSftpServer, process_factory=self._archive_process))
            except Exception as exc:  # surfaced in the GUI service status
                failure.append(exc)
            finally:
                started.set()
            if not failure:
                self.loop.run_forever()
            self.loop.close()

        self.thread = threading.Thread(target=run, daemon=True, name="krftp-sftp")
        self.thread.start()
        started.wait(timeout=5)
        if failure:
            self.thread = None
            self.error = str(failure[0])
            raise RuntimeError(self.error)

    def _archive_process(self, process):
        username = process.get_extra_info("username")
        peer = process.get_extra_info("peername")
        client_ip = peer[0] if peer else ""
        try:
            args = shlex.split(process.command)
            if len(args) != 3 or args[0] not in {"krftp-zip", "krftp-unzip"}:
                raise ValueError("Usage: krftp-zip <source> <archive.zip> or krftp-unzip <archive.zip> <destination>")
            root = self.db.protocol_root(username, "SFTP")
            if not root:
                raise PermissionError("No SFTP root configured")
            permissions = set(__import__("json").loads(root.permissions))
            is_zip = args[0] == "krftp-zip"
            required = "compress" if is_zip else "decompress"
            if required not in permissions:
                raise PermissionError("Permission denied")
            if is_zip:
                create_zip(root.root_path, args[1], args[2])
                action = "COMPRESS"
            else:
                extract_zip(root.root_path, args[1], args[2])
                action = "DECOMPRESS"
            self.db.audit(username, "SFTP", client_ip, action, f"{args[1]} -> {args[2]}")
            process.stdout.write("OK\n")
            process.exit(0)
        except Exception as exc:
            self.db.audit(username or "", "SFTP", client_ip, "ARCHIVE", process.command, "FAIL", str(exc))
            process.stderr.write(f"ERROR: {exc}\n")
            process.exit(1)

    def stop(self) -> None:
        if self.loop and self.listener:
            async def close_listener():
                self.listener.close()
                await self.listener.wait_closed()
            asyncio.run_coroutine_threadsafe(close_listener(), self.loop).result(timeout=5)
            self.loop.call_soon_threadsafe(self.loop.stop)
        self.listener = None
        self.thread = None
