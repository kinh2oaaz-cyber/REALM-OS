"""Notes application service: CRUD, autosave support, recovery, export, protection."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from core.logging_setup import get_logger
from security.encryption import decrypt, encrypt

if TYPE_CHECKING:
    from core.context import AppContext

from .database import NotesRepository
from .models import Note, count_chars, count_words

_log = get_logger("notes")

# in-memory recovery drafts for autosave crash recovery
_RECOVERY: dict[int, str] = {}


class NotesService:
    def __init__(self, ctx: "AppContext") -> None:
        self.ctx = ctx
        self.repo = NotesRepository(ctx.db)

    # CRUD --------------------------------------------------------------
    def create_note(self, title: str = "Untitled", folder: str = "", category: str = "",
                    fmt: str = "markdown", content: str = "") -> int:
        note = Note(title=title or "Untitled", content=content, format=fmt, folder=folder, category=category,
                    word_count=count_words(content), char_count=count_chars(content))
        note_id = self.repo.create(note)
        self.ctx.event_bus.publish("note.created", {"note_id": note_id})
        return note_id

    def save_note(self, note_id: int, *, title: str | None = None, content: str | None = None,
                  plain_for_counts: str | None = None, fmt: str | None = None,
                  folder: str | None = None, category: str | None = None,
                  pinned: bool | None = None) -> None:
        note = self.repo.get(note_id)
        if note is None:
            return
        if title is not None:
            note.title = title
        if content is not None:
            note.content = content
        if fmt is not None:
            note.format = fmt
        if folder is not None:
            note.folder = folder
        if category is not None:
            note.category = category
        if pinned is not None:
            note.pinned = pinned
        counts_source = plain_for_counts if plain_for_counts is not None else note.content
        note.word_count = count_words(counts_source)
        note.char_count = count_chars(counts_source)
        self.repo.update(note)
        _RECOVERY.pop(note_id, None)
        self.ctx.event_bus.publish("note.updated", {"note_id": note_id})

    def delete_note(self, note_id: int) -> None:
        self.repo.delete(note_id)
        _RECOVERY.pop(note_id, None)
        self.ctx.event_bus.publish("note.deleted", {"note_id": note_id})

    def get_note(self, note_id: int) -> Note | None:
        note = self.repo.get(note_id)
        if note is not None:
            self.repo.touch_accessed(note_id)
        return note

    def list_notes(self, folder: str | None = None) -> list[Note]:
        return self.repo.list_notes(folder)

    def search(self, query: str) -> list[Note]:
        return self.repo.search(query)

    # pin / folders -----------------------------------------------------
    def set_pinned(self, note_id: int, pinned: bool) -> None:
        note = self.repo.get(note_id)
        if note:
            note.pinned = pinned
            self.repo.update(note)

    def folders(self) -> list[str]:
        return self.repo.list_folders()

    def add_folder(self, name: str) -> None:
        if name.strip():
            self.repo.add_folder(name.strip())

    def categories(self) -> list[str]:
        return self.repo.list_categories()

    # recovery ----------------------------------------------------------
    def stash_draft(self, note_id: int, content: str) -> None:
        """Remember an unsaved draft for autosave recovery."""
        _RECOVERY[note_id] = content

    def recover_draft(self, note_id: int) -> str | None:
        return _RECOVERY.get(note_id)

    # export ------------------------------------------------------------
    def export_txt(self, note_id: int, destination: str) -> Path:
        note = self.repo.get(note_id)
        if note is None:
            raise ValueError("Note not found")
        text = self._plain_content(note)
        path = Path(destination)
        path.write_text(text, encoding="utf-8")
        return path

    def export_markdown(self, note_id: int, destination: str) -> Path:
        note = self.repo.get(note_id)
        if note is None:
            raise ValueError("Note not found")
        if note.protected:
            raise ValueError("Cannot export a protected note without unlocking it first")
        path = Path(destination)
        md = f"# {note.title}\n\n{note.content}\n"
        path.write_text(md, encoding="utf-8")
        return path

    def _plain_content(self, note: Note) -> str:
        if note.protected:
            raise ValueError("Cannot export a protected note without unlocking it first")
        return note.content

    # attachments -------------------------------------------------------
    def add_attachment(self, note_id: int, path: str) -> None:
        self.repo.add_attachment(note_id, path, Path(path).name)
        # shared system: link note -> file
        self.ctx.db.execute(
            "INSERT INTO item_links (from_app, from_id, to_app, to_id, relation) VALUES ('notes', ?, 'file_manager', ?, 'attachment')",
            (str(note_id), path),
        )

    def attachments(self, note_id: int) -> list[dict]:
        return self.repo.list_attachments(note_id)

    def remove_attachment(self, attachment_id: int) -> None:
        self.repo.remove_attachment(attachment_id)

    # optional password protection -------------------------------------
    def protect_note(self, note_id: int, password: str) -> None:
        """Encrypt note content at rest with `password` (Fernet)."""
        note = self.repo.get(note_id)
        if note is None:
            return
        if note.protected:
            # already protected; need current session password to re-key
            current = _last_password.get(note_id)
            if current is None:
                return
            try:
                plain = decrypt(note.content, current)
            except ValueError:
                return
        else:
            plain = note.content
        note.content = encrypt(plain, password)
        note.protected = True
        self.repo.update(note)
        _last_password[note_id] = password
        self.ctx.event_bus.publish("note.updated", {"note_id": note_id})

    def unlock_note(self, note_id: int, password: str) -> str | None:
        """Return decrypted content if `password` is correct, else None."""
        note = self.repo.get(note_id)
        if note is None:
            return None
        if not note.protected:
            return note.content
        try:
            plain = decrypt(note.content, password)
            _last_password[note_id] = password
            return plain
        except ValueError:
            return None

    def remove_protection(self, note_id: int, password: str) -> bool:
        note = self.repo.get(note_id)
        if note is None or not note.protected:
            return False
        try:
            plain = decrypt(note.content, password)
        except ValueError:
            return False
        note.content = plain
        note.protected = False
        note.word_count = count_words(plain)
        note.char_count = count_chars(plain)
        self.repo.update(note)
        _last_password.pop(note_id, None)
        return True

    def save_protected_content(self, note_id: int, plain: str, password: str, title: str | None = None) -> None:
        """Save edits to a protected note, re-encrypting content."""
        note = self.repo.get(note_id)
        if note is None:
            return
        note.content = encrypt(plain, password)
        note.protected = True
        if title is not None:
            note.title = title
        note.word_count = count_words(plain)
        note.char_count = count_chars(plain)
        self.repo.update(note)


# in-memory last-unlocked passwords for session editing (never persisted)
_last_password: dict[int, str] = {}


