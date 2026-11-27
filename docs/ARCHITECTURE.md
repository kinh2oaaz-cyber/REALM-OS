# REALM OS Architecture

## Guiding principles

1. **Modular** — every application is a self-contained package; the shell
   knows nothing about individual modules, only `AppInfo`.
2. **Shared core** — one `AppContext` of reusable services (database,
   settings, event bus, notifications, theme, registry) passed everywhere.
3. **Local-first** — single SQLite database; no network required; no
   telemetry (`privacy.telemetry` defaults false and is never sent).
4. **Real functionality** — no fake buttons; un-built apps are honest
   scaffolds for their assigned phase.
5. **Reversible & safe** — parameterized SQL; forward-only migrations;
   confirmation before destructive actions; normal Windows permissions.

## Layering

```
app/        -> core + database + modules + ui
modules/*   -> core + database + ui (+ system)
ui/*        -> core (context, theme tokens); no module depends on another module's UI
core/*      -> (no Qt in event_bus/settings; Qt only in theme/context)
database/*  -> standalone (sqlite3); no Qt
system/*    -> psutil; standalone
security/*  -> stdlib; standalone
```

## Phase 1 shell data flow

```
QApplication
  └─ RealmOSApplication
       ├─ ensure_dirs() + setup_logging()
       ├─ Database(...).initialize()          # run_migrations
       ├─ EventBus
       ├─ Settings(db)
       ├─ NotificationService(db, bus)
       ├─ ThemeManager(settings, app)
       ├─ AppRegistry(db)
       ├─ AppContext(...)                     # shared services
       ├─ register_all_modules(registry, ctx) # modules register AppInfo
       ├─ ThemeManager.apply_saved()
       └─ MainWindow(context)
            ├─ Sidebar          (navigate signal -> navigate())
            ├─ TopBar           (search / clock / notifications / quick actions / prefs)
            └─ QStackedWidget   (lazy page_factory(context) per app)
```

## Navigation

`MainWindow.navigate(app_id)`. Modules request navigation by publishing
`navigation.requested {"app_id": ...}` on the event bus
(`AppContext.navigate`). Pages are created lazily on first open,
receive `on_show`/`on_hide`, and exceptions are logged without breaking
the shell. Favorites + recently opened persist in SQLite.

## Event bus (cross-module shared system)

`navigation.requested`, `app.opened`, `app.favorite_changed`,
`notification.added`, `notification.read`, `theme.changed`,
`global.search`. Future phases add e.g. `task.created`, `event.created`,
`note.updated`, `media.played`. The generic `item_links` table backs
Calendar→Task, Task→Note, Note→File, etc.

## Database

Single shared SQLite DB at `<data>/database/realmos.db`. WAL, foreign
keys on, `RLock`, transaction context manager, online `backup()`.
Forward-only integer migrations in `database/schema.py`
(`schema_migrations`). Parameterized SQL everywhere.

### Tables (schema v1)

- core: `app_meta`, `settings`, `app_favorites`, `app_recents`,
  `notifications`, `item_links`, `schema_migrations`
- calendar: `calendar_events`, `calendar_categories`
- notes: `notes`, `note_folders`, `note_attachments`
- tasks: `tasks`, `task_categories`
- file manager: `recent_files`, `favorite_files`
- gaming: `games`, `game_sessions`
- media: `media_tracks`, `playlists`, `playlist_items`, `media_history`
- network: `network_history`

## Where each file belongs

### `app/`
- `main.py` — `main()` entry; `python -m app.main`; graceful fatal handler.
- `application.py` — `RealmOSApplication`: dirs, logging, DB, services, registry, theme, window; shutdown.
- root `main.py` — convenience launcher; adds project root to `sys.path`.

### `core/`
- `config.py` — app name/version, `project_root`, `data_dir`, `database_path`, `ensure_dirs`, `is_windows`.
- `logging_setup.py` — `setup_logging`, `get_logger`; rotating file + console.
- `event_bus.py` — `EventBus`.
- `settings.py` — `Settings` (JSON, typed getters, `DEFAULTS`).
- `app_registry.py` — `AppInfo`, `AppRegistry` (register/search/favorites/recents), `HOME_ID`.
- `notifications.py` — `Notification`, `NotificationService`.
- `module_base.py` — `RealmModule`.
- `context.py` — `AppContext`.

### `database/`
- `connection.py` — `Database`.
- `schema.py` — `MIGRATIONS`, `run_migrations`, `CURRENT_SCHEMA_VERSION`.
- `repositories.py` — `Repository` base.
- `migrations/` — reserved for future versioned migration files.

### `ui/`
- `main_window.py` — `MainWindow`.
- `components/` — `Sidebar`, `TopBar`, `SearchBox`, `Card`, `EmptyState`,
  `ScaffoldPage`, `NotificationsPanel`, `quick_actions`, `RealmPage`.
- `pages/` — `HomePage`.
- `themes/` — `tokens.py`, `theme_manager.py`, `base.qss`.

### `modules/<app>/`
- `__init__.py`, `app.py` (`register`), `page.py`, `models.py`,
  `services.py`, `database.py`, `ui/`. `modules/registry.py`
  `register_all_modules`.

### `system/` — `info.py` (read-only psutil).
### `security/` — `passwords.py` (PBKDF2).
### `integrations/` — optional third-party (empty in Phase 1).
### `assets/` — `icons/`.
### `tests/` — `unittest`; `_base.py`; `test_*.py`.
### `scripts/` — PowerShell. `packaging/` — PyInstaller spec.
### `logs/`, `docs/`.

## Design system (Apple-inspired minimalist)

- Neutral backgrounds, one subtle accent; rounded corners (card 12 /
  control 8); subtle borders; light & dark; `Fusion` + generated QSS.
- Typography: Segoe UI; 13px base; 600/700 weights for headings.
- `ThemeManager`: `system|light|dark`, accent hex (validated),
  font family/size; persisted; `theme_changed`.
- No neon, no sci-fi HUD, no decorative orbs, minimal motion.

## Error handling

- `setup_logging` never raises; DB dir creation guarded; migrations
  roll back; `EventBus` isolates subscriber failures; `MainWindow`
  catches per-page factory/show errors; `main()` has a fatal handler;
  `QMessageBox` on DB-init failure.

## Testing

`python -m unittest discover -s tests -t .`. UI smoke test runs
`QT_QPA_PLATFORM=offscreen`.
