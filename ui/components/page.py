"""Base class for every top-level application page."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtWidgets import QVBoxLayout, QWidget

if TYPE_CHECKING:
    from core.context import AppContext


class RealmPage(QWidget):
    """A page hosted in the main workspace.

    Subclasses override :meth:`on_show` / :meth:`on_hide` for lazy
    refresh, and :attr:`page_title`.
    """

    page_title = "REALM OS"

    def __init__(self, context: "AppContext", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.context = context
        self.setObjectName("RealmPage")
        # Dynamic property lets the global QSS make pages transparent so the
        # atmospheric backdrop shows through (see ui/themes/base.qss).
        self.setProperty("realmPage", True)
        self._root = QVBoxLayout(self)
        self._root.setContentsMargins(32, 26, 32, 26)
        self._root.setSpacing(18)
        self.build_ui()

    # -- API ------------------------------------------------------------
    def build_ui(self) -> None:  # pragma: no cover - overridden
        """Populate the page. Called once after layout is created."""

    def on_show(self) -> None:
        """Called each time the page becomes visible."""

    def on_hide(self) -> None:
        """Called when the page is hidden."""

    @property
    def layout_root(self) -> QVBoxLayout:
        return self._root
