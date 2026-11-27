"""Download Manager: real HTTP(S) downloads with progress + cancel + history."""

from __future__ import annotations

import os
import urllib.request
from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QVBoxLayout

from ui.components.page import RealmPage

_UA = {"User-Agent": "REALM-OS/1.0"}


class DownloadWorker(QObject):
    progress = Signal(int, int)      # done, total
    finished = Signal(bool, str)     # ok, message
    failed = Signal(str)

    def __init__(self, url: str, dest: str) -> None:
        super().__init__(); self.url = url; self.dest = dest; self._cancel = False

    def cancel(self) -> None:
        self._cancel = True

    def run(self) -> None:
        try:
            req = urllib.request.Request(self.url, headers=_UA)
            with urllib.request.urlopen(req, timeout=30) as resp, open(self.dest, "wb") as out:  # noqa: S310
                total = int(resp.headers.get("Content-Length", 0) or 0)
                done = 0
                while True:
                    if self._cancel:
                        out.close(); self.finished.emit(False, "cancelled"); return
                    chunk = resp.read(64 * 1024)
                    if not chunk: break
                    out.write(chunk); done += len(chunk); self.progress.emit(done, total)
            self.finished.emit(True, self.dest)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))


class DownloadsPage(RealmPage):
    page_title = "Download Manager"

    def __init__(self, context, parent=None) -> None:
        self._thread: QThread | None = None; self._worker: DownloadWorker | None = None
        self._download_id: int | None = None
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        title = QLabel("Download Manager"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        row = QHBoxLayout()
        self.url_edit = QLineEdit(); self.url_edit.setPlaceholderText("https://example.com/file.zip"); row.addWidget(self.url_edit, 1)
        self.start_btn = QPushButton("Download…"); self.start_btn.setObjectName("PrimaryButton"); self.start_btn.clicked.connect(self.start_download); row.addWidget(self.start_btn)
        self.cancel_btn = QPushButton("Cancel"); self.cancel_btn.setEnabled(False); self.cancel_btn.clicked.connect(self.cancel); row.addWidget(self.cancel_btn)
        self.layout_root.addLayout(row)
        self.status = QLabel(""); self.status.setObjectName("Muted"); self.layout_root.addWidget(self.status)
        self.list = QListWidget(); self.layout_root.addWidget(self.list, 1)
        self.refresh_history()

    def start_download(self) -> None:
        url = self.url_edit.text().strip()
        if not url: return
        filename = os.path.basename(urllib.parse.urlparse(url).path) or "download"
        dest_dir = QFileDialog.getExistingDirectory(self, "Save to folder", str(Path.home() / "Downloads"))
        if not dest_dir: return
        dest = os.path.join(dest_dir, filename)
        cur = self.context.db.execute("INSERT INTO downloads (url, filename, destination, status) VALUES (?, ?, ?, 'downloading')", (url, filename, dest))
        self._download_id = int(cur.lastrowid)

        self._thread = QThread(self); self._worker = DownloadWorker(url, dest); self._worker.moveToThread(self._thread)
        self._worker.progress.connect(self._on_progress); self._worker.finished.connect(self._on_finished); self._worker.failed.connect(self._on_failed)
        self._thread.started.connect(self._worker.run); self._thread.start()
        self.start_btn.setEnabled(False); self.cancel_btn.setEnabled(True); self.status.setText(f"Downloading {filename}…")

    def cancel(self) -> None:
        if self._worker: self._worker.cancel()

    def _on_progress(self, done: int, total: int) -> None:
        pct = int(done / total * 100) if total else 0
        self.status.setText(f"Downloading… {done:,} / {total:,} bytes ({pct}%)" if total else f"Downloading… {done:,} bytes")

    def _on_finished(self, ok: bool, message: str) -> None:
        self._cleanup_thread()
        status = "done" if ok else "cancelled"
        if self._download_id:
            self.context.db.execute("UPDATE downloads SET status=?, finished_at=datetime('now') WHERE id=?", (status, self._download_id))
        self.status.setText("Done" if ok else f"Cancelled: {message}"); self.refresh_history()

    def _on_failed(self, message: str) -> None:
        self._cleanup_thread()
        if self._download_id:
            self.context.db.execute("UPDATE downloads SET status='failed', finished_at=datetime('now') WHERE id=?", (self._download_id,))
        self.status.setText("Failed: " + message); self.refresh_history()

    def _cleanup_thread(self) -> None:
        self.start_btn.setEnabled(True); self.cancel_btn.setEnabled(False)
        if self._thread: self._thread.quit(); self._thread.wait(1000); self._thread = None; self._worker = None

    def refresh_history(self) -> None:
        self.list.clear()
        for r in self.context.db.query("SELECT * FROM downloads ORDER BY id DESC LIMIT 50"):
            self.list.addItem(f"[{r['status']}] {r['filename']}  {r['url']}")


import urllib.parse  # noqa: E402
