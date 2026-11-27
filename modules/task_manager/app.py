"""Task Manager registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import TasksPage

APP_ID = "tasks"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Tasks",
            description="Personal task manager + PC task manager",
            icon="list-check",
            category="apps",
            order=30,
            keywords=("task", "tasks", "todo", "kanban", "process", "pc", "processes", "cpu", "ram"),
            page_factory=lambda c: TasksPage(c),
        )
    )
