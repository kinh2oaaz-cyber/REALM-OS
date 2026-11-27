"""A tiny synchronous event bus for cross-module communication.

Modules publish named events with an optional payload; subscribers
receive it. Handlers that raise are logged and never break the
publisher. This is the backbone of the shared-system requirement
(e.g. a task created from a calendar event publishes ``task.created``
so other apps can react).

Event names used in Phase 1:
    navigation.requested      {"app_id": str}
    app.opened                {"app_id": str}
    app.favorite_changed      {"app_id": str, "favorite": bool}
    theme.changed             {"theme": str}
    notification.added        Notification payload dict
    notification.read         {"id": int}
    global.search             {"query": str}
"""

from __future__ import annotations

import threading
from collections import defaultdict
from typing import Callable

from .logging_setup import get_logger

Handler = Callable[[object], None]

_log = get_logger("event_bus")


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, list[Handler]] = defaultdict(list)
        self._lock = threading.RLock()

    def subscribe(self, event: str, handler: Handler) -> Callable[[], None]:
        """Register ``handler`` for ``event``. Returns an unsubscribe callable."""
        with self._lock:
            self._subs[event].append(handler)

        def unsubscribe() -> None:
            with self._lock:
                if handler in self._subs.get(event, []):
                    self._subs[event].remove(handler)

        return unsubscribe

    def publish(self, event: str, payload: object = None) -> None:
        with self._lock:
            handlers = list(self._subs.get(event, ()))
        for handler in handlers:
            try:
                handler(payload)
            except Exception:  # noqa: BLE001 - a bad subscriber must not break others
                _log.exception("Subscriber for event %r failed", event)

    def clear(self) -> None:
        with self._lock:
            self._subs.clear()
