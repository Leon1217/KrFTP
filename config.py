from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "krftp.sqlite3"
RESOURCE_DIR = BASE_DIR / "resource"
ICON_PATH = RESOURCE_DIR / "images" / "logo.ico"
APP_NAME = "krFTP Server Manager"

DEFAULT_SETTINGS = {
    "bind_ip": "0.0.0.0",
    "ftp_port": "21",
    "sftp_port": "22",
    "auto_start_services": "true",
    "auto_start_ftp": "true",
    "auto_start_sftp": "true",
    "language": "zh_CN",
}
