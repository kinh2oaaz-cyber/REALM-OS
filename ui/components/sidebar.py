"""Left navigation rail — grouped, refined, REALM identity header."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt, Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
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

# icons are recolored per state (QSS cannot recolor QPushButton icons)
_ICON_IDLE = "#9C929C"
_ICON_ACTIVE = "#D6AD55"


class _NavItem(QPushButton):
    def __init__(self, app: "AppInfo", parent=None) -> None:
        super().__init__(parent)
        self.app_id = app.id
        self.setObjectName("NavButton")
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setIconSize(QSize(18, 18))
        # "&&" renders a literal ampersand instead of a mnemonic accelerator.
        self.setText(app.name.replace("&", "&&"))
        self.setToolTip(app.description)
        self.setMinimumHeight(40)
        self._refresh_icon(False)
        self.toggled.connect(self._refresh_icon)

    def _refresh_icon(self, checked: bool) -> None:
        self.setIcon(app_icon(self.app_id, color=_ICON_ACTIVE if checked else _ICON_IDLE, size=18))


class Sidebar(QWidget):
    navigate = Signal(str)
    favorite_toggled = Signal(str, bool)

    _GROUPS = (
        ("WORKSPACE", "apps"),
        ("TOOLKIT", "extra"),
        ("SYSTEM", "system"),
    )

    def __init__(self, context: "AppContext", parent=None) -> None:
        super().__init__(parent)
        self.context = context
        self.setObjectName("Sidebar")
        # Plain QWidget subclasses only honour QSS backgrounds with this flag.
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setFixedWidth(252)
        self._items: dict[str, _NavItem] = {}
        self._current: str | None = None

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 14)
        outer.setSpacing(0)

        outer.addWidget(self._identity())

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        container = QWidget()
        self._list = QVBoxLayout(container)
        self._list.setContentsMargins(0, 6, 0, 6)
        self._list.setSpacing(1)
        scroll.setWidget(container)
        outer.addWidget(scroll, 1)

        self.rebuild()

    # -- identity header -------------------------------------------------
    def _identity(self) -> QWidget:
        wrap = QWidget()
        wrap.setObjectName("SidebarIdentity")
        lay = QHBoxLayout(wrap)
        lay.setContentsMargins(18, 18, 16, 14)
        lay.setSpacing(12)

        mark = QLabel()
        mark.setFixedSize(34, 34)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setPixmap(realm_logo(30).pixmap(30, 30))
        mark.setStyleSheet("background: transparent; border: none;")
        lay.addWidget(mark)

        text = QVBoxLayout()
        text.setSpacing(0)
        title = QLabel("REALM OS")
        title.setObjectName("SidebarTitle")
        tagline = QLabel("PERSONAL DESKTOP")
        tagline.setObjectName("SidebarTagline")
        text.addWidget(title)
        text.addWidget(tagline)
        lay.addLayout(text, 1)
        return wrap

    # -- construction ---------------------------------------------------
    def _section(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setObjectName("SidebarSection")
        return label

    def _separator(self) -> QFrame:
        line = QFrame()
        line.setObjectName("SidebarSeparator")
        line.setFixedHeight(1)
        return line

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
        by_cat: dict[str, list["AppInfo"]] = {}
        for app in apps:
            if app.id == HOME_ID:
                continue
            by_cat.setdefault(app.category, []).append(app)

        # Home stands alone at the top.
        for app in home:
            self._add_app(app)

        for label, cat in self._GROUPS:
            group = by_cat.get(cat, [])
            if not group:
                continue
            self._list.addWidget(self._section(label))
            for app in group:
                self._add_app(app)

        self._list.addStretch(1)
        if self._current:
            self.set_current(self._current)

    def _add_app(self, app: "AppInfo") -> None:
        item = _NavItem(app)
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
