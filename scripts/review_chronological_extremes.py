"""Audit extreme chronological-bootstrap fits without opening light curves.

Replays selected joint-host bootstrap replicates from chronological_calibration.py
at the primary fixed outcome scale a=1.  It compares 384- and 768-node
Gauss-Hermite scoring with independent wide-range adaptive integration and
attributes each resampled score contrast to evaluation hosts.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import chronological_calibration as chronological  # noqa: E402
import forecast_variance_components as variance  # noqa: E402
from review_tranche2_mixture import stable_planet_ll, stable_precompute  # noqa: E402

PRIMARY_A = 1.0
SEED = 20261107
REPLICATES = (6, 61, 273, 325)
LOG2PI = float(np.log(2 * np.pi))


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def wide_log_integral(item, b, s):
    def log_integrand(z):
        c = b * b * np.exp(s * z)
        return float(stable_planet_ll(item, c) - 0.5 * z * z - 0.5 * LOG2PI)

    optimum = minimize_scalar(
        lambda z: -log_integrand(z),
        bounds=(-100.0, 100.0),
        method="bounded",
        options={"xatol": 1e-10},
    )
    mode = float(optimum.x)
    peak = log_integrand(mode)
    value, error = quad(
        lambda z: np.exp(log_integrand(z) - peak),
        mode - 15.0,
        mode + 15.0,
        epsabs=1e-12,
        epsrel=1e-11,
        limit=500,
    )
    return peak + np.log(value), mode, float(error / value)


def model_summary(model):
    keys = (
        "b",
        "s_log_lambda",
        "beta_log_sd",
        "nll",
        "gradient_max",
        "at_bound",
    )
    result = {key: model[key] for key in keys if key in model}
    if "s_log_lambda" in model:
        result["near_zero_heterogeneity"] = model["s_log_lambda"] < 1e-3
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default=str(ROOT / "results/pilot_v1/chronological_calibration/extreme_audit.json"),
    )
    args = parser.parse_args(argv)

    variance.source_manifest()
    metadata_path = ROOT / "results/pilot_v1/tranche2_review/metadata_per_planet.csv"
    metadata = {row["planet"]: row for row in csv.DictReader(metadata_path.open())}
    train, train_clipped = variance.visits(
        "DRC", PRIMARY_A, start="2022-01-01", end="2022-12-31"
    )
    test, test_clipped = variance.visits(
        "DRC", PRIMARY_A, start="2023-01-01", end="2024-01-03"
    )
    if train_clipped or test_clipped:
        raise ValueError("Chronological extreme audit requires no outcome trimming")

    pre_train = variance.precompute(train, [planet["m"] for planet in train])
    pre_test = variance.precompute(test, [planet["m"] for planet in test])
    independent_test = stable_precompute(test, [planet["m"] for planet in test])
    span_train = np.array(
        [np.log10(float(metadata[planet["planet"]]["training_span_days"])) for planet in train]
    )
    span_test = np.array(
        [np.log10(float(metadata[planet["planet"]]["training_span_days"])) for planet in test]
    )
    train_hosts = np.array([planet["host"] for planet in train])
    test_hosts = np.array([planet["host"] for planet in test])
    windows = np.array([len(planet["m"]) for planet in test])

    rng = np.random.default_rng(SEED)
    selected = {}
    for replicate in range(max(REPLICATES) + 1):
        train_weights, test_weights = chronological.bootstrap_indices(
            train_hosts, test_hosts, rng
        )
        if replicate in REPLICATES:
            selected[replicate] = (train_weights, test_weights)

    results = []
    for replicate in REPLICATES:
        train_weights, test_weights = selected[replicate]
        fitted = {}
        for order in (384, 768):
            with np.errstate(divide="ignore"):
                models, centre, sd = chronological.train_models(
                    train, pre_train, span_train, train_weights, order
                )
                scores = chronological.score_models(
                    models, pre_test, span_test, centre, sd, order
                )
            contrast = (scores["span_mixture"] - scores["constant_mixture"]) / windows
            fitted[order] = {
                "models": models,
                "centre": centre,
                "sd": sd,
                "scores": scores,
                "contrast": contrast,
                "mean_contrast": float(np.average(contrast, weights=test_weights)),
            }

        base = fitted[384]
        x_test = (span_test - base["centre"]) / base["sd"]
        adaptive_scores = {}
        adaptive_modes = {}
        adaptive_errors = {}
        for name in ("constant_mixture", "span_mixture"):
            model = base["models"][name]
            beta = model.get("beta_log_sd", 0.0)
            values = [
                wide_log_integral(
                    item,
                    model["b"] * np.exp(beta * x),
                    model["s_log_lambda"],
                )
                for item, x in zip(independent_test, x_test)
            ]
            adaptive_scores[name] = np.array([value[0] for value in values])
            adaptive_modes[name] = np.array([value[1] for value in values])
            adaptive_errors[name] = np.array([value[2] for value in values])

        adaptive_contrast = (
            adaptive_scores["span_mixture"] - adaptive_scores["constant_mixture"]
        ) / windows
        host_contributions = []
        for host in np.unique(test_hosts[test_weights > 0]):
            use = test_hosts == host
            host_contributions.append(
                {
                    "host": str(host),
                    "resample_count": int(test_weights[use][0]),
                    "contribution_to_resampled_mean": float(
                        np.sum(test_weights[use] * adaptive_contrast[use])
                        / test_weights.sum()
                    ),
                    "planets": [
                        {
                            "planet": test[index]["planet"],
                            "windows": int(windows[index]),
                            "contrast_per_window": float(adaptive_contrast[index]),
                        }
                        for index in np.where(use)[0]
                    ],
                }
            )
        host_contributions.sort(key=lambda row: row["contribution_to_resampled_mean"])

        result = {
            "replicate": replicate,
            "nonzero_training_hosts": int(np.sum(train_weights > 0)),
            "nonzero_evaluation_hosts": int(np.sum(test_weights > 0)),
            "training_planet_weight_sum": int(train_weights.sum()),
            "evaluation_planet_weight_sum": int(test_weights.sum()),
            "training_predictor_centre": base["centre"],
            "training_predictor_sd": base["sd"],
            "q384": {
                "span_vs_constant_mean_nats_per_window": base["mean_contrast"],
                "constant_mixture": model_summary(base["models"]["constant_mixture"]),
                "span_mixture": model_summary(base["models"]["span_mixture"]),
            },
            "q768": {
                "span_vs_constant_mean_nats_per_window": fitted[768]["mean_contrast"],
                "constant_mixture": model_summary(
                    fitted[768]["models"]["constant_mixture"]
                ),
                "span_mixture": model_summary(fitted[768]["models"]["span_mixture"]),
            },
            "wide_adaptive": {
                "span_vs_constant_mean_nats_per_window": float(
                    np.average(adaptive_contrast, weights=test_weights)
                ),
                "max_abs_q384_minus_adaptive_log_density": {
                    name: float(np.max(np.abs(base["scores"][name] - adaptive_scores[name])))
                    for name in adaptive_scores
                },
                "max_abs_posterior_mode_z": {
                    name: float(np.max(np.abs(adaptive_modes[name])))
                    for name in adaptive_modes
                },
                "max_relative_integration_error": {
                    name: float(np.max(adaptive_errors[name]))
                    for name in adaptive_errors
                },
            },
            "most_adverse_host_contributions": host_contributions[:5],
            "most_favourable_host_contributions": host_contributions[-5:][::-1],
        }
        if abs(result["q384"]["span_vs_constant_mean_nats_per_window"] - result["wide_adaptive"]["span_vs_constant_mean_nats_per_window"]) > 1e-6:
            raise AssertionError("Q384 and adaptive scores disagree")
        if abs(result["q384"]["span_vs_constant_mean_nats_per_window"] - result["q768"]["span_vs_constant_mean_nats_per_window"]) > 0.01:
            raise AssertionError("Q384 and Q768 scores disagree")
        results.append(result)

    dependencies = [
        ROOT / "scripts/chronological_calibration.py",
        ROOT / "scripts/forecast_variance_components.py",
        ROOT / "scripts/review_tranche2_mixture.py",
        metadata_path,
    ]
    report = {
        "development_only": True,
        "light_curves_opened": 0,
        "conclusion": "Extreme bootstrap losses are reproduced numerical consequences of near-zero fitted heterogeneity and predictor extrapolation, not quadrature error.",
        "primary_a": PRIMARY_A,
        "bootstrap_seed": SEED,
        "selected_replicates": list(REPLICATES),
        "training_dates": ["2022-01-01", "2022-12-31"],
        "evaluation_dates": ["2023-01-01", "2024-01-03"],
        "near_zero_heterogeneity_threshold": 1e-3,
        "replicates": results,
        "source_manifest": variance.source_manifest(),
        "git_head": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "script_sha256": sha256(Path(__file__)),
        "dependencies": [
            {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}
            for path in dependencies
        ],
        "command": "python scripts/review_chronological_extremes.py",
        "limitations": [
            "Selected adverse replicates diagnose the completed 400-replicate bootstrap; they are not a new uncertainty interval.",
            "All outcomes were previously inspected and the training-span predictor was selected using the full development era.",
            "This is an observation-cutoff development hindcast, not availability-correct Track A.",
            "The outcome scale, model family and cohort are fixed; issued T0-period covariance remains missing.",
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(output),
                "scores": {
                    row["replicate"]: row["q384"][
                        "span_vs_constant_mean_nats_per_window"
                    ]
                    for row in results
                },
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
