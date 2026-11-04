"""Track R: reproduce ExoClock IV Table 5 and its first-order sensitivities.

Development material only: these TESS outcomes (2022-01-01 to 2024-01-03) are
now inspected and cannot later serve as an untouched evaluation era.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from transit_audit.exoclock import (host_of, read_catalogue, read_drb_ephemerides,  # noqa: E402
                                    read_mid_times, residuals_without_covariance)
from transit_audit.scoring import cluster_bootstrap_interval, planet_means  # noqa: E402

RAW = ROOT / "data" / "raw" / "osf"
PUBLISHED = {  # ExoClock IV Table 5 (arXiv:2511.14407v1 main.tex lines 418-428)
    "DRD": (424, 4716, (66.39, 93.70, 99.28, 99.96)),
    "DRC": (308, 3604, (62.32, 91.32, 98.34, 99.61)),
    "DRB": (130, 1585, (48.01, 76.53, 93.50, 98.30)),
}
# Availability anchors (date_kind recorded in coordination/decisions.md D013).
ISSUE = {
    "DRB": {"training_end": "2020-12-31", "osf_upload": "2021-10-27", "arxiv_v1": "2021-10-26",
            "journal": "2022-02-09"},
    "DRC": {"training_end": "2021-12-31", "osf_upload": "2022-09-27", "arxiv_v1": "2022-09-20",
            "journal": "2023-02-14"},
    "DRD": {"training_end": "2023-12-31", "osf_upload": "2025-11-17", "arxiv_v1": "2025-11-18",
            "journal": "2026-02-11"},
}
KS = (1, 2, 3, 4)


def load():
    eph = {
        "DRB": read_drb_ephemerides(RAW / "wna5e" / "updated_ephemerides.txt"),
        "DRC": read_catalogue(RAW / "p298n" / "catalogue_of_ephemerides.txt"),
        "DRD": read_catalogue(RAW / "wpjtn" / "catalogue_of_ephemerides.txt"),
    }
    tess = [m for m in read_mid_times(RAW / "wpjtn" / "all_mid_time_data.txt")
            if m.source == "space" and m.tess_date and m.tess_date >= "2022-01-01"]
    flags: dict[str, set[str]] = {"DRC": set(), "DRD": set()}
    with (ROOT / "data" / "fixtures" / "exoclock_ttv_flags.csv").open() as f:
        for r in csv.DictReader(f):
            flags[r["flag_release"]].add(r["planet"])
    flags["DRB"] = {p for p, e in eph["DRB"].items() if "nonlinear" in e.flags}
    return eph, tess, flags


def summarise(release, variant, eph, events, rng_seed=2000):
    n, oc, pred_sd, sig = residuals_without_covariance(eph, events)
    z = np.abs(oc) / sig
    planets = [e.planet for e in events]
    row = {"release": release, "variant": variant, "planets": len(set(planets)),
           "measurements": len(events)}
    for k in KS:
        row[f"pooled_within_{k}sigma_pct"] = round(100 * float(np.mean(z < k)), 2)
    for k in KS:
        means = planet_means((z < k).astype(float), planets)
        row[f"planet_balanced_within_{k}sigma_pct"] = round(100 * float(np.mean(list(means.values()))), 2)
    pm = planet_means((z >= 3).astype(float), planets)
    ids, miss3 = list(pm), np.array(list(pm.values()))
    lo, hi = cluster_bootstrap_interval(miss3, [host_of(p) for p in ids], seed=rng_seed)
    row["planet_balanced_miss3_ci95_low_pct"] = round(100 * lo, 2)
    row["planet_balanced_miss3_ci95_high_pct"] = round(100 * hi, 2)
    row["planets_with_any_miss3"] = int(np.sum(miss3 > 0))
    row["median_abs_oc_min"] = round(float(np.median(np.abs(oc))) * 1440, 3)
    row["median_pred_sd_min"] = round(float(np.median(pred_sd)) * 1440, 3)
    row["median_forecast_var_share"] = round(float(np.median(pred_sd**2 / sig**2)), 3)
    row["frac_forecast_var_share_gt_half"] = round(float(np.mean(pred_sd**2 / sig**2 > 0.5)), 3)
    return row


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "pilot_v1"))
    args = ap.parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    eph, tess, flags = load()
    rows, checks = [], {}
    for rel in ("DRB", "DRC", "DRD"):
        E = eph[rel]
        base = [m for m in tess if m.planet in E]
        variants = {
            "R0_published_excl_DRD_flags": [m for m in base if m.planet not in flags["DRD"]],
            "S1_no_flag_exclusion": base,
            "S2_excl_flags_known_at_origin": [m for m in base if m.planet not in flags[rel]],
        }
        for key in ("arxiv_v1", "journal"):
            cut = ISSUE[rel][key]
            variants[f"S3_post_{key}_excl_origin_flags"] = [
                m for m in variants["S2_excl_flags_known_at_origin"] if m.tess_date > cut]
            variants[f"S3_pre_{key}_excl_origin_flags"] = [
                m for m in variants["S2_excl_flags_known_at_origin"] if m.tess_date <= cut]
        for v, ev in variants.items():
            if ev:
                rows.append(summarise(rel, v, E, ev))
        r0 = next(r for r in rows if r["release"] == rel and r["variant"].startswith("R0"))
        pp, pm, pv = PUBLISHED[rel]
        checks[rel] = {
            "planets": [r0["planets"], pp], "measurements": [r0["measurements"], pm],
            "pct": [[r0[f"pooled_within_{k}sigma_pct"] for k in KS], list(pv)],
            "exact": r0["planets"] == pp and r0["measurements"] == pm
            and all(abs(r0[f"pooled_within_{k}sigma_pct"] - v) < 0.005 for k, v in zip(KS, pv)),
        }
    with (out / "table5_variants.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    (out / "table5_reproduction_check.json").write_text(json.dumps({
        "track": "R",
        "definition": "TESS mid-times in DRD all_mid_time_data.txt with record-ID date >= 2022-01-01; "
                      "planet in the release; DRD 42 TTV-flagged planets excluded; nearest epoch; "
                      "|O-C| / sqrt(sigma_Tmid^2 + sigma_T0^2 + (n sigma_P)^2) < k; pooled over measurements",
                      "checks": checks,
        "development_only": True,
    }, indent=2) + "\n")
    for rel, c in checks.items():
        print(rel, "exact" if c["exact"] else "MISMATCH", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
