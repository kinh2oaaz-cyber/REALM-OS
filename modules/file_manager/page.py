"""File Manager page."""

from __future__ import annotations

import os
from pathlib import Path

from PySide6.QtCore import QModelIndex, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QPixmap
from PySide6.QtWidgets import (
    QFileSystemModel,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSplitter,
    QTabWidget,
    QTextBrowser,
    QTreeView,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage
from ui.icons import icon as _icon

from .services import FileService


def _human(n: float) -> str:
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


class FileManagerPage(RealmPage):
    page_title = "File Manager"

    def __init__(self, context, parent=None) -> None:
        self.service = FileService(context)
        self.current_path = str(Path.home())
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel("File Manager"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        self.layout_root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # ---- left: drives / favorites / recents ----
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0); ll.setSpacing(8)
        ll.addWidget(QLabel("Drives"))
        self.drives_list = QListWidget(); self.drives_list.itemClicked.connect(self._open_drive); ll.addWidget(self.drives_list)
        ll.addWidget(QLabel("Favorites"))
        self.fav_list = QListWidget(); self.fav_list.itemClicked.connect(self._open_favorite); ll.addWidget(self.fav_list)
        ll.addWidget(QLabel("Recent"))
        self.recent_list = QListWidget(); self.recent_list.itemClicked.connect(self._open_recent); ll.addWidget(self.recent_list, 1)
        splitter.addWidget(left)

        # ---- center: browser + toolbar ----
        center = QWidget(); cl = QVBoxLayout(center); cl.setContentsMargins(0,0,0,0); cl.setSpacing(8)
        toolbar = QHBoxLayout()
        up = QPushButton(" Up"); up.clicked.connect(self.go_up); toolbar.addWidget(up)
        self.path_edit = QLineEdit(self.current_path); self.path_edit.returnPressed.connect(self._go_to_path); toolbar.addWidget(self.path_edit, 1)
        self.search_edit = QLineEdit(); self.search_edit.setObjectName("SearchBox"); self.search_edit.setPlaceholderText("Filter / search…")
        self.search_edit.setClearButtonEnabled(True); self.search_edit.textChanged.connect(lambda _t: self.refresh()); toolbar.addWidget(self.search_edit)
        new_folder = QPushButton("＋ New Folder"); new_folder.clicked.connect(self.new_folder); toolbar.addWidget(new_folder)
        cl.addLayout(toolbar)

        # storage overview
        self.storage_label = QLabel(); self.storage_label.setObjectName("Muted"); cl.addWidget(self.storage_label)

        # action toolbar
        actions = QHBoxLayout()
        for label, slot in [("Open", self.open_selected), ("Copy", self.copy_selected), ("Move", self.move_selected),
                            ("Rename", self.rename_selected), ("Delete", self.delete_selected),
                            ("Favorite", self.toggle_favorite), ("Open in app", self.open_external)]:
            b = QPushButton(label); b.clicked.connect(slot)
            if label == "Delete": b.setObjectName("DangerButton")
            actions.addWidget(b)
        actions.addStretch(1); cl.addLayout(actions)

        self.model = QFileSystemModel()
        self.model.setRootPath("")
        self.model.setFilter(QDirFilters())
        self.tree = QTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(self.model.index(self.current_path))
        self.tree.setSortingEnabled(True)
        self.tree.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        self.tree.setColumnWidth(0, 320)
        self.tree.doubleClicked.connect(self._on_double_click)
        self.tree.selectionModel().selectionChanged.connect(lambda *_a: self._show_preview())
        cl.addWidget(self.tree, 1)
        splitter.addWidget(center)

        # ---- right: preview + metadata ----
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(8)
        rl.addWidget(QLabel("Preview"))
        self.preview_scroll = QScrollArea(); self.preview_scroll.setWidgetResizable(True)
        self.preview = QTextBrowser(); self.preview_scroll.setWidget(self.preview)
        self.image_preview = QLabel(); self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        rl.addWidget(self.preview_scroll, 1)
        rl.addWidget(QLabel("Metadata"))
        self.meta_label = QLabel(); self.meta_label.setObjectName("Muted"); self.meta_label.setWordWrap(True); rl.addWidget(self.meta_label)
        splitter.addWidget(right)

        splitter.setSizes([220, 700, 320])
        self.layout_root.addWidget(splitter, 1)

        self._refresh_drives()
        self.refresh()
        self._refresh_favorites()
        self._refresh_recents()
        self._update_storage()

    # -- navigation -----------------------------------------------------
    def _on_double_click(self, index: QModelIndex) -> None:
        path = self.model.filePath(index)
        self.open_path(path)

    def open_path(self, path: str) -> None:
        if os.path.isdir(path):
            self.current_path = path
            self.path_edit.setText(path)
            self.tree.setRootIndex(self.model.index(path))
            self.refresh()
            self._update_storage()
        elif os.path.isfile(path):
            self.service.record_recent(path)
            self._refresh_recents()
            self._show_preview_for(path)

    def go_up(self) -> None:
        parent = str(Path(self.current_path).parent)
        if parent != self.current_path:
            self.open_path(parent)

    def _go_to_path(self) -> None:
        self.open_path(self.path_edit.text().strip())

    def _open_drive(self, item: QListWidgetItem) -> None:
        self.open_path(item.data(Qt.ItemDataRole.UserRole))

    def _open_favorite(self, item: QListWidgetItem) -> None:
        self.open_path(item.data(Qt.ItemDataRole.UserRole))

    def _open_recent(self, item: QListWidgetItem) -> None:
        self.open_path(item.data(Qt.ItemDataRole.UserRole))

    # -- listing --------------------------------------------------------
    def refresh(self) -> None:
        self.tree.setRootIndex(self.model.index(self.current_path))
        self._update_storage()

    def _update_storage(self) -> None:
        try:
            ov = self.service.storage_overview(self.current_path)
            self.storage_label.setText(
                f"{_human(ov['used'])} used of {_human(ov['total'])}  ·  {_human(ov['free'])} free  ·  {ov['used_percent']}% used")
        except OSError:
            self.storage_label.setText("")

    def _refresh_drives(self) -> None:
        self.drives_list.clear()
        for d in self.service.drives():
            item = QListWidgetItem(d["name"])
            item.setData(Qt.ItemDataRole.UserRole, d["path"])
            if d["total"]:
                item.setToolTip(f"{_human(d['free'])} free of {_human(d['total'])}")
            self.drives_list.addItem(item)

    def _refresh_favorites(self) -> None:
        self.fav_list.clear()
        for path in self.service.favorites():
            item = QListWidgetItem(Path(path).name or path)
            item.setData(Qt.ItemDataRole.UserRole, path); self.fav_list.addItem(item)

    def _refresh_recents(self) -> None:
        self.recent_list.clear()
        for path in self.service.recents(15):
            item = QListWidgetItem(Path(path).name)
            item.setData(Qt.ItemDataRole.UserRole, path); item.setToolTip(path); self.recent_list.addItem(item)

    # -- selection ------------------------------------------------------
    def selected_path(self) -> str | None:
        idxs = self.tree.selectionModel().selectedIndexes()
        if not idxs:
            return None
        return self.model.filePath(idxs[0])

    # -- preview --------------------------------------------------------
    def _show_preview(self) -> None:
        path = self.selected_path()
        if path:
            self._show_preview_for(path)

    def _show_preview_for(self, path: str) -> None:
        if os.path.isdir(path):
            self.preview.setPlainText(f"Folder: {path}\n\n{len(os.listdir(path)) if os.access(path, os.R_OK) else '?'} items")
            self.meta_label.setText("Directory")
            return
        try:
            meta = self.service.metadata(path)
            self.meta_label.setText(
                f"Name: {meta['name']}\nSize: {_human(meta['size'])}\nModified: {meta['modified']}\n"
                f"Created: {meta['created']}\nType: {meta['extension'] or 'file'}\nRead-only: {meta['readonly']}\n{meta['path']}")
        except OSError as exc:
            self.meta_label.setText(str(exc))
        if self.service.is_image(path):
            pix = QPixmap(path)
            if not pix.isNull():
                self.image_preview.setPixmap(pix.scaledToWidth(300, Qt.TransformationMode.SmoothTransformation))
                self.preview_scroll.setWidget(self.image_preview)
                return
        self.preview_scroll.setWidget(self.preview)
        if self.service.is_text(path):
            self.preview.setPlainText(self.service.read_text_preview(path))
        else:
            self.preview.setPlainText(f"No inline preview for this file type.\n\n{path}\n\nUse 'Open in app' to open it.")

    # -- operations (confirmation enforced) -----------------------------
    def open_selected(self) -> None:
        path = self.selected_path()
        if path:
            self.open_path(path)

    def open_external(self) -> None:
        path = self.selected_path()
        if path:
            QDesktopServices.openUrl(QUrl.fromLocalFile(path))

    def new_folder(self) -> None:
        name, ok = QInputDialog.getText(self, "New folder", "Folder name:")
        if not ok or not name.strip():
            return
        try:
            created = self.service.create_folder(self.current_path, name.strip())
            self.refresh()
        except FileExistsError:
            QMessageBox.warning(self, "New folder", "A folder with that name already exists.")
        except PermissionError:
            QMessageBox.warning(self, "New folder", "Permission denied.")
        except OSError as exc:
            QMessageBox.warning(self, "New folder", str(exc))

    def copy_selected(self) -> None:
        src = self.selected_path()
        if not src: return
        if QMessageBox.question(self, "Copy", f"Copy '{Path(src).name}' to a folder?") != QMessageBox.StandardButton.Yes: return
        from PySide6.QtWidgets import QFileDialog
        dst_dir = QFileDialog.getExistingDirectory(self, "Copy to folder", self.current_path)
        if not dst_dir: return
        try:
            self.service.copy(src, dst_dir); self.refresh()
        except (PermissionError, OSError, shutil_err()) as exc:
            QMessageBox.warning(self, "Copy failed", str(exc))

    def move_selected(self) -> None:
        src = self.selected_path()
        if not src: return
        if QMessageBox.question(self, "Move", f"Move '{Path(src).name}' to a folder?") != QMessageBox.StandardButton.Yes: return
        from PySide6.QtWidgets import QFileDialog
        dst_dir = QFileDialog.getExistingDirectory(self, "Move to folder", self.current_path)
        if not dst_dir: return
        try:
            self.service.move(src, dst_dir); self.refresh()
        except (PermissionError, OSError) as exc:
            QMessageBox.warning(self, "Move failed", str(exc))

    def rename_selected(self) -> None:
        src = self.selected_path()
        if not src: return
        name, ok = QInputDialog.getText(self, "Rename", "New name:", text=Path(src).name)
        if not ok or not name.strip(): return
        if QMessageBox.question(self, "Rename", f"Rename '{Path(src).name}' to '{name}'?") != QMessageBox.StandardButton.Yes: return
        try:
            self.service.rename(src, name.strip()); self.refresh()
        except (PermissionError, OSError, FileExistsError) as exc:
            QMessageBox.warning(self, "Rename failed", str(exc))

    def delete_selected(self) -> None:
        src = self.selected_path()
        if not src: return
        kind = "folder" if os.path.isdir(src) else "file"
        if QMessageBox.question(
            self, "Delete", f"Permanently delete this {kind}?\n\n{src}\n\nThis cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No,
        ) != QMessageBox.StandardButton.Yes:
            return
        try:
            self.service.delete(src); self.refresh(); self._refresh_recents()
        except (PermissionError, OSError) as exc:
            QMessageBox.warning(self, "Delete failed", str(exc))

    def toggle_favorite(self) -> None:
        src = self.selected_path()
        if not src: return
        if self.service.is_favorite(src):
            self.service.remove_favorite(src)
        else:
            self.service.add_favorite(src)
        self._refresh_favorites()

    def on_show(self) -> None:
        self.refresh(); self._refresh_favorites(); self._refresh_recents()


def QDirFilters():
    from PySide6.QtCore import QDir
    return QDir.Filter.AllEntries | QDir.Filter.NoDotAndDotDot | QDir.Filter.AllDirs


def shutil_err():
    import shutil
    return shutil.Error
