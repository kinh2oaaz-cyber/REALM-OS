"""Personal Finance Tracker: income/expense, categories, balances."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QDoubleSpinBox, QFormLayout, QFrame, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem,
    QMessageBox, QPushButton, QVBoxLayout, QWidget,
)

from ui.components.page import RealmPage


class FinancePage(RealmPage):
    page_title = "Finance"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        title = QLabel("Personal Finance"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)

        self.summary = QLabel(); self.summary.setStyleSheet("font-size:15px; font-weight:600;"); self.layout_root.addWidget(self.summary)

        # add transaction
        form = QFrame(); form.setObjectName("Card"); fl = QHBoxLayout(form); fl.setSpacing(8)
        self.kind_combo = QComboBox(); self.kind_combo.addItems(["expense", "income"]); fl.addWidget(self.kind_combo)
        self.amount = QDoubleSpinBox(); self.amount.setRange(0, 1e9); self.amount.setDecimals(2); self.amount.setPrefix("$ "); fl.addWidget(self.amount)
        self.category = QLineEdit(); self.category.setPlaceholderText("Category"); fl.addWidget(self.category, 1)
        self.note = QLineEdit(); self.note.setPlaceholderText("Note"); fl.addWidget(self.note, 1)
        add = QPushButton("Add"); add.setObjectName("PrimaryButton"); add.clicked.connect(self.add_transaction); fl.addWidget(add)
        self.layout_root.addWidget(form)

        self.list = QListWidget(); self.layout_root.addWidget(self.list, 1)
        self.refresh()

    def add_transaction(self) -> None:
        amount = self.amount.value()
        if amount <= 0: QMessageBox.warning(self, "Finance", "Enter an amount."); return
        self.context.db.execute(
            "INSERT INTO finance_transactions (kind, amount, category, note) VALUES (?, ?, ?, ?)",
            (self.kind_combo.currentText(), amount, self.category.text().strip(), self.note.text().strip()))
        self.amount.setValue(0); self.category.clear(); self.note.clear(); self.refresh()

    def refresh(self) -> None:
        rows = self.context.db.query("SELECT * FROM finance_transactions ORDER BY date DESC, id DESC")
        income = sum(r["amount"] for r in rows if r["kind"] == "income")
        expense = sum(r["amount"] for r in rows if r["kind"] == "expense")
        balance = income - expense
        self.summary.setText(f"Balance ${balance:,.2f}    ·    Income ${income:,.2f}    ·    Expenses ${expense:,.2f}")
        self.list.clear()
        for r in rows:
            sign = "+" if r["kind"] == "income" else "-"
            item = QListWidgetItem(f"{r['date']}  {sign}${r['amount']:,.2f}  {r['category']}  {r['note']}")
            self.list.addItem(item)

    def on_show(self) -> None:
        self.refresh()
