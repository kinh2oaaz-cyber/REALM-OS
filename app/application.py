"""Top-level application object wiring core services + UI shell."""

from __future__ import annotations

import os
import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMessageBox

from core.app_registry import AppRegistry
from core.config import APP_NAME, APP_VERSION, ORG_NAME, ensure_dirs
from core.context import AppContext
from core.event_bus import EventBus
from core.logging_setup import get_logger, setup_logging
from core.notifications import NotificationService
from core.settings import Settings
from database import Database
from database.connection import Database as _Database  # noqa: F401
from modules import register_all_modules
from ui.main_window import MainWindow
from ui.themes import ThemeManager

from core import config as _config

_log = get_logger("application")


class RealmOSApplication:
    """Owns the QApplication, database and shared services."""

    def __init__(self, argv: list[str] | None = None) -> None:
        argv = argv if argv is not None else sys.argv

        # filesystem + logging first so everything else can log
        ensure_dirs()
        self.logger = setup_logging(_config.logs_dir())

        # Performance-safe Qt Quick (integrated graphics); no extra deps.
        os.environ.setdefault("QT_QUICK_BACKEND", "software")
        os.environ.setdefault("QSG_RENDER_LOOP", "basic")
        self.app = QApplication.instance() or QApplication(argv)
        try:
            self.app.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts, True)
        except Exception:  # noqa: BLE001
            pass
        self.app.setApplicationName(APP_NAME)
        self.app.setApplicationVersion(APP_VERSION)
        self.app.setOrganizationName(ORG_NAME)
        self.app.setApplicationDisplayName(APP_NAME)
        try:
            from ui.icons import realm_logo
            self.app.setWindowIcon(realm_logo(256))
        except Exception:  # noqa: BLE001
            pass

        # database
        self.db = Database(_config.database_path())
        try:
            self.db.initialize()
        except Exception as exc:  # noqa: BLE001
            _log.exception("Database initialization failed")
            QMessageBox.critical(None, "REALM OS", f"Could not initialize database:\n{exc}")
            raise

        # shared services
        self.event_bus = EventBus()
        self.settings = Settings(self.db)
        self.notifications = NotificationService(self.db, self.event_bus)
        self.theme = ThemeManager(self.settings, self.app)
        self.registry = AppRegistry(self.db)

        self.context = AppContext(
            app=self.app,
            db=self.db,
            settings=self.settings,
            event_bus=self.event_bus,
            notifications=self.notifications,
            theme=self.theme,
            registry=self.registry,
        )

        # register modules, then apply theme, then build window
        register_all_modules(self.registry, self.context)
        self.theme.apply_saved()

        self.window = MainWindow(self.context)
        self.app.aboutToQuit.connect(self.shutdown)

    def run(self) -> int:
        self.window.show()
        return self.app.exec()

    def shutdown(self) -> None:
        try:
            self.db.close()
        except Exception:  # noqa: BLE001
            _log.exception("Error closing database")
