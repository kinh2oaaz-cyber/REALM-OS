# Design system — “REALM Cinematic”

A dark, cinematic, premium desktop language. Near-black and graphite
dominate; **blood crimson** signals action/active/important; **metallic
gold** is reserved for premium highlights and selected detail; warm white
is the primary text colour and muted grey is secondary. Every application
shares these tokens, components and motion rules.

## Principles

- **Black first.** The field is near-black; surfaces are graphite. Colour is
  an accent, never a background wash.
- **One primary action per view.** Crimson is used for the main action,
  active navigation and important status only.
- **Gold is a detail.** Thin indicators, eyebrows, selected icons, focus
  rings and premium labels — never gold borders on every panel.
- **Deliberate asymmetry.** Home uses varied panel widths and a dominant
  featured panel; other apps use the composition that fits their job
  (calendar grid, notes split editor, kanban columns, media split player).
- **Real content only.** No decorative fake buttons or placeholder controls.

## Tokens (`ui/themes/tokens.py`)

`ThemeTokens` is the single source of truth. `REDGOLD_TOKENS` is the
default (`redgold`); `LIGHT_TOKENS` and `DARK_TOKENS` remain available.

| role | value |
|---|---|
| `bg` | `#07060A` |
| `surface` | `#121016` |
| `surface_alt` | `#0C0A10` |
| `surface_elevated` | `#1A151F` |
| `sidebar_bg` | `#0A0810` |
| `text` | `#F4EEE7` |
| `text_secondary` | `#9C929C` |
| `text_tertiary` | `#6B6370` |
| `border` | `rgba(255,255,255,0.07)` |
| `border_strong` | `rgba(214,173,85,0.28)` |
| `hairline` | `rgba(255,255,255,0.05)` |
| `crimson` / `crimson_strong` | `#C51F35` / `#E2384F` |
| `crimson_soft` | `rgba(197,31,53,0.16)` |
| `gold` | `#D6AD55` |
| `gold_soft` | `rgba(214,173,85,0.14)` |
| `accent` (default) | `#D6AD55` |

Geometry: `radius_card=14`, `radius_control=9`. Type: Segoe UI, base
`13px`, section heading `16px`, hero title `30px`, small `11px`.

## Theme engine (`ui/themes/theme_manager.py`)

```python
theme.set_mode("redgold" | "system" | "light" | "dark")
theme.set_accent("#D6AD55")      # validated hex; invalid -> default
theme.set_font_family("Segoe UI")
theme.set_font_size(13)          # clamped 9..28
theme.toggle_dark()
theme.apply_saved()
theme.effective_theme()          # resolves system
theme.theme_changed              # Signal(str)
```

- QSS is generated from `ui/themes/base.qss` by substituting `@tokens`
  (longest key first). All widget styling lives in `base.qss`; every module
  inherits it.
- The app uses the **Fusion** style. `_apply_palette()` derives a dark (or
  light) `QPalette` from the active tokens so natively drawn subcontrols —
  combo/spin arrows, menus, dialogs — match the theme instead of rendering
  dark-on-dark.
- `_redgold_extra_qss()` only paints the atmospheric backdrop on
  `QWidget#RootBackground`; pages and scroll areas are transparent so it
  shows through.

## Surfaces & components (`ui/components/`)

- `RealmPage` — base page: 32×26 margins, 18px spacing, transparent
  background (dynamic property `realmPage=true`).
- `Card` / `SectionCard` — graphite gradient panel, hairline border,
  14px radius. `Card.title_label` lets pages clear their body safely.
- `HeroCard` — dominant featured panel with a soft drop shadow.
- `StatTile` — big value + uppercase micro-label.
- `AppTile` — launcher tile with an icon badge, name and description.
- `EmptyState` — dashed centred placeholder: icon, title, guidance and
  real actions (used by Gaming, etc.).
- `Sidebar` — grouped navigation (`WORKSPACE`, `TOOLKIT`, `SYSTEM`),
  REALM identity header, gold active icon and a crimson active row with a
  thin gold left indicator. Ampersands are escaped for display.
- `TopBar` — global search, clock, quick actions, notifications with badge,
  theme toggle and preferences.
- `SearchBox`, `NotificationsPanel`, quick-actions menu.

Text primitives: `heading`, `eyebrow`, `hero_title`, `muted`, `tiny`,
`gold_label`. Button object names: `PrimaryButton` (crimson), `DangerButton`
(crimson outline), `GhostButton` (quiet), `IconButton`.

## Atmospheric backdrop (`ui/background.py`)

Qt QSS has no `backdrop-filter`. REALM OS uses real, cached blur:

1. **QtWidgets shell** — a near-black field with very restrained crimson /
   gold radial bloom, a strong vignette and `QGraphicsBlurEffect`, cached as
   a versioned PNG (`ensure_redgold_background`). The bloom opacities are
   low single digits to ~0.12 so panels remain the subject.
2. **Qt Quick** — `ui/qml/BlurredBackground.qml` uses
   `QtQuick.Effects.FastBlur` via `QmlBlurredBackground(QQuickWidget)`.
   `QT_QUICK_BACKEND=software`, `QSG_RENDER_LOOP=basic`,
   `AA_ShareOpenGLContexts`; no animated blur, no extra dependencies.

## Motion (`ui/motion.py`, `ui/qml/`)

Page slide + fade ~220 ms `OutCubic`, `QGraphicsOpacityEffect`,
`QPropertyAnimation`; card elevation on hover; QML `Behavior` animations;
`LoadingSpinner`; `appearance.reduce_motion` disables motion. (Framer Motion
is React-only; this is Qt's native animation engine.)

## Application language

Every app keeps its own purpose-driven layout while sharing the tokens:

- **Home** — greeting, dominant featured panel + metric tiles, pinned apps,
  recently opened, and varied contextual panels (events/tasks/notes/games).
- **Calendar** — month/week/day grid, schedule rail, crimson events, gold
  today marker.
- **Notes** — library + split editor, formatting toolbar, autosave/export.
- **Tasks** — personal kanban / daily / weekly + PC task manager.
- **File Manager** — path bar, tree + preview, crimson selection.
- **Gaming** — library cards with covers, playtime, launch/favourite actions;
  a designed empty state when the library is empty.
- **Media** — library list + player, seek/controls, empty-library guidance.
- **Network** — status/speed tiles, ping diagnostics, adapters, Wi-Fi,
  devices, history.
- **Settings** — appearance (theme, accent swatches, font, size), startup,
  notifications, data, integrations, shortcuts, privacy, about.

## Quality bar

Backward-compatible SQLite and all 21 modules preserved; 65 tests pass;
`compileall` clean; responsive at 960×640 and above; readable contrast;
software rendering supported.
