"""Web-sourced SVG symbol icons (bundled, offline).

Icons are open-licensed (Tabler Icons, MIT; see
``assets/icons/LICENSE-tabler.txt``), fetched once and bundled — no
internet needed at runtime. Replaces emoji. `currentColor` is recolored
to match the active theme (e.g. gold on red). Falls back to empty icon.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPixmap
from PySide6.QtSvg import QSvgRenderer

from core.config import assets_dir

ICONS_DIR = assets_dir() / "icons"

# app id -> bundled symbol name
APP_ICONS: dict[str, str] = {
    "home": "home",
    "calendar": "calendar",
    "notes": "note",
    "tasks": "list-check",
    "file_manager": "folder",
    "gaming": "device-gamepad-2",
    "media": "music",
    "network": "wifi",
    "settings": "settings",
    "calculator": "calculator",
    "stopwatch": "stopwatch",
    "clipboard": "clipboard",
    "vault": "lock",
    "finance": "coins",
    "weather": "cloud",
    "screenshot": "camera",
    "pdf": "file-type-pdf",
    "downloads": "download",
    "projects": "folders",
    "devtools": "tools",
    "ai": "sparkles",
}

DEFAULT_APP_ICON = "app-window"
APP_LOGO = "hexagon"          # REALM OS mark (web symbol, not emoji)


def app_icon_name(app_id: str, fallback: str | None = None) -> str:
    return APP_ICONS.get(app_id, fallback or DEFAULT_APP_ICON)


def _svg_path(name: str) -> Path:
    return ICONS_DIR / f"{name}.svg"


def has_icon(name: str) -> bool:
    return _svg_path(name).exists()


@lru_cache(maxsize=512)
def _render(name: str, color: str, size: int) -> QPixmap:
    path = _svg_path(name)
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    if not path.exists():
        return pix
    svg = path.read_text(encoding="utf-8", errors="replace")
    svg = svg.replace("currentColor", color)
    renderer = QSvgRenderer(svg.encode("utf-8"))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return pix


def icon(name: str, color: str | None = None, size: int = 20) -> QIcon:
    """Return a QIcon for bundled symbol `name`, recolored to `color`."""
    color = color or "#1D1D1F"
    key_color = QColor(color).name() if QColor(color).isValid() else "#1D1D1F"
    pix = _render(name, key_color, size)
    return QIcon(pix)


def app_icon(app_id: str, color: str | None = None, size: int = 20, fallback_emoji: str | None = None) -> QIcon:
    name = app_icon_name(app_id)
    if has_icon(name):
        return icon(name, color, size)
    return QIcon()  # no emoji fallback; caller shows text


def realm_logo_path():
    """Path to the bundled REALM OS logo PNG (2000x2000)."""
    for candidate in (
        assets_dir() / "REALM OS LOGO.png",
        assets_dir() / "icons" / "realmos.png",
        assets_dir().parent / "REALM OS LOGO.png",
    ):
        if candidate.exists():
            return candidate
    return None


def realm_logo(size: int = 28) -> QIcon:
    """QIcon for the REALM OS logo; falls back to `hexagon` symbol."""
    from PySide6.QtGui import QPixmap
    path = realm_logo_path()
    if path is not None:
        pix = QPixmap(str(path))
        if not pix.isNull():
            pix = pix.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            return QIcon(pix)
    return icon(APP_LOGO, size=size)


def realm_symbol_path():
    """Path to original geometric REALM symbol SVG (crimson + gold; no letters; not Riot)."""
    p = assets_dir() / "icons" / "realm-symbol.svg"
    return p if p.exists() else None


def realm_symbol(size: int = 28) -> QIcon:
    """QIcon for the original REALM geometric symbol."""
    path = realm_symbol_path()
    if path is not None:
        return _svg_icon_file(path, size)
    return realm_logo(size=size)


def _svg_icon_file(path, size: int) -> QIcon:
    from PySide6.QtGui import QPixmap
    from PySide6.QtSvg import QSvgRenderer
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    renderer = QSvgRenderer(str(path))
    painter = QPainter(pix)
    renderer.render(painter)
    painter.end()
    return QIcon(pix)
