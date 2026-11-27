"""File metadata model."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class FileInfo:
    path: str
    name: str
    is_dir: bool
    size: int
    modified: str
    created: str
    extension: str
    is_hidden: bool
