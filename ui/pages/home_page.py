"""Home page: simple, practical launcher + personal dashboard."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.cards import Card, heading, muted
from ui.components.page import RealmPage

if TYPE_CHECKING:
    from core.app_registry import AppInfo
    from core.context import AppContext


def _app_tile(app: "AppInfo", favorite: bool, context: "AppContext") -> QWidget:
    tile = QPushButton()
    tile.setCursor(Qt.CursorShape.PointingHandCursor)
    tile.setMinimumHeight(72)
    tile.setStyleSheet(
        "QPushButton { text-align: left; padding: 12px 14px; border-radius: 12px;"
        " background: palette(base); border: 1px solid palette(mid); }"
        "QPushButton:hover { border-color: palette(highlight); }"
    )
    inner = QVBoxLayout(tile)
    inner.setContentsMargins(12, 10, 12, 10)
    inner.setSpacing(2)
    title = QLabel(app.name)
    title.setStyleSheet("font-weight: 600; background: transparent; border: none;")
    sub = QLabel(app.description)
    sub.setObjectName("Muted")
    sub.setStyleSheet("background: transparent; border: none; font-size: 11px;")
    sub.setWordWrap(True)
    inner.addWidget(title)
    inner.addWidget(sub)
    tile.clicked.connect(lambda _c=False, aid=app.id: context.navigate(aid))
    return tile


class HomePage(RealmPage):
    page_title = "Home"

    def __init__(self, context: "AppContext", parent=None) -> None:
        self._cards: list[QWidget] = []
        super().__init__(context, parent)

    # -- construction ---------------------------------------------------
    def build_ui(self) -> None:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        content = QWidget()
        self._content_layout = QVBoxLayout(content)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(20)
        scroll.setWidget(content)
        self.layout_root.addWidget(scroll)

        # header
        header = QVBoxLayout()
        header.setSpacing(4)
        self._greeting = heading("Welcome back", "SectionTitle")
        self._greeting.setStyleSheet("font-size: 24px; font-weight: 700;")
        self._date = muted("")
        header.addWidget(self._greeting)
        header.addWidget(self._date)
        self._content_layout.addLayout(header)

        # quick actions row
        self._quick = QHBoxLayout()
        self._quick.setSpacing(10)
        self._content_layout.addLayout(self._quick)

        # grids
        self._favorites_grid = QGridLayout()
        self._favorites_grid.setSpacing(12)
        self._recents_grid = QGridLayout()
        self._recents_grid.setSpacing(12)

        self._fav_card = Card("Favorite applications")
        self._fav_card.add_layout(self._favorites_grid)
        self._rec_card = Card("Recently opened")
        self._rec_card.add_layout(self._recents_grid)

        apps_row = QHBoxLayout()
        apps_row.setSpacing(16)
        apps_row.addWidget(self._fav_card, 1)
        apps_row.addWidget(self._rec_card, 1)
        self._content_layout.addLayout(apps_row)

        self._events_card = Card("Upcoming events")
        self._tasks_card = Card("Pending tasks")
        self._notes_card = Card("Recently accessed notes")
        info_row = QHBoxLayout()
        info_row.setSpacing(16)
        info_row.addWidget(self._events_card, 1)
        info_row.addWidget(self._tasks_card, 1)
        info_row.addWidget(self._notes_card, 1)
        self._content_layout.addLayout(info_row)

        self._content_layout.addStretch(1)

    # -- refresh --------------------------------------------------------
    def on_show(self) -> None:
        self.refresh()

    def refresh(self) -> None:
        ctx = self.context
        now = datetime.now()
        self._date.setText(now.strftime("%A, %d %B %Y"))
        hour = now.hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
        self._greeting.setText(greeting)

        self._fill_quick()
        self._fill_apps_grid(self._favorites_grid, ctx.registry.favorites(), "No favorites yet")
        self._fill_apps_grid(self._recents_grid, ctx.registry.recents(limit=8), "Nothing opened yet")
        self._fill_events()
        self._fill_tasks()
        self._fill_notes()

    def _fill_quick(self) -> None:
        while self._quick.count():
            item = self._quick.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        ctx = self.context
        from PySide6.QtCore import QSize as _QS
        from ui.icons import app_icon
        for app_id, label in (
            ("calendar", "New Event"),
            ("notes", "Open Notes"),
            ("tasks", "Open Tasks"),
            ("settings", "Settings"),
        ):
            btn = QPushButton(label)
            btn.setIcon(app_icon(app_id, size=18))
            btn.setIconSize(_QS(18, 18))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("PrimaryButton" if app_id == "calendar" else "")
            btn.clicked.connect(lambda _c=False, aid=app_id: ctx.navigate(aid))
            self._quick.addWidget(btn)
        self._quick.addStretch(1)

    def _fill_apps_grid(self, grid: QGridLayout, apps: list, empty_text: str) -> None:
        while grid.count():
            item = grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        if not apps:
            label = muted(empty_text)
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            grid.addWidget(label, 0, 0)
            return
        for i, app in enumerate(apps):
            tile = _app_tile(app, self.context.registry.is_favorite(app.id), self.context)
            grid.addWidget(tile, i // 2, i % 2)

    def _fill_events(self) -> None:
        card = self._events_card
        self._clear_card_body(card)
        rows = self.context.db.query(
            "SELECT title, start, location FROM calendar_events "
            "WHERE start >= datetime('now','localtime') ORDER BY start ASC LIMIT 5"
        )
        if not rows:
            card.add_widget(muted("No upcoming events."))
            return
        for r in rows:
            card.add_widget(self._row(f" {r['title']}", f"{r['start']}  {r.get('location','')}".strip()))

    def _fill_tasks(self) -> None:
        card = self._tasks_card
        self._clear_card_body(card)
        rows = self.context.db.query(
            "SELECT title, deadline, priority FROM tasks "
            "WHERE status != 'done' ORDER BY (deadline IS NULL), deadline ASC LIMIT 5"
        )
        if not rows:
            card.add_widget(muted("No pending tasks."))
            return
        for r in rows:
            sub = r.get("deadline") or "No deadline"
            card.add_widget(self._row(f" {r['title']}", sub))

    def _fill_notes(self) -> None:
        card = self._notes_card
        self._clear_card_body(card)
        rows = self.context.db.query(
            "SELECT title, last_accessed_at FROM notes ORDER BY last_accessed_at DESC LIMIT 5"
        )
        if not rows:
            card.add_widget(muted("No notes yet."))
            return
        for r in rows:
            card.add_widget(self._row(f" {r['title'] or 'Untitled'}", r["last_accessed_at"]))

    # -- helpers --------------------------------------------------------
    def _row(self, title: str, subtitle: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)
        lay.setSpacing(2)
        t = QLabel(title)
        t.setStyleSheet("font-weight: 500;")
        s = QLabel(subtitle)
        s.setObjectName("Tiny")
        s.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(s)
        return w

    def _clear_card_body(self, card: Card) -> None:
        body = card.body_layout()
        # keep title label (index 0) if present
        start = 1 if card.title_label is not None else 0
        while body.count() > start:
            item = body.takeAt(body.count() - 1)
            w = item.widget()
            if w is not None:
                w.deleteLater()
            elif item.layout() is not None:
                self._clear_layout(item.layout())

    def _clear_layout(self, layout) -> None:  # noqa: ANN001
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
