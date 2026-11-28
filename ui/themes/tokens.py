"""REALM OS design tokens — "REALM Cinematic" design language.

A dark, cinematic, premium desktop aesthetic: deep near-black backgrounds,
graphite surfaces, blood-crimson primary accents and metallic gold premium
highlights. Tokens are the single source of truth for every widget; QSS is
generated from them at runtime (see ``theme_manager.build_qss``).
"""

from __future__ import annotations

from dataclasses import dataclass

# Default accent (gold = premium highlight / selected detail).
DEFAULT_ACCENT = "#D6AD55"

ACCENT_PRESETS: list[tuple[str, str]] = [
    ("Gold", "#D6AD55"),
    ("Crimson", "#C51F35"),
    ("Rose", "#E0566E"),
    ("Amber", "#E0A458"),
    ("Emerald", "#3FB950"),
    ("Teal", "#30B0C7"),
    ("Indigo", "#7C83E0"),
    ("Purple", "#AF52DE"),
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
    radius_card: int = 14
    radius_control: int = 9
    spacing: int = 12
    # typography
    font_family: str = "Segoe UI"
    base_size: int = 13
    title_size: int = 20
    heading_size: int = 16
    small_size: int = 11
    # extended "REALM Cinematic" palette (appended; safe defaults)
    surface_elevated: str = ""
    surface_glass: str = ""
    gold: str = ""
    gold_soft: str = ""
    crimson: str = ""
    crimson_soft: str = ""
    crimson_strong: str = ""
    text_on_accent: str = ""
    hairline: str = ""
    glow_crimson: str = ""


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

# ---------------------------------------------------------------------------
# REALM Cinematic — the flagship dark theme.
# Discipline: charcoal/black dominate; crimson = primary action / active /
# important; gold = premium highlight / selected detail only.
# ---------------------------------------------------------------------------
REDGOLD_TOKENS = ThemeTokens(
    name="redgold",
    bg="#07060A",                 # deep near-black (violet-black)
    surface="#121016",            # graphite panel
    surface_alt="#0C0A10",        # recessed / secondary background
    sidebar_bg="#0A0810",         # nav rail
    text="#F4EEE7",               # warm white
    text_secondary="#9C929C",     # muted grey
    text_tertiary="#6B6370",      # faint
    border="rgba(255, 255, 255, 0.07)",
    border_strong="rgba(214, 173, 85, 0.28)",
    hover="rgba(255, 255, 255, 0.05)",
    pressed="rgba(255, 255, 255, 0.09)",
    accent="#D6AD55",             # metallic gold (premium highlight)
    accent_soft="rgba(214, 173, 85, 0.14)",
    accent_text="#0A0709",
    danger="#C51F35",             # blood crimson
    success="#3FB950",
    warning="#E0A458",
    shadow="rgba(0, 0, 0, 0.62)",
    scrollbar="rgba(214, 173, 85, 0.30)",
    scrollbar_hover="rgba(214, 173, 85, 0.55)",
    radius_card=14,
    radius_control=9,
    font_family="Segoe UI",
    base_size=13,
    # extended palette
    surface_elevated="#1A151F",                    # raised card
    surface_glass="rgba(18, 15, 22, 0.72)",        # translucent panel
    gold="#D6AD55",
    gold_soft="rgba(214, 173, 85, 0.14)",
    crimson="#C51F35",
    crimson_soft="rgba(197, 31, 53, 0.16)",
    crimson_strong="#E2384F",
    text_on_accent="#FFF6F7",
    hairline="rgba(255, 255, 255, 0.05)",
    glow_crimson="rgba(197, 31, 53, 0.35)",
)

PALETTES["redgold"] = REDGOLD_TOKENS
PALETTES["crimson_gold"] = REDGOLD_TOKENS
