"""Personal Finance Tracker registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import FinancePage

APP_ID = "finance"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Finance", description="Personal finance tracker",
        icon="coins", category="extra", order=204, keywords=("finance", "money", "budget", "expense", "income"),
        page_factory=lambda c: FinancePage(c),
    ))