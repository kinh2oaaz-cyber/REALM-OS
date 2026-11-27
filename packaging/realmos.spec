# PyInstaller spec for REALM OS (Windows executable packaging, Phase 10).
# Build:  pyinstaller packaging\realmos.spec
# Requires: pip install pyinstaller
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(SPECPATH).parent

block_cipher = None

a = Analysis(
    [str(ROOT / "main.py")],
    pathex=[str(ROOT)],
    binaries=[],
    datas=collect_data_files("PySide6") + [
        (str(ROOT / "REALM OS LOGO.png"), "."),
        (str(ROOT / "ui" / "themes" / "base.qss"), "ui/themes"),
        (str(ROOT / "assets"), "assets"),
    ],
    hiddenimports=collect_submodules("PySide6")
    + collect_submodules("modules")
    + ["psutil", "cryptography", "PySide6.QtPdf", "PySide6.QtPdfWidgets", "PySide6.QtMultimedia", "PySide6.QtMultimediaWidgets"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="REALM OS",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # GUI app, no console window
    icon=str(ROOT / "assets" / "REALM OS LOGO.ico"),
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="REALM OS",
)
