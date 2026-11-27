"""Calendar page: monthly/weekly/daily views, events, reminders, search."""

from __future__ import annotations

from datetime import date, datetime, timedelta

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QAbstractItemView,
    QButtonGroup,
    QDialog,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage
from ui.icons import icon as _icon

from .dialogs import EventDialog
from .models import CalendarEvent
from .services import CalendarService

_VIEWS = ("Month", "Week", "Day")


class CalendarPage(RealmPage):
    page_title = "Calendar"

    def __init__(self, context, parent=None) -> None:
        self.service = CalendarService(context)
        self.view = "Month"
        self.cursor = date.today()          # focus date
        self._day_cells: list[QListWidget] = []
        super().__init__(context, parent)
        self._start_reminder_timer()

    # -- construction ---------------------------------------------------
    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(14)

        # header
        header = QHBoxLayout()
        title = QLabel("Calendar")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch(1)

        self.view_group = QButtonGroup(self)
        for i, name in enumerate(_VIEWS):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setChecked(name == self.view)
            btn.clicked.connect(lambda _c=False, n=name: self.set_view(n))
            self.view_group.addButton(btn, i)
            header.addWidget(btn)

        prev_btn = QPushButton("‹")
        prev_btn.clicked.connect(self.go_prev)
        today_btn = QPushButton("Today")
        today_btn.clicked.connect(self.go_today)
        next_btn = QPushButton("›")
        next_btn.clicked.connect(self.go_next)
        header.addWidget(prev_btn)
        header.addWidget(today_btn)
        header.addWidget(next_btn)

        add_btn = QPushButton("New Event")
        add_btn.setObjectName("PrimaryButton")
        add_btn.clicked.connect(lambda: self.open_event_editor(None, self.cursor))
        header.addWidget(add_btn)
        self.layout_root.addLayout(header)

        # period label + search
        toolbar = QHBoxLayout()
        self.period_label = QLabel()
        self.period_label.setObjectName("SectionTitle")
        toolbar.addWidget(self.period_label)
        toolbar.addStretch(1)
        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("SearchBox")
        self.search_edit.setPlaceholderText("Search events…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.returnPressed.connect(self.do_search)
        self.search_edit.textChanged.connect(lambda t: self.do_search() if not t else None)
        toolbar.addWidget(self.search_edit)
        self.layout_root.addLayout(toolbar)

        # body splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.calendar_container = QWidget()
        self.calendar_layout = QVBoxLayout(self.calendar_container)
        self.calendar_layout.setContentsMargins(0, 0, 0, 0)
        splitter.addWidget(self.calendar_container)

        side = QWidget()
        side_layout = QVBoxLayout(side)
        side_layout.setContentsMargins(0, 0, 0, 0)
        side_layout.setSpacing(12)
        sched_title = QLabel("Schedule")
        sched_title.setObjectName("SectionTitle")
        side_layout.addWidget(sched_title)
        self.schedule_list = QListWidget()
        self.schedule_list.setObjectName("ScheduleList")
        self.schedule_list.itemDoubleClicked.connect(self._open_event_from_item)
        side_layout.addWidget(self.schedule_list, 1)
        today_label = QLabel("Today")
        today_label.setObjectName("SectionTitle")
        side_layout.addWidget(today_label)
        self.today_list = QListWidget()
        self.today_list.itemDoubleClicked.connect(self._open_event_from_item)
        side_layout.addWidget(self.today_list, 1)
        splitter.addWidget(side)
        splitter.setSizes([780, 320])
        self.layout_root.addWidget(splitter, 1)

        self._render()

    # -- views ----------------------------------------------------------
    def set_view(self, name: str) -> None:
        self.view = name
        self._render()

    def go_today(self) -> None:
        self.cursor = date.today()
        self._render()

    def go_prev(self) -> None:
        self.cursor = self._shift(-1)
        self._render()

    def go_next(self) -> None:
        self.cursor = self._shift(1)
        self._render()

    def _shift(self, direction: int) -> date:
        if self.view == "Month":
            first = self.cursor.replace(day=1)
            if direction < 0:
                return (first - timedelta(days=1)).replace(day=1)
            # next month
            return (first + timedelta(days=32)).replace(day=1)
        if self.view == "Week":
            return self.cursor + timedelta(weeks=direction)
        return self.cursor + timedelta(days=direction)

    def _render(self) -> None:
        self._clear(self.calendar_layout)
        self._day_cells.clear()
        if self.view == "Month":
            self._render_month()
        elif self.view == "Week":
            self._render_week()
        else:
            self._render_day()
        self._render_schedule()
        self._render_today()

    def _render_month(self) -> None:
        self.period_label.setText(self.cursor.strftime("%B %Y"))
        # week header
        grid = QGridLayout()
        grid.setSpacing(6)
        for col, name in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
            lbl = QLabel(name)
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl.setObjectName("Muted")
            grid.addWidget(lbl, 0, col)
        first = self.cursor.replace(day=1)
        start = first - timedelta(days=first.weekday())
        range_end = start + timedelta(days=42)
        events = self.service.events_in_range(datetime.combine(start, datetime.min.time()),
                                               datetime.combine(range_end, datetime.min.time()))
        today = date.today()
        for i in range(42):
            day = start + timedelta(days=i)
            cell = QListWidget()
            cell.setObjectName("Card")
            cell.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            header = QListWidgetItem(str(day.day))
            header.setFlags(Qt.ItemFlag.NoItemFlags)
            f = QFont(); f.setBold(True)
            header.setFont(f)
            if day.month != self.cursor.month:
                header.setForeground(Qt.GlobalColor.gray)
            if day == today:
                header.setForeground(Qt.GlobalColor.blue)
            cell.addItem(header)
            for ev in self._events_on(events, day):
                item = QListWidgetItem(ev.title)
                color = ev.color or self._category_color(ev.category)
                item.setForeground(_qcolor(color))
                item.setToolTip(f"{ev.start}  {ev.end}\n{ev.location}\n{ev.description}")
                item.setData(Qt.ItemDataRole.UserRole, ev.id)
                cell.addItem(item)
            cell.setMinimumHeight(84)
            cell.itemDoubleClicked.connect(self._open_event_from_item)
            # click header area to add
            cell.itemClicked.connect(lambda _it, d=day: None)
            row = 1 + i // 7
            col = i % 7
            grid.addWidget(cell, row, col)
            self._day_cells.append(cell)
        # double-click empty cell to add: wrap
        grid.setRowStretch(7, 0)
        wrap = QWidget(); wrap.setLayout(grid)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setWidget(wrap)
        self.calendar_layout.addWidget(scroll)

    def _render_week(self) -> None:
        start = self.cursor - timedelta(days=self.cursor.weekday())
        end = start + timedelta(days=7)
        self.period_label.setText(f"Week of {start.strftime('%d %b %Y')}")
        events = self.service.events_in_range(datetime.combine(start, datetime.min.time()),
                                              datetime.combine(end, datetime.min.time()))
        grid = QGridLayout(); grid.setSpacing(8)
        today = date.today()
        for col in range(7):
            day = start + timedelta(days=col)
            header = QLabel(day.strftime("%a\n%d %b"))
            header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            header.setObjectName("Card")
            if day == today:
                header.setStyleSheet("font-weight:700; color: palette(highlight);")
            grid.addWidget(header, 0, col)
            cell = QListWidget(); cell.setObjectName("Card")
            cell.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
            for ev in self._events_on(events, day):
                item = QListWidgetItem(f"{ev.start[11:16]}  {ev.title}" if len(ev.start) > 10 else ev.title)
                item.setForeground(_qcolor(ev.color or self._category_color(ev.category)))
                item.setData(Qt.ItemDataRole.UserRole, ev.id)
                cell.addItem(item)
            cell.itemDoubleClicked.connect(self._open_event_from_item)
            cell.setMinimumHeight(320)
            grid.addWidget(cell, 1, col)
        wrap = QWidget(); wrap.setLayout(grid)
        self.calendar_layout.addWidget(wrap)

    def _render_day(self) -> None:
        self.period_label.setText(self.cursor.strftime("%A, %d %B %Y"))
        events = self.service.events_on_day(datetime.combine(self.cursor, datetime.min.time()))
        cell = QListWidget(); cell.setObjectName("Card")
        cell.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        if not events:
            cell.addItem("No events today. Double-click to add.")
        for ev in events:
            when = "All day" if ev.all_day else f"{ev.start[11:16]}–{ev.end[11:16]}"
            item = QListWidgetItem(f"{when}   {ev.title}   {('· ' + ev.location) if ev.location else ''}")
            item.setForeground(_qcolor(ev.color or self._category_color(ev.category)))
            item.setData(Qt.ItemDataRole.UserRole, ev.id)
            cell.addItem(item)
        cell.itemDoubleClicked.connect(self._open_event_from_item)
        # double-click empty space adds event
        self.calendar_layout.addWidget(cell, 1)

    # -- schedule side --------------------------------------------------
    def _render_schedule(self) -> None:
        self.schedule_list.clear()
        events = self.service.upcoming(days=30, limit=100)
        for ev in events:
            item = QListWidgetItem(f"{ev.start[:16]}  {ev.title}")
            item.setData(Qt.ItemDataRole.UserRole, ev.id)
            self.schedule_list.addItem(item)

    def _render_today(self) -> None:
        self.today_list.clear()
        for ev in self.service.today_schedule():
            when = "All day" if ev.all_day else ev.start[11:16]
            item = QListWidgetItem(f"{when}  {ev.title}")
            item.setData(Qt.ItemDataRole.UserRole, ev.id)
            self.today_list.addItem(item)

    # -- events ---------------------------------------------------------
    def open_event_editor(self, event: CalendarEvent | None, day: date | None = None) -> None:
        default_start = datetime.combine(day or self.cursor, datetime.now().time().replace(second=0, microsecond=0))
        dlg = EventDialog(event, self.service.categories(), default_start=default_start, parent=self)
        if event is not None:
            dlg.setWindowTitle("Edit Event")
        if dlg.exec() != QDialog.DialogCode.Accepted or dlg.result_event is None:
            return
        result = dlg.result_event
        try:
            if event is not None and event.id is not None:
                result.id = event.id
                self.service.update_event(result)
            else:
                self.service.create_event(result)
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Calendar", f"Could not save event:\n{exc}")
            return
        self._render()

    def _open_event_from_item(self, item: QListWidgetItem) -> None:
        eid = item.data(Qt.ItemDataRole.UserRole)
        if eid is None:
            return
        event = self.service.get_event(int(eid))
        if event is None:
            return
        self.open_event_editor(event)
        # offer delete / create task
        # (kept simple; delete via button in editor future)

    def _add_event_on_day(self, day: date) -> None:
        self.open_event_editor(None, day)

    def do_search(self) -> None:
        query = self.search_edit.text().strip()
        self.schedule_list.clear()
        if not query:
            self._render_schedule()
            return
        for ev in self.service.search(query):
            item = QListWidgetItem(f"{ev.start[:16]}  {ev.title}")
            item.setData(Qt.ItemDataRole.UserRole, ev.id)
            self.schedule_list.addItem(item)

    # -- reminders ------------------------------------------------------
    def _start_reminder_timer(self) -> None:
        self._reminder_timer = QTimer(self)
        self._reminder_timer.setInterval(30_000)
        self._reminder_timer.timeout.connect(self._check_reminders)
        self._reminder_timer.start()
        self._reminded: set[tuple[int, str]] = set()

    def _check_reminders(self) -> None:
        try:
            due = self.service.due_reminders()
        except Exception:  # noqa: BLE001
            return
        for ev in due:
            key = (ev.id or -1, ev.start)
            if key in self._reminded:
                continue
            self._reminded.add(key)
            if self.context.settings.get_bool("notifications.enabled", True):
                self.context.notifications.add(
                    f" {ev.title}", f"Starts {ev.start}" + (f" · {ev.location}" if ev.location else ""),
                    app_id="calendar", level="info",
                )

    # -- lifecycle ------------------------------------------------------
    def on_show(self) -> None:
        self._render()

    # -- helpers --------------------------------------------------------
    def _events_on(self, events: list[CalendarEvent], day: date) -> list[CalendarEvent]:
        result = []
        for ev in events:
            ev_day = _parse_day(ev.start)
            if ev_day == day:
                result.append(ev)
            elif ev.all_day:
                ev_end = _parse_day(ev.end) or ev_day
                if ev_day and ev_day <= day <= ev_end:
                    result.append(ev)
        result.sort(key=lambda e: e.start)
        return result

    def _category_color(self, name: str) -> str:
        for cat in self.service.categories():
            if cat["name"] == name:
                return cat["color"]
        return "#0071E3"

    def _clear(self, layout) -> None:  # noqa: ANN001
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                self._clear(item.layout())


def _parse_day(value: str) -> date | None:
    if not value:
        return None
    try:
        return datetime.strptime(value[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _qcolor(hex_color: str):
    from PySide6.QtGui import QColor
    c = QColor(hex_color or "#0071E3")
    return c if c.isValid() else QColor("#0071E3")


