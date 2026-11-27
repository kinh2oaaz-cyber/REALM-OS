"""Left navigation sidebar with app launcher + favorites."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QLabel,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from core.app_registry import AppInfo
    from core.context import AppContext

from core.app_registry import HOME_ID
from ui.icons import app_icon, realm_logo


class _NavItem(QPushButton):
    def __init__(self, app: "AppInfo", favorite: bool, accent: str = "#C8A951", parent=None) -> None:
        super().__init__(parent)
        self.app_id = app.id
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setIcon(app_icon(app.id, color=accent, size=20))
        self.setIconSize(QSize(20, 20))
        self.setText(app.name)
        self.setToolTip(app.description)
        self.setMinimumHeight(42)


class Sidebar(QWidget):
    navigate = Signal(str)
    favorite_toggled = Signal(str, bool)

    def __init__(self, context: "AppContext", parent=None) -> None:
        super().__init__(parent)
        self.context = context
        self.setObjectName("Sidebar")
        self.setFixedWidth(248)
        self._items: dict[str, _NavItem] = {}
        self._current: str | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 12)
        outer.setSpacing(0)

        title = QLabel("REALM OS")
        title.setObjectName("SidebarTitle")
        from PySide6.QtCore import QSize as _QS
        title.setPixmap(realm_logo(28).pixmap(_QS(28, 28)))
        outer.addWidget(title)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self._list = QVBoxLayout(container)
        self._list.setContentsMargins(0, 4, 0, 4)
        self._list.setSpacing(1)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)

        self.rebuild()

    # -- construction ---------------------------------------------------
    def rebuild(self) -> None:
        while self._list.count():
            item = self._list.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._items.clear()

        registry = self.context.registry
        apps = registry.all()
        home = [a for a in apps if a.id == HOME_ID]
        rest = [a for a in apps if a.id != HOME_ID]

        # Home first, then apps, Settings pinned last.
        ordered = home + [a for a in rest if a.id != "settings"]
        settings_apps = [a for a in rest if a.id == "settings"]

        for app in ordered:
            self._add_app(app)

        if settings_apps:
            sep = QFrame()
            sep.setFrameShape(QFrame.Shape.HLine)
            sep.setStyleSheet("color: transparent;")
            self._list.addSpacing(8)
            self._list.addWidget(sep)
            for app in settings_apps:
                self._add_app(app)

        self._list.addStretch(1)
        if self._current:
            self.set_current(self._current)

    def _add_app(self, app: "AppInfo") -> None:
        item = _NavItem(app, self.context.registry.is_favorite(app.id), accent=self.context.theme.accent())
        item.clicked.connect(lambda _checked=False, aid=app.id: self.navigate.emit(aid))
        self._list.addWidget(item)
        self._items[app.id] = item

    # -- state ----------------------------------------------------------
    def set_current(self, app_id: str) -> None:
        self._current = app_id
        for aid, item in self._items.items():
            item.setChecked(aid == app_id)

    def current(self) -> str | None:
        return self._current

