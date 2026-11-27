"""Personal task database access."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from database import Database

from .models import Task


class TaskRepository:
    def __init__(self, db: "Database") -> None:
        self.db = db

    def list_all(self, order_by: str = " (deadline IS NULL), deadline ASC, priority DESC") -> list[Task]:
        return [Task.from_row(r) for r in self.db.query(f"SELECT * FROM tasks ORDER BY{order_by}")]

    def by_column(self, column: str) -> list[Task]:
        return [Task.from_row(r) for r in self.db.query(
            "SELECT * FROM tasks WHERE kanban_column=? ORDER BY priority DESC, (deadline IS NULL), deadline", (column,))]

    def get(self, task_id: int) -> Task | None:
        row = self.db.query_one("SELECT * FROM tasks WHERE id=?", (task_id,))
        return Task.from_row(row) if row else None

    def search(self, query: str) -> list[Task]:
        like = f"%{query.strip()}%"
        return [Task.from_row(r) for r in self.db.query(
            "SELECT * FROM tasks WHERE title LIKE ? OR description LIKE ? OR category LIKE ? ORDER BY updated_at DESC",
            (like, like, like))]

    def create(self, task: Task) -> int:
        cur = self.db.execute(
            "INSERT INTO tasks (title, description, status, kanban_column, priority, category, deadline, updated_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))",
            (task.title, task.description, task.status, task.kanban_column, task.priority, task.category, task.deadline))
        return int(cur.lastrowid)

    def update(self, task: Task) -> None:
        self.db.execute(
            "UPDATE tasks SET title=?, description=?, status=?, kanban_column=?, priority=?, category=?, deadline=?, "
            "completed_at=?, updated_at=datetime('now') WHERE id=?",
            (task.title, task.description, task.status, task.kanban_column, task.priority, task.category,
             task.deadline, task.completed_at, task.id))

    def delete(self, task_id: int) -> None:
        self.db.execute("DELETE FROM tasks WHERE id=?", (task_id,))

    def categories(self) -> list[str]:
        return [r["category"] for r in self.db.query("SELECT DISTINCT category FROM tasks WHERE category!='' ORDER BY category")]

    def pending(self, limit: int = 100) -> list[Task]:
        return [Task.from_row(r) for r in self.db.query(
            "SELECT * FROM tasks WHERE status!='done' ORDER BY (deadline IS NULL), deadline, priority DESC LIMIT ?", (limit,))]

    def due_between(self, start: str, end: str) -> list[Task]:
        return [Task.from_row(r) for r in self.db.query(
            "SELECT * FROM tasks WHERE deadline IS NOT NULL AND deadline>=? AND deadline<? ORDER BY deadline", (start, end))]

    def counts(self) -> dict[str, int]:
        rows = self.db.query("SELECT status, COUNT(*) AS c FROM tasks GROUP BY status")
        out = {s: 0 for s in ("todo", "in_progress", "done")}
        for r in rows:
            out[r["status"]] = r["c"]
        out["total"] = sum(out.values())
        return out
