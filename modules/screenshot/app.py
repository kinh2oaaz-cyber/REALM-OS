"""Screenshot Tool registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import ScreenshotPage

APP_ID = "screenshot"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Screenshot Tool", description="Capture screenshots",
        icon="camera", category="extra", order=206, keywords=("screenshot", "capture", "screen", "snap"),
        page_factory=lambda c: ScreenshotPage(c),
    ))