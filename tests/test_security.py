"""Security primitives tests."""

from __future__ import annotations

import unittest

from security.passwords import hash_password, verify_password


class TestPasswords(unittest.TestCase):
    def test_roundtrip(self) -> None:
        h = hash_password("correct horse battery staple")
        self.assertTrue(verify_password("correct horse battery staple", h))

    def test_wrong_password_rejected(self) -> None:
        h = hash_password("secret")
        self.assertFalse(verify_password("Secret", h))
        self.assertFalse(verify_password("", h))

    def test_format_and_salt(self) -> None:
        h1 = hash_password("x")
        h2 = hash_password("x")
        self.assertTrue(h1.startswith("pbkdf2$"))
        self.assertNotEqual(h1, h2)  # random salt
        self.assertNotIn("x", h1.split("$", 2)[2])  # no plain password

    def test_invalid_encoded_rejected(self) -> None:
        self.assertFalse(verify_password("x", "garbage"))
        self.assertFalse(verify_password("x", ""))
        self.assertFalse(verify_password("x", "pbkdf2$notint$aa$bb"))


if __name__ == "__main__":
    unittest.main()
