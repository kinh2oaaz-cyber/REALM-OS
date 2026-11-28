"""Main application window: sidebar + top bar + workspace + navigation."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QHBoxLayout,
    QMainWindow,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from core.app_registry import HOME_ID
from core.logging_setup import get_logger

from .components.sidebar import Sidebar
from .components.top_bar import TopBar
from .pages.home_page import HomePage
from .components.page import RealmPage
from .motion import page_transition

if TYPE_CHECKING:
    from core.app_registry import AppInfo
    from core.context import AppContext

_log = get_logger("main_window")


class MainWindow(QMainWindow):
    def __init__(self, context: "AppContext", parent=None) -> None:
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("REALM OS")
        self.setMinimumSize(960, 640)
        self.resize(1280, 820)

        central = QWidget()
        central.setObjectName("RootBackground")
        central.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self.sidebar = Sidebar(context, self)
        self.sidebar.navigate.connect(self.navigate)
        root.addWidget(self.sidebar)

        # Right column: top bar + workspace
        right = QWidget()
        right.setObjectName("WorkspaceColumn")
        right_layout = QVBoxLayout(right)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self.top_bar = TopBar(context, self)
        self.top_bar.search_requested.connect(self._on_global_search)
        self.top_bar.open_preferences.connect(lambda: self.navigate("settings"))
        right_layout.addWidget(self.top_bar)

        self.workspace = QStackedWidget()
        right_layout.addWidget(self.workspace, 1)
        root.addWidget(right, 1)

        self._pages: dict[str, QWidget] = {}

        # keyboard shortcuts
        QShortcut(QKeySequence("Ctrl+F"), self, activated=lambda: self.top_bar.search.setFocus())
        QShortcut(QKeySequence("Ctrl+D"), self, activated=context.theme.toggle_dark)
        QShortcut(QKeySequence("Ctrl+,"), self, activated=lambda: self.navigate("settings"))
        QShortcut(QKeySequence("Ctrl+1"), self, activated=lambda: self.navigate("home"))
        QShortcut(QKeySequence("F5"), self, activated=self._refresh_current)

        # navigation via event bus (modules can request navigation)
        context.event_bus.subscribe("navigation.requested", self._on_navigation_requested)
        context.event_bus.subscribe("app.favorite_changed", lambda _p: self.sidebar.rebuild())
        context.theme.theme_changed.connect(lambda _t: None)

        # home is always first
        self._home = HomePage(context, self)
        self.workspace.addWidget(self._home)
        self._pages[HOME_ID] = self._home

        # restore last app if requested
        start = context.settings.get_str("app.last_app", HOME_ID)
        if not context.settings.get_bool("startup.open_last", False):
            start = HOME_ID
        self.navigate(start if start in context.registry else HOME_ID)

    # -- navigation -----------------------------------------------------
    def navigate(self, app_id: str) -> None:
        try:
            page = self._get_or_create_page(app_id)
        except Exception:  # noqa: BLE001 - never let a bad module break the shell
            _log.exception("Failed to open app %r", app_id)
            return
        if page is None:
            return

        current = self.workspace.currentWidget()
        if isinstance(current, RealmPage):
            try:
                current.on_hide()
            except Exception:  # noqa: BLE001
                _log.exception("on_hide failed for %s", type(current).__name__)

        self.workspace.setCurrentWidget(page)
        self.sidebar.set_current(app_id)
        self.context.settings.set("app.last_app", app_id)

        if app_id != HOME_ID:
            self.context.registry.record_open(app_id)
            self.context.event_bus.publish("app.opened", {"app_id": app_id})
        self.sidebar.rebuild()

        # smooth page transition (Qt animation engine; Framer Motion is React-only)
        page_transition(page, self.context.settings)

        if isinstance(page, RealmPage):
            try:
                page.on_show()
            except Exception:  # noqa: BLE001
                _log.exception("on_show failed for %s", type(page).__name__)

    def _get_or_create_page(self, app_id: str) -> QWidget | None:
        if app_id in self._pages:
            return self._pages[app_id]
        if app_id == HOME_ID:
            return self._pages[HOME_ID]
        app: AppInfo | None = self.context.registry.get(app_id)
        if app is None:
            _log.warning("Unknown app id %r", app_id)
            return None
        if app.page_factory is None:
            _log.warning("App %r has no page factory", app_id)
            return None
        page = app.page_factory(self.context)
        page.setObjectName(f"Page_{app_id}")
        self.workspace.addWidget(page)
        self._pages[app_id] = page
        return page

    def _on_navigation_requested(self, payload: object) -> None:
        app_id = None
        if isinstance(payload, dict):
            app_id = payload.get("app_id")
        if app_id:
            self.navigate(str(app_id))

    def _on_global_search(self, query: str) -> None:
        query = query.strip()
        if not query:
            return
        self.context.event_bus.publish("global.search", {"query": query})
        results = self.context.registry.search(query)
        if results:
            self.navigate(results[0].id)

    def _refresh_current(self) -> None:
        page = self.workspace.currentWidget()
        if isinstance(page, RealmPage):
            page.on_show()

    # -- qt -------------------------------------------------------------
    def closeEvent(self, event) -> None:  # noqa: N802
        try:
            self.context.db.close()
        except Exception:  # noqa: BLE001
            pass
        super().closeEvent(event)
