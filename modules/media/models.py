"""Media model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a", ".wma", ".opus"}
VIDEO_EXTENSIONS = {".mp4", ".mkv", ".avi", ".mov", ".wmv", ".webm", ".m4v", ".mpg", ".mpeg", ".flv"}


@dataclass
class MediaTrack:
    id: int | None = None
    path: str = ""
    title: str = ""
    artist: str = ""
    album: str = ""
    duration_seconds: float = 0.0
    added_at: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "MediaTrack":
        return cls(
            id=row.get("id"), path=row.get("path", ""), title=row.get("title", ""),
            artist=row.get("artist", ""), album=row.get("album", ""),
            duration_seconds=float(row.get("duration_seconds", 0)), added_at=row.get("added_at"),
        )

    @property
    def is_video(self) -> bool:
        from pathlib import Path
        return Path(self.path).suffix.lower() in VIDEO_EXTENSIONS
