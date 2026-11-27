"""File Manager registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import FileManagerPage

APP_ID = "file_manager"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="File Manager",
            description="Browse, search, preview and manage local files",
            icon="folder",
            category="apps",
            order=40,
            keywords=("file", "files", "folder", "directory", "explorer", "drive"),
            page_factory=lambda c: FileManagerPage(c),
        )
    )
