"""SQLite connection management.

A single shared connection (check_same_thread=False + RLock) so any
thread can use it safely. WAL mode for durability, foreign keys on,
and a small transaction helper. All SQL uses parameter binding.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

from core.logging_setup import get_logger

from .schema import run_migrations

_log = get_logger("database")


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self._conn: sqlite3.Connection | None = None
        self._lock = threading.RLock()

    # -- lifecycle ------------------------------------------------------
    def connect(self) -> sqlite3.Connection:
        if self._conn is not None:
            return self._conn
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            _log.warning("Could not create database directory %s", self.path.parent, exc_info=True)
        conn = sqlite3.connect(str(self.path), check_same_thread=False, timeout=30.0)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            conn.execute("PRAGMA journal_mode = WAL")
            conn.execute("PRAGMA synchronous = NORMAL")
        except sqlite3.DatabaseError:
            _log.warning("Could not enable WAL mode", exc_info=True)
        self._conn = conn
        return conn

    @property
    def conn(self) -> sqlite3.Connection:
        return self.connect()

    def initialize(self) -> None:
        """Create schema / apply pending migrations."""
        with self._lock:
            run_migrations(self)
            self.conn.commit()

    def close(self) -> None:
        with self._lock:
            if self._conn is not None:
                try:
                    self._conn.commit()
                finally:
                    self._conn.close()
                    self._conn = None

    # -- execution ------------------------------------------------------
    def execute(self, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.execute(sql, params)
            self.conn.commit()
            return cur

    def executemany(self, sql: str, seq: list[tuple[Any, ...]]) -> None:
        with self._lock:
            self.conn.executemany(sql, seq)
            self.conn.commit()

    def executescript(self, script: str) -> None:
        with self._lock:
            self.conn.executescript(script)
            self.conn.commit()

    def query(self, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> list[dict[str, Any]]:
        with self._lock:
            cur = self.conn.execute(sql, params)
            return [dict(row) for row in cur.fetchall()]

    def query_one(self, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> dict[str, Any] | None:
        with self._lock:
            cur = self.conn.execute(sql, params)
            row = cur.fetchone()
            return dict(row) if row else None

    def scalar(self, sql: str, params: tuple[Any, ...] | dict[str, Any] = ()) -> Any:
        row = self.query_one(sql, params)
        if not row:
            return None
        return next(iter(row.values()))

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Atomic block; rolls back on exception."""
        with self._lock:
            conn = self.conn
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise

    # -- maintenance ----------------------------------------------------
    def backup(self, destination: str | Path) -> None:
        """Online backup to a destination file."""
        dest = sqlite3.connect(str(destination))
        try:
            with self._lock:
                self.conn.backup(dest)
        finally:
            dest.close()

    def vacuum(self) -> None:
        with self._lock:
            self.conn.execute("VACUUM")
