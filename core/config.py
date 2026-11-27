"""Application configuration and filesystem locations.

REALM OS is local-first. All user data lives under a per-user data
directory. On Windows this is ``%LOCALAPPDATA%\\REALM OS``; elsewhere a
platform-appropriate home directory is used. Set ``REALMOS_DATA_DIR``
to override (useful for portable installs and tests).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "REALM OS"
APP_ID = "realmos"
ORG_NAME = "REALM"
APP_VERSION = "1.0.0"
APP_CODENAME = "All phases"

DB_FILENAME = "realmos.db"


def is_windows() -> bool:
    """Return True when running on Windows 10/11."""
    return os.name == "nt" or sys.platform.startswith("win")


def project_root() -> Path:
    """Absolute path to the repository root (parent of ``core``)."""
    return Path(__file__).resolve().parent.parent


def assets_dir() -> Path:
    """Directory containing static assets shipped with the app."""
    return project_root() / "assets"


def data_dir() -> Path:
    """Per-user writable directory for the database, logs and caches."""
    override = os.environ.get("REALMOS_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if is_windows():
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_NAME
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "realmos"
    return Path.home() / ".local" / "share" / "realmos"


def database_dir() -> Path:
    return data_dir() / "database"


def database_path() -> Path:
    return database_dir() / DB_FILENAME


def logs_dir() -> Path:
    return data_dir() / "logs"


def cache_dir() -> Path:
    return data_dir() / "cache"


def project_logs_dir() -> Path:
    """In-repo logs directory (created for documentation/consistency)."""
    return project_root() / "logs"


def ensure_dirs() -> None:
    """Create every required directory. Idempotent."""
    for path in (
        data_dir(),
        database_dir(),
        logs_dir(),
        cache_dir(),
        project_logs_dir(),
        project_root() / "assets",
    ):
        try:
            path.mkdir(parents=True, exist_ok=True)
        except OSError:
            # Never let directory creation crash startup; logging is set
            # up afterwards and will surface problems.
            pass
