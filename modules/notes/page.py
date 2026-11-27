"""Notepad page: rich-text + Markdown, autosave, folders, pin, search,
word/char counter, export TXT/MD, optional password protection, attachments."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QTextCursor
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage
from ui.icons import icon as _icon

from .models import FORMATS
from .services import NotesService


class NotesPage(RealmPage):
    page_title = "Notes"

    def __init__(self, context, parent=None) -> None:
        self.service = NotesService(context)
        self.current_note_id: int | None = None
        self._current_password: str | None = None     # for protected notes in session
        self._loading = False
        super().__init__(context, parent)

    # -- construction ---------------------------------------------------
    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)

        header = QHBoxLayout()
        title = QLabel("Notes")
        title.setObjectName("SectionTitle")
        header.addWidget(title)
        header.addStretch(1)
        new_btn = QPushButton("New Note"); new_btn.setIcon(_icon("plus", size=18))
        new_btn.setObjectName("PrimaryButton")
        new_btn.clicked.connect(self.new_note)
        header.addWidget(new_btn)
        self.layout_root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---- left list ----
        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(8)

        self.search_edit = QLineEdit()
        self.search_edit.setObjectName("SearchBox")
        self.search_edit.setPlaceholderText("Search notes…")
        self.search_edit.setClearButtonEnabled(True)
        self.search_edit.textChanged.connect(lambda _t: self.refresh_list())
        left_layout.addWidget(self.search_edit)

        self.folder_combo = QComboBox()
        self.folder_combo.addItem("All folders", None)
        self.folder_combo.currentIndexChanged.connect(lambda _i: self.refresh_list())
        left_layout.addWidget(self.folder_combo)

        self.note_list = QListWidget()
        self.note_list.itemClicked.connect(self._on_note_selected)
        left_layout.addWidget(self.note_list, 1)

        folder_row = QHBoxLayout()
        add_folder = QPushButton("Folder"); add_folder.setIcon(_icon("folder-plus", size=18))
        add_folder.clicked.connect(self.add_folder)
        folder_row.addWidget(add_folder)
        left_layout.addLayout(folder_row)
        splitter.addWidget(left)

        # ---- editor ----
        editor = QWidget()
        ed = QVBoxLayout(editor)
        ed.setContentsMargins(0, 0, 0, 0)
        ed.setSpacing(8)

        title_row = QHBoxLayout()
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Title")
        self.title_edit.textChanged.connect(lambda _t: self.schedule_autosave())
        title_row.addWidget(self.title_edit, 1)
        self.pin_btn = QPushButton(); self.pin_btn.setIcon(_icon("pin", size=18))
        self.pin_btn.setCheckable(True)
        self.pin_btn.setToolTip("Pin important note")
        self.pin_btn.clicked.connect(self.toggle_pin)
        title_row.addWidget(self.pin_btn)
        self.protect_btn = QPushButton(); self.protect_btn.setIcon(_icon("lock", size=18))
        self.protect_btn.setCheckable(True)
        self.protect_btn.setToolTip("Password-protect note")
        self.protect_btn.clicked.connect(self.toggle_protection)
        title_row.addWidget(self.protect_btn)
        ed.addLayout(title_row)

        meta_row = QHBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems([f.capitalize() for f in FORMATS])
        self.format_combo.currentIndexChanged.connect(lambda _i: self.on_format_changed())
        meta_row.addWidget(QLabel("Format:"))
        meta_row.addWidget(self.format_combo)
        self.folder_edit = QLineEdit()
        self.folder_edit.setPlaceholderText("Folder")
        self.folder_edit.textChanged.connect(lambda _t: self.schedule_autosave())
        meta_row.addWidget(QLabel("Folder:"))
        meta_row.addWidget(self.folder_edit)
        self.category_edit = QLineEdit()
        self.category_edit.setPlaceholderText("Category")
        self.category_edit.textChanged.connect(lambda _t: self.schedule_autosave())
        meta_row.addWidget(QLabel("Category:"))
        meta_row.addWidget(self.category_edit)
        ed.addLayout(meta_row)

        # markdown toolbar (simple, real)
        self.md_toolbar = QHBoxLayout()
        for label, snippet in [("B", "**bold**"), ("I", "*italic*"), ("#", "# "), ("•", "- "), ("`", "`code`"), ("[link]", "[text](url)")]:
            b = QPushButton(label)
            b.setMaximumWidth(48)
            b.clicked.connect(lambda _c=False, s=snippet: self.insert_snippet(s))
            self.md_toolbar.addWidget(b)
        self.md_toolbar.addStretch(1)
        ed.addLayout(self.md_toolbar)

        self.editor = QTextEdit()
        self.editor.setAcceptRichText(True)
        self.editor.textChanged.connect(self.schedule_autosave)
        ed.addWidget(self.editor, 1)

        # bottom bar
        bottom = QHBoxLayout()
        self.counts_label = QLabel("0 words · 0 chars")
        self.counts_label.setObjectName("Muted")
        bottom.addWidget(self.counts_label)
        self.saved_label = QLabel("")
        self.saved_label.setObjectName("Tiny")
        bottom.addWidget(self.saved_label)
        bottom.addStretch(1)

        attach_btn = QPushButton("Attach file"); attach_btn.setIcon(_icon("paperclip", size=18))
        attach_btn.clicked.connect(self.attach_file)
        bottom.addWidget(attach_btn)
        self.export_txt_btn = QPushButton("Export TXT")
        self.export_txt_btn.clicked.connect(lambda: self.export("txt"))
        bottom.addWidget(self.export_txt_btn)
        self.export_md_btn = QPushButton("Export MD")
        self.export_md_btn.clicked.connect(lambda: self.export("md"))
        bottom.addWidget(self.export_md_btn)
        delete_btn = QPushButton("Delete")
        delete_btn.setObjectName("DangerButton")
        delete_btn.clicked.connect(self.delete_note)
        bottom.addWidget(delete_btn)
        ed.addLayout(bottom)

        splitter.addWidget(editor)
        splitter.setSizes([300, 820])
        self.layout_root.addWidget(splitter, 1)

        # autosave
        self._autosave = QTimer(self)
        self._autosave.setSingleShot(True)
        self._autosave.setInterval(800)
        self._autosave.timeout.connect(self.save_now)

        self._refresh_folders()
        self.refresh_list()
        self.set_editor_enabled(False)

    # -- list -----------------------------------------------------------
    def _refresh_folders(self) -> None:
        current = self.folder_combo.currentText()
        self.folder_combo.blockSignals(True)
        self.folder_combo.clear()
        self.folder_combo.addItem("All folders", None)
        self.folder_combo.addItem("(No folder)", "")
        for f in self.service.folders():
            self.folder_combo.addItem(f, f)
        idx = self.folder_combo.findText(current)
        self.folder_combo.setCurrentIndex(max(0, idx))
        self.folder_combo.blockSignals(False)

    def refresh_list(self) -> None:
        query = self.search_edit.text().strip()
        self.note_list.clear()
        if query:
            notes = self.service.search(query)
        else:
            folder = self.folder_combo.currentData()
            notes = self.service.list_notes(folder=folder)
        for note in notes:
            lock = ""
            pin = ""
            title = note.title or "Untitled"
            item = QListWidgetItem(f"{pin}{lock}{title}")
            item.setData(Qt.ItemDataRole.UserRole, note.id)
            item.setToolTip(f"{note.folder}\n{note.updated_at}")
            self.note_list.addItem(item)
        self._refresh_folders()

    def _on_note_selected(self, item: QListWidgetItem) -> None:
        note_id = item.data(Qt.ItemDataRole.UserRole)
        if note_id is None:
            return
        self.save_now()
        self.open_note(int(note_id))

    # -- note actions ---------------------------------------------------
    def new_note(self) -> None:
        self.save_now()
        note_id = self.service.create_note()
        self.open_note(note_id)
        self.refresh_list()

    def open_note(self, note_id: int) -> None:
        note = self.service.get_note(note_id)
        if note is None:
            return
        self.current_note_id = note_id
        self._current_password = None
        self._loading = True
        self.title_edit.setText(note.title)
        self.folder_edit.setText(note.folder)
        self.category_edit.setText(note.category)
        self.pin_btn.setChecked(note.pinned)
        self.protect_btn.setChecked(note.protected)
        fmt_index = FORMATS.index(note.format) if note.format in FORMATS else 0
        self.format_combo.setCurrentIndex(fmt_index)

        content = note.content
        if note.protected:
            pwd, ok = QInputDialog.getText(self, "Protected note", "Enter password:", QLineEdit.EchoMode.Password)
            if not ok:
                self._loading = False
                self.set_editor_enabled(False)
                return
            decrypted = self.service.unlock_note(note_id, pwd)
            if decrypted is None:
                QMessageBox.warning(self, "Protected note", "Wrong password.")
                self._loading = False
                self.set_editor_enabled(False)
                return
            self._current_password = pwd
            content = decrypted

        if note.format == "richtext":
            self.editor.setHtml(content)
        else:
            self.editor.setPlainText(content)
        self._loading = False
        self.set_editor_enabled(True)
        self.update_counts()
        self.saved_label.setText("")

    def save_now(self) -> None:
        if self.current_note_id is None or self._loading:
            return
        note = self.service.repo.get(self.current_note_id)
        fmt = FORMATS[self.format_combo.currentIndex()]
        if note and note.protected:
            plain = self.editor.toPlainText() if fmt != "richtext" else self.editor.toHtml()
            # strip html for richtext protected storage of plaintext
            plain_text = self.editor.toPlainText()
            if self._current_password:
                self.service.save_protected_content(
                    self.current_note_id, plain_text, self._current_password, title=self.title_edit.text()
                )
            self.update_counts()
            self.saved_label.setText("Saved ")
            return
        if fmt == "richtext":
            content = self.editor.toHtml()
        else:
            content = self.editor.toPlainText()
        self.service.save_note(
            self.current_note_id,
            title=self.title_edit.text() or "Untitled",
            content=content,
            plain_for_counts=self.editor.toPlainText(),
            fmt=fmt,
            folder=self.folder_edit.text().strip(),
            category=self.category_edit.text().strip(),
        )
        self.update_counts()
        self.saved_label.setText("Saved ")
        # stash draft for recovery
        self.service.stash_draft(self.current_note_id, content)

    def schedule_autosave(self) -> None:
        if self._loading or self.current_note_id is None:
            return
        self.saved_label.setText("…")
        self._autosave.start()
        self.update_counts()

    def on_format_changed(self) -> None:
        if self._loading:
            return
        self.schedule_autosave()

    def toggle_pin(self) -> None:
        if self.current_note_id is None:
            return
        self.service.set_pinned(self.current_note_id, self.pin_btn.isChecked())
        self.refresh_list()

    def toggle_protection(self) -> None:
        if self.current_note_id is None:
            return
        if self.protect_btn.isChecked():
            pwd, ok = QInputDialog.getText(self, "Protect note", "Set password:", QLineEdit.EchoMode.Password)
            if not ok or not pwd:
                self.protect_btn.setChecked(False)
                return
            self.save_now()
            self.service.protect_note(self.current_note_id, pwd)
            self._current_password = pwd
        else:
            pwd, ok = QInputDialog.getText(self, "Remove protection", "Enter password:", QLineEdit.EchoMode.Password)
            if not ok or not self.service.remove_protection(self.current_note_id, pwd):
                QMessageBox.warning(self, "Protected note", "Wrong password.")
                self.protect_btn.setChecked(True)
                return
            self._current_password = None
        self.refresh_list()

    def delete_note(self) -> None:
        if self.current_note_id is None:
            return
        if QMessageBox.question(self, "Delete note", "Delete this note permanently?") != QMessageBox.StandardButton.Yes:
            return
        self.service.delete_note(self.current_note_id)
        self.current_note_id = None
        self._loading = True
        self.title_edit.clear(); self.editor.clear(); self.folder_edit.clear(); self.category_edit.clear()
        self._loading = False
        self.set_editor_enabled(False)
        self.refresh_list()

    def add_folder(self) -> None:
        name, ok = QInputDialog.getText(self, "New folder", "Folder name:")
        if ok and name.strip():
            self.service.add_folder(name.strip())
            self._refresh_folders()
            self.refresh_list()

    def attach_file(self) -> None:
        if self.current_note_id is None:
            return
        path, _ = QFileDialog.getOpenFileName(self, "Attach file")
        if not path:
            return
        try:
            self.service.add_attachment(self.current_note_id, path)
            QMessageBox.information(self, "Attachment", f"Attached:\n{path}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Attachment", str(exc))

    def export(self, kind: str) -> None:
        if self.current_note_id is None:
            return
        note = self.service.repo.get(self.current_note_id)
        if note and note.protected:
            QMessageBox.warning(self, "Export", "Unlock and remove protection before exporting.")
            return
        self.save_now()
        safe_title = (note.title if note else "note").replace("/", "-").replace("\\", "-") or "note"
        ext = "txt" if kind == "txt" else "md"
        dest, _ = QFileDialog.getSaveFileName(self, "Export", f"{safe_title}.{ext}", f"*.{ext}")
        if not dest:
            return
        try:
            if kind == "txt":
                self.service.export_txt(self.current_note_id, dest)
            else:
                self.service.export_markdown(self.current_note_id, dest)
            QMessageBox.information(self, "Export", f"Saved:\n{dest}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Export failed", str(exc))

    def insert_snippet(self, snippet: str) -> None:
        cursor = self.editor.textCursor()
        cursor.insertText(snippet)
        self.editor.setTextCursor(cursor)

    # -- helpers --------------------------------------------------------
    def update_counts(self) -> None:
        text = self.editor.toPlainText()
        words = len([w for w in text.split() if w.strip()])
        self.counts_label.setText(f"{words} words · {len(text)} chars")

    def set_editor_enabled(self, enabled: bool) -> None:
        for w in (self.title_edit, self.editor, self.format_combo, self.folder_edit,
                  self.category_edit, self.pin_btn, self.protect_btn,
                  self.export_txt_btn, self.export_md_btn):
            w.setEnabled(enabled)

    def on_show(self) -> None:
        self.refresh_list()
