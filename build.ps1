param(
    [string]$Python = "python"
)

$ErrorActionPreference = "Stop"

& $Python -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --name "krFTP" `
    --icon "resource/images/logo.ico" `
    --add-data "i18n/*.qm;i18n" `
    --add-data "LICENSE;." `
    --add-data "NOTICE.txt;." `
    --collect-all asyncssh `
    --collect-all pyftpdlib `
    --collect-all argon2 `
    main.py

Copy-Item "README.md" "dist/krFTP/README.md" -Force
Copy-Item "LICENSE" "dist/krFTP/LICENSE" -Force
Copy-Item "NOTICE.txt" "dist/krFTP/NOTICE.txt" -Force
New-Item -ItemType Directory -Path "dist/krFTP/i18n" -Force | Out-Null
Copy-Item "i18n/*.qm" "dist/krFTP/i18n" -Force
Write-Host "Package created: dist/krFTP/krFTP.exe"
