# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Sprint 2 outcome rule t015v3: identification, attempt/truth ledger and controls.

Development era only (S46-S73, both access guards in t015_timing_pipeline).
Changes from t015v2 (D039), all prespecified in docs/sprint2_outcome_design.md:

* identification: BLS restricted to the catalogue period +/-0.5%, epoch blind,
  depth SNR >= 7, other DRD planets on the host masked;
* windows: 1.5 T14 + 60 min, or T14/2 + 90 min when P < 1.4 d (R7);
* one ledger row per intended injected truth, written before any fit, with a
  one-to-one assignment of recovered windows (60-min gate) and a terminal status;
* exact 2.5/97.5% posterior quantiles, gauss_ok and likelihood grids (I1);
* controls: real-window subtraction instead of removal, and a misspecified
  injected shape with spot-crossing bumps.

    uv run scripts/sprint2_outcomes.py run --sample dev        # D039 hosts, inspected
    uv run scripts/sprint2_outcomes.py idtests                 # identification boundary
    uv run scripts/sprint2_outcomes.py select-confirm          # metadata only
    uv run scripts/sprint2_outcomes.py run --sample confirm    # after the design commit
    uv run scripts/sprint2_outcomes.py analyse --sample dev|confirm
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import subprocess
import sys
from collections import defaultdict
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import t015_timing_pipeline as tp  # noqa: E402

RULE = "t015v3"
CONVENTION = "t015v3_beta_chi"
SEED = 20261107
SALT = "t015v2"
SHORT_P = 1.4
ID_FRAC = 0.005
ID_SNR = 7.0
GATE = tp.WINDOW_S / 86400
PHASES = (0.27, 0.73)
STRATA = [("A_lt10", -99, 10.0), ("B_10_11", 10.0, 11.0), ("C_11_12", 11.0, 12.0), ("D_12_13.5", 12.0, 13.5)]
OUT = ROOT / "results" / "sprint2"
DRD_CAT = ROOT / "data" / "raw" / "osf" / "wpjtn" / "catalogue_of_ephemerides.txt"
DRD_MID = ROOT / "data" / "raw" / "osf" / "wpjtn" / "all_mid_time_data.txt"
GRIDS = ROOT / "data" / "derived" / "outcomes" / RULE / "grids"


def rule_version():
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    h = hashlib.sha256((HERE / "sprint2_outcomes.py").read_bytes() + (HERE / "t015_timing_pipeline.py").read_bytes())
    return f"{RULE}@{head}+{h.hexdigest()[:12]}"


# t015v3c: equal-host least squares of host mean z^2 on (Tmag - 11), 45 inspected
# development hosts (production set, removal mode), fitted 2026-11-07 before the
# confirmation sample was drawn or downloaded. sigma_c = sigma * TMAG_G(Tmag).
TMAG_COEF = (0.88566859, -0.09191112)


def tmag_multiplier(tmag):
    x = min(max(float(tmag), 8.0), 13.5) - 11.0
    return math.sqrt(max(TMAG_COEF[0] + TMAG_COEF[1] * x, 0.25))


def half_width(per, t14):
    return t14 / 2 + 90 / 1440 if per < SHORT_P else 1.5 * t14 + 60 / 1440


def t14_guess(per):
    return 13 / 24 * (per / 365.25) ** (1 / 3)


def identify(t, f, e, per_cat):
    """Catalogue-period BLS: period within +/-ID_FRAC, every epoch searched."""
    from astropy.timeseries import BoxLeastSquares
    g = t14_guess(per_cat)
    durs = np.geomspace(0.3 * g, 2.5 * g, 8)
    durs = durs[durs < 0.25 * per_cat]
    if not len(durs):
        durs = np.array([0.2 * per_cat])
    flat = f / tp.running_median(t, f, max(1.0, 4 * durs.max()))
    bls = BoxLeastSquares(t, flat, dy=e)
    n = max(401, int(math.ceil(2 * ID_FRAC * (t.max() - t.min()) / (durs.min() / 8))))
    periods = per_cat * (1 + np.linspace(-ID_FRAC, ID_FRAC, n))
    r = bls.power(periods, durs)
    i = int(np.argmax(r.power))
    p0, dur = float(r.period[i]), float(r.duration[i])
    fine = np.linspace(max(p0 * (1 - 2e-4), periods[0]), min(p0 * (1 + 2e-4), periods[-1]), 801)
    r2 = bls.power(fine, [dur])
    j = int(np.argmax(r2.power))
    per = float(r2.period[j])
    constrained = ID_FRAC * (t.max() - t.min()) > dur
    if not constrained:
        r3 = bls.power([per_cat], [dur])
        per, j, r2 = per_cat, 0, r3
    return {"per": per, "tref": float(r2.transit_time[j]), "dur": dur, "depth": float(r2.depth[j]),
            "snr": float(r2.depth_snr[j]), "period_constrained": bool(constrained),
            "boundary": bool(constrained and abs(per / per_cat - 1) > 0.9 * ID_FRAC)}


def id_failure(idr):
    if not np.isfinite(idr["snr"]) or idr["snr"] < ID_SNR:
        return f"id_snr_{idr['snr']:.1f}_lt_{ID_SNR:g}"
    if idr["boundary"]:
        return "id_period_at_search_boundary"
    if idr["depth"] <= 0:
        return "id_nonpositive_depth"
    return ""


def solution(t, f, e, exp_s, per_cat):
    idr = identify(t, f, e, per_cat)
    sol = {"id": idr, "id_fail": id_failure(idr)}
    if sol["id_fail"]:
        return sol
    per, tref, dur = idr["per"], idr["tref"], idr["dur"]
    half = max(1.5 * dur, dur + 2 * GATE)
    if per < SHORT_P:
        half = min(half, 0.3 * per)
    cents = [c for _, c in tp.windows(t, per, tref, half)]
    ga = max(3.0, per / (np.pi * dur))
    g = {"tc": tref, "rp": float(np.sqrt(max(idr["depth"], 1e-4))), "a": ga, "inc": 88.0,
         "a_lo": max(1.5, ga / 4), "a_hi": min(tp.A_MAX, ga * 4)}
    shape, rchi, at_bound = tp.fit_shape(t, f, e, per, cents, half, g, exp_s)
    d14 = tp.t14(per, shape["rp"], shape["a"], shape["inc"])
    if not np.isfinite(d14) or d14 < 0.25 * dur:
        sol["id_fail"] = f"shape_t14_{d14 * 1440:.1f}min_inconsistent_with_bls_{dur * 1440:.0f}min"
        return sol
    half = half_width(per, d14)
    sol.update({"per": per, "shape": shape, "rchi_shape": rchi, "at_bound": at_bound, "t14": d14, "half": half,
                "tref": shape["tc"], "wins": tp.windows(t, per, shape["tc"], half)})
    return sol


def time_windows(t, f, e, sol, exp_s, cadence, loo=False, cad=None):
    rows = []
    for k, c in sol["wins"]:
        cov, cin = tp.coverage(t, c, sol["half"], cadence), tp.coverage(t, c, sol["t14"] / 2, cadence)
        base = {"local_epoch": k, "centre": c, "coverage_window": round(min(cov, 1.0), 4),
                "coverage_in_transit": round(min(cin, 1.0), 4)}
        if cov < 0.75 or cin < 0.75:
            rows.append({**base, "status": "excluded_coverage", "failure_reason": "window_or_in_transit_coverage_lt_0.75"})
            continue
        r, rs, beta, rchi, scale = tp.timed(t, f, e, c, sol["per"], sol["shape"], sol["half"], exp_s, cadence)
        q, sig = rs["q"], rs["sig"]
        lo95, hi95 = q[2] - q[5], q[6] - q[2]
        fl = tp.flags(rs)
        unresolved = bool({"coarse_fine_shift", "mass_outside_fine"} & set(fl.split(";")))
        status = "integration_unresolved" if unresolved else "edge" if "edge" in fl else "timed"
        reason = ("timing_grid_integration_unresolved:" + fl if unresolved else
                  "posterior_mass_within_5min_of_prior_edge" if "edge" in fl else "")
        row = {**base, "status": status, "failure_reason": reason,
               "tc": rs["tc"], "q": q, "sig": sig, "sig_white": r["sig"], "tc_white": r["tc"], "q_white": r["q"],
               "beta": beta, "rchi": rchi, "scale": scale, "flags": fl, "n": rs["n"],
               "resid_rms": float(np.std(r["resid"])),
               "gauss_ok": bool(not unresolved and abs(lo95 / (1.959964 * sig) - 1) <= 0.1
                                and abs(hi95 / (1.959964 * sig) - 1) <= 0.1),
               "edge_mass": rs["edge_mass"], "mass_outside_fine": rs["mass_outside_fine"],
               "coarse_shift_sig": rs["coarse_shift_sig"], "fine_step_s": rs["fine_step_s"],
               "grid": rs["grid"], "chi": rs["chi"]}
        if cad is not None:
            cc = cad[rs["mask"]]
            row["cadenceno_first"], row["cadenceno_last"] = int(cc.min()), int(cc.max())
        if loo:
            others = [cc for kk, cc in sol["wins"] if kk != k]
            row["loo_shift_s"] = "not_estimable"
            if len(others) >= 2:
                sh, _, _ = tp.fit_shape(t, f, e, sol["per"], others, sol["half"], sol["shape"], exp_s)
                rl = tp.time_transit(t, f, e, c, sol["per"], sh, sol["half"], exp_s, err_scale=scale)
                row["loo_shift_s"] = round((rl["tc"] - rs["tc"]) * 86400, 3)
        rows.append(row)
    return rows


def write_grid(event_id, r):
    """Flat-prior posterior over the +/-60-min support: proportional to the likelihood there."""
    GRIDS.mkdir(parents=True, exist_ok=True)
    x = (r["grid"] - r["tc"]) * 86400
    logd = -0.5 * (r["chi"] - r["chi"].min())
    path = GRIDS / (hashlib.sha256(event_id.encode()).hexdigest()[:20] + ".json")
    path.write_text(json.dumps({"event_id": event_id, "kind": "posterior", "prior": "uniform",
                                "prior_constant_over_support": True, "units": "seconds",
                                "coordinate": "true_midtime_minus_reported_midtime",
                                "support_s": [float(x[0]), float(x[-1])],
                                "offset_s": [round(float(v), 4) for v in x],
                                "log_density": [round(float(v), 6) for v in logd]}) + "\n")
    return str(path.relative_to(ROOT))


def mask_others(t, others, tmin, tmax):
    keep = np.ones(len(t), bool)
    for eph in others:
        hw = max(0.25, 2 * t14_guess(eph["per"])) + 3 * eph.get("sigma_d", 0.0)
        k0, k1 = math.floor((tmin - eph["t0"]) / eph["per"]) - 1, math.ceil((tmax - eph["t0"]) / eph["per"]) + 1
        for k in range(k0, k1 + 1):
            keep &= np.abs(t - (eph["t0"] + k * eph["per"])) >= hw
    return keep


# ---------------------------------------------------------------- injections

def model_train(t, centres, per, shape, half, exp_s, spots=None):
    out = np.ones(len(t))
    for i, c in enumerate(centres):
        m = np.abs(t - c) < half
        if m.any():
            out[m] *= tp.Model(t[m], per, shape, exp_s)(c)
            if spots and spots[i]:
                amp, off, wid = spots[i]
                out[m] += amp * np.exp(-0.5 * ((t[m] - c - off) / wid) ** 2)
    return out


def misspecified(shape, rng, ntr, t14):
    """Perturbed impact parameter and limb darkening, spot bumps on half the transits."""
    s = dict(shape)
    b = s["a"] * math.cos(math.radians(s["inc"]))
    b2 = min(b + 0.2, 0.85)
    s["inc"] = math.degrees(math.acos(min(b2 / s["a"], 1.0)))
    s["q1"], s["q2"] = min(s["q1"] + 0.2, 0.95), max(s["q2"] - 0.15, 0.05)
    depth = s["rp"] ** 2
    spots = [(0.2 * depth, rng.uniform(-0.35, 0.35) * t14, 0.12 * t14) if rng.random() < 0.5 else None
             for _ in range(ntr)]
    return s, spots


def assign(truths, wins):
    """One-to-one assignment of recovered window centres to truths within GATE."""
    from scipy.optimize import linear_sum_assignment
    if not truths or not wins:
        return {}
    tv, wv = np.array(truths), np.array([c for _, c in wins])
    d = np.abs(tv[:, None] - wv[None, :])
    cost = np.where(d <= GATE, d, 1e6)
    ri, ci = linear_sum_assignment(cost)
    return {int(i): (int(j), float(d[i, j])) for i, j in zip(ri, ci) if d[i, j] <= GATE}


def inject_run(t, f, e, exp_s, sol, per_cat, truths, mode, rng, base, cadence):
    """One run; returns ledger rows (one per planned truth plus spurious windows) and a run row."""
    real_c = [sol["tref"] + k * sol["per"] for k in range(
        math.floor((t.min() - sol["tref"]) / sol["per"]) - 1, math.ceil((t.max() - sol["tref"]) / sol["per"]) + 2)]
    if mode == "subtract":
        ti, fb, ei = t, f / model_train(t, real_c, sol["per"], sol["shape"], sol["half"], exp_s), e
    else:
        keep = np.ones(len(t), bool)
        for c in real_c:
            keep &= np.abs(t - c) >= sol["half"]
        ti, fb, ei = t[keep], f[keep], e[keep]
    shape, spots = (misspecified(sol["shape"], rng, len(truths), sol["t14"]) if mode == "shape"
                    else (sol["shape"], None))
    t14i = tp.t14(sol["per"], shape["rp"], shape["a"], shape["inc"])
    halfi = half_width(sol["per"], t14i)
    fi = fb * model_train(ti, truths, sol["per"], shape, halfi, exp_s, spots)
    led = []
    for i, tr in enumerate(truths):
        cov, cin = tp.coverage(ti, tr, halfi, cadence), tp.coverage(ti, tr, t14i / 2, cadence)
        led.append({**base, "truth_id": f"{base['run_id']}|{i}", "truth_btjd": round(tr, 7),
                    "spot": bool(spots and spots[i]), "observable": bool(cov >= 0.75 and cin >= 0.75),
                    "truth_coverage_window": round(min(cov, 1), 4), "status": "not_recovered"})
    run = {**base, "mode": mode, "n_truths": len(truths), "n_observable": sum(r["observable"] for r in led)}
    try:
        si = solution(ti, fi, ei, exp_s, per_cat)
    except Exception as exc:  # noqa: BLE001
        for r in led:
            r["status"] = "run_failed"
        return led, {**run, "status": f"solution_exception: {exc!r}"[:200]}
    run.update({"id_snr": round(si["id"]["snr"], 2), "id_period_d": si["id"]["per"]})
    if si["id_fail"]:
        for r in led:
            r["status"] = "run_id_failed"
        return led, {**run, "status": "id_failed:" + si["id_fail"]}
    rows = time_windows(ti, fi, ei, si, exp_s, cadence)
    match = assign(truths, si["wins"])
    used = set()
    for i, r in enumerate(led):
        if i not in match:
            continue
        j, dist = match[i]
        used.add(j)
        w = rows[j]
        r.update({"window_local_epoch": w["local_epoch"], "window_centre_btjd": round(w["centre"], 7),
                  "match_dist_s": round(dist * 86400, 2), "gate_s": tp.WINDOW_S, "status": w["status"]})
        if w["status"] in ("timed", "edge"):
            tr, q, qw, sg = truths[i], w["q"], w["q_white"], w["sig"]
            r.update({"err_s": round((w["tc"] - tr) * 86400, 3), "sigma_s": round(sg * 86400, 3),
                      "z": round((w["tc"] - tr) / sg, 4), "z_white": round((w["tc_white"] - tr) / w["sig_white"], 4),
                      "cover68": bool(q[1] <= tr <= q[3]), "cover95": bool(q[5] <= tr <= q[6]),
                      "cover9545": bool(q[0] <= tr <= q[4]), "cover95_white": bool(qw[5] <= tr <= qw[6]),
                      "lo95_s": round((q[2] - q[5]) * 86400, 3), "hi95_s": round((q[6] - q[2]) * 86400, 3),
                      "beta": round(w["beta"], 3), "rchi2": round(w["rchi"], 3), "resid_rms": w["resid_rms"],
                      "sigma_white_s": round(w["sig_white"] * 86400, 3), "gauss_ok": w["gauss_ok"],
                      "flags": w["flags"]})
    for j, w in enumerate(rows):
        if j not in used:
            led.append({**base, "truth_id": "", "status": "spurious_window:" + w["status"],
                        "window_centre_btjd": round(w["centre"], 7), "observable": False})
    run.update({"status": "ok", "refit_t14_min": round(si["t14"] * 1440, 2), "shape_rchi2": round(si["rchi_shape"], 3)})
    return led, run


# ---------------------------------------------------------------- per host

def drd_catalogue():
    from transit_audit.exoclock import read_catalogue
    return read_catalogue(DRD_CAT)


def process_host(host, modes=("remove", "subtract")):
    cat = drd_catalogue()
    e_cat = cat[host["planet"]]
    rng = np.random.default_rng([SEED, int(host["tic"].split()[-1])])
    draws = {ph: (ph + rng.uniform(-0.02, 0.02), rng.uniform(-2, 2, 200) / 1440) for ph in PHASES}
    prods = [(p, host[f"{k}_uri"], host[f"{k}_t_max_mjd"]) for p, k in (("TESS-SPOC_200", "ffi"), ("SPOC_120", "spoc"))
             if host.get(f"{k}_uri")]
    base0 = {k: host[k] for k in ("host", "planet", "tic", "tmag", "stratum", "set", "sector") if k in host}
    products, real, ledger, runs = [], [], [], []
    for ptype, uri, tmax in prods:
        pb = {**base0, "product": ptype, "flux": "pdcsap"}
        t = None
        try:
            path = tp.download({"tic": host["tic"], "uri": uri, "t_max_mjd": float(tmax),
                                "guard_ok": float(tmax) <= tp.MAX_MJD})
            t, f, e, cad, meta = tp.read(path, "pdcsap")
        except Exception as exc:  # noqa: BLE001
            products.append({**pb, "status": f"read_failed: {exc!r}"[:200]})
            sol = None
        else:
            exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
            sol = solution(t, f, e, exp_s, e_cat.period_days)
            prow = {**pb, "file": path.name, "sha256": tp.sha256(path), "data_rel": meta["DATA_REL"],
                    "exp_s": round(exp_s, 2), "n_cadences": len(t), "id_snr": round(sol["id"]["snr"], 2),
                    "id_period_d": sol["id"]["per"], "id_over_catalogue": round(sol["id"]["per"] / e_cat.period_days, 6)}
            if sol["id_fail"]:
                products.append({**prow, "status": "id_failed:" + sol["id_fail"]})
            else:
                prow.update({"t14_min": round(sol["t14"] * 1440, 2), "half_min": round(sol["half"] * 1440, 2),
                             "shape_rchi2": round(sol["rchi_shape"], 3), "shape_at_bound": ";".join(sol["at_bound"]),
                             **{f"shape_{k}": round(v, 6) for k, v in sol["shape"].items() if k != "tc"}})
                products.append({**prow, "status": "ok"})
                for r in time_windows(t, f, e, sol, exp_s, cadence, loo=True):
                    row = {**pb, "local_epoch": r["local_epoch"], "status": r["status"],
                           "coverage_window": r["coverage_window"]}
                    if "tc" in r:
                        row.update({"tc_btjd": round(r["tc"], 7), "sigma_s": round(r["sig"] * 86400, 3),
                                    "sigma_white_s": round(r["sig_white"] * 86400, 3), "beta": round(r["beta"], 3),
                                    "rchi2": round(r["rchi"], 3), "resid_rms": r["resid_rms"], "flags": r["flags"],
                                    "gauss_ok": r["gauss_ok"], "loo_shift_s": r.get("loo_shift_s")})
                    real.append(row)
        for ph in PHASES:
            phj, offs = draws[ph]
            if sol is None or sol["id_fail"]:
                status = "product_read_failed" if t is None else "product_id_failed"
                for mode in modes:
                    run_id = f"{host['host']}|{ptype}|{mode}|{ph}"
                    rb = {**pb, "mode": mode, "phase": round(phj, 4), "run_id": run_id}
                    runs.append({**rb, "status": status})
                    if t is None:
                        ledger.append({**rb, "truth_id": "", "status": status, "observable": "unknown"})
                        continue
                    pc, g = e_cat.period_days, t14_guess(e_cat.period_days)
                    t0 = e_cat.t0_bjd_tdb - float(meta["BJDREFI"]) - float(meta["BJDREFF"])
                    ks = range(math.floor((t.min() - t0) / pc) - 1, math.ceil((t.max() - t0) / pc) + 2)
                    for i, k in enumerate(ks):
                        x = t0 + (k + phj) * pc
                        obs = (tp.coverage(t, x, half_width(pc, g), cadence) >= 0.75
                               and tp.coverage(t, x, g / 2, cadence) >= 0.75)
                        ledger.append({**rb, "truth_id": f"{run_id}|{i}", "truth_btjd": round(x, 7),
                                       "status": status, "observable": obs, "observable_basis": "catalogue_ephemeris"})
                continue
            per, tref, half = sol["per"], sol["tref"], sol["half"]
            gap = min(phj, 1 - phj) * per
            ks = range(math.floor((t.min() - tref) / per) - 1, math.ceil((t.max() - tref) / per) + 2)
            truths = [tref + (k + phj) * per + offs[(k - ks.start) % 200] for k in ks]
            truths = [x for x in truths if t.min() - half < x < t.max() + half]
            for mode in modes:
                run_id = f"{host['host']}|{ptype}|{mode}|{ph}"
                rb = {**pb, "mode": mode, "phase": round(phj, 4), "run_id": run_id}
                if gap <= 2 * half:
                    runs.append({**rb, "status": "dropped_window_overlap", "n_truths": len(truths)})
                    ledger += [{**rb, "truth_id": f"{run_id}|{i}", "truth_btjd": round(x, 7), "status": "run_dropped_overlap",
                                "observable": "unknown"} for i, x in enumerate(truths)]
                    continue
                led, run = inject_run(t, f, e, meta["exp_s"], sol, e_cat.period_days, truths, mode,
                                      np.random.default_rng([SEED, int(host["tic"].split()[-1]), int(ph * 100),
                                                             len(mode)]), rb, cadence)
                ledger += led
                runs.append(run)
    print(host.get("stratum"), host["host"], "timed", sum(1 for r in ledger if r.get("status") == "timed"), flush=True)
    return products, real, ledger, runs


def safe_process(args):
    host, modes = args
    try:
        return process_host(host, modes)
    except Exception as exc:  # noqa: BLE001
        print(host["host"], "FAILED", repr(exc), flush=True)
        return ([{"host": host["host"], "planet": host["planet"], "stratum": host.get("stratum"),
                  "status": f"exception: {exc!r}"[:300]}], [], [], [])


SAMPLES = {"dev": ROOT / "results" / "t015_validation" / "frame_and_selection.csv",
           "confirm": OUT / "confirm" / "selection.csv"}
MODES = {"dev": ("remove", "subtract", "shape"), "confirm": ("remove", "subtract")}


def run(args):
    hosts = [r for r in csv.DictReader(SAMPLES[args.sample].open()) if r.get("selection") == "selected"]
    if args.only:
        hosts = [h for h in hosts if h["host"] in args.only.split(",")]
    out = Path(args.out) if args.out else OUT / args.sample
    out.mkdir(parents=True, exist_ok=True)
    for h in hosts:
        for key in ("ffi", "spoc"):
            if h.get(f"{key}_uri"):
                try:
                    tp.download({"tic": h["tic"], "uri": h[f"{key}_uri"], "t_max_mjd": float(h[f"{key}_t_max_mjd"]),
                                 "guard_ok": float(h[f"{key}_t_max_mjd"]) <= tp.MAX_MJD})
                except Exception as exc:  # noqa: BLE001
                    print("download failed", h["host"], key, exc, flush=True)
    with Pool(args.workers) as pool:
        res = pool.map(safe_process, [(h, MODES[args.sample]) for h in hosts], chunksize=1)
    for i, name in enumerate(("products", "real_transits", "ledger", "runs")):
        tp.write_csv(out / f"{name}.csv", [row for r in res for row in r[i]])
    (out / "run_receipt.json").write_text(json.dumps({"rule_version": rule_version(), "sample": args.sample,
                                                      "hosts": len(hosts), "modes": MODES[args.sample],
                                                      "max_mjd_guard": tp.MAX_MJD, "max_btjd_guard": tp.MAX_BTJD},
                                                     indent=1) + "\n")


# ---------------------------------------------------------------- identification tests

def idtest_host(host):
    cat = drd_catalogue()
    pc = cat[host["planet"]].period_days
    rng = np.random.default_rng([SEED, 7, int(host["tic"].split()[-1])])
    key = "spoc" if host.get("spoc_uri") else "ffi"
    path = tp.download({"tic": host["tic"], "uri": host[f"{key}_uri"], "t_max_mjd": float(host[f"{key}_t_max_mjd"]),
                        "guard_ok": float(host[f"{key}_t_max_mjd"]) <= tp.MAX_MJD})
    t, f, e, cad, meta = tp.read(path, "pdcsap")
    exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
    sol = solution(t, f, e, exp_s, pc)
    out = []
    if sol["id_fail"]:
        return [{"host": host["host"], "status": "real_id_failed"}]
    real_c = [sol["tref"] + k * sol["per"] for k in range(
        math.floor((t.min() - sol["tref"]) / sol["per"]) - 1, math.ceil((t.max() - sol["tref"]) / sol["per"]) + 2)]
    fb = f / model_train(t, real_c, sol["per"], sol["shape"], sol["half"], exp_s)
    trials = [("period_offset", d) for d in (-0.006, -0.004, -0.002, 0.0, 0.002, 0.004, 0.006)]
    trials += [("alias", a) for a in (0.5, 2.0, 3.0)] + [("ttv_offset_min", m) for m in (30, 50, 70, 90, 120)]
    for kind, val in trials:
        ptrue = pc * (1 + val) if kind == "period_offset" else pc * val if kind == "alias" else sol["per"]
        for attempt in range(50):
            ph = rng.uniform(0, 1)
            t0 = sol["tref"] + ph * sol["per"]
            if min(ph, 1 - ph) * sol["per"] > 2 * sol["half"] + 0.05:
                break
        ks = range(math.floor((t.min() - t0) / ptrue) - 1, math.ceil((t.max() - t0) / ptrue) + 2)
        truths = [t0 + k * ptrue for k in ks]
        shifted = [i % 3 == 1 for i in range(len(truths))] if kind == "ttv_offset_min" else [False] * len(truths)
        truths = [x + (val / 1440 if s else 0) for x, s in zip(truths, shifted)]
        keep = [t.min() - sol["half"] < x < t.max() + sol["half"] for x in truths]
        truths = [x for x, k in zip(truths, keep) if k]
        shifted = [s for s, k in zip(shifted, keep) if k]
        fi = fb * model_train(t, truths, ptrue, sol["shape"], sol["half"], exp_s)
        row = {"host": host["host"], "tmag": host["tmag"], "period_cat_d": pc, "kind": kind, "value": val,
               "phase": round(ph, 4), "n_truths": len(truths)}
        try:
            si = solution(t, fi, e, exp_s, pc)
        except Exception as exc:  # noqa: BLE001
            out.append({**row, "status": f"exception {exc!r}"[:200]})
            continue
        row.update({"id_fail": si["id_fail"], "id_period_d": si["id"]["per"], "id_snr": round(si["id"]["snr"], 2)})
        if si["id_fail"]:
            out.append({**row, "status": "id_failed"})
            continue
        rows = time_windows(t, fi, e, si, exp_s, cadence)
        match = assign(truths, si["wins"])
        obs = [tp.coverage(t, x, si["half"], cadence) >= 0.75 and tp.coverage(t, x, si["t14"] / 2, cadence) >= 0.75
               for x in truths]
        matched = {j for j, _ in match.values()}
        row["spurious_timed_windows"] = sum(1 for j, w in enumerate(rows) if j not in matched and w["status"] == "timed")
        for i, x in enumerate(truths):
            st = rows[match[i][0]]["status"] if i in match else "not_recovered"
            z = ((rows[match[i][0]]["tc"] - x) / rows[match[i][0]]["sig"]) if i in match and "tc" in rows[match[i][0]] else None
            out.append({**row, "status": "ok", "truth_index": i, "shifted": shifted[i], "observable": obs[i],
                        "event_status": st, "z": None if z is None else round(z, 4)})
    print(host["host"], "idtests done", flush=True)
    return out


def idtests(args):
    hosts = [r for r in csv.DictReader(SAMPLES["dev"].open()) if r.get("selection") == "selected"]
    with Pool(args.workers) as pool:
        res = pool.map(idtest_host, hosts, chunksize=1)
    (OUT / "dev").mkdir(parents=True, exist_ok=True)
    tp.write_csv(OUT / "dev" / "identification_tests.csv", [r for x in res for r in x])


# ---------------------------------------------------------------- confirmation selection

def select_confirm(args):
    rank = lambda s: hashlib.sha256(s.encode()).hexdigest()  # noqa: E731
    fr = list(csv.DictReader(SAMPLES["dev"].open()))
    out = []
    for stratum, _, _ in STRATA:
        pool = sorted((r for r in fr if r["frame"] == "in_frame" and r["stratum"] == stratum
                       and r["selection"] == "not_reached"), key=lambda r: r["rank"])
        n = 0
        for r in pool:
            row = {k: r[k] for k in ("host", "planet", "tic", "tmag", "stratum", "period_d", "tess_point_sectors", "rank")}
            if n == args.per_stratum:
                out.append({**row, "selection": "not_reached"})
                continue
            secs = [int(s) for s in r["tess_point_sectors"].split()]
            spoc = {x["sector"]: x for x in tp.search(r["tic"], secs, "SPOC", 120) if x["guard_ok"]}
            ffi = {x["sector"]: x for x in tp.search(r["tic"], secs, "TESS-SPOC", 200) if x["guard_ok"]}
            if not spoc and not ffi:
                out.append({**row, "selection": "no_qualified_product_passing_guard"})
                continue
            pool_secs = sorted(spoc) if spoc else sorted(ffi)
            sec = min(pool_secs, key=lambda s: rank(f"{SALT}:confirm:{r['tic']}:{s}"))
            n += 1
            out.append({**row, "selection": "selected", "stratum_rank": n, "set": "confirmation", "sector": sec,
                        "ffi_uri": ffi[sec]["uri"] if sec in ffi else "",
                        "ffi_t_max_mjd": ffi[sec]["t_max_mjd"] if sec in ffi else "",
                        "spoc_uri": spoc[sec]["uri"] if sec in spoc else "",
                        "spoc_t_max_mjd": spoc[sec]["t_max_mjd"] if sec in spoc else ""})
            print(stratum, n, r["host"], "S%d" % sec, "spoc" if sec in spoc else "-", "ffi" if sec in ffi else "-",
                  flush=True)
    (OUT / "confirm").mkdir(parents=True, exist_ok=True)
    tp.write_csv(OUT / "confirm" / "selection.csv", out)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--sample", choices=("dev", "confirm"), required=True)
    p.add_argument("--workers", type=int, default=8)
    p.add_argument("--only", default="")
    p.add_argument("--out", default="")
    p.set_defaults(func=run)
    p = sub.add_parser("idtests")
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(func=idtests)
    p = sub.add_parser("select-confirm")
    p.add_argument("--per-stratum", type=int, default=30)
    p.set_defaults(func=select_confirm)
    p = sub.add_parser("analyse")
    p.add_argument("--sample", choices=("dev", "confirm"), required=True)
    p.add_argument("--bootstrap", type=int, default=10000)
    p.set_defaults(func=lambda a: __import__("sprint2_analysis").analyse(a))
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
