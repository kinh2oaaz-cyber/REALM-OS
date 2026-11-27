"""App registry tests."""

from __future__ import annotations

import unittest

from core.app_registry import HOME_ID, AppInfo, AppRegistry

from ._base import DatabaseTestCase


class TestAppRegistry(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.reg = AppRegistry(self.db)
        self.reg.register(AppInfo(id="calendar", name="Calendar", icon="📅", order=10, keywords=("events",)))
        self.reg.register(AppInfo(id="notes", name="Notes", icon="📝", order=20))
        self.reg.register(AppInfo(id="settings", name="Settings", order=1000))

    def test_register_and_get(self) -> None:
        self.assertIn("calendar", self.reg)
        self.assertEqual(len(self.reg), 3)
        self.assertEqual(self.reg.get("notes").name, "Notes")
        self.assertIsNone(self.reg.get("nope"))

    def test_ordering(self) -> None:
        self.assertEqual([a.id for a in self.reg.all()], ["calendar", "notes", "settings"])

    def test_search(self) -> None:
        self.assertEqual([a.id for a in self.reg.search("cal")], ["calendar"])
        self.assertEqual([a.id for a in self.reg.search("events")], ["calendar"])
        self.assertEqual([a.id for a in self.reg.search("")], [a.id for a in self.reg.all()])
        self.assertEqual(self.reg.search("zzz"), [])

    def test_favorites_persist(self) -> None:
        self.assertFalse(self.reg.is_favorite("notes"))
        self.reg.set_favorite("notes", True)
        self.assertTrue(self.reg.is_favorite("notes"))
        self.assertTrue(self.reg.toggle_favorite("notes") is False)
        self.assertFalse(self.reg.is_favorite("notes"))
        self.reg.set_favorite("notes", True)
        reg2 = AppRegistry(self.db)
        reg2.register(AppInfo(id="notes", name="Notes"))
        self.assertTrue(reg2.is_favorite("notes"))  # persisted in SQLite

    def test_recents_persist(self) -> None:
        self.reg.record_open("calendar")
        self.reg.record_open("notes")
        self.reg.record_open("calendar")
        ids = [a.id for a in self.reg.recents()]
        self.assertEqual(ids[0], "calendar")  # most recent first
        reg2 = AppRegistry(self.db)
        reg2.register(AppInfo(id="calendar", name="Calendar"))
        reg2.register(AppInfo(id="notes", name="Notes"))
        self.assertIn("calendar", [a.id for a in reg2.recents()])

    def test_recents_filters_unknown(self) -> None:
        self.reg.record_open("calendar")
        self.reg.record_open("ghost")
        self.assertEqual([a.id for a in self.reg.recents()], ["calendar"])


class TestHomeConstant(unittest.TestCase):
    def test_home_id(self) -> None:
        self.assertEqual(HOME_ID, "home")


if __name__ == "__main__":
    unittest.main()
