$ErrorActionPreference = 'Stop'
$tool = 'C:\Qt5Tools\bin\lrelease.exe'

if (-not (Test-Path $tool)) {
    throw "Qt lrelease was not found: $tool"
}

Get-ChildItem -Path $PSScriptRoot -Filter 'krftp_*.ts' | ForEach-Object {
    & $tool $_.FullName
    if ($LASTEXITCODE -ne 0) { throw "Failed to compile $($_.Name)" }
}
