"""Settings service tests."""

from __future__ import annotations

import unittest

from core.settings import Settings

from ._base import DatabaseTestCase


class TestSettings(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.settings = Settings(self.db)

    def test_defaults(self) -> None:
        self.assertEqual(self.settings.get("appearance.theme"), "redgold")
        self.assertEqual(self.settings.get("appearance.accent"), "#C8AA6E")
        self.assertFalse(self.settings.get_bool("privacy.telemetry"))

    def test_set_get_roundtrip_types(self) -> None:
        self.settings.set("a.bool", True)
        self.settings.set("a.int", 7)
        self.settings.set("a.float", 1.5)
        self.settings.set("a.str", "hello")
        self.settings.set("a.list", [1, 2, 3])
        self.settings.set("a.dict", {"k": "v"})
        self.assertIs(self.settings.get("a.bool"), True)
        self.assertEqual(self.settings.get("a.int"), 7)
        self.assertEqual(self.settings.get("a.float"), 1.5)
        self.assertEqual(self.settings.get("a.str"), "hello")
        self.assertEqual(self.settings.get("a.list"), [1, 2, 3])
        self.assertEqual(self.settings.get("a.dict"), {"k": "v"})

    def test_overwrite_and_remove(self) -> None:
        self.settings.set("k", "1")
        self.settings.set("k", "2")
        self.assertEqual(self.settings.get("k"), "2")
        self.settings.remove("k")
        self.assertIsNone(self.settings.get("k"))

    def test_typed_helpers(self) -> None:
        self.settings.set("n", "42")
        self.assertEqual(self.settings.get_int("n"), 42)
        self.settings.set("b", "true")
        self.assertTrue(self.settings.get_bool("b"))
        self.assertEqual(self.settings.get_int("missing", 9), 9)

    def test_persistence(self) -> None:
        self.settings.set("persist", {"x": 1})
        s2 = Settings(self.db)
        self.assertEqual(s2.get("persist"), {"x": 1})

    def test_keys_and_reset(self) -> None:
        self.settings.set("z", 1)
        self.assertIn("z", self.settings.keys())
        self.settings.reset_all()
        self.assertNotIn("z", self.settings.keys())


if __name__ == "__main__":
    unittest.main()
