# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Manifest-driven measurement for the final evaluation (rule t015v3a; D060).

For every SPOC 120-s product named in the fixed manifest (product_obs_id), and
every manifest planet on it: read the light curve, mask the other DRD planets on
the host, identify with BLS within the issued DRD period +/-0.5% (epoch blind,
SNR >= 7), and time every recovered window with the frozen t015v3 core
(sprint2_outcomes.time_windows). Writes the three inputs of
scripts/final_evaluation.py evaluate:

* windows.csv.gz: I1 rows (one per recovered window; grids for non-Gaussian timings);
* products.csv: per planet-product diagnostics (status, shape_rchi2, t14), including
  read and download failures, so no manifest product disappears;
* coverage.csv: quality-0 cadence coverage at every manifest event's DRD prediction
  (declared window and in-transit half-widths), from the unmasked light curve.

Era: development keeps both access guards (MAST t_max from --product-meta checked
before any request; header TSTOP before any flux). Protected lifts them only when
configs/protected_access.json records Barry's decision (final_evaluation.era_limit).

    uv run scripts/final_measure.py --manifest M --out DIR [--product-meta P] [--era development]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402

PRODUCT = "SPOC_120"
ID_SOURCE, ID_DATE = "ExoClock DRD catalogue (OSF wpjtn)", "2025-11-18"
_ERA = {}


def write_csv(p, rows):
    p = Path(p)
    keys = list(dict.fromkeys(k for r in rows for k in r)) or ["planet"]
    with (gzip.open(p, "wt", newline="") if p.suffix == ".gz" else p.open("w", newline="")) as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def set_era(era, grids):
    if era == "protected":
        import final_evaluation as fe
        fe.era_limit("protected")
        tp.MAX_MJD = tp.MAX_BTJD = math.inf
    so.GRIDS = Path(grids)
    _ERA["era"] = era


def coverage_at(t, centre, per, t14, cadence):
    return (min(tp.coverage(t, centre, so.half_width(per, t14), cadence), 1.0),
            min(tp.coverage(t, centre, t14 / 2, cadence), 1.0))


def measure_product(item):
    obs_id, events, meta_row, era, grids = item
    if _ERA.get("era") != era:
        set_era(era, grids)
    from reproduce_table5 import load
    from transit_audit.exoclock import host_of
    drd = load()[0]["DRD"]
    tic = "TIC " + str(int(obs_id.split("-")[2]))
    uri = f"mast:TESS/product/{obs_id}_lc.fits"
    planets = sorted({e["planet"] for e in events})
    host = events[0]["host"]
    sector = str(int(events[0]["sector"]))
    base = {"host": host, "tic": tic, "sector": sector, "product": PRODUCT, "uri": uri, "product_obs_id": obs_id}
    windows, diags, cover = [], [], []
    try:
        t_max = float(meta_row["t_max_mjd"]) if meta_row and meta_row.get("t_max_mjd") else None
        if era == "development" and t_max is None:
            raise ValueError("MAST t_max unknown; development guard cannot be verified before request")
        path = tp.download({"tic": tic, "uri": uri, "t_max_mjd": t_max if t_max is not None else math.nan,
                            "guard_ok": era == "protected" or t_max <= tp.MAX_MJD})
        t, f, e, cad, meta = tp.read(path, "pdcsap")
    except Exception as exc:  # noqa: BLE001
        for p in planets:
            diags.append({**base, "planet": p, "status": f"read_failed: {exc!r}"[:200]})
        for ev in events:
            cover.append({"event_id": ev["event_id"], "coverage_window_at_prediction": "",
                          "coverage_in_transit_at_prediction": "", "coverage_basis": "product_unreadable"})
        return windows, diags, cover
    bjd0 = float(meta["BJDREFI"]) + float(meta["BJDREFF"])
    sha = tp.sha256(path)
    exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
    common = {"host": host, "tic": tic, "sector": int(meta["SECTOR"]), "camera": meta["CAMERA"], "ccd": meta["CCD"],
              "product": PRODUCT, "flux": "PDCSAP", "file": path.name, "file_sha256": sha, "data_rel": meta["DATA_REL"],
              "timesys": meta["TIMESYS"], "timeref": meta["TIMEREF"], "bjdrefi": meta["BJDREFI"],
              "bjdreff": meta["BJDREFF"], "error_convention": so.CONVENTION, "rule_version": so.rule_version(),
              "exp_s": round(exp_s, 2)}
    others_all = [p for p in drd if host_of(p) == host]
    by_planet = defaultdict(list)
    for ev in events:
        by_planet[ev["planet"]].append(ev)
    for planet in planets:
        d = drd[planet]
        others = [{"t0": drd[o].t0_bjd_tdb - bjd0, "per": drd[o].period_days,
                   "sigma_d": math.hypot(drd[o].sigma_t0_days, drd[o].sigma_period_days *
                                         abs((t.mean() + bjd0 - drd[o].t0_bjd_tdb) / drd[o].period_days))}
                  for o in others_all if o != planet]
        keep = so.mask_others(t, others, t.min(), t.max()) if others else np.ones(len(t), bool)
        tm, fm, em, cm = t[keep], f[keep], e[keep], cad[keep]
        idinfo = {"planet": planet, "id_method": "catalogue_period", "id_period_d": d.period_days,
                  "id_period_source": ID_SOURCE, "id_period_source_date": ID_DATE,
                  "masked_other_planets": ";".join(o for o in others_all if o != planet),
                  "masked_cadence_fraction": round(1 - keep.mean(), 4)}
        try:
            sol = so.solution(tm, fm, em, exp_s, d.period_days)
        except Exception as exc:  # noqa: BLE001
            sol = {"id_fail": f"solution_exception {exc!r}"[:150], "id": {"snr": float("nan"), "per": float("nan")}}
        diag = {**base, "planet": planet, "status": "ok" if not sol["id_fail"] else "id_failed:" + sol["id_fail"],
                "id_snr": round(sol["id"]["snr"], 2), "id_period_found_d": sol["id"]["per"], "file_sha256": sha,
                "masked_cadence_fraction": idinfo["masked_cadence_fraction"]}
        if not sol["id_fail"]:
            diag.update({"t14_min": round(sol["t14"] * 1440, 2), "half_min": round(sol["half"] * 1440, 2),
                         "shape_rchi2": round(sol["rchi_shape"], 3), "shape_at_bound": ";".join(sol["at_bound"])})
        diags.append(diag)
        t14 = sol["t14"] if not sol["id_fail"] else so.t14_guess(d.period_days)
        for ev in by_planet[planet]:
            pred = d.t0_bjd_tdb + int(ev["forecast_epoch"]) * d.period_days - bjd0
            cw, ci = coverage_at(t, pred, d.period_days, t14, cadence)
            cover.append({"event_id": ev["event_id"], "coverage_window_at_prediction": round(cw, 4),
                          "coverage_in_transit_at_prediction": round(ci, 4),
                          "coverage_basis": "quality-0 cadences at DRD prediction, unmasked light curve"})
        if sol["id_fail"]:
            continue
        for r in so.time_windows(tm, fm, em, sol, exp_s, cadence, loo=True, cad=cm):
            ref = r.get("tc", r["centre"]) + bjd0
            n = int(round((ref - d.t0_bjd_tdb) / d.period_days))
            row = {**common, **idinfo, "event_id": f"{planet}|S{common['sector']}|{PRODUCT}|D{n}",
                   "observation_id": f"{planet}|S{common['sector']}|D{n}", "drd_epoch": n,
                   "local_epoch": r["local_epoch"], "status": r["status"], "failure_reason": r["failure_reason"],
                   "shape_group_id": f"{planet}|S{common['sector']}|{PRODUCT}",
                   "coverage_window": r["coverage_window"], "coverage_in_transit": r["coverage_in_transit"],
                   "window_centre_bjd_tdb": round(r["centre"] + bjd0, 7), "t14_min": round(sol["t14"] * 1440, 2),
                   "cadenceno_first": r.get("cadenceno_first", 0), "cadenceno_last": r.get("cadenceno_last", 0),
                   "loo_shift_s": r.get("loo_shift_s", "not_estimable"), "gauss_ok": r.get("gauss_ok", False),
                   "posterior_grid_path": ""}
            if "tc" in r:
                q = r["q"]
                row.update({"tc_bjd_tdb": round(r["tc"] + bjd0, 8), "sigma_s": round(r["sig"] * 86400, 3),
                            "q025_s": round((q[5] - q[2]) * 86400, 3), "q1587_s": round((q[1] - q[2]) * 86400, 3),
                            "q8413_s": round((q[3] - q[2]) * 86400, 3), "q975_s": round((q[6] - q[2]) * 86400, 3),
                            "sigma_white_s": round(r["sig_white"] * 86400, 3), "beta": round(r["beta"], 3),
                            "rchi2": round(r["rchi"], 3), "flags": r["flags"], "n_points": r["n"]})
                if r["status"] == "timed" and not r["gauss_ok"]:
                    row["posterior_grid_path"] = so.write_grid(row["event_id"], r)
            windows.append(row)
    return windows, diags, cover


def safe(item):
    try:
        return measure_product(item)
    except Exception as exc:  # noqa: BLE001
        ev = item[1]
        return ([], [{"planet": p, "sector": str(int(ev[0]["sector"])), "product": PRODUCT, "product_obs_id": item[0],
                      "status": f"exception: {exc!r}"[:300]} for p in sorted({e["planet"] for e in ev})],
                [{"event_id": e["event_id"], "coverage_window_at_prediction": "", "coverage_in_transit_at_prediction": "",
                  "coverage_basis": "measurement_exception"} for e in ev])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--product-meta", default="", help="CSV with uri and t_max_mjd (development guard)")
    ap.add_argument("--era", choices=("development", "protected"), default="development")
    ap.add_argument("--workers", type=int, default=8)
    a = ap.parse_args(argv)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    grids = out / "grids"
    set_era(a.era, grids)
    man = list(csv.DictReader(Path(a.manifest).open()))
    meta = {}
    if a.product_meta:
        meta = {r["uri"].split("/")[-1].removesuffix("_lc.fits"): r for r in csv.DictReader(Path(a.product_meta).open())}
    groups = defaultdict(list)
    for m in man:
        groups[m["product_obs_id"]].append(m)
    items = [(k, v, meta.get(k), a.era, str(grids)) for k, v in sorted(groups.items())]
    with Pool(a.workers) as pool:
        res = pool.map(safe, items, chunksize=1)
    windows = [r for x in res for r in x[0]]
    write_csv(out / "windows.csv.gz", windows)
    write_csv(out / "products.csv", [r for x in res for r in x[1]])
    write_csv(out / "coverage.csv", [r for x in res for r in x[2]])
    receipt = {"era": a.era, "manifest_sha256": hashlib.sha256(Path(a.manifest).read_bytes()).hexdigest(),
               "products": len(items), "manifest_events": len(man), "windows": len(windows),
               "timed": sum(r["status"] == "timed" for r in windows), "rule_version": so.rule_version(),
               "measure_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "max_mjd_guard": tp.MAX_MJD, "max_btjd_guard": tp.MAX_BTJD}
    (out / "measure_receipt.json").write_text(json.dumps(receipt, indent=1, default=str) + "\n")
    print(json.dumps(receipt, default=str))


if __name__ == "__main__":
    main()
