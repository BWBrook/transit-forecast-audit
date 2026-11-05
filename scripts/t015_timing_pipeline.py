# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package", "setuptools"]
# ///
"""T015: forecast-independent TESS mid-time pipeline (corrected per D035).

Development material only (D014). Access guard, in order: the MAST search is
restricted to S46-S73; a product is requested only if its MAST t_max is at most
MJD 60312.98 (end of 2024-01-03 less 0.02 d); the file is written by astroquery
without being read, and its header TSTOP must be at most BTJD 3313.49 (end of
2024-01-03, JD 2460313.5, less 0.01 d, which exceeds the largest barycentric
light time plus TDB-UTC) before the flux table is opened. Nothing after
2025-11-18 is requested (D023).

Forecast independence: period and epoch come from a blind BLS search (0.5-12 d);
each transit has a uniform +/-60-min timing prior; the shape (rp, a, inc, q1, q2)
is fitted to the sector's own data; a linear baseline per transit is solved at
every trial time. Posterior quantiles use a trapezoid CDF on a coarse 10-s grid
refined to min(1 s, sigma/25) over +/-10 sigma. Red noise is the gap-aware
time-averaging beta. See docs/t015_validation_design.md.

This entry point re-times the four D034 hosts with the corrected conventions.
The stratified validation is scripts/t015_stratified_validation.py.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mast"
TARGETS = {"HD209458b": "TIC 420814525", "WASP-69b": "TIC 248853232",
           "WASP-80b": "TIC 243921117", "HAT-P-12b": "TIC 198108326"}
MIN_SECTOR, MAX_SECTOR = 46, 73
MAX_MJD = 60313.0 - 0.02
MAX_BTJD = 3313.5 - 0.01
WINDOW_S = 3600.0
COARSE_S = 10.0
DOF_TIMING = 3


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def search(tic, sectors, author, exptime):
    import lightkurve as lk
    secs = [s for s in sectors if MIN_SECTOR <= s <= MAX_SECTOR]
    if not secs:
        return []
    res = lk.search_lightcurve(tic, mission="TESS", author=author, exptime=exptime, sector=secs)
    rows = []
    for row in res.table:
        sec = int(str(row["mission"]).split()[-1])
        if not MIN_SECTOR <= sec <= MAX_SECTOR:
            raise ValueError(f"search returned S{sec}, outside the development era")
        rows.append({"tic": tic, "sector": sec, "author": str(row["author"]), "exptime": float(row["exptime"]),
                     "t_max_mjd": float(row["t_max"]), "uri": str(row["dataURI"]),
                     "guard_ok": float(row["t_max"]) <= MAX_MJD})
    return rows


def download(row):
    from astroquery.mast import Observations
    if not row["guard_ok"]:
        raise ValueError(f"{row['uri']} t_max {row['t_max_mjd']} beyond MJD {MAX_MJD}; not requested")
    dest = RAW / row["tic"].replace(" ", "_")
    dest.mkdir(parents=True, exist_ok=True)
    path = dest / row["uri"].split("/")[-1]
    if not path.exists():
        Observations.download_file(row["uri"], local_path=str(path), cache=False)
    return path


def read(path, flux="pdcsap"):
    from astropy.io import fits
    hdr1 = fits.getheader(path, 1)
    if float(hdr1["TSTOP"]) > MAX_BTJD:
        raise ValueError(f"{path.name} TSTOP {hdr1['TSTOP']} > {MAX_BTJD}; flux not read")
    hdr0 = fits.getheader(path, 0)
    with fits.open(path) as h:
        d = h[1].data
        t = np.asarray(d["TIME"], float)
        f = np.asarray(d[flux.upper() + "_FLUX"], float)
        e = np.asarray(d[flux.upper() + "_FLUX_ERR"], float)
        q = np.asarray(d["QUALITY"], int)
        cad = np.asarray(d["CADENCENO"], int)
    ok = np.isfinite(t) & np.isfinite(f) & np.isfinite(e) & (e > 0) & (q == 0)
    t, f, e, cad = t[ok], f[ok], e[ok], cad[ok]
    med = np.median(f)
    meta = {k: hdr1.get(k) for k in ("TIMESYS", "TIMEREF", "TIMEUNIT", "BJDREFI", "BJDREFF", "TSTART", "TSTOP",
                                     "TELAPSE", "EXPOSURE", "TIMEDEL")}
    meta.update({k: hdr0.get(k) for k in ("SECTOR", "CAMERA", "CCD", "DATA_REL", "TICID", "TESSMAG", "PROCVER",
                                          "FILEVER", "ORIGIN")})
    meta["exp_s"] = float(hdr1["TIMEDEL"]) * 86400
    return t, f / med, e / med, cad, meta


def running_median(t, f, width):
    order = np.argsort(t)
    t, f = t[order], f[order]
    lo = np.searchsorted(t, t - width / 2)
    hi = np.searchsorted(t, t + width / 2)
    out = np.array([np.median(f[a:b]) for a, b in zip(lo, hi)])
    res = np.empty_like(out)
    res[order] = out
    return res


def blind_bls(t, f):
    from astropy.timeseries import BoxLeastSquares
    flat = f / running_median(t, f, 1.0)
    bls = BoxLeastSquares(t, flat)
    periods = np.exp(np.linspace(np.log(0.5), np.log(12.0), 60000))
    r = bls.power(periods, [0.04, 0.08, 0.12, 0.16])
    i = int(np.argmax(r.power))
    p0, dur = float(r.period[i]), float(r.duration[i])
    fine = np.linspace(p0 * 0.999, p0 * 1.001, 4001)
    r2 = bls.power(fine, [dur])
    j = int(np.argmax(r2.power))
    return float(r2.period[j]), float(r2.transit_time[j]), dur, float(r2.depth[j])


def supersample(exp_s):
    return max(1, math.ceil(exp_s / 30.0))


class Model:
    def __init__(self, t, per, shape, exp_s):
        import batman
        self.p = batman.TransitParams()
        self.p.t0, self.p.per, self.p.ecc, self.p.w = float(np.mean(t)), per, 0.0, 90.0
        self.set_shape(shape)
        self.m = batman.TransitModel(self.p, t, supersample_factor=supersample(exp_s), exp_time=exp_s / 86400)

    def set_shape(self, s):
        self.p.rp, self.p.a, self.p.inc = s["rp"], s["a"], s["inc"]
        sq = math.sqrt(s["q1"])
        self.p.u, self.p.limb_dark = [2 * sq * s["q2"], sq * (1 - 2 * s["q2"])], "quadratic"

    def __call__(self, tc):
        self.p.t0 = tc
        return self.m.light_curve(self.p)


def t14(per, rp, a, inc):
    b = a * np.cos(np.radians(inc))
    arg = np.sqrt(max((1 + rp) ** 2 - b * b, 1e-12)) / (a * np.sin(np.radians(inc)))
    return per / np.pi * np.arcsin(min(arg, 1.0))


def windows(t, per, tref, half):
    n = np.arange(np.floor((t.min() - tref) / per) - 1, np.ceil((t.max() - tref) / per) + 2)
    return [(int(k), tref + k * per) for k in n if np.sum(np.abs(t - (tref + k * per)) < half) > 0]


def fit_shape(t, f, e, per, centres, half, guess, exp_s):
    from scipy.optimize import least_squares
    m = np.zeros(len(t), bool)
    for c in centres:
        m |= np.abs(t - c) < half
    tt, ff, ee = t[m], f[m], e[m]
    seg = np.array([int(np.argmin(np.abs(np.asarray(centres) - ti))) for ti in tt])
    segs = [seg == s for s in np.unique(seg)]
    mod = Model(tt, per, {"rp": guess["rp"], "a": guess["a"], "inc": guess["inc"], "q1": 0.36, "q2": 0.3}, exp_s)

    def resid(x):
        tc0, rp, a, inc, q1, q2 = x
        mod.set_shape({"rp": rp, "a": a, "inc": inc, "q1": q1, "q2": q2})
        mm = mod(tc0)
        r = np.empty_like(ff)
        for k in segs:
            A = np.column_stack([mm[k], mm[k] * (tt[k] - tt[k].mean())])
            coef = np.linalg.lstsq(A / ee[k, None], ff[k] / ee[k], rcond=None)[0]
            r[k] = (ff[k] - A @ coef) / ee[k]
        return r

    x0 = [guess["tc"], guess["rp"], guess["a"], guess["inc"], guess.get("q1", 0.36), guess.get("q2", 0.3)]
    lo = [guess["tc"] - 0.05, 0.01, 1.5, 70.0, 0.0, 0.0]
    hi = [guess["tc"] + 0.05, 0.5, 40.0, 90.0, 1.0, 1.0]
    x0 = list(np.clip(x0, np.array(lo) + 1e-9, np.array(hi) - 1e-9))
    r = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac")
    dof = max(len(ff) - 6 - 2 * len(segs), 1)
    shape = dict(zip(("tc", "rp", "a", "inc", "q1", "q2"), map(float, r.x)))
    at_bound = [k for k, v, l, h in zip(shape, r.x, lo, hi) if k != "tc" and (v - l < 1e-4 * (h - l) or h - v < 1e-4 * (h - l))]
    return shape, float(np.sum(r.fun ** 2) / dof), at_bound


def _quantiles(grid, chi):
    w = np.exp(-0.5 * (chi - chi.min()))
    mass = 0.5 * (w[1:] + w[:-1]) * np.diff(grid)
    cdf = np.r_[0.0, np.cumsum(mass)]
    cdf /= cdf[-1]
    return np.interp([0.022750, 0.158655, 0.5, 0.841345, 0.977250], cdf, grid), cdf


def time_transit(t, f, e, centre, per, shape, half, exp_s, err_scale=1.0):
    """Posterior on t_c (days) under a uniform +/-60-min prior about centre."""
    m = np.abs(t - centre) < half
    tt, ff, ee = t[m], f[m], e[m] * err_scale
    tm = tt.mean()
    mod = Model(tt, per, shape, exp_s)

    def chi2(tc):
        mm = mod(tc)
        A = np.column_stack([mm, mm * (tt - tm)]) / ee[:, None]
        coef = np.linalg.lstsq(A, ff / ee, rcond=None)[0]
        return float(np.sum((ff / ee - A @ coef) ** 2)), coef

    lo, hi = centre - WINDOW_S / 86400, centre + WINDOW_S / 86400
    coarse = centre + np.arange(-WINDOW_S, WINDOW_S + COARSE_S / 2, COARSE_S) / 86400
    cchi = np.array([chi2(x)[0] for x in coarse])
    qc, cdf_c = _quantiles(coarse, cchi)
    sig_c = 0.5 * (qc[3] - qc[1])
    edge_mass = float(np.interp(lo + 300 / 86400, coarse, cdf_c) + 1 - np.interp(hi - 300 / 86400, coarse, cdf_c))
    step = min(1.0, max(sig_c * 86400 / 25, 0.05)) / 86400
    a, b = max(lo, qc[2] - 10 * sig_c), min(hi, qc[2] + 10 * sig_c)
    fine = np.arange(a, b + step / 2, step)
    fchi = np.array([chi2(x)[0] for x in fine])
    q, _ = _quantiles(fine, fchi)
    outside = float(np.interp(a, coarse, cdf_c) + 1 - np.interp(b, coarse, cdf_c))
    sig = 0.5 * (q[3] - q[1])
    best = fine[int(np.argmin(fchi))]
    _, coef = chi2(best)
    mm = mod(best)
    resid = ff - np.column_stack([mm, mm * (tt - tm)]) @ coef
    return {"tc": float(q[2]), "q": q, "sig": float(sig), "chi2_min": float(min(fchi.min(), cchi.min())),
            "n": int(m.sum()), "resid": resid, "tt": tt, "mask": m, "edge_mass": edge_mass,
            "mass_outside_fine": outside, "coarse_shift_sig": float((qc[2] - q[2]) / sig) if sig > 0 else np.inf,
            "fine_step_s": float(step * 86400)}


def beta_factor(tt, resid, cadence_days, bins_min=(10, 15, 20, 30), dof=DOF_TIMING):
    s1 = math.sqrt(float(np.sum(resid ** 2)) / max(len(resid) - dof, 1))
    betas = []
    for bmin in bins_min:
        w = bmin / 1440
        idx = np.floor((tt - tt.min()) / w).astype(int)
        nexp = w / cadence_days
        z = []
        for k in np.unique(idx):
            sel = idx == k
            n = int(sel.sum())
            if n >= 0.8 * nexp and n >= 2:
                z.append(resid[sel].mean() / (s1 / math.sqrt(n)))
        if len(z) >= 3:
            betas.append(float(np.std(z, ddof=1)))
    return max(1.0, float(np.median(betas))) if betas else 1.0


def coverage(t, centre, half, cadence_days):
    return float(np.sum(np.abs(t - centre) < half) / (2 * half / cadence_days))


def timed(t, f, e, c, per, shape, half, exp_s, cadence):
    r = time_transit(t, f, e, c, per, shape, half, exp_s)
    beta = beta_factor(r["tt"], r["resid"], cadence)
    rchi = r["chi2_min"] / max(r["n"] - DOF_TIMING, 1)
    scale = math.sqrt(max(rchi, 1.0)) * beta
    rs = time_transit(t, f, e, c, per, shape, half, exp_s, err_scale=scale)
    return r, rs, beta, rchi, scale


def flags(r):
    out = []
    if r["edge_mass"] > 1e-3:
        out.append("edge")
    if abs(r["coarse_shift_sig"]) > 0.1:
        out.append("coarse_fine_shift")
    if r["mass_outside_fine"] > 1e-4:
        out.append("mass_outside_fine")
    return ";".join(out)


def sector_solution(t, f, e, exp_s):
    """Blind BLS, shape fit and windows for one light curve."""
    per, tref, dur, depth = blind_bls(t, f)
    half = max(1.5 * dur, dur + 2 * WINDOW_S / 86400)
    cents = [c for _, c in windows(t, per, tref, half)]
    g = {"tc": tref, "rp": float(np.sqrt(max(depth, 1e-4))), "a": max(3.0, per / (np.pi * dur)), "inc": 88.0}
    shape, rchi, at_bound = fit_shape(t, f, e, per, cents, half, g, exp_s)
    dur14 = t14(per, shape["rp"], shape["a"], shape["inc"])
    half = 1.5 * dur14 + WINDOW_S / 86400
    return {"per": per, "bls_dur": dur, "bls_depth": depth, "shape": shape, "rchi_shape": rchi,
            "at_bound": at_bound, "t14": dur14, "half": half, "tref": shape["tc"],
            "wins": windows(t, per, shape["tc"], half)}


def match_exoclock(planet, tc_bjd, path):
    best = None
    for line in Path(path).read_text().splitlines()[1:]:
        f = line.split()
        if len(f) == 5 and f[0] == planet and f[3] == "space" and f[4].endswith("_TESS"):
            d = abs(float(f[1]) - tc_bjd)
            if best is None or d < best[0]:
                best = (d, float(f[1]), float(f[2]), f[4])
    return best if best and best[0] < 0.1 else None


def write_csv(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "t015_corrected"))
    args = ap.parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    drd_mid = ROOT / "data" / "raw" / "osf" / "wpjtn" / "all_mid_time_data.txt"
    v1 = {(r["planet"], r["sector"], r["local_epoch"]): r
          for r in csv.DictReader((ROOT / "results" / "t015" / "t015_events.csv").open()) if r["status"] == "timed"}
    events, products = [], []
    for planet, tic in TARGETS.items():
        for row in search(tic, range(MIN_SECTOR, MAX_SECTOR + 1), "SPOC", 120):
            path = download(row)
            t, f, e, cad, meta = read(path)
            products.append({"planet": planet, "sector": row["sector"], "file": path.name, "sha256": sha256(path),
                             "t_max_mjd": row["t_max_mjd"], **{k.lower(): v for k, v in meta.items()}})
            sol = sector_solution(t, f, e, meta["exp_s"])
            cadence = float(np.median(np.diff(t)))
            for k, c in sol["wins"]:
                if coverage(t, c, sol["half"], cadence) < 0.75 or coverage(t, c, sol["t14"] / 2, cadence) < 0.75:
                    continue
                r, rs, beta, rchi, _ = timed(t, f, e, c, sol["per"], sol["shape"], sol["half"], meta["exp_s"], cadence)
                bjd = rs["tc"] + float(meta["BJDREFI"]) + float(meta["BJDREFF"])
                ec = match_exoclock(planet, bjd, drd_mid)
                old = v1.get((planet, str(row["sector"]), str(k)))
                ev = {"planet": planet, "sector": row["sector"], "local_epoch": k, "tc_bjd_tdb": round(bjd, 7),
                      "sigma_min": round(rs["sig"] * 1440, 4), "sigma_white_min": round(r["sig"] * 1440, 4),
                      "beta_red": round(beta, 3), "reduced_chi2": round(rchi, 3), "flags": flags(rs),
                      "fine_step_s": round(rs["fine_step_s"], 3)}
                if old:
                    ev["v1_minus_corrected_s"] = round((float(old["tc_bjd_tdb"]) - bjd) * 86400, 2)
                    ev["v1_sigma_over_corrected"] = round(float(old["sigma_min"]) / (rs["sig"] * 1440), 3)
                if ec:
                    d = (bjd - ec[1]) * 1440
                    ev.update({"delta_vs_exoclock_s": round(d * 60, 2),
                               "z_vs_exoclock": round(d / math.hypot(rs["sig"] * 1440, ec[2] * 1440), 3)})
                events.append(ev)
            print(planet, row["sector"], len(events), flush=True)
    write_csv(out / "corrected_events.csv", events)
    write_csv(out / "corrected_products.csv", products)
    d = np.array([x["v1_minus_corrected_s"] for x in events if "v1_minus_corrected_s" in x])
    rat = np.array([x["v1_sigma_over_corrected"] for x in events if "v1_sigma_over_corrected" in x])
    z = np.array([x["z_vs_exoclock"] for x in events if "z_vs_exoclock" in x])
    summary = {"development_only": True, "transits_timed": len(events), "matched_v1": int(len(d)),
               "v1_minus_corrected_s": {"median": round(float(np.median(d)), 2), "min": round(float(d.min()), 2),
                                        "max": round(float(d.max()), 2)},
               "v1_sigma_over_corrected": {"median": round(float(np.median(rat)), 3), "min": round(float(rat.min()), 3),
                                           "max": round(float(rat.max()), 3)},
               "vs_exoclock": {"n": int(len(z)), "rms_z": round(float(np.sqrt(np.mean(z ** 2))), 3),
                               "median_delta_s": round(float(np.median([x["delta_vs_exoclock_s"] for x in events if "delta_vs_exoclock_s" in x])), 2)},
               "flagged": [f"{x['planet']} S{x['sector']} E{x['local_epoch']}: {x['flags']}" for x in events if x["flags"]],
               "guard": {"max_mjd_pre_request": MAX_MJD, "max_btjd_tstop": MAX_BTJD},
               "command": "uv run scripts/t015_timing_pipeline.py"}
    (out / "corrected_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
