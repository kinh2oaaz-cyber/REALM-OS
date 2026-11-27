"""Global search box for the top bar."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLineEdit


class SearchBox(QLineEdit):
    """Emits :attr:`search_requested` on Enter (and live via textChanged)."""

    search_requested = Signal(str)

    def __init__(self, placeholder: str = "Search REALM OS", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("SearchBox")
        self.setPlaceholderText(placeholder)
        self.setClearButtonEnabled(True)
        self.setMinimumWidth(260)
        self.returnPressed.connect(lambda: self.search_requested.emit(self.text().strip()))

    def keyPressEvent(self, event) -> None:  # noqa: N802 (Qt naming)
        if event.key() == Qt.Key.Key_Escape:
            self.clear()
        super().keyPressEvent(event)
