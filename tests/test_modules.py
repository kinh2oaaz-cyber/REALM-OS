"""Module registration tests."""

from __future__ import annotations

import unittest

from core.app_registry import HOME_ID, AppRegistry

EXPECTED_APP_IDS = {
    HOME_ID,
    "calendar",
    "notes",
    "tasks",
    "file_manager",
    "gaming",
    "media",
    "network",
    "settings",
}

# Required sidebar apps from the brief.
SIDEBAR_REQUIRED = {"Home", "Calendar", "Notes", "Tasks", "File Manager", "Gaming", "Media", "Network", "Settings"}


class TestModuleRegistration(unittest.TestCase):
    def test_all_modules_register(self) -> None:
        from modules import register_all_modules

        registry = AppRegistry(db=None)
        register_all_modules(registry, ctx=None)  # type: ignore[arg-type]
        ids = {a.id for a in registry.all()}
        self.assertTrue(EXPECTED_APP_IDS.issubset(ids), EXPECTED_APP_IDS - ids)

    def test_sidebar_names_present(self) -> None:
        from modules import register_all_modules

        registry = AppRegistry(db=None)
        register_all_modules(registry, ctx=None)  # type: ignore[arg-type]
        names = {a.name for a in registry.all()}
        self.assertTrue(SIDEBAR_REQUIRED.issubset(names), SIDEBAR_REQUIRED - names)

    def test_every_app_has_page_factory_and_metadata(self) -> None:
        from modules import register_all_modules

        registry = AppRegistry(db=None)
        register_all_modules(registry, ctx=None)  # type: ignore[arg-type]
        for app in registry.all():
            self.assertTrue(app.name, app.id)
            self.assertTrue(app.icon, app.id)
            self.assertIsNotNone(app.page_factory, app.id)


if __name__ == "__main__":
    unittest.main()
