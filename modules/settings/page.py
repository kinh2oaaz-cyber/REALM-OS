"""Settings page (Phase 8).

Global light/dark themes, accent color, fonts, startup behavior,
notifications, data management (backup & restore), application
integrations, keyboard shortcuts, privacy & permissions, About.
Everything real and persisted in the shared SQLite database.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QCheckBox,
    QColorDialog,
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from core.config import APP_NAME, APP_VERSION, data_dir, database_path, logs_dir
from ui.components.cards import Card, heading, muted
from ui.components.page import RealmPage
from ui.themes import ACCENT_PRESETS
from ui.themes.theme_manager import THEME_DARK, THEME_LIGHT, THEME_REDGOLD, THEME_SYSTEM

_FONTS = ["Segoe UI", "Segoe UI Variable", "Calibri", "Arial", "Georgia", "Consolas", "Tahoma"]

_SHORTCUTS = [
    ("Ctrl+F", "Global search"), ("Ctrl+D", "Toggle dark / light"),
    ("Ctrl+,", "Open Settings"), ("Ctrl+1", "Go to Home"), ("F5", "Refresh current page"),
]

_INTEGRATIONS = [
    ("notes.markdown", "Markdown editing in Notes"),
    ("gaming.detect", "Best-effort installed-game detection"),
    ("media.local", "Local media library"),
    ("integrations.spotify", "Spotify (optional, not assumed)"),
    ("integrations.game_launchers", "Steam / Epic / GOG detection (optional)"),
]


class SettingsPage(RealmPage):
    page_title = "Settings"

    def build_ui(self) -> None:
        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget(); col = QVBoxLayout(content); col.setContentsMargins(0, 0, 0, 0); col.setSpacing(18)
        scroll.setWidget(content); self.layout_root.addWidget(scroll)

        col.addWidget(heading("Settings", "SectionTitle"))
        col.addWidget(self._appearance_card())
        col.addWidget(self._startup_card())
        col.addWidget(self._notifications_card())
        col.addWidget(self._data_card())
        col.addWidget(self._integrations_card())
        col.addWidget(self._shortcuts_card())
        col.addWidget(self._privacy_card())
        col.addWidget(self._about_card())
        col.addStretch(1)

    # -- Appearance -----------------------------------------------------
    def _appearance_card(self) -> Card:
        theme = self.context.theme
        card = Card("Appearance")
        row = QHBoxLayout(); row.addWidget(QLabel("Theme"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItem("Red & Gold (blur)", THEME_REDGOLD); self.theme_combo.addItem("System", THEME_SYSTEM); self.theme_combo.addItem("Light", THEME_LIGHT); self.theme_combo.addItem("Dark", THEME_DARK)
        self.theme_combo.setCurrentIndex(max(0, self.theme_combo.findData(theme.mode())))
        self.theme_combo.currentIndexChanged.connect(self._on_theme_mode); row.addWidget(self.theme_combo, 1); card.add_layout(row)

        card.add_widget(QLabel("Accent color"))
        swatches = QHBoxLayout(); swatches.setSpacing(8)
        for name, hex_color in ACCENT_PRESETS:
            btn = QPushButton(); btn.setFixedSize(28, 28); btn.setToolTip(name); btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setStyleSheet(f"QPushButton {{ background:{hex_color}; border:1px solid rgba(0,0,0,0.15); border-radius:14px; }} QPushButton:hover {{ border:2px solid {hex_color}; }}")
            btn.clicked.connect(lambda _c=False, h=hex_color: self._set_accent(h)); swatches.addWidget(btn)
        swatches.addStretch(1)
        custom = QPushButton("Custom…"); custom.clicked.connect(self._pick_accent); swatches.addWidget(custom); card.add_layout(swatches)
        self.accent_preview = QLabel(); self.accent_preview.setFixedHeight(10); self.accent_preview.setMaximumWidth(240); self.accent_preview.setStyleSheet(f"background:{theme.accent()}; border-radius:5px;"); card.add_widget(self.accent_preview)

        font_row = QHBoxLayout(); font_row.addWidget(QLabel("Font")); self.font_combo = QComboBox(); self.font_combo.addItems(_FONTS); self.font_combo.setEditable(True)
        self.font_combo.setCurrentText(theme.font_family()); self.font_combo.currentTextChanged.connect(theme.set_font_family); font_row.addWidget(self.font_combo, 1); card.add_layout(font_row)
        size_row = QHBoxLayout(); size_row.addWidget(QLabel("Interface size")); self.size_spin = QSpinBox(); self.size_spin.setRange(9, 28); self.size_spin.setValue(theme.font_size()); self.size_spin.valueChanged.connect(theme.set_font_size); size_row.addWidget(self.size_spin, 1); card.add_layout(size_row)
        reset = QPushButton("Reset appearance"); reset.setObjectName("DangerButton"); reset.clicked.connect(self._reset_appearance); card.add_widget(reset)
        return card

    def _on_theme_mode(self, _i: int) -> None: self.context.theme.set_mode(str(self.theme_combo.currentData()))
    def _set_accent(self, h: str) -> None:
        self.context.theme.set_accent(h); self.accent_preview.setStyleSheet(f"background:{h}; border-radius:5px;")
    def _pick_accent(self) -> None:
        c = QColorDialog.getColor(QColor(self.context.theme.accent()), self, "Choose accent color")
        if c.isValid(): self._set_accent(c.name())

    # -- Startup --------------------------------------------------------
    def _startup_card(self) -> Card:
        s = self.context.settings; card = Card("Startup behavior")
        cb1 = QCheckBox("Reopen last opened application on startup"); cb1.setChecked(s.get_bool("startup.open_last", False)); cb1.toggled.connect(lambda v: s.set("startup.open_last", v)); card.add_widget(cb1)
        cb2 = QCheckBox("Start hidden to system tray"); cb2.setChecked(s.get_bool("startup.start_hidden", False)); cb2.toggled.connect(lambda v: s.set("startup.start_hidden", v)); card.add_widget(cb2)
        card.add_widget(muted("Start with Windows integration is available for packaged builds."))
        return card

    # -- Notifications --------------------------------------------------
    def _notifications_card(self) -> Card:
        s = self.context.settings; card = Card("Notifications")
        en = QCheckBox("Enable notifications"); en.setChecked(s.get_bool("notifications.enabled", True)); en.toggled.connect(lambda v: s.set("notifications.enabled", v)); card.add_widget(en)
        rem = QCheckBox("Calendar reminders"); rem.setChecked(s.get_bool("notifications.calendar_reminders", True)); rem.toggled.connect(lambda v: s.set("notifications.calendar_reminders", v)); card.add_widget(rem)
        clear = QPushButton("Clear all notifications"); clear.clicked.connect(lambda: (self.context.notifications.clear(), QMessageBox.information(self, "Notifications", "Cleared."))); card.add_widget(clear)
        return card

    # -- Data -----------------------------------------------------------
    def _data_card(self) -> Card:
        card = Card("Data management")
        card.add_widget(muted(f"Database: {database_path()}"))
        card.add_widget(muted(f"Data folder: {data_dir()}"))
        card.add_widget(muted(f"Logs: {logs_dir()}"))
        open_btn = QPushButton("Open data folder"); open_btn.clicked.connect(self._open_data_folder); card.add_widget(open_btn)
        backup_btn = QPushButton("Back up database…"); backup_btn.clicked.connect(self._backup_db); card.add_widget(backup_btn)
        restore_btn = QPushButton("Restore database…"); restore_btn.setObjectName("DangerButton"); restore_btn.clicked.connect(self._restore_db); card.add_widget(restore_btn)
        return card

    def _open_data_folder(self) -> None:
        from ui.components.quick_actions import _open_path
        _open_path(data_dir())

    def _backup_db(self) -> None:
        suggested = str(database_path().with_suffix(".backup.db"))
        dest, _ = QFileDialog.getSaveFileName(self, "Back up database", suggested, "SQLite DB (*.db)")
        if not dest: return
        try:
            self.context.db.backup(dest); QMessageBox.information(self, "Backup", f"Backup saved to:\n{dest}")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Backup failed", str(exc))

    def _restore_db(self) -> None:
        src, _ = QFileDialog.getOpenFileName(self, "Restore database", "", "SQLite DB (*.db);;All files (*)")
        if not src: return
        if QMessageBox.question(self, "Restore database",
                                "Restore will replace your current database with the backup.\n\n"
                                "A copy of the current database will be saved first. Continue?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
            return
        try:
            db_path = database_path()
            self.context.db.close()
            if db_path.exists():
                shutil.copy2(db_path, db_path.with_suffix(".pre-restore.db"))
            shutil.copy2(src, db_path)
            # reopen
            from database import Database
            self.context.db = Database(db_path)
            self.context.db.initialize()
            QMessageBox.information(self, "Restore", "Database restored. Please restart REALM OS to reload all data.")
        except Exception as exc:  # noqa: BLE001
            QMessageBox.warning(self, "Restore failed", str(exc))

    def _reset_appearance(self) -> None:
        if QMessageBox.question(self, "Reset appearance", "Reset theme, accent and fonts to defaults?") != QMessageBox.StandardButton.Yes: return
        for key in ("appearance.theme", "appearance.accent", "appearance.font_family", "appearance.font_size"):
            self.context.settings.remove(key)
        self.context.theme.apply(); QMessageBox.information(self, "Reset", "Appearance reset. Reopen Settings to refresh controls.")

    # -- Integrations ---------------------------------------------------
    def _integrations_card(self) -> Card:
        s = self.context.settings; card = Card("Application integrations")
        for key, label in _INTEGRATIONS:
            cb = QCheckBox(label); cb.setChecked(s.get_bool(key, key in ("notes.markdown", "gaming.detect", "media.local")))
            cb.toggled.connect(lambda v, k=key: s.set(k, v)); card.add_widget(cb)
        card.add_widget(muted("External services are optional and never assumed; REALM OS works fully offline."))
        return card

    # -- Shortcuts ------------------------------------------------------
    def _shortcuts_card(self) -> Card:
        card = Card("Keyboard shortcuts")
        for keys, desc in _SHORTCUTS:
            row = QHBoxLayout(); k = QLabel(keys); k.setStyleSheet("font-family: Consolas, monospace; font-weight:600;"); row.addWidget(k); row.addStretch(1); row.addWidget(QLabel(desc)); card.add_layout(row)
        return card

    # -- Privacy --------------------------------------------------------
    def _privacy_card(self) -> Card:
        s = self.context.settings; card = Card("Privacy & permissions")
        tel = QCheckBox("Send anonymous telemetry"); tel.setChecked(s.get_bool("privacy.telemetry", False)); tel.toggled.connect(lambda v: s.set("privacy.telemetry", v)); card.add_widget(tel)
        card.add_widget(muted("REALM OS is local-first. No telemetry is sent; nothing leaves your machine unless a feature explicitly needs the network (e.g. Network Monitor checks, Weather)."))
        card.add_widget(muted("Normal Windows permissions apply. File changes always require confirmation. No process is terminated without confirmation."))
        return card

    # -- About ----------------------------------------------------------
    def _about_card(self) -> Card:
        card = Card("About REALM OS")
        card.add_widget(QLabel(f"{APP_NAME}  ·  version {APP_VERSION}"))
        card.add_widget(muted("A premium, interconnected personal desktop ecosystem. Local-first; no internet required."))
        card.add_widget(muted("Powered by Python 3.14, PySide6 (Qt 6), SQLite, psutil, cryptography."))
        card.add_widget(muted("Not a replacement for Windows. Not a sci-fi dashboard."))
        return card

    def on_show(self) -> None:
        self.accent_preview.setStyleSheet(f"background:{self.context.theme.accent()}; border-radius:5px;")
