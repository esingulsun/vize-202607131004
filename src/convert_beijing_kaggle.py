#!/usr/bin/env python3
"""Optional adapter for the Kaggle Beijing Multi-Site Air-Quality CSV files.

Put the unzipped Kaggle CSV files in data/kaggle_beijing/ and run this script.
The output is a separate air_quality_observations.csv; it is not silently
mixed into the Istanbul teaching events because it describes Beijing (2013-2017).
"""
from __future__ import annotations
import argparse
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument("--input", default=str(ROOT / "data" / "kaggle_beijing"))
args = parser.parse_args()
indir = Path(args.input)
files = sorted(indir.glob("*.csv"))
if not files:
    raise SystemExit(f"CSV bulunamadi: {indir}\nKaggle dosyalarini bu klasore cikart.")
frames = []
for path in files:
    df = pd.read_csv(path)
    lower = {c.lower().strip(): c for c in df.columns}
    required = ["year", "month", "day", "hour"]
    if not all(c in lower for c in required):
        continue
    def col(name): return lower.get(name)
    date = pd.to_datetime({
        "year": df[col("year")], "month": df[col("month")],
        "day": df[col("day")], "hour": df[col("hour")]
    }, errors="coerce")
    station = df[col("station")] if col("station") else path.stem
    out = pd.DataFrame({
        "measurement_at": date,
        "station": station,
        "pm25_ug_m3": df[col("pm2.5")] if col("pm2.5") else pd.NA,
        "pm10_ug_m3": df[col("pm10")] if col("pm10") else pd.NA,
        "so2_ug_m3": df[col("so2")] if col("so2") else pd.NA,
        "no2_ug_m3": df[col("no2")] if col("no2") else pd.NA,
        "co_mg_m3": df[col("co")] if col("co") else pd.NA,
        "o3_ug_m3": df[col("o3")] if col("o3") else pd.NA,
        "temperature_c": df[col("temp")] if col("temp") else pd.NA,
        "pressure_hpa": df[col("pres")] if col("pres") else pd.NA,
        "dew_point_c": df[col("dewp")] if col("dewp") else pd.NA,
        "rain_mm": df[col("rain")] if col("rain") else pd.NA,
        "wind_direction": df[col("wd")] if col("wd") else pd.NA,
        "wind_speed_m_s": df[col("wspm")] if col("wspm") else pd.NA,
        "source": "Kaggle Beijing Multi-Site Air-Quality Data Set",
    })
    frames.append(out.dropna(subset=["measurement_at"]))
if not frames:
    raise SystemExit("Beklenen year/month/day/hour sutunlari bulunan CSV bulunamadi.")
result = pd.concat(frames, ignore_index=True).sort_values(["measurement_at", "station"])
outfile = ROOT / "data" / "air_quality_observations.csv"
result.to_csv(outfile, index=False)
print(f"{len(result):,} gozlem yazildi: {outfile}")
print("Not: Bu kayitlar Beijing/2013-2017 kaynaklidir; Istanbul verisi gibi sunmayin.")
