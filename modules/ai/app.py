"""REALM AI (AI Assistant) registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import AIPage

APP_ID = "ai"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="REALM AI", description="Local AI assistant (requires a local model)",
        icon="sparkles", category="extra", order=211, keywords=("ai", "assistant", "chat", "realm ai"),
        page_factory=lambda c: AIPage(c),
    ))