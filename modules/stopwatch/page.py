"""Stopwatch & Timer."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QPushButton, QSpinBox, QTabWidget, QVBoxLayout, QWidget

from ui.components.page import RealmPage


def _fmt_ms(ms: int) -> str:
    cs = (ms // 10) % 100; s = (ms // 1000) % 60; m = (ms // 60000) % 60; h = ms // 3600000
    return f"{h:02d}:{m:02d}:{s:02d}.{cs:02d}"


def _fmt_s(seconds: int) -> str:
    m = seconds // 60; s = seconds % 60
    return f"{m:02d}:{s:02d}"


class Stopwatch(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._elapsed = 0; self._running = False; self._laps: list[int] = []
        lay = QVBoxLayout(self); lay.setSpacing(12)
        self.display = QLabel("00:00:00.00"); self.display.setAlignment(Qt.AlignmentFlag.AlignCenter); self.display.setStyleSheet("font-size:32px; font-weight:600;"); lay.addWidget(self.display)
        btns = QHBoxLayout(); btns.setSpacing(8)
        self.start_btn = QPushButton("Start"); self.start_btn.setObjectName("PrimaryButton"); self.start_btn.clicked.connect(self.toggle); btns.addWidget(self.start_btn)
        self.lap_btn = QPushButton("Lap"); self.lap_btn.clicked.connect(self.lap); btns.addWidget(self.lap_btn)
        self.reset_btn = QPushButton("Reset"); self.reset_btn.clicked.connect(self.reset); btns.addWidget(self.reset_btn)
        lay.addLayout(btns)
        self.laps_list = QListWidget(); lay.addWidget(self.laps_list, 1)
        self._timer = QTimer(self); self._timer.setInterval(10); self._timer.timeout.connect(self._tick)

    def toggle(self) -> None:
        self._running = not self._running
        if self._running: self._timer.start(); self.start_btn.setText("Pause")
        else: self._timer.stop(); self.start_btn.setText("Start")

    def _tick(self) -> None:
        self._elapsed += 10; self.display.setText(_fmt_ms(self._elapsed))

    def lap(self) -> None:
        if self._running or self._elapsed:
            self._laps.append(self._elapsed); self.laps_list.insertItem(0, f"Lap {len(self._laps)}   {_fmt_ms(self._elapsed)}")

    def reset(self) -> None:
        self._timer.stop(); self._running = False; self._elapsed = 0; self._laps.clear()
        self.display.setText("00:00:00.00"); self.laps_list.clear(); self.start_btn.setText("Start")


class Timer(QWidget):
    def __init__(self, parent=None, notify=None) -> None:
        super().__init__(parent); self._notify = notify; self._remaining = 0; self._total = 0; self._running = False
        lay = QVBoxLayout(self); lay.setSpacing(12)
        self.display = QLabel("00:00"); self.display.setAlignment(Qt.AlignmentFlag.AlignCenter); self.display.setStyleSheet("font-size:32px; font-weight:600;"); lay.addWidget(self.display)
        setrow = QHBoxLayout(); setrow.addWidget(QLabel("Minutes")); self.min_spin = QSpinBox(); self.min_spin.setRange(0, 999); self.min_spin.setValue(5); setrow.addWidget(self.min_spin)
        setrow.addWidget(QLabel("Seconds")); self.sec_spin = QSpinBox(); self.sec_spin.setRange(0, 59); setrow.addWidget(self.sec_spin); lay.addLayout(setrow)
        btns = QHBoxLayout(); btns.setSpacing(8)
        self.start_btn = QPushButton("Start"); self.start_btn.setObjectName("PrimaryButton"); self.start_btn.clicked.connect(self.toggle); btns.addWidget(self.start_btn)
        self.reset_btn = QPushButton("Reset"); self.reset_btn.clicked.connect(self.reset); btns.addWidget(self.reset_btn)
        lay.addLayout(btns); lay.addStretch(1)
        self._timer = QTimer(self); self._timer.setInterval(1000); self._timer.timeout.connect(self._tick); self._sync()

    def _sync(self) -> None:
        if not self._running: self._remaining = self.min_spin.value() * 60 + self.sec_spin.value()
        self.display.setText(_fmt_s(self._remaining))

    def toggle(self) -> None:
        if not self._running:
            self._sync()
            if self._remaining <= 0: return
            self._running = True; self._timer.start(); self.start_btn.setText("Pause")
        else:
            self._running = False; self._timer.stop(); self.start_btn.setText("Start")

    def _tick(self) -> None:
        self._remaining -= 1
        if self._remaining <= 0:
            self._remaining = 0; self._running = False; self._timer.stop(); self.start_btn.setText("Start")
            if self._notify: self._notify("Timer finished", "Your countdown timer reached zero.")
        self.display.setText(_fmt_s(self._remaining))

    def reset(self) -> None:
        self._running = False; self._timer.stop(); self.start_btn.setText("Start"); self._sync()


class StopwatchPage(RealmPage):
    page_title = "Stopwatch & Timer"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        title = QLabel("Stopwatch & Timer"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        tabs = QTabWidget()
        tabs.addTab(Stopwatch(), "Stopwatch")
        notify = lambda t, m: self.context.notifications.add(t, m, app_id="stopwatch", level="info")
        tabs.addTab(Timer(notify=notify), "Timer")
        self.layout_root.addWidget(tabs, 1)
