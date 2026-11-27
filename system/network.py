"""Read-only network helpers (psutil + OS tools). No intrusive monitoring."""

from __future__ import annotations

import socket
import subprocess
import sys
import time

try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None  # type: ignore[assignment]


def internet_status(timeout: float = 3.0) -> bool:
    """True if a TCP connection to a public DNS resolver succeeds."""
    for host, port in (("1.1.1.1", 53), ("8.8.8.8", 53)):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            continue
    return False


def local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def hostname() -> str:
    return socket.gethostname()


def public_ip(timeout: float = 3.0) -> str | None:
    """Best-effort public IP via a lightweight HTTPS check (optional; None offline)."""
    try:
        import urllib.request

        with urllib.request.urlopen("https://api.ipify.org", timeout=timeout) as resp:  # noqa: S310
            return resp.read().decode("ascii").strip()
    except Exception:  # noqa: BLE001
        return None


def adapters() -> list[dict]:
    if psutil is None:
        return []
    out = []
    stats = psutil.net_if_stats()
    for name, addrs in psutil.net_if_addrs().items():
        st = stats.get(name)
        out.append({
            "name": name,
            "is_up": bool(st.isup) if st else False,
            "speed_mbps": st.speed if st else 0,
            "mtu": st.mtu if st else 0,
            "addresses": [
                {"family": str(a.family), "address": a.address, "netmask": a.netmask, "broadcast": a.broadcast}
                for a in addrs
            ],
        })
    return out


def io_counters() -> tuple[int, int]:
    """(bytes_recv, bytes_sent) cumulative."""
    if psutil is None:
        return (0, 0)
    c = psutil.net_io_counters()
    return (c.bytes_recv, c.bytes_sent)


class SpeedSampler:
    """Compute download/upload speed in bytes/sec between samples."""

    def __init__(self) -> None:
        self._last: tuple[int, int, float] | None = None

    def sample(self) -> tuple[float, float]:
        recv, sent = io_counters()
        now = time.monotonic()
        if self._last is None:
            self._last = (recv, sent, now)
            return (0.0, 0.0)
        prev_recv, prev_sent, prev_t = self._last
        dt = max(1e-6, now - prev_t)
        down = max(0.0, (recv - prev_recv) / dt)
        up = max(0.0, (sent - prev_sent) / dt)
        self._last = (recv, sent, now)
        return (down, up)


def ping(host: str, count: int = 1, timeout_ms: int = 1000) -> dict:
    """System ping. Returns {success, latency_ms, output}."""
    if sys.platform.startswith("win"):
        cmd = ["ping", "-n", str(count), "-w", str(timeout_ms), host]
    else:
        cmd = ["ping", "-c", str(count), "-W", str(max(1, timeout_ms // 1000)), host]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_ms / 1000 * count + 5)  # noqa: S603
        output = result.stdout + result.stderr
        latency = _parse_latency(output)
        return {"success": result.returncode == 0, "latency_ms": latency, "output": output.strip()}
    except (subprocess.TimeoutExpired, OSError) as exc:
        return {"success": False, "latency_ms": None, "output": str(exc)}


def _parse_latency(output: str) -> float | None:
    import re

    # Windows: "time=12ms" / "time<1ms"; Unix: "time=12.3 ms"
    m = re.search(r"time[=<]\s*([\d.]+)\s*ms", output, re.I)
    if m:
        return float(m.group(1))
    m = re.search(r"([\d.]+)\s*ms", output)
    if m:
        return float(m.group(1))
    return None


def wifi_details() -> dict:
    """Wi-Fi connection details on Windows via `netsh wlan show interfaces`."""
    info: dict = {"connected": False}
    if not sys.platform.startswith("win"):
        return info
    try:
        result = subprocess.run(["netsh", "wlan", "show", "interfaces"], capture_output=True, text=True, timeout=5)  # noqa: S603
        text = result.stdout
        for line in text.splitlines():
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip().lower(); value = value.strip()
            if key == "ssid":
                info["ssid"] = value; info["connected"] = True
            elif key == "bssid":
                info["bssid"] = value
            elif key == "signal":
                info["signal"] = value
            elif key == "radio type":
                info["radio_type"] = value
            elif key == "channel":
                info["channel"] = value
            elif key == "authentication":
                info["authentication"] = value
            elif key == "state":
                info["state"] = value
                info["connected"] = value.lower() == "connected"
    except (subprocess.TimeoutExpired, OSError):
        pass
    return info


def connected_devices() -> list[dict]:
    """Devices in the OS ARP/neighbor cache for the local network.

    Reads the existing OS table; does NOT perform any scanning or
    intrusive probing. Connected-device discovery is limited to the
    user's own network.
    """
    devices: list[dict] = []
    try:
        if sys.platform.startswith("win"):
            result = subprocess.run(["arp", "-a"], capture_output=True, text=True, timeout=5)  # noqa: S603
        else:
            result = subprocess.run(["ip", "neigh"], capture_output=True, text=True, timeout=5)  # noqa: S603
        import re

        for line in result.stdout.splitlines():
            m = re.search(r"(\d+\.\d+\.\d+\.\d+).*?([0-9a-fA-F]{2}([-:][0-9a-fA-F]{2}){5})", line)
            if m:
                devices.append({"ip": m.group(1), "mac": m.group(2).replace("-", ":")})
    except (subprocess.TimeoutExpired, OSError):
        pass
    # de-dup
    seen = set(); out = []
    for d in devices:
        if d["ip"] in seen: continue
        seen.add(d["ip"]); out.append(d)
    return out
