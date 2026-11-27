"""Motion engine tests (offscreen)."""

from __future__ import annotations

import os
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtWidgets import QApplication, QPushButton  # noqa: E402

from ui import motion  # noqa: E402

_app = QApplication.instance() or QApplication([])


class TestMotion(unittest.TestCase):
    def test_fade_in_no_crash(self) -> None:
        w = QPushButton("x"); w.show()
        motion.fade_in(w, duration=50, settings=None)
        self.assertTrue(motion.motion_enabled(None))

    def test_reduce_motion(self) -> None:
        class S:
            def get_bool(self, k, d=False): return True
        self.assertFalse(motion.motion_enabled(S()))
        w = QPushButton("y")
        motion.fade_in(w, settings=S())  # no-op, no effect
        self.assertIsNone(w.graphicsEffect())

    def test_page_transition(self) -> None:
        w = QPushButton("z")
        motion.page_transition(w, settings=None)


if __name__ == "__main__":
    unittest.main()
