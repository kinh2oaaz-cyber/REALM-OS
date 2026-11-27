"""Design system: tokens, light/dark/redgold palettes + QSS. Default redgold (frosted glass)."""

from __future__ import annotations

from .tokens import ACCENT_PRESETS, DARK_TOKENS, LIGHT_TOKENS, REDGOLD_TOKENS, ThemeTokens
from .theme_manager import ThemeManager, build_qss

__all__ = [
    "ACCENT_PRESETS",
    "DARK_TOKENS",
    "LIGHT_TOKENS",
    "REDGOLD_TOKENS",
    "ThemeTokens",
    "ThemeManager",
    "build_qss",
]

