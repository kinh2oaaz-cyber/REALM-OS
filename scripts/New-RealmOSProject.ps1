<#
.SYNOPSIS
    Create the REALM OS project directory structure.

.DESCRIPTION
    Recreates the full folder layout described in the Master Brief.
    Idempotent. Run from anywhere.

.PARAMETER Root
    Target project root. Defaults to current directory.

.EXAMPLE
    .\New-RealmOSProject.ps1 -Root "C:\work station\REALM OS"
#>
param(
    [string]$Root = (Get-Location).Path
)

$ErrorActionPreference = "Stop"

$directories = @(
    "app",
    "core",
    "database",
    "database\migrations",
    "ui",
    "ui\pages",
    "ui\components",
    "ui\themes",
    "modules",
    "modules\calendar",        "modules\calendar\ui",
    "modules\notes",           "modules\notes\ui",
    "modules\task_manager",    "modules\task_manager\ui",
    "modules\file_manager",    "modules\file_manager\ui",
    "modules\gaming",          "modules\gaming\ui",
    "modules\media",           "modules\media\ui",
    "modules\network",         "modules\network\ui",
    "modules\settings",        "modules\settings\ui",
    "system",
    "integrations",
    "security",
    "assets",
    "assets\icons",
    "tests",
    "logs",
    "docs",
    "scripts",
    "packaging"
)

foreach ($dir in $directories) {
    $path = Join-Path $Root $dir
    if (-not (Test-Path $path)) {
        New-Item -ItemType Directory -Path $path -Force | Out-Null
        Write-Host "Created $path"
    }
}

# keep empty dirs in git
foreach ($keep in @("logs", "assets\icons")) {
    $gitkeep = Join-Path (Join-Path $Root $keep) ".gitkeep"
    if (-not (Test-Path $gitkeep)) { New-Item -ItemType File -Path $gitkeep -Force | Out-Null }
}

Write-Host "REALM OS project structure ready at $Root"
