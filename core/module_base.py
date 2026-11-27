"""Base class and metadata for REALM OS feature modules."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .app_registry import AppInfo

if TYPE_CHECKING:
    from .app_registry import AppRegistry
    from .context import AppContext


class RealmModule:
    """A self-contained application inside REALM OS.

    Subclasses implement :meth:`register`. Each module owns its
    services, models and database access in its own package.
    """

    info: AppInfo

    def register(self, registry: "AppRegistry", ctx: "AppContext") -> None:
        registry.register(self.info)

    @staticmethod
    def _noop_page(ctx: "AppContext"):  # pragma: no cover - replaced per module
        from ui.components.empty_state import EmptyState

        return EmptyState("Not available", "This module is not loaded.")
