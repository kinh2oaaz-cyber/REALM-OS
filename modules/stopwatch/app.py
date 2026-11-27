"""Stopwatch & Timer registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import StopwatchPage

APP_ID = "stopwatch"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Stopwatch & Timer", description="Stopwatch with laps and countdown timer",
        icon="stopwatch", category="extra", order=201, keywords=("stopwatch", "timer", "countdown", "lap"),
        page_factory=lambda c: StopwatchPage(c),
    ))