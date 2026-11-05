#!/usr/bin/env python3
"""Generate a reproducible teaching dataset for Kura #5.

Sensor events and notifications are synthetic. Weather is a clearly labelled
synthetic fallback; replace it with Open-Meteo data using fetch_open_meteo.py.
"""
from __future__ import annotations
import argparse, csv, json, math, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RNG = random.Random(20261105)
START = datetime(2025, 1, 1, 0, 0)
N_EVENTS = 720

SENSORS = [
    (f"S{i:03}", region, typ)
    for i, (region, typ) in enumerate([
        ("Kadikoy", "air_quality"), ("Kadikoy", "traffic"),
        ("Besiktas", "air_quality"), ("Besiktas", "noise"),
        ("Uskudar", "flood"), ("Uskudar", "air_quality"),
        ("Sisli", "traffic"), ("Sisli", "noise"),
        ("Fatih", "waste"), ("Fatih", "air_quality"),
        ("Atasehir", "heat"), ("Atasehir", "traffic"),
    ], start=1)
]
EVENT_TYPES = [
    "air_quality_alert", "traffic_congestion", "noise_threshold",
    "flood_risk", "heat_stress", "waste_overflow"
]
EVENT_WEIGHTS = [0.22, 0.20, 0.14, 0.12, 0.17, 0.15]
EVENT_SENSOR_TYPE = {
    "air_quality_alert": "air_quality", "traffic_congestion": "traffic",
    "noise_threshold": "noise", "flood_risk": "flood",
    "heat_stress": "heat", "waste_overflow": "waste",
}
TOKEN_MULTIPLIER = {
    "air_quality_alert": 1.85, "traffic_congestion": 1.42,
    "noise_threshold": 0.78, "flood_risk": 1.62,
    "heat_stress": 1.28, "waste_overflow": 0.92,
}
MODEL_CONFIG = {
    "economy_v1":  {"weight": 0.55, "input_rate": 0.00000600, "output_rate": 0.00001100, "base_ms": 360},
    "balanced_v1": {"weight": 0.33, "input_rate": 0.00002000, "output_rate": 0.00003600, "base_ms": 620},
    "premium_v1":  {"weight": 0.12, "input_rate": 0.00008000, "output_rate": 0.00016000, "base_ms": 1050},
}


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def make_weather() -> list[dict]:
    rows = []
    for hour in range(31 * 24):
        ts = START + timedelta(hours=hour)
        # Educational fallback only. Values are not observed measurements.
        seasonal = 7.8 + 2.0 * math.sin((hour / 744) * 2 * math.pi)
        daily = 2.5 * math.sin(((ts.hour - 8) / 24) * 2 * math.pi)
        temperature = seasonal + daily + RNG.gauss(0, 1.0)
        humidity = min(98, max(35, 76 - 1.4 * (temperature - 8) + RNG.gauss(0, 7)))
        rain = max(0, RNG.gauss(0.20, 0.55)) if RNG.random() < 0.23 else 0
        wind = max(0.4, RNG.gauss(14, 6))
        rows.append({
            "observed_at": ts.strftime("%Y-%m-%d %H:%M:%S"),
            "temperature_2m_c": round(temperature, 1),
            "relative_humidity_2m_pct": round(humidity, 1),
            "precipitation_mm": round(rain, 2),
            "wind_speed_10m_kmh": round(wind, 1),
            "data_source": "synthetic_fallback_NOT_OPEN_METEO",
        })
    return rows


def generate() -> dict:
    DATA.mkdir(parents=True, exist_ok=True)
    sensor_rows = [
        {"id": sid, "region": region, "type": typ}
        for sid, region, typ in SENSORS
    ]
    events = []
    for i in range(1, N_EVENTS + 1):
        event_type = RNG.choices(EVENT_TYPES, EVENT_WEIGHTS, k=1)[0]
        compatible_sensors = [s for s in SENSORS if s[2] == EVENT_SENSOR_TYPE[event_type]]
        sid, region, stype = RNG.choice(compatible_sensors)
        # Severity is ordinal. A small event-type effect produces realistic variation.
        base = {
            "air_quality_alert": 3.0, "traffic_congestion": 3.1,
            "noise_threshold": 2.3, "flood_risk": 3.8,
            "heat_stress": 3.2, "waste_overflow": 2.5,
        }[event_type]
        severity = max(1, min(5, round(RNG.gauss(base, 1.0))))
        minute = RNG.randrange(60)
        event_at = START + timedelta(hours=RNG.randrange(31 * 24), minutes=minute)
        events.append({
            "id": i, "sensor_id": sid, "event_type": event_type,
            "severity_1_5": severity,
            "event_at": event_at.strftime("%Y-%m-%d %H:%M:%S"),
        })

    notifications = []
    nid = 1
    for event in events:
        event_type = event["event_type"]
        severity = int(event["severity_1_5"])
        event_at = datetime.strptime(event["event_at"], "%Y-%m-%d %H:%M:%S")
        # Most events create one alert; some create a follow-up notification.
        count = 2 if RNG.random() < 0.11 else 1
        for _ in range(count):
            model = RNG.choices(list(MODEL_CONFIG), [c["weight"] for c in MODEL_CONFIG.values()], k=1)[0]
            cfg = MODEL_CONFIG[model]
            input_tokens = int(RNG.randint(90, 180) * TOKEN_MULTIPLIER[event_type])
            output_tokens = int(RNG.randint(45, 105) * TOKEN_MULTIPLIER[event_type] + severity * 6)
            total_tokens = input_tokens + output_tokens
            cost = input_tokens * cfg["input_rate"] + output_tokens * cfg["output_rate"]
            cost = round(cost, 7)
            # Positive severity-to-latency signal, with model and token effects.
            latency = int(cfg["base_ms"] + severity * 210 + total_tokens * 1.15 + RNG.gauss(0, 170))
            latency = max(120, latency)
            # Add a small number of severe backlogs so the SLOW CASE branch is exercised.
            if severity >= 4 and RNG.random() < 0.08:
                latency += RNG.randint(1800, 2600)
            sent_at = event_at + timedelta(milliseconds=latency)
            notifications.append({
                "id": nid, "event_id": event["id"], "model_name": model,
                "total_tokens": total_tokens, "cost_usd": cost,
                "latency_ms": latency,
                "sent_at": sent_at.strftime("%Y-%m-%d %H:%M:%S"),
            })
            nid += 1

    # Add 18 legitimate event-less notifications (event_id NULL).
    for _ in range(18):
        model = RNG.choices(list(MODEL_CONFIG), [c["weight"] for c in MODEL_CONFIG.values()], k=1)[0]
        cfg = MODEL_CONFIG[model]
        tokens = RNG.randint(120, 300)
        cost = round(tokens * (cfg["input_rate"] + cfg["output_rate"]) / 2, 7)
        sent_at = START + timedelta(hours=RNG.randrange(31 * 24), minutes=RNG.randrange(60))
        notifications.append({
            "id": nid, "event_id": "", "model_name": model,
            "total_tokens": tokens, "cost_usd": cost,
            "latency_ms": RNG.randint(300, 2600),
            "sent_at": sent_at.strftime("%Y-%m-%d %H:%M:%S"),
        })
        nid += 1

    # Inject expected data-quality issues for the Week 4 exercise.
    rng_ids = list(range(len(notifications)))
    RNG.shuffle(rng_ids)
    missing_cost_idxs = set(rng_ids[:30])
    negative_latency_idxs = set(rng_ids[30:42])
    for idx, row in enumerate(notifications):
        if idx in missing_cost_idxs:
            row["cost_usd"] = ""
        if idx in negative_latency_idxs:
            row["latency_ms"] = -abs(int(row["latency_ms"]))

    weather = make_weather()
    write_csv(DATA / "sensors.csv", sensor_rows, ["id", "region", "type"])
    write_csv(DATA / "sensor_events.csv", events, ["id", "sensor_id", "event_type", "severity_1_5", "event_at"])
    write_csv(DATA / "notifications.csv", notifications, ["id", "event_id", "model_name", "total_tokens", "cost_usd", "latency_ms", "sent_at"])
    write_csv(DATA / "weather_hourly.csv", weather, ["observed_at", "temperature_2m_c", "relative_humidity_2m_pct", "precipitation_mm", "wind_speed_10m_kmh", "data_source"])

    profile = {
        "project": "Kura #5 - Akilli sehir x IoT x LLM maliyet/gecikme",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "random_seed": 20261105,
        "counts": {"sensors": len(sensor_rows), "sensor_events": len(events), "notifications": len(notifications), "weather_hourly": len(weather)},
        "quality_issues": {
            "notifications_missing_event_id": sum(1 for r in notifications if not r["event_id"]),
            "notifications_missing_cost_usd": sum(1 for r in notifications if r["cost_usd"] == ""),
            "notifications_negative_latency_ms": sum(1 for r in notifications if int(r["latency_ms"]) < 0),
        },
        "provenance": {
            "sensor_events": "synthetic teaching data; not real municipality telemetry",
            "notifications": "synthetic teaching data; costs and latency are simulated",
            "weather_hourly": "synthetic fallback in this prepared package; use src/fetch_open_meteo.py to replace with Open-Meteo observations",
        }
    }
    (DATA / "data_profile.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
    return profile


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--try-open-meteo", action="store_true", help="Try downloading actual Open-Meteo historical weather first")
    args = parser.parse_args()
    result = generate()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if args.try_open_meteo:
        import subprocess, sys
        subprocess.run([sys.executable, str(Path(__file__).with_name("fetch_open_meteo.py"))], check=False)
