"""Network Monitor page."""

from __future__ import annotations

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from ui.components.page import RealmPage

from .services import NetworkService


def _human_bps(bps: float) -> str:
    n = float(bps)
    for unit in ("B/s", "KB/s", "MB/s", "GB/s"):
        if abs(n) < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB/s"


class NetworkPage(RealmPage):
    page_title = "Network"

    def __init__(self, context, parent=None) -> None:
        self.service = NetworkService(context)
        super().__init__(context, parent)

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20)
        self.layout_root.setSpacing(12)
        header = QHBoxLayout()
        title = QLabel("Network Monitor"); title.setObjectName("SectionTitle"); header.addWidget(title); header.addStretch(1)
        self.layout_root.addLayout(header)

        scroll = QScrollArea(); scroll.setWidgetResizable(True); scroll.setFrameShape(QFrame.Shape.NoFrame)
        content = QWidget(); col = QVBoxLayout(content); col.setSpacing(12)
        scroll.setWidget(content); self.layout_root.addWidget(scroll, 1)

        # status + speeds
        top = QHBoxLayout(); top.setSpacing(12)
        self.status_card = self._card("Connection", "…"); top.addWidget(self.status_card[0], 1)
        self.down_card = self._card("Download", "0 B/s"); top.addWidget(self.down_card[0], 1)
        self.up_card = self._card("Upload", "0 B/s"); top.addWidget(self.up_card[0], 1)
        col.addLayout(top)

        # ping / diagnostics
        ping_card = QFrame(); ping_card.setObjectName("Card"); pl = QVBoxLayout(ping_card)
        pl.addWidget(QLabel("Ping & diagnostics"))
        prow = QHBoxLayout()
        self.ping_edit = QLineEdit("1.1.1.1"); prow.addWidget(self.ping_edit, 1)
        ping_btn = QPushButton("Ping"); ping_btn.clicked.connect(self.do_ping); prow.addWidget(ping_btn)
        pl.addLayout(prow)
        self.ping_result = QLabel(""); self.ping_result.setObjectName("Muted"); self.ping_result.setWordWrap(True); pl.addWidget(self.ping_result)
        col.addWidget(ping_card)

        # adapters
        adapters_card = QFrame(); adapters_card.setObjectName("Card"); al = QVBoxLayout(adapters_card)
        al.addWidget(QLabel("Network adapters & IP"))
        self.adapters_list = QListWidget(); al.addWidget(self.adapters_list)
        col.addWidget(adapters_card)

        # wifi
        wifi_card = QFrame(); wifi_card.setObjectName("Card"); wl = QVBoxLayout(wifi_card)
        wl.addWidget(QLabel("Wi-Fi"))
        self.wifi_label = QLabel("—"); self.wifi_label.setObjectName("Muted"); self.wifi_label.setWordWrap(True); wl.addWidget(self.wifi_label)
        col.addWidget(wifi_card)

        # connected devices
        dev_card = QFrame(); dev_card.setObjectName("Card"); dl = QVBoxLayout(dev_card)
        dl.addWidget(QLabel("Devices on your network (ARP cache)"))
        self.devices_list = QListWidget(); dl.addWidget(self.devices_list)
        refresh_dev = QPushButton("Refresh devices"); refresh_dev.clicked.connect(self.refresh_devices); dl.addWidget(refresh_dev)
        col.addWidget(dev_card)

        # history
        hist_card = QFrame(); hist_card.setObjectName("Card"); hl = QVBoxLayout(hist_card)
        hl.addWidget(QLabel("Connection history"))
        self.history_list = QListWidget(); hl.addWidget(self.history_list)
        col.addWidget(hist_card)

        self._timer = QTimer(self); self._timer.setInterval(1000); self._timer.timeout.connect(self._tick); self._timer.start()
        self._tick_count = 0
        self._tick()
        self.refresh_adapters(); self.refresh_wifi(); self.refresh_devices(); self.refresh_history()

    def _card(self, title: str, value: str):
        frame = QFrame(); frame.setObjectName("Card"); lay = QVBoxLayout(frame)
        t = QLabel(title); t.setObjectName("Tiny"); lay.addWidget(t)
        v = QLabel(value); v.setStyleSheet("font-size:18px; font-weight:700;"); lay.addWidget(v)
        return (frame, v)

    def _tick(self) -> None:
        down, up = self.service.speeds()
        self.down_card[1].setText(_human_bps(down))
        self.up_card[1].setText(_human_bps(up))
        self._tick_count += 1
        if self._tick_count % 5 == 1:
            status = self.service.status()
            online = status["online"]
            self.status_card[1].setText((" Online" if online else " Offline"))
            self.status_card[1].setStyleSheet(f"font-size:18px; font-weight:700; color: {'#34C759' if online else '#FF3B30'};")
            # record history every 5s
            latency = None
            self.service.record_history(down, up, latency)
            self.refresh_history()
        # also reflect IP in status card tooltip
        try:
            self.status_card[0].setToolTip(f"Local IP: {self.service.status()['local_ip']}\nHost: {self.service.status()['hostname']}")
        except Exception:  # noqa: BLE001
            pass

    def do_ping(self) -> None:
        host = self.ping_edit.text().strip() or "1.1.1.1"
        result = self.service.ping(host)
        if result["success"]:
            lat = result["latency_ms"]
            self.ping_result.setText(f" {host} reachable" + (f" · {lat} ms" if lat is not None else ""))
        else:
            self.ping_result.setText(f" {host} unreachable\n{result['output'][:300]}")

    def refresh_adapters(self) -> None:
        self.adapters_list.clear()
        for a in self.service.adapters():
            state = "up" if a["is_up"] else "down"
            ips = ", ".join(addr["address"] for addr in a["addresses"] if addr["family"].endswith("AF_INET") or addr["family"] == "AddressFamily.AF_INET")
            item = QListWidgetItem(f"{a['name']}  [{state}]  {ips}  {a['speed_mbps']} Mbps")
            self.adapters_list.addItem(item)

    def refresh_wifi(self) -> None:
        w = self.service.wifi()
        if w.get("connected"):
            self.wifi_label.setText(
                f"SSID: {w.get('ssid','?')}\nSignal: {w.get('signal','?')}\nBSSID: {w.get('bssid','')}\n"
                f"Radio: {w.get('radio_type','')}  Channel: {w.get('channel','')}  Auth: {w.get('authentication','')}")
        else:
            self.wifi_label.setText("Not connected to Wi-Fi (or no wireless adapter).")

    def refresh_devices(self) -> None:
        self.devices_list.clear()
        devices = self.service.devices()
        if not devices:
            self.devices_list.addItem("No devices in ARP cache."); return
        for d in devices:
            self.devices_list.addItem(f"{d['ip']}   {d.get('mac','')}")

    def refresh_history(self) -> None:
        self.history_list.clear()
        for h in self.service.history(limit=30):
            self.history_list.addItem(
                f"{h['recorded_at']}  {_human_bps(h['download_bps'])}  {_human_bps(h['upload_bps'])}")

    def on_show(self) -> None:
        self.refresh_adapters(); self.refresh_wifi(); self.refresh_devices(); self.refresh_history()
