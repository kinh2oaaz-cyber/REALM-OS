"""Feature modules.

Each module is a self-contained application inside REALM OS with its
own services, models, database access and UI. Modules register
themselves with the central :class:`core.app_registry.AppRegistry`.
"""

from __future__ import annotations

from .registry import register_all_modules

__all__ = ["register_all_modules"]
