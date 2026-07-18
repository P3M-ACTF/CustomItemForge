# Build CustomItemForge release bundle into dist/
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root

python scripts/build_release.py @args
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host ""
Write-Host "Tip: zip dist/ for distribution, or copy the whole dist folder to users." -ForegroundColor Cyan
