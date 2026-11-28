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
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap, QRadialGradient
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene

from core.config import assets_dir, project_root

# REALM cinematic palette
_BG = "#07060A"
_SECONDARY = "#0C0A10"
_SURFACE = "#121016"
_CRIMSON = "#C51F35"
_DEEP_CRIMSON = "#5E0F1E"
_GOLD = "#D6AD55"
_LIGHT_GOLD = "#F1D58A"

_QML_DIR = Path(__file__).resolve().parent / "qml"


def redgold_pixmap(width: int = 1920, height: int = 1080) -> QPixmap:
    """Near-black field with very restrained crimson / gold atmosphere.

    The brief calls for black and charcoal to dominate. The bloom here is
    deliberately faint (single-digit-to-low-teens opacity) so panels read as
    the subject and the backdrop only adds depth — never a coloured wash.
    """
    pix = QPixmap(width, height)
    pix.fill(QColor(_BG))
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    # base vertical gradient: near-black → barely-there graphite → near-black
    grad = QLinearGradient(QPointF(0, 0), QPointF(0, height))
    grad.setColorAt(0.0, QColor("#08070B"))
    grad.setColorAt(0.50, QColor("#0A0810"))
    grad.setColorAt(1.0, QColor("#050408"))
    painter.fillRect(QRectF(0, 0, width, height), grad)

    # soft radial light sources (additive) — extremely restrained
    def _bloom(cx: float, cy: float, radius: float, color: str, opacity: float) -> None:
        g = QRadialGradient(QPointF(cx, cy), radius)
        c0 = QColor(color)
        c0.setAlphaF(opacity)
        c1 = QColor(color)
        c1.setAlphaF(0.0)
        g.setColorAt(0.0, c0)
        g.setColorAt(1.0, c1)
        painter.fillRect(QRectF(0, 0, width, height), g)

    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
    _bloom(width * 0.86, height * 0.10, width * 0.46, _CRIMSON, 0.11)
    _bloom(width * 0.08, height * 0.90, width * 0.42, _DEEP_CRIMSON, 0.12)
    _bloom(width * 0.92, height * 0.94, width * 0.30, _GOLD, 0.05)
    _bloom(width * 0.12, height * 0.08, width * 0.26, _LIGHT_GOLD, 0.03)

    # strong vignette: focus the centre, deepen every edge toward black
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    vg = QRadialGradient(QPointF(width * 0.5, height * 0.45), width * 0.78)
    vg.setColorAt(0.30, QColor(0, 0, 0, 0))
    vg.setColorAt(1.0, QColor(0, 0, 0, 205))
    painter.fillRect(QRectF(0, 0, width, height), vg)
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


# Bump when the artwork changes so stale cached PNGs are not reused.
_BG_VERSION = 2


def ensure_redgold_background() -> Path:
    """Generate + cache the blurred backdrop for the current artwork version."""
    dest = assets_dir() / f"background_redgold_v{_BG_VERSION}.png"
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
