"""Read-only system information via psutil. Never mutates system state."""

from __future__ import annotations

import platform
import sys
from typing import Any

try:
    import psutil
except ImportError:  # pragma: no cover - psutil is a hard dependency
    psutil = None  # type: ignore[assignment]


def python_version() -> str:
    return sys.version.split()[0]


def os_description() -> str:
    return f"{platform.system()} {platform.release()} ({platform.version()})"


def system_info() -> dict[str, Any]:
    """A snapshot of CPU/memory/disk basics for display."""
    info: dict[str, Any] = {
        "os": os_description(),
        "python": python_version(),
        "cpu_count_logical": None,
        "cpu_count_physical": None,
        "cpu_percent": None,
        "memory_total": None,
        "memory_available": None,
        "memory_percent": None,
    }
    if psutil is None:
        return info
    try:
        info["cpu_count_logical"] = psutil.cpu_count(logical=True)
        info["cpu_count_physical"] = psutil.cpu_count(logical=False)
        info["cpu_percent"] = psutil.cpu_percent(interval=None)
        vm = psutil.virtual_memory()
        info["memory_total"] = vm.total
        info["memory_available"] = vm.available
        info["memory_percent"] = vm.percent
    except Exception:  # noqa: BLE001
        pass
    return info


def list_processes(limit: int | None = None) -> list[dict[str, Any]]:
    """Snapshot of running processes (read-only)."""
    if psutil is None:
        return []
    procs: list[dict[str, Any]] = []
    for p in psutil.process_iter(["pid", "name", "username", "cpu_percent", "memory_info", "status"]):
        try:
            info = p.info
            mem = info.get("memory_info")
            procs.append(
                {
                    "pid": info.get("pid"),
                    "name": info.get("name") or "",
                    "username": info.get("username") or "",
                    "cpu_percent": info.get("cpu_percent") or 0.0,
                    "memory_bytes": getattr(mem, "rss", 0) if mem else 0,
                    "status": info.get("status") or "",
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    procs.sort(key=lambda p: p["cpu_percent"], reverse=True)
    if limit is not None:
        return procs[:limit]
    return procs
