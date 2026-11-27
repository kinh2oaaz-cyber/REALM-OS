"""Central logging configuration.

Writes a rotating log file under the per-user logs directory and also
emits to stderr. Guaranteed to never raise from ``setup_logging``.
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging(logs_dir: Path | None = None, level: int = logging.INFO) -> logging.Logger:
    """Configure the root logger once. Returns the ``realmos`` logger."""
    global _configured
    root = logging.getLogger("realmos")
    root.setLevel(level)
    if _configured:
        return root

    formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)

    console = logging.StreamHandler(sys.stderr)
    console.setFormatter(formatter)
    root.addHandler(console)

    try:
        if logs_dir is not None:
            logs_dir.mkdir(parents=True, exist_ok=True)
            file_handler = RotatingFileHandler(
                logs_dir / "realmos.log",
                maxBytes=1_000_000,
                backupCount=3,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            root.addHandler(file_handler)
    except OSError:
        root.warning("Could not attach file logging handler", exc_info=True)

    _configured = True
    return root


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"realmos.{name}")
