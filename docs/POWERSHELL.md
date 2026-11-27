# PowerShell reference

## Create project structure

```powershell
.\scripts\New-RealmOSProject.ps1 -Root "C:\work station\REALM OS"
```

Manual:

```powershell
$root = "C:\work station\REALM OS"
New-Item -ItemType Directory -Path $root -Force | Out-Null
$dirs = @("app","core","database","database\migrations","ui","ui\pages","ui\components","ui\themes",
  "modules","modules\calendar","modules\calendar\ui","modules\notes","modules\notes\ui",
  "modules\task_manager","modules\task_manager\ui","modules\file_manager","modules\file_manager\ui",
  "modules\gaming","modules\gaming\ui","modules\media","modules\media\ui","modules\network","modules\network\ui",
  "modules\settings","modules\settings\ui","system","integrations","security","assets","assets\icons",
  "tests","logs","docs","scripts","packaging")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path (Join-Path $root $d) -Force | Out-Null }
```

## Create a single file

```powershell
New-Item -ItemType File -Path ".\core\example.py" -Force
Set-Content -Path ".\core\example.py" -Value '"""Module docstring."""' -Encoding UTF8
```

## Environment / venv

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run / test / build

```powershell
.\scripts\run.ps1                 # python main.py
.\scripts\test.ps1                # unittest discover
.\scripts\build-windows.ps1       # pyinstaller packaging\realmos.spec
```

## Data location override

```powershell
$env:REALMOS_DATA_DIR = "D:\REALM OS Data"
python main.py
```

## Open logs

```powershell
Invoke-Item (Join-Path $env:LOCALAPPDATA "REALM OS\logs")
```
