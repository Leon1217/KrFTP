from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import RLock
from uuid import uuid4


@dataclass(frozen=True)
class Session:
    session_id: str
    username: str
    protocol: str
    client_ip: str
    connected_at: datetime
    close_callback: Callable[[], None] | None = field(default=None, repr=False, compare=False)


class SessionManager:
    def __init__(self) -> None:
        self._sessions: dict[str, Session] = {}
        self._lock = RLock()

    def add(self, username: str, protocol: str, client_ip: str, close_callback: Callable[[], None] | None = None) -> str:
        session_id = str(uuid4())
        session = Session(session_id, username, protocol, client_ip, datetime.now(), close_callback)
        with self._lock:
            self._sessions[session_id] = session
        return session_id

    def remove(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def snapshot(self) -> list[Session]:
        with self._lock:
            return list(self._sessions.values())

    def count(self) -> int:
        with self._lock:
            return len(self._sessions)

    def disconnect(self, session_id: str) -> bool:
        with self._lock:
            session = self._sessions.pop(session_id, None)
        if not session:
            return False
        if session.close_callback:
            session.close_callback()
        return True
