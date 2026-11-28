"""Home — cinematic, asymmetric personal launcher + dashboard.

Composition (deliberately varied, not a grid of identical cards):
  1. Greeting header with quick actions.
  2. Featured hero panel (dominant) + stacked metric tiles.
  3. Pinned applications + recently opened.
  4. Contextual panels: events, tasks, notes, games (varied widths).
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.cards import (
    AppTile,
    Card,
    HeroCard,
    StatTile,
    eyebrow,
    heading,
    hero_title,
    muted,
    tiny,
)
from ui.components.page import RealmPage
from ui.icons import app_icon

if TYPE_CHECKING:
    from core.app_registry import AppInfo
    from core.context import AppContext


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
        self._content = QVBoxLayout(content)
        self._content.setContentsMargins(0, 0, 0, 0)
        self._content.setSpacing(22)
        scroll.setWidget(content)
        self.layout_root.addWidget(scroll)

        self._content.addLayout(self._build_header())
        self._content.addLayout(self._build_hero())
        self._content.addLayout(self._build_apps())
        self._content.addLayout(self._build_info())
        self._content.addStretch(1)

    def _build_header(self) -> QVBoxLayout:
        # Stacked header: greeting block, then quick actions on their own row.
        # This keeps the page's minimum width small enough for 960×640 without
        # a horizontal scrollbar or clipped buttons.
        block = QVBoxLayout()
        block.setSpacing(12)
        left = QVBoxLayout()
        left.setSpacing(4)
        self._eyebrow = eyebrow("")
        self._greeting = hero_title("Welcome back")
        self._greeting.setStyleSheet("font-size: 28px; font-weight: 800;")
        self._date = muted("")
        left.addWidget(self._eyebrow)
        left.addWidget(self._greeting)
        left.addWidget(self._date)
        block.addLayout(left)

        self._quick = QHBoxLayout()
        self._quick.setSpacing(10)
        block.addLayout(self._quick)
        return block

    def _build_hero(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)

        self._hero = HeroCard()
        hl = self._hero.body_layout()
        hl.addWidget(eyebrow("Featured"))
        self._hero_title = hero_title("Your day, in one place")
        hl.addWidget(self._hero_title)
        self._hero_sub = muted("")
        self._hero_sub.setStyleSheet("font-size: 13px;")
        hl.addWidget(self._hero_sub)
        hl.addSpacing(6)
        self._hero_actions = QHBoxLayout()
        self._hero_actions.setSpacing(10)
        hl.addLayout(self._hero_actions)
        hl.addStretch(1)
        row.addWidget(self._hero, 2)

        stats = QVBoxLayout()
        stats.setSpacing(12)
        self._stat_events = StatTile("0", "Events today")
        self._stat_tasks = StatTile("0", "Open tasks")
        self._stat_notes = StatTile("0", "Notes")
        stats.addWidget(self._stat_events)
        stats.addWidget(self._stat_tasks)
        stats.addWidget(self._stat_notes)
        row.addLayout(stats, 1)
        return row

    def _build_apps(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)

        self._fav_card = Card("Pinned applications")
        self._fav_grid = QGridLayout()
        self._fav_grid.setSpacing(10)
        self._fav_card.add_layout(self._fav_grid)
        row.addWidget(self._fav_card, 3)

        self._rec_card = Card("Recently opened")
        self._rec_body = QVBoxLayout()
        self._rec_body.setSpacing(8)
        self._rec_card.add_layout(self._rec_body)
        row.addWidget(self._rec_card, 2)
        return row

    def _build_info(self) -> QHBoxLayout:
        row = QHBoxLayout()
        row.setSpacing(18)
        self._events_card = Card("Upcoming events")
        self._tasks_card = Card("Pending tasks")
        self._notes_card = Card("Recent notes")
        self._games_card = Card("Recently played")
        row.addWidget(self._events_card, 16)
        row.addWidget(self._tasks_card, 12)
        row.addWidget(self._notes_card, 11)
        row.addWidget(self._games_card, 13)
        return row

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
        self._eyebrow.setText(now.strftime("%A · %d %B").upper())

        self._fill_hero()
        self._fill_quick()
        self._fill_stats()
        self._fill_favorites()
        self._fill_recents()
        self._fill_events()
        self._fill_tasks()
        self._fill_notes()
        self._fill_games()

    def _fill_hero(self) -> None:
        ctx = self.context
        recents = ctx.registry.recents(limit=1)
        recent = recents[0] if recents else None
        if recent is not None:
            self._hero_title.setText(recent.name)
            self._hero_sub.setText(
                f"Continue where you left off — {recent.description or 'recently opened'}."
            )
        else:
            self._hero_title.setText("Your day, in one place")
            self._hero_sub.setText(
                "Launch your applications, track tasks and events, and pick up your notes."
            )
        # rebuild action buttons
        while self._hero_actions.count():
            item = self._hero_actions.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        primary = QPushButton("Continue" if recent else "Open Home")
        primary.setObjectName("PrimaryButton")
        primary.setCursor(Qt.CursorShape.PointingHandCursor)
        target = recent.id if recent else "home"
        primary.clicked.connect(lambda _c=False, aid=target: ctx.navigate(aid))
        if recent is not None:
            primary.setIcon(app_icon(recent.id, color="#FFF6F7", size=16))
            primary.setIconSize(QSize(16, 16))
        self._hero_actions.addWidget(primary)

        secondary = QPushButton("Open calendar")
        secondary.setObjectName("GhostButton")
        secondary.setCursor(Qt.CursorShape.PointingHandCursor)
        secondary.clicked.connect(lambda _c=False: ctx.navigate("calendar"))
        self._hero_actions.addWidget(secondary)
        self._hero_actions.addStretch(1)

    def _fill_quick(self) -> None:
        while self._quick.count():
            item = self._quick.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        ctx = self.context
        for app_id, label in (
            ("calendar", "New event"),
            ("notes", "Notes"),
            ("tasks", "Tasks"),
            ("settings", "Settings"),
        ):
            btn = QPushButton(label)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("PrimaryButton" if app_id == "calendar" else "")
            btn.setIcon(app_icon(app_id, color="#FFF6F7" if app_id == "calendar" else "#B9AEB9", size=16))
            btn.setIconSize(QSize(16, 16))
            btn.clicked.connect(lambda _c=False, aid=app_id: ctx.navigate(aid))
            self._quick.addWidget(btn)

    def _fill_stats(self) -> None:
        db = self.context.db
        def _count(sql: str, params=()) -> int:
            try:
                rows = db.query(sql, params)
                if not rows:
                    return 0
                return int(list(rows[0].values())[0] or 0)
            except Exception:  # noqa: BLE001
                return 0
        today = datetime.now().strftime("%Y-%m-%d")
        events = _count("SELECT COUNT(*) c FROM calendar_events WHERE date(start) = ?", (today,))
        tasks = _count("SELECT COUNT(*) c FROM tasks WHERE status != 'done'")
        notes = _count("SELECT COUNT(*) c FROM notes")
        self._stat_events.set_value(str(events))
        self._stat_tasks.set_value(str(tasks))
        self._stat_notes.set_value(str(notes))

    def _fill_favorites(self) -> None:
        while self._fav_grid.count():
            item = self._fav_grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        ctx = self.context
        apps = ctx.registry.favorites()
        if not apps:
            apps = [a for a in ctx.registry.all() if a.id not in ("home", "settings")][:6]
        if not apps:
            label = muted("No applications available.")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._fav_grid.addWidget(label, 0, 0)
            return
        for i, app in enumerate(apps[:6]):
            tile = AppTile(app_icon(app.id, color="#D6AD55", size=22), app.name, app.description,
                           lambda aid=app.id: ctx.navigate(aid))
            self._fav_grid.addWidget(tile, i // 2, i % 2)

    def _fill_recents(self) -> None:
        while self._rec_body.count():
            item = self._rec_body.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        ctx = self.context
        recents = ctx.registry.recents(limit=6)
        if not recents:
            self._rec_body.addWidget(muted("Nothing opened yet."))
            self._rec_body.addStretch(1)
            return
        for app in recents:
            row = QWidget()
            lay = QHBoxLayout(row)
            lay.setContentsMargins(2, 4, 2, 4)
            lay.setSpacing(10)
            badge = QLabel()
            badge.setFixedSize(26, 26)
            badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            badge.setPixmap(app_icon(app.id, color="#B9AEB9", size=16).pixmap(16, 16))
            badge.setStyleSheet(
                "background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.06);"
                "border-radius: 7px;"
            )
            lay.addWidget(badge)
            name = QLabel(app.name)
            name.setStyleSheet("font-weight: 500; background: transparent;")
            lay.addWidget(name, 1)
            btn = QPushButton("Open")
            btn.setObjectName("GhostButton")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _c=False, aid=app.id: ctx.navigate(aid))
            lay.addWidget(btn)
            self._rec_body.addWidget(row)
        self._rec_body.addStretch(1)

    # -- contextual panels ---------------------------------------------
    def _fill_events(self) -> None:
        card = self._events_card
        self._clear_body(card)
        rows = self.context.db.query(
            "SELECT title, start, location FROM calendar_events "
            "WHERE start >= datetime('now','localtime') ORDER BY start ASC LIMIT 4"
        )
        if not rows:
            card.add_widget(muted("No upcoming events."))
            return
        for r in rows:
            card.add_widget(self._row(r["title"], f"{r['start']}  {r.get('location','')}".strip()))

    def _fill_tasks(self) -> None:
        card = self._tasks_card
        self._clear_body(card)
        rows = self.context.db.query(
            "SELECT title, deadline, priority FROM tasks "
            "WHERE status != 'done' ORDER BY (deadline IS NULL), deadline ASC LIMIT 4"
        )
        if not rows:
            card.add_widget(muted("No pending tasks."))
            return
        for r in rows:
            sub = r.get("deadline") or "No deadline"
            card.add_widget(self._row(r["title"], sub))

    def _fill_notes(self) -> None:
        card = self._notes_card
        self._clear_body(card)
        rows = self.context.db.query(
            "SELECT title, last_accessed_at FROM notes ORDER BY last_accessed_at DESC LIMIT 4"
        )
        if not rows:
            card.add_widget(muted("No notes yet."))
            return
        for r in rows:
            card.add_widget(self._row(r["title"] or "Untitled", r["last_accessed_at"]))

    def _fill_games(self) -> None:
        card = self._games_card
        self._clear_body(card)
        rows = self.context.db.query(
            "SELECT name, last_played_at, total_playtime_seconds FROM games "
            "WHERE last_played_at IS NOT NULL ORDER BY last_played_at DESC LIMIT 4"
        )
        if not rows:
            card.add_widget(muted("No recently played games."))
            return
        for r in rows:
            mins = (r["total_playtime_seconds"] or 0) // 60
            card.add_widget(self._row(r["name"], f"{r['last_played_at']}  {mins}m"))

    # -- helpers --------------------------------------------------------
    def _row(self, title: str, subtitle: str) -> QWidget:
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(2, 4, 2, 4)
        lay.setSpacing(1)
        t = QLabel(title)
        t.setStyleSheet("font-weight: 500; background: transparent;")
        t.setWordWrap(True)
        s = tiny(subtitle)
        lay.addWidget(t)
        lay.addWidget(s)
        return w

    def _clear_body(self, card: Card) -> None:
        body = card.body_layout()
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
            elif item.layout() is not None:
                self._clear_layout(item.layout())
