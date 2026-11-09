"""Execute the predeclared 12-run D071/R01 synthetic flux-to-timing control.

Use the retained frozen measurement Python (batman/astropy), not system Python.
No downloads, real photometry or protected outcomes are read.
"""

from __future__ import annotations

import os
for _name in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[_name] = "1"

import csv
import hashlib
import importlib.metadata
import json
import math
import platform
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import acceptance as A
import sprint1_forecast_core as c
import sprint1_outcome_adapter as ad
import sprint2_outcomes as so

OUT = ROOT / "results/d071_controls"
SEED = 20261109
CADENCE = 120 / 86400
PERIOD = 3.0
FORECAST_SD_S = 60.0
SHAPE = {"rp": .06, "a": 10., "inc": 88.5, "q1": .36, "q2": .3}
MODELS = {"M0": {"b": 1., "s_log_lambda": 0.},
          "M2": {"b": 1., "s_log_lambda": 2.0469590063}}
SCENARIOS = ("complete_white", "forecast_phase_gaps", "gaps_shared_shape_red_understated_errors")


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixed_phase_gap_mask(t, predicted):
    keep = np.ones(len(t), dtype=bool)
    for centre in predicted:
        keep &= np.abs(t - (centre + 90 / 1440)) >= 30 / 1440
    return keep


def correlated_noise(rng, size, sigma=.001):
    phi = math.exp(-2 / 20)
    values = np.empty(size)
    values[0] = rng.normal(0, sigma)
    for i in range(1, size):
        values[i] = phi * values[i-1] + rng.normal(0, sigma * math.sqrt(1 - phi**2))
    return values


def runtime():
    packages = {}
    for name in ("numpy", "scipy", "astropy", "batman-package"):
        packages[name] = importlib.metadata.version(name)
    evaluation = subprocess.check_output(
        [str(ROOT / ".venv/bin/python"), "-c", "import json,platform,numpy,scipy; print(json.dumps({'python':platform.python_version(),'numpy':numpy.__version__,'scipy':scipy.__version__}))"], text=True)
    return {"measurement_and_control_scoring_python": platform.python_version(),
            "measurement_and_control_scoring_packages": packages,
            "separate_frozen_evaluation_runtime": json.loads(evaluation)}


def gaussian_score(residual_s, sigma_s, model):
    event = {"forecast_variance_s2": FORECAST_SD_S**2, "sigma_s": sigma_s,
             "outcome_scale": 1., "residual_s": residual_s}
    return {k: float(v[0]) for k,v in c.predictive_scores([event], model, order=384, interpolate=False).items()}


def grid_file(run_id, truth_index, window):
    path = OUT / "grids" / f"{run_id}_{truth_index}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"kind": "likelihood", "units": "seconds",
               "coordinate": "true_midtime_minus_reported_midtime",
               "offset_s": ((window["grid"] - window["tc"]) * 86400).tolist(),
               "log_density": (-.5 * (window["chi"] - np.min(window["chi"]))).tolist(),
               "synthetic": True}
    path.write_text(json.dumps(payload, separators=(",", ":"), allow_nan=False) + "\n")
    return path


def run_one(family, replicate, scenario, latent_s, white, red):
    run_id = f"{family}_{replicate}_{scenario}"
    t_full = np.arange(0, 12, CADENCE)
    predicted = np.array([1., 4., 7., 10.])
    truth = predicted + latent_s / 86400
    duration = so.tp.t14(PERIOD, SHAPE["rp"], SHAPE["a"], SHAPE["inc"])
    half = so.half_width(PERIOD, duration)
    spots = [(.25 * SHAPE["rp"]**2, .2 * duration, .12 * duration)] * 4 if scenario == SCENARIOS[2] else None
    flux = so.model_train(t_full, truth, PERIOD, SHAPE, half, 120., spots=spots) + white
    error = np.full(len(t_full), .003)
    if scenario == SCENARIOS[2]:
        flux += red
        error *= .5
    keep = np.ones(len(t_full), dtype=bool) if scenario == SCENARIOS[0] else fixed_phase_gap_mask(t_full, predicted)
    t, f, e = t_full[keep], flux[keep], error[keep]
    intended = []
    for i, (pred, actual) in enumerate(zip(predicted, truth)):
        intended.append({"run_id": run_id, "family": family, "replicate": replicate,
                         "scenario": scenario, "truth_index": i, "predicted_synthetic_day": float(pred),
                         "truth_synthetic_day": float(actual), "latent_error_s": latent_s,
                         "truth_coverage_window": so.tp.coverage(t, actual, half, CADENCE),
                         "truth_coverage_in_transit": so.tp.coverage(t, actual, duration / 2, CADENCE),
                         "status": "not_recovered", "window_status": "", "timing_error_s": None,
                         "measured_error_s": None, "sigma_s": None, "shape_rchi2": None,
                         "gauss_ok": None, "flags": "", "grid_path": "", "grid_sha256": ""})
    scores = []
    for row in intended:
        for model, params in MODELS.items():
            scores.append({**{k:row[k] for k in ("run_id","family","replicate","scenario","truth_index")},
                           "target": "latent_all_intended", "model": model,
                           **gaussian_score(latent_s, 0., params)})
    try:
        sol = so.solution(t, f, e, 120., PERIOD)
        if sol["id_fail"]:
            for row in intended:
                row["status"] = "run_id_failed:" + sol["id_fail"]
            return intended, scores, {"run_id": run_id, "status": sol["id_fail"], "accepted": 0}
        windows = so.time_windows(t, f, e, sol, 120., CADENCE)
        matched = so.assign(list(truth), sol["wins"])
        diag = {"status": "ok", "shape_rchi2": sol["rchi_shape"]}
        for i, row in enumerate(intended):
            row["shape_rchi2"] = sol["rchi_shape"]
            if i not in matched:
                continue
            w = windows[matched[i][0]]
            row.update(window_status=w["status"], flags=w.get("flags", ""))
            if "tc" not in w:
                row["status"] = w["status"]
                continue
            path = grid_file(run_id, i, w) if not w["gauss_ok"] else None
            # The acceptance API field is transient; these are explicitly simulated
            # coordinate days, never an observed BJD or a time-standard conversion.
            api_row = {"status": w["status"], "flags": w["flags"], "sigma_s": w["sig"] * 86400,
                       "tc_bjd_tdb": w["tc"], "gauss_ok": w["gauss_ok"],
                       "q025_s": (w["q"][5] - w["tc"]) * 86400,
                       "q975_s": (w["q"][6] - w["tc"]) * 86400,
                       "posterior_grid_path": str(path) if path else ""}
            cov_at_prediction = (so.tp.coverage(t, predicted[i], sol["half"], CADENCE) >= .75 and
                                 so.tp.coverage(t, predicted[i], sol["t14"] / 2, CADENCE) >= .75)
            row["status"] = A.terminal_status("ok", [api_row], diag, predicted[i], PERIOD, cov_at_prediction)
            row.update(timing_error_s=(w["tc"] - truth[i]) * 86400,
                       measured_error_s=(w["tc"] - predicted[i]) * 86400,
                       sigma_s=w["sig"] * 86400, gauss_ok=w["gauss_ok"],
                       grid_path=str(path.relative_to(ROOT)) if path else "",
                       grid_sha256=sha(path) if path else "")
            if row["status"] != A.ACCEPTED:
                continue
            grid = ad.likelihood_grid(path) if path else None
            for model, params in MODELS.items():
                for target in ("latent_accepted_subset", "measured_naive_no_convolution", "measured_convolved_reported_timing"):
                    if target == "latent_accepted_subset":
                        metrics = gaussian_score(latent_s, 0., params)
                    elif target == "measured_naive_no_convolution":
                        metrics = gaussian_score(row["measured_error_s"], 0., params)
                    elif grid is None:
                        metrics = gaussian_score(row["measured_error_s"], row["sigma_s"], params)
                    else:
                        metrics = ad.grid_score(row["measured_error_s"], FORECAST_SD_S**2, params,
                                                grid, math.sqrt(FORECAST_SD_S**2 + row["sigma_s"]**2))
                    scores.append({**{k:row[k] for k in ("run_id","family","replicate","scenario","truth_index")},
                                   "target": target, "model": model, **metrics})
        summary = {"run_id": run_id, "status": "ok", "id_snr": sol["id"]["snr"],
                   "shape_rchi2": sol["rchi_shape"], "fitted_duration_minutes": sol["t14"] * 1440,
                   "accepted": sum(r["status"] == A.ACCEPTED for r in intended),
                   "status_counts": dict(Counter(r["status"] for r in intended))}
        return intended, scores, summary
    except Exception as exc:
        for row in intended:
            if row["status"] == "not_recovered":
                row["status"] = "run_exception"
        return intended, scores, {"run_id": run_id, "status": "exception", "error": repr(exc),
                                  "accepted": sum(r["status"] == A.ACCEPTED for r in intended)}


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(dict.fromkeys(k for r in rows for k in r)), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    sources = [ROOT / p for p in ("scripts/d071_injection_controls.py", "scripts/sprint2_outcomes.py",
               "scripts/t015_timing_pipeline.py", "scripts/acceptance.py", "scripts/sprint1_forecast_core.py",
               "scripts/sprint1_outcome_adapter.py", "docs/d071_injection_controls.md")]
    before = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    all_rows, all_scores, runs = [], [], []
    latent_rng = np.random.default_rng(SEED)
    gaussian_latents = latent_rng.normal(0, FORECAST_SD_S, 2)
    for fi, family in enumerate(("gaussian", "two_point")):
        for replicate in (0, 1):
            latent = float(gaussian_latents[replicate]) if family == "gaussian" else (-3000. if replicate == 0 else 3000.)
            noise_rng = np.random.default_rng([SEED, fi, replicate, 1])
            white = noise_rng.normal(0, .003, len(np.arange(0, 12, CADENCE)))
            red = correlated_noise(np.random.default_rng([SEED, fi, replicate, 2]), len(white))
            for scenario in SCENARIOS:
                rows, scores, run = run_one(family, replicate, scenario, latent, white, red)
                all_rows.extend(rows); all_scores.extend(scores); runs.append(run)
                print(json.dumps(run), flush=True)
    write_csv(OUT / "truth_ledger.csv", all_rows)
    write_csv(OUT / "scores.csv", all_scores)
    (OUT / "runs.json").write_text(json.dumps(runs, indent=2, allow_nan=False) + "\n")
    group = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for row in all_scores:
        group[row["family"], row["scenario"], row["target"]][row["model"]][row["replicate"]].append(row)
    summaries = []
    for (family, scenario, target), models in group.items():
        result = {"family": family, "scenario": scenario, "target": target,
                  "defined_replicates": len(models["M0"]), "weighting": "mean events within replicate, replicates equally"}
        for metric in ("is95_standardised", "is95_minutes", "covered95", "width95_minutes"):
            for model in MODELS:
                means = [np.mean([r[metric] for r in rows]) for rows in models[model].values()]
                result[f"{model}_{metric}"] = float(np.mean(means))
            result[f"M2_minus_M0_{metric}"] = result[f"M2_{metric}"] - result[f"M0_{metric}"]
        summaries.append(result)
    write_csv(OUT / "target_comparisons.csv", summaries)
    for path, expected in before.items():
        if sha(ROOT / path) != expected:
            raise ValueError("Control source changed during execution: " + path)
    report = {"synthetic": True, "design_commit": "03fbf67", "seed": SEED,
              "runs": len(runs), "intended_events": len(all_rows),
              "status_counts": dict(Counter(r["status"] for r in all_rows)),
              "latent_gaussian_draws_s": gaussian_latents.tolist(), "runtime": runtime(),
              "source_sha256_before_after": before,
              "grid_sha256": {r["grid_path"]: r["grid_sha256"] for r in all_rows if r["grid_path"]},
              "outputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in OUT.iterdir() if p.is_file() and p.name != "receipt.json"},
              "scope": "Small labelled interpretation control; no bootstrap, power estimate, model qualification or new primary verdict.",
              "raw_photometry_or_headers_read": False, "network_requests": 0,
              "measurement_convolution_limit": "uses returned reported conditional timing distribution; misspecification can invalidate it",
              "new_framework_added": False}
    (OUT / "receipt.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
