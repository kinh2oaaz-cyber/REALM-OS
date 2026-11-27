"""PDF Reader using Qt PDF."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtPdf import QPdfDocument
from PySide6.QtPdfWidgets import QPdfView
from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from ui.components.page import RealmPage
from ui.icons import icon as _icon


class PdfPage(RealmPage):
    page_title = "PDF Reader"

    def __init__(self, context, parent=None) -> None:
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("PDF Reader"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        open_btn = QPushButton("Open PDF"); open_btn.setObjectName("PrimaryButton"); open_btn.setIcon(_icon("folder-open", size=18)); open_btn.clicked.connect(self.open_pdf); header.addWidget(open_btn)
        zoom_in = QPushButton(); zoom_in.setIcon(_icon("plus", size=18)); zoom_in.clicked.connect(lambda: self.zoom(1.25)); header.addWidget(zoom_in)
        zoom_out = QPushButton(); zoom_out.setIcon(_icon("minus", size=18)); zoom_out.clicked.connect(lambda: self.zoom(0.8)); header.addWidget(zoom_out)
        self.page_label = QLabel(""); self.page_label.setObjectName("Muted"); header.addWidget(self.page_label)
        self.layout_root.addLayout(header)

        self.doc = QPdfDocument(self)
        self.view = QPdfView()
        self.view.setDocument(self.doc)
        self.view.setPageMode(QPdfView.PageMode.MultiPage)
        self.layout_root.addWidget(self.view, 1)

        self.doc.statusChanged.connect(self._on_status)

    def open_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF (*.pdf)")
        if not path: return
        self.doc.load(path)

    def zoom(self, factor: float) -> None:
        self.view.setZoomFactor(self.view.zoomFactor() * factor)

    def _on_status(self, status) -> None:  # noqa: ANN001
        if status == QPdfDocument.Status.Ready:
            self.page_label.setText(f"{self.doc.pageCount()} pages")
