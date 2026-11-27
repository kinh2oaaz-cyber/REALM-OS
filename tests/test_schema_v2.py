"""Schema v2 migration tests."""

from __future__ import annotations

import unittest

from database.schema import CURRENT_SCHEMA_VERSION

from ._base import DatabaseTestCase

V2_TABLES = ["vault_entries", "finance_transactions", "projects", "clipboard_items", "downloads"]


class TestSchemaV2(DatabaseTestCase):
    def test_version_2(self) -> None:
        self.assertGreaterEqual(CURRENT_SCHEMA_VERSION, 2)
        versions = {r["version"] for r in self.db.query("SELECT version FROM schema_migrations")}
        self.assertIn(2, versions)

    def test_v2_tables(self) -> None:
        names = {r["name"] for r in self.db.query("SELECT name FROM sqlite_master WHERE type='table'")}
        for t in V2_TABLES:
            self.assertIn(t, names)

    def test_vault_roundtrip(self) -> None:
        self.db.execute("INSERT INTO vault_entries (title, username, password) VALUES ('x','u','enc')")
        self.assertEqual(self.db.scalar("SELECT password FROM vault_entries WHERE title='x'"), "enc")


if __name__ == "__main__":
    unittest.main()
