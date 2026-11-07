"""Fixed intended-event attempt ledger (D056 §3), exercised on development outcomes.

Every intended event (planet, sector, DRD epoch) from a manifest built before
fitting receives exactly one terminal status. Recovered windows map to events by
DRD cycle number (nearest epoch to the window centre or timed mid-time); a
window whose timed mid-time lies more than P/4 from its DRD prediction is
retained as `cycle_ambiguous`, never silently re-assigned. Product-level
failures propagate to every intended event of the product. Windows with no
intended event are reported as `outside_manifest`.

Development use: the manifest is every DRD epoch inside each remeasured SPOC
product's header TSTART-TSTOP interval (metadata support, not cadence
observability). The sealed-era manifest is results/sprint2/freeze_candidate/events_drd.csv.

    .venv/bin/python scripts/prefreeze_attempts.py
"""

from __future__ import annotations

import csv
import gzip
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
from reproduce_table5 import load  # noqa: E402
from sprint2_freeze_package import fits_header_cards  # noqa: E402

OUT = ROOT / "results" / "prefreeze"
SHAPE_RCHI_MAX = 10.0
INTEG = {"mass_outside_fine", "coarse_fine_shift"}


def terminal_status(window):
    st = window["status"]
    if st == "timed" and INTEG & set((window.get("flags") or "").split(";")):
        return "integration_unresolved"
    return st


def build_ledger(manifest, windows, product_state, ephemeris):
    """manifest: rows with planet, sector, epoch. windows: outcome rows. product_state: {(planet, sector): status}."""
    by_event = defaultdict(list)
    outside = []
    keys = {(m["planet"], str(m["sector"]), int(m["epoch"])) for m in manifest}
    for w in windows:
        e = ephemeris[w["planet"]]
        ref = float(w.get("tc_bjd_tdb") or w.get("window_centre_bjd_tdb") or w.get("predicted_bjd_tdb_drd"))
        n = int(round((ref - e.t0_bjd_tdb) / e.period_days))
        k = (w["planet"], str(w["sector"]), n)
        (by_event[k] if k in keys else outside).append(w)
    ledger = []
    for m in manifest:
        k = (m["planet"], str(m["sector"]), int(m["epoch"]))
        ps = product_state.get(k[:2], "no_product")
        row = {"planet": k[0], "sector": k[1], "epoch": k[2]}
        if ps != "ok":
            ledger.append({**row, "status": ps})
            continue
        ws = by_event.get(k, [])
        if not ws:
            # Identified products enumerate a window wherever any cadence lies within the half-width,
            # so an intended epoch with no window had no cadences there (a data gap, not a recovery failure).
            ledger.append({**row, "status": "no_cadence_in_window"})
            continue
        if len(ws) > 1:
            ledger.append({**row, "status": "ambiguous_multiple_windows"})
            continue
        w = ws[0]
        st = terminal_status(w)
        if st == "timed":
            e = ephemeris[k[0]]
            if abs(float(w["tc_bjd_tdb"]) - (e.t0_bjd_tdb + k[2] * e.period_days)) > e.period_days / 4:
                st = "cycle_ambiguous"
        ledger.append({**row, "status": st, "event_id": w["event_id"]})
    return ledger, outside


def development():
    eph, _, _ = load()
    drd = eph["DRD"]
    out = [r for r in csv.DictReader(gzip.open(ROOT / "results/outcomes/t015v3/outcomes.csv.gz", "rt"))
           if r["product"] == "SPOC_120"]
    pid = [r for r in csv.DictReader((ROOT / "results/outcomes/t015v3/product_identification.csv").open())
           if r.get("product") == "SPOC_120"]
    prod_rows = [r for r in csv.DictReader((ROOT / "results/outcomes/t015v3/products.csv").open())
                 if r["status"] == "selected" and r["product"] == "SPOC_120"]
    spans = {}
    for p in prod_rows:
        f = ROOT / "data/raw/mast" / p["tic"].replace(" ", "_") / p["uri"].split("/")[-1]
        if f.exists():
            h = fits_header_cards(f)
            bjd0 = float(h[1]["BJDREFI"]) + float(h[1]["BJDREFF"])
            spans[(p["host"], str(p["sector"]))] = (float(h[1]["TSTART"]) + bjd0, float(h[1]["TSTOP"]) + bjd0)
    state, manifest = {}, []
    for r in pid:
        planet, sector = r["planet"], str(r["sector"])
        st = "ok"
        if r["status"] != "ok":
            st = "product_id_failed"
        elif r.get("shape_rchi2") and float(r["shape_rchi2"]) > SHAPE_RCHI_MAX:
            st = "product_shape_gate_failed"
        state[(planet, sector)] = st
        span = spans.get((r["host"], sector))
        if span is None:
            continue
        e = drd[planet]
        n0, n1 = math.ceil((span[0] - e.t0_bjd_tdb) / e.period_days), math.floor((span[1] - e.t0_bjd_tdb) / e.period_days)
        manifest += [{"planet": planet, "sector": sector, "epoch": n} for n in range(n0, n1 + 1)]
    ledger, outside = build_ledger(manifest, out, state, drd)
    counts = Counter(r["status"] for r in ledger)
    by_planet = defaultdict(lambda: [0, 0])
    for r in ledger:
        by_planet[r["planet"]][0] += r["status"] == "timed"
        by_planet[r["planet"]][1] += 1
    return {"intended_events": len(ledger), "terminal_status_counts": dict(counts.most_common()),
            "timed_fraction_events": round(counts["timed"] / len(ledger), 4),
            "planet_balanced_timed_fraction": round(sum(a / b for a, b in by_planet.values()) / len(by_planet), 4),
            "windows_outside_manifest": len(outside),
            "outside_manifest_status": dict(Counter(w["status"] for w in outside)),
            "products": len(state), "product_states": dict(Counter(state.values())),
            "shape_gate_max_reduced_chi2": SHAPE_RCHI_MAX,
            "manifest_basis": "DRD epochs inside header TSTART-TSTOP of each remeasured SPOC product; metadata support only"}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = development()
    (OUT / "attempt_ledger_development.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
