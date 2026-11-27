# Contributing to REALM OS

Thanks for your interest. REALM OS is a modular PySide6 + SQLite app.

## Dev setup (Windows 10/11, Python 3.14)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## Test
```powershell
python -m unittest discover -s tests -t . -v      # or .\scripts\test.ps1
```
CI runs the same on `windows-latest` with `QT_QPA_PLATFORM=offscreen`.

## Architecture
See `docs/ARCHITECTURE.md`, `docs/DESIGN_SYSTEM.md`, `docs/MOTION.md`,
`docs/ICONS.md`, `docs/PROGRESS.md`. Keep modules self-contained; add
real functionality (no fake buttons); additive DB migrations
(`database/schema.py`, bump version); parameterized SQL; confirm
destructive actions.

## Never commit
secrets, `.env`, tokens, `__pycache__`, `.venv`, `dist`, `build`, logs,
`*.db`. See `.gitignore`. 

## Style
match surrounding code; type hints; `from __future__ import annotations`;
no emoji icons (use `ui.icons` web SVGs).
