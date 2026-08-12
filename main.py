from __future__ import annotations

import sys

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from config import APP_NAME, BASE_DIR, DATABASE_PATH, ICON_PATH
from database import DatabaseManager
from i18n import LanguageManager
from resource import krftp_rc  # Registers :/images/logo.ico.
from servers import ServiceManager
from ui.login_dialog import LoginDialog
from ui.main_window import MainWindow


def main() -> int:
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    app.setApplicationName(APP_NAME)
    icon = QIcon(":/images/logo.ico")
    if icon.isNull():
        icon = QIcon(str(ICON_PATH))
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
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
