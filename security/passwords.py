"""Password hashing primitives (PBKDF2-HMAC-SHA256, stdlib only).

Used for optional password-protected notes and, later, a password
vault. Never stores or logs plain-text secrets. Verification uses a
constant-time compare.
"""

from __future__ import annotations

import hashlib
import hmac
import os

_ITERATIONS = 200_000
_SALT_BYTES = 16


def hash_password(password: str, *, iterations: int = _ITERATIONS) -> str:
    """Return a self-contained `pbkdf2$iter$salt_hex$hash_hex` string."""
    salt = os.urandom(_SALT_BYTES)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return f"pbkdf2${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        scheme, iter_s, salt_hex, hash_hex = encoded.split("$", 3)
        if scheme != "pbkdf2":
            return False
        iterations = int(iter_s)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, AttributeError):
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return hmac.compare_digest(dk, expected)
