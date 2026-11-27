"""Shared SQLite database layer for REALM OS.

``Database`` owns the single SQLite connection. ``schema`` defines the
migration list. ``repositories`` provides small data-access helpers.
Every feature module gets its own tables here so the whole application
shares one consistent local-first database.
"""

from __future__ import annotations

from .connection import Database
from .schema import MIGRATIONS, run_migrations

__all__ = ["Database", "MIGRATIONS", "run_migrations"]
