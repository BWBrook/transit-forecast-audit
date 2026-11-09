"""Independent bounded numerical audit of the authorised D065 outputs.

Run from any directory with the existing project environment:
    UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_d065_numerics.py

Reads derived tables and likelihood grids only. Replays all saved multiplicities
and conditional draws, independently checks selected scores at quadrature order
512, and refits/rescores draw 0 of each run. Does not repeat the 2,000-refit run,
re-extract measurements, inspect FITS, or change the frozen analysis. The dense
M2 likelihood check shares the frozen calibration design, not its likelihood
implementation. The draw-rescoring spot check intentionally uses the frozen
scorer, whose selected event calculations are checked independently.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
import platform
import subprocess
import sys
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy
from scipy.optimize import brentq, minimize_scalar
from scipy.special import logsumexp, ndtr, ndtri, roots_hermitenorm

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import final_evaluation as fe
import sprint1_forecast_core as core

METHODS = ("M0", "M1", "M2", "M3")
LABELS = ("primary", "extension")
PROBS = (.158655254, .841344746, .025, .975)


def read_csv(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def read_run(label):
    directory = ROOT / "results" / f"final_{label}"
    with gzip.open(directory / "joint_draws.json.gz", "rt") as stream:
        draws = json.load(stream)
    return {
        "scores": read_csv(directory / "scores.csv"),
        "outcomes": read_csv(directory / "accepted_outcomes.csv"),
        "forecasts": read_csv(directory / "accepted_forecasts.csv"),
        "summary": json.loads((directory / "evaluation_summary.json").read_text()),
        "descriptives": json.loads((directory / "descriptives.json").read_text()),
        "draws": draws,
    }


def arithmetic(run):
    rows, summary, descriptives, draws = (
        run[k] for k in ("scores", "summary", "descriptives", "draws")
    )
    groups = defaultdict(list)
    for row in rows:
        groups[row["method"], row["planet"]].append(row)
    planets = sorted({row["planet"] for row in rows})
    hosts = {row["planet"]: row["host"] for row in rows}
    event_ids = {m: {r["event_id"] for r in rows if r["method"] == m} for m in METHODS}
    columns = {
        "planet_balanced_is95_std": "is95_standardised",
        "planet_balanced_is95_min": "is95_minutes",
        "planet_balanced_cov68": "covered68",
        "planet_balanced_cov95": "covered95",
        "planet_balanced_width95_min": "width95_minutes",
    }
    calculated = {}
    for model in METHODS:
        calculated[model] = {
            name: float(np.mean([
                np.mean([float(row[column]) for row in groups[model, planet]])
                for planet in planets
            ]))
            for name, column in columns.items()
        }
        calculated[model]["event_cov95"] = float(np.mean([
            float(row["covered95"]) for row in rows if row["method"] == model
        ]))
    differences = [
        abs(calculated[m][k] - descriptives[m][k])
        for m in METHODS for k in calculated[m]
    ]
    delta = np.array([
        np.mean([float(r["is95_standardised"]) for r in groups["M2", p]])
        - np.mean([float(r["is95_standardised"]) for r in groups["M0", p]])
        for p in planets
    ])
    frozen_seeds = json.loads((ROOT / "configs/candidate_freeze.json").read_text())["seeds"]
    host_index = {h: i for i, h in enumerate(draws["hosts"])}
    planet_host_index = [host_index[hosts[p]] for p in planets]
    rng = np.random.default_rng(draws["seed"])
    mismatches, fixed_errors, undefined = [], [], []
    joint, parameter_s = [], []
    for index, draw in enumerate(draws["draws"]):
        expected = np.bincount(
            rng.integers(len(host_index), size=len(host_index)), minlength=len(host_index)
        )
        if not np.array_equal(expected, draw["multiplicity"]) or draw["draw"] != index:
            mismatches.append(index)
        weights = np.array(draw["multiplicity"])[planet_host_index]
        if weights.sum():
            value = float(np.average(delta, weights=weights))
            fixed_errors.append(abs(value - draw["fixed_parameter_delta"]))
        else:
            undefined.append(index)
            if np.isfinite(draw["fixed_parameter_delta"]):
                raise ValueError("Undefined draw has a finite saved fixed-parameter delta")
        joint.append(draw["paired_delta_M2_M0"])
        parameter_s.append(draw["models"]["M2"]["s_log_lambda"])
    rng = np.random.default_rng(summary["seeds"]["conditional_fixed_parameter_bootstrap"])
    evaluation_hosts = sorted(set(hosts.values()))
    evaluation_index = {h: i for i, h in enumerate(evaluation_hosts)}
    planet_evaluation_index = [evaluation_index[hosts[p]] for p in planets]
    conditional = []
    for _ in range(summary["conditional_bootstrap"]):
        weights = np.bincount(
            rng.integers(len(evaluation_hosts), size=len(evaluation_hosts)),
            minlength=len(evaluation_hosts),
        )[planet_evaluation_index]
        conditional.append(float(np.average(delta, weights=weights)))
    conditional_ci = np.quantile(conditional, [.025, .975])
    joint_ci = np.nanquantile(joint, [.025, .975])
    s_quantiles = np.quantile(parameter_s, [.025, .975])
    return {
        "calculated_descriptives": calculated,
        "descriptives_max_abs_error": max(differences),
        "mean_delta": float(delta.mean()),
        "mean_delta_summary_error": abs(float(delta.mean()) - summary["primary_delta_M2_M0"]),
        "median_delta": float(np.median(delta)),
        "fraction_improved": float(np.mean(delta < 0)),
        "num_improved": int(sum(delta < 0)),
        "events_per_model": {m: len(event_ids[m]) for m in METHODS},
        "same_event_sets": all(event_ids[m] == event_ids["M0"] for m in METHODS),
        "score_rows": len(rows),
        "score_finite": all(np.isfinite(float(r[k])) for r in rows for k in (
            "is95_standardised", "is95_minutes", "width95_minutes", "m0_predictive_sd_s"
        )),
        "weight_sum_per_model": {
            m: sum(float(r["weight"]) for r in rows if r["method"] == m) for m in METHODS
        },
        "joint_draw_count": len(joint),
        "joint_ci95": joint_ci.tolist(),
        "joint_ci_max_error": float(max(abs(joint_ci - summary["joint_refit_ci95"]))),
        "M2_s_quantile_error": float(max(abs(s_quantiles - summary["draw_M2_s_q025_q975"]))),
        "joint_seed": draws["seed"],
        "seeds_match_frozen_config": (
            draws["seed"] == summary["seeds"]["evaluation_joint_bootstrap"]
            == frozen_seeds["evaluation_joint_bootstrap"]
            and summary["seeds"]["conditional_fixed_parameter_bootstrap"]
            == frozen_seeds["conditional_fixed_parameter_bootstrap"]
        ),
        "bootstrap_count_matches_summary": len(joint) == summary["joint_bootstrap"],
        "seed_multiplicity_mismatches": mismatches,
        "fixed_draw_max_error": max(fixed_errors),
        "undefined_draw_indices": undefined,
        "joint_undefined_count": int(sum(~np.isfinite(joint))),
        "joint_effective_draws": int(sum(np.isfinite(joint))),
        "undefined_draw_reason": "No evaluation host was selected in the union-host resample",
        "conditional_ci95": conditional_ci.tolist(),
        "conditional_ci_max_error": float(max(abs(
            conditional_ci - summary["conditional_fixed_parameter_ci95"]
        ))),
        "draw_host_sets_correct": (
            draws["hosts"] == sorted(set(draws["calibration_hosts"]) | set(draws["evaluation_hosts"]))
            and draws["evaluation_hosts"] == evaluation_hosts
        ),
        "planets": len(planets),
        "hosts": len(evaluation_hosts),
    }


def is_gaussian(row):
    return row["gauss_ok"].lower() in ("true", "1", "yes")


def grid_path(row):
    path = Path(row["posterior_grid_path"])
    return path if path.is_absolute() else ROOT / path


def independent_grid(row):
    raw = json.loads(grid_path(row).read_text())
    x = np.asarray(raw["offset_s"])
    density = np.exp(np.asarray(raw["log_density"]) - max(raw["log_density"]))
    widths = np.r_[np.diff(x)[0] / 2, (x[2:] - x[:-2]) / 2, np.diff(x)[-1] / 2]
    weights = density * widths
    return x, weights / weights.sum()


def independent_score(row, forecast, model):
    vf, sy = float(forecast["forecast_variance_s2"]), float(row["sigma_s"])
    residual = (float(row["tc_bjd_tdb"]) - float(forecast["predicted_bjd_tdb"])) * 86400
    b, s = float(forecast[model + "_b"]), float(forecast[model + "_s_log_lambda"])
    if s:
        z, weights = roots_hermitenorm(512)
        weights /= math.sqrt(2 * math.pi)
    else:
        z, weights = np.zeros(1), np.ones(1)
    forecast_sd = b * np.sqrt(vf) * np.exp(.5 * s * z)
    if not is_gaussian(row):
        x, mass = independent_grid(row)
        denominator = np.sqrt(vf + np.dot(mass, x * x) - np.dot(mass, x) ** 2)
        keep = weights > 1e-18
        forecast_sd, weights = forecast_sd[keep], weights[keep]
        def cdf(value):
            return float(np.dot(mass, ndtr((value + x[:, None]) / forecast_sd) @ weights))
        bracket = max(abs(x)) + 30 * b * np.sqrt(vf) * np.exp(s * s / 4)
        quantiles = [brentq(lambda value: cdf(value) - p, -bracket, bracket, xtol=1e-8) for p in PROBS]
        log_density = logsumexp(
            np.log(np.maximum(mass, np.finfo(float).tiny))[:, None] + np.log(weights)[None, :]
            - .5 * np.log(2 * np.pi) - np.log(forecast_sd)[None, :]
            - .5 * ((residual + x[:, None]) / forecast_sd[None, :]) ** 2
        )
    else:
        sd = np.sqrt(sy * sy + forecast_sd * forecast_sd)
        denominator = np.sqrt(vf + sy * sy)
        if s:
            def cdf(value):
                return float(np.dot(weights, ndtr(value / sd)))
            positive = [brentq(lambda value: cdf(value) - p, 0, max(sd) * 10, xtol=1e-8)
                        for p in (.841344746, .975)]
        else:
            positive = sd[0] * ndtri(np.array([.841344746, .975]))
        quantiles = [-positive[0], positive[0], -positive[1], positive[1]]
        with np.errstate(divide="ignore"):
            log_density = logsumexp(
                np.log(weights) - .5 * np.log(2 * np.pi) - np.log(sd) - .5 * (residual / sd) ** 2
            )
    lower68, upper68, lower95, upper95 = quantiles
    score = upper95 - lower95 + 40 * (max(lower95 - residual, 0) + max(residual - upper95, 0))
    return {
        "is95_standardised": score / denominator,
        "is95_minutes": score / 60,
        "covered68": float(lower68 <= residual <= upper68),
        "covered95": float(lower95 <= residual <= upper95),
        "width95_minutes": (upper95 - lower95) / 60,
        "m0_predictive_sd_s": denominator,
        "negative_log_score_seconds": -float(log_density),
    }


def scoring(run):
    forecasts = {r["event_id"]: r for r in run["forecasts"]}
    saved = {(r["event_id"], r["method"]): r for r in run["scores"]}
    variance_errors, baseline_errors = [], []
    for forecast in forecasts.values():
        st0, sp, epoch, rho = map(float, (forecast[k] for k in (
            "sigma_t0_s", "sigma_p_s", "forecast_epoch", "rho"
        )))
        variance = st0 * st0 + epoch * epoch * sp * sp + 2 * epoch * rho * st0 * sp
        variance_errors.append(abs(variance - float(forecast["forecast_variance_s2"])))
    for row in run["outcomes"]:
        if is_gaussian(row):
            calculated = independent_score(row, forecasts[row["event_id"]], "M0")
            baseline_errors.extend(abs(calculated[k] - float(saved[row["event_id"], "M0"][k]))
                                   for k in calculated)
    selected = []
    for gaussian in (True, False):
        subset = [r for r in run["outcomes"] if is_gaussian(r) == gaussian]
        def residual_size(row):
            return abs((float(row["tc_bjd_tdb"]) - float(
                forecasts[row["event_id"]]["predicted_bjd_tdb"]
            )) * 86400) / float(row["sigma_s"])
        for row in (subset[0], subset[-1], max(subset, key=residual_size)):
            if row["event_id"] not in {r["event_id"] for r in selected}:
                selected.append(row)
    max_errors, checks = {}, []
    for row in selected:
        for model in METHODS:
            calculated = independent_score(row, forecasts[row["event_id"]], model)
            errors = {k: abs(calculated[k] - float(saved[row["event_id"], model][k])) for k in calculated}
            for key, value in errors.items():
                max_errors[key] = max(max_errors.get(key, 0), value)
            checks.append({"event_id": row["event_id"], "model": model,
                           "gaussian": is_gaussian(row), "max_metric_error": max(errors.values())})
    return {
        "forecast_variance_max_error_s2": max(variance_errors),
        "all_gaussian_M0_event_count": sum(is_gaussian(r) for r in run["outcomes"]),
        "all_gaussian_M0_max_metric_error": max(baseline_errors),
        "spot_selection": "First, last, and largest absolute residual / sigma, within each Gaussian/grid class; duplicate picks removed",
        "independent_quadrature_order": 512,
        "spots": checks,
        "spot_max_metric_errors": max_errors,
    }


def joint_spots(runs):
    train = fe.calibration_planets()
    z, weights = roots_hermitenorm(384)
    log_weights = np.log(np.maximum(weights, np.finfo(float).tiny)) - .5 * np.log(2 * np.pi)
    precomputed = []
    for planet in train:
        epochs, se = planet["n"], planet["se"]
        residual = planet["m"] / se
        st0, sp, rho = planet["st0"], planet["sp"], planet.get("rho", 0.)
        covariance = (st0 * st0 + sp * sp * np.outer(epochs, epochs)
                      + rho * st0 * sp * (epochs[:, None] + epochs[None, :]))
        eigenvalues, rotation = np.linalg.eigh(covariance / np.outer(se, se))
        precomputed.append((np.maximum(eigenvalues, 0), (rotation.T @ residual) ** 2,
                            float(2 * np.log(se).sum() + len(residual) * np.log(2 * np.pi))))
    def independent_fit(multiplicity):
        def objective(s):
            latent_variance = np.exp(s * z)
            likelihoods = []
            for eigenvalues, projected_square, constant in precomputed:
                scaled = 1 + latent_variance[:, None] * eigenvalues
                log_likelihood = -.5 * (
                    constant + np.log(scaled).sum(1) + (projected_square / scaled).sum(1)
                )
                likelihoods.append(logsumexp(log_weights + log_likelihood))
            return -float(np.dot(multiplicity, likelihoods))
        result = minimize_scalar(objective, bounds=(.01, 4.99), method="bounded", options={"xatol": 1e-9})
        return {"s": float(result.x), "nll": float(result.fun), "success": bool(result.success)}
    point = independent_fit(np.ones(len(train)))
    frozen_models = json.loads((ROOT / "results/prefreeze/candidate_models_core_matched.json").read_text())["models"]
    report = {
        "training_planets": len(train), "training_hosts": len({p["host"] for p in train}),
        "point_independent_M2": point,
        "point_M2_s_error": abs(point["s"] - frozen_models["M2"]["s_log_lambda"]),
        "independent_likelihood": "Dense whitened covariance eigensystem; scalar M2 optimization; frozen calibration design",
        "runs": {},
    }
    for label, run in runs.items():
        draws, draw = run["draws"], run["draws"]["draws"][0]
        index = {h: i for i, h in enumerate(draws["hosts"])}
        multiplicity = np.array(draw["multiplicity"])[[index[p["host"]] for p in train]]
        independent = independent_fit(multiplicity)
        refitted = core.fit_methods(train, weights=multiplicity)
        parameter_error = max(abs(refitted[m][k] - draw["models"][m][k])
                              for m in refitted for k in ("b", "s_log_lambda"))
        events = fe.event_representation(run["outcomes"], run["forecasts"])
        differences = (fe.score_events(events, draw["models"]["M2"])
                       - fe.score_events(events, {"b": 1., "s_log_lambda": 0.}))
        groups = defaultdict(list)
        for event, value in zip(events, differences):
            groups[event["planet"]].append(value)
        planet_host = {e["planet"]: e["host"] for e in events}
        means = np.array([np.mean(v) for v in groups.values()])
        multiplicity = np.array([draw["multiplicity"][index[planet_host[p]]] for p in groups])
        delta = float(np.average(means, weights=multiplicity))
        report["runs"][label] = {
            "draw": 0, "independent_M2": independent,
            "stored_M2_s": draw["models"]["M2"]["s_log_lambda"],
            "independent_M2_s_error": abs(independent["s"] - draw["models"]["M2"]["s_log_lambda"]),
            "exact_all_models_max_parameter_error": parameter_error,
            "rescored_delta": delta, "stored_delta": draw["paired_delta_M2_M0"],
            "rescored_delta_error": abs(delta - draw["paired_delta_M2_M0"]),
        }
        print(f"Completed bounded joint check: {label}, draw 0", flush=True)
    return report


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def input_hashes(runs):
    manifest = json.loads((ROOT / "results/freeze/freeze_manifest.json").read_text())
    paths = {"configs/protected_access.json", "results/freeze/freeze_manifest.json"}
    for category in manifest["files"].values():
        paths.update(category)
    paths.update(manifest["likelihood_grids"]["sha256"])
    for label, run in runs.items():
        for name in ("scores.csv", "accepted_outcomes.csv", "accepted_forecasts.csv",
                     "evaluation_summary.json", "descriptives.json", "joint_draws.json.gz"):
            paths.add(f"results/final_{label}/{name}")
        for row in run["outcomes"]:
            if not is_gaussian(row):
                paths.add(grid_path(row).resolve().relative_to(ROOT).as_posix())
    return {path: sha256(ROOT / path) for path in sorted(paths)}


def validate(arithmetic_reports, scoring_reports, joint_report):
    for label in LABELS:
        a, s = arithmetic_reports[label], scoring_reports[label]
        if not (a["same_event_sets"] and a["score_finite"] and a["draw_host_sets_correct"]
                and a["seeds_match_frozen_config"] and a["bootstrap_count_matches_summary"]):
            raise ValueError(f"{label}: identity, finite-score, or host-set check failed")
        for key in ("descriptives_max_abs_error", "mean_delta_summary_error", "joint_ci_max_error",
                    "M2_s_quantile_error", "fixed_draw_max_error", "conditional_ci_max_error"):
            if a[key] > 1e-10:
                raise ValueError(f"{label}: {key} exceeds tolerance")
        if a["seed_multiplicity_mismatches"] or a["joint_undefined_count"] != len(a["undefined_draw_indices"]):
            raise ValueError(f"{label}: draw reproducibility or missingness mismatch")
        if s["all_gaussian_M0_max_metric_error"] > 1e-9 or s["forecast_variance_max_error_s2"] > 1e-6:
            raise ValueError(f"{label}: baseline or variance check failed")
        if max(s["spot_max_metric_errors"].values()) > 1e-7:
            raise ValueError(f"{label}: independent score check failed")
        j = joint_report["runs"][label]
        if (not j["independent_M2"]["success"] or j["independent_M2_s_error"] > 1e-5
                or j["exact_all_models_max_parameter_error"] > 1e-8 or j["rescored_delta_error"] > 1e-8):
            raise ValueError(f"{label}: bounded refit/rescoring check failed")
    if arithmetic_reports["primary"]["joint_undefined_count"]:
        raise ValueError("Primary bootstrap contains undefined draws")
    if not joint_report["point_independent_M2"]["success"] or joint_report["point_M2_s_error"] > 1e-5:
        raise ValueError("Independent point M2 fit failed")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("results/final_review/numerics"))
    args = parser.parse_args()
    output = args.out if args.out.is_absolute() else ROOT / args.out
    started = time.monotonic()
    fe.era_limit("protected")
    runs = {label: read_run(label) for label in LABELS}
    before = input_hashes(runs)
    arithmetic_reports = {label: arithmetic(run) for label, run in runs.items()}
    scoring_reports = {label: scoring(run) for label, run in runs.items()}
    joint_report = joint_spots(runs)
    validate(arithmetic_reports, scoring_reports, joint_report)
    if input_hashes(runs) != before:
        raise RuntimeError("An audit input changed during execution")
    output.mkdir(parents=True, exist_ok=True)
    for name, report in (("arithmetic.json", arithmetic_reports), ("scoring.json", scoring_reports),
                         ("joint_spots.json", joint_report)):
        (output / name).write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    receipt = {
        "status": "passed bounded independent numerical audit",
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": "UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/audit_d065_numerics.py",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "audit_script_sha256": sha256(Path(__file__)),
        "input_sha256": before,
        "output_sha256": {name: sha256(output / name) for name in (
            "arithmetic.json", "scoring.json", "joint_spots.json"
        )},
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "runtime_seconds": round(time.monotonic() - started, 3),
        "primary_verdict": "inconclusive; no equivalence or absence-of-effect conclusion",
        "extension_joint_draws": {"requested": arithmetic_reports["extension"]["joint_draw_count"],
                                  "undefined": arithmetic_reports["extension"]["joint_undefined_count"],
                                  "effective": arithmetic_reports["extension"]["joint_effective_draws"]},
        "limits": [
            "No measurement extraction, raw FITS/header inspection, or downloads",
            "All stored multiplicities and conditional draws replayed; no full 2000-refit rerun",
            "Joint refitting and full rescoring checked only for draw 0 of each run",
            "Independent 512-node scoring limited to selected events; Gaussian M0 checked for all events",
            "Independent M2 optimizer shares the frozen calibration design; bounded scalar search is not a global optimizer proof",
            "Accepted-timing conditioning and reconstructed covariance remain scientific limitations",
            "Saved extension draws contain nonstandard JSON NaN; these reports use strict JSON",
        ],
    }
    (output / "receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: receipt[k] for k in ("status", "runtime_seconds", "extension_joint_draws")}), flush=True)


if __name__ == "__main__":
    main()
