# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "batman-package", "setuptools", "lightkurve==2.5.1",
#                 "astroquery", "tess-point==0.9.5.post1"]
# ///
"""Fixed intended-event attempt ledger under the shared acceptance contract (D058 §3).

Manifest: every DRD epoch inside each selected SPOC 120-s product's header
TSTART-TSTOP (development) or the frozen sealed-era manifest. Each intended
event receives one terminal status:

* product states from scripts/acceptance.py (unavailable, read failure,
  identification failure, shape diagnostic unresolved, shape gate);
* a matched recovered window (by DRD cycle number) -> its acceptance state;
* no matched window -> a direct cadence check at the DRD-predicted position
  (quality-0 cadences, declared window half-width): `no_cadence_coverage_at_prediction`
  when window or in-transit coverage < 0.75, otherwise `unmatched_expected_event`.
  The prediction locates the check only; it never enters timing or acceptance.

Windows whose cycle has no intended event are reported as outside the manifest;
two windows on one cycle make the event `ambiguous_multiple_windows`.
Development photometry only (S46-S73, both guards).

    uv run scripts/prefreeze_attempts.py
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import acceptance as A  # noqa: E402
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402
from reproduce_table5 import load  # noqa: E402

OUT = ROOT / "results" / "prefreeze"


def coverage_at(t, centre, per, t14):
    cad = float(np.median(np.diff(t))) if len(t) > 1 else 120 / 86400
    half = so.half_width(per, t14)
    return tp.coverage(t, centre, half, cad), tp.coverage(t, centre, t14 / 2, cad)


def development():
    eph, _, _ = load()
    drd = eph["DRD"]
    outcomes = [r for r in csv.DictReader(gzip.open(ROOT / "results/outcomes/t015v3/outcomes.csv.gz", "rt"))
                if r["product"] == A.PRODUCT]
    pid = {(r["planet"], str(r["sector"])): r for r in
           csv.DictReader((ROOT / "results/outcomes/t015v3/product_identification.csv").open())
           if r.get("planet") and r.get("product") == A.PRODUCT}
    windows = defaultdict(list)
    for w in outcomes:
        e = drd[w["planet"]]
        ref = float(w.get("tc_bjd_tdb") or w.get("window_centre_bjd_tdb") or w.get("predicted_bjd_tdb_drd"))
        windows[(w["planet"], str(w["sector"]), int(round((ref - e.t0_bjd_tdb) / e.period_days)))].append(w)
    products = [r for r in csv.DictReader((ROOT / "results/outcomes/t015v3/products.csv").open())
                if r["status"] == "selected" and r["product"] == A.PRODUCT]
    ledger, unenumerated, used = [], [], set()
    for p in products:
        f = ROOT / "data/raw/mast" / p["tic"].replace(" ", "_") / p["uri"].split("/")[-1]
        try:
            t, _, _, _, meta = tp.read(f, "pdcsap")
            bjd0 = float(meta["BJDREFI"]) + float(meta["BJDREFF"])
            span = (float(meta["TSTART"]) + bjd0, float(meta["TSTOP"]) + bjd0)
            tt = t + bjd0
        except Exception as exc:  # noqa: BLE001
            for planet in p["planets"].split(";"):
                unenumerated.append({"planet": planet, "sector": p["sector"], "status": "product_read_failed",
                                     "reason": repr(exc)[:120]})
            continue
        for planet in p["planets"].split(";"):
            e = drd[planet]
            diag = pid.get((planet, str(p["sector"])))
            ps = A.product_state(diag)
            t14 = (float(diag["t14_min"]) / 1440 if diag and A._finite(diag.get("t14_min")) else so.t14_guess(e.period_days))
            n0 = math.ceil((span[0] - e.t0_bjd_tdb) / e.period_days)
            n1 = math.floor((span[1] - e.t0_bjd_tdb) / e.period_days)
            for n in range(n0, n1 + 1):
                pred = e.t0_bjd_tdb + n * e.period_days
                cw, ci = coverage_at(tt, pred, e.period_days, t14)
                row = {"event_id": f"{planet}|S{p['sector']}|DRD{n}", "planet": planet, "sector": p["sector"],
                       "product": A.PRODUCT, "epoch": n, "drd_predicted_bjd_tdb": round(pred, 6),
                       "coverage_window_at_prediction": round(min(cw, 1), 4),
                       "coverage_in_transit_at_prediction": round(min(ci, 1), 4)}
                key = (planet, str(p["sector"]), n)
                ws = windows.get(key, [])
                used.add(key)
                if ws:
                    row["window_event_id"] = ";".join(w["event_id"] for w in ws)
                st = A.terminal_status(ps, ws, diag, pred, e.period_days, cw >= .75 and ci >= .75)
                ledger.append({**row, "status": st})
    outside = [w for k, ws in windows.items() if k not in used for w in ws]
    counts = Counter(r["status"] for r in ledger)
    byp = defaultdict(lambda: [0, 0])
    for r in ledger:
        byp[r["planet"]][0] += r["status"] == A.ACCEPTED
        byp[r["planet"]][1] += 1
    cov_ok = [r for r in ledger if r["coverage_window_at_prediction"] >= .75 and r["coverage_in_transit_at_prediction"] >= .75]
    with gzip.open(OUT / "attempt_ledger_development.csv.gz", "wt", newline="") as fh:
        keys = list(dict.fromkeys(k for r in ledger for k in r))
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(ledger)
    return {"intended_events": len(ledger), "terminal_status_counts": dict(counts.most_common()),
            "accepted_fraction_all_intended": round(counts[A.ACCEPTED] / len(ledger), 4),
            "planet_balanced_accepted_fraction": round(sum(a / b for a, b in byp.values()) / len(byp), 4),
            "coverage_qualified_events_at_prediction": len(cov_ok),
            "accepted_fraction_coverage_qualified": round(sum(r["status"] == A.ACCEPTED for r in cov_ok) / len(cov_ok), 4),
            "windows_outside_manifest": len(outside),
            "outside_manifest_status": dict(Counter(w["status"] for w in outside)),
            "products_unenumerated": unenumerated,
            "rule": "scripts/acceptance.py", "shape_rchi_max": A.SHAPE_RCHI_MAX,
            "manifest_basis": "DRD epochs inside header TSTART-TSTOP of each selected SPOC product (development)"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = development()
    (OUT / "attempt_ledger_development.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
