"""PDF Reader registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import PdfPage

APP_ID = "pdf"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="PDF Reader", description="Read PDF documents",
        icon="file-type-pdf", category="extra", order=207, keywords=("pdf", "document", "reader"),
        page_factory=lambda c: PdfPage(c),
    ))