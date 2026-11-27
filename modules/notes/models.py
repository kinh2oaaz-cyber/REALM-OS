"""Notes data model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

FORMATS = ("markdown", "richtext", "plain")


@dataclass
class Note:
    id: int | None = None
    title: str = "Untitled"
    content: str = ""
    format: str = "markdown"
    folder: str = ""
    category: str = ""
    pinned: bool = False
    protected: bool = False
    word_count: int = 0
    char_count: int = 0
    created_at: str | None = None
    updated_at: str | None = None
    last_accessed_at: str | None = None

    @classmethod
    def from_row(cls, row: dict[str, Any]) -> "Note":
        return cls(
            id=row.get("id"),
            title=row.get("title", "Untitled"),
            content=row.get("content", ""),
            format=row.get("format", "markdown"),
            folder=row.get("folder", ""),
            category=row.get("category", ""),
            pinned=bool(row.get("pinned", 0)),
            protected=bool(row.get("protected", 0)),
            word_count=int(row.get("word_count", 0)),
            char_count=int(row.get("char_count", 0)),
            created_at=row.get("created_at"),
            updated_at=row.get("updated_at"),
            last_accessed_at=row.get("last_accessed_at"),
        )


def count_words(text: str) -> int:
    return len([w for w in text.split() if w.strip()])


def count_chars(text: str) -> int:
    return len(text)
