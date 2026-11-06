"""Independent numerical and interface checks for the sprint-1 score chain."""

from __future__ import annotations

import argparse
import csv
import json
import math
import sys
import tempfile
from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr, ndtri

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))

import forecast_variance_components as f
import sprint1_forecast_core as c
from sprint1_outcome_adapter import grid_score, production_rows, score_outcomes, validate_i1


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def covariance_check(seed=20261106, replicates=200):
    rng = np.random.default_rng(seed)
    errors, stress = [], []
    for i in range(replicates):
        k = int(rng.integers(1, 9))
        n = rng.integers(-2000, 2001, k).astype(float)
        y = rng.normal(size=k)
        se = np.exp(rng.uniform(-3, 3, k))
        st0 = float(np.exp(rng.uniform(-3, 3)))
        sp = float(np.exp(rng.uniform(-8, -1)))
        rho = (-1.0, 1.0, float(rng.uniform(-1, 1)))[i % 3]
        p = {"n": n, "m": y, "se": se, "st0": st0, "sp": sp, "rho": rho}
        pre = f.precompute([p], [y])
        base = (st0 * st0 + sp * sp * np.outer(n, n)
                + rho * st0 * sp * (n[:, None] + n[None, :]))
        for scale in (1e-8, 1e-3, 1.0, 1e3, 1e8):
            total = np.diag(se * se) + scale * base
            sign, logdet = np.linalg.slogdet(total)
            if sign <= 0:
                raise RuntimeError("Dense covariance lost positive definiteness")
            expected = -0.5 * (logdet + y @ np.linalg.solve(total, y) + k * np.log(2 * np.pi))
            actual = float(f.planet_ll(pre, scale)[0])
            condition = float(np.linalg.cond(total))
            (errors if condition < 1e10 else stress).append(abs(actual - expected))
    return {"replicates": replicates, "well_conditioned_dense_comparisons": len(errors),
            "max_abs_loglik_error_condition_lt_1e10": float(max(errors)),
            "ill_conditioned_dense_oracle_comparisons_excluded": len(stress),
            "max_dense_disagreement_in_excluded_stress_cases": float(max(stress)),
            "stress_note": "Dense solve is not an oracle near machine precision; the reviewed SVD form is designed to avoid this cancellation"}


def gradient_check(seed=20261106, replicates=20):
    rng = np.random.default_rng(seed)
    errors = []
    relative = []
    for _ in range(replicates):
        planets, ys = [], []
        for _ in range(7):
            k = int(rng.integers(1, 6))
            planets.append({"n": rng.integers(-500, 501, k).astype(float),
                            "se": np.exp(rng.uniform(-1, 2, k)),
                            "st0": float(np.exp(rng.uniform(-1, 2))),
                            "sp": float(np.exp(rng.uniform(-6, -2))),
                            "rho": float(rng.uniform(-.95, .95))})
            ys.append(rng.normal(0, 5, k))
        data = f.packed(f.precompute(planets, ys))
        weights = rng.uniform(.2, 2, len(planets))
        for mixture, theta in ((False, np.array([rng.uniform(-1, 1)])),
                               (True, np.array([rng.uniform(-1, 1), rng.uniform(-1, 1)]))):
            value, analytic = f.objective(theta, data, mixture, 192,
                                          np.zeros(len(planets)), weights)
            numeric = []
            for j in range(len(theta)):
                step = 1e-6 * max(1., abs(theta[j]))
                delta = np.zeros(len(theta)); delta[j] = step
                plus = -float(weights @ f.objective(theta + delta, data, mixture, 192,
                                                    np.zeros(len(planets)), weights, gradient=False))
                minus = -float(weights @ f.objective(theta - delta, data, mixture, 192,
                                                     np.zeros(len(planets)), weights, gradient=False))
                numeric.append((plus - minus) / (2 * step))
            numeric = np.asarray(numeric)
            diff = np.abs(analytic - numeric)
            errors.extend(diff.tolist())
            relative.extend((diff / np.maximum(1., np.abs(numeric))).tolist())
            if not np.isfinite(value):
                raise RuntimeError("Non-finite objective in gradient check")
    return {"replicates": replicates, "comparisons": len(errors),
            "max_abs_gradient_error": float(max(errors)),
            "max_scaled_gradient_error": float(max(relative))}


def adaptive_cdf(value, ratio, s):
    integrand = lambda z: math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi) * ndtr(
        value / math.sqrt(ratio * ratio + math.exp(s * z)))
    return quad(integrand, -12, 12, epsabs=2e-12, epsrel=2e-11, limit=300)[0]


def adaptive_nll(value, ratio, s):
    def integrand(z):
        variance = ratio * ratio + math.exp(s * z)
        return (math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)
                * math.exp(-0.5 * value * value / variance) / math.sqrt(2 * math.pi * variance))
    density = quad(integrand, -12, 12, epsabs=2e-13, epsrel=2e-10, limit=400)[0]
    return -math.log(density)


def quadrature_check():
    rows = []
    for s in (0.1, 1.0, 2.5, 5.0):
        for ratio in (0.01, 1.0, 100.0):
            q = c.mixture_quantiles(np.array([ratio]), s, order=384)[0]
            adaptive_q = []
            for prob in (0.841344746, 0.975):
                upper = max(float(q[1]) * 2, 10 * math.sqrt(1 + ratio * ratio))
                adaptive_q.append(brentq(lambda x: adaptive_cdf(x, ratio, s) - prob, 0, upper,
                                          xtol=1e-10, rtol=1e-11))
            for multiple in (0.0, 1.0, 5.0):
                value = multiple * math.sqrt(1 + ratio * ratio)
                event = {"forecast_variance_s2": 1.0, "sigma_s": ratio,
                         "outcome_scale": 1.0, "residual_s": value}
                gh = c.predictive_scores([event], {"b": 1.0, "s_log_lambda": s},
                                         order=384, interpolate=False)
                rows.append({"s": s, "ratio": ratio, "multiple": multiple,
                             "quantile_max_abs_error": float(np.max(np.abs(q - adaptive_q))),
                             "nll_abs_error": abs(float(gh["negative_log_score_seconds"][0])
                                                  - adaptive_nll(value, ratio, s))})
    return {"cases": len(rows),
            "max_quantile_abs_error": max(r["quantile_max_abs_error"] for r in rows),
            "max_nll_abs_error": max(r["nll_abs_error"] for r in rows),
            "worst_quantile": max(rows, key=lambda r: r["quantile_max_abs_error"]),
            "worst_nll": max(rows, key=lambda r: r["nll_abs_error"])}


def analytic_gaussian_score_check(seed=20261106, replicates=200):
    rng = np.random.default_rng(seed)
    errors = defaultdict(list)
    z68, z95 = ndtri(.841344746), ndtri(.975)
    for _ in range(replicates):
        vf = float(np.exp(rng.uniform(-5, 15)))
        sy = float(np.exp(rng.uniform(-3, 8)))
        y = float(rng.normal(0, math.sqrt(vf + sy * sy) * 5))
        event = {"forecast_variance_s2": vf, "sigma_s": sy,
                 "outcome_scale": 1., "residual_s": y}
        got = c.predictive_scores([event], {"b": 1., "s_log_lambda": 0.},
                                  interpolate=False)
        sd = math.sqrt(vf + sy * sy)
        width68, width95 = z68 * sd, z95 * sd
        expected = {
            "is95_standardised": (2 * width95 + 40 * max(abs(y) - width95, 0)) / sd,
            "is95_minutes": (2 * width95 + 40 * max(abs(y) - width95, 0)) / 60,
            "negative_log_score_seconds": .5 * (math.log(2 * math.pi * sd * sd) + y * y / (sd * sd)),
            "covered68": float(abs(y) <= width68),
            "covered95": float(abs(y) <= width95),
            "width95_minutes": 2 * width95 / 60,
        }
        for key, value in expected.items():
            errors[key].append(abs(float(got[key][0]) - value))
    return {"replicates": replicates,
            "max_abs_error": {key: float(max(value)) for key, value in errors.items()}}


def grid_convolution_check():
    x = np.linspace(-40, 50, 1801)
    measurement_mean, measurement_sd = 4., 3.
    density = np.exp(-.5 * ((x - measurement_mean) / measurement_sd) ** 2)
    widths = np.r_[np.diff(x)[0] / 2, (x[2:] - x[:-2]) / 2, np.diff(x)[-1] / 2]
    mass = density * widths
    mass /= mass.sum()
    forecast_variance = 25.
    residual = 7.
    denominator = math.sqrt(forecast_variance + measurement_sd ** 2)
    got = grid_score(residual, forecast_variance, {"b": 1., "s_log_lambda": 0.},
                     (x, mass), denominator)
    mean = -measurement_mean
    z68, z95 = ndtri(.841344746), ndtri(.975)
    lower, upper = mean - z95 * denominator, mean + z95 * denominator
    is95 = upper - lower + 40 * (max(lower - residual, 0) + max(residual - upper, 0))
    expected = {
        "is95_standardised": is95 / denominator,
        "is95_minutes": is95 / 60,
        "negative_log_score_seconds": .5 * (math.log(2 * math.pi * denominator ** 2)
                                                + (residual - mean) ** 2 / denominator ** 2),
        "covered68": float(mean - z68 * denominator <= residual <= mean + z68 * denominator),
        "covered95": float(lower <= residual <= upper),
        "width95_minutes": (upper - lower) / 60,
    }
    return {"measurement_offset_mean_s": measurement_mean,
            "expected_reported_residual_mean_s": mean,
            "max_abs_error": float(max(abs(got[key] - value) for key, value in expected.items())),
            "errors": {key: float(abs(got[key] - value)) for key, value in expected.items()}}


def aggregate_detail(path):
    rows = list(csv.DictReader(path.open()))
    by = defaultdict(dict)
    for r in rows:
        by[(r["method"], r["planet"])].setdefault("rows", []).append(r)
    out = {}
    for method in ("M1", "M2", "M3"):
        out[method] = {}
        for metric in ("is95_standardised", "is95_forecast_normalised", "is95_minutes"):
            delta = []
            planets = sorted({r["planet"] for r in rows})
            for planet in planets:
                a = np.mean([float(r[metric]) for r in by[(method, planet)]["rows"]])
                b = np.mean([float(r[metric]) for r in by[("M0", planet)]["rows"]])
                delta.append(a - b)
            out[method][metric] = {"mean_planet_delta": float(np.mean(delta)),
                                   "median_planet_delta": float(np.median(delta)),
                                   "fraction_planets_improved": float(np.mean(np.asarray(delta) < 0))}
    return out


def observed_weighting_checks():
    out = {}
    for name in ("release_transfer", "chronological", "delayed_origin", "late_published_proxy"):
        path = ROOT / "data/derived/sprint1" / name / "a_1.087/c2/scores.csv"
        out[name] = aggregate_detail(path) if path.exists() else {"status": "detail_not_yet_available"}
    return out


def artifact_checks():
    out = {}
    metrics = ("is95_standardised", "is95_minutes", "is95_forecast_normalised",
               "negative_log_score_seconds", "covered68", "covered95", "width95_minutes")
    for name in ("release_transfer", "chronological", "delayed_origin", "late_published_proxy"):
        directory = ROOT / "data/derived/sprint1" / name / "a_1.087/c2"
        required = [directory / p for p in ("events.csv", "forecasts.csv", "parameters.json", "scores.csv")]
        if not all(p.exists() for p in required):
            out[name] = {"status": "primary_detail_not_yet_complete",
                         "missing": [str(p.relative_to(ROOT)) for p in required if not p.exists()]}
            continue
        events = list(csv.DictReader((directory / "events.csv").open()))
        training_events = list(csv.DictReader((directory / "training_events.csv").open()))
        forecasts = list(csv.DictReader((directory / "forecasts.csv").open()))
        score_rows = list(csv.DictReader((directory / "scores.csv").open()))
        summary = json.loads((ROOT / "results/sprint1/forecasts" /
                              f"{name}__a_1.087__c2.json").read_text())
        event_ids = [r["event_id"] for r in events]
        forecast_ids = [r["event_id"] for r in forecasts]
        parameter_hash = c.digest(directory / "parameters.json")
        by_score = {(r["method"], r["event_id"]): r for r in score_rows}
        if len(by_score) != len(score_rows):
            raise RuntimeError("Duplicate score row")
        if set(event_ids) != set(forecast_ids):
            raise RuntimeError("Primary event and forecast sets differ")
        if set(by_score) != {(m, event_id) for m in c.METHODS for event_id in event_ids}:
            raise RuntimeError("Primary score grid is incomplete")
        if any(r["parameter_version"] != parameter_hash for r in forecasts + score_rows):
            raise RuntimeError("Parameter version hash mismatch")
        max_variance_error = 0.
        for r in forecasts:
            expected = float(c.forecast_variance(float(r["sigma_t0_s"]), float(r["sigma_p_s"]),
                                                 float(r["forecast_epoch"]), float(r["rho"])))
            max_variance_error = max(max_variance_error, abs(expected - float(r["forecast_variance_s2"])))
        max_metric_error = 0.
        max_weight_error = 0.
        planets = sorted({r["planet"] for r in events})
        for method in c.METHODS:
            ordered = [by_score[(method, event_id)] for event_id in event_ids]
            weights = np.array([float(r["weight"]) for r in ordered])
            max_weight_error = max(max_weight_error, abs(weights.sum() - 1))
            for planet in planets:
                total = sum(float(r["weight"]) for r in ordered if r["planet"] == planet)
                max_weight_error = max(max_weight_error, abs(total - 1 / len(planets)))
            for metric in metrics:
                values = np.array([float(r[metric]) for r in ordered])
                _, planet_means = c.planet_aggregate(events, values)
                actual = float(planet_means.mean())
                max_metric_error = max(max_metric_error,
                                       abs(actual - float(summary["metrics"][method][metric])))
            delta = np.array([float(r["is95_standardised"]) -
                              float(by_score[("M0", r["event_id"])]["is95_standardised"])
                              for r in ordered])
            _, planet_delta = c.planet_aggregate(events, delta)
            checks = {
                "delta_standardised_vs_M0": float(planet_delta.mean()),
                "median_planet_delta_standardised": float(np.median(planet_delta)),
                "fraction_planets_improved": float(np.mean(planet_delta < 0)),
            }
            for key, value in checks.items():
                max_metric_error = max(max_metric_error,
                                       abs(value - float(summary["metrics"][method][key])))
        out[name] = {"status": "checked", "events": len(events), "planets": len(planets),
                     "training_C3_planets": sorted({r["planet"] for r in training_events
                                                    if r["covariance_tier"].startswith("C3")}),
                     "scoring_C3_planets": sorted({r["planet"] for r in events
                                                   if r["covariance_tier"].startswith("C3")}),
                     "score_rows": len(score_rows), "parameter_sha256": parameter_hash,
                     "max_abs_forecast_variance_reconstruction_error_s2": float(max_variance_error),
                     "max_abs_summary_reaggregation_error": float(max_metric_error),
                     "max_abs_weight_invariant_error": float(max_weight_error)}
    return out


def m2_semantics():
    out = []
    gaussian_z = np.array([ndtri(0.841344746), ndtri(0.975)])
    for s in (1.0, 2.1618792749978195, 2.5, 5.0):
        for ratio in (0.01, 1.0, 100.0):
            q = c.mixture_quantiles(np.array([ratio]), s, order=384)[0]
            baseline = gaussian_z * math.sqrt(1 + ratio * ratio)
            out.append({"s": s, "outcome_to_forecast_sd_ratio": ratio,
                        "central68_halfwidth_ratio_to_M0": float(q[0] / baseline[0]),
                        "central95_halfwidth_ratio_to_M0": float(q[1] / baseline[1])})
    return out


def sensitivity_decisions():
    out = {}
    base = ROOT / "results/sprint1/forecasts"
    for name in ("release_transfer", "chronological", "delayed_origin", "late_published_proxy"):
        rows = []
        for path in sorted(base.glob(f"{name}__a_*__*.json")):
            value = json.loads(path.read_text())
            ci = value["host_refit"]["M2"]["delta_is95_standardised_percentile95"]
            rows.append({"a": value["a"], "covariance": value["covariance"],
                         "point_delta": value["metrics"]["M2"]["delta_standardised_vs_M0"],
                         "percentile95": ci,
                         "conditional_decision": value["host_refit"]["M2"]["conditional_decision"]})
        out[name] = rows
    return out


def bootstrap_tail_resolution():
    out = {}
    for name in ("release_transfer", "chronological"):
        out[name] = {}
        for a in ("1", "1.087"):
            path = ROOT / "data/derived/sprint1" / name / f"a_{a}/c2/host_refit_bootstrap.csv"
            if not path.exists():
                continue
            rows = [r for r in csv.DictReader(path.open()) if r["method"] == "M2"]
            values = np.asarray([float(r["delta_is95_standardised"]) for r in rows])
            out[name][a] = {"replicates": len(values),
                            "positive_replicates": int(np.sum(values > 0)),
                            "upper_tail_quantiles": {str(q): float(np.quantile(values, q))
                                                     for q in (.95, .97, .975, .98, .99)}}
    return out


def epoch_identity_check():
    eph, _, _ = c.load()
    out = {}
    for name in ("release_transfer", "chronological"):
        path = ROOT / "data/derived/sprint1" / name / "a_1.087/c2/events.csv"
        rows = list(csv.DictReader(path.open()))
        ratios = []
        for r in rows:
            period_s = eph[r["release"]][r["planet"]].period_days * 86400
            ratios.append(abs(float(r["residual_s"])) / period_s)
        out[name] = {"events": len(rows), "max_abs_residual_over_period": float(max(ratios)),
                     "events_over_quarter_period": int(np.sum(np.asarray(ratios) > .25)),
                     "events_over_half_period": int(np.sum(np.asarray(ratios) > .5)),
                     "assignment_note": "development_events derives cycle by rounding the scored mid-time against the issued ephemeris; no realised adjacent-cycle wrap is present, but independent cycle identity is not established"}
    return out


def receipt_checks():
    out = {}
    base = ROOT / "results/sprint1/forecasts"
    for path in sorted(base.glob("receipt_*.json")):
        receipt = json.loads(path.read_text())
        bad_summaries, missing, bad_code = [], [], []
        for name, expected in receipt.get("summary_hashes", {}).items():
            source = ROOT / name
            if not source.exists():
                missing.append(name)
            elif c.digest(source) != expected:
                bad_summaries.append(name)
        for name, expected in receipt["source_config_sha256"].items():
            source = ROOT / name
            if not source.exists() or c.digest(source) != expected:
                bad_code.append(name)
        out[path.name] = {"recorded_summaries": len(receipt.get("summary_hashes", {})),
                          "missing_summaries": missing,
                          "summary_hash_mismatches": bad_summaries,
                          "current_code_hash_mismatches": bad_code,
                          "protected_access": receipt.get("protected_access")}
    return out


def interface_counterexamples():
    try:
        production_rows([{"event_id": "e", "observation_id": "o",
                          "product": "SPOC_120", "flux": "", "status": "timed"}])
        blank = "accepted"
    except ValueError as exc:
        blank = str(exc)
    x = np.linspace(-20, 20, 401)
    density = np.exp(-0.5 * (x / 3) ** 2)
    mass = density / density.sum()
    try:
        grid_score(0.0, 0.0, {"b": 1.0, "s_log_lambda": 0.0}, (x, mass), 3.0)
        singular = "accepted"
    except ValueError as exc:
        singular = str(exc)
    full_i1 = {"event_id":"i1","observation_id":"obs","planet":"Planet b","host":"Planet",
               "tic":"1","sector":"56","camera":"1","ccd":"1","product":"SPOC_120",
               "flux":"PDCSAP","file":"product.fits","file_sha256":"0"*64,"data_rel":"35",
               "cadenceno_first":"1","cadenceno_last":"2","timesys":"TDB",
               "timeref":"SOLARSYSTEM","bjdrefi":"2457000","bjdreff":"0",
               "tc_bjd_tdb":"2460000","sigma_s":"5","gauss_ok":"true",
               "q025_s":"-9.79982","q1587_s":"-5","q8413_s":"5",
               "q975_s":"9.79982","posterior_grid_path":"","shape_group_id":"group",
               "loo_shift_s":"0","id_method":"blind","id_period_d":"2",
               "id_period_source":"source","id_period_source_date":"2024-01-01",
               "coverage_window":"1","coverage_in_transit":"1","status":"timed",
               "failure_reason":"","error_convention":"t015v2_beta_chi","rule_version":"version"}
    validate_i1([full_i1])
    try:
        validate_i1([{**full_i1, "id_method":""}])
        blank_id_method = "accepted"
    except ValueError as exc:
        blank_id_method = str(exc)
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        forecasts = td / "forecasts.csv"; outcomes = td / "outcomes.csv"
        score_path = td / "scores.csv"
        fc_rows = []
        for event in ("present", "missing"):
            fc_rows.append({"event_id": event, "observation_id": event, "planet": "P" + event,
                            "host": "H" + event, "release": "DRC", "predicted_bjd_tdb": 2460000.0,
                            "forecast_variance_s2": 100.0, "parameter_version": "v",
                            "M0_b": 1.0, "M0_s_log_lambda": 0.0,
                            "M1_b": 1.2, "M1_s_log_lambda": 0.0,
                            "M2_b": 1.0, "M2_s_log_lambda": 1.0,
                            "M3_b": 1.2, "M3_s_log_lambda": 1.0})
        with forecasts.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fc_rows[0]))
            writer.writeheader(); writer.writerows(fc_rows)
        outcome = {"event_id": "present", "observation_id": "present", "planet": "Ppresent",
                   "host": "Hpresent", "product": "SPOC_120", "flux": "PDCSAP", "status": "timed",
                   "timesys": "TDB", "timeref": "SOLARSYSTEM", "tc_bjd_tdb": 2460000.0,
                   "sigma_s": 5.0, "error_convention": "exoclock_reported", "shape_group_id": "g"}
        with outcomes.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(outcome))
            writer.writeheader(); writer.writerow(outcome)
        try:
            score_outcomes(SimpleNamespace(forecasts=str(forecasts), outcomes=str(outcomes),
                                           error_convention="exoclock_reported", outcome_scale=1.0,
                                           output=str(score_path)))
            mismatch = "accepted"
        except ValueError as exc:
            mismatch = str(exc)
        with forecasts.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(fc_rows[0]))
            writer.writeheader(); writer.writerow(fc_rows[0])
        failed = {**outcome, "status": "id_failed", "failure_reason": "synthetic_failure"}
        with outcomes.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(failed))
            writer.writeheader(); writer.writerow(failed)
        score_outcomes(SimpleNamespace(forecasts=str(forecasts), outcomes=str(outcomes),
                                       error_convention="exoclock_reported", outcome_scale=1.0,
                                       output=str(score_path)))
        receipt = json.loads(score_path.with_suffix(".receipt.json").read_text())
        header_only = len(score_path.read_text().splitlines()) == 1
    return {"blank_flux_result": blank,
            "complete_i1_row_result": "accepted",
            "blank_id_method_result": blank_id_method,
            "zero_forecast_variance_nonGaussian_result": singular,
            "extra_forecast_rows": 1,
            "forecast_attempt_set_mismatch_result": mismatch,
            "all_failed_receipt": receipt,
            "all_failed_score_has_header_only": header_only}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(ROOT / "results/sprint1/scoring_review/numerical_checks.json"))
    args = parser.parse_args()
    result = {"covariance_dense_check": covariance_check(),
              "likelihood_gradient_check": gradient_check(),
              "mixture_adaptive_check": quadrature_check(),
              "gaussian_analytic_score_check": analytic_gaussian_score_check(),
              "grid_convolution_check": grid_convolution_check(),
              "observed_weighting": observed_weighting_checks(),
              "artifact_checks": artifact_checks(),
              "m2_width_semantics": m2_semantics(),
              "sensitivity_decisions": sensitivity_decisions(),
              "bootstrap_tail_resolution": bootstrap_tail_resolution(),
              "epoch_identity_check": epoch_identity_check(),
              "receipt_checks": receipt_checks(),
              "interface_counterexamples": interface_counterexamples(),
              "protected_data_accessed": False}
    write_json(Path(args.output), result)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
