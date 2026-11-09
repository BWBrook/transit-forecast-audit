"""Independent empirical-trapezoid timing check under the committed T017 design.

No project measurement, acceptance or score module is imported here. The issued
epoch enters only a later comparison script, never this extraction or fitting.
"""

import os
for _key in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
             "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_key] = "1"

import argparse
import hashlib
import json
import re
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import scipy
from astropy import __version__ as astropy_version
from astropy.io import fits
from astropy.timeseries import BoxLeastSquares
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "configs/independent_validation/t017_design.json"
OUT = ROOT / "results/independent_validation/t017"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def phase(t, epoch, period):
    return (np.asarray(t) - epoch + period / 2) % period - period / 2


def trapezoid(t, centre, duration, ingress_fraction):
    return np.clip((duration / 2 - np.abs(np.asarray(t) - centre))
                   / (duration * ingress_fraction), 0, 1)


def continuum(t, flux, width=.5, quantile=.8):
    trend = np.empty_like(flux)
    chunks = np.split(np.arange(len(t)), np.flatnonzero(np.diff(t) > .5) + 1)
    for indices in chunks:
        bins = np.floor((t[indices] - t[indices[0]]) / width).astype(int)
        centres, levels = [], []
        for number in np.unique(bins):
            sample = indices[bins == number]
            centres.append(float(np.mean(t[sample])))
            levels.append(float(np.quantile(flux[sample], quantile)))
        trend[indices] = np.interp(t[indices], centres, levels)
    return trend


class LocalProfile:
    """Weighted linear baseline and nonnegative transit depth, profiled exactly."""

    def __init__(self, t, flux, error):
        self.t = np.asarray(t)
        self.y = np.asarray(flux)
        self.w = 1 / np.asarray(error) ** 2
        self.h = np.column_stack((np.ones(len(t)), self.t - np.mean(self.t)))
        self.gram_inv = np.linalg.inv(self.h.T @ (self.w[:, None] * self.h))
        self.base = self.gram_inv @ (self.h.T @ (self.w * self.y))
        self.residual = self.y - self.h @ self.base
        self.base_chi2 = float(np.sum(self.w * self.residual ** 2))

    def many(self, centres, duration, ingress):
        centres = np.atleast_1d(centres)
        chis, depths = [], []
        for start in range(0, len(centres), 128):
            q = trapezoid(self.t[None, :], centres[start:start + 128, None], duration, ingress)
            cross = q @ (self.w[:, None] * self.h)
            denominator = np.sum(q * q * self.w, axis=1) - np.sum((cross @ self.gram_inv) * cross, axis=1)
            numerator = q @ (self.w * self.residual)
            valid = denominator > np.max(self.w) * 1e-10
            depth = np.where(valid, np.maximum(-numerator, 0) / np.maximum(denominator, 1e-100), 0)
            chi = self.base_chi2 - depth * np.maximum(-numerator, 0)
            chis.extend(chi)
            depths.extend(depth)
        return np.asarray(chis), np.asarray(depths)


def identify(t, flux, error, period_hint, settings):
    periods = np.geomspace(*settings["blind_period_range_d"], settings["period_grid_size"])
    durations = np.array(settings["durations_d"])
    signals, excluded = [], np.zeros(len(t), bool)
    for _ in range(settings["maximum_sequential_signals"]):
        keep = ~excluded
        if keep.sum() < 50:
            break
        model = BoxLeastSquares(t[keep], flux[keep], dy=error[keep])
        result = model.power(periods, durations, objective="snr", method="fast")
        best = int(np.nanargmax(result.power))
        signal = {"period_d": float(result.period[best]), "epoch_btjd": float(result.transit_time[best]),
                  "duration_d": float(result.duration[best]), "depth": float(result.depth[best]),
                  "snr": float(result.depth_snr[best])}
        if signal["snr"] < settings["minimum_bls_snr"]:
            break
        signals.append(signal)
        excluded |= np.abs(phase(t, signal["epoch_btjd"], signal["period_d"])) < 1.2 * signal["duration_d"]
    candidates = [i for i, s in enumerate(signals)
                  if abs(s["period_d"] / period_hint - 1) <= settings["target_period_tolerance_fraction"]]
    selected = min(candidates, key=lambda i: abs(signals[i]["period_d"] / period_hint - 1)) if candidates else None
    return signals, selected, len(candidates) > 1


def companion_mask(t, signals, target):
    selected = signals[target]
    target_region = np.abs(phase(t, selected["epoch_btjd"], selected["period_d"])) < 1.2 * selected["duration_d"]
    combined, diagnostics = np.zeros(len(t), bool), []
    for index, other in enumerate(signals):
        if index == target:
            continue
        masked = np.abs(phase(t, other["epoch_btjd"], other["period_d"])) < .8 * other["duration_d"]
        ratio = other["period_d"] / selected["period_d"]
        harmonic = any(abs(ratio / candidate - 1) < .01
                       for n in range(1, 5) for candidate in (float(n), 1 / n))
        overlap = masked & target_region
        if harmonic:
            masked &= ~target_region
        combined |= masked
        diagnostics.append({"signal": index, "period_ratio": float(ratio),
                            "harmonic_candidate": harmonic,
                            "overlapping_target_cadences": int(overlap.sum()),
                            "target_cadences_protected_from_harmonic_mask": int(overlap.sum()) if harmonic else 0,
                            "interpretation": "Harmonic overlap is ambiguous, not a confirmed separate companion." if harmonic else "Nonharmonic signal masked, including overlaps."})
    return combined, diagnostics


def shared_shape(t, flux, error, signal, other_mask):
    folded = phase(t, signal["epoch_btjd"], signal["period_d"])
    selected = (np.abs(folded) < 2.5 * signal["duration_d"]) & ~other_mask
    x, y, e = folded[selected], flux[selected], error[selected]
    if len(x) < 50:
        raise ValueError("Insufficient folded target data")
    prof = LocalProfile(x, y, e)
    duration = signal["duration_d"]
    bounds = [(-duration, duration), (duration * .3, min(duration * 2.5, .45 * signal["period_d"])), (.02, .49)]
    def objective(theta):
        return float(prof.many([theta[0]], theta[1], theta[2])[0][0])
    fits_ = [minimize(objective, [0., duration, ingress], method="Powell", bounds=bounds,
                      options={"maxiter": 100, "xtol": 1e-7, "ftol": 1e-8}) for ingress in (.12, .3)]
    valid = [fit for fit in fits_ if fit.success and np.isfinite(fit.fun)]
    if not valid:
        raise ValueError("Shared trapezoid fit did not converge")
    fit = min(valid, key=lambda fit: fit.fun)
    return {"phase_shift_d": float(fit.x[0]), "duration_d": float(fit.x[1]),
            "ingress_fraction": float(fit.x[2]), "reduced_chi2": float(fit.fun / max(1, len(x) - 6)),
            "points": len(x), "empirical_model": "symmetric trapezoid, depth and linear baseline profiled"}


def profile_transit(t, flux, error, centre, shape, period, settings, other_mask):
    duration = shape["duration_d"]
    half = min(settings["fit_window_duration_multiplier"] * duration,
               settings["maximum_local_half_window_fraction_period"] * period)
    selected = (np.abs(t - centre) < half) & ~other_mask
    x, y, e = t[selected] - centre, flux[selected], error[selected]
    required = settings["minimum_points_each_outside_side"]
    if ((x < -duration).sum() < required or (x > duration).sum() < required
            or (np.abs(x) < duration / 2).sum() < required):
        return {"status": "insufficient_window_coverage", "window_centre_btjd": centre,
                "points": len(x)}
    prof = LocalProfile(x, y, e)
    extent = min(duration, .2 * period)
    grid = np.linspace(-extent, extent, int(np.ceil(2 * extent * 86400 / settings["timing_profile_step_s"])) + 1)
    chi, depth = prof.many(grid, duration, shape["ingress_fraction"])
    best = int(np.argmin(chi))
    scale = max(float(chi[best] / max(1, len(x) - 3)), 1.)
    weights = np.exp(-.5 * (chi - chi[best]) / scale)
    cumulative = np.r_[0., np.cumsum((weights[:-1] + weights[1:]) / 2 * np.diff(grid))]
    if cumulative[-1] <= 0 or not np.isfinite(cumulative[-1]):
        return {"status": "invalid_profile", "window_centre_btjd": centre, "points": len(x)}
    cumulative /= cumulative[-1]
    q025, q16, q50, q84, q975 = np.interp([.025, .15865, .5, .84135, .975], cumulative, grid)
    result = {"status": "timed", "window_centre_btjd": centre, "points": len(x),
              "tc_btjd": float(centre + grid[best]), "profile_median_btjd": float(centre + q50),
              "sigma_min": float((q84 - q16) * 720), "q025_btjd": float(centre + q025),
              "q975_btjd": float(centre + q975), "depth": float(depth[best]),
              "reduced_chi2": scale, "profile_signal_snr": float(np.sqrt(max(prof.base_chi2 - chi[best], 0) / scale)),
              "profile_boundary_weight": float(max(weights[0], weights[-1])),
              "profile_edge": bool(best <= 1 or best >= len(grid) - 2),
              "weak_profile": bool((prof.base_chi2 - chi[best]) / scale < 9)}
    return result


def joint_nuisance(t, flux, error, centre, shape, period, settings, other_mask):
    duration = shape["duration_d"]
    half = min(settings["fit_window_duration_multiplier"] * duration, .45 * period)
    selected = (np.abs(t - centre) < half) & ~other_mask
    x, y, e = t[selected] - centre, flux[selected], error[selected]
    if len(x) < 30:
        return {"status": "insufficient_joint_data"}
    prof = LocalProfile(x, y, e)
    bounds = [(-min(duration, .2 * period), min(duration, .2 * period)),
              (duration * .4, min(duration * 2., .4 * period)), (.02, .49)]
    def objective(theta):
        return float(prof.many([theta[0]], theta[1], theta[2])[0][0])
    fit = minimize(objective, [0., duration, shape["ingress_fraction"]], method="Powell", bounds=bounds,
                   options={"maxiter": 200, "ftol": 1e-8, "xtol": 1e-7})
    return {"status": "joint_fit" if fit.success else "joint_nonconvergence",
            "tc_btjd": float(centre + fit.x[0]), "duration_d": float(fit.x[1]),
            "ingress_fraction": float(fit.x[2]), "chi2": float(fit.fun),
            "note": "Local shape sensitivity with baseline/depth profiled, not nuisance marginalisation."}


def allowed_product(product):
    name = Path(product["relative_fits_path"]).name
    match = re.search(r"-s(\d{4})-", name)
    if match is None or int(match[1]) != product["sector"]:
        raise ValueError("Filename/selection sector mismatch")
    sector = product["sector"]
    if not (46 <= sector <= 73 or sector >= 98):
        raise ValueError("Forbidden or unauthorised sector; no product opened")
    path = (ROOT / product["relative_fits_path"]).resolve()
    if ROOT / "data/raw/mast" not in path.parents:
        raise ValueError("Product must be an existing local MAST file")
    return path


def process_product(task):
    case, product, settings, joint_events = task
    started = time.monotonic()
    result = {"planet": case["planet"], "category": case["category"], "sector": product["sector"],
              "relative_fits_path": product["relative_fits_path"], "fluxes": {}}
    try:
        path = allowed_product(product)
        if not path.exists():
            raise FileNotFoundError("Selected local product is missing")
        digest = sha(path)
        if product["expected_sha256"] and digest != product["expected_sha256"]:
            raise ValueError("Selected product hash differs from saved metadata")
        result["file_sha256"] = digest
        with fits.open(path, memmap=False) as hdus:
            header, table = hdus[1].header, hdus[1].data
            time_system = str(header.get("TIMESYS", hdus[0].header.get("TIMESYS", ""))).strip()
            reference = str(header.get("TIMEREF", hdus[0].header.get("TIMEREF", ""))).strip()
            bjdref = float(header.get("BJDREFI", 0)) + float(header.get("BJDREFF", 0))
            if time_system != "TDB" or reference != "SOLARSYSTEM" or bjdref != 2457000.:
                raise ValueError("Unrecognised time-reference metadata; no relabelling")
            result["time_metadata"] = {"TIMESYS": time_system, "TIMEREF": reference, "BJDREF": bjdref}
            for column in ("PDCSAP_FLUX", "SAP_FLUX"):
                try:
                    good = ((table["QUALITY"] == 0) & np.isfinite(table["TIME"])
                            & np.isfinite(table[column]) & np.isfinite(table[column + "_ERR"])
                            & (table[column + "_ERR"] > 0))
                    t = np.asarray(table["TIME"][good], dtype=float)
                    raw = np.asarray(table[column][good], dtype=float)
                    err = np.asarray(table[column + "_ERR"][good], dtype=float)
                    order = np.argsort(t); t, raw, err = t[order], raw[order], err[order]
                    normal = float(np.median(raw)); raw, err = raw / normal, err / normal
                    trend = continuum(t, raw, settings["detrend_bin_width_d"], settings["continuum_quantile"])
                    detrended, detrend_error = raw / trend, err / trend
                    signals, target, ambiguous = identify(t, detrended, detrend_error, case["period_hint_d"], settings)
                    flux_result = {"signals": signals, "selected_signal": target, "phase_ambiguity": ambiguous,
                                   "good_cadences": len(t), "tc_uses_issued_epoch": False}
                    result["fluxes"][column] = flux_result
                    if target is None:
                        flux_result["status"] = "target_not_identified"
                        continue
                    signal = signals[target]
                    other_mask, mask_diagnostics = companion_mask(t, signals, target)
                    flux_result["companion_mask_diagnostics"] = mask_diagnostics
                    shape = shared_shape(t, detrended, detrend_error, signal, other_mask)
                    epoch = signal["epoch_btjd"] + shape["phase_shift_d"]
                    period = signal["period_d"]
                    flux_result.update(status="identified", shared_shape=shape, transits=[])
                    n0 = int(np.ceil((t.min() - epoch) / period))
                    n1 = int(np.floor((t.max() - epoch) / period))
                    for orbit in range(n0, n1 + 1):
                        centre = epoch + orbit * period
                        event = profile_transit(t, raw, err, centre, shape, period, settings, other_mask)
                        event["local_epoch"] = orbit
                        if event["status"] == "timed":
                            event["tc_bjd_tdb"] = event["tc_btjd"] + bjdref
                            nearby = any(abs(event["tc_bjd_tdb"] - reference_tc) < .2 * period
                                         for reference_tc in joint_events.get(case["planet"], []))
                            if case["category"] == "evaluation_influence" and nearby:
                                event["joint_nuisance"] = joint_nuisance(t, raw, err, centre, shape, period, settings, other_mask)
                        flux_result["transits"].append(event)
                except Exception as exc:
                    result["fluxes"][column] = {"status": "processing_failed", "error": str(exc)}
        result["status"] = "completed"
    except Exception as exc:
        result.update(status="product_failed", error=str(exc))
    result["seconds"] = time.monotonic() - started
    return result


def validate_design_commit(commit):
    relative = str(DESIGN.relative_to(ROOT))
    committed = subprocess.check_output(["git", "show", f"{commit}:{relative}"], cwd=ROOT)
    if committed != DESIGN.read_bytes():
        raise ValueError("Design differs from its pre-fit committed bytes")
    return hashlib.sha256(committed).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--design-commit", required=True)
    parser.add_argument("--amendment-commit", required=True)
    parser.add_argument("--workers", type=int, default=2)
    args = parser.parse_args()
    design_hash = validate_design_commit(args.design_commit)
    source_relative = str(Path(__file__).resolve().relative_to(ROOT))
    amended_source = subprocess.check_output(["git", "show", f"{args.amendment_commit}:{source_relative}"], cwd=ROOT)
    if amended_source != Path(__file__).read_bytes():
        raise ValueError("Engine differs from committed exploratory amendment")
    design = json.loads(DESIGN.read_text())
    import csv
    joint_events = {}
    for row in csv.DictReader((ROOT / "results/final_primary/accepted_outcomes.csv").open()):
        if row["gauss_ok"].lower() not in ("true", "1"):
            joint_events.setdefault(row["planet"], []).append(float(row["tc_bjd_tdb"]))
    tasks, seen = [], set()
    for case in design["cases"]:
        for product in case["products"]:
            key = case["planet"], product["relative_fits_path"]
            if key not in seen:
                tasks.append((case, product, design["method_settings"], joint_events))
                seen.add(key)
    OUT.mkdir(parents=True, exist_ok=True)
    start = time.monotonic()
    products = []
    with ProcessPoolExecutor(max_workers=args.workers) as pool:
        for result in pool.map(process_product, tasks):
            products.append(result)
            path = OUT / f"{result['planet']}_S{result['sector']}.json"
            path.write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
            print(json.dumps({"completed": len(products), "total": len(tasks), "planet": result["planet"],
                              "sector": result["sector"], "status": result["status"]}), flush=True)
    receipt = {"design_commit": args.design_commit, "design_sha256": design_hash,
               "amendment_commit": args.amendment_commit,
               "first_attempt_receipt_sha256": sha(OUT / "attempt1_receipt.json"),
               "engine_sha256": sha(Path(__file__)), "products": len(products),
               "raw_products_failed": sum(r["status"] != "completed" for r in products),
               "seconds": time.monotonic() - start, "workers": args.workers,
               "versions": {"python": sys.version.split()[0], "numpy": np.__version__,
                            "scipy": scipy.__version__, "astropy": astropy_version},
               "protected_sectors_74_97_opened": False, "downloads": 0,
               "output_sha256": {f"{r['planet']}_S{r['sector']}.json": sha(OUT / f"{r['planet']}_S{r['sector']}.json") for r in products},
               "limits": ["Same source photons and shared standard Astropy BLS library, independently written timing/profile code.",
                          "Empirical trapezoid shape is an approximation; profile uncertainty is not fully marginal or newly qualified.",
                          "No pixel/centroid check; non-detection is not evidence of a forecast miss."]}
    (OUT / "measurement_receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
