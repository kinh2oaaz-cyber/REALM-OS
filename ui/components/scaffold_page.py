"""Honest Phase-1 scaffold page for apps built in later phases.

Not fake functionality: clearly states what's available now and what
phase implements the app, plus any already-available shared data.
"""

from __future__ import annotations

from PySide6.QtWidgets import QLabel, QVBoxLayout

from .cards import heading, muted
from .page import RealmPage


class ScaffoldPage(RealmPage):
    page_title = "App"
    app_icon = "•"
    app_name = "App"
    description = ""
    phase = "a later phase"

    def build_ui(self) -> None:
        self.layout_root.addWidget(heading(f"{self.app_icon}  {self.app_name}", "SectionTitle"))

        if self.description:
            desc = muted(self.description)
            self.layout_root.addWidget(desc)

        card_wrap = QVBoxLayout()
        note = QLabel(
            f"This application's full interface is scheduled for {self.phase}.\n\n"
            "The application shell, navigation, shared database and design system "
            "are already in place, so it will integrate seamlessly. Nothing here is "
            "faked — there are no non-functional buttons."
        )
        note.setObjectName("Muted")
        note.setWordWrap(True)
        note.setContentsMargins(4, 12, 4, 4)
        self.layout_root.addWidget(note)
        self.layout_root.addLayout(card_wrap)
        self.layout_root.addStretch(1)
