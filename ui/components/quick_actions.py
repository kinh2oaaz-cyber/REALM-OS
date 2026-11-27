"""Quick actions menu in the top bar."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtGui import QAction
from PySide6.QtWidgets import QMenu

if TYPE_CHECKING:
    from core.context import AppContext


def build_quick_actions_menu(context: "AppContext", parent) -> QMenu:  # noqa: ANN001
    menu = QMenu(parent)
    menu.setTitle("Quick Actions")

    def add(text: str, slot) -> QAction:  # noqa: ANN001
        action = QAction(text, menu)
        action.triggered.connect(lambda _checked=False: slot())
        menu.addAction(action)
        return action

    add("Go to Home", lambda: context.navigate("home"))
    add("Open Notes", lambda: context.navigate("notes"))
    add("Open Tasks", lambda: context.navigate("tasks"))
    add("Open Calendar", lambda: context.navigate("calendar"))
    menu.addSeparator()
    add("Toggle Dark / Light", context.theme.toggle_dark)
    add("Open Settings", lambda: context.navigate("settings"))
    menu.addSeparator()
    add("Open Data Folder", _open_data_folder)
    add("Open Logs Folder", _open_logs_folder)
    return menu


def _open_data_folder() -> None:
    from core.config import data_dir

    _open_path(data_dir())


def _open_logs_folder() -> None:
    from core.config import logs_dir

    _open_path(logs_dir())


def _open_path(path) -> None:  # noqa: ANN001
    try:
        import os

        path.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]  # noqa: S606
        else:
            import subprocess

            subprocess.run(["xdg-open", str(path)], check=False)  # noqa: S603
    except Exception:  # noqa: BLE001
        pass
