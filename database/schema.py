"""SQLite schema and forward-only migrations.

Migration version N is applied once, in order, inside a transaction.
Add new entries to ``MIGRATIONS`` with increasing version numbers;
never edit an already-released migration.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .connection import Database

CURRENT_SCHEMA_VERSION = 2

# Core Phase 1 schema (version 1) + per-module tables so every app
# shares one consistent local database. Module-specific columns will
# be extended in later phases with additive migrations.
_V1 = """
CREATE TABLE IF NOT EXISTS schema_migrations (
    version     INTEGER PRIMARY KEY,
    applied_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS app_meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS app_favorites (
    app_id   TEXT PRIMARY KEY,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS app_recents (
    app_id    TEXT PRIMARY KEY,
    opened_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS notifications (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    message    TEXT NOT NULL DEFAULT '',
    app_id     TEXT,
    level      TEXT NOT NULL DEFAULT 'info',
    read       INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(read);
CREATE INDEX IF NOT EXISTS idx_notifications_created ON notifications(created_at);

-- Generic cross-module links (Calendar->Task, Task->Note, Note->File, ...)
CREATE TABLE IF NOT EXISTS item_links (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    from_app    TEXT NOT NULL,
    from_id     TEXT NOT NULL,
    to_app      TEXT NOT NULL,
    to_id       TEXT NOT NULL,
    relation    TEXT NOT NULL DEFAULT 'related',
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_links_from ON item_links(from_app, from_id);
CREATE INDEX IF NOT EXISTS idx_links_to ON item_links(to_app, to_id);

-- ============================ Calendar ============================
CREATE TABLE IF NOT EXISTS calendar_categories (
    name  TEXT PRIMARY KEY,
    color TEXT NOT NULL DEFAULT '#0071E3'
);
CREATE TABLE IF NOT EXISTS calendar_events (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    title            TEXT NOT NULL,
    description      TEXT NOT NULL DEFAULT '',
    location         TEXT NOT NULL DEFAULT '',
    start            TEXT NOT NULL,
    end              TEXT NOT NULL,
    all_day          INTEGER NOT NULL DEFAULT 0,
    category         TEXT NOT NULL DEFAULT '',
    color            TEXT NOT NULL DEFAULT '',
    recurring_rule   TEXT NOT NULL DEFAULT '',   -- RRULE-like string; '' = none
    reminder_minutes INTEGER NOT NULL DEFAULT -1, -- -1 = no reminder
    created_at       TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at       TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_events_start ON calendar_events(start);
CREATE INDEX IF NOT EXISTS idx_events_end ON calendar_events(end);

-- ============================= Notes ==============================
CREATE TABLE IF NOT EXISTS note_folders (
    name TEXT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS notes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL DEFAULT 'Untitled',
    content         TEXT NOT NULL DEFAULT '',
    format          TEXT NOT NULL DEFAULT 'markdown', -- markdown | richtext | plain
    folder          TEXT NOT NULL DEFAULT '',
    category        TEXT NOT NULL DEFAULT '',
    pinned          INTEGER NOT NULL DEFAULT 0,
    protected       INTEGER NOT NULL DEFAULT 0,        -- password-protected
    word_count      INTEGER NOT NULL DEFAULT 0,
    char_count      INTEGER NOT NULL DEFAULT 0,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now')),
    last_accessed_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_notes_updated ON notes(updated_at);
CREATE INDEX IF NOT EXISTS idx_notes_accessed ON notes(last_accessed_at);
CREATE INDEX IF NOT EXISTS idx_notes_folder ON notes(folder);
CREATE TABLE IF NOT EXISTS note_attachments (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    note_id INTEGER NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    path    TEXT NOT NULL,
    name    TEXT NOT NULL DEFAULT '',
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ======================== Personal Tasks ==========================
CREATE TABLE IF NOT EXISTS task_categories (
    name TEXT PRIMARY KEY
);
CREATE TABLE IF NOT EXISTS tasks (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    title        TEXT NOT NULL,
    description  TEXT NOT NULL DEFAULT '',
    status       TEXT NOT NULL DEFAULT 'todo',   -- todo | in_progress | done
    kanban_column TEXT NOT NULL DEFAULT 'todo',
    priority     INTEGER NOT NULL DEFAULT 1,      -- 0 low,1 normal,2 high,3 urgent
    category     TEXT NOT NULL DEFAULT '',
    deadline     TEXT,                            -- ISO 8601 or NULL
    created_at   TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at   TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_deadline ON tasks(deadline);
CREATE INDEX IF NOT EXISTS idx_tasks_kanban ON tasks(kanban_column);

-- ========================= File Manager ===========================
CREATE TABLE IF NOT EXISTS recent_files (
    path      TEXT PRIMARY KEY,
    opened_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS favorite_files (
    path     TEXT PRIMARY KEY,
    added_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ========================== Gaming Hub ============================
CREATE TABLE IF NOT EXISTS games (
    id                    INTEGER PRIMARY KEY AUTOINCREMENT,
    name                  TEXT NOT NULL,
    exe_path              TEXT NOT NULL DEFAULT '',
    cover_path            TEXT NOT NULL DEFAULT '',
    icon_path             TEXT NOT NULL DEFAULT '',
    category              TEXT NOT NULL DEFAULT '',
    favorite              INTEGER NOT NULL DEFAULT 0,
    total_playtime_seconds INTEGER NOT NULL DEFAULT 0,
    last_played_at        TEXT,
    added_at              TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS game_sessions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    game_id     INTEGER NOT NULL REFERENCES games(id) ON DELETE CASCADE,
    started_at  TEXT NOT NULL,
    ended_at    TEXT,
    duration_seconds INTEGER NOT NULL DEFAULT 0
);

-- ========================= Media Center ===========================
CREATE TABLE IF NOT EXISTS media_tracks (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    path       TEXT NOT NULL UNIQUE,
    title      TEXT NOT NULL DEFAULT '',
    artist     TEXT NOT NULL DEFAULT '',
    album      TEXT NOT NULL DEFAULT '',
    duration_seconds REAL NOT NULL DEFAULT 0,
    added_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS playlists (
    id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS playlist_items (
    playlist_id INTEGER NOT NULL REFERENCES playlists(id) ON DELETE CASCADE,
    track_id    INTEGER NOT NULL REFERENCES media_tracks(id) ON DELETE CASCADE,
    position    INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (playlist_id, track_id)
);
CREATE TABLE IF NOT EXISTS media_history (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    track_id  INTEGER NOT NULL REFERENCES media_tracks(id) ON DELETE CASCADE,
    played_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ======================== Network Monitor =========================
CREATE TABLE IF NOT EXISTS network_history (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    recorded_at  TEXT NOT NULL DEFAULT (datetime('now')),
    download_bps REAL NOT NULL DEFAULT 0,
    upload_bps   REAL NOT NULL DEFAULT 0,
    latency_ms   REAL
);
"""

_V2 = """
-- ====================== Password Vault (Phase 9) ======================
CREATE TABLE IF NOT EXISTS vault_entries (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    username    TEXT NOT NULL DEFAULT '',
    password    TEXT NOT NULL DEFAULT '',   -- encrypted at rest (Fernet)
    url         TEXT NOT NULL DEFAULT '',
    notes       TEXT NOT NULL DEFAULT '',   -- encrypted at rest
    category    TEXT NOT NULL DEFAULT '',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ================== Personal Finance (Phase 9) ========================
CREATE TABLE IF NOT EXISTS finance_transactions (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    kind      TEXT NOT NULL DEFAULT 'expense',  -- income | expense
    amount    REAL NOT NULL DEFAULT 0,
    category  TEXT NOT NULL DEFAULT '',
    note      TEXT NOT NULL DEFAULT '',
    date      TEXT NOT NULL DEFAULT (date('now')),
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_finance_date ON finance_transactions(date);

-- ======================== Project Manager =============================
CREATE TABLE IF NOT EXISTS projects (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'active',  -- active | paused | done
    color       TEXT NOT NULL DEFAULT '#0071E3',
    start_date  TEXT,
    due_date    TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ======================== Clipboard Manager ===========================
CREATE TABLE IF NOT EXISTS clipboard_items (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    content    TEXT NOT NULL,
    source     TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ======================== Download Manager ============================
CREATE TABLE IF NOT EXISTS downloads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    url         TEXT NOT NULL,
    filename    TEXT NOT NULL DEFAULT '',
    destination TEXT NOT NULL DEFAULT '',
    status      TEXT NOT NULL DEFAULT 'queued',
    bytes_done  INTEGER NOT NULL DEFAULT 0,
    bytes_total INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    finished_at TEXT
);
"""

MIGRATIONS: list[tuple[int, str]] = [
    (1, _V1),
    (2, _V2),
]


def applied_versions(db: "Database") -> set[int]:
    rows = db.query("SELECT version FROM schema_migrations")
    return {int(r["version"]) for r in rows}


def run_migrations(db: "Database") -> None:
    """Apply all pending migrations in order, atomically per version."""
    db.executescript(
        "CREATE TABLE IF NOT EXISTS schema_migrations ("
        "version INTEGER PRIMARY KEY, applied_at TEXT NOT NULL DEFAULT (datetime('now')));"
    )
    done = applied_versions(db)
    conn = db.conn
    for version, sql in sorted(MIGRATIONS, key=lambda m: m[0]):
        if version in done:
            continue
        # sqlite3.executescript implicitly commits first and does not wrap
        # the script in a transaction, so embed BEGIN/COMMIT ourselves.
        script = (
            "BEGIN IMMEDIATE;\n"
            + sql
            + f"\nINSERT INTO schema_migrations (version) VALUES ({int(version)});\nCOMMIT;"
        )
        try:
            conn.executescript(script)
        except Exception:
            try:
                conn.execute("ROLLBACK")
            except Exception:
                pass
            raise
        done.add(version)
    conn.commit()
