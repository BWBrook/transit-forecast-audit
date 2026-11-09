#!/usr/bin/env python3
"""Independent saved-table checks for transit-forecast-audit commit 629f466.

Uses only Python 3 standard library. No package installation, network request,
project-code import, raw-photometry read, or edit to the audited checkout.

Usage:
    python check_saved_measurements.py --source /path/to/transit-forecast-audit \
        --output evidence_measurement_check.json

Checks accounting, unique accepted measurements, metadata consistency,
leave-one-out shape sensitivity, and HR 858 b's *saved* timing trajectory.
Does not validate astrophysical identification or independent photometry.
"""
from __future__ import annotations
import argparse
import collections
import csv
import gzip
import hashlib
import json
import math
import statistics
from pathlib import Path

PATHS = {
    "ledger": "results/final_primary/terminal_ledger.csv.gz",
    "windows": "data/derived/final_primary/measured/windows.csv.gz",
    "products": "data/derived/final_primary/measured/products.csv",
    "coverage": "data/derived/final_primary/measured/coverage.csv",
}

def csv_rows(path):
    with (gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open(newline="")) as f:
        return list(csv.DictReader(f))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--source", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    a = ap.parse_args()
    data = {k: csv_rows(a.source / v) for k, v in PATHS.items()}
    ledger, windows, products = data["ledger"], data["windows"], data["products"]
    coverage = {r["event_id"]: r for r in data["coverage"]}
    wm = {r["event_id"]: r for r in windows}
    accepted = [r for r in ledger if r["status"] == "accepted"]
    assert len(wm) == len(windows), "Duplicated saved measurement IDs"
    assert len({r["event_id"] for r in ledger}) == len(ledger), "Duplicated manifest IDs"
    assert len({r["window_event_id"] for r in accepted}) == len(accepted), "Measurement scored more than once"
    aw = [wm[r["window_event_id"]] for r in accepted]
    no = [coverage[r["event_id"]] for r in ledger if r["status"] == "no_cadence_coverage_at_prediction"]
    loo = sorted([
        {"event_id": w["event_id"], "planet": w["planet"],
         "absolute_shift_over_sigma": abs(float(w["loo_shift_s"])) / float(w["sigma_s"]),
         "shift_s": float(w["loo_shift_s"]), "sigma_s": float(w["sigma_s"])}
        for w in aw if w["loo_shift_s"] not in ("", "not_estimable")
    ], key=lambda r: r["absolute_shift_over_sigma"], reverse=True)
    hr = [(r, wm[r["window_event_id"]]) for r in accepted if r["planet"] == "HR858b"]
    ns = [int(r["forecast_epoch"]) for r, _ in hr]
    ts = [float(w["tc_bjd_tdb"]) for _, w in hr]
    n0, t0 = statistics.mean(ns), statistics.mean(ts)
    slope = sum((n-n0)*(t-t0) for n,t in zip(ns,ts)) / sum((n-n0)**2 for n in ns)
    rms_min = math.sqrt(statistics.mean([(t-t0-slope*(n-n0))**2 for n,t in zip(ns,ts)])) * 1440
    residuals = [(float(w["tc_bjd_tdb"]) - float(r["drd_predicted_bjd_tdb"])) * 1440 for r,w in hr]
    hrprod = [p for p in products if p["planet"] == "HR858b"]
    out = {
        "audited_commit": "629f466a2567152047d9cd75be336d865a1d68ad",
        "scope": "Independent arithmetic on saved tables only; no new astrophysical identification",
        "input_sha256": {v: hashlib.sha256((a.source/v).read_bytes()).hexdigest() for v in PATHS.values()},
        "terminal_counts": dict(collections.Counter(r["status"] for r in ledger)),
        "accepted_events": len(accepted),
        "accepted_planets": len({r["planet"] for r in accepted}),
        "accepted_hosts": len({r["host"] for r in accepted}),
        "accepted_unique_measurement_ids": len({r["window_event_id"] for r in accepted}),
        "coverage_qualified_events": sum(r["coverage_ok_at_prediction"] == "True" for r in ledger),
        "accepted_coverage_qualified_events": sum(r["coverage_ok_at_prediction"] == "True" for r in accepted),
        "accepted_fraction_all_opportunities": len(accepted)/len(ledger),
        "zero_coverage_status_rows": len(no),
        "zero_coverage_status_rows_with_positive_window_coverage": sum(float(r["coverage_window_at_prediction"])>0 for r in no),
        "accepted_rows_with_other_DRD_planets_masked": sum(bool(r["masked_other_planets"]) for r in aw),
        "accepted_timing_standards": dict(collections.Counter(r["timesys"]+"|"+r["timeref"] for r in aw)),
        "loo_shape_check": {
            "available": len(loo),
            "median_absolute_shift_over_sigma": statistics.median(r["absolute_shift_over_sigma"] for r in loo),
            "above_half_sigma": sum(r["absolute_shift_over_sigma"] > 0.5 for r in loo),
            "above_one_sigma": sum(r["absolute_shift_over_sigma"] > 1 for r in loo),
            "largest_ten": loo[:10],
            "limit": "LOO point-estimate shifts do not marginalise shape uncertainty or establish calibration."
        },
        "HR858b": {
            "accepted_events": len(hr), "epoch_range": [min(ns),max(ns)],
            "sectors": sorted({int(w["sector"]) for _,w in hr}),
            "residual_minutes_range": [min(residuals),max(residuals)],
            "residual_minutes_mean": statistics.mean(residuals),
            "local_period_days_centered_OLS": slope, "linear_residual_rms_minutes": rms_min,
            "measurement_sigma_minutes_range": [min(float(w["sigma_s"])/60 for _,w in hr),max(float(w["sigma_s"])/60 for _,w in hr)],
            "max_LOO_absolute_shift_over_sigma": max(r["absolute_shift_over_sigma"] for r in loo if r["planet"] == "HR858b"),
            "product_diagnostics": [{k:p[k] for k in ("sector","tic","id_snr","id_period_found_d","masked_cadence_fraction","t14_min","shape_rchi2","shape_at_bound")} for p in hrprod],
            "limit": "Coherence and good fit diagnostics do not independently verify planet identity or physical mechanism."
        }
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k:out[k] for k in ("accepted_events","accepted_planets","accepted_hosts","accepted_fraction_all_opportunities")},indent=2))

if __name__ == "__main__":
    main()

