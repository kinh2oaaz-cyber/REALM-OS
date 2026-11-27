"""PC Task Manager: running processes, CPU/RAM/disk/network, system info,
process search & sorting, safe termination with confirmation."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from system.info import list_processes, system_info

_COLUMNS = ["PID", "Name", "CPU %", "RAM", "Disk I/O", "User", "Status"]
_SORTABLE = {"PID": "pid", "Name": "name", "CPU %": "cpu_percent", "RAM": "memory_bytes"}


def _human(n: float) -> str:
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024:
            return f"{n:.0f} {unit}"
        n /= 1024
    return f"{n:.0f} PB"


class PCTaskManager(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._procs: list[dict] = []
        self._sort_col = 2
        self._sort_desc = True
        self._last_io: dict[int, tuple[int, int]] = {}
        self._build()
        self._timer = QTimer(self)
        self._timer.setInterval(1500)
        self._timer.timeout.connect(self.refresh)
        self._timer.start()
        self.refresh()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        # system info
        self.sys_label = QLabel()
        self.sys_label.setObjectName("Muted")
        self.sys_label.setWordWrap(True)
        layout.addWidget(self.sys_label)

        bar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setObjectName("SearchBox")
        self.search.setPlaceholderText("Search processes…")
        self.search.setClearButtonEnabled(True)
        self.search.textChanged.connect(lambda _t: self._render_table())
        bar.addWidget(self.search, 1)
        refresh = QPushButton("Refresh")
        refresh.clicked.connect(self.refresh)
        bar.addWidget(refresh)
        self.kill_btn = QPushButton("End task…")
        self.kill_btn.setObjectName("DangerButton")
        self.kill_btn.clicked.connect(self.terminate_selected)
        bar.addWidget(self.kill_btn)
        layout.addLayout(bar)

        self.table = QTableWidget(0, len(_COLUMNS))
        self.table.setHorizontalHeaderLabels(_COLUMNS)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.setSortingEnabled(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().sectionClicked.connect(self._on_sort)
        layout.addWidget(self.table, 1)

    def refresh(self) -> None:
        self._update_system_info()
        self._procs = self._collect()
        self._render_table()

    def _update_system_info(self) -> None:
        info = system_info()
        mem_total = _human(info.get("memory_total") or 0)
        mem_avail = _human(info.get("memory_available") or 0)
        self.sys_label.setText(
            f"OS: {info.get('os','')}   ·   CPU: {info.get('cpu_count_physical','?')} physical / "
            f"{info.get('cpu_count_logical','?')} logical   ·   CPU load: {info.get('cpu_percent','?')}%   ·   "
            f"RAM: {mem_total} total, {mem_avail} available   ·   {len(self._procs)} processes   ·   "
            f"Python: {info.get('python','')}"
        )

    def _collect(self) -> list[dict]:
        import psutil  # local import

        procs = []
        for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_info", "status", "io_counters"]):
            try:
                info = p.info
                mem = info.get("memory_info")
                io = info.get("io_counters")
                read = io.read_bytes if io else 0
                write = io.write_bytes if io else 0
                pid = info.get("pid")
                prev = self._last_io.get(pid, (read, write))
                disk_io = (read - prev[0]) + (write - prev[1])
                self._last_io[pid] = (read, write)
                procs.append({
                    "pid": pid,
                    "name": info.get("name") or "",
                    "cpu_percent": info.get("cpu_percent") or 0.0,
                    "memory_bytes": getattr(mem, "rss", 0) if mem else 0,
                    "disk_io": max(0, disk_io),
                    "username": info.get("username") or "",
                    "status": info.get("status") or "",
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                continue
        # prime cpu_percent for next iteration
        return procs

    def _render_table(self) -> None:
        query = self.search.text().strip().lower()
        rows = [p for p in self._procs if not query or query in p["name"].lower() or query in str(p["pid"])]
        key = {0: "pid", 1: "name", 2: "cpu_percent", 3: "memory_bytes", 4: "disk_io", 5: "username", 6: "status"}[self._sort_col]
        rows.sort(key=lambda p: (p[key] or 0), reverse=self._sort_desc)

        self.table.setRowCount(len(rows))
        for r, p in enumerate(rows):
            values = [
                str(p["pid"]),
                p["name"],
                f"{p['cpu_percent']:.1f}",
                _human(p["memory_bytes"]),
                _human(p["disk_io"]),
                p["username"],
                p["status"],
            ]
            for c, val in enumerate(values):
                cell = QTableWidgetItem(val)
                if c == 0:
                    cell.setData(Qt.ItemDataRole.UserRole, p["pid"])
                self.table.setItem(r, c, cell)

    def _on_sort(self, col: int) -> None:
        if self._sort_col == col:
            self._sort_desc = not self._sort_desc
        else:
            self._sort_col = col
            self._sort_desc = True
        self._render_table()

    def terminate_selected(self) -> None:
        rows = self.table.selectionModel().selectedRows()
        if not rows:
            QMessageBox.information(self, "End task", "Select a process first.")
            return
        row = rows[0].row()
        pid_item = self.table.item(row, 0)
        name_item = self.table.item(row, 1)
        if pid_item is None:
            return
        pid = int(pid_item.text())
        name = name_item.text() if name_item else ""
        # safety: never kill self or PID 0/4 (System) or PID 4
        if pid <= 4:
            QMessageBox.warning(self, "End task", "This system process cannot be terminated.")
            return
        answer = QMessageBox.question(
            self, "End task",
            f"Terminate '{name}' (PID {pid})?\n\nUnsaved data in that process may be lost.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if answer != QMessageBox.StandardButton.Yes:
            return
        try:
            import psutil

            proc = psutil.Process(pid)
            proc.terminate()
            try:
                proc.wait(timeout=3)
            except psutil.TimeoutExpired:
                # ask before force kill
                if QMessageBox.question(self, "Force end task",
                                        f"'{name}' did not close. Force terminate?",
                                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                        QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    proc.kill()
            QMessageBox.information(self, "End task", f"Terminated '{name}' (PID {pid}).")
        except psutil.NoSuchProcess:
            QMessageBox.information(self, "End task", "Process already exited.")
        except psutil.AccessDenied:
            QMessageBox.warning(self, "End task", "Access denied. Try running REALM OS as administrator.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "End task", f"Could not terminate process:\n{exc}")
        finally:
            self.refresh()
