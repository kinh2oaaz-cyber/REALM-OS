"""Register every built-in module with the central registry."""

from __future__ import annotations

from typing import TYPE_CHECKING

from core.app_registry import HOME_ID, AppInfo, AppRegistry

if TYPE_CHECKING:
    from core.context import AppContext

from ui.pages.home_page import HomePage


def register_all_modules(registry: AppRegistry, ctx: "AppContext") -> None:
    """Register Home + all built-in applications."""
    registry.register(
        AppInfo(
            id=HOME_ID,
            name="Home",
            description="Launcher and personal dashboard",
            icon="home",
            category="system",
            order=0,
            keywords=("home", "dashboard", "launcher", "start"),
            page_factory=lambda c: HomePage(c),
        )
    )

    from .calendar.app import register as register_calendar
    from .file_manager.app import register as register_file_manager
    from .gaming.app import register as register_gaming
    from .media.app import register as register_media
    from .network.app import register as register_network
    from .notes.app import register as register_notes
    from .settings.app import register as register_settings
    from .task_manager.app import register as register_task_manager

    register_calendar(registry, ctx)
    register_notes(registry, ctx)
    register_task_manager(registry, ctx)
    register_file_manager(registry, ctx)
    register_gaming(registry, ctx)
    register_media(registry, ctx)
    register_network(registry, ctx)
    register_settings(registry, ctx)

    # ---- Phase 9 additional applications ----
    from .ai.app import register as register_ai
    from .calculator.app import register as register_calculator
    from .clipboard.app import register as register_clipboard
    from .devtools.app import register as register_devtools
    from .downloads.app import register as register_downloads
    from .finance.app import register as register_finance
    from .pdf.app import register as register_pdf
    from .projects.app import register as register_projects
    from .screenshot.app import register as register_screenshot
    from .stopwatch.app import register as register_stopwatch
    from .vault.app import register as register_vault
    from .weather.app import register as register_weather

    register_calculator(registry, ctx)
    register_stopwatch(registry, ctx)
    register_clipboard(registry, ctx)
    register_vault(registry, ctx)
    register_finance(registry, ctx)
    register_weather(registry, ctx)
    register_screenshot(registry, ctx)
    register_pdf(registry, ctx)
    register_downloads(registry, ctx)
    register_projects(registry, ctx)
    register_devtools(registry, ctx)
    register_ai(registry, ctx)
