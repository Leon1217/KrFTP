from __future__ import annotations

import sys

from PySide6.QtCore import QSharedMemory
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config import APP_NAME, BASE_DIR, DATABASE_PATH, ICON_PATH
from database import DatabaseManager
from i18n import LanguageManager
from resource import krftp_rc  # Registers :/images/logo.ico.
from servers import ServiceManager
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow

INSTANCE_KEY = "krFTP.ServerManager.SingleInstance"


def acquire_instance_lock() -> QSharedMemory | None:
    """Create the process-wide lock, reclaiming a stale lock after a crash."""
    lock = QSharedMemory(INSTANCE_KEY)
    if lock.create(1):
        return lock
    if lock.attach():
        lock.detach()
        if lock.create(1):
            return lock
    return None


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    instance_lock = acquire_instance_lock()
    if instance_lock is None:
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(None, "krFTP", "krFTP 已在运行，不能重复启动。")
        return 0
    # Prefer the physical .ico file. It is reliable for the Windows tray in
    # both source runs and the frozen distribution; the Qt resource remains a fallback.
    icon = QIcon(str(ICON_PATH))
    if icon.isNull():
        icon = QIcon(":/images/logo.ico")
    if icon.isNull():
        from PySide6.QtWidgets import QMessageBox

        QMessageBox.critical(None, "krFTP", "无法加载程序图标，程序无法启动。")
        return 1
    app.setWindowIcon(icon)

    db = DatabaseManager(DATABASE_PATH)
    db.initialize()
    languages = LanguageManager(BASE_DIR / "i18n")
    languages.apply(db.settings().get("language", "zh_CN"))
    login = LoginDialog(db, languages)
    login.setWindowIcon(icon)
    if login.exec() != LoginDialog.Accepted:
        return 0
    window = MainWindow(db, ServiceManager(db), login.user, icon, languages)
    app.aboutToQuit.connect(window.shutdown)
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
