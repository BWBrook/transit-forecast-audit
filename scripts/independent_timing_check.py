"""Independent transit identification and timing for an influential held-out system (review R03, D071).

Shares no code with the project's timing pipeline (t015/sprint2) and never reads the issued epoch while
identifying or fitting transits. Route: SPOC light-curve FITS -> per-segment robust running-median
detrending -> blind box-least-squares search (iteratively masking found signals) -> global batman shape
fit per planet -> per-transit mid-time fits on locally normalised flux with a linear baseline and the
shape fixed, uncertainty from a chi-square profile rescaled to the local out-of-transit scatter.
Repeated on PDCSAP and SAP flux. Comparison with the frozen accepted timings and with DRD happens only
after the fits. Exploratory: these outcomes were inspected in the protected evaluation (D065).

    uv run --with batman-package --with astropy --with scipy --with matplotlib \
        scripts/independent_timing_check.py configs/independent_validation/hr858.json
"""

import csv
import json
import sys
from pathlib import Path

import batman
import numpy as np
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
from scipy.optimize import least_squares

ROOT = Path(__file__).resolve().parents[1]
BTJD = 2457000.0
MIN = 1440.0


def load(paths, column):
    t, f, e = [], [], []
    for p in paths:
        with fits.open(p) as h:
            d = h[1].data
            ok = (d["QUALITY"] == 0) & np.isfinite(d["TIME"]) & np.isfinite(d[column]) & np.isfinite(d[column + "_ERR"])
            med = np.nanmedian(d[column][ok])
            t.append(d["TIME"][ok]); f.append(d[column][ok] / med); e.append(d[column + "_ERR"][ok] / med)
    return np.concatenate(t), np.concatenate(f), np.concatenate(e)


def segments(t, gap=0.5):
    cut = np.flatnonzero(np.diff(t) > gap) + 1
    return np.split(np.arange(t.size), cut)


def detrend(t, f, window=1.0, mask=None):
    keep = np.ones(t.size, bool) if mask is None else ~mask
    trend = np.empty_like(f)
    for idx in segments(t):
        ts, fs, ks = t[idx], f[idx], keep[idx]
        lo = np.searchsorted(ts, ts - window / 2); hi = np.searchsorted(ts, ts + window / 2)
        for j in range(ts.size):
            w = fs[lo[j]:hi[j]][ks[lo[j]:hi[j]]]
            trend[idx[j]] = np.median(w) if w.size > 10 else np.nan
    good = np.isfinite(trend)
    return f / np.where(good, trend, 1.0), good


def bls_search(t, y, dy, n_signals, pmin, pmax):
    found, mask = [], np.zeros(t.size, bool)
    durations = np.array([0.06, 0.08, 0.1, 0.12, 0.15, 0.18])
    for _ in range(n_signals):
        bls = BoxLeastSquares(t[~mask], y[~mask], dy[~mask])
        periods = np.exp(np.linspace(np.log(pmin), np.log(pmax), 60000))
        r = bls.power(periods, durations, objective="snr")
        i = int(np.argmax(r.power))
        sig = {"period": float(r.period[i]), "t0_btjd": float(r.transit_time[i]), "duration_d": float(r.duration[i]),
               "depth_ppm": float(r.depth[i] * 1e6), "snr": float(r.depth_snr[i]), "power": float(r.power[i])}
        found.append(sig)
        ph = ((t - sig["t0_btjd"] + 0.5 * sig["period"]) % sig["period"]) - 0.5 * sig["period"]
        mask |= np.abs(ph) < 1.0 * sig["duration_d"]
    return found


def model(theta, t, P):
    t0, rp, ars, b, q1, q2 = theta
    u1, u2 = 2 * np.sqrt(q1) * q2, np.sqrt(q1) * (1 - 2 * q2)
    p = batman.TransitParams()
    p.t0, p.per, p.rp, p.a = t0, P, rp, ars
    p.inc = np.degrees(np.arccos(min(b / ars, 0.999)))
    p.ecc, p.w, p.u, p.limb_dark = 0.0, 90.0, [u1, u2], "quadratic"
    return batman.TransitModel(p, t, supersample_factor=3, exp_time=2.0 / MIN).light_curve(p)


def companion_mask(t, sigs, skip, pad=1.0):
    m = np.zeros(t.size, bool)
    for k, s in enumerate(sigs):
        if k == skip:
            continue
        ph = ((t - s["t0_btjd"] + 0.5 * s["period"]) % s["period"]) - 0.5 * s["period"]
        m |= np.abs(ph) < pad * s["duration_d"]
    return m


def fit_planet(t, f, e, raw_f, sig, others, window):
    P = sig["period"]
    near = np.abs(((t - sig["t0_btjd"] + 0.5 * P) % P) - 0.5 * P) < window
    use = near & ~others
    tt, yy, ee = t[use], f[use], e[use]
    x0 = [sig["t0_btjd"], np.sqrt(max(sig["depth_ppm"], 50) * 1e-6), 8.0, 0.5, 0.36, 0.3]
    lo, hi = [sig["t0_btjd"] - 0.1, 0.003, 2.0, 0.0, 0.0, 0.0], [sig["t0_btjd"] + 0.1, 0.2, 40.0, 1.0, 1.0, 1.0]

    def resid_lin(th):
        return (yy - model(th, tt, th_P[0])) / ee
    th_P = [P]
    g = least_squares(resid_lin, x0, bounds=(lo, hi))
    # refine period with a linear ephemeris fit to provisional per-transit times later; keep BLS period here
    shape = g.x
    epochs = np.unique(np.round((t[near] - shape[0]) / P)).astype(int)
    rows = []
    for n in epochs:
        tc0 = shape[0] + n * P
        w = (np.abs(t - tc0) < window) & ~others
        if w.sum() < 60:
            continue
        tw, fw, ew = t[w], raw_f[w], e[w]
        intr = np.abs(tw - tc0) < 0.6 * sig["duration_d"]
        if intr.sum() < 20 or (~intr).sum() < 30:
            continue
        grid = tc0 + np.arange(-0.35, 0.35 + 1e-9, 0.5 / MIN)
        chi = np.empty(grid.size)
        for k, tc in enumerate(grid):
            m = model([tc, *shape[1:]], tw, P)
            A = np.vstack([m, m * (tw - tc0)]).T
            coef, *_ = np.linalg.lstsq(A / ew[:, None], fw / ew, rcond=None)
            chi[k] = np.sum(((fw - A @ coef) / ew) ** 2)
        k = int(np.argmin(chi))
        if k in (0, grid.size - 1):
            continue
        m = model([grid[k], *shape[1:]], tw, P)
        A = np.vstack([m, m * (tw - tc0)]).T
        coef, *_ = np.linalg.lstsq(A / ew[:, None], fw / ew, rcond=None)
        r = (fw - A @ coef) / ew
        scale = max(np.sum(r ** 2) / (r.size - 3), 1.0)
        prof = (chi - chi[k]) / scale
        inside = grid[prof <= 1.0]
        a, c, b_ = np.polyfit(grid[max(k - 6, 0):k + 7] - grid[k], chi[max(k - 6, 0):k + 7], 2)
        tc_best = grid[k] - c / (2 * a) if a > 0 else grid[k]
        rows.append({"epoch_local": int(n), "tc_btjd": float(tc_best), "sigma_min": float(0.5 * (inside.max() - inside.min()) * MIN),
                     "chi2_scale": float(scale), "n_points": int(w.sum())})
    return shape, rows


def linear(tc, n, w=None):
    A = np.vstack([np.ones_like(n, float), n]).T
    W = np.ones_like(tc) if w is None else w
    coef = np.linalg.lstsq(A * np.sqrt(W)[:, None], tc * np.sqrt(W), rcond=None)[0]
    return coef, tc - A @ coef


def main(cfg_path):
    cfg = json.loads(Path(cfg_path).read_text())
    paths = sorted((ROOT / cfg["fits_dir"]).glob(cfg.get("fits_glob", "*_lc.fits")))
    out_dir = ROOT / cfg["out_dir"]; out_dir.mkdir(parents=True, exist_ok=True)
    report = {"config": cfg, "fits": [p.name for p in paths], "routes": {}}
    for column in cfg["flux_columns"]:
        t, raw, e = load(paths, column)
        y, good = detrend(t, raw)
        t, y, e, raw = t[good], y[good], e[good], raw[good]
        sigs = bls_search(t, y, e, cfg["n_signals"], *cfg["period_range_d"])
        # flag every transit of every found signal, then re-detrend with transits excluded from the trend
        allm = companion_mask(t, sigs, skip=-1, pad=1.2)
        y2, good2 = detrend(t, raw, mask=allm)
        t, y, e, raw = t[good2], y2[good2], e[good2], raw[good2]
        route = {"signals": sigs, "planets": {}}
        for name, spec in cfg["planets"].items():
            k = int(np.argmin([abs(s["period"] - spec["period_hint_d"]) for s in sigs]))
            if abs(sigs[k]["period"] - spec["period_hint_d"]) / spec["period_hint_d"] > 0.01:
                route["planets"][name] = {"identified": False}
                continue
            others = companion_mask(t, sigs, skip=k, pad=1.0)
            shape, rows = fit_planet(t, y, e, raw / np.median(raw), sigs[k], others, cfg["fit_window_d"])
            tc = np.array([r["tc_btjd"] for r in rows]) + BTJD
            sig = np.array([r["sigma_min"] for r in rows])
            ref = spec.get("reference_ephemeris")
            for r, x in zip(rows, tc):
                r["tc_bjd_tdb"] = float(x)
                if ref:
                    nn = np.round((x - ref["t0_bjd_tdb"]) / ref["period_d"])
                    r["ref_epoch"] = int(nn)
                    r["o_minus_c_ref_min"] = float((x - ref["t0_bjd_tdb"] - nn * ref["period_d"]) * MIN)
            n = np.round((tc - tc[0]) / sigs[k]["period"])
            coef, res = linear(tc, n, 1 / sig ** 2)
            overlap = []
            for r in rows:
                for j, s in enumerate(sigs):
                    if j == k:
                        continue
                    ph = ((r["tc_btjd"] - s["t0_btjd"] + 0.5 * s["period"]) % s["period"]) - 0.5 * s["period"]
                    if abs(ph) < s["duration_d"] + sigs[k]["duration_d"]:
                        overlap.append(r["epoch_local"])
            route["planets"][name] = {
                "identified": True, "bls_signal_index": k, "bls": sigs[k],
                "shape": dict(zip(["t0_btjd", "rp_rs", "a_rs", "b", "q1", "q2"], map(float, shape))),
                "n_transits": len(rows), "local_period_d": float(coef[1]), "linear_rms_min": float(np.std(res) * MIN),
                "median_sigma_min": float(np.median(sig)), "overlaps_companion_epochs": sorted(set(overlap)), "transits": rows}
        report["routes"][column] = route
    compare = cfg.get("compare_frozen")
    if compare:
        o = [r for r in csv.DictReader((ROOT / compare["outcomes"]).open()) if r["planet"] == compare["planet"]]
        fc = {r["event_id"]: r for r in csv.DictReader((ROOT / compare["forecasts"]).open())}
        frozen = np.array(sorted((float(r["tc_bjd_tdb"]), float(fc[r["event_id"]]["predicted_bjd_tdb"]), float(r["sigma_s"]) / 60) for r in o))
        cmp = {}
        for column, route in report["routes"].items():
            pl = route["planets"].get(compare["independent_name"], {})
            if not pl.get("identified"):
                cmp[column] = {"identified": False}
                continue
            mine = np.array([r["tc_bjd_tdb"] for r in pl["transits"]]); msig = np.array([r["sigma_min"] for r in pl["transits"]])
            pairs = []
            for tc_f, pred, s_f in frozen:
                j = int(np.argmin(np.abs(mine - tc_f)))
                if abs(mine[j] - tc_f) * MIN < 120:
                    pairs.append({"frozen_tc": tc_f, "independent_tc": float(mine[j]), "diff_min": float((mine[j] - tc_f) * MIN),
                                  "combined_sigma_min": float(np.hypot(msig[j], s_f)), "independent_minus_drd_min": float((mine[j] - pred) * MIN)})
            d = np.array([p["diff_min"] for p in pairs]); z = d / np.array([p["combined_sigma_min"] for p in pairs])
            cmp[column] = {"frozen_events": len(frozen), "matched": len(pairs), "independent_transits": len(mine),
                           "diff_min_median": float(np.median(d)), "diff_min_max_abs": float(np.max(np.abs(d))),
                           "z_rms": float(np.sqrt(np.mean(z ** 2))),
                           "independent_minus_drd_min_range": [float(min(p["independent_minus_drd_min"] for p in pairs)),
                                                               float(max(p["independent_minus_drd_min"] for p in pairs))],
                           "pairs": pairs}
        report["comparison_with_frozen"] = cmp
    (out_dir / "summary.json").write_text(json.dumps(report, indent=1) + "\n")
    print(json.dumps({c: {k: v for k, v in r.items() if k != "pairs"} for c, r in report.get("comparison_with_frozen", {}).items()}, indent=1))
    for column, route in report["routes"].items():
        print(column, [(round(s["period"], 5), round(s["depth_ppm"]), round(s["snr"], 1)) for s in route["signals"]])
        for name, pl in route["planets"].items():
            if pl.get("identified"):
                ocs = [r.get("o_minus_c_ref_min") for r in pl["transits"]]
                print(" ", name, pl["n_transits"], "P_loc", round(pl["local_period_d"], 6), "rms", round(pl["linear_rms_min"], 2),
                      "sig", round(pl["median_sigma_min"], 1), "O-C(ref) min", None if ocs[0] is None else [round(min(ocs)), round(max(ocs))],
                      "overlaps", pl["overlaps_companion_epochs"], "rp", round(pl["shape"]["rp_rs"], 4), "b", round(pl["shape"]["b"], 2))


if __name__ == "__main__":
    main(sys.argv[1])
