<#
.SYNOPSIS
  Build REALM OS Windows executable + installer.
.DESCRIPTION
  1) PyInstaller one-folder -> dist\REALM OS\REALM OS.exe
  2) (optional) PyInstaller one-file  -> dist\REALM OS.exe
  3) (optional) Inno Setup installer  -> dist\REALM OS Setup.exe  (if ISCC found)
.EXAMPLE
  .\scripts\build-windows.ps1
  .\scripts\build-windows.ps1 -OneFile -NoInstaller

param([switch]$OneFile, [switch]$NoInstaller, [switch]$Clean)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

python -m pip install pyinstaller pillow

if ($Clean) { Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue; Write-Host "cleaned build/ dist/" }

# ensure .ico from logo
python -c "from PIL import Image; im=Image.open(r'$root\REALM OS LOGO.png').convert('RGBA'); im.save(r'$root\assets\REALM OS LOGO.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"

# 1) one-folder (reliable Qt bundling)
Write-Host "== PyInstaller one-folder =="
python -m PyInstaller packaging\realmos.spec --noconfirm

# 2) one-file (single .exe)
if ($OneFile) {
    Write-Host "== PyInstaller one-file =="
    python -m PyInstaller packaging\realmos-onefile.spec --noconfirm
}

# 3) Inno Setup installer
if (-not $NoInstaller) {
    $iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
    if (-not $iscc) {
        foreach ($cand in @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe",
                            "${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe",
                            "$env:ProgramFiles\Inno Setup 6\ISCC.exe")) {
            if (Test-Path $cand) { $iscc = Get-Item $cand; break }
        }
    }
    if ($iscc) {
        Write-Host "== Inno Setup installer =="
        & $iscc.FullName packaging\inno\realmos.iss
    } else {
        Write-Warning "Inno Setup (ISCC.exe) not found. PyInstaller output is in dist\. Use packaging\install.ps1 OR install Inno Setup 6 then re-run. See docs\PACKAGING.md."
    }
}

Write-Host "`nDONE. dist\ contains REALM OS.exe / REALM OS\ / (REALM OS.exe one-file) / REALM OS Setup.exe if Inno ran."
