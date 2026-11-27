"""Media Center registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import MediaPage

APP_ID = "media"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(
        AppInfo(
            id=APP_ID,
            name="Media",
            description="Local music & video player, library, playlists",
            icon="music",
            category="apps",
            order=60,
            keywords=("media", "music", "video", "audio", "playlist", "player", "album", "artist"),
            page_factory=lambda c: MediaPage(c),
        )
    )
