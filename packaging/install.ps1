<#
.SYNOPSIS
  Simple portable installer for an already-built REALM OS (no Inno Setup needed).
.DESCRIPTION
  Copies a PyInstaller one-folder build (dist\REALM OS) to a per-user
  location and creates Start Menu + Desktop shortcuts. No admin needed.
.EXAMPLE
  .\packaging\install.ps1 -Source ".\dist\REALM OS"
#>
param(
    [string]$Source = (Join-Path (Split-Path -Parent $PSScriptRoot) "dist\REALM OS"),
    [string]$InstallDir = (Join-Path $env:LOCALAPPDATA "Programs\REALM OS"),
    [switch]$DesktopShortcut = $true
)
$ErrorActionPreference = "Stop"

if (-not (Test-Path $Source)) { throw "Build not found at '$Source'. Run .\scripts\build-windows.ps1 first." }
$exe = Join-Path $Source "REALM OS.exe"
if (-not (Test-Path $exe)) { throw "Executable not found: $exe" }

Write-Host "Installing REALM OS to $InstallDir ..."
New-Item -ItemType Directory -Path $InstallDir -Force | Out-Null
Copy-Item -Path (Join-Path $Source "*") -Destination $InstallDir -Recurse -Force

$installedExe = Join-Path $InstallDir "REALM OS.exe"
$wsh = New-Object -ComObject WScript.Shell

$startMenu = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\REALM OS.lnk"
$lnk = $wsh.CreateShortcut($startMenu)
$lnk.TargetPath = $installedExe
$lnk.WorkingDirectory = $InstallDir
$lnk.IconLocation = "$installedExe,0"
$lnk.Description = "REALM OS"
$lnk.Save()

if ($DesktopShortcut) {
    $desk = $wsh.CreateShortcut((Join-Path ([Environment]::GetFolderPath("Desktop")) "REALM OS.lnk"))
    $desk.TargetPath = $installedExe
    $desk.WorkingDirectory = $InstallDir
    $desk.IconLocation = "$installedExe,0"
    $desk.Save()
}

# uninstaller convenience script
@"
@echo off
rmdir /s /q "$InstallDir"
del "%APPDATA%\Microsoft\Windows\Start Menu\Programs\REALM OS.lnk"
del "%USERPROFILE%\Desktop\REALM OS.lnk"
echo REALM OS uninstalled. Your data in %LOCALAPPDATA%\REALM OS was NOT removed.
"@ | Set-Content -Path (Join-Path $InstallDir "uninstall.bat") -Encoding ASCII

Write-Host "Installed. Launch 'REALM OS'. Uninstall via uninstall.bat or Windows 'Apps'."
