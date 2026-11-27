"""Typed key/value settings persisted in the shared SQLite database.

Settings keys are dotted namespaces, e.g. ``appearance.theme``,
``appearance.accent``, ``startup.open_last``. Values are JSON encoded
so booleans, numbers, strings, lists and dicts round-trip safely.
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from database import Database

# Defaults applied when a key has never been set.
DEFAULTS: dict[str, Any] = {
    "appearance.theme": "redgold",  # redgold | system | light | dark
    "appearance.accent": "#C8AA6E",
    "appearance.font_family": "Segoe UI",
    "appearance.font_size": 13,
    "appearance.reduce_motion": False,
    "startup.open_last": False,
    "startup.start_hidden": False,
    "notifications.enabled": True,
    "privacy.telemetry": False,  # local-first: never sends anything anywhere
    "app.last_app": "home",
}


class Settings:
    def __init__(self, db: "Database") -> None:
        self._db = db

    # -- core -----------------------------------------------------------
    def get(self, key: str, default: Any = None) -> Any:
        row = self._db.query_one("SELECT value FROM settings WHERE key = ?", (key,))
        if row is None:
            if default is not None:
                return default
            return DEFAULTS.get(key)
        try:
            return json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return row["value"]

    def set(self, key: str, value: Any) -> None:
        payload = json.dumps(value)
        self._db.execute(
            """
            INSERT INTO settings (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
            """,
            (key, payload),
        )

    def remove(self, key: str) -> None:
        self._db.execute("DELETE FROM settings WHERE key = ?", (key,))

    def keys(self) -> list[str]:
        rows = self._db.query("SELECT key FROM settings ORDER BY key")
        return [r["key"] for r in rows]

    def as_dict(self) -> dict[str, Any]:
        return {k: self.get(k) for k in self.keys()}

    def reset_all(self) -> None:
        self._db.execute("DELETE FROM settings")

    # -- typed helpers --------------------------------------------------
    def get_bool(self, key: str, default: bool = False) -> bool:
        value = self.get(key, default)
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "yes", "on"}
        return bool(value)

    def get_int(self, key: str, default: int = 0) -> int:
        value = self.get(key, default)
        try:
            return int(value)
        except (TypeError, ValueError):
            return default

    def get_str(self, key: str, default: str = "") -> str:
        value = self.get(key, default)
        return default if value is None else str(value)
