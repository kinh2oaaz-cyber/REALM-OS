"""Notification service backed by the shared database.

Notifications are in-app (no OS toast requirement). Emits
``notification.added`` / ``notification.read`` on the event bus.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database import Database

    from .event_bus import EventBus

LEVELS = ("info", "success", "warning", "error")


@dataclass
class Notification:
    id: int
    title: str
    message: str
    app_id: str | None
    level: str
    read: bool
    created_at: str

    @classmethod
    def from_row(cls, row: dict) -> "Notification":
        return cls(
            id=row["id"],
            title=row["title"],
            message=row["message"],
            app_id=row.get("app_id"),
            level=row.get("level", "info"),
            read=bool(row.get("read", 0)),
            created_at=row["created_at"],
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "app_id": self.app_id,
            "level": self.level,
            "read": self.read,
            "created_at": self.created_at,
        }


class NotificationService:
    def __init__(self, db: "Database", event_bus: "EventBus") -> None:
        self._db = db
        self._bus = event_bus

    def add(
        self,
        title: str,
        message: str = "",
        app_id: str | None = None,
        level: str = "info",
    ) -> Notification:
        if level not in LEVELS:
            level = "info"
        cur = self._db.execute(
            """
            INSERT INTO notifications (title, message, app_id, level, read, created_at)
            VALUES (?, ?, ?, ?, 0, datetime('now'))
            """,
            (title, message, app_id, level),
        )
        note = self.get(int(cur.lastrowid))
        assert note is not None
        self._bus.publish("notification.added", note.to_dict())
        return note

    def get(self, note_id: int) -> Notification | None:
        row = self._db.query_one("SELECT * FROM notifications WHERE id = ?", (note_id,))
        return Notification.from_row(row) if row else None

    def list(self, limit: int = 50, unread_only: bool = False) -> list[Notification]:
        sql = "SELECT * FROM notifications"
        if unread_only:
            sql += " WHERE read = 0"
        sql += " ORDER BY created_at DESC, id DESC LIMIT ?"
        return [Notification.from_row(r) for r in self._db.query(sql, (limit,))]

    def unread_count(self) -> int:
        row = self._db.query_one("SELECT COUNT(*) AS c FROM notifications WHERE read = 0")
        return int(row["c"]) if row else 0

    def mark_read(self, note_id: int) -> None:
        self._db.execute("UPDATE notifications SET read = 1 WHERE id = ?", (note_id,))
        self._bus.publish("notification.read", {"id": note_id})

    def mark_all_read(self) -> None:
        self._db.execute("UPDATE notifications SET read = 1 WHERE read = 0")
        self._bus.publish("notification.read", {"id": None})

    def clear(self) -> None:
        self._db.execute("DELETE FROM notifications")
