<# Run the REALM OS test suite. #>
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root
python -m unittest discover -s tests -t . -v
