"""Convenience launcher at project root.

``python main.py``  ==  ``python -m app.main``
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure project root on sys.path when run as a script.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.main import main

if __name__ == "__main__":
    raise SystemExit(main())
