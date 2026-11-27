"""Settings registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import SettingsPage

APP_ID = "settings"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Settings",
            description="Themes, accent, fonts, data and preferences",
            icon="settings",
            category="system",
            order=1000,
            keywords=("settings", "preferences", "theme", "dark", "accent", "font", "data"),
            page_factory=lambda c: SettingsPage(c),
        )
    )
