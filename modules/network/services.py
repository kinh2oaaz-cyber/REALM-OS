"""Network Monitor service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from system import network as net

if TYPE_CHECKING:
    from core.context import AppContext


class NetworkService:
    def __init__(self, ctx: "AppContext | None" = None) -> None:
        self.ctx = ctx
        self.sampler = net.SpeedSampler()

    def status(self) -> dict:
        return {
            "online": net.internet_status(),
            "local_ip": net.local_ip(),
            "hostname": net.hostname(),
            "public_ip": None,  # call public_ip() explicitly (network)
        }

    def speeds(self) -> tuple[float, float]:
        return self.sampler.sample()

    def adapters(self) -> list[dict]:
        return net.adapters()

    def wifi(self) -> dict:
        return net.wifi_details()

    def ping(self, host: str) -> dict:
        return net.ping(host)

    def devices(self) -> list[dict]:
        return net.connected_devices()

    def record_history(self, download_bps: float, upload_bps: float, latency_ms: float | None = None) -> None:
        if self.ctx is None: return
        self.ctx.db.execute(
            "INSERT INTO network_history (download_bps, upload_bps, latency_ms) VALUES (?, ?, ?)",
            (download_bps, upload_bps, latency_ms))

    def history(self, limit: int = 100) -> list[dict]:
        if self.ctx is None: return []
        return self.ctx.db.query("SELECT * FROM network_history ORDER BY recorded_at DESC LIMIT ?", (limit,))
