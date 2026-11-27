"""REALM OS entry point.

Run with ``python -m app.main`` or ``python main.py`` from project root.
Graceful top-level error handling; logs to the per-user logs directory.
"""

from __future__ import annotations

import sys
import traceback

from core.logging_setup import get_logger


def main(argv: list[str] | None = None) -> int:
    log = get_logger("main")
    try:
        from app.application import RealmOSApplication

        application = RealmOSApplication(argv)
        return application.run()
    except Exception:  # noqa: BLE001 - never die silently
        log.exception("Fatal startup error")
        traceback.print_exc()
        try:
            from PySide6.QtWidgets import QApplication, QMessageBox

            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "REALM OS", "REALM OS could not start.\n\nSee logs for details.")
        except Exception:  # noqa: BLE001
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
