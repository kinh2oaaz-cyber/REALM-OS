"""Gaming Hub page."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.cards import EmptyState
from ui.components.page import RealmPage
from ui.icons import icon as _icon

from .models import Game
from .services import GamingService


def _fmt_playtime(seconds: int) -> str:
    h = seconds // 3600; m = (seconds % 3600) // 60
    return f"{h}h {m}m"


class GamingPage(RealmPage):
    page_title = "Gaming"

    def __init__(self, context, parent=None) -> None:
        self.service = GamingService(context)
        self._filter = "All"
        super().__init__(context, parent)
        self.service.tracker.finished.connect(self._on_session_finished)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel("Gaming Hub"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        add = QPushButton("Add Game"); add.setObjectName("PrimaryButton"); add.setIcon(_icon("plus", size=18)); add.clicked.connect(self.add_game); header.addWidget(add)
        detect = QPushButton("Detect installed"); detect.clicked.connect(self.detect_installed); header.addWidget(detect)
        self.layout_root.addLayout(header)

        self.stats_label = QLabel(); self.stats_label.setObjectName("Muted"); self.layout_root.addWidget(self.stats_label)

        bar = QHBoxLayout()
        self.search = QLineEdit(); self.search.setObjectName("SearchBox"); self.search.setPlaceholderText("Search games…")
        self.search.setClearButtonEnabled(True); self.search.textChanged.connect(lambda _t: self.refresh()); bar.addWidget(self.search, 1)
        self.filter_combo = QComboBox(); self.filter_combo.addItems(["All", "Favorites", "Recently Played"]); self.filter_combo.currentTextChanged.connect(self._set_filter); bar.addWidget(self.filter_combo)
        self.layout_root.addLayout(bar)

        self.scroll = QScrollArea(); self.scroll.setWidgetResizable(True); self.scroll.setFrameShape(QFrame.Shape.NoFrame)
        self.grid_holder = QWidget(); self.grid_layout = QVBoxLayout(self.grid_holder); self.grid_layout.setSpacing(10)
        self.scroll.setWidget(self.grid_holder); self.layout_root.addWidget(self.scroll, 1)
        self.refresh()

    def _set_filter(self, text: str) -> None:
        self._filter = text; self.refresh()

    def refresh(self) -> None:
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            w = item.widget()
            if w: w.deleteLater()
        stats = self.service.stats()
        self.stats_label.setText(
            f"{stats['games']} games · {stats['favorites']} favorites · "
            f"{_fmt_playtime(stats['total_playtime_seconds'])} total · {stats['sessions']} sessions · {stats['categories']} categories")

        query = self.search.text().strip().lower()
        if self._filter == "Favorites":
            games = self.service.repo.favorites()
        elif self._filter == "Recently Played":
            games = self.service.repo.recently_played()
        else:
            games = self.service.repo.list_all()
        if query:
            games = [g for g in games if query in g.name.lower() or query in g.category.lower()]
        if not games:
            empty = EmptyState(
                _icon("device-gamepad-2", color="#D6AD55", size=42),
                "Your library is empty",
                "Add a game manually or let REALM OS detect titles already installed on this PC.",
            )
            add = QPushButton("Add game"); add.setObjectName("PrimaryButton"); add.clicked.connect(self.add_game)
            detect = QPushButton("Detect installed"); detect.clicked.connect(self.detect_installed)
            empty.add_action(add); empty.add_action(detect)
            self.grid_layout.addWidget(empty)
            self.grid_layout.addStretch(1); return
        for game in games:
            self.grid_layout.addWidget(self._game_card(game))
        self.grid_layout.addStretch(1)

    def _game_card(self, game: Game) -> QWidget:
        card = QFrame(); card.setObjectName("Card")
        lay = QHBoxLayout(card); lay.setContentsMargins(12, 12, 12, 12); lay.setSpacing(14)

        # cover
        cover = QLabel(); cover.setFixedSize(72, 96); cover.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cover.setObjectName("Card")
        if game.cover_path:
            pix = QPixmap(game.cover_path)
            if not pix.isNull():
                cover.setPixmap(pix.scaled(72, 96, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation))
        else:
            cover.setText("")
        lay.addWidget(cover)

        info = QVBoxLayout(); info.setSpacing(3)
        name = QLabel(game.name); name.setStyleSheet("font-weight:700; font-size:15px;"); info.addWidget(name)
        meta = []
        if game.category: meta.append(game.category)
        meta.append(f" {_fmt_playtime(game.total_playtime_seconds)}")
        if game.last_played_at: meta.append("last " + game.last_played_at[:10])
        m = QLabel("·".join(meta)); m.setObjectName("Tiny"); info.addWidget(m)
        if game.exe_path:
            p = QLabel(game.exe_path); p.setObjectName("Tiny"); p.setWordWrap(True); info.addWidget(p)
        else:
            p = QLabel("No executable set"); p.setObjectName("Tiny"); info.addWidget(p)
        info.addStretch(1); lay.addLayout(info, 1)

        actions = QVBoxLayout(); actions.setSpacing(6)
        launch = QPushButton("Launch"); launch.setObjectName("PrimaryButton"); launch.setIcon(_icon("player-play", size=16)); launch.clicked.connect(lambda _c=False, gid=game.id: self.launch_game(gid)); actions.addWidget(launch)
        fav = QPushButton(); fav.setIcon(_icon("star", size=16)); fav.clicked.connect(lambda _c=False, gid=game.id: self.toggle_favorite(gid)); actions.addWidget(fav)
        edit = QPushButton("Edit"); edit.clicked.connect(lambda _c=False, gid=game.id: self.edit_game(gid)); actions.addWidget(edit)
        cover_btn = QPushButton("Cover"); cover_btn.clicked.connect(lambda _c=False, gid=game.id: self.set_cover(gid)); actions.addWidget(cover_btn)
        remove = QPushButton("Remove"); remove.setObjectName("DangerButton"); remove.clicked.connect(lambda _c=False, gid=game.id: self.remove_game(gid)); actions.addWidget(remove)
        lay.addLayout(actions)
        return card

    # -- actions --------------------------------------------------------
    def add_game(self) -> None:
        name, ok = QInputDialog.getText(self, "Add game", "Game name:")
        if not ok or not name.strip(): return
        exe, _ = QFileDialog.getOpenFileName(self, "Select game executable", "", "Executables (*.exe);;All files (*)")
        self.service.add_game(name.strip(), exe or "")
        self.refresh()

    def edit_game(self, game_id: int) -> None:
        game = self.service.repo.get(game_id)
        if not game: return
        name, ok = QInputDialog.getText(self, "Edit game", "Game name:", text=game.name)
        if ok and name.strip(): game.name = name.strip()
        cat, _ = QInputDialog.getText(self, "Edit game", "Category:", text=game.category)
        game.category = cat
        exe, _ = QFileDialog.getOpenFileName(self, "Select executable", game.exe_path or "", "Executables (*.exe);;All files (*)")
        if exe: game.exe_path = exe
        self.service.update_game(game); self.refresh()

    def set_cover(self, game_id: int) -> None:
        game = self.service.repo.get(game_id)
        if not game: return
        path, _ = QFileDialog.getOpenFileName(self, "Custom cover", "", "Images (*.png *.jpg *.jpeg *.webp *.bmp)")
        if path:
            game.cover_path = path; self.service.update_game(game); self.refresh()

    def toggle_favorite(self, game_id: int) -> None:
        game = self.service.repo.get(game_id)
        if game: self.service.set_favorite(game_id, not game.favorite); self.refresh()

    def remove_game(self, game_id: int) -> None:
        if QMessageBox.question(self, "Remove game", "Remove this game from your library?") != QMessageBox.StandardButton.Yes: return
        self.service.remove_game(game_id); self.refresh()

    def launch_game(self, game_id: int) -> None:
        if not self.service.launch(game_id):
            QMessageBox.warning(self, "Launch", "Could not launch. Set a valid executable path.")

    def detect_installed(self) -> None:
        items = self.service.detect_installed()
        if not items:
            QMessageBox.information(self, "Detect installed", "No installed games detected. You can add games manually."); return
        added = self.service.import_detected(items)
        QMessageBox.information(self, "Detect installed", f"Found {len(items)} games; added {added}.")
        self.refresh()

    def _on_session_finished(self, game_id: int, duration: int) -> None:
        game = self.service.repo.get(game_id)
        name = game.name if game else "Game"
        self.context.notifications.add("Gaming session ended", f"{name}: {_fmt_playtime(duration)}", app_id="gaming", level="info")
        self.refresh()

    def on_show(self) -> None:
        self.refresh()
