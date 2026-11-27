"""Network Monitor registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import NetworkPage

APP_ID = "network"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Network",
            description="Connection status, speeds, adapters, diagnostics",
            icon="wifi",
            category="apps",
            order=70,
            keywords=("network", "internet", "wifi", "speed", "ping", "ip", "latency"),
            page_factory=lambda c: NetworkPage(c),
        )
    )
