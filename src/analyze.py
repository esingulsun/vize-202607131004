#!/usr/bin/env python3
"""Create repeatable analysis outputs from the generated CSV files."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA, REPORTS = ROOT / "data", ROOT / "reports"
REPORTS.mkdir(exist_ok=True)
events = pd.read_csv(DATA / "sensor_events.csv", parse_dates=["event_at"])
notes = pd.read_csv(DATA / "notifications.csv", parse_dates=["sent_at"])
sensors = pd.read_csv(DATA / "sensors.csv")
notes["event_id"] = pd.to_numeric(notes["event_id"], errors="coerce")
notes["cost_usd"] = pd.to_numeric(notes["cost_usd"], errors="coerce")
notes["latency_ms"] = pd.to_numeric(notes["latency_ms"], errors="coerce")
joined = notes.merge(events, left_on="event_id", right_on="id", how="left", suffixes=("_notification", "_event"))

# Query 1: event type volume and spend.
q1 = (joined.dropna(subset=["event_type"]).groupby("event_type")
      .agg(notification_count=("id_notification", "count"), total_cost_usd=("cost_usd", "sum"),
           avg_cost_usd=("cost_usd", "mean"), avg_tokens=("total_tokens", "mean"))
      .reset_index().sort_values("total_cost_usd", ascending=False))
q1.to_csv(REPORTS / "q1_event_type_cost.csv", index=False)

# Query 2: event_id empty count and share of all notification records.
missing_event = int(notes["event_id"].isna().sum())
q2 = pd.DataFrame([{"missing_event_id_count": missing_event,
                    "total_notifications": len(notes),
                    "missing_event_id_pct": round(100 * missing_event / len(notes), 2)}])
q2.to_csv(REPORTS / "q2_orphan_notification_share.csv", index=False)

# Query 3: event types with spend > $1.
q3 = q1[q1["total_cost_usd"] > 1.0].copy()
q3.to_csv(REPORTS / "q3_event_type_over_one_usd.csv", index=False)

# Query 4: CASE-style latency groups, preserving negative values as a separate class.
def latency_group(x):
    if pd.isna(x): return "UNKNOWN"
    if x < 0: return "NEGATIVE_CLOCK_ERROR"
    if x <= 1000: return "FAST_0_1000"
    if x <= 3000: return "MEDIUM_1001_3000"
    return "SLOW_OVER_3000"
notes["latency_category"] = notes["latency_ms"].map(latency_group)
joined = joined.merge(notes[["id", "latency_category"]], left_on="id_notification", right_on="id", how="left")
q4 = (joined.dropna(subset=["event_type"])
      .groupby(["severity_1_5", "latency_category"]).size()
      .rename("notification_count").reset_index())
q4.to_csv(REPORTS / "q4_severity_latency_crosstab.csv", index=False)

# Query 5: sent hour and average latency; negative values included but separately flagged in profile.
notes["sent_hour"] = notes["sent_at"].dt.hour
q5 = (notes.groupby("sent_hour").agg(
         notification_count=("id", "count"),
         valid_latency_count=("latency_ms", lambda s: int((s >= 0).sum())),
         avg_valid_latency_ms=("latency_ms", lambda s: s[s >= 0].mean()),
         avg_cost_usd=("cost_usd", "mean"))
      .reset_index().sort_values("notification_count", ascending=False))
q5.to_csv(REPORTS / "q5_hourly_intensity.csv", index=False)

# Severity/latency relationship: exclude invalid negative latencies, report Pearson and Spearman.
valid = joined.dropna(subset=["severity_1_5", "latency_ms"]).query("latency_ms >= 0")
pearson = valid["severity_1_5"].corr(valid["latency_ms"], method="pearson")
spearman = valid["severity_1_5"].corr(valid["latency_ms"], method="spearman")

# Model comparison: global and within event type/severity strata.
model_global = (joined.dropna(subset=["event_type", "cost_usd", "latency_ms"])
                .query("latency_ms >= 0").groupby("model_name")
                .agg(notifications=("id_notification", "count"), avg_cost_usd=("cost_usd", "mean"),
                     avg_latency_ms=("latency_ms", "mean"), avg_tokens=("total_tokens", "mean"))
                .reset_index().sort_values("avg_cost_usd"))
model_global.to_csv(REPORTS / "model_comparison_global.csv", index=False)
model_strat = (joined.dropna(subset=["event_type", "severity_1_5", "cost_usd", "latency_ms"])
               .query("latency_ms >= 0").groupby(["event_type", "severity_1_5", "model_name"])
               .agg(n=("id_notification", "count"), avg_cost_usd=("cost_usd", "mean"),
                    avg_latency_ms=("latency_ms", "mean"))
               .reset_index())
model_strat.to_csv(REPORTS / "model_comparison_by_event_severity.csv", index=False)

profile = {
    "row_counts": {"sensors": int(len(sensors)), "sensor_events": int(len(events)), "notifications": int(len(notes))},
    "quality": {
        "notifications_without_event_id": missing_event,
        "notifications_missing_cost": int(notes["cost_usd"].isna().sum()),
        "negative_latency_rows": int((notes["latency_ms"] < 0).sum()),
        "negative_latency_policy": "Preserved and reported; excluded only from valid latency correlation/model latency summaries.",
    },
    "severity_latency": {"valid_pairs": int(len(valid)), "pearson_r": round(float(pearson), 4), "spearman_rho": round(float(spearman), 4)},
    "top_cost_event_type": q1.iloc[0]["event_type"],
    "top_cost_usd": round(float(q1.iloc[0]["total_cost_usd"]), 4),
    "q1": q1.to_dict(orient="records"),
    "q2": q2.to_dict(orient="records"),
    "q3": q3.to_dict(orient="records"),
    "model_comparison": model_global.to_dict(orient="records"),
}
(REPORTS / "analysis_summary.json").write_text(json.dumps(profile, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(profile, ensure_ascii=False, indent=2))
