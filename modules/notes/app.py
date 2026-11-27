"""Notes registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import NotesPage

APP_ID = "notes"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Notes",
            description="Rich-text & Markdown notes, folders, autosave, search, export",
            icon="note",
            category="apps",
            order=20,
            keywords=("notes", "note", "markdown", "text", "writing", "editor"),
            page_factory=lambda c: NotesPage(c),
        )
    )
