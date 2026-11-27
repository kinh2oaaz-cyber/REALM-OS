"""Gaming Hub service: library, launch, playtime tracking, stats."""

from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QProcess, Signal

from core.logging_setup import get_logger

if TYPE_CHECKING:
    from core.context import AppContext

from .database import GameRepository
from .detect import detect_installed_games
from .models import Game

_log = get_logger("gaming")


class PlaytimeTracker(QObject):
    """Launches a game process and records a session + total playtime."""

    finished = Signal(int, int)   # game_id, duration_seconds
    started = Signal(int)

    def __init__(self, repo: GameRepository, ctx: "AppContext") -> None:
        super().__init__()
        self.repo = repo
        self.ctx = ctx
        self._active: dict[int, tuple[QProcess, float, int]] = {}

    def launch(self, game_id: int) -> bool:
        game = self.repo.get(game_id)
        if game is None or not game.exe_path:
            return False
        exe = game.exe_path
        if not Path(exe).exists():
            _log.warning("Game executable not found: %s", exe)
            return False
        process = QProcess(self)
        working_dir = str(Path(exe).parent)
        process.setWorkingDirectory(working_dir)
        started_at = time.time()
        cur = self.ctx.db.execute(
            "INSERT INTO game_sessions (game_id, started_at) VALUES (?, datetime('now'))", (game_id,))
        session_id = int(cur.lastrowid)
        self._active[game_id] = (process, started_at, session_id)
        process.finished.connect(lambda _code, _status, gid=game_id: self._on_finished(gid))
        process.errorOccurred.connect(lambda _err, gid=game_id: self._on_finished(gid))
        process.start(exe, [])
        self.started.emit(game_id)
        return True

    def _on_finished(self, game_id: int) -> None:
        entry = self._active.pop(game_id, None)
        if entry is None:
            return
        _process, started_at, session_id = entry
        duration = max(0, int(time.time() - started_at))
        self.ctx.db.execute(
            "UPDATE game_sessions SET ended_at=datetime('now'), duration_seconds=? WHERE id=?", (duration, session_id))
        self.repo.add_playtime(game_id, duration, session_id)
        self.finished.emit(game_id, duration)
        self.ctx.event_bus.publish("game.session_ended", {"game_id": game_id, "duration_seconds": duration})

    def is_running(self, game_id: int) -> bool:
        return game_id in self._active


class GamingService:
    def __init__(self, ctx: "AppContext") -> None:
        self.ctx = ctx
        self.repo = GameRepository(ctx.db)
        self.tracker = PlaytimeTracker(self.repo, ctx)

    def add_game(self, name: str, exe_path: str = "", category: str = "",
                 cover_path: str = "", icon_path: str = "") -> int:
        game = Game(name=name, exe_path=exe_path, category=category, cover_path=cover_path, icon_path=icon_path)
        game_id = self.repo.create(game)
        self.ctx.event_bus.publish("game.added", {"game_id": game_id})
        return game_id

    def update_game(self, game: Game) -> None:
        self.repo.update(game)

    def remove_game(self, game_id: int) -> None:
        self.repo.delete(game_id)

    def set_favorite(self, game_id: int, favorite: bool) -> None:
        game = self.repo.get(game_id)
        if game:
            game.favorite = favorite; self.repo.update(game)

    def launch(self, game_id: int) -> bool:
        return self.tracker.launch(game_id)

    def detect_installed(self) -> list[dict]:
        return detect_installed_games()

    def import_detected(self, items: list[dict]) -> int:
        added = 0
        for item in items:
            name = item.get("name", "").strip()
            exe = item.get("exe_path", "")
            if not name:
                continue
            if exe and self.repo.find_by_exe(exe):
                continue
            if self.repo.find_by_exe(exe) is None:
                self.repo.create(Game(name=name, exe_path=exe, category=item.get("source", "")))
                added += 1
        return added

    def stats(self) -> dict:
        return self.repo.stats()
