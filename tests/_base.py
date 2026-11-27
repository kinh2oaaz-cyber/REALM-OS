"""Shared test helpers."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from database import Database


class DatabaseTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self._tmp.name) / "test.db"
        self.db = Database(self.db_path)
        self.db.initialize()

    def tearDown(self) -> None:
        self.db.close()
        self._tmp.cleanup()
