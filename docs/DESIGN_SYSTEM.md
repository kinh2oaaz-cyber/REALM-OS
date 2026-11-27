# Design system

Apple-inspired minimalist. Clean spacious layouts, rounded corners,
subtle shadows/borders, beautiful typography, smooth transitions,
light + dark, neutral backgrounds, subtle accents, functional nav,
responsive, minimal decoration. No neon, no sci-fi HUD, no decorative
AI orbs, no clutter, no fake buttons.

## Tokens (`ui/themes/tokens.py`)

`ThemeTokens` — colors (`bg`, `surface`, `surface_alt`, `sidebar_bg`,
`text`, `text_secondary`, `text_tertiary`, `border`, `border_strong`,
`hover`, `pressed`, `accent`, `accent_soft`, `accent_text`, `danger`,
`success`, `warning`, `shadow`, `scrollbar*`), geometry
(`radius_card=12`, `radius_control=8`, `spacing=12`), typography
(`font_family`, `base_size=13`, `title_size=20`, `heading_size=16`,
`small_size=11`).

`LIGHT_TOKENS`, `DARK_TOKENS`. `ACCENT_PRESETS`. Default accent
`#0071E3`; dark uses `#0A84FF`.

## ThemeManager

```python
theme.set_mode("system" | "light" | "dark")
theme.set_accent("#FF3B30")     # validated hex; invalid -> default
theme.set_font_family("Segoe UI")
theme.set_font_size(13)         # clamped 9..28
theme.toggle_dark()
theme.apply_saved()
theme.effective_theme()         # resolves system
theme.theme_changed             # Signal(str)
```

QSS is generated from `ui/themes/base.qss` with `@token` substitution
(longest-key-first). `accent_soft` is derived from the accent.
`Fusion` style + stylesheet applied app-wide.

## Components

`Card`, `SectionCard`, `EmptyState`, `ScaffoldPage`, `RealmPage`,
`Sidebar`, `TopBar`, `SearchBox`, `NotificationsPanel`, quick actions.
Primary buttons `#PrimaryButton`, danger `#DangerButton`, ghost
`#GhostButton`, icon `#IconButton`.


## Red & Gold blur (default)

Default theme edgold (user can switch System/Light/Dark). Deep red→gold background (ui/background.py, pre-blurred ssets/background_redgold.png), frosted-glass translucent panels, **gold accent #D4AF37**, warm dark text. Qt QSS has no ackdrop-filter, so a pre-blurred image + QGraphicsBlurEffect + translucent surfaces are used. No neon, no sci-fi, readable contrast. See docs/MOTION.md, docs/ICONS.md.


## Riot-Client-style polish

Dark #0F1114, translucent panels, **Riot red #E84057** + **gold #C8AA6E** + #F0E6D2, rounded, shadows, smooth Qt motion, blurred background. **REALM OS logo** REALM OS LOGO.png. Honest note: matches Riot-Client *style*; not pixel-identical; **not** Framer Motion (Riot Client itself is CEF/React + Framer Motion; REALM OS is PySide6).
