# REALM OS Visual Redesign — Crimson × Royal Gold

Riot-Client-**inspired** layout/polish; **original REALM identity; NOT a
Riot clone; NO Riot Games branding, logos, icons, artwork or proprietary
assets.** Preserves all working logic + SQLite + 21 apps. No rewrite.

## Palette (centralized `ui/themes/tokens.py::REDGOLD_TOKENS`, `redgold` default)
| role | value |
|---|---|
| Background | `#07060A` |
| Surface | `#121016` |
| Recessed | `#0C0A10` |
| Elevated | `#1A151F` |
| Sidebar | `#0A0810` |
| Primary crimson | `#C51F35` |
| Crimson strong | `#E2384F` |
| Royal gold | `#D6AD55` |
| Text | `#F4EEE7` |
| Secondary text | `#9C929C` |
| Tertiary text | `#6B6370` |
| Hairline | `rgba(255,255,255,0.05)` |
| Gold border | `rgba(214,173,85,0.28)` |

Black/charcoal dominate. Gold = premium highlight and selected detail
(not overused); crimson = action, active state and importance (never a
bright background wash). See `docs/DESIGN_SYSTEM.md`.

## Blur / glass (real, not fake transparency)
Qt QSS has no `backdrop-filter`. **Three real supported paths:**
1. **QtWidgets shell**: pre-blurred, versioned backdrop
   (`assets/background_redgold_v2.png`, `QGraphicsBlurEffect`,
   `ui/background.py::ensure_redgold_background`) + `QWidget#RootBackground`.
   The field is near-black with restrained crimson/gold bloom and a strong
   vignette; opaque sidebar/top bar and graphite cards sit above it.
2. **`QGraphicsBlurEffect`** + **`QGraphicsDropShadowEffect`** on cards.
3. **Qt Quick / QML `QtQuick.Effects.FastBlur`** in reusable
   **`ui/qml/BlurredBackground.qml`**; **`QmlBlurredBackground(QQuickWidget)`**
   (`ui/background.py`). `QT_QUICK_BACKEND=software`, `QSG_RENDER_LOOP=basic`,
   `QT.AA_ShareOpenGLContexts`. **Performance-safe** (no animated blur; cached;
   no extra deps; integrated graphics).
Honest note: current shell is QtWidgets; Qt Quick blur is provided as
reusable QML + `QQuickWidget`, not a full QML rewrite (preserves logic).

## Motion (`ui/motion.py`, `ui/qml`)
Page slide+fade 220ms `OutCubic`, `QGraphicsOpacityEffect`,
`QPropertyAnimation`, card hover scale + crimson glow + `QGraphicsDropShadowEffect`,
sidebar selection, `QML Behavior`/`NumberAnimation`/`ColorAnimation`,
`LoadingSpinner`, notifications; `appearance.reduce_motion`. (Not Framer Motion — React-only.)

## Layout
Left nav compact: **REALM logo + identity** + Home, Calendar, Notes,
Tasks, File Manager, Gaming, Media, Network, Settings. Active = subtle
crimson + **thin gold indicator** + gold icons + hover. Top bar: search,
date/time, notifications, user/profile, quick settings. Spacious central workspace.

## Application cards (`QFrame#Card` + QML `GlassCard`)
dark glass, subtle border, rounded, **crimson glow on hover**, gold accents,
scale + elevation; consistent spacing. `QGraphicsDropShadowEffect`.

## Home
welcome, recently opened, favorites, upcoming events, pending tasks,
recently opened notes, recently played games; elegant hover; not a cluttered dashboard.
(recently played games + notes/events/tasks already queried; apps grid).

## Module language
Global restyle applies to **all 21 apps**; calendar crimson events + gold
selection; notes clean dark surface + gold active; tasks/priority +
Kanban; file manager clean icons + crimson selection; gaming large art +
play; media artwork/playlists + immersive controls; network readable +
graphs; settings organized. No module removed; no functionality replaced.

## Logo / brand
- **`REALM OS LOGO.png`** (user-provided REALM logo, NOT Riot) →
  window icon + sidebar + packaging. 
- **Original `assets/icons/realm-symbol.svg`** — abstract geometric,
  crimson+gold, **no letters, not a recognizable existing logo**;
  `ui.icons.realm_symbol()`; works on dark + light; app icon + sidebar fallback.
- No copyrighted Riot Client assets.

## Reusable QML (`ui/qml/`)
`BlurredBackground.qml`, `GlassCard.qml`, `RealmButton.qml`,
`LoadingSpinner.qml`, `PageTransition.qml`. Centralized theme tokens.

## Compatibility / quality
PySide6 + Qt Quick; existing SQLite + modules; backward-compatible DB;
resize + fullscreen; readable contrast; software rendering; no extra deps;
**65 tests**; `compileall`.
