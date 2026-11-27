"""Notification service tests."""

from __future__ import annotations

import unittest

from core.event_bus import EventBus
from core.notifications import NotificationService

from ._base import DatabaseTestCase


class TestNotifications(DatabaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.bus = EventBus()
        self.svc = NotificationService(self.db, self.bus)

    def test_add_and_list(self) -> None:
        n = self.svc.add("Title", "Body", app_id="calendar", level="success")
        self.assertEqual(n.title, "Title")
        self.assertEqual(n.level, "success")
        self.assertFalse(n.read)
        self.assertEqual(self.svc.unread_count(), 1)
        self.assertEqual(len(self.svc.list()), 1)

    def test_invalid_level_falls_back(self) -> None:
        n = self.svc.add("x", level="weird")
        self.assertEqual(n.level, "info")

    def test_mark_read(self) -> None:
        n = self.svc.add("x")
        self.svc.mark_read(n.id)
        self.assertEqual(self.svc.unread_count(), 0)
        self.assertTrue(self.svc.get(n.id).read)

    def test_mark_all_read(self) -> None:
        self.svc.add("a")
        self.svc.add("b")
        self.svc.mark_all_read()
        self.assertEqual(self.svc.unread_count(), 0)

    def test_clear(self) -> None:
        self.svc.add("a")
        self.svc.clear()
        self.assertEqual(self.svc.list(), [])

    def test_event_emitted(self) -> None:
        events = []
        self.bus.subscribe("notification.added", events.append)
        self.svc.add("hi")
        self.assertEqual(len(events), 1)

    def test_persistence(self) -> None:
        self.svc.add("persist")
        svc2 = NotificationService(self.db, self.bus)
        self.assertEqual(len(svc2.list()), 1)


if __name__ == "__main__":
    unittest.main()
