#!/usr/bin/env python3
"""Replace the synthetic weather fallback with Open-Meteo historical hourly data."""
from __future__ import annotations
import csv, json, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "weather_hourly.csv"
params = {
    "latitude": 41.0082, "longitude": 28.9784,
    "start_date": "2025-01-01", "end_date": "2025-01-31",
    "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
    "timezone": "Europe/Istanbul",
}
url = "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)
try:
    with urllib.request.urlopen(url, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))
    hourly = payload["hourly"]
    rows = []
    for i, ts in enumerate(hourly["time"]):
        rows.append({
            "observed_at": ts.replace("T", " ") + (":00" if len(ts) == 16 else ""),
            "temperature_2m_c": hourly["temperature_2m"][i],
            "relative_humidity_2m_pct": hourly["relative_humidity_2m"][i],
            "precipitation_mm": hourly["precipitation"][i],
            "wind_speed_10m_kmh": hourly["wind_speed_10m"][i],
            "data_source": "Open-Meteo Historical Weather API",
        })
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    meta = {
        "source": "Open-Meteo Historical Weather API",
        "endpoint": "https://archive-api.open-meteo.com/v1/archive",
        "latitude": params["latitude"], "longitude": params["longitude"],
        "timezone": params["timezone"], "start_date": params["start_date"], "end_date": params["end_date"],
        "hourly_variables": params["hourly"].split(","), "rows": len(rows),
    }
    (ROOT / "data" / "open_meteo_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK: {len(rows)} saatlik Open-Meteo satiri yazildi: {OUT}")
except Exception as exc:
    print("Open-Meteo indirilemedi; mevcut dosya korunuyor.")
    print(f"Hata: {exc}")
    print("İnternet erişimi olan bir bilgisayarda tekrar çalıştır: python src/fetch_open_meteo.py")
