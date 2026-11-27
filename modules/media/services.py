"""Media Center service: library scanning, metadata, history, playlists."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import AppContext

from .models import AUDIO_EXTENSIONS, VIDEO_EXTENSIONS, MediaTrack

MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


class MediaService:
    def __init__(self, ctx: "AppContext | None" = None) -> None:
        self.ctx = ctx

    # -- scanning -------------------------------------------------------
    def scan_folder(self, root: str, limit: int = 5000) -> list[MediaTrack]:
        tracks: list[MediaTrack] = []
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".")]
            for name in filenames:
                ext = Path(name).suffix.lower()
                if ext not in MEDIA_EXTENSIONS:
                    continue
                p = Path(dirpath) / name
                tracks.append(MediaTrack(path=str(p), title=p.stem, artist="", album=p.parent.name))
                if len(tracks) >= limit:
                    return tracks
        tracks.sort(key=lambda t: t.title.lower())
        return tracks

    def add_to_library(self, tracks: list[MediaTrack]) -> int:
        if self.ctx is None:
            return 0
        added = 0
        for t in tracks:
            self.ctx.db.execute(
                "INSERT OR IGNORE INTO media_tracks (path, title, artist, album, duration_seconds) VALUES (?, ?, ?, ?, ?)",
                (t.path, t.title, t.artist, t.album, t.duration_seconds))
            added += 1
        return added

    def library(self, query: str | None = None) -> list[MediaTrack]:
        if self.ctx is None:
            return []
        if query:
            like = f"%{query.strip()}%"
            rows = self.ctx.db.query(
                "SELECT * FROM media_tracks WHERE title LIKE ? OR artist LIKE ? OR album LIKE ? ORDER BY title", (like, like, like))
        else:
            rows = self.ctx.db.query("SELECT * FROM media_tracks ORDER BY title")
        return [MediaTrack.from_row(r) for r in rows]

    def albums(self) -> list[str]:
        if self.ctx is None: return []
        return [r["album"] for r in self.ctx.db.query("SELECT DISTINCT album FROM media_tracks WHERE album!='' ORDER BY album")]

    def artists(self) -> list[str]:
        if self.ctx is None: return []
        return [r["artist"] for r in self.ctx.db.query("SELECT DISTINCT artist FROM media_tracks WHERE artist!='' ORDER BY artist")]

    # -- history --------------------------------------------------------
    def record_played(self, track_id: int) -> None:
        if self.ctx is None: return
        self.ctx.db.execute("INSERT INTO media_history (track_id, played_at) VALUES (?, datetime('now'))", (track_id,))

    def recently_played(self, limit: int = 20) -> list[MediaTrack]:
        if self.ctx is None: return []
        rows = self.ctx.db.query(
            "SELECT t.* FROM media_tracks t JOIN media_history h ON h.track_id=t.id "
            "GROUP BY t.id ORDER BY MAX(h.played_at) DESC LIMIT ?", (limit,))
        return [MediaTrack.from_row(r) for r in rows]

    # -- playlists ------------------------------------------------------
    def create_playlist(self, name: str) -> int:
        if self.ctx is None: return -1
        cur = self.ctx.db.execute("INSERT INTO playlists (name) VALUES (?)", (name,))
        return int(cur.lastrowid)

    def list_playlists(self) -> list[dict]:
        if self.ctx is None: return []
        return self.ctx.db.query("SELECT * FROM playlists ORDER BY name")

    def add_to_playlist(self, playlist_id: int, track_id: int) -> None:
        if self.ctx is None: return
        pos = int(self.ctx.db.scalar("SELECT COALESCE(MAX(position),-1)+1 FROM playlist_items WHERE playlist_id=?", (playlist_id,)) or 0)
        self.ctx.db.execute("INSERT OR IGNORE INTO playlist_items (playlist_id, track_id, position) VALUES (?, ?, ?)",
                            (playlist_id, track_id, pos))

    def playlist_tracks(self, playlist_id: int) -> list[MediaTrack]:
        if self.ctx is None: return []
        rows = self.ctx.db.query(
            "SELECT t.* FROM media_tracks t JOIN playlist_items pi ON pi.track_id=t.id "
            "WHERE pi.playlist_id=? ORDER BY pi.position", (playlist_id,))
        return [MediaTrack.from_row(r) for r in rows]
