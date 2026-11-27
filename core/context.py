"""Shared application context passed to every module and page."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtWidgets import QApplication

    from database import Database

    from .app_registry import AppRegistry
    from .event_bus import EventBus
    from .notifications import NotificationService
    from .settings import Settings
    from ui.themes import ThemeManager


@dataclass
class AppContext:
    """Bundle of shared services."""

    app: "QApplication"
    db: "Database"
    settings: "Settings"
    event_bus: "EventBus"
    notifications: "NotificationService"
    theme: "ThemeManager"
    registry: "AppRegistry"

    def navigate(self, app_id: str) -> None:
        """Request navigation to an app via the event bus."""
        self.event_bus.publish("navigation.requested", {"app_id": app_id})
