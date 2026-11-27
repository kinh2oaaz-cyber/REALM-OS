"""Project Manager registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import ProjectsPage

APP_ID = "projects"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Project Manager", description="Organize projects, link tasks & notes",
        icon="folders", category="extra", order=209, keywords=("project", "manager", "organize"),
        page_factory=lambda c: ProjectsPage(c),
    ))