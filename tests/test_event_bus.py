"""Event bus tests."""

from __future__ import annotations

import unittest

from core.event_bus import EventBus


class TestEventBus(unittest.TestCase):
    def test_publish_subscribe(self) -> None:
        bus = EventBus()
        received = []
        bus.subscribe("x", received.append)
        bus.publish("x", {"a": 1})
        self.assertEqual(received, [{"a": 1}])

    def test_unsubscribe(self) -> None:
        bus = EventBus()
        received = []
        unsub = bus.subscribe("x", received.append)
        unsub()
        bus.publish("x", 1)
        self.assertEqual(received, [])

    def test_multiple_subscribers(self) -> None:
        bus = EventBus()
        a, b = [], []
        bus.subscribe("x", a.append)
        bus.subscribe("x", b.append)
        bus.publish("x", 5)
        self.assertEqual(a, [5])
        self.assertEqual(b, [5])

    def test_bad_subscriber_does_not_break_others(self) -> None:
        bus = EventBus()
        good = []

        def boom(_p):
            raise RuntimeError("nope")

        bus.subscribe("x", boom)
        bus.subscribe("x", good.append)
        bus.publish("x", 1)  # must not raise
        self.assertEqual(good, [1])

    def test_no_subscribers_ok(self) -> None:
        EventBus().publish("nothing", None)


if __name__ == "__main__":
    unittest.main()
