"""Calendar database access layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from database import Database

from .models import CalendarEvent, DEFAULT_CATEGORIES


class CalendarRepository:
    def __init__(self, db: "Database") -> None:
        self.db = db

    def seed_categories(self) -> None:
        for name, color in DEFAULT_CATEGORIES.items():
            self.db.execute(
                "INSERT OR IGNORE INTO calendar_categories (name, color) VALUES (?, ?)", (name, color)
            )

    def list_categories(self) -> list[dict[str, Any]]:
        return self.db.query("SELECT name, color FROM calendar_categories ORDER BY name")

    def add_category(self, name: str, color: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO calendar_categories (name, color) VALUES (?, ?)", (name, color))

    def all_events(self) -> list[CalendarEvent]:
        return [CalendarEvent.from_row(r) for r in self.db.query("SELECT * FROM calendar_events ORDER BY start")]

    def get(self, event_id: int) -> CalendarEvent | None:
        row = self.db.query_one("SELECT * FROM calendar_events WHERE id = ?", (event_id,))
        return CalendarEvent.from_row(row) if row else None

    def search(self, query: str) -> list[CalendarEvent]:
        like = f"%{query.strip()}%"
        rows = self.db.query(
            "SELECT * FROM calendar_events WHERE title LIKE ? OR description LIKE ? OR location LIKE ? "
            "OR category LIKE ? ORDER BY start",
            (like, like, like, like),
        )
        return [CalendarEvent.from_row(r) for r in rows]

    def create(self, event: CalendarEvent) -> int:
        data = event.to_dict()
        cur = self.db.execute(
            """
            INSERT INTO calendar_events
                (title, description, location, start, end, all_day, category, color, recurring_rule, reminder_minutes, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """,
            (
                data["title"], data["description"], data["location"], data["start"], data["end"],
                1 if data["all_day"] else 0, data["category"], data["color"], data["recurring_rule"],
                data["reminder_minutes"],
            ),
        )
        return int(cur.lastrowid)

    def update(self, event: CalendarEvent) -> None:
        data = event.to_dict()
        self.db.execute(
            """
            UPDATE calendar_events SET
                title=?, description=?, location=?, start=?, end=?, all_day=?, category=?, color=?,
                recurring_rule=?, reminder_minutes=?, updated_at=datetime('now')
            WHERE id=?
            """,
            (
                data["title"], data["description"], data["location"], data["start"], data["end"],
                1 if data["all_day"] else 0, data["category"], data["color"], data["recurring_rule"],
                data["reminder_minutes"], event.id,
            ),
        )

    def delete(self, event_id: int) -> None:
        self.db.execute("DELETE FROM calendar_events WHERE id = ?", (event_id,))
