"""Phase 9 additional apps + safe evaluation tests."""

from __future__ import annotations

import os
import tempfile
import unittest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
os.environ.setdefault("REALMOS_DATA_DIR", tempfile.mkdtemp(prefix="realmos_p9_"))

from modules.calculator.page import safe_eval
from modules.vault.page import generate_password

PHASE9_APPS = {
    "calculator", "stopwatch", "clipboard", "vault", "finance", "weather",
    "screenshot", "pdf", "downloads", "projects", "devtools", "ai",
}


class TestSafeEval(unittest.TestCase):
    def test_arithmetic(self) -> None:
        self.assertEqual(safe_eval("1+2*3"), 7)
        self.assertEqual(safe_eval("(1+2)*3"), 9)
        self.assertEqual(safe_eval("2**8"), 256)
        self.assertEqual(safe_eval("10/4"), 2.5)
        self.assertEqual(safe_eval("7%3"), 1)
        self.assertAlmostEqual(safe_eval("sqrt(16)+pi"), 7.141592653589793)
        self.assertEqual(safe_eval("-5+3"), -2)

    def test_rejects_unsafe(self) -> None:
        for bad in ["__import__('os').system('x')", "open('x')", "a+b", "1;2", "().__class__"]:
            with self.assertRaises((ValueError, SyntaxError)):
                safe_eval(bad)


class TestPasswordGen(unittest.TestCase):
    def test_generate_password(self) -> None:
        p = generate_password(20)
        self.assertEqual(len(p), 20)
        self.assertTrue(any(c.islower() for c in p))
        self.assertTrue(any(c.isupper() for c in p))
        self.assertTrue(any(c.isdigit() for c in p))
        self.assertNotEqual(generate_password(), generate_password())


class TestPhase9Registration(unittest.TestCase):
    def test_apps_registered(self) -> None:
        from app.application import RealmOSApplication

        app = RealmOSApplication(["test"])
        ids = {a.id for a in app.registry.all()}
        self.assertTrue(PHASE9_APPS.issubset(ids), PHASE9_APPS - ids)
        app.shutdown()


if __name__ == "__main__":
    unittest.main()
