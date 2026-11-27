"""Notifications panel (popup) listing recent in-app notifications."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from core.context import AppContext

_LEVEL_DOT = {
    "info": "#0071E3",
    "success": "#34C759",
    "warning": "#FF9500",
    "error": "#FF3B30",
}


class NotificationsPanel(QDialog):
    def __init__(self, context: "AppContext", parent=None) -> None:
        super().__init__(parent)
        self.context = context
        self.setWindowTitle("Notifications")
        self.setModal(False)
        self.resize(380, 460)
        self.setObjectName("NotificationsPanel")

        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        header = QHBoxLayout()
        title = QLabel("Notifications")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        mark_all = QPushButton("Mark all read")
        mark_all.setObjectName("GhostButton")
        mark_all.clicked.connect(self._mark_all_read)
        header.addWidget(mark_all)
        clear = QPushButton("Clear")
        clear.setObjectName("GhostButton")
        clear.clicked.connect(self._clear)
        header.addWidget(clear)
        root.addLayout(header)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        self._body = QWidget()
        self._list = QVBoxLayout(self._body)
        self._list.setContentsMargins(0, 0, 0, 0)
        self._list.setSpacing(8)
        scroll.setWidget(self._body)
        root.addWidget(scroll, 1)

        context.event_bus.subscribe("notification.added", lambda _p: self.refresh())
        context.event_bus.subscribe("notification.read", lambda _p: self.refresh())

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self.refresh()

    def refresh(self) -> None:
        while self._list.count():
            item = self._list.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        notes = self.context.notifications.list(limit=50)
        if not notes:
            empty = QLabel("No notifications yet.")
            empty.setObjectName("Muted")
            empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._list.addWidget(empty)
            self._list.addStretch(1)
            return

        for note in notes:
            self._list.addWidget(self._make_row(note))
        self._list.addStretch(1)

    def _make_row(self, note) -> QWidget:  # noqa: ANN001
        row = QFrame()
        row.setObjectName("Card")
        lay = QVBoxLayout(row)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(4)

        top = QHBoxLayout()
        dot = QLabel("")
        dot.setStyleSheet(f"color: {_LEVEL_DOT.get(note.level, '#0071E3')}; font-size: 10px;")
        title = QLabel(note.title)
        title.setStyleSheet("font-weight: 600;" + ("" if note.read else ""))
        top.addWidget(dot)
        top.addWidget(title, 1)
        if not note.read:
            top.addWidget(QLabel("•"))
        lay.addLayout(top)

        if note.message:
            msg = QLabel(note.message)
            msg.setObjectName("Muted")
            msg.setWordWrap(True)
            lay.addWidget(msg)

        meta = QLabel(note.created_at)
        meta.setObjectName("Tiny")
        lay.addWidget(meta)

        if not note.read:
            row.mousePressEvent = lambda _e, nid=note.id: self._mark_read(nid)  # type: ignore[assignment]
            row.setCursor(Qt.CursorShape.PointingHandCursor)
        return row

    def _mark_read(self, note_id: int) -> None:
        self.context.notifications.mark_read(note_id)

    def _mark_all_read(self) -> None:
        self.context.notifications.mark_all_read()

    def _clear(self) -> None:
        self.context.notifications.clear()
        self.refresh()
