"""Gaming Hub registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import GamingPage

APP_ID = "gaming"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Gaming",
            description="Personal game library, launch and playtime",
            icon="device-gamepad-2",
            category="apps",
            order=50,
            keywords=("gaming", "games", "game", "library", "playtime", "launch"),
            page_factory=lambda c: GamingPage(c),
        )
    )
