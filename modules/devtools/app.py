"""Developer Toolkit registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import DevToolsPage

APP_ID = "devtools"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Developer Toolkit", description="JSON, Base64, hashing, UUID, regex, diff",
        icon="tools", category="extra", order=210, keywords=("dev", "json", "base64", "hash", "uuid", "regex", "diff"),
        page_factory=lambda c: DevToolsPage(c),
    ))