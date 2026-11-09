"""Characterise the HR858b held-out timings that dominate the primary mean (C048).

Reads the frozen accepted outcomes/forecasts of the primary run (regenerable, local) and the committed
product diagnostics; writes results/final_review/hr858b_check.json. Descriptive.

    .venv/bin/python scripts/check_hr858b.py
"""

import csv
import gzip
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PLANET = "HR858b"


def main():
    run = ROOT / "results/final_primary"
    o = [r for r in csv.DictReader((run / "accepted_outcomes.csv").open()) if r["planet"] == PLANET]
    f = {r["event_id"]: r for r in csv.DictReader((run / "accepted_forecasts.csv").open())}
    n = np.array([int(r["drd_epoch"]) for r in o])
    tc = np.array([float(r["tc_bjd_tdb"]) for r in o])
    pred = np.array([float(f[r["event_id"]]["predicted_bjd_tdb"]) for r in o])
    resid_min = (tc - pred) * 1440
    fit = np.polyfit(n, tc, 1)
    drd_period = float(np.polyfit(n, pred, 1)[0])
    prods = [r for r in csv.DictReader((ROOT / "data/derived/final_primary/measured/products.csv").open())
             if r["planet"] == PLANET]
    dev = [r for r in csv.DictReader(gzip.open(ROOT / "results/outcomes/t015v3/outcomes.csv.gz", "rt"))
           if r["planet"] == PLANET]
    out = {"planet": PLANET, "accepted_events": len(o), "sectors": sorted({r["sector"] for r in o}),
           "residual_min_range": [float(resid_min.min()), float(resid_min.max())],
           "residual_min_mean": float(resid_min.mean()),
           "forecast_sd_min_range": [float(min(np.sqrt(float(f[r["event_id"]]["forecast_variance_s2"])) / 60 for r in o)),
                                     float(max(np.sqrt(float(f[r["event_id"]]["forecast_variance_s2"])) / 60 for r in o))],
           "sigma_min_range": [float(min(float(r["sigma_s"]) for r in o) / 60), float(max(float(r["sigma_s"]) for r in o) / 60)],
           "measured_local_period_d": float(fit[0]), "drd_period_d": drd_period,
           "linear_fit_rms_min": float(np.std(tc - np.polyval(fit, n)) * 1440),
           "product_shape_rchi2": {r["sector"]: r["shape_rchi2"] for r in prods},
           "development_outcome_rows": len(dev),
           "note": "Literature: HR 858 = TOI-396, timing variations reported by Bonfanti et al. 2025 (arXiv 2411.14911)."}
    dest = ROOT / "results/final_review/hr858b_check.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
