# 翻译资源

内置 locale：`zh_CN`、`en_US`、`zh_TW`、`ja_JP`、`ko_KR`、`es_ES`、`fr_FR`、`de_DE`、`pt_BR`、`ru_RU`。

将 Qt Linguist 编译后的翻译文件命名为 `krftp_<locale>.qm`。用户可在系统设置页导入该文件，程序会复制至 `i18n/custom/` 并提供该 locale 作为可选语言。

使用 Qt 5 工具编译内置翻译：

```powershell
./i18n/build_translations.ps1
```

编译脚本使用 `C:\Qt5Tools\bin\lrelease.exe`，会为每个 `krftp_*.ts` 文件生成同名 `.qm` 文件。
