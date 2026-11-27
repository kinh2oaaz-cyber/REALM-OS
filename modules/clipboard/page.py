"""Clipboard Manager: monitor clipboard, persistent history, copy back."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout,
)

from ui.components.page import RealmPage

_MAX_HISTORY = 200


class ClipboardPage(RealmPage):
    page_title = "Clipboard Manager"

    def __init__(self, context, parent=None) -> None:
        self._clipboard = QApplication.clipboard()
        super().__init__(context, parent)
        self._clipboard.dataChanged.connect(self._on_clipboard_change)
        self._last = None

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("Clipboard Manager"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        clear = QPushButton("Clear history"); clear.setObjectName("DangerButton"); clear.clicked.connect(self.clear_history); header.addWidget(clear); self.layout_root.addLayout(header)

        self.search = QLineEdit(); self.search.setObjectName("SearchBox"); self.search.setPlaceholderText("Search clipboard history…"); self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(lambda _t: self.refresh()); self.layout_root.addWidget(self.search)

        self.list = QListWidget(); self.list.itemDoubleClicked.connect(self._copy_item); self.layout_root.addWidget(self.list, 1)
        hint = QLabel("Double-click an entry to copy it back. Clipboard changes are captured automatically."); hint.setObjectName("Muted"); self.layout_root.addWidget(hint)
        self.refresh()

    def _on_clipboard_change(self) -> None:
        text = self._clipboard.text()
        if not text or text == self._last:
            return
        self._last = text
        self.context.db.execute("INSERT INTO clipboard_items (content) VALUES (?)", (text,))
        # trim history
        self.context.db.execute(
            "DELETE FROM clipboard_items WHERE id NOT IN (SELECT id FROM clipboard_items ORDER BY id DESC LIMIT ?)", (_MAX_HISTORY,))
        self.refresh()

    def refresh(self) -> None:
        query = self.search.text().strip() if hasattr(self, "search") else ""
        self.list.clear()
        if query:
            rows = self.context.db.query("SELECT * FROM clipboard_items WHERE content LIKE ? ORDER BY id DESC", (f"%{query}%",))
        else:
            rows = self.context.db.query("SELECT * FROM clipboard_items ORDER BY id DESC")
        for r in rows:
            preview = r["content"].replace("\n", " ").strip()[:120]
            item = QListWidgetItem(preview or "(empty)"); item.setData(Qt.ItemDataRole.UserRole, r["content"]); item.setToolTip(r["content"][:500])
            self.list.addItem(item)

    def _copy_item(self, item: QListWidgetItem) -> None:
        content = item.data(Qt.ItemDataRole.UserRole)
        self._clipboard.setText(content)

    def clear_history(self) -> None:
        if QMessageBox.question(self, "Clear history", "Clear all clipboard history?") != QMessageBox.StandardButton.Yes: return
        self.context.db.execute("DELETE FROM clipboard_items"); self.refresh()

    def on_show(self) -> None:
        self.refresh()
