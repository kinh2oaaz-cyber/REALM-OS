# Icons — real web symbols, not emoji

Per requirement, REALM OS uses **real logo/symbol SVGs sourced from the
web, bundled offline**, **not emoji**.

- **Source:** **Tabler Icons** (MIT), `@tabler/icons@3.30.0` outline set,
  fetched once from `https://cdn.jsdelivr.net/npm/@tabler/icons@...`
  into `assets/icons/*.svg`. License: `assets/icons/LICENSE-tabler.txt`.
- **Runtime offline:** icons are bundled; no internet needed.
- `ui/icons.py`:
  - `icon(name, color=None, size=20) -> QIcon` (recolors `currentColor`
    to match theme, e.g. gold on red; cached).
  - `app_icon(app_id, color, size)`, `app_icon_name`, `has_icon`.
  - `APP_ICONS` maps every app id → symbol. `APP_LOGO="hexagon"`.
  - `QSvgRenderer`.
- **App identity:** `AppInfo.icon` is a symbol name; `Sidebar` +
  `HomePage` render `QIcon`. No emoji app icons.
- **Shell:** top bar (bell, search, bolt, sun/moon, settings), pin,
  lock, paperclip, plus, play/pause/stop, star, folder, etc. use SVGs.
- **REALM OS logo:** bundled `assets/icons/realmos.svg` + web `hexagon`
  symbol.

## Remaining typographic glyphs
Only typographic `＋`/`－`/`·` are used in plain text; **no emoji**.
Curated `ACCENT_PRESETS` colors are unaffected.
