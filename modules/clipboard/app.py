"""Clipboard Manager registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import ClipboardPage

APP_ID = "clipboard"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Clipboard Manager", description="Clipboard history with one-click copy",
        icon="clipboard", category="extra", order=202, keywords=("clipboard", "copy", "paste", "history"),
        page_factory=lambda c: ClipboardPage(c),
    ))