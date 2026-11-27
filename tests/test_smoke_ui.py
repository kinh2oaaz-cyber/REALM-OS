"""Offscreen UI smoke test: build the full shell, navigate every app."""

from __future__ import annotations

import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

# isolate data
_tmp = tempfile.mkdtemp(prefix="realmos_test_")
os.environ["REALMOS_DATA_DIR"] = _tmp


class TestSmokeUI(unittest.TestCase):
    def test_build_and_navigate_all(self) -> None:
        from app.application import RealmOSApplication

        application = RealmOSApplication(["realmos-test"])
        window = application.window
        self.assertEqual(window.windowTitle(), "REALM OS")

        ids = [a.id for a in application.registry.all()]
        self.assertIn("home", ids)

        for app_id in ids:
            window.navigate(app_id)  # must not raise
        window.navigate("home")

        # notifications pipeline through the shell
        application.notifications.add("Test", "message", app_id="home")
        self.assertGreaterEqual(application.notifications.unread_count(), 1)

        # theme toggle doesn't crash
        application.theme.toggle_dark()
        application.theme.toggle_dark()

        # global search routes to an app
        window._on_global_search("calendar")  # noqa: SLF001
        self.assertEqual(window.sidebar.current(), "calendar")

        application.shutdown()

    def test_persistence_across_restart(self) -> None:
        from app.application import RealmOSApplication

        app1 = RealmOSApplication(["realmos-test"])
        app1.settings.set("smoke", {"ok": True})
        app1.registry.set_favorite("notes", True)
        app1.shutdown()

        app2 = RealmOSApplication(["realmos-test"])
        self.assertEqual(app2.settings.get("smoke"), {"ok": True})
        self.assertTrue(app2.registry.is_favorite("notes"))
        app2.shutdown()


if __name__ == "__main__":
    unittest.main()
