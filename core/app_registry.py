"""Central application registry.

Every feature module registers an :class:`AppInfo`. The registry powers
the launcher sidebar, global search, favorites and "recently opened"
tracking (persisted in SQLite so it survives restarts).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

    from database import Database

    from .context import AppContext

# A page factory builds the top-level widget for an app.
PageFactory = Callable[["AppContext"], "QWidget"]

HOME_ID = "home"


@dataclass(frozen=True)
class AppInfo:
    id: str
    name: str
    description: str = ""
    icon: str = "app"
    category: str = "apps"
    order: int = 100
    keywords: tuple[str, ...] = field(default_factory=tuple)
    page_factory: Optional[PageFactory] = None


class AppRegistry:
    def __init__(self, db: "Database | None" = None) -> None:
        self._apps: dict[str, AppInfo] = {}
        self._db = db

    # -- registration ---------------------------------------------------
    def register(self, info: AppInfo) -> AppInfo:
        self._apps[info.id] = info
        return info

    def unregister(self, app_id: str) -> None:
        self._apps.pop(app_id, None)

    def get(self, app_id: str) -> AppInfo | None:
        return self._apps.get(app_id)

    def all(self) -> list[AppInfo]:
        return sorted(self._apps.values(), key=lambda a: (a.order, a.name.lower()))

    def __contains__(self, app_id: str) -> bool:
        return app_id in self._apps

    def __len__(self) -> int:
        return len(self._apps)

    # -- search ---------------------------------------------------------
    def search(self, query: str) -> list[AppInfo]:
        q = query.strip().lower()
        if not q:
            return self.all()
        scored: list[tuple[int, AppInfo]] = []
        for app in self._apps.values():
            haystack = " ".join(
                [app.name.lower(), app.description.lower(), " ".join(app.keywords).lower(), app.id]
            )
            if q in app.name.lower():
                scored.append((0, app))
            elif q in app.id.lower():
                scored.append((1, app))
            elif any(q in k.lower() for k in app.keywords):
                scored.append((2, app))
            elif q in haystack:
                scored.append((3, app))
        scored.sort(key=lambda t: (t[0], t[1].order, t[1].name.lower()))
        return [app for _, app in scored]

    # -- favorites ------------------------------------------------------
    def is_favorite(self, app_id: str) -> bool:
        if self._db is None:
            return False
        row = self._db.query_one("SELECT 1 FROM app_favorites WHERE app_id = ?", (app_id,))
        return row is not None

    def set_favorite(self, app_id: str, favorite: bool) -> None:
        if self._db is None:
            return
        if favorite:
            self._db.execute(
                "INSERT OR IGNORE INTO app_favorites (app_id, added_at) VALUES (?, datetime('now'))",
                (app_id,),
            )
        else:
            self._db.execute("DELETE FROM app_favorites WHERE app_id = ?", (app_id,))

    def toggle_favorite(self, app_id: str) -> bool:
        new_state = not self.is_favorite(app_id)
        self.set_favorite(app_id, new_state)
        return new_state

    def favorites(self) -> list[AppInfo]:
        return [a for a in self.all() if self.is_favorite(a.id)]

    # -- recents --------------------------------------------------------
    def record_open(self, app_id: str) -> None:
        if self._db is None:
            return
        self._db.execute(
            """
            INSERT INTO app_recents (app_id, opened_at)
            VALUES (?, datetime('now'))
            ON CONFLICT(app_id) DO UPDATE SET opened_at = excluded.opened_at
            """,
            (app_id,),
        )

    def recents(self, limit: int = 8) -> list[AppInfo]:
        if self._db is None:
            return []
        rows = self._db.query(
            "SELECT app_id FROM app_recents ORDER BY opened_at DESC LIMIT ?", (limit,)
        )
        out: list[AppInfo] = []
        for row in rows:
            app = self._apps.get(row["app_id"])
            if app is not None:
                out.append(app)
        return out

    def clear_recents(self) -> None:
        if self._db is not None:
            self._db.execute("DELETE FROM app_recents")
