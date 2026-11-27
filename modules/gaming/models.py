"""Game model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Game:
    id: int | None = None
    name: str = ""
    exe_path: str = ""
    cover_path: str = ""
    icon_path: str = ""
    category: str = ""
    favorite: bool = False
    total_playtime_seconds: int = 0
    last_played_at: str | None = None
    added_at: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Game":
        return cls(
            id=row.get("id"), name=row.get("name", ""), exe_path=row.get("exe_path", ""),
            cover_path=row.get("cover_path", ""), icon_path=row.get("icon_path", ""),
            category=row.get("category", ""), favorite=bool(row.get("favorite", 0)),
            total_playtime_seconds=int(row.get("total_playtime_seconds", 0)),
            last_played_at=row.get("last_played_at"), added_at=row.get("added_at"),
        )

    @property
    def playtime_hours(self) -> float:
        return round(self.total_playtime_seconds / 3600, 1)
