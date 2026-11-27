"""Best-effort installed-game detection. Never required; user can add manually.

Sources: Steam `steamapps`, Windows uninstall registry keys, common
install roots. Read-only.
"""

from __future__ import annotations

import os
import re
from pathlib import Path

STEAM_ROOTS = [
    r"C:\Program Files (x86)\Steam",
    r"C:\Program Files\Steam",
    os.path.expandvars(r"%LOCALAPPDATA%\Steam"),
]

COMMON_ROOTS = [
    r"C:\Program Files", r"C:\Program Files (x86)",
    r"C:\Program Files\Epic Games", r"C:\Program Files (x86)\Epic Games",
    r"C:\Program Files\GOG Galaxy\Games", r"C:\Program Files (x86)\GOG Galaxy\Games",
    r"C:\Games", r"D:\Games", r"E:\Games",
]

_EXE_BLACKLIST = re.compile(r"(unins|uninstall|setup|install|redist|vcredist|crash|report|update|helper|launcher)", re.I)


def detect_installed_games(limit: int = 200) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    for game in _scan_steam() + _scan_registry_uninstall():
        key = (game.get("name", "").lower(), game.get("exe_path", "").lower())
        if key in seen or not game.get("name"):
            continue
        seen.add(key)
        found.append(game)
        if len(found) >= limit:
            break
    found.sort(key=lambda g: g["name"].lower())
    return found


def _scan_steam() -> list[dict]:
    out = []
    for root in STEAM_ROOTS:
        steamapps = Path(root) / "steamapps"
        if not steamapps.exists():
            continue
        for manifest in steamapps.glob("appmanifest_*.acf"):
            try:
                text = manifest.read_text(encoding="utf-8", errors="replace")
                name = _acf_value(text, "name")
                installdir = _acf_value(text, "installdir")
                if not name:
                    continue
                game_dir = steamapps / "common" / (installdir or name)
                exe = _find_main_exe(game_dir)
                out.append({"name": name, "exe_path": exe, "source": "Steam"})
            except OSError:
                continue
    return out


def _acf_value(text: str, key: str) -> str:
    m = re.search(rf'"{re.escape(key)}"\s+"([^"]*)"', text, re.I)
    return m.group(1) if m else ""


def _scan_registry_uninstall() -> list[dict]:
    out = []
    if os.name != "nt":
        return out
    try:
        import winreg
    except ImportError:
        return out
    roots = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
    ]
    for hive, subkey in roots:
        try:
            with winreg.OpenKey(hive, subkey) as key:
                i = 0
                while True:
                    try:
                        sub = winreg.EnumKey(key, i); i += 1
                    except OSError:
                        break
                    try:
                        with winreg.OpenKey(key, sub) as app_key:
                            name = _reg(key=app_key, name="DisplayName", winreg=winreg)
                            location = _reg(key=app_key, name="InstallLocation", winreg=winreg)
                            icon = _reg(key=app_key, name="DisplayIcon", winreg=winreg)
                            if not name:
                                continue
                            exe = _clean_icon_path(icon) or _find_main_exe(Path(location)) if location else _clean_icon_path(icon)
                            out.append({"name": name, "exe_path": exe or "", "source": "Windows"})
                    except OSError:
                        continue
        except OSError:
            continue
    return out


def _reg(key, name: str, winreg):  # noqa: ANN001
    try:
        val, _ = winreg.QueryValueEx(key, name)
        return val
    except OSError:
        return ""


def _clean_icon_path(icon: str) -> str:
    if not icon:
        return ""
    icon = icon.split(",")[0].strip().strip('"')
    return icon if icon.lower().endswith(".exe") and os.path.exists(icon) else ""


def _find_main_exe(game_dir: Path) -> str:
    try:
        if not game_dir.exists():
            return ""
        exes = [p for p in game_dir.rglob("*.exe") if not _EXE_BLACKLIST.search(p.name)]
        if not exes:
            return ""
        # prefer exe matching folder name, then largest
        exes.sort(key=lambda p: (p.name.lower().startswith(game_dir.name.lower()) is False, -p.stat().st_size))
        return str(exes[0])
    except (OSError, PermissionError):
        return ""
