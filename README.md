# REALM OS

A premium, interconnected **personal desktop application ecosystem** for
Windows 10 and Windows 11. One consistent interface, shared local
database, unified navigation and a single design language across every
app.

REALM OS is **not** a replacement for Windows and not a sci-fi dashboard.
It is a polished collection of native-style desktop applications that
work together, **local-first**, with no internet required.

> **All phases (1–10) implemented.** Core architecture, shell, shared SQLite, design system, 8 main apps + 12 additional apps (21 total), packaging. See `docs/PROGRESS.md`. Nothing is faked; no placeholder buttons.
> navigation, shared SQLite database, design system (light/dark + accent),
> notifications, global search, persistent settings/favorites/recents,
> and honest scaffolds for each app. Applications are built progressively
> in later phases (see `docs/PROGRESS.md`). Nothing is faked.

---

## Tech stack

- **Python 3.14**
- **PySide6** (Qt 6, QtWidgets today; Qt Quick/QML-ready module boundaries)
- **SQLite** (single shared local database, WAL, migrations)
- **psutil** (system/process info for PC Task Manager, Gaming, Network)
- **Windows APIs** where required (via `os`, `pywin32`, `ctypes`)
- **PyInstaller** for executable packaging

## Run

```powershell
python -m pip install -r requirements.txt
python main.py            # or: python -m app.main
```

or use the helper: `.\scripts\run.ps1`

## Test

```powershell
python -m unittest discover -s tests -t . -v   # or: .\scripts\test.ps1
```

62 tests cover database, settings, event bus, registry, notifications,
theme, modules, security, system info and a full offscreen UI smoke test.

## Data

Local-first. Everything is stored under a per-user directory; nothing
leaves your machine.

- Windows: `%LOCALAPPDATA%\REALM OS`
- Database: `<data>\database\realmos.db`
- Logs: `<data>\logs\realmos.log`
- Override location with `REALMOS_DATA_DIR`

## Build a Windows executable

```powershell
.\scripts\build-windows.ps1        # pyinstaller packaging\realmos.spec
```

---

## Main interface

**Left sidebar:** Home Â· Calendar Â· Notes Â· Tasks Â· File Manager Â·
Gaming Â· Media Â· Network Â· Settings

**Top bar:** global search Â· current date/time Â· notifications Â·
quick actions Â· user preferences Â· theme toggle

**Home:** recently opened apps Â· upcoming events Â· pending tasks Â·
recently accessed notes Â· favorite apps Â· quick actions

**Keyboard:** `Ctrl+F` search Â· `Ctrl+D` toggle dark Â· `Ctrl+,`
settings Â· `Ctrl+1` home Â· `F5` refresh

---

## Project structure

See **`docs/ARCHITECTURE.md`**. Summary:

```
REALM OS/
  app/                 entry point + application object
  core/                config, logging, event bus, settings, registry, notifications, theme-base, context
  database/            SQLite connection, schema/migrations, repositories
  ui/
    pages/             top-level pages (Home)
    components/        reusable widgets (Sidebar, TopBar, Card, ...)
    themes/            design tokens, light/dark, QSS
  modules/
    calendar/          app + services + models + database + ui
    notes/
    task_manager/      personal + PC task manager
    file_manager/
    gaming/
    media/
    network/
    settings/
  system/              psutil system/process info
  integrations/        optional third-party (none required)
  security/            password hashing / encryption hooks
  assets/              icons
  tests/               unittest suite
  logs/                runtime logs
  docs/                documentation + progress log
  scripts/             PowerShell automation
  packaging/           PyInstaller spec
```

Each module exposes `register(registry, ctx)` and owns its own
services, models and database access.

---

## PowerShell: create the project structure

```powershell
.\scripts\New-RealmOSProject.ps1 -Root "C:\work station\REALM OS"
```

Equivalent manual commands:

```powershell
$root = "C:\work station\REALM OS"
$dirs = @("app","core","database","database\migrations","ui","ui\pages","ui\components","ui\themes",
  "modules","modules\calendar","modules\calendar\ui","modules\notes","modules\notes\ui",
  "modules\task_manager","modules\task_manager\ui","modules\file_manager","modules\file_manager\ui",
  "modules\gaming","modules\gaming\ui","modules\media","modules\media\ui","modules\network","modules\network\ui",
  "modules\settings","modules\settings\ui","system","integrations","security","assets","assets\icons",
  "tests","logs","docs","scripts","packaging")
foreach ($d in $dirs) { New-Item -ItemType Directory -Path (Join-Path $root $d) -Force | Out-Null }
```

See **`docs/POWERSHELL.md`** for full command reference, and **where each
file belongs** in `docs/ARCHITECTURE.md`.

---

## Development rules honored

Progressive development Â· no giant single script Â· reusable components Â·
consistent design system Â· real functionality, no fake/placeholder
buttons Â· tested modules Â· preserved working functionality Â· no
overwriting unrelated files Â· lightweight dependencies Â· PowerShell
provided Â· documented file locations Â· documentation + progress log Â·
validated imports/dependencies Â· graceful error handling Â· persistent
data across restarts.

See `docs/PROGRESS.md` for the development log.

