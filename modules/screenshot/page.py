"""Screenshot Tool: capture full screen / active window, save PNG."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QGuiApplication, QPixmap
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QScrollArea, QVBoxLayout

from ui.components.page import RealmPage

_OUT_DIR = Path.home() / "Pictures" / "REALM OS Screenshots"


class ScreenshotPage(RealmPage):
    page_title = "Screenshot Tool"

    def __init__(self, context, parent=None) -> None:
        self._last_pixmap: QPixmap | None = None
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        title = QLabel("Screenshot Tool"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        row = QHBoxLayout(); row.setSpacing(8)
        full = QPushButton("Capture full screen"); full.setObjectName("PrimaryButton"); full.clicked.connect(lambda: self.capture("screen")); row.addWidget(full)
        win = QPushButton("Capture active window"); win.clicked.connect(lambda: self.capture("window")); row.addWidget(win)
        save = QPushButton("Save…"); save.clicked.connect(self.save); row.addWidget(save); row.addStretch(1); self.layout_root.addLayout(row)
        hint = QLabel("A short delay is applied so you can focus the target. Screenshots are saved as PNG."); hint.setObjectName("Muted"); self.layout_root.addWidget(hint)
        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.preview = QLabel("No capture yet"); self.preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll.setWidget(self.preview); self.layout_root.addWidget(self.scroll, 1)

    def capture(self, mode: str) -> None:
        # hide ourselves briefly then capture
        QTimer.singleShot(250, lambda: self._grab(mode))

    def _grab(self, mode: str) -> None:
        screen = QGuiApplication.primaryScreen()
        if screen is None: return
        if mode == "window":
            win = QGuiApplication.focusWindow()
            if win is not None:
                pix = screen.grabWindow(int(win.winId()))
            else:
                pix = screen.grabWindow(0)
        else:
            pix = screen.grabWindow(0)
        self._last_pixmap = pix
        self.preview.setPixmap(pix.scaledToWidth(min(1000, pix.width()), Qt.TransformationMode.SmoothTransformation))

    def save(self) -> None:
        if self._last_pixmap is None or self._last_pixmap.isNull():
            QMessageBox.information(self, "Screenshot", "Take a screenshot first."); return
        _OUT_DIR.mkdir(parents=True, exist_ok=True)
        default = str(_OUT_DIR / f"Screenshot {datetime.now():%Y-%m-%d %H-%M-%S}.png")
        dest, _ = QFileDialog.getSaveFileName(self, "Save screenshot", default, "PNG (*.png)")
        if not dest: return
        if self._last_pixmap.save(dest, "PNG"):
            QMessageBox.information(self, "Screenshot", f"Saved:\n{dest}")
        else:
            QMessageBox.warning(self, "Screenshot", "Could not save.")
