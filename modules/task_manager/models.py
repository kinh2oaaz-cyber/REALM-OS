"""Task data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

STATUSES = ("todo", "in_progress", "done")
KANBAN_COLUMNS = ("todo", "in_progress", "done")
PRIORITIES = {0: "Low", 1: "Normal", 2: "High", 3: "Urgent"}
PRIORITY_LABELS = list(PRIORITIES.values())


@dataclass
class Task:
    id: int | None = None
    title: str = ""
    description: str = ""
    status: str = "todo"
    kanban_column: str = "todo"
    priority: int = 1
    category: str = ""
    deadline: str | None = None
    created_at: str | None = None
    updated_at: str | None = None
    completed_at: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Task":
        return cls(
            id=row.get("id"),
            title=row.get("title", ""),
            description=row.get("description", ""),
            status=row.get("status", "todo"),
            kanban_column=row.get("kanban_column", "todo"),
            priority=int(row.get("priority", 1)),
            category=row.get("category", ""),
            deadline=row.get("deadline"),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            completed_at=row.get("completed_at"),
        )

    @property
    def is_done(self) -> bool:
        return self.status == "done"
