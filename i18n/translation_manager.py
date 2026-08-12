from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QTranslator

SUPPORTED_LOCALES = (
    "zh_CN", "en_US", "zh_TW", "ja_JP", "ko_KR",
    "es_ES", "fr_FR", "de_DE", "pt_BR", "ru_RU",
)

LANGUAGE_NAMES = {
    "zh_CN": "简体中文", "en_US": "English", "zh_TW": "繁體中文", "ja_JP": "日本語",
    "ko_KR": "한국어", "es_ES": "Español", "fr_FR": "Français", "de_DE": "Deutsch",
    "pt_BR": "Português (Brasil)", "ru_RU": "Русский",
}


class LanguageManager:
    def __init__(self, translations_dir: Path):
        self.translations_dir = Path(translations_dir)
        self.custom_dir = self.translations_dir / "custom"
        self.custom_dir.mkdir(parents=True, exist_ok=True)
        self.translator = QTranslator()

    def available_locales(self) -> list[str]:
        custom = sorted(path.stem.removeprefix("krftp_") for path in self.custom_dir.glob("krftp_*.qm"))
        return list(SUPPORTED_LOCALES) + [locale for locale in custom if locale not in SUPPORTED_LOCALES]

    def display_name(self, locale: str) -> str:
        return LANGUAGE_NAMES.get(locale, locale)

    def apply(self, locale: str) -> bool:
        QCoreApplication.removeTranslator(self.translator)
        self.translator = QTranslator()
        candidates = [self.custom_dir / f"krftp_{locale}.qm", self.translations_dir / f"krftp_{locale}.qm"]
        for candidate in candidates:
            if candidate.exists() and self.translator.load(str(candidate)):
                QCoreApplication.installTranslator(self.translator)
                return True
        return locale == "zh_CN"

    def import_catalog(self, source: str) -> str:
        path = Path(source)
        if path.suffix.lower() != ".qm" or not path.is_file():
            raise ValueError("请选择有效的 Qt .qm 翻译文件。")
        locale = path.stem.removeprefix("krftp_")
        if not locale or locale == path.stem:
            raise ValueError("翻译文件名称必须为 krftp_<locale>.qm。")
        target = self.custom_dir / f"krftp_{locale}.qm"
        shutil.copy2(path, target)
        return locale
