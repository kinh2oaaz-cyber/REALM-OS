"""File Manager service: browsing, search, metadata, safe file operations,
storage overview, recents, favorites. Never modifies without caller confirmation
(confirmation is enforced in the UI). Normal Windows permissions apply."""

from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.context import AppContext

from .models import FileInfo

TEXT_EXTENSIONS = {".txt", ".md", ".py", ".js", ".ts", ".json", ".xml", ".html", ".css", ".csv", ".log", ".ini", ".cfg", ".yaml", ".yml", ".sql", ".sh", ".ps1", ".bat", ".c", ".h", ".cpp", ".java", ".rs", ".go"}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp", ".svg", ".ico"}


def _ts(ts: float) -> str:
    try:
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError, OverflowError):
        return ""


class FileService:
    def __init__(self, ctx: "AppContext | None" = None) -> None:
        self.ctx = ctx

    # -- drives ---------------------------------------------------------
    def drives(self) -> list[dict]:
        out = []
        if os.name == "nt":
            import string

            for letter in string.ascii_uppercase:
                root = f"{letter}:\\"
                if os.path.exists(root):
                    try:
                        usage = shutil.disk_usage(root)
                        out.append({"path": root, "name": root, "total": usage.total, "used": usage.used, "free": usage.free})
                    except OSError:
                        out.append({"path": root, "name": root, "total": 0, "used": 0, "free": 0})
        else:
            usage = shutil.disk_usage("/")
            out.append({"path": "/", "name": "/", "total": usage.total, "used": usage.used, "free": usage.free})
        return out

    def storage_overview(self, path: str) -> dict:
        usage = shutil.disk_usage(path if os.path.exists(path) else os.sep)
        return {"total": usage.total, "used": usage.used, "free": usage.free,
                "used_percent": round(usage.used / usage.total * 100, 1) if usage.total else 0}

    # -- listing --------------------------------------------------------
    def list_dir(self, path: str, sort_by: str = "name", ascending: bool = True,
                 filter_text: str = "", show_hidden: bool = False) -> list[FileInfo]:
        p = Path(path)
        items: list[FileInfo] = []
        try:
            entries = list(p.iterdir())
        except (PermissionError, OSError):
            return []
        for entry in entries:
            try:
                name = entry.name
                hidden = name.startswith(".") or _is_windows_hidden(entry)
                if hidden and not show_hidden:
                    continue
                if filter_text and filter_text.lower() not in name.lower():
                    continue
                stat = entry.stat()
                is_dir = entry.is_dir()
                items.append(FileInfo(
                    path=str(entry), name=name, is_dir=is_dir,
                    size=0 if is_dir else stat.st_size,
                    modified=_ts(stat.st_mtime), created=_ts(stat.st_ctime),
                    extension=entry.suffix.lower(), is_hidden=hidden,
                ))
            except (PermissionError, OSError):
                continue
        key = {
            "name": lambda f: (not f.is_dir, f.name.lower()),
            "size": lambda f: (not f.is_dir, f.size),
            "modified": lambda f: (not f.is_dir, f.modified),
            "type": lambda f: (not f.is_dir, f.extension, f.name.lower()),
        }.get(sort_by, lambda f: (not f.is_dir, f.name.lower()))
        items.sort(key=key, reverse=not ascending)
        # directories first regardless
        items.sort(key=lambda f: not f.is_dir)
        return items

    def metadata(self, path: str) -> dict:
        p = Path(path)
        stat = p.stat()
        return {
            "name": p.name, "path": str(p), "is_dir": p.is_dir(),
            "size": 0 if p.is_dir() else stat.st_size,
            "modified": _ts(stat.st_mtime), "created": _ts(stat.st_ctime),
            "extension": p.suffix.lower(), "parent": str(p.parent),
            "readonly": not os.access(path, os.W_OK),
        }

    def is_text(self, path: str) -> bool:
        return Path(path).suffix.lower() in TEXT_EXTENSIONS

    def is_image(self, path: str) -> bool:
        return Path(path).suffix.lower() in IMAGE_EXTENSIONS

    def read_text_preview(self, path: str, max_chars: int = 20000) -> str:
        try:
            return Path(path).read_text(encoding="utf-8", errors="replace")[:max_chars]
        except (PermissionError, OSError) as exc:
            return f"[Cannot read: {exc}]"

    # -- safe operations (caller must confirm; we re-check targets) ------
    def copy(self, src: str, dst_dir: str) -> str:
        src_p = Path(src); dst = Path(dst_dir) / src_p.name
        dst = _unique(dst)
        if src_p.is_dir():
            shutil.copytree(src_p, dst)
        else:
            shutil.copy2(src_p, dst)
        return str(dst)

    def move(self, src: str, dst_dir: str) -> str:
        src_p = Path(src); dst = Path(dst_dir) / src_p.name
        if dst.exists():
            dst = _unique(dst)
        shutil.move(str(src_p), str(dst))
        return str(dst)

    def rename(self, src: str, new_name: str) -> str:
        src_p = Path(src); dst = src_p.with_name(new_name)
        if dst.exists():
            raise FileExistsError(f"{new_name} already exists")
        src_p.rename(dst)
        return str(dst)

    def delete(self, path: str) -> None:
        p = Path(path)
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()

    def create_folder(self, parent: str, name: str) -> str:
        target = Path(parent) / name
        target.mkdir(parents=True, exist_ok=False)
        return str(target)

    # -- recents / favorites (persisted) --------------------------------
    def record_recent(self, path: str) -> None:
        if self.ctx is None:
            return
        self.ctx.db.execute(
            "INSERT INTO recent_files (path, opened_at) VALUES (?, datetime('now')) "
            "ON CONFLICT(path) DO UPDATE SET opened_at=excluded.opened_at", (path,))

    def recents(self, limit: int = 20) -> list[str]:
        if self.ctx is None:
            return []
        return [r["path"] for r in self.ctx.db.query("SELECT path FROM recent_files ORDER BY opened_at DESC LIMIT ?", (limit,))]

    def add_favorite(self, path: str) -> None:
        if self.ctx is None:
            return
        self.ctx.db.execute("INSERT OR IGNORE INTO favorite_files (path, added_at) VALUES (?, datetime('now'))", (path,))

    def remove_favorite(self, path: str) -> None:
        if self.ctx is None:
            return
        self.ctx.db.execute("DELETE FROM favorite_files WHERE path=?", (path,))

    def favorites(self) -> list[str]:
        if self.ctx is None:
            return []
        return [r["path"] for r in self.ctx.db.query("SELECT path FROM favorite_files ORDER BY added_at DESC")]

    def is_favorite(self, path: str) -> bool:
        if self.ctx is None:
            return False
        return self.ctx.db.query_one("SELECT 1 FROM favorite_files WHERE path=?", (path,)) is not None

    # -- search ---------------------------------------------------------
    def search(self, root: str, query: str, limit: int = 200) -> list[FileInfo]:
        query_l = query.lower()
        results: list[FileInfo] = []
        root_p = Path(root)
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if not d.startswith(".") and not d.startswith("$")]
            for name in filenames:
                if query_l in name.lower():
                    try:
                        p = Path(dirpath) / name
                        st = p.stat()
                        results.append(FileInfo(str(p), name, False, st.st_size, _ts(st.st_mtime), _ts(st.st_ctime), p.suffix.lower(), name.startswith(".")))
                    except (PermissionError, OSError):
                        continue
                if len(results) >= limit:
                    return results
        return results


def _unique(path: Path) -> Path:
    if not path.exists():
        return path
    stem, suffix, parent = path.stem, path.suffix, path.parent
    i = 1
    while (parent / f"{stem} ({i}){suffix}").exists():
        i += 1
    return parent / f"{stem} ({i}){suffix}"


def _is_windows_hidden(path: Path) -> bool:
    if os.name != "nt":
        return False
    try:
        attrs = os.stat(path).st_file_attributes  # type: ignore[attr-defined]
        return bool(attrs & 2)  # FILE_ATTRIBUTE_HIDDEN
    except (AttributeError, OSError):
        return False
