"""Password Vault: encrypted local storage with master password + generator."""

from __future__ import annotations

import secrets
import string

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QFrame, QHBoxLayout, QInputDialog, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QSplitter, QVBoxLayout, QWidget,
)

from security.encryption import decrypt, encrypt
from security.passwords import hash_password, verify_password
from ui.components.page import RealmPage

_MASTER_KEY = "vault.master_hash"


class VaultPage(RealmPage):
    page_title = "Password Vault"

    def __init__(self, context, parent=None) -> None:
        self._unlocked = False
        self._master: str | None = None
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("Password Vault"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        add = QPushButton("Add"); add.setObjectName("PrimaryButton"); add.clicked.connect(self.add_entry); header.addWidget(add)
        self.lock_btn = QPushButton("Lock"); self.lock_btn.clicked.connect(self.lock); header.addWidget(self.lock_btn); self.layout_root.addLayout(header)

        self.body = QWidget(); self.body_layout = QVBoxLayout(self.body); self.body_layout.setContentsMargins(0,0,0,0)
        self.layout_root.addWidget(self.body, 1)
        self._render()

    # -- lock state -----------------------------------------------------
    def _master_hash(self) -> str | None:
        return self.context.settings.get_str(_MASTER_KEY, "") or None

    def _render(self) -> None:
        while self.body_layout.count():
            it = self.body_layout.takeAt(0); w = it.widget()
            if w: w.deleteLater()
        if not self._unlocked:
            self._render_locked()
        else:
            self._render_unlocked()

    def _render_locked(self) -> None:
        frame = QFrame(); frame.setObjectName("Card"); lay = QVBoxLayout(frame); lay.setSpacing(10)
        has_master = self._master_hash() is not None
        lay.addWidget(QLabel("Vault locked" if has_master else "Set a master password to protect your vault"))
        pwd = QLineEdit(); pwd.setEchoMode(QLineEdit.EchoMode.Password); pwd.setPlaceholderText("Master password"); lay.addWidget(pwd)
        if has_master:
            btn = QPushButton("Unlock"); btn.setObjectName("PrimaryButton"); btn.clicked.connect(lambda: self.unlock(pwd.text())); lay.addWidget(btn)
            pwd.returnPressed.connect(lambda: self.unlock(pwd.text()))
        else:
            confirm = QLineEdit(); confirm.setEchoMode(QLineEdit.EchoMode.Password); confirm.setPlaceholderText("Confirm master password"); lay.addWidget(confirm)
            btn = QPushButton("Create vault"); btn.setObjectName("PrimaryButton"); btn.clicked.connect(lambda: self.setup(pwd.text(), confirm.text())); lay.addWidget(btn)
        self.body_layout.addWidget(frame); self.body_layout.addStretch(1)

    def _render_unlocked(self) -> None:
        splitter = QSplitter(Qt.Orientation.Horizontal)
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0)
        self.search = QLineEdit(); self.search.setObjectName("SearchBox"); self.search.setPlaceholderText("Search…"); self.search.textChanged.connect(lambda _t: self.refresh_list()); ll.addWidget(self.search)
        self.list = QListWidget(); self.list.itemClicked.connect(lambda item: self._show_detail(item.data(Qt.ItemDataRole.UserRole))); ll.addWidget(self.list, 1); splitter.addWidget(left)
        self.detail = QLabel("Select an entry"); self.detail.setObjectName("Muted"); self.detail.setWordWrap(True); self.detail.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse); splitter.addWidget(self.detail); splitter.setSizes([380, 500])
        self.body_layout.addWidget(splitter, 1)
        self.refresh_list()

    # -- master ---------------------------------------------------------
    def setup(self, password: str, confirm: str) -> None:
        if len(password) < 4: QMessageBox.warning(self, "Vault", "Master password too short."); return
        if password != confirm: QMessageBox.warning(self, "Vault", "Passwords don't match."); return
        self.context.settings.set(_MASTER_KEY, hash_password(password))
        self._master = password; self._unlocked = True; self._render()

    def unlock(self, password: str) -> None:
        h = self._master_hash()
        if h and verify_password(password, h):
            self._master = password; self._unlocked = True; self._render()
        else:
            QMessageBox.warning(self, "Vault", "Wrong master password.")

    def lock(self) -> None:
        self._unlocked = False; self._master = None; self._render()

    # -- entries --------------------------------------------------------
    def refresh_list(self) -> None:
        if not hasattr(self, "list"): return
        query = self.search.text().strip().lower() if hasattr(self, "search") else ""
        self.list.clear()
        rows = self.context.db.query("SELECT id, title, username, category FROM vault_entries ORDER BY title")
        for r in rows:
            if query and query not in r["title"].lower() and query not in r["username"].lower(): continue
            item = QListWidgetItem(r["title"] + (f"  ({r['username']})" if r["username"] else "")); item.setData(Qt.ItemDataRole.UserRole, r["id"]); self.list.addItem(item)

    def add_entry(self) -> None:
        if not self._unlocked or not self._master: return
        title, ok = QInputDialog.getText(self, "Add entry", "Title / site:")
        if not ok or not title.strip(): return
        username, _ = QInputDialog.getText(self, "Add entry", "Username / email:")
        pwd, _ = QInputDialog.getText(self, "Add entry", "Password (leave blank to generate):", QLineEdit.EchoMode.Password)
        if not pwd:
            pwd = generate_password()
            QMessageBox.information(self, "Generated password", f"Saved generated password:\n{pwd}")
        url, _ = QInputDialog.getText(self, "Add entry", "URL (optional):")
        enc_pwd = encrypt(pwd, self._master)
        self.context.db.execute(
            "INSERT INTO vault_entries (title, username, password, url, updated_at) VALUES (?, ?, ?, ?, datetime('now'))",
            (title.strip(), username.strip(), enc_pwd, url.strip()))
        self.refresh_list()

    def _show_detail(self, entry_id: int) -> None:
        row = self.context.db.query_one("SELECT * FROM vault_entries WHERE id=?", (entry_id,))
        if not row: return
        pwd = decrypt(row["password"], self._master) if self._master else ""
        self.detail.setText(f"Title: {row['title']}\nUsername: {row['username']}\nPassword: {pwd}\nURL: {row['url']}\n\nNotes: {row['notes']}")

    def on_show(self) -> None:
        pass


def generate_password(length: int = 16) -> str:
    """Cryptographically secure password with letters, digits, symbols."""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()-_=+"
    while True:
        pwd = "".join(secrets.choice(alphabet) for _ in range(length))
        if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd) and any(c in "!@#$%^&*()-_=+" for c in pwd)):
            return pwd
