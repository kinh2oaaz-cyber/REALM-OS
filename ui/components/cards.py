"""Reusable card containers."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QFrame, QGraphicsDropShadowEffect, QLabel, QVBoxLayout, QWidget


class Card(QFrame):
    """Rounded, subtly bordered surface."""

    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(18, 16, 18, 16)
        self._layout.setSpacing(10)
        self.title_label: QLabel | None = None
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("SectionTitle")
            self._layout.addWidget(self.title_label)

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)

    def add_layout(self, layout) -> None:  # noqa: ANN001
        self._layout.addLayout(layout)

    def body_layout(self) -> QVBoxLayout:
        return self._layout


class SectionCard(Card):
    """Card with a title row."""

    def __init__(self, title: str, parent: QWidget | None = None) -> None:
        super().__init__(title=title, parent=parent)
        self.setContentsMargins(0, 0, 0, 0)


def heading(text: str, object_name: str = "SectionTitle") -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setTextFormat(Qt.TextFormat.PlainText)
    return label


def muted(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Muted")
    label.setWordWrap(True)
    return label
