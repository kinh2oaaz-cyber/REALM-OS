"""Event editor dialog."""

from __future__ import annotations

from datetime import datetime

from PySide6.QtCore import QDate, QDateTime, Qt, QTime
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QDateTimeEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from .models import CalendarEvent, RECURRENCE_FREQS, Recurrence

_REMINDERS = [
    ("No reminder", -1),
    ("At start", 0),
    ("5 minutes before", 5),
    ("10 minutes before", 10),
    ("15 minutes before", 15),
    ("30 minutes before", 30),
    ("1 hour before", 60),
    ("1 day before", 1440),
]


class EventDialog(QDialog):
    def __init__(self, event: CalendarEvent | None = None, categories: list[dict] | None = None,
                 default_start: datetime | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Event")
        self.setMinimumWidth(460)
        self.result_event: CalendarEvent | None = None
        self._color = event.color if event else ""
        self._categories = categories or []

        root = QVBoxLayout(self)
        form = QFormLayout()
        form.setSpacing(10)

        self.title_edit = QLineEdit(event.title if event else "")
        self.title_edit.setPlaceholderText("Event title")
        form.addRow("Title", self.title_edit)

        start_dt = _to_qdt(event.start if event else _fmt(default_start or datetime.now()))
        end_dt = _to_qdt(event.end if (event and event.end) else _fmt((default_start or datetime.now())))
        self.start_edit = QDateTimeEdit(start_dt)
        self.start_edit.setCalendarPopup(True)
        self.start_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.end_edit = QDateTimeEdit(end_dt)
        self.end_edit.setCalendarPopup(True)
        self.end_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        form.addRow("Start", self.start_edit)
        form.addRow("End", self.end_edit)

        self.all_day = QCheckBox("All day")
        self.all_day.setChecked(event.all_day if event else False)
        form.addRow("", self.all_day)

        self.location_edit = QLineEdit(event.location if event else "")
        self.location_edit.setPlaceholderText("Location")
        form.addRow("Location", self.location_edit)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        self.category_combo.addItem("")
        for cat in self._categories:
            self.category_combo.addItem(cat["name"])
        self.category_combo.setCurrentText(event.category if event else "")
        form.addRow("Category", self.category_combo)

        color_row = QHBoxLayout()
        self.color_btn = QPushButton("Choose…")
        self.color_btn.clicked.connect(self._pick_color)
        self.color_swatch = QLabel()
        self.color_swatch.setFixedSize(22, 22)
        self._update_swatch()
        color_row.addWidget(self.color_btn)
        color_row.addWidget(self.color_swatch)
        color_row.addStretch(1)
        form.addRow("Color", _wrap(color_row))

        self.desc_edit = QTextEdit(event.description if event else "")
        self.desc_edit.setPlaceholderText("Description")
        self.desc_edit.setFixedHeight(90)
        form.addRow("Description", self.desc_edit)

        # recurrence
        rec = event.recurrence if event else Recurrence()
        self.recur_combo = QComboBox()
        self.recur_combo.addItems(RECURRENCE_FREQS)
        self.recur_combo.setCurrentText(rec.freq)
        form.addRow("Repeats", self.recur_combo)
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 365)
        self.interval_spin.setValue(rec.interval)
        form.addRow("Every N", self.interval_spin)
        self.recur_count = QSpinBox()
        self.recur_count.setRange(0, 9999)
        self.recur_count.setValue(rec.count or 0)
        self.recur_count.setToolTip("0 = no limit")
        form.addRow("Occurrences (0=∞)", self.recur_count)

        # reminder
        self.reminder_combo = QComboBox()
        for label, mins in _REMINDERS:
            self.reminder_combo.addItem(label, mins)
        cur_rem = event.reminder_minutes if event else -1
        idx = next((i for i, (_, m) in enumerate(_REMINDERS) if m == cur_rem), 0)
        self.reminder_combo.setCurrentIndex(idx)
        form.addRow("Reminder", self.reminder_combo)

        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    def _pick_color(self) -> None:
        color = QColorDialog.getColor(QColor(self._color or "#0071E3"), self, "Event color")
        if color.isValid():
            self._color = color.name()
            self._update_swatch()

    def _update_swatch(self) -> None:
        c = self._color or "#0071E3"
        self.color_swatch.setStyleSheet(f"background:{c};border:1px solid #999;border-radius:4px;")

    def _accept(self) -> None:
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "Event", "Please enter a title.")
            return
        freq = self.recur_combo.currentText()
        rec = Recurrence(
            freq=freq,
            interval=self.interval_spin.value(),
            count=self.recur_count.value() or None,
        )
        start = self.start_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        end = self.end_edit.dateTime().toString("yyyy-MM-dd HH:mm")
        if self.all_day.isChecked():
            start = self.start_edit.date().toString("yyyy-MM-dd")
            end = self.end_edit.date().toString("yyyy-MM-dd")
        self.result_event = CalendarEvent(
            title=title,
            description=self.desc_edit.toPlainText(),
            location=self.location_edit.text().strip(),
            start=start,
            end=end,
            all_day=self.all_day.isChecked(),
            category=self.category_combo.currentText().strip(),
            color=self._color,
            recurrence=rec,
            reminder_minutes=self.reminder_combo.currentData(),
        )
        self.accept()


def _wrap(layout) -> QWidget:  # noqa: ANN001
    w = QWidget()
    w.setLayout(layout)
    return w


def _to_qdt(value: str) -> QDateTime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(value, fmt)
            return QDateTime(QDate(dt.year, dt.month, dt.day), QTime(dt.hour, dt.minute))
        except ValueError:
            continue
    now = datetime.now()
    return QDateTime(QDate(now.year, now.month, now.day), QTime(now.hour, now.minute))


def _fmt(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d %H:%M")
