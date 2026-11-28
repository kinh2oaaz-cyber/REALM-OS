"""Reusable REALM Cinematic surfaces and text primitives.

All components are styled through the global QSS (object names), so they
inherit the shared design language across every application.
"""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtGui import QColor


def _soft_shadow(widget: QWidget, blur: int = 28, dy: int = 8, alpha: int = 150) -> None:
    """Attach a soft, low-opacity drop shadow (elevation without heaviness)."""
    effect = QGraphicsDropShadowEffect(widget)
    effect.setBlurRadius(blur)
    effect.setOffset(0, dy)
    effect.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(effect)


class Card(QFrame):
    """Rounded graphite surface with a hairline border."""

    def __init__(self, title: str | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 18, 20, 18)
        self._layout.setSpacing(12)
        self.title_label: QLabel | None = None
        if title:
            self.title_label = QLabel(title)
            self.title_label.setObjectName("SectionTitle")
            self.title_label.setWordWrap(True)
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


class HeroCard(QFrame):
    """Large, visually dominant featured panel with a soft shadow."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HeroCard")
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(30, 28, 30, 28)
        self._layout.setSpacing(10)
        _soft_shadow(self, blur=48, dy=16, alpha=170)

    def body_layout(self) -> QVBoxLayout:
        return self._layout

    def add_widget(self, widget: QWidget) -> None:
        self._layout.addWidget(widget)

    def add_layout(self, layout) -> None:  # noqa: ANN001
        self._layout.addLayout(layout)


class StatTile(QFrame):
    """Compact metric tile: big value + small uppercase label."""

    def __init__(self, value: str = "—", label: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("StatTile")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(16, 14, 16, 14)
        lay.setSpacing(2)
        self.value = QLabel(value)
        self.value.setObjectName("StatValue")
        self.label = QLabel(label.upper())
        self.label.setObjectName("StatLabel")
        lay.addWidget(self.value)
        lay.addWidget(self.label)

    def set_value(self, value: str) -> None:
        self.value.setText(value)

    def set_label(self, label: str) -> None:
        self.label.setText(label.upper())


class AppTile(QFrame):
    """Launcher tile: icon + name + description, clickable via callback."""

    def __init__(self, icon, name: str, description: str, on_click, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("Card")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._on_click = on_click
        lay = QHBoxLayout(self)
        lay.setContentsMargins(14, 12, 14, 12)
        lay.setSpacing(12)

        badge = QLabel()
        badge.setFixedSize(38, 38)
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        badge.setPixmap(icon.pixmap(22, 22))
        badge.setStyleSheet(
            "background: rgba(197,31,53,0.14); border: 1px solid rgba(214,173,85,0.22);"
            "border-radius: 10px;"
        )
        lay.addWidget(badge)

        text = QVBoxLayout()
        text.setSpacing(1)
        title = QLabel(name)
        title.setStyleSheet("font-weight: 600; font-size: 13px; background: transparent;")
        sub = QLabel(description)
        sub.setObjectName("Tiny")
        sub.setWordWrap(True)
        text.addWidget(title)
        text.addWidget(sub)
        lay.addLayout(text, 1)

    def mouseReleaseEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if event.button() == Qt.MouseButton.LeftButton:
            self._on_click()
        super().mouseReleaseEvent(event)


class EmptyState(QFrame):
    """Dashed, centred placeholder for a genuinely empty collection.

    Gives an empty page a deliberate composition (icon + title + guidance +
    actions) instead of a lone line of text floating in a void.
    """

    def __init__(self, icon, title: str, description: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("EmptyState")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(28, 34, 28, 34)
        lay.setSpacing(10)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        badge = QLabel()
        badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if icon is not None:
            badge.setPixmap(icon.pixmap(42, 42))
        lay.addWidget(badge, 0, Qt.AlignmentFlag.AlignHCenter)

        title_label = QLabel(title)
        title_label.setObjectName("EmptyTitle")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(title_label)

        if description:
            desc = muted(description)
            desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lay.addWidget(desc)

        self.actions = QHBoxLayout()
        self.actions.setSpacing(8)
        self.actions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addLayout(self.actions)

    def add_action(self, button: QWidget) -> None:
        self.actions.addWidget(button)


# -- text primitives -----------------------------------------------------
def heading(text: str, object_name: str = "SectionTitle") -> QLabel:
    label = QLabel(text)
    label.setObjectName(object_name)
    label.setTextFormat(Qt.TextFormat.PlainText)
    return label


def eyebrow(text: str) -> QLabel:
    label = QLabel(text.upper())
    label.setObjectName("Eyebrow")
    return label


def hero_title(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("HeroTitle")
    label.setTextFormat(Qt.TextFormat.PlainText)
    return label


def muted(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Muted")
    label.setWordWrap(True)
    return label


def tiny(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Tiny")
    label.setWordWrap(True)
    return label


def gold_label(text: str) -> QLabel:
    label = QLabel(text)
    label.setObjectName("Gold")
    return label
