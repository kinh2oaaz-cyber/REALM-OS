"""Theme engine tests (pure QSS generation; no QApplication needed for build_qss)."""

from __future__ import annotations

import unittest

from ui.themes import DARK_TOKENS, LIGHT_TOKENS, ThemeTokens, build_qss
from ui.themes.theme_manager import _accent_soft, _is_hex_color


class TestQss(unittest.TestCase):
    def test_light_dark_produce_qss(self) -> None:
        for tokens in (LIGHT_TOKENS, DARK_TOKENS):
            qss = build_qss(tokens, accent="#FF3B30")
            self.assertIn("QWidget", qss)
            self.assertIn("#FF3B30", qss)  # accent applied
            self.assertNotIn("@accent", qss)  # all tokens substituted
            self.assertNotIn("@bg", qss)
            self.assertNotIn("@text", qss)

    def test_accent_invalid_falls_back(self) -> None:
        qss = build_qss(LIGHT_TOKENS, accent="not-a-color")
        self.assertIn("#C8AA6E", qss)  # default gold

    def test_font_and_size(self) -> None:
        qss = build_qss(LIGHT_TOKENS, font_family="Georgia", base_size=17)
        self.assertIn("Georgia", qss)
        self.assertIn("17px", qss)

    def test_token_substitution_complete(self) -> None:
        qss = build_qss(DARK_TOKENS)
        # no leftover @placeholders
        leftovers = [tok for tok in ("@surface", "@border", "@accent_soft", "@radius_card") if tok in qss]
        self.assertEqual(leftovers, [])


class TestHelpers(unittest.TestCase):
    def test_is_hex_color(self) -> None:
        self.assertTrue(_is_hex_color("#C8AA6E"))
        self.assertTrue(_is_hex_color("#fff"))
        self.assertFalse(_is_hex_color("0071E3"))
        self.assertFalse(_is_hex_color("#xyzxyz"))
        self.assertFalse(_is_hex_color("#12"))
        self.assertFalse(_is_hex_color(""))

    def test_accent_soft(self) -> None:
        self.assertTrue(_accent_soft("#C8AA6E", "light").startswith("#"))
        self.assertTrue(_accent_soft("#C8AA6E", "dark").startswith("#"))
        self.assertTrue(_accent_soft("garbage", "light").startswith("#"))


class TestTokens(unittest.TestCase):
    def test_is_theme_tokens(self) -> None:
        self.assertIsInstance(LIGHT_TOKENS, ThemeTokens)
        self.assertEqual(LIGHT_TOKENS.name, "light")
        self.assertEqual(DARK_TOKENS.name, "dark")


if __name__ == "__main__":
    unittest.main()
