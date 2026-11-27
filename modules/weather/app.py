"""Weather registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import WeatherPage

APP_ID = "weather"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Weather", description="Optional weather (internet required)",
        icon="cloud", category="extra", order=205, keywords=("weather", "forecast", "temperature"),
        page_factory=lambda c: WeatherPage(c),
    ))