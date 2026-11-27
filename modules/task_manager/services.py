"""Personal task service."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import AppContext

from .database import TaskRepository
from .models import Task


class TaskService:
    def __init__(self, ctx: "AppContext") -> None:
        self.ctx = ctx
        self.repo = TaskRepository(ctx.db)

    def create_task(self, title: str, description: str = "", priority: int = 1, category: str = "",
                    deadline: str | None = None) -> int:
        task = Task(title=title, description=description, priority=priority, category=category, deadline=deadline)
        task_id = self.repo.create(task)
        self.ctx.event_bus.publish("task.created", {"task_id": task_id})
        return task_id

    def update_task(self, task: Task) -> None:
        self.repo.update(task)
        self.ctx.event_bus.publish("task.updated", {"task_id": task.id})

    def delete_task(self, task_id: int) -> None:
        self.repo.delete(task_id)
        self.ctx.event_bus.publish("task.deleted", {"task_id": task_id})

    def set_status(self, task_id: int, status: str) -> None:
        task = self.repo.get(task_id)
        if not task:
            return
        task.status = status
        task.kanban_column = status
        task.completed_at = datetime.now().isoformat(timespec="seconds") if status == "done" else None
        self.repo.update(task)
        self.ctx.event_bus.publish("task.updated", {"task_id": task_id})

    def toggle_done(self, task_id: int) -> None:
        task = self.repo.get(task_id)
        if task:
            self.set_status(task_id, "todo" if task.is_done else "done")

    def move_to_column(self, task_id: int, column: str) -> None:
        self.set_status(task_id, column)

    # link task -> note (shared system) --------------------------------
    def link_note(self, task_id: int, note_id: int) -> None:
        self.ctx.db.execute(
            "INSERT INTO item_links (from_app, from_id, to_app, to_id, relation) VALUES ('tasks', ?, 'notes', ?, 'related')",
            (str(task_id), str(note_id)))

    def linked_notes(self, task_id: int) -> list[int]:
        rows = self.ctx.db.query(
            "SELECT to_id FROM item_links WHERE from_app='tasks' AND from_id=? AND to_app='notes'", (str(task_id),))
        return [int(r["to_id"]) for r in rows]

    # daily / weekly views ---------------------------------------------
    def daily(self, day: datetime | None = None) -> list[Task]:
        day = day or datetime.now()
        start = day.strftime("%Y-%m-%d")
        end = (day + timedelta(days=1)).strftime("%Y-%m-%d")
        pending = [t for t in self.repo.pending(500) if (t.deadline or "").startswith(start) or not t.deadline]
        due = self.repo.due_between(start, end)
        seen = {t.id for t in due}
        return due + [t for t in pending if t.id not in seen and (t.deadline or "").startswith(start)]

    def weekly(self) -> list[Task]:
        now = datetime.now()
        start = now.strftime("%Y-%m-%d")
        end = (now + timedelta(days=7)).strftime("%Y-%m-%d %H:%M")
        return self.repo.due_between(start, end)

    def counts(self) -> dict[str, int]:
        return self.repo.counts()
