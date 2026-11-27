<# Build only the installer from an existing PyInstaller one-folder build. #>
param([string]$Dist = (Join-Path (Split-Path -Parent $PSScriptRoot) "dist\REALM OS"))
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
if (-not (Test-Path (Join-Path $Dist "REALM OS.exe"))) {
    Write-Host "Building PyInstaller one-folder first..."
    python -m PyInstaller packaging\realmos.spec --noconfirm
}
$iscc = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if (-not $iscc) {
    foreach ($cand in @("$env:LOCALAPPDATA\Programs\Inno Setup 6\ISCC.exe","${env:ProgramFiles(x86)}\Inno Setup 6\ISCC.exe","$env:ProgramFiles\Inno Setup 6\ISCC.exe")) {
        if (Test-Path $cand) { $iscc = Get-Item $cand; break }
    }
}
if ($iscc) { & $iscc.FullName packaging\inno\realmos.iss }
else {
    Write-Warning "Inno Setup not found. Falling back to portable installer packaging\install.ps1"
    & (Join-Path $root "packaging\install.ps1") -Source $Dist
}
