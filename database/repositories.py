"""Small data-access helpers on top of :class:`Database`.

Feature modules are encouraged to implement their own repository
classes in ``modules/<name>/database.py``; this base removes
boilerplate. All SQL uses parameter binding.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .connection import Database


class Repository:
    table: str = ""

    def __init__(self, db: "Database") -> None:
        self.db = db
        if not self.table:
            raise ValueError("Repository subclasses must set `table`.")

    def all(self, order_by: str | None = None, limit: int | None = None) -> list[dict[str, Any]]:
        sql = f"SELECT * FROM {self.table}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        return self.db.query(sql)

    def get(self, row_id: int) -> dict[str, Any] | None:
        return self.db.query_one(f"SELECT * FROM {self.table} WHERE id = ?", (row_id,))

    def count(self) -> int:
        return int(self.db.scalar(f"SELECT COUNT(*) FROM {self.table}") or 0)

    def insert(self, **fields: Any) -> int:
        cols = ", ".join(fields)
        placeholders = ", ".join("?" for _ in fields)
        cur = self.db.execute(
            f"INSERT INTO {self.table} ({cols}) VALUES ({placeholders})",
            tuple(fields.values()),
        )
        return int(cur.lastrowid)

    def update(self, row_id: int, **fields: Any) -> None:
        if not fields:
            return
        assignments = ", ".join(f"{k} = ?" for k in fields)
        self.db.execute(
            f"UPDATE {self.table} SET {assignments} WHERE id = ?",
            (*fields.values(), row_id),
        )

    def delete(self, row_id: int) -> None:
        self.db.execute(f"DELETE FROM {self.table} WHERE id = ?", (row_id,))
