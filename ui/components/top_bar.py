"""Top bar: global search, clock, notifications, quick actions, preferences."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QWidget,
)

from .notifications_panel import NotificationsPanel
from .quick_actions import build_quick_actions_menu
from .search_box import SearchBox

if TYPE_CHECKING:
    from core.context import AppContext


class TopBar(QWidget):
    search_requested = Signal(str)
    open_preferences = Signal()

    def __init__(self, context: "AppContext", parent=None) -> None:
        super().__init__(parent)
        self.context = context
        self.setObjectName("TopBar")
        self.setFixedHeight(60)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        self.search = SearchBox("Search apps, notes, tasks, events…")
        self.search.search_requested.connect(self.search_requested.emit)
        layout.addWidget(self.search, 1)

        self.clock = QLabel()
        self.clock.setObjectName("ClockLabel")
        self.clock.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(self.clock)

        # Quick actions
        self.quick_button = QPushButton()
        from ui.icons import icon as _ic
        self.quick_button.setIcon(_ic("bolt", size=18))
        self.quick_button.setObjectName("IconButton")
        self.quick_button.setToolTip("Quick actions")
        self.quick_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self._quick_menu = build_quick_actions_menu(context, self)
        self.quick_button.clicked.connect(self._show_quick_actions)
        layout.addWidget(self.quick_button)

        # Notifications
        self.notify_button = QPushButton()
        self.notify_button.setIcon(_ic("bell", size=18))
        self.notify_button.setObjectName("IconButton")
        self.notify_button.setToolTip("Notifications")
        self.notify_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notify_button.clicked.connect(self._toggle_notifications)
        self._notify_badge = QLabel(self.notify_button)
        self._notify_badge.setStyleSheet(
            "background:#FF3B30;color:white;border-radius:8px;font-size:9px;padding:1px 5px;"
        )
        self._notify_badge.hide()
        layout.addWidget(self.notify_button)

        # Theme toggle (also a quick action; convenient in top bar)
        self.theme_button = QPushButton()
        self.theme_button.setIcon(_ic("moon", size=18))
        self.theme_button.setObjectName("IconButton")
        self.theme_button.setToolTip("Toggle dark / light")
        self.theme_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.theme_button.clicked.connect(self._toggle_theme)
        layout.addWidget(self.theme_button)

        # Preferences / settings
        self.prefs_button = QPushButton()
        self.prefs_button.setIcon(_ic("settings", size=18))
        self.prefs_button.setObjectName("IconButton")
        self.prefs_button.setToolTip("Settings & preferences")
        self.prefs_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.prefs_button.clicked.connect(self.open_preferences.emit)
        layout.addWidget(self.prefs_button)

        self._notifications = NotificationsPanel(context, self)

        # clock
        self._timer = QTimer(self)
        self._timer.setInterval(1000)
        self._timer.timeout.connect(self._update_clock)
        self._timer.start()
        self._update_clock()
        self._update_badge()

        context.event_bus.subscribe("notification.added", lambda _p: self._update_badge())
        context.event_bus.subscribe("notification.read", lambda _p: self._update_badge())
        context.theme.theme_changed.connect(lambda _t: self._update_theme_icon())

    # -- actions --------------------------------------------------------
    def _show_quick_actions(self) -> None:
        pos = self.quick_button.mapToGlobal(self.quick_button.rect().bottomLeft())
        self._quick_menu.exec(pos)

    def _toggle_notifications(self) -> None:
        if self._notifications.isVisible():
            self._notifications.hide()
        else:
            self._notifications.refresh()
            pos = self.notify_button.mapToGlobal(self.notify_button.rect().bottomRight())
            self._notifications.move(pos.x() - self._notifications.width(), pos.y() + 6)
            self._notifications.show()

    def _toggle_theme(self) -> None:
        self.context.theme.toggle_dark()

    # -- updates --------------------------------------------------------
    def _update_clock(self) -> None:
        now = datetime.now()
        self.clock.setText(now.strftime("%a %d %b   %H:%M:%S"))

    def _update_badge(self) -> None:
        try:
            count = self.context.notifications.unread_count()
        except Exception:  # noqa: BLE001
            count = 0
        if count > 0:
            self._notify_badge.setText(str(count if count < 100 else "99+"))
            self._notify_badge.adjustSize()
            self._notify_badge.move(self.notify_button.width() - 14, 2)
            self._notify_badge.show()
        else:
            self._notify_badge.hide()

    def _update_theme_icon(self) -> None:
        dark = self.context.theme.effective_theme() == "dark"
        from ui.icons import icon as _ic2
        self.theme_button.setIcon(_ic2("sun" if dark else "moon", size=18))
