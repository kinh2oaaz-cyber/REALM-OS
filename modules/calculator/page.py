"""Calculator with safe expression evaluation (no arbitrary code execution)."""

from __future__ import annotations

import ast
import math
import operator

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ui.components.page import RealmPage

_OPS = {
    ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
    ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv, ast.Mod: operator.mod,
    ast.Pow: operator.pow, ast.USub: operator.neg, ast.UAdd: operator.pos,
}
_FUNCS = {"sqrt": math.sqrt, "sin": math.sin, "cos": math.cos, "tan": math.tan, "log": math.log,
          "log10": math.log10, "exp": math.exp, "abs": abs, "floor": math.floor, "ceil": math.ceil, "round": round}
_CONSTS = {"pi": math.pi, "e": math.e}


def safe_eval(expr: str) -> float:
    """Evaluate a math expression safely (no names/calls beyond whitelist)."""
    node = ast.parse(expr.strip(), mode="eval").body
    return _eval(node)


def _eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.Name):
        if node.id in _CONSTS: return _CONSTS[node.id]
        raise ValueError(f"Unknown name {node.id!r}")
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.left), _eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_eval(node.operand))
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _FUNCS and not node.keywords:
        return _FUNCS[node.func.id](*[_eval(a) for a in node.args])
    raise ValueError("Unsupported expression")


class CalculatorPage(RealmPage):
    page_title = "Calculator"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        title = QLabel("Calculator"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        self.display = QLineEdit(); self.display.setAlignment(Qt.AlignmentFlag.AlignRight); self.display.setStyleSheet("font-size:22px; padding:10px;")
        self.display.returnPressed.connect(self.equals); self.layout_root.addWidget(self.display)
        self.result = QLabel("0"); self.result.setAlignment(Qt.AlignmentFlag.AlignRight); self.result.setObjectName("Muted"); self.layout_root.addWidget(self.result)

        grid = QGridLayout(); grid.setSpacing(8)
        buttons = [
            ["C", "(", ")", "/"], ["7", "8", "9", "*"], ["4", "5", "6", "-"],
            ["1", "2", "3", "+"], ["0", ".", "%", "^"], ["π", "√", "", "="],
        ]
        for r, row in enumerate(buttons):
            for c, label in enumerate(row):
                btn = QPushButton(label); btn.setMinimumHeight(48); btn.setCursor(Qt.CursorShape.PointingHandCursor)
                btn.clicked.connect(lambda _c=False, l=label: self.on_key(l))
                if label == "=": btn.setObjectName("PrimaryButton")
                if label == "C": btn.setObjectName("DangerButton")
                grid.addWidget(btn, r, c)
        self.layout_root.addLayout(grid); self.layout_root.addStretch(1)

    def on_key(self, label: str) -> None:
        if label == "C": self.display.clear(); self.result.setText("0"); return
        if label == "": self.display.setText(self.display.text()[:-1]); return
        if label == "=": self.equals(); return
        if label == "%": self._insert(" /100 "); return
        if label == "^": self._insert("**"); return
        if label == "π": self._insert("pi"); return
        if label == "√": self._insert("sqrt("); return
        self._insert(label)

    def _insert(self, text: str) -> None:
        self.display.setText(self.display.text() + text); self.display.setFocus()

    def equals(self) -> None:
        expr = self.display.text().strip()
        if not expr: return
        try:
            value = safe_eval(expr)
            self.result.setText(_fmt(value))
            self.display.setText(_fmt(value))
        except (ValueError, SyntaxError, ZeroDivisionError, OverflowError) as exc:
            self.result.setText("Error: " + str(exc))


def _fmt(value: float) -> str:
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return f"{value:.10g}"
