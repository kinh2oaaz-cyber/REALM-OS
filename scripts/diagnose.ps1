<# Diagnose REALM OS runtime: platform, Qt, theme, DB, caches. #>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
Remove-Item Env:QT_QPA_PLATFORM -ErrorAction SilentlyContinue
python -c @"
import sys, os
sys.path.insert(0, r'$root')
import PySide6
print('python', sys.version.split()[0])
print('PySide6', PySide6.__version__)
print('QT_QPA_PLATFORM', os.environ.get('QT_QPA_PLATFORM'))
print('Qt style hints check...')
from PySide6.QtWidgets import QApplication
app = QApplication.instance() or QApplication([])
print('qt version', app.libraryPaths())
from app.application import RealmOSApplication
"@
python -m compileall -q . ; Write-Host "compileall OK"
python -m unittest discover -s tests -t . 2>`$null; Write-Host "tests exit: `$LASTEXITCODE"
