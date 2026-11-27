"""REALM AI assistant.

Honest design: connects to a *local* model provider (Ollama at
127.0.0.1:11434) if one is running. No fake responses. If no local
model is available, it says so. REALM OS itself stays local-first and
offline; this feature only works when a local model is present.
"""

from __future__ import annotations

import json
import urllib.request

from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QPushButton, QVBoxLayout

from ui.components.page import RealmPage

_OLLAMA = "http://127.0.0.1:11434"


def ollama_available(timeout: float = 1.5) -> bool:
    try:
        with urllib.request.urlopen(_OLLAMA + "/api/tags", timeout=timeout) as resp:  # noqa: S310
            return resp.status == 200
    except Exception:  # noqa: BLE001
        return False


def ollama_models(timeout: float = 2.0) -> list[str]:
    try:
        with urllib.request.urlopen(_OLLAMA + "/api/tags", timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8"))
        return [m.get("name", "") for m in data.get("models", [])]
    except Exception:  # noqa: BLE001
        return []


def ollama_chat(model: str, prompt: str, timeout: float = 120.0) -> str | None:
    """Return model reply or None on failure. No fabricated output."""
    try:
        body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode("utf-8")
        req = urllib.request.Request(_OLLAMA + "/api/generate", data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("response")
    except Exception:  # noqa: BLE001
        return None


class AIPage(RealmPage):
    page_title = "REALM AI"

    def __init__(self, context, parent=None) -> None:
        self._models: list[str] = []
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        header = QHBoxLayout(); title = QLabel("REALM AI"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        refresh = QPushButton("Check local model"); refresh.clicked.connect(self.refresh_models); header.addWidget(refresh); self.layout_root.addLayout(header)

        self.status = QLabel(); self.status.setObjectName("Muted"); self.status.setWordWrap(True); self.layout_root.addWidget(self.status)
        self.chat = QListWidget(); self.layout_root.addWidget(self.chat, 1)

        row = QHBoxLayout()
        self.input = QLineEdit(); self.input.setPlaceholderText("Ask REALM AI…"); self.input.returnPressed.connect(self.send); row.addWidget(self.input, 1)
        send = QPushButton("Send"); send.setObjectName("PrimaryButton"); send.clicked.connect(self.send); row.addWidget(send); self.layout_root.addLayout(row)
        self.refresh_models()

    def refresh_models(self) -> None:
        self._models = ollama_models()
        if self._models:
            self.status.setText("Local model available: " + ", ".join(self._models))
        else:
            self.status.setText(
                "No local model available. REALM AI requires a local model provider (e.g. Ollama running at "
                "127.0.0.1:11434 with a model pulled). It never fabricates answers, and nothing is sent to the cloud.")

    def send(self) -> None:
        text = self.input.text().strip()
        if not text: return
        self.chat.addItem("You: " + text); self.input.clear()
        if not self._models:
            self.chat.addItem("REALM AI: (no local model available — see status above)")
            return
        model = self._models[0]
        self.chat.addItem("REALM AI: …")
        reply = ollama_chat(model, text)
        # replace placeholder
        if self.chat.count():
            self.chat.takeItem(self.chat.count() - 1)
        self.chat.addItem("REALM AI: " + (reply if reply else "(no response from local model)"))

    def on_show(self) -> None:
        self.refresh_models()
