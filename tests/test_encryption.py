"""Encryption at rest tests."""

from __future__ import annotations

import unittest

from security.encryption import decrypt, encrypt


class TestEncryption(unittest.TestCase):
    def test_roundtrip(self) -> None:
        blob = encrypt("secret message", "password")
        self.assertNotIn("secret message", blob)
        self.assertEqual(decrypt(blob, "password"), "secret message")

    def test_wrong_password(self) -> None:
        blob = encrypt("x", "right")
        with self.assertRaises(ValueError):
            decrypt(blob, "wrong")

    def test_malformed(self) -> None:
        with self.assertRaises(ValueError):
            decrypt("not-a-valid-blob", "x")


if __name__ == "__main__":
    unittest.main()
