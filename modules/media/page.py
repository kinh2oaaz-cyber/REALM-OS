"""Media Center page: local music + video, library, playlists, playback."""

from __future__ import annotations

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QColor
from ui.icons import icon as _icon
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QPushButton,
    QSlider,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage

from .models import MediaTrack
from .services import MEDIA_EXTENSIONS, MediaService


def _fmt_time(ms: int) -> str:
    s = max(0, ms // 1000); return f"{s // 60}:{s % 60:02d}"


class MediaPage(RealmPage):
    page_title = "Media"

    def __init__(self, context, parent=None) -> None:
        self.service = MediaService(context)
        self.queue: list[MediaTrack] = []
        self.current_index = -1
        self._repeat = False
        super().__init__(context, parent)
        self.player.durationChanged.connect(self._on_duration)
        self.player.positionChanged.connect(self._on_position)
        self.player.mediaStatusChanged.connect(self._on_status)
        self.player.errorOccurred.connect(self._on_error)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel("Media Center"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        scan = QPushButton("Add folder to library"); scan.setIcon(_icon("folder-plus", size=18)); scan.clicked.connect(self.scan_folder); header.addWidget(scan)
        open_file = QPushButton("Open file"); open_file.setObjectName("PrimaryButton"); open_file.setIcon(_icon("player-play", size=18)); open_file.clicked.connect(self.open_file); header.addWidget(open_file)
        self.layout_root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # library
        left = QWidget(); ll = QVBoxLayout(left); ll.setContentsMargins(0,0,0,0); ll.setSpacing(8)
        self.search = QLineEdit(); self.search.setObjectName("SearchBox"); self.search.setPlaceholderText("Search library…")
        self.search.setClearButtonEnabled(True); self.search.textChanged.connect(lambda _t: self.refresh_library()); ll.addWidget(self.search)
        self.library_list = QListWidget(); self.library_list.itemDoubleClicked.connect(self._play_from_library); ll.addWidget(self.library_list, 1)
        splitter.addWidget(left)

        # player + video
        right = QWidget(); rl = QVBoxLayout(right); rl.setContentsMargins(0,0,0,0); rl.setSpacing(10)
        self.player = QMediaPlayer(self)
        self.audio = QAudioOutput(self)
        self.player.setAudioOutput(self.audio)
        self.audio.setVolume(0.8)
        self.video = QVideoWidget(); self.video.setMinimumHeight(260); self.player.setVideoOutput(self.video); rl.addWidget(self.video, 1)
        self.now_playing = QLabel("Nothing playing"); self.now_playing.setObjectName("SectionTitle"); self.now_playing.setAlignment(Qt.AlignmentFlag.AlignCenter); rl.addWidget(self.now_playing)

        # seek
        seek_row = QHBoxLayout()
        self.pos_label = QLabel("0:00"); seek_row.addWidget(self.pos_label)
        self.seek = QSlider(Qt.Orientation.Horizontal); self.seek.setRange(0, 0); self.seek.sliderMoved.connect(self.player.setPosition); seek_row.addWidget(self.seek, 1)
        self.dur_label = QLabel("0:00"); seek_row.addWidget(self.dur_label)
        rl.addLayout(seek_row)

        # controls
        controls = QHBoxLayout(); controls.setSpacing(8); controls.addStretch(1)
        self.prev_btn = QPushButton(); self.prev_btn.setIcon(_icon("player-skip-back", size=18)); self.prev_btn.clicked.connect(self.prev_track); controls.addWidget(self.prev_btn)
        self.play_btn = QPushButton(); self.play_btn.setIcon(_icon("player-play", size=18)); self.play_btn.setObjectName("PrimaryButton"); self.play_btn.clicked.connect(self.toggle_play); controls.addWidget(self.play_btn)
        self.stop_btn = QPushButton(); self.stop_btn.setIcon(_icon("player-stop", size=18)); self.stop_btn.clicked.connect(self.stop); controls.addWidget(self.stop_btn)
        self.next_btn = QPushButton(); self.next_btn.setIcon(_icon("player-skip-forward", size=18)); self.next_btn.clicked.connect(self.next_track); controls.addWidget(self.next_btn)
        self.repeat_btn = QPushButton(); self.repeat_btn.setIcon(_icon("repeat", size=18)); self.repeat_btn.setCheckable(True); self.repeat_btn.clicked.connect(lambda c: self.set_repeat(c)); controls.addWidget(self.repeat_btn)
        controls.addStretch(1)
        controls.addWidget(QLabel(""))
        self.volume = QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0, 100); self.volume.setValue(80); self.volume.setMaximumWidth(120)
        self.volume.valueChanged.connect(lambda v: self.audio.setVolume(v / 100.0)); controls.addWidget(self.volume)
        rl.addLayout(controls)

        splitter.addWidget(right); splitter.setSizes([420, 680])
        self.layout_root.addWidget(splitter, 1)

        self.refresh_library()

    # -- library --------------------------------------------------------
    def refresh_library(self) -> None:
        query = self.search.text().strip() or None
        self.library_list.clear()
        tracks = self.service.library(query)
        if not tracks:
            hint = QListWidgetItem(
                "Your library is empty.\nAdd a folder or open a file to start listening."
                if not query
                else "No tracks match this search."
            )
            hint.setFlags(Qt.ItemFlag.NoItemFlags)
            hint.setForeground(QColor("#6B6370"))
            self.library_list.addItem(hint)
            return
        for t in tracks:
            icon = ""
            item = QListWidgetItem(f"{icon} {t.title}" + (f" — {t.artist}" if t.artist else ""))
            item.setData(Qt.ItemDataRole.UserRole, t.path); item.setToolTip(t.path); self.library_list.addItem(item)

    def scan_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Add folder to library")
        if not folder: return
        tracks = self.service.scan_folder(folder)
        added = self.service.add_to_library(tracks)
        self.refresh_library()
        QMessageBox.information(self, "Media library", f"Scanned {len(tracks)} media files; library updated ({added} processed).")

    def _play_from_library(self, item: QListWidgetItem) -> None:
        path = item.data(Qt.ItemDataRole.UserRole)
        # play whole library queue starting at this item
        all_tracks = self.service.library(self.search.text().strip() or None)
        start = next((i for i, t in enumerate(all_tracks) if t.path == path), 0)
        self.queue = all_tracks; self.play_index(start)

    def open_file(self) -> None:
        exts = " ".join(f"*{e}" for e in sorted(MEDIA_EXTENSIONS))
        path, _ = QFileDialog.getOpenFileName(self, "Open media", "", f"Media ({exts});;All files (*)")
        if not path: return
        track = MediaTrack(path=path, title=__import__("pathlib").Path(path).stem)
        self.queue = [track]; self.play_index(0)

    # -- playback -------------------------------------------------------
    def play_index(self, index: int) -> None:
        if not self.queue or index < 0 or index >= len(self.queue):
            return
        self.current_index = index
        track = self.queue[index]
        self.player.setSource(QUrl.fromLocalFile(track.path))
        self.player.play()
        self.now_playing.setText(track.title)
        # history
        if track.id:
            self.service.record_played(track.id)
        self.play_btn.setIcon(_icon("player-play", size=18))

    def toggle_play(self) -> None:
        if self.player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.player.pause(); self.play_btn.setIcon(_icon("player-pause", size=18))
        else:
            if self.current_index < 0 and self.queue:
                self.play_index(0); return
            self.player.play(); self.play_btn.setIcon(_icon("player-play", size=18))

    def stop(self) -> None:
        self.player.stop(); self.play_btn.setIcon(_icon("player-play", size=18))

    def next_track(self) -> None:
        if self.queue:
            self.play_index((self.current_index + 1) % len(self.queue))

    def prev_track(self) -> None:
        if self.queue:
            self.play_index((self.current_index - 1) % len(self.queue))

    def set_repeat(self, on: bool) -> None:
        self._repeat = on

    def _on_duration(self, duration: int) -> None:
        self.seek.setRange(0, duration); self.dur_label.setText(_fmt_time(duration))

    def _on_position(self, position: int) -> None:
        if not self.seek.isSliderDown():
            self.seek.setValue(position)
        self.pos_label.setText(_fmt_time(position))

    def _on_status(self, status) -> None:  # noqa: ANN001
        if status == QMediaPlayer.MediaStatus.EndOfMedia:
            if self._repeat:
                self.player.setPosition(0); self.player.play()
            else:
                self.next_track()

    def _on_error(self, error, error_string: str) -> None:  # noqa: ANN001
        if error != QMediaPlayer.Error.NoError:
            self.now_playing.setText(error_string or "Playback error")

    def on_show(self) -> None:
        self.refresh_library()
