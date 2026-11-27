"""Frosted-glass / blurred background helpers.

Honest note: Qt QSS has **no `backdrop-filter: blur`**. REALM OS
provides a pre-blurred **red + gold** background image (generated
once, bundled) + translucent panels for a frosted-glass look, OR a
`QGraphicsBlurEffect` on a dedicated background widget. No sci-fi/neon.
"""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QPointF, QRectF, Qt
from PySide6.QtGui import QColor, QLinearGradient, QPainter, QPixmap
from PySide6.QtWidgets import QGraphicsBlurEffect, QGraphicsPixmapItem, QGraphicsScene

from core.config import assets_dir


def redgold_pixmap(width: int = 1920, height: int = 1080) -> QPixmap:
    """A redgold gradient pixmap (pre-blur source)."""
    pix = QPixmap(width, height)
    pix.fill(QColor("#0F1114"))
    painter = QPainter(pix)
    grad = QLinearGradient(QPointF(0, 0), QPointF(width, height))
    grad.setColorAt(0.0, QColor("#2A0B12"))    # deep red
    grad.setColorAt(0.35, QColor("#3A0D14"))   # red
    grad.setColorAt(0.55, QColor("#5A1420"))   # red
    grad.setColorAt(0.78, QColor("#6E3A2A"))   # red-orange
    grad.setColorAt(1.0, QColor("#C8AA6E"))    # Riot gold
    painter.fillRect(QRectF(0, 0, width, height), grad)
    # soft gold/red glows
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Screen)
    painter.setOpacity(0.35)
    painter.fillRect(QRectF(width * 0.55, height * 0.1, width * 0.5, height * 0.6), QColor("#C8AA6E"))
    painter.setOpacity(0.25)
    painter.fillRect(QRectF(0, height * 0.4, width * 0.4, height * 0.6), QColor("#E84057"))
    painter.end()
    return pix


def blur_pixmap(source: QPixmap, radius: int = 48) -> QPixmap:
    """Return a blurred copy of `source` via QGraphicsBlurEffect."""
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


def blurred_redgold(width: int = 1920, height: int = 1080, radius: int = 48) -> QPixmap:
    return blur_pixmap(redgold_pixmap(width, height), radius)


def ensure_redgold_background() -> Path:
    """Generate + cache `assets/background_redgold.png`. Returns path."""
    dest = assets_dir() / "background_redgold.png"
    if not dest.exists():
        pix = blurred_redgold()
        dest.parent.mkdir(parents=True, exist_ok=True)
        pix.save(str(dest), "PNG")
    return dest
