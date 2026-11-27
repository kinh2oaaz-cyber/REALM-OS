"""Notes database access layer."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from database import Database

from .models import Note


class NotesRepository:
    def __init__(self, db: "Database") -> None:
        self.db = db

    def list_folders(self) -> list[str]:
        rows = self.db.query("SELECT name FROM note_folders ORDER BY name")
        folders = [r["name"] for r in rows]
        # include folders used on notes even if not separately registered
        for r in self.db.query("SELECT DISTINCT folder FROM notes WHERE folder != '' ORDER BY folder"):
            if r["folder"] not in folders:
                folders.append(r["folder"])
        return sorted(set(folders))

    def add_folder(self, name: str) -> None:
        self.db.execute("INSERT OR IGNORE INTO note_folders (name) VALUES (?)", (name,))

    def remove_folder(self, name: str) -> None:
        self.db.execute("DELETE FROM note_folders WHERE name = ?", (name,))
        self.db.execute("UPDATE notes SET folder='' WHERE folder=?", (name,))

    def list_categories(self) -> list[str]:
        return [r["category"] for r in self.db.query("SELECT DISTINCT category FROM notes WHERE category != '' ORDER BY category")]

    def list_notes(self, folder: str | None = None, order_by: str = "pinned DESC, updated_at DESC") -> list[Note]:
        sql = "SELECT * FROM notes"
        params: tuple[Any, ...] = ()
        if folder is not None:
            sql += " WHERE folder = ?"
            params = (folder,)
        sql += f" ORDER BY {order_by}"
        return [Note.from_row(r) for r in self.db.query(sql, params)]

    def search(self, query: str) -> list[Note]:
        like = f"%{query.strip()}%"
        rows = self.db.query(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR folder LIKE ? OR category LIKE ? "
            "ORDER BY pinned DESC, updated_at DESC",
            (like, like, like, like),
        )
        return [Note.from_row(r) for r in rows]

    def get(self, note_id: int) -> Note | None:
        row = self.db.query_one("SELECT * FROM notes WHERE id = ?", (note_id,))
        return Note.from_row(row) if row else None

    def create(self, note: Note) -> int:
        cur = self.db.execute(
            """
            INSERT INTO notes (title, content, format, folder, category, pinned, protected, word_count, char_count, updated_at, last_accessed_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
            """,
            (note.title, note.content, note.format, note.folder, note.category,
             1 if note.pinned else 0, 1 if note.protected else 0, note.word_count, note.char_count),
        )
        return int(cur.lastrowid)

    def update(self, note: Note) -> None:
        self.db.execute(
            """
            UPDATE notes SET title=?, content=?, format=?, folder=?, category=?, pinned=?, protected=?,
                word_count=?, char_count=?, updated_at=datetime('now') WHERE id=?
            """,
            (note.title, note.content, note.format, note.folder, note.category,
             1 if note.pinned else 0, 1 if note.protected else 0, note.word_count, note.char_count, note.id),
        )

    def touch_accessed(self, note_id: int) -> None:
        self.db.execute("UPDATE notes SET last_accessed_at=datetime('now') WHERE id=?", (note_id,))

    def delete(self, note_id: int) -> None:
        self.db.execute("DELETE FROM notes WHERE id = ?", (note_id,))

    def recently_accessed(self, limit: int = 10) -> list[Note]:
        return [Note.from_row(r) for r in self.db.query("SELECT * FROM notes ORDER BY last_accessed_at DESC LIMIT ?", (limit,))]

    # attachments (notes can contain file attachments) ------------------
    def add_attachment(self, note_id: int, path: str, name: str) -> None:
        self.db.execute("INSERT INTO note_attachments (note_id, path, name) VALUES (?, ?, ?)", (note_id, path, name))

    def list_attachments(self, note_id: int) -> list[dict[str, Any]]:
        return self.db.query("SELECT * FROM note_attachments WHERE note_id=? ORDER BY added_at", (note_id,))

    def remove_attachment(self, attachment_id: int) -> None:
        self.db.execute("DELETE FROM note_attachments WHERE id=?", (attachment_id,))
