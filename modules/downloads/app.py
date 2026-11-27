"""Download Manager registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import DownloadsPage

APP_ID = "downloads"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Download Manager", description="Download files with progress",
        icon="download", category="extra", order=208, keywords=("download", "http", "file"),
        page_factory=lambda c: DownloadsPage(c),
    ))