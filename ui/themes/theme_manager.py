"""Theme engine.

Resolves system/light/dark, applies accent color, font family and
size, and generates a QSS stylesheet from ``base.qss`` + tokens.
Persists choices via :class:`core.settings.Settings`.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from PySide6.QtCore import QObject, Qt, Signal
from PySide6.QtWidgets import QApplication

from core.logging_setup import get_logger
from core.settings import Settings

from .tokens import DEFAULT_ACCENT, PALETTES, ThemeTokens

_log = get_logger("theme")

_QSS_PATH = Path(__file__).resolve().parent / "base.qss"

THEME_REDGOLD = "redgold"
THEME_SYSTEM = "system"
THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_MODES = (THEME_REDGOLD, THEME_SYSTEM, THEME_LIGHT, THEME_DARK)


def _accent_soft(accent_hex: str, theme: str) -> str:
    """A translucent-ish soft background derived from the accent."""
    accent_hex = accent_hex.lstrip("#")
    if len(accent_hex) != 6:
        return "#E5F0FC" if theme == THEME_LIGHT else "#1B3A5B"
    try:
        r = int(accent_hex[0:2], 16)
        g = int(accent_hex[2:4], 16)
        b = int(accent_hex[4:6], 16)
    except ValueError:
        return "#E5F0FC" if theme == THEME_LIGHT else "#1B3A5B"
    if theme != THEME_LIGHT:
        # blend toward dark surface
        r = int(r * 0.30 + 0x2C * 0.70)
        g = int(g * 0.30 + 0x2C * 0.70)
        b = int(b * 0.30 + 0x2C * 0.70)
    else:
        r = int(r * 0.18 + 0xFF * 0.82)
        g = int(g * 0.18 + 0xFF * 0.82)
        b = int(b * 0.18 + 0xFF * 0.82)
    return f"#{r:02X}{g:02X}{b:02X}"


def build_qss(
    tokens: ThemeTokens,
    accent: str = DEFAULT_ACCENT,
    font_family: str | None = None,
    base_size: int | None = None,
    template: str | None = None,
) -> str:
    """Render the base QSS template with concrete token values."""
    accent = accent if _is_hex_color(accent) else DEFAULT_ACCENT
    fam = font_family or tokens.font_family
    size = base_size or tokens.base_size
    eff = replace(
        tokens,
        accent=accent,
        accent_soft=_accent_soft(accent, tokens.name),
        font_family=fam,
        base_size=size,
    )
    if template is None:
        template = _QSS_PATH.read_text(encoding="utf-8")

    replacements = {
        "@bg": eff.bg,
        "@surface": eff.surface,
        "@surface_alt": eff.surface_alt,
        "@sidebar_bg": eff.sidebar_bg,
        "@text_secondary": eff.text_secondary,
        "@text_tertiary": eff.text_tertiary,
        "@text": eff.text,
        "@border_strong": eff.border_strong,
        "@border": eff.border,
        "@hover": eff.hover,
        "@pressed": eff.pressed,
        "@accent_soft": eff.accent_soft,
        "@accent_text": eff.accent_text,
        "@accent": eff.accent,
        "@danger": eff.danger,
        "@success": eff.success,
        "@warning": eff.warning,
        "@scrollbar_hover": eff.scrollbar_hover,
        "@scrollbar": eff.scrollbar,
        "@font_family": eff.font_family,
        "@base_size": f"{eff.base_size}px",
        "@title_size": f"{eff.title_size}px",
        "@heading_size": f"{eff.heading_size}px",
        "@small_size": f"{eff.small_size}px",
        "@radius_card": str(eff.radius_card),
        "@radius_control": str(eff.radius_control),
    }
    # Longest keys first to avoid prefix collisions (@accent vs @accent_soft).
    out = template
    for key in sorted(replacements, key=len, reverse=True):
        out = out.replace(key, replacements[key])
    return out


def _is_hex_color(value: str) -> bool:
    if not isinstance(value, str) or not value.startswith("#"):
        return False
    body = value[1:]
    if len(body) not in (3, 6):
        return False
    try:
        int(body, 16)
        return True
    except ValueError:
        return False


class ThemeManager(QObject):
    """Applies and persists the active theme."""

    theme_changed = Signal(str)

    def __init__(self, settings: Settings, app: QApplication) -> None:
        super().__init__()
        self._settings = settings
        self._app = app

    # -- queries --------------------------------------------------------
    def mode(self) -> str:
        mode = self._settings.get_str("appearance.theme", THEME_REDGOLD)
        return mode if mode in THEME_MODES else THEME_REDGOLD

    def accent(self) -> str:
        value = self._settings.get_str("appearance.accent", DEFAULT_ACCENT)
        return value if _is_hex_color(value) else DEFAULT_ACCENT

    def font_family(self) -> str:
        return self._settings.get_str("appearance.font_family", "Segoe UI")

    def font_size(self) -> int:
        return self._settings.get_int("appearance.font_size", 13)

    def effective_theme(self) -> str:
        mode = self.mode()
        if mode != THEME_SYSTEM:
            return mode
        return self._system_theme()

    def _system_theme(self) -> str:
        try:
            hints = self._app.styleHints()
            scheme = hints.colorScheme() if hints is not None else Qt.ColorScheme.Unknown
            if scheme == Qt.ColorScheme.Dark:
                return THEME_DARK
        except Exception:  # noqa: BLE001 - defensive across Qt versions
            _log.debug("Could not query system color scheme", exc_info=True)
        return THEME_LIGHT

    def tokens(self) -> ThemeTokens:
        return PALETTES[self.effective_theme()]

    # -- mutation -------------------------------------------------------
    def apply(self) -> None:
        """Generate QSS and apply it to the whole application."""
        qss = build_qss(
            self.tokens(),
            accent=self.accent(),
            font_family=self.font_family(),
            base_size=self.font_size(),
        )
        if self.effective_theme() == THEME_REDGOLD:
            qss += _redgold_extra_qss()
        try:
            self._app.setStyle("Fusion")
            self._app.setStyleSheet(qss)
        except Exception:  # noqa: BLE001
            _log.exception("Failed to apply theme")
        self.theme_changed.emit(self.effective_theme())

    def apply_saved(self) -> None:
        self.apply()

    def set_mode(self, mode: str) -> None:
        if mode not in THEME_MODES:
            mode = THEME_SYSTEM
        self._settings.set("appearance.theme", mode)
        self.apply()

    def set_accent(self, accent_hex: str) -> None:
        if not _is_hex_color(accent_hex):
            accent_hex = DEFAULT_ACCENT
        self._settings.set("appearance.accent", accent_hex)
        self.apply()

    def set_font_family(self, family: str) -> None:
        self._settings.set("appearance.font_family", family or "Segoe UI")
        self.apply()

    def set_font_size(self, size: int) -> None:
        size = max(9, min(28, int(size)))
        self._settings.set("appearance.font_size", size)
        self.apply()

    def toggle_dark(self) -> str:
        """Toggle between light and dark; returns new effective theme."""
        new = THEME_LIGHT if self.effective_theme() == THEME_DARK else THEME_DARK
        self.set_mode(new)
        return new

def _redgold_extra_qss() -> str:
    """Frosted-glass Crimson x Royal Gold overrides; appended in redgold mode."""
    try:
        from ui.background import ensure_redgold_background

        bg_path = ensure_redgold_background().as_posix()
    except Exception:  # noqa: BLE001
        bg_path = ""
    bg_rule = (
        f'QWidget#RootBackground {{ background-image: url("{bg_path}"); '
        'background-position: center; background-repeat: no-repeat; }'
        if bg_path
        else ""
    )
    return (
        "\n/* ---- REALM crimson x gold frosted glass ---- */\n"
        "QWidget { background: transparent; }\n"
        "QMainWindow { background: transparent; }\n"
        + bg_rule
        + "\nQFrame#Card { background: rgba(28, 21, 25, 0.72); border: 1px solid rgba(214, 173, 85, 0.18); border-radius: 14px; }\n"
        "QWidget#Sidebar { background: rgba(20, 16, 20, 0.85); border-right: 1px solid rgba(214, 173, 85, 0.18); }\n"
        "QWidget#TopBar { background: rgba(20, 16, 20, 0.80); border-bottom: 1px solid rgba(214, 173, 85, 0.18); }\n"
        "QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit { background: rgba(20, 16, 20, 0.72); border: 1px solid rgba(214, 173, 85, 0.25); }\n"
        "QPushButton { background: rgba(28, 21, 25, 0.72); border: 1px solid rgba(214, 173, 85, 0.22); }\n"
        "QPushButton#PrimaryButton { background: #D6AD55; color: #0B090B; border: none; }\n"
        "QPushButton#PrimaryButton:hover { background: #F1D58A; color: #0B090B; border: none; }\n"
        "QPushButton#NavButton:checked { background: rgba(197, 31, 53, 0.18); color: #F1D58A; border-left: 3px solid #D6AD55; font-weight: 600; }\n"
        "QListWidget { background: transparent; }\n"
        "QScrollArea { background: transparent; }\n"
    )
