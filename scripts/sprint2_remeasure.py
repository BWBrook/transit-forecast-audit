# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Remeasure every supported development-era transit of the sprint-1 cohort (R5, I1).

Cohort: every planet in a sprint-1 development comparison (training or scoring).
Products: S46-S73 through both access guards; production rule SPOC 120-s PDCSAP
where it exists for the sector, otherwise TESS-SPOC 200-s PDCSAP. Rule t015v3
(sprint2_outcomes): identification period from the earliest release holding the
planet among DRC, then DRB, then DRD; other DRD planets on the host masked.

    uv run scripts/sprint2_remeasure.py select     # metadata: TIC, pointing, MAST products
    uv run scripts/sprint2_remeasure.py run        # download, identify, time -> I1 outcomes
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import math
import sys
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402

OUT = ROOT / "results" / "outcomes" / so.RULE
DERIVED = ROOT / "data" / "derived" / "outcomes" / so.RULE
ISSUE = {"DRB": "2021-10-27", "DRC": "2022-09-27", "DRD": "2025-11-18"}
SOURCE = {"DRB": "ExoClock DRB updated_ephemerides (OSF wna5e)", "DRC": "ExoClock DRC catalogue (OSF p298n)",
          "DRD": "ExoClock DRD catalogue (OSF wpjtn)"}


def ephemerides():
    from reproduce_table5 import load
    eph, _, flags = load()
    return eph, flags


def cohort():
    planets = set()
    for f in glob.glob(str(ROOT / "data/derived/sprint1/*/a_1.087/c2/*events.csv")):
        planets |= {r["planet"] for r in csv.DictReader(open(f))}
    return sorted(planets)


def select(args):
    import tess_stars2px as t2p
    from sealed_era_inventory import coordinates
    from transit_audit.exoclock import host_of
    eph, _ = ephemerides()
    planets = cohort()
    coords = coordinates(planets)
    hosts = defaultdict(list)
    for p in planets:
        hosts[host_of(p)].append(p)

    def one(item):
        host, ps = item
        c = coords.get(ps[0])
        base = {"host": host, "planets": ";".join(ps)}
        if c is None or not c[2]:
            return [{**base, "status": "no_tic"}]
        ra, dec, tic, tmag, basis = c
        res = t2p.tess_stars2px_function_entry(np.array([0]), np.array([ra]), np.array([dec]), trySector=None)
        secs = sorted({int(s) for s in res[3] if tp.MIN_SECTOR <= int(s) <= tp.MAX_SECTOR})
        base.update({"tic": tic, "tmag": tmag, "coord_basis": basis, "pointing_sectors": " ".join(map(str, secs))})
        if not secs:
            return [{**base, "status": "no_s46_s73_pointing"}]
        spoc = {x["sector"]: x for x in tp.search(tic, secs, "SPOC", 120)}
        ffi = {x["sector"]: x for x in tp.search(tic, secs, "TESS-SPOC", 200)}
        rows = []
        for s in secs:
            x = spoc.get(s) or ffi.get(s)
            if x is None:
                rows.append({**base, "sector": s, "status": "no_qualified_product"})
            elif not x["guard_ok"]:
                rows.append({**base, "sector": s, "status": "guard_excluded", "t_max_mjd": x["t_max_mjd"]})
            else:
                rows.append({**base, "sector": s, "status": "selected", "product": "SPOC_120" if s in spoc else "TESS-SPOC_200",
                             "uri": x["uri"], "t_max_mjd": x["t_max_mjd"], "paired_ffi_exists": s in ffi and s in spoc})
        print(host, len(rows), flush=True)
        return rows

    with ThreadPoolExecutor(args.threads) as ex:
        res = list(ex.map(one, sorted(hosts.items())))
    OUT.mkdir(parents=True, exist_ok=True)
    tp.write_csv(OUT / "products.csv", [r for x in res for r in x])


def id_period(planet, eph):
    for rel in ("DRC", "DRB", "DRD"):
        if planet in eph[rel]:
            return eph[rel][planet].period_days, rel
    raise KeyError(planet)


def process(item):
    host, prows = item
    from transit_audit.exoclock import host_of
    eph, _ = ephemerides()
    drd = eph["DRD"]
    others_all = [p for p in drd if host_of(p) == host]
    out, prod_out = [], []
    rv = so.rule_version()
    for pr in prows:
        try:
            path = tp.download({"tic": pr["tic"], "uri": pr["uri"], "t_max_mjd": float(pr["t_max_mjd"]),
                                "guard_ok": float(pr["t_max_mjd"]) <= tp.MAX_MJD})
            t, f, e, cad, meta = tp.read(path, "pdcsap")
        except Exception as exc:  # noqa: BLE001
            prod_out.append({**pr, "status": f"read_failed: {exc!r}"[:200]})
            continue
        bjd0 = float(meta["BJDREFI"]) + float(meta["BJDREFF"])
        sha = tp.sha256(path)
        exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
        common = {"host": host, "tic": pr["tic"], "tmag": pr["tmag"], "sector": int(meta["SECTOR"]), "camera": meta["CAMERA"],
                  "ccd": meta["CCD"], "product": pr["product"], "flux": "PDCSAP", "file": path.name,
                  "file_sha256": sha, "data_rel": meta["DATA_REL"], "timesys": meta["TIMESYS"],
                  "timeref": meta["TIMEREF"], "bjdrefi": meta["BJDREFI"], "bjdreff": meta["BJDREFF"],
                  "error_convention": so.CONVENTION, "rule_version": rv, "exp_s": round(exp_s, 2)}
        for planet in pr["planets"].split(";"):
            per_cat, rel = id_period(planet, eph)
            others = [{"t0": drd[o].t0_bjd_tdb - bjd0, "per": drd[o].period_days,
                       "sigma_d": math.hypot(drd[o].sigma_t0_days, drd[o].sigma_period_days *
                                             abs((t.mean() + bjd0 - drd[o].t0_bjd_tdb) / drd[o].period_days))}
                      for o in others_all if o != planet]
            keep = so.mask_others(t, others, t.min(), t.max()) if others else np.ones(len(t), bool)
            tm, fm, em, cm = t[keep], f[keep], e[keep], cad[keep]
            idinfo = {"planet": planet, "id_method": "catalogue_period", "id_period_d": per_cat,
                      "id_period_source": SOURCE[rel], "id_period_source_date": ISSUE[rel],
                      "masked_other_planets": ";".join(o for o in others_all if o != planet),
                      "masked_cadence_fraction": round(1 - keep.mean(), 4)}
            try:
                sol = so.solution(tm, fm, em, exp_s, per_cat)
            except Exception as exc:  # noqa: BLE001
                sol = {"id_fail": f"solution_exception {exc!r}"[:150], "id": {"snr": float("nan"), "per": float("nan")}}
            pinfo = {**pr, "planet": planet, "status": "ok" if not sol["id_fail"] else "id_failed:" + sol["id_fail"],
                     "id_snr": round(sol["id"]["snr"], 2), "id_period_found_d": sol["id"]["per"],
                     "file_sha256": sha, **{k: idinfo[k] for k in ("id_period_source", "masked_cadence_fraction")}}
            d = drd[planet]
            if sol["id_fail"]:
                prod_out.append(pinfo)
                g = so.t14_guess(per_cat)
                t0 = d.t0_bjd_tdb - bjd0
                for k in range(math.floor((tm.min() - t0) / d.period_days), math.ceil((tm.max() - t0) / d.period_days) + 1):
                    c = t0 + k * d.period_days
                    cov = tp.coverage(tm, c, so.half_width(per_cat, g), cadence)
                    cin = tp.coverage(tm, c, g / 2, cadence)
                    if cov < 0.75 or cin < 0.75:
                        continue
                    out.append({**common, **idinfo, "event_id": f"{planet}|S{common['sector']}|{pr['product']}|D{k}",
                                "observation_id": f"{planet}|S{common['sector']}|D{k}", "drd_epoch": k,
                                "local_epoch": "", "status": "id_failed", "failure_reason": sol["id_fail"],
                                "predicted_bjd_tdb_drd": round(c + bjd0, 6), "shape_group_id": f"{planet}|S{common['sector']}|{pr['product']}",
                                "coverage_window": round(min(cov, 1), 4), "coverage_in_transit": round(min(cin, 1), 4),
                                "cadenceno_first": 0, "cadenceno_last": 0, "loo_shift_s": "not_estimable",
                                "gauss_ok": False, "posterior_grid_path": ""})
                continue
            pinfo.update({"t14_min": round(sol["t14"] * 1440, 2), "half_min": round(sol["half"] * 1440, 2),
                          "shape_rchi2": round(sol["rchi_shape"], 3), "shape_at_bound": ";".join(sol["at_bound"]),
                          "period_constrained": sol["id"]["period_constrained"]})
            prod_out.append(pinfo)
            for r in so.time_windows(tm, fm, em, sol, exp_s, cadence, loo=True, cad=cm):
                ref = r.get("tc", r["centre"]) + bjd0
                n = int(round((ref - d.t0_bjd_tdb) / d.period_days))
                row = {**common, **idinfo, "event_id": f"{planet}|S{common['sector']}|{pr['product']}|D{n}",
                       "observation_id": f"{planet}|S{common['sector']}|D{n}", "drd_epoch": n,
                       "local_epoch": r["local_epoch"], "status": r["status"], "failure_reason": r["failure_reason"],
                       "shape_group_id": f"{planet}|S{common['sector']}|{pr['product']}",
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
                                "q0228_s": round((q[0] - q[2]) * 86400, 3), "q9772_s": round((q[4] - q[2]) * 86400, 3),
                                "sigma_white_s": round(r["sig_white"] * 86400, 3), "beta": round(r["beta"], 3),
                                "rchi2": round(r["rchi"], 3), "flags": r["flags"], "n_points": r["n"]})
                    if r["status"] == "timed" and not r["gauss_ok"]:
                        row["posterior_grid_path"] = so.write_grid(row["event_id"], r)
                    ec = tp.match_exoclock(planet, row["tc_bjd_tdb"], so.DRD_MID)
                    if ec:
                        row.update({"exoclock_tc_bjd_tdb": ec[1], "exoclock_sigma_s": round(ec[2] * 86400, 2),
                                    "exoclock_record": ec[3], "exoclock_delta_s": round((row["tc_bjd_tdb"] - ec[1]) * 86400, 2)})
                out.append(row)
    print(host, "timed", sum(r["status"] == "timed" for r in out), "of", len(out), flush=True)
    return out, prod_out


def safe(item):
    try:
        return process(item)
    except Exception as exc:  # noqa: BLE001
        print(item[0], "FAILED", repr(exc), flush=True)
        return [], [{"host": item[0], "status": f"exception {exc!r}"[:300]}]


def run(args):
    rows = [r for r in csv.DictReader((OUT / "products.csv").open()) if r["status"] == "selected"]
    if args.only:
        rows = [r for r in rows if r["host"] in args.only.split(",")]
    for r in rows:
        try:
            tp.download({"tic": r["tic"], "uri": r["uri"], "t_max_mjd": float(r["t_max_mjd"]),
                         "guard_ok": float(r["t_max_mjd"]) <= tp.MAX_MJD})
        except Exception as exc:  # noqa: BLE001
            print("download failed", r["host"], r["sector"], exc, flush=True)
    by = defaultdict(list)
    for r in rows:
        by[r["host"]].append(r)
    with Pool(args.workers) as pool:
        res = pool.map(safe, sorted(by.items()), chunksize=1)
    dest = Path(args.out) if args.out else DERIVED
    dest.mkdir(parents=True, exist_ok=True)
    outcomes = [r for x in res for r in x[0]]
    tp.write_csv(dest / "outcomes.csv", outcomes)
    tp.write_csv(dest / "product_identification.csv", [r for x in res for r in x[1]])
    (dest / "run_receipt.json").write_text(json.dumps({
        "rule_version": so.rule_version(), "hosts": len(by), "products": len(rows), "attempted_events": len(outcomes),
        "timed": sum(r["status"] == "timed" for r in outcomes), "max_mjd_guard": tp.MAX_MJD,
        "max_btjd_guard": tp.MAX_BTJD, "protected_outcomes_accessed": False}, indent=1) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("select")
    p.add_argument("--threads", type=int, default=6)
    p.set_defaults(func=select)
    p = sub.add_parser("run")
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--only", default="")
    p.add_argument("--out", default="")
    p.set_defaults(func=run)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
