# Building a Windows executable + installer

REALM OS packages with **PyInstaller** (exe) + **Inno Setup** (installer),
or a simple portable installer. No internet needed at runtime.

## Outputs (`dist\`)
- `dist\REALM OS\REALM OS.exe` — **one-folder** build (reliable Qt bundling)
- `dist\REALM OS.exe` — **one-file** build (`-OneFile` / `realmos-onefile.spec`)
- `dist\REALM OS Setup.exe` — **Inno Setup installer** (if Inno Setup 6 installed)
- per-user install via `packaging\install.ps1` (no admin) otherwise

## One command
```powershell
.\scripts\build-windows.ps1            # one-folder + Inno (if available)
.\scripts\build-windows.ps1 -OneFile   # also produce single .exe
.\scripts\build-windows.ps1 -Clean -NoInstaller
```

## Steps
### 1) PyInstaller
```powershell
python -m pip install pyinstaller pillow
python -m PyInstaller packaging\realmos.spec --noconfirm          # one-folder
python -m PyInstaller packaging\realmos-onefile.spec --noconfirm  # one-file
```
- `packaging/realmos.spec` / `realmos-onefile.spec`.
- bundles **PySide6 (QtMultimedia/QtPdf)**, **psutil**, **cryptography**,
  `REALM OS LOGO.png`, `ui/themes/base.qss`, `assets/`.
- **Windows icon = `.ico`.** `assets/REALM OS LOGO.ico` generated from
  `REALM OS LOGO.png` via Pillow (`build-windows.ps1` does it).
- `console=False` (GUI), app name `REALM OS`, `icon`, no admin.

### 2) Installer
**Inno Setup 6** (https://jrsoftware.org/isinfo.php):
```powershell
ISCC.exe packaging\inno\realmos.iss     # -> dist\REALM OS Setup.exe
```
`realmos.iss`: per-user (`PrivilegesRequired=lowest`), Start Menu +
optional Desktop shortcut, uninstaller, icon, `LicenseFile`, bundles
`dist\REALM OS\*`. Build one-folder first.

**No Inno Setup?** `.\packaging\install.ps1 -Source ".\dist\REALM OS"`
(copies to `%LOCALAPPDATA%\Programs\REALM OS`, shortcuts, `uninstall.bat`).

## GitHub Releases
`.github/workflows/tests.yml` runs tests. A separate release workflow
can run `scripts\build-windows.ps1` and attach `dist\REALM OS.exe`,
`dist\REALM OS Setup.exe`, `dist\REALM OS\` zip to a Release. Never
commit `dist\`/`build\`. Nothing secret is bundled; user data is in
`%LOCALAPPDATA%\REALM OS`.

## Notes / honesty
- Can't guarantee a build in every environment; run on Windows 10/11.
- PyInstaller doesn't sign the exe. **Code-sign** with your cert to
  avoid SmartScreen (`signtool sign ...`). Unsigned apps may warn.
- REALM OS logo `.ico` derived from `REALM OS LOGO.png`.
