"""Tasks page: Personal Task Manager (Kanban, daily/weekly) + PC Task Manager."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage
from ui.icons import icon as _icon

from .models import KANBAN_COLUMNS, PRIORITIES, Task
from .pc_task_manager import PCTaskManager
from .services import TaskService

_COLUMN_TITLES = {"todo": "To Do", "in_progress": "In Progress", "done": "Done"}
_PRIORITY_COLORS = {0: "#8E8E93", 1: "#0071E3", 2: "#FF9500", 3: "#FF3B30"}


class TasksPage(RealmPage):
    page_title = "Tasks"

    def __init__(self, context, parent=None) -> None:
        self.service = TaskService(context)
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel("Tasks")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        self.layout_root.addLayout(header)

        self.tabs = QTabWidget()
        self.tabs.addTab(self._personal_tab(), "Personal Task Manager")
        self.pc = PCTaskManager()
        self.tabs.addTab(self.pc, "PC Task Manager")
        self.layout_root.addWidget(self.tabs, 1)

    # ===================== Personal Task Manager =====================
    def _personal_tab(self) -> QWidget:
        wrap = QWidget()
        layout = QVBoxLayout(wrap)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)

        bar = QHBoxLayout()
        self.search = QLineEdit(); self.search.setObjectName("SearchBox")
        self.search.setPlaceholderText("Search tasks…"); self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(lambda _t: self.refresh_kanban())
        bar.addWidget(self.search, 1)
        self.view_combo = QComboBox(); self.view_combo.addItems(["Kanban", "Daily", "Weekly", "All"])
        self.view_combo.currentIndexChanged.connect(lambda _i: self.refresh_kanban())
        bar.addWidget(self.view_combo)
        add = QPushButton("New Task"); add.setObjectName("PrimaryButton"); add.clicked.connect(self.add_task)
        bar.addWidget(add)
        layout.addLayout(bar)

        self.stats = QLabel(); self.stats.setObjectName("Muted"); layout.addWidget(self.stats)

        self.content = QWidget()
        self.content_layout = QVBoxLayout(self.content)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setWidget(self.content); layout.addWidget(scroll, 1)

        self.refresh_kanban()
        return wrap

    def refresh_kanban(self) -> None:
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
            elif item.layout(): self._clear(item.layout())

        counts = self.service.counts()
        self.stats.setText(
            f"{counts.get('total',0)} total · {counts.get('todo',0)} to do · "
            f"{counts.get('in_progress',0)} in progress · {counts.get('done',0)} done")

        mode = self.view_combo.currentText()
        query = self.search.text().strip().lower()

        if mode == "Kanban":
            board = QHBoxLayout(); board.setSpacing(12)
            for col in KANBAN_COLUMNS:
                board.addWidget(self._kanban_column(col, query), 1)
            holder = QWidget(); holder.setLayout(board); self.content_layout.addWidget(holder)
        else:
            tasks = self._tasks_for_mode(mode)
            if query:
                tasks = [t for t in tasks if query in t.title.lower() or query in t.description.lower()]
            if not tasks:
                empty = QLabel("No tasks."); empty.setObjectName("Muted"); self.content_layout.addWidget(empty)
            for t in tasks:
                self.content_layout.addWidget(self._task_card(t))
            self.content_layout.addStretch(1)

    def _tasks_for_mode(self, mode: str) -> list[Task]:
        if mode == "Daily":
            return self.service.daily()
        if mode == "Weekly":
            return self.service.weekly()
        return self.service.repo.list_all()

    def _kanban_column(self, column: str, query: str) -> QWidget:
        col_widget = QFrame(); col_widget.setObjectName("Card")
        lay = QVBoxLayout(col_widget); lay.setSpacing(8)
        title = QLabel(_COLUMN_TITLES.get(column, column)); title.setObjectName("SectionTitle"); lay.addWidget(title)
        tasks = self.service.repo.by_column(column)
        if query:
            tasks = [t for t in tasks if query in t.title.lower() or query in t.description.lower()]
        if not tasks:
            hint = QLabel("No tasks here yet.")
            hint.setObjectName("Tiny")
            lay.addWidget(hint)
        for t in tasks:
            lay.addWidget(self._task_card(t, in_kanban=True, column=column))
        add = QPushButton("+ Add task"); add.setObjectName("GhostButton"); add.clicked.connect(lambda _c=False, c=column: self.add_task(column=c)); lay.addWidget(add)
        lay.addStretch(1)
        return col_widget

    def _task_card(self, task: Task, in_kanban: bool = False, column: str = "todo") -> QWidget:
        card = QFrame(); card.setObjectName("Card")
        lay = QVBoxLayout(card); lay.setContentsMargins(12, 10, 12, 10); lay.setSpacing(4)
        top = QHBoxLayout()
        title = QLabel((" " if task.is_done else " ") + task.title)
        title.setStyleSheet("font-weight:600;" + ("text-decoration: line-through;" if task.is_done else ""))
        title.setWordWrap(True)
        top.addWidget(title, 1)
        dot = QLabel(""); dot.setStyleSheet(f"color:{_PRIORITY_COLORS.get(task.priority,'#0071E3')};"); top.addWidget(dot)
        lay.addLayout(top)
        meta = []
        if task.priority: meta.append(PRIORITIES.get(task.priority, "Normal"))
        if task.category: meta.append(task.category)
        if task.deadline: meta.append("due " + task.deadline)
        if meta:
            m = QLabel("·".join(meta)); m.setObjectName("Tiny"); lay.addWidget(m)
        if task.description:
            d = QLabel(task.description); d.setObjectName("Muted"); d.setWordWrap(True); lay.addWidget(d)

        actions = QHBoxLayout()
        if not task.is_done:
            done_btn = QPushButton("Done"); done_btn.clicked.connect(lambda _c=False, tid=task.id: self._set_done(tid)); actions.addWidget(done_btn)
        else:
            reopen = QPushButton("Reopen"); reopen.clicked.connect(lambda _c=False, tid=task.id: self._set_undone(tid)); actions.addWidget(reopen)
        edit = QPushButton("Edit"); edit.clicked.connect(lambda _c=False, tid=task.id: self.edit_task(tid)); actions.addWidget(edit)
        if in_kanban:
            others = [c for c in KANBAN_COLUMNS if c != column]
            for c in others:
                b = QPushButton(" " + _COLUMN_TITLES[c]); b.setObjectName("GhostButton")
                b.clicked.connect(lambda _c=False, tid=task.id, col=c: self._move(tid, col)); actions.addWidget(b)
        delete = QPushButton("Delete"); delete.setObjectName("DangerButton"); delete.clicked.connect(lambda _c=False, tid=task.id: self.delete_task(tid)); actions.addWidget(delete)
        actions.addStretch(1); lay.addLayout(actions)
        return card

    # -- actions --------------------------------------------------------
    def add_task(self, column: str = "todo") -> None:
        dlg = TaskDialog(parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted or not dlg.result_title:
            return
        tid = self.service.create_task(dlg.result_title, dlg.result_description, dlg.result_priority, dlg.result_category, dlg.result_deadline)
        self.service.move_to_column(tid, column)
        self.refresh_kanban()

    def edit_task(self, task_id: int) -> None:
        task = self.service.repo.get(task_id)
        if not task: return
        dlg = TaskDialog(task=task, parent=self)
        if dlg.exec() != QDialog.DialogCode.Accepted: return
        task.title = dlg.result_title or task.title
        task.description = dlg.result_description
        task.priority = dlg.result_priority
        task.category = dlg.result_category
        task.deadline = dlg.result_deadline
        self.service.update_task(task)
        self.refresh_kanban()

    def delete_task(self, task_id: int) -> None:
        if QMessageBox.question(self, "Delete task", "Delete this task?") != QMessageBox.StandardButton.Yes: return
        self.service.delete_task(task_id); self.refresh_kanban()

    def _set_done(self, task_id: int) -> None:
        self.service.set_status(task_id, "done"); self.refresh_kanban()

    def _set_undone(self, task_id: int) -> None:
        self.service.set_status(task_id, "todo"); self.refresh_kanban()

    def _move(self, task_id: int, column: str) -> None:
        self.service.move_to_column(task_id, column); self.refresh_kanban()

    def on_show(self) -> None:
        self.refresh_kanban()

    def _clear(self, layout) -> None:  # noqa: ANN001
        while layout.count():
            item = layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()


class TaskDialog(QDialog):
    def __init__(self, task: Task | None = None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Task"); self.setMinimumWidth(420)
        self.result_title = task.title if task else ""
        self.result_description = task.description if task else ""
        self.result_priority = task.priority if task else 1
        self.result_category = task.category if task else ""
        self.result_deadline = task.deadline if task else None

        root = QVBoxLayout(self); form = QFormLayout(); form.setSpacing(10)
        self.title_edit = QLineEdit(self.result_title); form.addRow("Title", self.title_edit)
        self.desc_edit = QTextEdit(self.result_description); self.desc_edit.setFixedHeight(80); form.addRow("Description", self.desc_edit)
        self.prio_combo = QComboBox(); self.prio_combo.addItems(list(PRIORITIES.values())); self.prio_combo.setCurrentIndex(self.result_priority); form.addRow("Priority", self.prio_combo)
        self.cat_edit = QLineEdit(self.result_category); form.addRow("Category", self.cat_edit)
        self.deadline_edit = QLineEdit(self.result_deadline or ""); self.deadline_edit.setPlaceholderText("YYYY-MM-DD HH:MM"); form.addRow("Deadline", self.deadline_edit)
        root.addLayout(form)
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._accept); buttons.rejected.connect(self.reject); root.addWidget(buttons)

    def _accept(self) -> None:
        self.result_title = self.title_edit.text().strip()
        if not self.result_title:
            QMessageBox.warning(self, "Task", "Please enter a title."); return
        self.result_description = self.desc_edit.toPlainText()
        self.result_priority = self.prio_combo.currentIndex()
        self.result_category = self.cat_edit.text().strip()
        dl = self.deadline_edit.text().strip()
        self.result_deadline = dl or None
        self.accept()
