# Build CustomItemForge release bundle and optional zip
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python scripts/build_release.py @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

if ($args -notcontains "--zip") {
    Write-Host ""
    Write-Host "Tip: add --zip to create dist/CustomItemForge-<version>.zip for GitHub Releases." -ForegroundColor Cyan
}
