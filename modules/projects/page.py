"""Project Manager: projects with status + links to tasks/notes (shared system)."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QComboBox, QFrame, QHBoxLayout, QInputDialog, QLabel, QListWidget, QMessageBox, QPushButton, QVBoxLayout

from ui.components.page import RealmPage

_STATUSES = ["active", "paused", "done"]


class ProjectsPage(RealmPage):
    page_title = "Project Manager"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("Project Manager"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        add = QPushButton("New Project"); add.setObjectName("PrimaryButton"); add.clicked.connect(self.add_project); header.addWidget(add); self.layout_root.addLayout(header)
        self.list = QListWidget(); self.list.itemClicked.connect(lambda _i: self._render_detail()); self.layout_root.addWidget(self.list, 1)
        self.detail = QLabel(""); self.detail.setObjectName("Muted"); self.detail.setWordWrap(True); self.layout_root.addWidget(self.detail)
        self.refresh()

    def add_project(self) -> None:
        name, ok = QInputDialog.getText(self, "New project", "Project name:")
        if not ok or not name.strip(): return
        self.context.db.execute("INSERT INTO projects (name) VALUES (?)", (name.strip(),)); self.refresh()

    def refresh(self) -> None:
        self.list.clear()
        for p in self.context.db.query("SELECT * FROM projects ORDER BY status, name"):
            self.list.addItem(f"[{p['status']}] {p['name']}")
        # store ids
        for i in range(self.list.count()):
            pass
        self._render_detail()

    def _selected_project(self):
        idx = self.list.currentRow()
        rows = self.context.db.query("SELECT * FROM projects ORDER BY status, name")
        if 0 <= idx < len(rows): return rows[idx]
        return None

    def _render_detail(self) -> None:
        p = self._selected_project()
        if not p: self.detail.setText(""); return
        tasks = self.context.db.query("SELECT COUNT(*) c FROM tasks WHERE category=?", (p["name"],))
        self.detail.setText(f"{p['name']}\n{p['description']}\nStatus: {p['status']}\nProject tasks: {tasks[0]['c'] if tasks else 0}")

    def on_show(self) -> None:
        self.refresh()
