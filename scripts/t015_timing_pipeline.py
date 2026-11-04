# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "lightkurve==2.5.1", "batman-package", "setuptools"]
# ///
"""T015: forecast-independent TESS mid-time pipeline on inspected development events.

Development material only (D014). The guard refuses any sector beyond S73 and any
light curve whose TSTOP is after 2024-01-03 (the inspected era); nothing after
2025-11-18 is requested (D023).

Forecast independence: no ExoClock or DRD ephemeris is used to locate, window or
fit a transit. The period and epoch come from a blind BLS search (0.5-12 d) of the
sector itself; archive periods are recorded only as a sanity check. Each transit
time has a uniform prior over +/-60 min around its BLS-predicted centre. The shape
(rp, a, inc, q1, q2) is fitted to the sector's phase-folded data, and a
leave-one-out shape (excluding the transit being timed) is a sensitivity. A
linear baseline per transit is solved by weighted least squares at every grid
time, and the posterior on t_c is exp(-chi2/2) on a 2-s grid. Red noise is
measured by the time-averaging beta factor on residuals.

Injection-recovery: the fitted model is injected into real off-transit flux at
phases 0.25-0.40 and 0.60-0.75 with random offsets and refitted, giving real-noise
tests of bias and sigma calibration. Agreement with ExoClock's own mid-time for
the same epoch is a pipeline check on the same photons, not an independent
replication (Codex, docs/independent_review.md).
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "mast"
TARGETS = {"HD209458b": "TIC 420814525", "WASP-69b": "TIC 248853232",
           "WASP-80b": "TIC 243921117", "HAT-P-12b": "TIC 198108326"}  # Exoplanet Archive tic_id
MIN_SECTOR, MAX_SECTOR = 46, 73          # 2021-12-03 .. 2024-01-03, the inspected development era
MAX_BTJD = 2460313.5 - 2457000.0          # 2024-01-03 00:00 UTC, end of inspected era
WINDOW_MIN = 60.0
GRID_S = 2.0
N_INJ = 12


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fetch(target):
    import lightkurve as lk
    res = lk.search_lightcurve(target, mission="TESS", author="SPOC", exptime=120,
                               sector=list(range(MIN_SECTOR, MAX_SECTOR + 1)))
    if len(res) == 0:
        raise RuntimeError(f"no SPOC 120-s light curve for {target} in S{MIN_SECTOR}-S{MAX_SECTOR}")
    out = []
    for i in range(len(res)):
        sec = int(str(res.mission[i]).split()[-1])
        if not MIN_SECTOR <= sec <= MAX_SECTOR:
            raise ValueError("search returned a sector outside the inspected era")
        dest = RAW / target.replace(" ", "_")
        dest.mkdir(parents=True, exist_ok=True)
        lc = res[i].download(download_dir=str(dest))
        src = Path(lc.meta["FILENAME"]) if "FILENAME" in lc.meta else None
        out.append((sec, lc, src))
    return out


def clean(lc):
    from astropy.io import fits
    hdr0 = fits.getheader(lc.meta["FILENAME"], 0)
    hdr1 = fits.getheader(lc.meta["FILENAME"], 1)
    if float(hdr1["TSTOP"]) > MAX_BTJD:
        raise ValueError("light curve extends beyond the inspected era; refusing to read flux")
    t = np.asarray(lc.time.value, float)
    f = np.asarray(lc["pdcsap_flux"].value, float)
    e = np.asarray(lc["pdcsap_flux_err"].value, float)
    q = np.asarray(lc.quality.value, int)
    cad = np.asarray(lc.cadenceno.value, int)
    ok = np.isfinite(t) & np.isfinite(f) & np.isfinite(e) & (q == 0)
    t, f, e, cad = t[ok], f[ok], e[ok], cad[ok]
    med = np.median(f)
    meta = {k: hdr1.get(k) for k in ("TIMESYS", "TIMEREF", "TIMEUNIT", "BJDREFI", "BJDREFF", "TSTART", "TSTOP",
                                     "TELAPSE", "EXPOSURE", "TIMEDEL")}
    meta.update({k: hdr0.get(k) for k in ("SECTOR", "CAMERA", "CCD", "DATA_REL", "TICID", "RA_OBJ", "DEC_OBJ",
                                          "PROCVER", "FILEVER")})
    return t, f / med, e / med, cad, meta


def blind_bls(t, f):
    from astropy.timeseries import BoxLeastSquares
    flat = f / _running_median(t, f, 1.0)
    bls = BoxLeastSquares(t, flat)
    periods = np.exp(np.linspace(np.log(0.5), np.log(12.0), 60000))
    r = bls.power(periods, [0.04, 0.08, 0.12, 0.16])
    i = int(np.argmax(r.power))
    p0, t00, dur = float(r.period[i]), float(r.transit_time[i]), float(r.duration[i])
    fine = np.linspace(p0 * 0.999, p0 * 1.001, 4001)
    r2 = bls.power(fine, [dur])
    j = int(np.argmax(r2.power))
    return float(r2.period[j]), float(r2.transit_time[j]), dur, float(r2.depth[j])


def _running_median(t, f, width):
    out = np.empty_like(f)
    for i, ti in enumerate(t):
        m = np.abs(t - ti) < width / 2
        out[i] = np.median(f[m])
    return out


def model(t, tc, per, rp, a, inc, q1, q2, supersample=7):
    import batman
    pm = batman.TransitParams()
    pm.t0, pm.per, pm.rp, pm.a, pm.inc, pm.ecc, pm.w = tc, per, rp, a, inc, 0.0, 90.0
    sq = np.sqrt(q1)
    pm.u, pm.limb_dark = [2 * sq * q2, sq * (1 - 2 * q2)], "quadratic"
    m = batman.TransitModel(pm, t, supersample_factor=supersample, exp_time=120 / 86400)
    return m.light_curve(pm)


def t14(per, rp, a, inc):
    b = a * np.cos(np.radians(inc))
    arg = np.sqrt(max((1 + rp) ** 2 - b * b, 1e-12)) / (a * np.sin(np.radians(inc)))
    return per / np.pi * np.arcsin(min(arg, 1.0))


def windows(t, per, tref, half):
    n = np.arange(np.floor((t.min() - tref) / per) - 1, np.ceil((t.max() - tref) / per) + 2)
    return [(int(k), tref + k * per) for k in n if np.sum(np.abs(t - (tref + k * per)) < half) > 0]


def fit_shape(t, f, e, per, centres, half, guess):
    from scipy.optimize import least_squares
    m = np.zeros(len(t), bool)
    for c in centres:
        m |= np.abs(t - c) < half
    tt, ff, ee = t[m], f[m], e[m]
    seg = np.array([int(np.argmin(np.abs(np.array(centres) - ti))) for ti in tt])

    def resid(x):
        tc0, rp, a, inc, q1, q2 = x
        mod = model(tt, tc0, per, rp, a, inc, q1, q2)
        r = np.empty_like(ff)
        for s in np.unique(seg):
            k = seg == s
            A = np.column_stack([mod[k], mod[k] * (tt[k] - tt[k].mean())])
            coef = np.linalg.lstsq(A / ee[k, None], ff[k] / ee[k], rcond=None)[0]
            r[k] = (ff[k] - A @ coef) / ee[k]
        return r

    x0 = [guess["tc"], guess["rp"], guess["a"], guess["inc"], 0.36, 0.3]
    lo = [guess["tc"] - 0.05, 0.01, 1.5, 70.0, 0.0, 0.0]
    hi = [guess["tc"] + 0.05, 0.5, 40.0, 90.0, 1.0, 1.0]
    r = least_squares(resid, x0, bounds=(lo, hi), x_scale="jac")
    return dict(zip(("tc", "rp", "a", "inc", "q1", "q2"), r.x)), float(np.sum(r.fun**2) / (len(ff) - 6))


def time_transit(t, f, e, centre, per, shape, half, err_scale=1.0):
    m = np.abs(t - centre) < half
    tt, ff, ee = t[m], f[m], e[m] * err_scale
    grid = centre + np.arange(-WINDOW_MIN * 60, WINDOW_MIN * 60 + GRID_S, GRID_S) / 86400
    chi = np.empty(len(grid))
    tm = tt.mean()
    for i, tc in enumerate(grid):
        mod = model(tt, tc, per, shape["rp"], shape["a"], shape["inc"], shape["q1"], shape["q2"], supersample=3)
        A = np.column_stack([mod, mod * (tt - tm)]) / ee[:, None]
        coef, res, *_ = np.linalg.lstsq(A, ff / ee, rcond=None)
        chi[i] = float(np.sum((ff / ee - A @ coef) ** 2))
    w = np.exp(-0.5 * (chi - chi.min()))
    cdf = np.cumsum(w) / w.sum()
    q16, q50, q84 = (float(np.interp(q, cdf, grid)) for q in (0.15865, 0.5, 0.84135))
    best = grid[int(np.argmin(chi))]
    mod = model(tt, best, per, shape["rp"], shape["a"], shape["inc"], shape["q1"], shape["q2"], supersample=3)
    A = np.column_stack([mod, mod * (tt - tm)])
    coef = np.linalg.lstsq(A / ee[:, None], ff / ee, rcond=None)[0]
    resid = ff - A @ coef
    edge = min(abs(q50 - grid[0]), abs(grid[-1] - q50)) * 1440
    return {"tc": q50, "sig_lo": q50 - q16, "sig_hi": q84 - q50, "chi2_min": float(chi.min()), "n": int(m.sum()),
            "resid": resid, "tt": tt, "ee": ee, "mask": m, "edge_min": edge}


def beta_factor(tt, resid, ee, bins_min=(10, 15, 20, 30)):
    s1 = np.std(resid)
    betas = []
    cad = np.median(np.diff(tt)) * 1440
    for b in bins_min:
        nb = max(int(round(b / cad)), 2)
        k = len(resid) // nb
        if k < 3:
            continue
        binned = resid[: k * nb].reshape(k, nb).mean(axis=1)
        expect = s1 / np.sqrt(nb) * np.sqrt(k / (k - 1))
        betas.append(np.std(binned) / expect)
    return max(1.0, float(np.median(betas))) if betas else 1.0


def coverage(t, centre, half, cadence_days):
    expected = 2 * half / cadence_days
    return float(np.sum(np.abs(t - centre) < half) / expected)


def match_exoclock(planet, tc_bjd, path):
    best = None
    for line in Path(path).read_text().splitlines()[1:]:
        f = line.split()
        if len(f) == 5 and f[0] == planet and f[3] == "space" and f[4].endswith("_TESS"):
            d = abs(float(f[1]) - tc_bjd)
            if best is None or d < best[0]:
                best = (d, float(f[1]), float(f[2]), f[4])
    return best if best and best[0] < 0.1 else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "t015"))
    ap.add_argument("--planets", nargs="*", default=list(TARGETS))
    ap.add_argument("--seed", type=int, default=20261105)
    args = ap.parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    drd_mid = ROOT / "data" / "raw" / "osf" / "wpjtn" / "all_mid_time_data.txt"
    events, injections, products, shapes = [], [], [], []
    for planet in args.planets:
        for sec, lc, _ in fetch(TARGETS[planet]):
            t, f, e, cad, meta = clean(lc)
            fname = Path(lc.meta["FILENAME"])
            products.append({"planet": planet, "sector": sec, "file": fname.name,
                             "local_path": str(fname.relative_to(ROOT)), "sha256": sha256(fname),
                             **{k.lower(): v for k, v in meta.items()}})
            per, tref, dur, depth = blind_bls(t, f)
            half = max(1.5 * dur, dur + 2 * WINDOW_MIN / 1440)
            cents = [c for _, c in windows(t, per, tref, half)]
            guess = {"tc": tref, "rp": float(np.sqrt(max(depth, 1e-4))), "a": max(3.0, per / (np.pi * dur)),
                     "inc": 88.0}
            shape, rchi = fit_shape(t, f, e, per, cents, half, guess)
            dur14 = t14(per, shape["rp"], shape["a"], shape["inc"])
            half = 1.5 * dur14 + WINDOW_MIN / 1440
            tref = shape["tc"]
            wins = windows(t, per, tref, half)
            shapes.append({"planet": planet, "sector": sec, "bls_period_d": per, "t14_min": dur14 * 1440,
                           "rp": shape["rp"], "a": shape["a"], "inc": shape["inc"], "q1": shape["q1"],
                           "q2": shape["q2"], "reduced_chi2_shape": rchi, "transits_in_sector": len(wins)})
            cadence = np.median(np.diff(t))
            for k, c in wins:
                cov = coverage(t, c, half, cadence)
                cov_in = coverage(t, c, dur14 / 2, cadence)
                if cov < 0.75 or cov_in < 0.75:
                    events.append({"planet": planet, "sector": sec, "local_epoch": k, "status": "excluded_coverage",
                                   "coverage_window": round(cov, 3), "coverage_in_transit": round(cov_in, 3)})
                    continue
                r = time_transit(t, f, e, c, per, shape, half)
                beta = beta_factor(r["tt"], r["resid"], r["ee"])
                rchi_w = r["chi2_min"] / max(r["n"] - 2, 1)
                scale = np.sqrt(max(rchi_w, 1.0)) * beta
                rs = time_transit(t, f, e, c, per, shape, half, err_scale=scale)
                others = [cc for kk, cc in wins if kk != k]
                loo, _ = fit_shape(t, f, e, per, others, half, {**shape, "tc": tref}) if len(others) >= 2 else (shape, 0)
                rl = time_transit(t, f, e, c, per, loo, half, err_scale=scale)
                bjd = lambda x: x + float(meta["BJDREFI"]) + float(meta["BJDREFF"])
                ec = match_exoclock(planet, bjd(rs["tc"]), drd_mid)
                cads = cad[r["mask"]]
                sig = 0.5 * (rs["sig_lo"] + rs["sig_hi"])
                row = {"planet": planet, "sector": sec, "local_epoch": k, "status": "timed",
                       "coverage_window": round(cov, 3), "coverage_in_transit": round(cov_in, 3),
                       "cadenceno_first": int(cads.min()), "cadenceno_last": int(cads.max()), "n_points": r["n"],
                       "tc_bjd_tdb": round(bjd(rs["tc"]), 7), "sigma_min": round(sig * 1440, 4),
                       "sigma_white_min": round(0.5 * (r["sig_lo"] + r["sig_hi"]) * 1440, 4),
                       "beta_red": round(beta, 3), "reduced_chi2": round(rchi_w, 3),
                       "loo_shape_shift_s": round((rl["tc"] - rs["tc"]) * 86400, 2),
                       "posterior_edge_min": round(rs["edge_min"], 1)}
                if ec:
                    d = (bjd(rs["tc"]) - ec[1]) * 1440
                    row.update({"exoclock_record": ec[3], "exoclock_tmid_bjd_tdb": ec[1],
                                "exoclock_sigma_min": round(ec[2] * 1440, 4), "delta_vs_exoclock_min": round(d, 4),
                                "z_vs_exoclock": round(d / np.hypot(sig * 1440, ec[2] * 1440), 3)})
                events.append(row)
                for j in range(N_INJ):
                    ph = rng.choice([rng.uniform(0.25, 0.40), rng.uniform(0.60, 0.75)])
                    ci = c + ph * per
                    if coverage(t, ci, half, cadence) < 0.75 or coverage(t, ci, dur14 / 2, cadence) < 0.75:
                        continue
                    off = rng.uniform(-15, 15) / 1440
                    mi = np.abs(t - ci) < half
                    inj = f.copy()
                    inj[mi] = f[mi] * model(t[mi], ci + off, per, shape["rp"], shape["a"], shape["inc"],
                                            shape["q1"], shape["q2"], supersample=3)
                    ri = time_transit(t, inj, e, ci, per, shape, half)
                    bi = beta_factor(ri["tt"], ri["resid"], ri["ee"])
                    si = np.sqrt(max(ri["chi2_min"] / max(ri["n"] - 2, 1), 1.0)) * bi
                    ri2 = time_transit(t, inj, e, ci, per, shape, half, err_scale=si)
                    sg = 0.5 * (ri2["sig_lo"] + ri2["sig_hi"])
                    sw = 0.5 * (ri["sig_lo"] + ri["sig_hi"])
                    injections.append({"planet": planet, "sector": sec, "host_epoch": k, "phase": round(ph, 3),
                                       "injected_offset_s": round(off * 86400, 2),
                                       "recovered_minus_injected_s": round((ri2["tc"] - ci - off) * 86400, 2),
                                       "sigma_s": round(sg * 86400, 2), "sigma_white_s": round(sw * 86400, 2),
                                       "z": round((ri2["tc"] - ci - off) / sg, 3),
                                       "z_white": round((ri["tc"] - ci - off) / sw, 3)})
            print(planet, sec, "timed", sum(1 for x in events if x["planet"] == planet and x.get("status") == "timed"),
                  flush=True)

    def write(name, rows):
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with (out / name).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)

    write("t015_events.csv", events)
    write("t015_injections.csv", injections)
    write("t015_products.csv", products)
    write("t015_shapes.csv", shapes)
    timed = [r for r in events if r.get("status") == "timed"]
    z_ec = np.array([r["z_vs_exoclock"] for r in timed if "z_vs_exoclock" in r])
    zi = np.array([r["z"] for r in injections])
    zw = np.array([r["z_white"] for r in injections])
    bias = np.array([r["recovered_minus_injected_s"] for r in injections])
    summary = {
        "development_only": True, "max_sector": MAX_SECTOR, "max_btjd": MAX_BTJD,
        "forecast_independent": "blind BLS 0.5-12 d; uniform +/-60 min timing prior; no ExoClock ephemeris used",
        "planets": args.planets, "transits_timed": len(timed),
        "transits_excluded": sum(1 for r in events if r.get("status") != "timed"),
        "matched_exoclock": int(len(z_ec)),
        "vs_exoclock": {"median_delta_s": round(float(np.median([r["delta_vs_exoclock_min"] for r in timed if "delta_vs_exoclock_min" in r]) * 60), 2) if len(z_ec) else None,
                        "rms_z": round(float(np.sqrt(np.mean(z_ec**2))), 3) if len(z_ec) else None,
                        "max_abs_z": round(float(np.max(np.abs(z_ec))), 3) if len(z_ec) else None,
                        "median_sigma_ratio_ours_over_exoclock": round(float(np.median([r["sigma_min"] / r["exoclock_sigma_min"] for r in timed if "exoclock_sigma_min" in r])), 3) if len(z_ec) else None},
        "injections": {"n": int(len(zi)), "median_bias_s": round(float(np.median(bias)), 2),
                       "rms_z_beta_scaled": round(float(np.sqrt(np.mean(zi**2))), 3),
                       "rms_z_white": round(float(np.sqrt(np.mean(zw**2))), 3),
                       "frac_abs_z_lt_1": round(float(np.mean(np.abs(zi) < 1)), 3),
                       "per_planet_rms_z": {p: round(float(np.sqrt(np.mean(np.array([r["z"] for r in injections if r["planet"] == p]) ** 2))), 3)
                                            for p in args.planets if any(r["planet"] == p for r in injections)}},
        "seed": args.seed, "light_curves_opened_after_2025_11_18": 0,
        "command": "uv run scripts/t015_timing_pipeline.py",
    }
    (out / "t015_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
