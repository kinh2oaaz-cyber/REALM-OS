"""Developer Toolkit: real local utilities."""

from __future__ import annotations

import base64
import hashlib
import json
import re
import urllib.parse
import uuid

from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QPlainTextEdit, QPushButton, QTabWidget, QVBoxLayout, QWidget

from ui.components.page import RealmPage


class _Tool(QWidget):
    def __init__(self, title: str, hint: str, parent=None) -> None:
        super().__init__(parent)
        lay = QVBoxLayout(self); lay.setSpacing(8)
        lay.addWidget(QLabel(title))
        self.input = QPlainTextEdit(); self.input.setPlaceholderText(hint); lay.addWidget(self.input, 1)
        bar = QHBoxLayout(); bar.setSpacing(8); self.bar = bar; lay.addLayout(bar)
        self.output = QPlainTextEdit(); self.output.setReadOnly(True); lay.addWidget(self.output, 1)


class DevToolsPage(RealmPage):
    page_title = "Developer Toolkit"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        title = QLabel("Developer Toolkit"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        tabs = QTabWidget()

        # JSON
        json_tool = _Tool("JSON formatter", "Paste JSON…")
        fmt = QPushButton("Format"); fmt.clicked.connect(lambda: self._json(json_tool)); json_tool.bar.addWidget(fmt)
        mini = QPushButton("Minify"); mini.clicked.connect(lambda: self._json(json_tool, minify=True)); json_tool.bar.addWidget(mini); json_tool.bar.addStretch(1)
        tabs.addTab(json_tool, "JSON")

        # Base64
        b64 = _Tool("Base64", "Enter text…")
        e = QPushButton("Encode"); e.clicked.connect(lambda: self._b64(b64, encode=True)); b64.bar.addWidget(e)
        d = QPushButton("Decode"); d.clicked.connect(lambda: self._b64(b64, encode=False)); b64.bar.addWidget(d); b64.bar.addStretch(1)
        tabs.addTab(b64, "Base64")

        # Hashing
        hash_tool = _Tool("Hashing", "Enter text…")
        self.hash_combo = QComboBox(); self.hash_combo.addItems(["md5", "sha1", "sha256", "sha512"]); hash_tool.bar.addWidget(self.hash_combo)
        hb = QPushButton("Hash"); hb.clicked.connect(lambda: self._hash(hash_tool)); hash_tool.bar.addWidget(hb); hash_tool.bar.addStretch(1)
        tabs.addTab(hash_tool, "Hash")

        # URL
        url = _Tool("URL encode / decode", "Enter text…")
        ue = QPushButton("Encode"); ue.clicked.connect(lambda: self._url(url, True)); url.bar.addWidget(ue)
        ud = QPushButton("Decode"); ud.clicked.connect(lambda: self._url(url, False)); url.bar.addWidget(ud); url.bar.addStretch(1)
        tabs.addTab(url, "URL")

        # UUID
        u = _Tool("UUID", "")
        gen = QPushButton("Generate UUID4"); gen.clicked.connect(lambda: u.output.setPlainText(str(uuid.uuid4()))); u.bar.addWidget(gen); u.bar.addStretch(1)
        u.input.hide(); tabs.addTab(u, "UUID")

        # Regex
        rx = _Tool("Regex tester", "Pattern (first line), test text (rest)…")
        rxb = QPushButton("Test"); rxb.clicked.connect(lambda: self._regex(rx)); rx.bar.addWidget(rxb); rx.bar.addStretch(1)
        tabs.addTab(rx, "Regex")

        self.layout_root.addWidget(tabs, 1)

    def _json(self, tool: _Tool, minify: bool = False) -> None:
        try:
            data = json.loads(tool.input.toPlainText())
            tool.output.setPlainText(json.dumps(data, indent=None if minify else 2, ensure_ascii=False))
        except json.JSONDecodeError as exc:
            tool.output.setPlainText(f"Invalid JSON: {exc}")

    def _b64(self, tool: _Tool, encode: bool) -> None:
        try:
            if encode:
                tool.output.setPlainText(base64.b64encode(tool.input.toPlainText().encode()).decode())
            else:
                tool.output.setPlainText(base64.b64decode(tool.input.toPlainText().strip().encode()).decode("utf-8", errors="replace"))
        except Exception as exc:  # noqa: BLE001
            tool.output.setPlainText(f"Error: {exc}")

    def _hash(self, tool: _Tool) -> None:
        data = tool.input.toPlainText().encode("utf-8")
        algo = self.hash_combo.currentText()
        tool.output.setPlainText(hashlib.new(algo, data).hexdigest())

    def _url(self, tool: _Tool, encode: bool) -> None:
        text = tool.input.toPlainText()
        tool.output.setPlainText(urllib.parse.quote(text, safe="") if encode else urllib.parse.unquote(text))

    def _regex(self, tool: _Tool) -> None:
        raw = tool.input.toPlainText().split("\n")
        pattern = raw[0] if raw else ""
        test = "\n".join(raw[1:]) if len(raw) > 1 else ""
        try:
            matches = list(re.finditer(pattern, test))
            out = [f"{len(matches)} match(es)"] + [f"  {m.span()} {m.group(0)!r}" for m in matches[:50]]
            tool.output.setPlainText("\n".join(out))
        except re.error as exc:
            tool.output.setPlainText(f"Regex error: {exc}")
