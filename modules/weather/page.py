"""Weather — optional internet feature.

Local-first: REALM OS works offline; this app needs internet and an
external service (Open-Meteo, no API key). Honest when offline.
"""

from __future__ import annotations

import json
import urllib.parse
import urllib.request

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from ui.components.page import RealmPage

_UA = {"User-Agent": "REALM-OS/1.0"}


def fetch_weather(city: str, timeout: float = 6.0) -> dict | None:
    """Geocode city then fetch current weather from Open-Meteo. None if offline/unknown."""
    try:
        # geocoding
        geo_url = "https://geocoding-api.open-meteo.com/v1/search?" + urllib.parse.urlencode({"name": city, "count": 1})
        req = urllib.request.Request(geo_url, headers=_UA)
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            geo = json.loads(resp.read().decode("utf-8"))
        results = geo.get("results") or []
        if not results:
            return {"error": "City not found"}
        loc = results[0]
        lat, lon = loc["latitude"], loc["longitude"]
        wx_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
            "latitude": lat, "longitude": lon, "current_weather": "true", "timezone": "auto",
        })
        req2 = urllib.request.Request(wx_url, headers=_UA)
        with urllib.request.urlopen(req2, timeout=timeout) as resp2:  # noqa: S310
            data = json.loads(resp2.read().decode("utf-8"))
        cw = data.get("current_weather", {})
        return {
            "name": loc.get("name", city), "country": loc.get("country", ""),
            "temperature": cw.get("temperature"), "windspeed": cw.get("windspeed"),
            "weathercode": cw.get("weathercode"), "time": cw.get("time"),
        }
    except Exception as exc:  # noqa: BLE001
        return {"error": f"Could not fetch weather (offline or unavailable): {exc}"}


_WX = {0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog", 48: "Fog",
       51: "Drizzle", 61: "Rain", 63: "Rain", 65: "Heavy rain", 71: "Snow", 73: "Snow", 75: "Heavy snow",
       80: "Showers", 95: "Thunderstorm"}


class WeatherPage(RealmPage):
    page_title = "Weather"

    def build_ui(self) -> None:
        self.layout_root.setContentsMargins(24, 20, 24, 20); self.layout_root.setSpacing(12)
        title = QLabel("Weather"); title.setObjectName("SectionTitle"); self.layout_root.addWidget(title)
        row = QHBoxLayout()
        self.city = QLineEdit("London"); self.city.setPlaceholderText("City"); self.city.returnPressed.connect(self.load); row.addWidget(self.city, 1)
        go = QPushButton("Get weather"); go.setObjectName("PrimaryButton"); go.clicked.connect(self.load); row.addWidget(go); self.layout_root.addLayout(row)

        card = QFrame(); card.setObjectName("Card"); self.result = QLabel("Enter a city. Requires internet."); self.result.setObjectName("Muted")
        self.result.setWordWrap(True); self.result.setAlignment(Qt.AlignmentFlag.AlignCenter); self.result.setStyleSheet("font-size:16px;")
        v = QVBoxLayout(card); v.addWidget(self.result); self.layout_root.addWidget(card, 1)
        note = QLabel("Weather is an optional internet feature. Everything else in REALM OS works offline."); note.setObjectName("Tiny"); note.setWordWrap(True); self.layout_root.addWidget(note)

    def load(self) -> None:
        city = self.city.text().strip()
        if not city: return
        self.result.setText("Loading…")
        data = fetch_weather(city)
        if data is None or "error" in data:
            self.result.setText(data["error"] if data else "Unavailable."); return
        wx = _WX.get(data.get("weathercode"), "—")
        self.result.setText(
            f"{data['name']}, {data.get('country','')}\n\n{data.get('temperature')}°C · {wx}\nWind {data.get('windspeed')} km/h\n{data.get('time','')}")
