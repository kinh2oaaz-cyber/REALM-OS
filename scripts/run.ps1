<# Run REALM OS (real window, NOT offscreen). Clears stale caches; ensures Qt renders normally. #>
param([switch]$ResetTheme, [switch]$ClearData, [switch]$Reinstall)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

# CRITICAL: make sure offscreen rendering is NOT set in this shell.
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
$env:QT_QPA_PLATFORM = "windows"

# clear stale bytecode caches so updated code is always loaded
Get-ChildItem -Path $root -Recurse -Filter "__pycache__" -Directory -ErrorAction SilentlyContinue |
    Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

if ($Reinstall) { python -m pip install -r requirements.txt }

if ($ResetTheme) {
    python -c "import sys; sys.path.insert(0,r'$root'); from database import Database; from core.config import database_path; d=Database(database_path()); d.initialize(); [d.execute('DELETE FROM settings WHERE key=?',(k,)) for k in ('appearance.theme','appearance.accent','appearance.font_family','appearance.font_size','appearance.reduce_motion')]; d.close(); print('theme reset to redgold defaults')"
}

if ($ClearData) {
    $data = Join-Path $env:LOCALAPPDATA "REALM OS"
    if (Test-Path $data) { Remove-Item -Recurse -Force $data; Write-Host "cleared data dir: $data" }
}

python main.py
