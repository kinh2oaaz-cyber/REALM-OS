"""Calendar application service."""

from __future__ import annotations

from datetime import datetime, time, timedelta
from typing import TYPE_CHECKING

from core.logging_setup import get_logger

if TYPE_CHECKING:
    from core.context import AppContext

from .database import CalendarRepository
from .models import CalendarEvent
from .recurrence import expand_events

_log = get_logger("calendar")


def _day_bounds(day: datetime) -> tuple[datetime, datetime]:
    start = datetime.combine(day.date(), time(0, 0))
    return start, start + timedelta(days=1)


class CalendarService:
    def __init__(self, ctx: "AppContext") -> None:
        self.ctx = ctx
        self.repo = CalendarRepository(ctx.db)
        try:
            self.repo.seed_categories()
        except Exception:  # noqa: BLE001
            _log.exception("Could not seed calendar categories")

    # CRUD --------------------------------------------------------------
    def create_event(self, event: CalendarEvent) -> int:
        event_id = self.repo.create(event)
        self.ctx.event_bus.publish("event.created", {"event_id": event_id})
        return event_id

    def update_event(self, event: CalendarEvent) -> None:
        self.repo.update(event)
        self.ctx.event_bus.publish("event.updated", {"event_id": event.id})

    def delete_event(self, event_id: int) -> None:
        self.repo.delete(event_id)
        self.ctx.event_bus.publish("event.deleted", {"event_id": event_id})

    def get_event(self, event_id: int) -> CalendarEvent | None:
        return self.repo.get(event_id)

    def search(self, query: str) -> list[CalendarEvent]:
        return self.repo.search(query)

    def categories(self) -> list[dict]:
        return self.repo.list_categories()

    # queries -----------------------------------------------------------
    def events_in_range(self, range_start: datetime, range_end: datetime) -> list[CalendarEvent]:
        base = self.repo.all_events()
        return expand_events(base, range_start, range_end)

    def events_on_day(self, day: datetime) -> list[CalendarEvent]:
        start, end = _day_bounds(day)
        return self.events_in_range(start, end)

    def today_schedule(self) -> list[CalendarEvent]:
        return self.events_on_day(datetime.now())

    def upcoming(self, days: int = 7, limit: int = 50) -> list[CalendarEvent]:
        now = datetime.now()
        return self.events_in_range(now, now + timedelta(days=days))[:limit]

    # shared-system: create a related task -----------------------------
    def create_task_from_event(self, event_id: int) -> int | None:
        event = self.repo.get(event_id)
        if event is None:
            return None
        try:
            cur = self.ctx.db.execute(
                "INSERT INTO tasks (title, description, deadline, category, status) VALUES (?, ?, ?, ?, 'todo')",
                (event.title, event.description, event.start, event.category or "Calendar"),
            )
            task_id = int(cur.lastrowid)
            self.ctx.db.execute(
                "INSERT INTO item_links (from_app, from_id, to_app, to_id, relation) VALUES ('calendar', ?, 'tasks', ?, 'related')",
                (str(event_id), str(task_id)),
            )
            self.ctx.event_bus.publish("task.created", {"task_id": task_id})
            return task_id
        except Exception:  # noqa: BLE001
            _log.exception("Could not create task from event")
            return None

    # reminders ---------------------------------------------------------
    def due_reminders(self, now: datetime | None = None, window_minutes: int = 1) -> list[CalendarEvent]:
        """Events whose reminder trigger time is within [now-window, now+window]."""
        now = now or datetime.now()
        results: list[CalendarEvent] = []
        for event in self.repo.all_events():
            if event.reminder_minutes < 0:
                continue
            start = datetime.strptime(event.start[:16], "%Y-%m-%d %H:%M") if event.start else now
            trigger = start - timedelta(minutes=event.reminder_minutes)
            if abs((trigger - now).total_seconds()) <= window_minutes * 60:
                results.append(event)
        return results
