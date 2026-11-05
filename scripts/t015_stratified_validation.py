# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""T015 stratified validation, executing docs/t015_validation_design.md (commit 26590c3).

Development era only: S56-S73 products ending by 2024-01-03 (guard in
t015_timing_pipeline). Single-DRD-planet hosts in four Tmag strata, 12 per
stratum chosen by SHA-256 rank, odd ranks calibration and even ranks validation.
Each host contributes its TESS-SPOC 200-s product and, where it exists, the SPOC
120-s product for the same sector. Injection runs at phases 0.27 and 0.73 rerun
the whole pipeline (blind BLS, shape refit, timing) on PDCSAP and SAP flux, with
real transit windows removed.

    uv run scripts/t015_stratified_validation.py select     # metadata + MAST search only
    uv run scripts/t015_stratified_validation.py run        # download, fit, inject
    uv run scripts/t015_stratified_validation.py analyse    # metrics and acceptance
"""

from __future__ import annotations

import argparse
import csv
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
import t015_timing_pipeline as tp  # noqa: E402

OUT = ROOT / "results" / "t015_validation"
SALT = "t015v2"
SEED = 20261106
SECTORS = range(56, 74)
STRATA = [("A_lt10", -99, 10.0), ("B_10_11", 10.0, 11.0), ("C_11_12", 11.0, 12.0), ("D_12_13.5", 12.0, 13.5)]
PER_STRATUM = 12
PHASES = (0.27, 0.73)
D034_HOSTS = {"HD209458", "WASP-69", "WASP-80", "HAT-P-12"}
DRD_MID = ROOT / "data" / "raw" / "osf" / "wpjtn" / "all_mid_time_data.txt"


def rank(s):
    return hashlib.sha256(s.encode()).hexdigest()


def frame():
    import tess_stars2px as t2p
    from sealed_era_inventory import coordinates
    from transit_audit.exoclock import host_of, read_catalogue
    D = read_catalogue(ROOT / "data" / "raw" / "osf" / "wpjtn" / "catalogue_of_ephemerides.txt")
    by_host = defaultdict(list)
    for p in D:
        by_host[host_of(p)].append(p)
    coords = coordinates(sorted(D))
    rows = []
    for host, planets in sorted(by_host.items()):
        base = {"host": host, "planets": ";".join(planets)}
        if len(planets) != 1:
            rows.append({**base, "frame": "excluded_multi_drd_planet"})
            continue
        p = planets[0]
        if host in D034_HOSTS:
            rows.append({**base, "frame": "excluded_d034_development_host"})
            continue
        c = coords.get(p)
        if c is None or not c[2] or c[3] == "":
            rows.append({**base, "frame": "excluded_no_tic_or_tmag"})
            continue
        ra, dec, tic, tmag, _ = c
        tmag = float(tmag)
        stratum = next((s for s, lo, hi in STRATA if lo <= tmag < hi), None)
        res = t2p.tess_stars2px_function_entry(np.array([0]), np.array([ra]), np.array([dec]), trySector=None)
        secs = sorted({int(s) for s in res[3] if int(s) in SECTORS})
        row = {**base, "planet": p, "tic": tic, "tmag": round(tmag, 3), "stratum": stratum or "",
               "period_d": D[p].period_days, "tess_point_sectors": " ".join(map(str, secs)), "rank": rank(f"{SALT}:{tic}")}
        if stratum is None:
            row["frame"] = "excluded_tmag_outside_strata"
        elif not secs:
            row["frame"] = "excluded_no_s56_s73_pointing"
        else:
            row["frame"] = "in_frame"
        rows.append(row)
    return rows


def select(args):
    OUT.mkdir(parents=True, exist_ok=True)
    fr = frame()
    chosen = []
    for stratum, _, _ in STRATA:
        pool = sorted((r for r in fr if r["frame"] == "in_frame" and r["stratum"] == stratum), key=lambda r: r["rank"])
        n = 0
        for r in pool:
            if n == PER_STRATUM:
                r["selection"] = "not_reached"
                continue
            secs = [int(s) for s in r["tess_point_sectors"].split()]
            ffi = [x for x in tp.search(r["tic"], secs, "TESS-SPOC", 200) if x["guard_ok"]]
            if not ffi:
                r["selection"] = "no_tess_spoc_200s_passing_guard"
                print(stratum, r["host"], r["selection"], flush=True)
                continue
            pick = min(ffi, key=lambda x: rank(f"{SALT}:{r['tic']}:{x['sector']}"))
            spoc = [x for x in tp.search(r["tic"], [pick["sector"]], "SPOC", 120) if x["guard_ok"]]
            n += 1
            r.update({"selection": "selected", "stratum_rank": n, "set": "calibration" if n % 2 else "validation",
                      "sector": pick["sector"], "ffi_uri": pick["uri"], "ffi_t_max_mjd": pick["t_max_mjd"],
                      "spoc_uri": spoc[0]["uri"] if spoc else "", "spoc_t_max_mjd": spoc[0]["t_max_mjd"] if spoc else ""})
            chosen.append(r)
            print(stratum, n, r["host"], r["tmag"], "S%d" % pick["sector"], "spoc" if spoc else "ffi-only", flush=True)
    tp.write_csv(OUT / "frame_and_selection.csv", fr)
    print(len(chosen), "hosts selected")


def inject_flux(t, f, centres, per, shape, half, exp_s):
    out = f.copy()
    for c in centres:
        m = np.abs(t - c) < half
        if m.any():
            out[m] = f[m] * tp.Model(t[m], per, shape, exp_s)(c)
    return out


def time_all(t, f, e, sol, exp_s, cadence, loo=False):
    rows = []
    for k, c in sol["wins"]:
        cov = tp.coverage(t, c, sol["half"], cadence)
        cin = tp.coverage(t, c, sol["t14"] / 2, cadence)
        if cov < 0.75 or cin < 0.75:
            rows.append({"local_epoch": k, "status": "excluded_coverage", "centre": c})
            continue
        r, rs, beta, rchi, scale = tp.timed(t, f, e, c, sol["per"], sol["shape"], sol["half"], exp_s, cadence)
        row = {"local_epoch": k, "status": "timed", "centre": c, "tc": rs["tc"], "q": rs["q"], "sig": rs["sig"],
               "sig_white": r["sig"], "tc_white": r["tc"], "q_white": r["q"], "beta": beta, "rchi": rchi,
               "flags": tp.flags(rs), "n": rs["n"]}
        if loo:
            others = [cc for kk, cc in sol["wins"] if kk != k]
            if len(others) >= 2:
                sh, _, _ = tp.fit_shape(t, f, e, sol["per"], others, sol["half"], sol["shape"], exp_s)
                rl = tp.time_transit(t, f, e, c, sol["per"], sh, sol["half"], exp_s, err_scale=scale)
                row["loo_shift_s"] = (rl["tc"] - rs["tc"]) * 86400
        rows.append(row)
    return rows


def process(host):
    """All products, fluxes and injection runs for one selected host."""
    rng = np.random.default_rng([SEED, int(host["tic"].split()[-1])])
    draws = {ph: (ph + rng.uniform(-0.02, 0.02), rng.uniform(-2, 2, 64) / 1440) for ph in PHASES}
    prods = [("TESS-SPOC_200", host["ffi_uri"], host["ffi_t_max_mjd"])]
    if host["spoc_uri"]:
        prods.append(("SPOC_120", host["spoc_uri"], host["spoc_t_max_mjd"]))
    products, real, inj, runs = [], [], [], []
    base = {"host": host["host"], "planet": host["planet"], "tic": host["tic"], "tmag": host["tmag"],
            "stratum": host["stratum"], "set": host["set"], "sector": host["sector"]}
    for ptype, uri, tmax in prods:
        try:
            path = tp.download({"tic": host["tic"], "uri": uri, "t_max_mjd": float(tmax),
                                "guard_ok": float(tmax) <= tp.MAX_MJD})
        except Exception as exc:  # noqa: BLE001
            products.append({**base, "product": ptype, "status": f"download_failed: {exc}"})
            continue
        for flux in ("pdcsap", "sap"):
            pb = {**base, "product": ptype, "flux": flux}
            try:
                t, f, e, cad, meta = tp.read(path, flux)
            except (ValueError, KeyError) as exc:
                products.append({**pb, "status": f"read_failed: {exc}"})
                continue
            exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
            sol = tp.sector_solution(t, f, e, exp_s)
            pratio = sol["per"] / float(host["period_d"])
            prow = {**pb, "file": path.name, "sha256": tp.sha256(path), "data_rel": meta["DATA_REL"],
                    "timesys": meta["TIMESYS"], "timeref": meta["TIMEREF"], "tstop_btjd": meta["TSTOP"],
                    "exp_s": round(exp_s, 2), "n_cadences": len(t), "bls_period_d": sol["per"],
                    "bls_over_catalogue_period": round(pratio, 6), "shape_rchi2": round(sol["rchi_shape"], 3),
                    "shape_at_bound": ";".join(sol["at_bound"]), "t14_min": round(sol["t14"] * 1440, 2),
                    **{f"shape_{k}": round(v, 6) for k, v in sol["shape"].items() if k != "tc"}}
            if abs(pratio - 1) > 0.005:
                products.append({**prow, "status": "bls_misidentified"})
                continue
            products.append({**prow, "status": "ok"})
            bjd0 = float(meta["BJDREFI"]) + float(meta["BJDREFF"])
            for r in time_all(t, f, e, sol, exp_s, cadence, loo=(flux == "pdcsap")):
                row = {**pb, "local_epoch": r["local_epoch"], "status": r["status"]}
                if r["status"] == "timed":
                    bjd = r["tc"] + bjd0
                    row.update({"tc_bjd_tdb": round(bjd, 7), "sigma_s": round(r["sig"] * 86400, 2),
                                "sigma_white_s": round(r["sig_white"] * 86400, 2), "beta": round(r["beta"], 3),
                                "rchi2": round(r["rchi"], 3), "flags": r["flags"], "n_points": r["n"],
                                "loo_shift_s": round(r.get("loo_shift_s", float("nan")), 2)})
                    ec = tp.match_exoclock(host["planet"], bjd, DRD_MID) if flux == "pdcsap" else None
                    if ec:
                        d = (bjd - ec[1]) * 86400
                        row.update({"exoclock_delta_s": round(d, 2), "exoclock_sigma_s": round(ec[2] * 86400, 2),
                                    "exoclock_z": round(d / math.hypot(r["sig"] * 86400, ec[2] * 86400), 3)})
                real.append(row)
            real_c = [sol["tref"] + k * sol["per"] for k in
                      range(int(np.floor((t.min() - sol["tref"]) / sol["per"])) - 1,
                            int(np.ceil((t.max() - sol["tref"]) / sol["per"])) + 2)]
            keep = np.ones(len(t), bool)
            for c in real_c:
                keep &= np.abs(t - c) >= sol["half"]
            ph1, ph2 = (draws[p][0] for p in PHASES)
            gap = min(ph1, 1 - ph2, abs(ph2 - ph1)) * sol["per"]
            for ph in PHASES:
                phj, offs = draws[ph]
                rb = {**pb, "phase": round(phj, 4)}
                if gap <= 2 * sol["half"]:
                    runs.append({**rb, "status": "dropped_window_overlap"})
                    continue
                ks = range(int(np.floor((t.min() - sol["tref"]) / sol["per"])) - 1,
                           int(np.ceil((t.max() - sol["tref"]) / sol["per"])) + 2)
                truth = {k: sol["tref"] + (k + phj) * sol["per"] + offs[(k - ks.start) % 64] for k in ks}
                ti, ei = t[keep], e[keep]
                fi = inject_flux(ti, f[keep], list(truth.values()), sol["per"], sol["shape"], sol["half"], exp_s)
                si = tp.sector_solution(ti, fi, ei, exp_s)
                ok_p = abs(si["per"] / sol["per"] - 1) < 0.001
                tv = np.array(list(truth.values()))
                ok_ph = np.min(np.abs(tv - si["tref"])) < sol["half"]
                if not (ok_p and ok_ph):
                    runs.append({**rb, "status": "bls_injected_not_recovered", "bls_period_d": si["per"]})
                    continue
                rr = time_all(ti, fi, ei, si, exp_s, float(np.median(np.diff(ti))))
                runs.append({**rb, "status": "ok", "shape_rchi2": round(si["rchi_shape"], 3),
                             "shape_at_bound": ";".join(si["at_bound"]),
                             **{f"refit_{k}": round(v, 6) for k, v in si["shape"].items() if k != "tc"}})
                for r in rr:
                    row = {**rb, "status": r["status"], "local_epoch": r["local_epoch"]}
                    if r["status"] == "timed":
                        tru = tv[int(np.argmin(np.abs(tv - r["tc"])))]
                        q, qw = r["q"], r["q_white"]
                        row.update({"err_s": round((r["tc"] - tru) * 86400, 3), "sigma_s": round(r["sig"] * 86400, 3),
                                    "z": round((r["tc"] - tru) / r["sig"], 4),
                                    "z_white": round((r["tc_white"] - tru) / r["sig_white"], 4),
                                    "lo95_s": round((q[2] - q[0]) * 86400, 3), "lo68_s": round((q[2] - q[1]) * 86400, 3),
                                    "hi68_s": round((q[3] - q[2]) * 86400, 3), "hi95_s": round((q[4] - q[2]) * 86400, 3),
                                    "cover68": bool(q[1] <= tru <= q[3]), "cover95": bool(q[0] <= tru <= q[4]),
                                    "cover95_white": bool(qw[0] <= tru <= qw[4]), "beta": round(r["beta"], 3),
                                    "rchi2": round(r["rchi"], 3), "flags": r["flags"]})
                    inj.append(row)
    print(host["stratum"], host["host"], "done", sum(1 for x in inj if x.get("status") == "timed"), flush=True)
    return products, real, inj, runs


def safe_process(host):
    try:
        return process(host)
    except Exception as exc:  # noqa: BLE001
        print(host["host"], "FAILED", repr(exc), flush=True)
        return ([{"host": host["host"], "planet": host["planet"], "stratum": host["stratum"], "set": host["set"],
                  "product": "TESS-SPOC_200", "flux": "pdcsap", "status": f"exception: {exc!r}"}], [], [], [])


def run(args):
    hosts = [r for r in csv.DictReader((OUT / "frame_and_selection.csv").open()) if r.get("selection") == "selected"]
    for h in hosts:
        for key in ("ffi", "spoc"):
            if h[f"{key}_uri"]:
                tp.download({"tic": h["tic"], "uri": h[f"{key}_uri"], "t_max_mjd": float(h[f"{key}_t_max_mjd"]),
                             "guard_ok": float(h[f"{key}_t_max_mjd"]) <= tp.MAX_MJD})
    with Pool(args.workers) as pool:
        res = pool.map(safe_process, hosts, chunksize=1)
    names = ("products", "real_transits", "injections", "injection_runs")
    for i, name in enumerate(names):
        tp.write_csv(OUT / f"{name}.csv", [row for r in res for row in r[i]])


def _stats(rows):
    z = np.array([r["z"] for r in rows])
    err = np.array([r["err_s"] for r in rows])
    return {"n": len(rows), "z_rms": float(np.sqrt(np.mean(z ** 2))), "median_bias_s": float(np.median(err)),
            "median_bias_sigma": float(np.median(z)), "cover68": float(np.mean([r["cover68"] for r in rows])),
            "cover95": float(np.mean([r["cover95"] for r in rows])), "abs_z_gt3": float(np.mean(np.abs(z) > 3))}


def boot(rows, B, rng):
    by = defaultdict(list)
    for r in rows:
        by[r["host"]].append(r)
    hosts = sorted(by)
    point = _stats(rows)
    point["hosts"] = len(hosts)
    host_rms = [math.sqrt(np.mean([x["z"] ** 2 for x in by[h]])) for h in hosts]
    point["host_z_rms_quartiles"] = [round(float(v), 3) for v in np.percentile(host_rms, [25, 50, 75])]
    if len(hosts) < 2:
        return point
    zz = {h: np.array([x["z"] for x in by[h]]) for h in hosts}
    c68 = {h: np.array([x["cover68"] for x in by[h]], float) for h in hosts}
    c95 = {h: np.array([x["cover95"] for x in by[h]], float) for h in hosts}
    sims = []
    for _ in range(B):
        pick = rng.integers(0, len(hosts), len(hosts))
        z = np.concatenate([zz[hosts[i]] for i in pick])
        sims.append((math.sqrt(np.mean(z ** 2)), np.median(z),
                     np.mean(np.concatenate([c68[hosts[i]] for i in pick])),
                     np.mean(np.concatenate([c95[hosts[i]] for i in pick]))))
    s = np.array(sims)
    for j, k in enumerate(("z_rms", "median_bias_sigma", "cover68", "cover95")):
        point[k + "_ci95"] = [round(float(v), 4) for v in np.percentile(s[:, j], [2.5, 97.5])]
    return point


def accept(st, failure_rate):
    checks = {"cover95_ge_0.90": st["cover95"] >= 0.90,
              "cover95_lower_ge_0.85": st.get("cover95_ci95", [0])[0] >= 0.85,
              "z_rms_ci_includes_1": st.get("z_rms_ci95", [9, 0])[0] <= 1 <= st.get("z_rms_ci95", [9, 0])[1],
              "z_rms_upper_le_1.25": st.get("z_rms_ci95", [0, 9])[1] <= 1.25,
              "abs_median_bias_lt_0.1sigma": abs(st["median_bias_sigma"]) < 0.1,
              "failure_rate_le_0.20": failure_rate <= 0.20}
    return {"checks": checks, "freeze_ready": all(checks.values())}


def analyse(args):
    rd = lambda n: list(csv.DictReader((OUT / n).open()))
    inj = [r for r in rd("injections.csv") if r["status"] == "timed"]
    for r in inj:
        for k in ("z", "err_s", "z_white", "sigma_s", "lo95_s", "lo68_s", "hi68_s", "hi95_s"):
            r[k] = float(r[k])
        for k in ("cover68", "cover95", "cover95_white"):
            r[k] = r[k] == "True"
    runs, prods, real = rd("injection_runs.csv"), rd("products.csv"), rd("real_transits.csv")
    rng = np.random.default_rng(SEED)
    out = {"design": "docs/t015_validation_design.md @ 26590c3", "bootstrap": args.bootstrap, "groups": {}}

    def fail_rate(sel):
        ps = [p for p in prods if sel(p)]
        rs = [r for r in runs if sel(r)]
        bad = sum(p["status"] != "ok" for p in ps) + sum(r["status"] == "bls_injected_not_recovered" for r in rs)
        edge = sum(1 for r in inj if sel(r) and "edge" in r["flags"])
        return {"products": len(ps), "products_failed": sum(p["status"] != "ok" for p in ps),
                "runs": len(rs), "runs_bls_failed": sum(r["status"] == "bls_injected_not_recovered" for r in rs),
                "runs_dropped_overlap": sum(r["status"] == "dropped_window_overlap" for r in rs),
                "edge_flagged_injections": edge,
                "failure_rate": (bad + edge) / max(len(ps) + len(rs), 1)}

    for ptype in ("TESS-SPOC_200", "SPOC_120"):
        for flux in ("pdcsap", "sap"):
            for sset in ("validation", "calibration"):
                for stratum in ["all"] + [s for s, _, _ in STRATA]:
                    sel = lambda r, ptype=ptype, flux=flux, sset=sset, stratum=stratum: (
                        r["product"] == ptype and r["flux"] == flux and r["set"] == sset
                        and (stratum == "all" or r["stratum"] == stratum))
                    rows = [r for r in inj if sel(r)]
                    if not rows:
                        continue
                    st = boot(rows, args.bootstrap if stratum == "all" or sset == "validation" else 2000, rng)
                    fr = fail_rate(sel)
                    st["failures"] = fr
                    st["cover95_white"] = float(np.mean([r["cover95_white"] for r in rows]))
                    st["z_rms_white"] = float(np.sqrt(np.mean([r["z_white"] ** 2 for r in rows])))
                    if sset == "validation":
                        st["acceptance"] = accept(st, fr["failure_rate"])
                    out["groups"][f"{ptype}|{flux}|{sset}|{stratum}"] = st
    for ptype in ("TESS-SPOC_200", "SPOC_120"):
        cal = [r for r in inj if r["product"] == ptype and r["flux"] == "pdcsap" and r["set"] == "calibration"]
        val = [r for r in inj if r["product"] == ptype and r["flux"] == "pdcsap" and r["set"] == "validation"]
        if not cal or not val:
            continue
        k = math.sqrt(np.mean([r["z"] ** 2 for r in cal]))
        scaled = [{**r, "z": r["z"] / k, "cover68": -k * r["lo68_s"] <= -r["err_s"] <= k * r["hi68_s"],
                   "cover95": -k * r["lo95_s"] <= -r["err_s"] <= k * r["hi95_s"]} for r in val]
        out["groups"][f"{ptype}|pdcsap|validation|all|secondary_k"] = {"k_from_calibration": round(k, 4),
                                                                        **boot(scaled, args.bootstrap, rng)}
    timed = [r for r in real if r["status"] == "timed"]
    ez = np.array([float(r["exoclock_z"]) for r in timed if r.get("exoclock_z")])
    pair = []
    by = defaultdict(list)
    for r in timed:
        if r["flux"] == "pdcsap":
            by[r["host"]].append(r)
    for h, rs in by.items():
        a = [r for r in rs if r["product"] == "SPOC_120"]
        b = [r for r in rs if r["product"] == "TESS-SPOC_200"]
        for x in a:
            m = [y for y in b if abs(float(y["tc_bjd_tdb"]) - float(x["tc_bjd_tdb"])) < 0.05]
            if m:
                d = (float(m[0]["tc_bjd_tdb"]) - float(x["tc_bjd_tdb"])) * 86400
                pair.append((d, d / math.hypot(float(x["sigma_s"]), float(m[0]["sigma_s"])),
                             float(m[0]["sigma_s"]) / float(x["sigma_s"])))
    pair = np.array(pair) if pair else np.zeros((0, 3))
    out["real_transits"] = {
        "timed_by_product_flux": {f"{p}|{f}": sum(1 for r in timed if r["product"] == p and r["flux"] == f)
                                  for p in ("TESS-SPOC_200", "SPOC_120") for f in ("pdcsap", "sap")},
        "exoclock_matched": int(len(ez)), "exoclock_z_rms": round(float(np.sqrt(np.mean(ez ** 2))), 3) if len(ez) else None,
        "exoclock_max_abs_z": round(float(np.max(np.abs(ez))), 3) if len(ez) else None,
        "ffi_minus_spoc": {"n": int(len(pair)),
                           "median_s": round(float(np.median(pair[:, 0])), 2) if len(pair) else None,
                           "z_rms": round(float(np.sqrt(np.mean(pair[:, 1] ** 2))), 3) if len(pair) else None,
                           "median_sigma_ratio_ffi_over_spoc": round(float(np.median(pair[:, 2])), 3) if len(pair) else None},
        "loo_shift_abs_median_s": round(float(np.nanmedian([abs(float(r["loo_shift_s"])) for r in timed if r["flux"] == "pdcsap"])), 2),
    }
    out["products"] = {s: sum(1 for p in prods if p["status"] == s) for s in sorted({p["status"] for p in prods})}
    out["light_curves_after_2025_11_18"] = 0
    out["command"] = "uv run scripts/t015_stratified_validation.py analyse"
    (OUT / "validation_summary.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    prim = out["groups"].get("TESS-SPOC_200|pdcsap|validation|all")
    print(json.dumps(prim, indent=1, default=float))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("step", choices=["select", "run", "analyse"])
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--bootstrap", type=int, default=10000)
    args = ap.parse_args(argv)
    {"select": select, "run": run, "analyse": analyse}[args.step](args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
