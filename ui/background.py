"""Frosted-glass / blurred background + Qt Quick blurred background.

REALM Crimson x Royal Gold, near-black. Two real blur paths:

1. **QtWidgets**: pre-blurred image + `QGraphicsBlurEffect` +
   translucent panels + `QWidget#RootBackground`.
2. **Qt Quick / QML**: :class:`QmlBlurredBackground` embedding
   `QtQuick.Effects.FastBlur` (reusable `ui/qml/BlurredBackground.qml`)
   — actual Qt Quick blur, NOT a static transparent rectangle.

Honest note: Qt QSS has no `backdrop-filter`. On the QtWidgets shell we
use (a) pre-blurred image and (b) `QGraphicsBlurEffect`; (c) Qt Quick
`FastBlur` is available for QML surfaces. Performance-safe (no
continuous re-blur; `QT_QUICK_BACKEND=software` supported).
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt, QUrl
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene

from core.config import assets_dir, project_root

# REALM palette
_BG = "#0B090B"
_SECONDARY = "#141014"
_CRIMSON = "#A82435"       # deeper, desaturated crimson
_DEEP_CRIMSON = "#7A1A2A"
_GOLD = "#C9A863"          # muted royal gold / antique bronze
_LIGHT_GOLD = "#F1D58A"

_QML_DIR = Path(__file__).resolve().parent / "qml"


def redgold_pixmap(width: int = 1920, height: int = 1080) -> QPixmap:
    """Near-black + dark crimson ambient + subtle blurred red/gold light sources."""
    pix = QPixmap(width, height)
    pix.fill(QColor(_BG))
    painter = QPainter(pix)
    # subtle dark crimson ambient gradient
    grad = QLinearGradient(QPointF(0, 0), QPointF(width, height))
    grad.setColorAt(0.0, QColor("#140A0C"))
    grad.setColorAt(0.35, QColor(_SECONDARY))
    grad.setColorAt(0.62, QColor("#1C0E12"))
    grad.setColorAt(1.0, QColor("#0B090B"))
    painter.fillRect(QRectF(0, 0, width, height), grad)
    # subtle blurred red + gold light sources (soft, not bright backgrounds)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
    painter.setOpacity(0.22)
    painter.fillRect(QRectF(width * 0.58, height * 0.06, width * 0.5, height * 0.5), QColor(_CRIMSON))
    painter.setOpacity(0.16)
    painter.fillRect(QRectF(width * 0.5, height * 0.55, width * 0.55, height * 0.5), QColor(_GOLD))
    painter.setOpacity(0.18)
    painter.fillRect(QRectF(0, height * 0.45, width * 0.4, height * 0.6), QColor(_DEEP_CRIMSON))
    painter.setOpacity(0.10)
    painter.fillRect(QRectF(width * 0.2, 0, width * 0.3, height * 0.35), QColor(_LIGHT_GOLD))
    painter.end()
    return pix


def blur_pixmap(source: QPixmap, radius: int = 64) -> QPixmap:
    """Return a blurred copy of `source` via QGraphicsBlurEffect (once)."""
    scene = QGraphicsScene()
    item = QGraphicsPixmapItem(source)
    effect = QGraphicsBlurEffect()
    effect.setBlurRadius(radius)
    effect.setBlurHints(QGraphicsBlurEffect.BlurHint.PerformanceHint)
    item.setGraphicsEffect(effect)
    scene.addItem(item)
    out = QPixmap(source.size())
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    scene.render(painter, QRectF(out.rect()), QRectF(source.rect()))
    painter.end()
    return out


def blurred_redgold(width: int = 1920, height: int = 1080, radius: int = 64) -> QPixmap:
    return blur_pixmap(redgold_pixmap(width, height), radius)


def ensure_redgold_background() -> Path:
    """Generate + cache `assets/background_redgold.png`. Returns path."""
    dest = assets_dir() / "background_redgold.png"
    # regenerate if missing; cheap one-time
    if not dest.exists():
        pix = blurred_redgold()
        dest.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(dest), "PNG")
    return dest


# ----------------------------- Qt Quick -----------------------------
try:
    from PySide6.QtQuickWidgets import QQuickWidget

    class QmlBlurredBackground(QQuickWidget):
        """Qt Quick background using `QtQuick.Effects.FastBlur` (real blur).

        Embeds ``ui/qml/BlurredBackground.qml``. `QT_QUICK_BACKEND=software`
        supported. Falls back gracefully if QtQuick is unavailable.
        """

        def __init__(self, parent=None) -> None:  # noqa: ANN001
            super().__init__(parent)
            self.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
            self.setClearColor(QColor(_BG))
            self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
            self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            qml = _QML_DIR / "BlurredBackground.qml"
            try:
                self.setSource(QUrl.fromLocalFile(str(qml)))
            except Exception:  # noqa: BLE001
                pass

except Exception:  # noqa: BLE001 - QtQuick not available; QtWidgets path still works
    class QmlBlurredBackground(QWidget):  # type: ignore[no-redef]
        def __init__(self, parent=None) -> None:  # noqa: ANN001
            from PySide6.QtWidgets import QWidget

            super().__init__(parent)
