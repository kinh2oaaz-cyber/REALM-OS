"""Core infrastructure shared by every REALM OS module.

Modules in this package are framework-level services: configuration,
logging, settings, event bus, application registry, notifications and
the theme engine. They must not depend on any individual feature module.
"""

from __future__ import annotations
