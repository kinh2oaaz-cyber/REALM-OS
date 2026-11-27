"""Calendar data models."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any

# Color-coded categories
DEFAULT_CATEGORIES: dict[str, str] = {
    "Work": "#0071E3",
    "Personal": "#34C759",
    "Family": "#FF9500",
    "Health": "#FF2D55",
    "Birthdays": "#AF52DE",
    "Holiday": "#30B0C7",
}

RECURRENCE_FREQS = ("NONE", "DAILY", "WEEKLY", "MONTHLY", "YEARLY")


@dataclass
class Recurrence:
    freq: str = "NONE"          # NONE | DAILY | WEEKLY | MONTHLY | YEARLY
    interval: int = 1
    count: int | None = None     # number of occurrences
    until: str | None = None     # ISO date/datetime end
    byweekday: list[int] = field(default_factory=list)  # 0=Mon..6=Sun for WEEKLY

    def to_json(self) -> str:
        if self.freq == "NONE":
            return ""
        return json.dumps(
            {
                "freq": self.freq,
                "interval": max(1, self.interval),
                "count": self.count,
                "until": self.until,
                "byweekday": self.byweekday,
            }
        )

    @classmethod
    def from_json(cls, raw: str) -> "Recurrence":
        if not raw:
            return cls()
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return cls()
        return cls(
            freq=str(data.get("freq", "NONE")),
            interval=int(data.get("interval", 1) or 1),
            count=data.get("count"),
            until=data.get("until"),
            byweekday=list(data.get("byweekday", []) or []),
        )


@dataclass
class CalendarEvent:
    id: int | None = None
    title: str = ""
    description: str = ""
    location: str = ""
    start: str = ""                 # ISO 8601 'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD'
    end: str = ""
    all_day: bool = False
    category: str = ""
    color: str = ""
    recurrence: Recurrence = field(default_factory=Recurrence)
    reminder_minutes: int = -1       # -1 = no reminder
    created_at: str | None = None
    updated_at: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "CalendarEvent":
        return cls(
            id=row.get("id"),
            title=row.get("title", ""),
            description=row.get("description", ""),
            location=row.get("location", ""),
            start=row.get("start", ""),
            end=row.get("end", ""),
            all_day=bool(row.get("all_day", 0)),
            category=row.get("category", ""),
            color=row.get("color", ""),
            recurrence=Recurrence.from_json(row.get("recurring_rule", "")),
            reminder_minutes=int(row.get("reminder_minutes", -1)),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "location": self.location,
            "start": self.start,
            "end": self.end,
            "all_day": self.all_day,
            "category": self.category,
            "color": self.color,
            "recurring_rule": self.recurrence.to_json(),
            "reminder_minutes": self.reminder_minutes,
        }
