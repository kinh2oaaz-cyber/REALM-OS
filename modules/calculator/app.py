"""Calculator registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import CalculatorPage

APP_ID = "calculator"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Calculator", description="Calculator with safe expression evaluation",
        icon="calculator", category="extra", order=200, keywords=("calc", "math", "arithmetic"),
        page_factory=lambda c: CalculatorPage(c),
    ))