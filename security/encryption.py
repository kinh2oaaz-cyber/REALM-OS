"""Symmetric encryption at rest via `cryptography` Fernet.

Used for optional password-protected notes and the password vault.
Key is derived from a user password + per-record salt with
PBKDF2-HMAC-SHA256. No plaintext secrets are stored or logged.
"""

from __future__ import annotations

import base64
import os

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

_ITERATIONS = 200_000
_SALT_BYTES = 16


def _key_from_password(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt(plaintext: str, password: str, *, salt: bytes | None = None) -> str:
    """Return `salt_hex$token`. Decrypt with same password + embedded salt."""
    salt = salt or os.urandom(_SALT_BYTES)
    fernet = Fernet(_key_from_password(password, salt))
    token = fernet.encrypt(plaintext.encode("utf-8")).decode("ascii")
    return f"{salt.hex()}${token}"


def decrypt(blob: str, password: str) -> str:
    """Inverse of :func:`encrypt`. Raises ValueError on wrong password."""
    try:
        salt_hex, token = blob.split("$", 1)
        salt = bytes.fromhex(salt_hex)
    except (ValueError, AttributeError) as exc:
        raise ValueError("Malformed encrypted blob") from exc
    fernet = Fernet(_key_from_password(password, salt))
    try:
        return fernet.decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError) as exc:
        raise ValueError("Wrong password or corrupted data") from exc
