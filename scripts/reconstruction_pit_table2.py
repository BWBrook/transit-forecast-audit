"""Exact predictive PIT values and Table 2 error percentiles for the reconstruction draft.

Reads only saved accepted outcomes, forecasts and likelihood grids from the
portable benchmark package. Uses the frozen adapter's grid convention and
quadrature. No fitting, photometry or protected-sector access.
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.special import ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import forecast_variance_components as f  # noqa: E402
import sprint1_outcome_adapter as adapter  # noqa: E402

PKG = ROOT / "data/derived/revision_stage0/benchmark"
OUT = ROOT / "results/reconstruction_displays"
ORDER = 384


def read(path):
    with open(path) as h:
        return list(csv.DictReader(h))


def mixture(model):
    b, s = model
    z, lw = f.quadrature(ORDER) if s >= 1e-5 else (np.zeros(1), np.zeros(1))
    return b, s, z, np.exp(lw)


def pit(residual, vf, sigma, grid, model):
    b, s, z, mw = mixture(model)
    var_f = b * b * vf * np.exp(s * z)
    if grid is None:
        return float(mw @ ndtr(residual / np.sqrt(var_f + sigma * sigma)))
    x, w = grid
    sd = np.sqrt(var_f)
    return float(w @ (ndtr((residual + x[:, None]) / sd[None, :]) @ mw))


def wquantile(values, weights, q):
    order = np.argsort(values)
    v, w = values[order], weights[order]
    cw = np.cumsum(w) / w.sum()
    return float(v[np.searchsorted(cw, q)])


def main():
    out = read(PKG / "primary/accepted_outcomes.csv")
    fc = {r["event_id"]: r for r in read(PKG / "primary/accepted_forecasts.csv")}
    rows = []
    for r in out:
        if r["status"] != "timed":
            continue
        e = fc[r["event_id"]]
        resid = (float(r["tc_bjd_tdb"]) - float(e["predicted_bjd_tdb"])) * 86400
        vf, sigma = float(e["forecast_variance_s2"]), float(r["sigma_s"])
        gauss = r["gauss_ok"].lower() in ("true", "1", "yes")
        grid = None if gauss else adapter.likelihood_grid(PKG / r["posterior_grid_path"])
        row = {"event_id": r["event_id"], "planet": r["planet"], "host": r["host"],
               "abs_error_min": abs(resid) / 60, "gaussian": gauss}
        for m in ("M0", "M2"):
            row["pit_" + m] = pit(resid, vf, sigma, grid,
                                  (float(e[m + "_b"]), float(e[m + "_s_log_lambda"])))
        rows.append(row)
    planets = sorted({r["planet"] for r in rows})
    counts = {p: sum(r["planet"] == p for r in rows) for p in planets}
    for r in rows:
        r["planet_weight"] = 1 / len(planets) / counts[r["planet"]]
    err = np.array([r["abs_error_min"] for r in rows])
    pw = np.array([r["planet_weight"] for r in rows])
    ew = np.ones_like(err)
    summary = {"events": len(rows), "planets": len(planets),
               "abs_error_min": {}, "pit_coverage95_check": {}, "pit_tail_mass": {}}
    for label, w in (("pooled", ew), ("equal_planet", pw)):
        summary["abs_error_min"][label] = {f"p{int(q*100)}": wquantile(err, w, q)
                                           for q in (.5, .95, .99)}
        summary["abs_error_min"][label]["max"] = float(err.max())
    for m in ("M0", "M2"):
        p = np.array([r["pit_" + m] for r in rows])
        inside = (p >= .025) & (p <= .975)
        summary["pit_coverage95_check"][m] = float(pw @ inside / pw.sum())
        summary["pit_tail_mass"][m] = {"below_0.025": float(pw @ (p < .025)),
                                       "above_0.975": float(pw @ (p > .975))}
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "pit_events.csv", "w", newline="") as h:
        wr = csv.DictWriter(h, fieldnames=list(rows[0]))
        wr.writeheader()
        wr.writerows(rows)
    summary["inputs_sha256"] = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (PKG / "primary/accepted_outcomes.csv", PKG / "primary/accepted_forecasts.csv")}
    (OUT / "pit_table2.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
