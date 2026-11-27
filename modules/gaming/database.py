"""Gaming Hub database access."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from database import Database

from .models import Game


class GameRepository:
    def __init__(self, db: "Database") -> None:
        self.db = db

    def list_all(self, order_by: str = "name COLLATE NOCASE") -> list[Game]:
        return [Game.from_row(r) for r in self.db.query(f"SELECT * FROM games ORDER BY {order_by}")]

    def get(self, game_id: int) -> Game | None:
        row = self.db.query_one("SELECT * FROM games WHERE id=?", (game_id,))
        return Game.from_row(row) if row else None

    def find_by_exe(self, exe_path: str) -> Game | None:
        row = self.db.query_one("SELECT * FROM games WHERE exe_path=?", (exe_path,))
        return Game.from_row(row) if row else None

    def create(self, game: Game) -> int:
        cur = self.db.execute(
            "INSERT INTO games (name, exe_path, cover_path, icon_path, category, favorite, total_playtime_seconds, last_played_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (game.name, game.exe_path, game.cover_path, game.icon_path, game.category,
             1 if game.favorite else 0, game.total_playtime_seconds, game.last_played_at))
        return int(cur.lastrowid)

    def update(self, game: Game) -> None:
        self.db.execute(
            "UPDATE games SET name=?, exe_path=?, cover_path=?, icon_path=?, category=?, favorite=?, "
            "total_playtime_seconds=?, last_played_at=? WHERE id=?",
            (game.name, game.exe_path, game.cover_path, game.icon_path, game.category,
             1 if game.favorite else 0, game.total_playtime_seconds, game.last_played_at, game.id))

    def delete(self, game_id: int) -> None:
        self.db.execute("DELETE FROM games WHERE id=?", (game_id,))

    def categories(self) -> list[str]:
        return [r["category"] for r in self.db.query("SELECT DISTINCT category FROM games WHERE category!='' ORDER BY category")]

    def recently_played(self, limit: int = 10) -> list[Game]:
        return [Game.from_row(r) for r in self.db.query(
            "SELECT * FROM games WHERE last_played_at IS NOT NULL ORDER BY last_played_at DESC LIMIT ?", (limit,))]

    def favorites(self) -> list[Game]:
        return [Game.from_row(r) for r in self.db.query("SELECT * FROM games WHERE favorite=1 ORDER BY name COLLATE NOCASE")]

    def add_playtime(self, game_id: int, seconds: int, session_id: int | None = None) -> None:
        self.db.execute("UPDATE games SET total_playtime_seconds = total_playtime_seconds + ?, last_played_at=datetime('now') WHERE id=?",
                        (max(0, seconds), game_id))

    def total_playtime(self) -> int:
        return int(self.db.scalar("SELECT COALESCE(SUM(total_playtime_seconds),0) FROM games") or 0)

    def stats(self) -> dict:
        return {
            "games": int(self.db.scalar("SELECT COUNT(*) FROM games") or 0),
            "favorites": int(self.db.scalar("SELECT COUNT(*) FROM games WHERE favorite=1") or 0),
            "total_playtime_seconds": self.total_playtime(),
            "sessions": int(self.db.scalar("SELECT COUNT(*) FROM game_sessions") or 0),
            "categories": int(self.db.scalar("SELECT COUNT(DISTINCT category) FROM games WHERE category!=''") or 0),
        }
