"""Motion engine — smooth transitions/animations for REALM OS.

IMPORTANT (honesty): Framer Motion is a **React/JavaScript** library and
cannot run inside this PySide6/Python app. REALM OS uses **Qt's own
animation engine** (`QPropertyAnimation`, `QEasingCurve`,
`QGraphicsOpacityEffect`, `QVariantAnimation`, `QSequentialAnimationGroup`)
which provides equivalent smooth motion. Respects
`appearance.reduce_motion`.
"""

from __future__ import annotations

from PySide6.QtCore import QEasingCurve, QObject, QPoint, QPropertyAnimation, QTimer
from PySide6.QtWidgets import QGraphicsOpacityEffect, QWidget

# sensible defaults
DEFAULT_DURATION = 180
EASING = QEasingCurve.Type.OutCubic

_active: list[QPropertyAnimation] = []  # keep refs alive


def motion_enabled(settings=None) -> bool:  # noqa: ANN001
    if settings is None:
        return True
    try:
        return not bool(settings.get_bool("appearance.reduce_motion", False))
    except Exception:  # noqa: BLE001
        return True


def _track(anim: QPropertyAnimation) -> QPropertyAnimation:
    _active.append(anim)
    anim.finished.connect(lambda: _active.remove(anim) if anim in _active else None)
    return anim


def fade_in(widget: QWidget, duration: int = DEFAULT_DURATION, settings=None) -> None:  # noqa: ANN001
    """Fade a widget from transparent to opaque."""
    if not motion_enabled(settings):
        return
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(0.0)
    anim.setEndValue(1.0)
    anim.setEasingCurve(EASING)
    anim.finished.connect(lambda: widget.setGraphicsEffect(None))
    _track(anim)
    anim.start()


def fade_out(widget: QWidget, duration: int = DEFAULT_DURATION, settings=None) -> None:  # noqa: ANN001
    if not motion_enabled(settings):
        return
    effect = QGraphicsOpacityEffect(widget)
    widget.setGraphicsEffect(effect)
    anim = QPropertyAnimation(effect, b"opacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(1.0)
    anim.setEndValue(0.0)
    anim.setEasingCurve(QEasingCurve.Type.OutCubic)
    _track(anim)
    anim.start()


def slide_in(widget: QWidget, dx: int = 24, dy: int = 0, duration: int = 200, settings=None) -> None:  # noqa: ANN001
    """Slide + fade a widget in (from an offset) to its natural position."""
    if not motion_enabled(settings):
        return
    end_pos = widget.pos()
    start_pos = QPoint(end_pos.x() + dx, end_pos.y() + dy)
    fade_in(widget, duration=duration, settings=settings)
    anim = QPropertyAnimation(widget, b"pos", widget)
    anim.setDuration(duration)
    anim.setStartValue(start_pos)
    anim.setEndValue(end_pos)
    anim.setEasingCurve(EASING)
    _track(anim)
    anim.start()


def pop(widget: QWidget, duration: int = 120, settings=None) -> None:  # noqa: ANN001
    """Brief scale-pop feedback on a widget (e.g. button click)."""
    if not motion_enabled(settings):
        return
    anim = QPropertyAnimation(widget, b"windowOpacity", widget)
    anim.setDuration(duration)
    anim.setStartValue(1.0); anim.setKeyValueAt(0.5, 0.85); anim.setEndValue(1.0)
    _track(anim); anim.start()


def page_transition(page: QWidget, settings=None) -> None:  # noqa: ANN001
    """Apply the standard page-enter transition (slide + fade)."""
    slide_in(page, dx=20, dy=6, duration=220, settings=settings)


def smooth_scroll(scroll_area, delta: int) -> None:  # noqa: ANN001
    """Animated smooth scrolling for a QScrollArea / scrollbar."""
    bar = scroll_area.verticalScrollBar()
    anim = QPropertyAnimation(bar, b"value", scroll_area)
    anim.setDuration(180); anim.setStartValue(bar.value()); anim.setEndValue(bar.value() + delta); anim.setEasingCurve(EASING)
    _track(anim); anim.start()
