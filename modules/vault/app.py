"""Password Vault registration."""

from __future__ import annotations

from core.app_registry import AppInfo, AppRegistry

from .page import VaultPage

APP_ID = "vault"


def register(registry: AppRegistry, ctx) -> None:
    registry.register(AppInfo(
        id=APP_ID, name="Password Vault", description="Encrypted local password vault",
        icon="lock", category="extra", order=203, keywords=("password", "vault", "secret", "credentials"),
        page_factory=lambda c: VaultPage(c),
    ))