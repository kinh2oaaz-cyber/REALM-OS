"""Calendar registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import CalendarPage

APP_ID = "calendar"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Calendar",
            description="Monthly, weekly and daily views; events, reminders, categories",
            icon="calendar",
            category="apps",
            order=10,
            keywords=("calendar", "events", "schedule", "reminder", "date", "agenda"),
            page_factory=lambda c: CalendarPage(c),
        )
    )
