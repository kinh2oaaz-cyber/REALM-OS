"""Design tokens for the Apple-inspired minimalist design system.

Clean spacious layouts, rounded corners, subtle shadows, neutral
backgrounds, subtle accents. Light and dark palettes share structure.
"""

from __future__ import annotations

from dataclasses import dataclass

# Default accent + curated presets (subtle, desaturated, not neon).
DEFAULT_ACCENT = "#C9A863"
ACCENT_PRESETS: list[tuple[str, str]] = [
    ("Blue", "#0071E3"),
    ("Indigo", "#5856D6"),
    ("Purple", "#AF52DE"),
    ("Pink", "#FF2D55"),
    ("Red", "#FF3B30"),
    ("Orange", "#FF9500"),
    ("Green", "#34C759"),
    ("Teal", "#30B0C7"),
    ("Graphite", "#8E8E93"),
]


@dataclass(frozen=True)
class ThemeTokens:
    name: str
    bg: str
    surface: str
    surface_alt: str
    sidebar_bg: str
    text: str
    text_secondary: str
    text_tertiary: str
    border: str
    border_strong: str
    hover: str
    pressed: str
    accent: str
    accent_soft: str
    accent_text: str
    danger: str
    success: str
    warning: str
    shadow: str
    scrollbar: str
    scrollbar_hover: str
    # geometry
    radius_card: int = 12
    radius_control: int = 8
    spacing: int = 12
    # typography
    font_family: str = "Segoe UI"
    base_size: int = 13
    title_size: int = 20
    heading_size: int = 16
    small_size: int = 11


LIGHT_TOKENS = ThemeTokens(
    name="light",
    bg="#F5F5F7",
    surface="#FFFFFF",
    surface_alt="#FAFAFC",
    sidebar_bg="#F5F5F7",
    text="#1D1D1F",
    text_secondary="#6E6E73",
    text_tertiary="#8E8E93",
    border="#D2D2D7",
    border_strong="#C7C7CC",
    hover="#ECECF1",
    pressed="#E2E2E8",
    accent=DEFAULT_ACCENT,
    accent_soft="#E5F0FC",
    accent_text="#FFFFFF",
    danger="#FF3B30",
    success="#34C759",
    warning="#FF9500",
    shadow="rgba(0, 0, 0, 0.12)",
    scrollbar="#C7C7CC",
    scrollbar_hover="#AEAEB2",
)

DARK_TOKENS = ThemeTokens(
    name="dark",
    bg="#1C1C1E",
    surface="#2C2C2E",
    surface_alt="#242426",
    sidebar_bg="#1C1C1E",
    text="#F5F5F7",
    text_secondary="#98989D",
    text_tertiary="#8E8E93",
    border="#38383A",
    border_strong="#48484A",
    hover="#3A3A3C",
    pressed="#48484A",
    accent="#0A84FF",
    accent_soft="#1B3A5B",
    accent_text="#FFFFFF",
    danger="#FF453A",
    success="#32D74B",
    warning="#FF9F0A",
    shadow="rgba(0, 0, 0, 0.5)",
    scrollbar="#48484A",
    scrollbar_hover="#636366",
    font_family="Segoe UI",
    base_size=13,
)

PALETTES: dict[str, ThemeTokens] = {"light": LIGHT_TOKENS, "dark": DARK_TOKENS}

REDGOLD_TOKENS = ThemeTokens(
    name="redgold",  # REALM Crimson x Royal Gold, frosted glass (Riot-INSPIRED, original; not Riot assets)
    bg="#0B090B",            # near-black
    surface="#1C1519",       # translucent in QSS; solid fallback
    surface_alt="#141014",   # secondary background
    sidebar_bg="#141014",
    text="#F5F0E9",          # main text
    text_secondary="#A69A9A",# secondary text
    text_tertiary="#7A6E6E",
    border="rgba(201, 168, 99, 0.12)",
    border_strong="rgba(201, 168, 99, 0.28)",
    hover="rgba(168, 36, 53, 0.10)",
    pressed="rgba(168, 36, 53, 0.20)",
    accent="#C9A863",        # muted royal gold (antique bronze)
    accent_soft="rgba(201, 168, 99, 0.10)",
    accent_text="#0B090B",
    danger="#A82435",        # deeper, desaturated crimson red
    success="#3FB950",
    warning="#F1D58A",
    shadow="rgba(0, 0, 0, 0.55)",
    scrollbar="rgba(201, 168, 99, 0.35)",
    scrollbar_hover="rgba(201, 168, 99, 0.55)",
    radius_card=14,
    radius_control=10,
    font_family="Segoe UI",
    base_size=13,
)
# REALM Crimson accents
PALETTES["redgold"] = REDGOLD_TOKENS
# alias name
PALETTES["crimson_gold"] = REDGOLD_TOKENS

