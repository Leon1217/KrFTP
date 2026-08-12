from __future__ import annotations

from database.db_manager import DatabaseManager
from .ftp_server import FtpService
from .session_manager import SessionManager
from .sftp_server import SftpService


class ServiceManager:
    def __init__(self, db: DatabaseManager):
        self.db = db
        self.sessions = SessionManager()
        self.ftp = FtpService(db, self.sessions)
        self.sftp = SftpService(db, self.sessions)

    def start_configured(self) -> dict[str, str]:
        settings = self.db.settings()
        results = {}
        for name, service, port_key, auto_key in (("FTP", self.ftp, "ftp_port", "auto_start_ftp"), ("SFTP", self.sftp, "sftp_port", "auto_start_sftp")):
            if settings.get(auto_key, settings.get("auto_start_services", "true")) != "true":
                results[name] = "STOPPED"
                continue
            try:
                service.start(settings["bind_ip"], int(settings[port_key]))
                results[name] = "RUNNING"
            except Exception as exc:
                results[name] = f"FAILED: {exc}"
        return results

    def start_service(self, name: str) -> str:
        settings = self.db.settings()
        service, port_key = (self.ftp, "ftp_port") if name == "FTP" else (self.sftp, "sftp_port")
        try:
            service.start(settings["bind_ip"], int(settings[port_key]))
            return "RUNNING"
        except Exception as exc:
            return f"FAILED: {exc}"

    def stop_service(self, name: str) -> None:
        (self.ftp if name == "FTP" else self.sftp).stop()

    def stop_all(self) -> None:
        self.ftp.stop()
        self.sftp.stop()

    def disconnect(self, session_id: str) -> bool:
        return self.sessions.disconnect(session_id)

    def disconnect_user(self, username: str) -> int:
        disconnected = 0
        for session in self.sessions.snapshot():
            if session.username == username:
                disconnected += int(self.disconnect(session.session_id))
        return disconnected

    def enforce_access_rules(self) -> int:
        disconnected = 0
        for session in self.sessions.snapshot():
            if not self.db.is_user_current(session.username) or self.db.is_blocked_ip(session.client_ip):
                disconnected += int(self.disconnect(session.session_id))
        return disconnected
