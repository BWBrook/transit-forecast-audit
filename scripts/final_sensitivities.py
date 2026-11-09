"""Declared sensitivity settings, implemented after unblinding on 9 November 2026.

    UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/final_sensitivities.py

No measurement, FITS access, downloads, primary modification or joint-bootstrap
rerun. Conditional host intervals hold each development-fitted scenario fixed.
They are secondary diagnostics and do not determine a new primary verdict.
"""

from __future__ import annotations

import os
for _thread_variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS",
                         "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ[_thread_variable] = "1"

import argparse
import csv
import gzip
import hashlib
import json
import multiprocessing
import platform
import subprocess
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import acceptance as A
import final_evaluation as fe
import prefreeze_package as pp
import sprint1_forecast_core as c
import sprint1_outcome_adapter as ad
import sprint2_forecasts as s2
import sprint2_outcomes as so
from reproduce_table5 import load

METHODS = ("M0", "M1", "M2", "M3")
METRICS = ("is95_standardised", "is95_minutes", "is95_forecast_normalised",
           "negative_log_score_seconds", "covered68", "covered95", "width95_minutes",
           "m0_predictive_sd_s")
CASES = ("baseline", "rho_zero", "rho_minus1", "rho_plus1", "all_spoc_training",
         "journal_anchor", "C2_only", "outcome_scale_div_1p1", "outcome_scale_x_1p1",
         "majority_gate", "t015v3c")
CASE_RHO = {"rho_zero": 0., "rho_minus1": -1., "rho_plus1": 1.}
OUT = ROOT / "results/final_secondaries/sensitivities"
SCORES = ROOT / "data/derived/final_secondaries/sensitivity_scores"
CONDITIONAL_B, CONDITIONAL_SEED = 10000, 20261109
_CONTEXT = {}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False,
                               default=lambda x: x.item()) + "\n")


def write_csv(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(key for row in rows for key in row)) or ["event_id"]
    with (gzip.open(path, "wt", newline="") if path.suffix == ".gz" else path.open("w", newline="")) as stream:
        writer = csv.DictWriter(stream, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def product_key(row):
    return row["planet"], str(int(float(row["sector"]))), row["product"]


def majority_products(raw_windows):
    grouped = defaultdict(lambda: {"raw_windows": 0, "denominator": 0, "numerator": 0})
    for row in raw_windows:
        result = grouped[product_key(row)]
        result["raw_windows"] += 1
        status = row.get("status")
        if status in ("timed", "edge", "integration_unresolved"):
            result["denominator"] += 1
            if status == "timed" and not (A.INTEGRATION_FLAGS & set((row.get("flags") or "").split(";"))):
                result["numerator"] += 1
    for result in grouped.values():
        result["passes"] = result["denominator"] > 0 and 2 * result["numerator"] > result["denominator"]
    return dict(grouped)


def numeric_jd(utc_stamp):
    stamp = datetime.fromisoformat(utc_stamp.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("Journal anchor must carry a UTC offset")
    return stamp.timestamp() / 86400 + 2440587.5


def journal_status(forecast, anchor_jd, margin_days=10 / 1440):
    difference = float(forecast["predicted_bjd_tdb"]) - anchor_jd
    if abs(difference) <= margin_days:
        return "excluded_numeric_journal_boundary_10min"
    if difference < 0:
        return "excluded_before_numeric_journal_anchor"
    return None


def scaled_event(event, factor=1., rho=None):
    result = dict(event)
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError("Outcome scale must be finite and positive")
    result["sigma_s"] = float(event["sigma_s"]) * factor
    if rho is not None:
        result["rho"] = rho
        result["forecast_variance_s2"] = float(c.forecast_variance(
            float(event["sigma_t0_s"]), float(event["sigma_p_s"]),
            float(event["forecast_epoch"]), rho,
        ))
    if event.get("grid") is not None:
        x, weights = event["grid"]
        x = np.asarray(x) * factor
        result["grid"] = x, weights
        noise_variance = float(weights @ (x * x) - (weights @ x) ** 2)
        result["denom"] = float(np.sqrt(result["forecast_variance_s2"] + noise_variance))
    return result


def conditional_intervals(planets, hosts, deltas, replicates=CONDITIONAL_B, seed=CONDITIONAL_SEED):
    unique_hosts = sorted(set(hosts))
    host_index = {host: i for i, host in enumerate(unique_hosts)}
    planet_host_indices = [host_index[host] for host in hosts]
    rng = np.random.default_rng(seed)
    values = []
    for _ in range(replicates):
        multiplicity = np.bincount(rng.integers(0, len(unique_hosts), len(unique_hosts)),
                                   minlength=len(unique_hosts))[planet_host_indices]
        values.append(np.average(deltas, weights=multiplicity, axis=0))
    return np.quantile(values, [.025, .975], axis=0).T.tolist()


def aggregate(events, scores, case):
    planets = sorted({event["planet"] for event in events})
    grouped = {planet: np.array([i for i, event in enumerate(events) if event["planet"] == planet])
               for planet in planets}
    host = {event["planet"]: event["host"] for event in events}
    planet_values = {model: {metric: np.array([np.mean(scores[model][metric][grouped[p]])
                                               for p in planets]) for metric in METRICS}
                     for model in METHODS}
    metrics = {model: {metric: float(values.mean()) for metric, values in columns.items()}
               for model, columns in planet_values.items()}
    deltas = np.column_stack([planet_values[m]["is95_standardised"]
                              - planet_values["M0"]["is95_standardised"] for m in METHODS[1:]])
    intervals = conditional_intervals(planets, [host[p] for p in planets], deltas)
    per_planet = []
    for i, planet in enumerate(planets):
        row = {"case": case, "planet": planet, "host": host[planet],
               "accepted_events": len(grouped[planet])}
        row.update({f"{m}_is95_standardised": float(planet_values[m]["is95_standardised"][i]) for m in METHODS})
        row.update({f"delta_{m}_minus_M0": float(deltas[i, j]) for j, m in enumerate(METHODS[1:])})
        per_planet.append(row)
    return metrics, per_planet, {model: intervals[j] for j, model in enumerate(METHODS[1:])}


def exact_scores(events, models, reuse, baseline_scores):
    result = {}
    gaussian = [i for i, event in enumerate(events) if event["grid"] is None]
    for model in METHODS:
        if model in reuse:
            result[model] = {metric: np.array([float(baseline_scores[event["event_id"], model][metric])
                                              for event in events]) for metric in METRICS}
            continue
        result[model] = {metric: np.empty(len(events)) for metric in METRICS}
        if gaussian:
            values = c.predictive_scores([events[i] for i in gaussian], models[model], order=384, interpolate=False)
            for metric in METRICS:
                result[model][metric][gaussian] = values[metric]
        for index, event in enumerate(events):
            if event["grid"] is not None:
                values = ad.grid_score(event["residual_s"], event["forecast_variance_s2"],
                                       models[model], event["grid"], event["denom"], order=384)
                for metric in METRICS:
                    result[model][metric][index] = values[metric]
    return result


def model_difference(left, right):
    return max(abs(left[m][key] - right[m][key]) for m in METHODS for key in ("b", "s_log_lambda"))


def prepare():
    eph, _, flags = load()
    manifest = fe.read_csv(ROOT / "results/prefreeze/manifest_core_primary.csv")
    forecasts = fe.read_csv(ROOT / "results/prefreeze/forecasts_core_draft.csv.gz")
    raw_windows = fe.read_csv(ROOT / "data/derived/final_primary/measured/windows.csv.gz")
    raw_products = fe.read_csv(ROOT / "data/derived/final_primary/measured/products.csv")
    products = {(r["planet"], str(int(float(r["sector"])))): r for r in raw_products
                if r.get("planet") and r.get("product") == A.PRODUCT}
    coverage = {r["event_id"]: r for r in fe.read_csv(ROOT / "data/derived/final_primary/measured/coverage.csv")}
    ledger, outside = fe.terminal_ledger(manifest, raw_windows, products, coverage, eph["DRD"])
    stored_ledger = fe.read_csv(ROOT / "results/final_primary/terminal_ledger.csv.gz")
    if {(r["event_id"], r["status"]) for r in ledger} != {(r["event_id"], r["status"]) for r in stored_ledger}:
        raise RuntimeError("Reconstructed original terminal ledger differs")
    outcomes, accepted_forecasts = fe.scoring_inputs(ledger, raw_windows, forecasts)
    events = fe.event_representation(outcomes, accepted_forecasts)
    forecast_by_id = {r["event_id"]: r for r in forecasts}
    for event in events:
        forecast = forecast_by_id[event["event_id"]]
        event.update({key: float(forecast[key]) for key in ("sigma_t0_s", "sigma_p_s", "forecast_epoch", "rho")})
        event["covariance_tier"] = forecast["covariance_tier"]
    development_raw = fe.read_csv(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    development_gated, gate_counts = pp.gated_rows()
    core = pp.core_planets(eph)
    sp = json.loads((ROOT / "configs/sprint1.json").read_text())["experiments"]["release_transfer"]["test"]
    development, rejected = s2.our_events(sp["release"], sp["start"], sp["end"],
        [r for r in development_gated if r["planet"] in core], eph, flags, c.covariance_rows(), convention="t015v3")
    all_spoc, all_rejected = s2.our_events(sp["release"], sp["start"], sp["end"],
        development_gated, eph, flags, c.covariance_rows(), convention="t015v3")
    baseline_models = c.fit_methods(c.visit_planets(development))
    candidate = json.loads((ROOT / "results/prefreeze/candidate_parameters.json").read_text())
    frozen_models = json.loads((ROOT / "results/prefreeze/candidate_models_core_matched.json").read_text())["models"]
    difference = model_difference(baseline_models, frozen_models)
    if len(development) != 2186 or len({e["planet"] for e in development}) != 206 or difference > 1e-6:
        raise RuntimeError("Baseline development population or frozen-model reproduction failed")
    roster = {r["planet"]: float(r["tmag"]) for r in fe.read_csv(ROOT / "results/sprint2/freeze_candidate/roster.csv")}
    raw_by_id = {r["event_id"]: r for r in development_raw}
    accepted_by_id = {r["event_id"]: r for r in outcomes}
    return {
        "manifest": manifest, "forecasts": forecast_by_id, "ledger": ledger, "events": events,
        "baseline_scores": {(r["event_id"], r["method"]): r for r in fe.read_csv(ROOT / "results/final_primary/scores.csv")},
        "primary_summary": json.loads((ROOT / "results/final_primary/evaluation_summary.json").read_text()),
        "development": development, "all_spoc": all_spoc, "development_raw": raw_by_id,
        "baseline_models": baseline_models, "frozen_models": frozen_models, "candidate": candidate,
        "baseline_refit_max_error": difference, "roster_tmag": roster,
        "development_gate_counts": gate_counts,
        "development_rejected": dict(Counter(r["reason"] for r in rejected)),
        "all_spoc_rejected": dict(Counter(r["reason"] for r in all_rejected)),
        "majority_development": majority_products(development_raw),
        "majority_evaluation": majority_products(raw_windows),
        "accepted_by_id": accepted_by_id, "outside_manifest_windows": len(outside),
        "journal_anchor_jd": numeric_jd("2026-02-12T00:00:00Z"),
    }


def init_worker(context):
    global _CONTEXT
    _CONTEXT = context


def run_case(case):
    started = time.monotonic()
    context = _CONTEXT
    original_development = context["all_spoc"] if case == "all_spoc_training" else context["development"]
    training = []
    for event in original_development:
        if case == "C2_only" and event["covariance_tier"] != "C2_candidate":
            continue
        raw = context["development_raw"][event["event_id"]]
        if case == "majority_gate" and not context["majority_development"].get(product_key(raw), {}).get("passes", False):
            continue
        factor = (1 / 1.1 if case == "outcome_scale_div_1p1" else 1.1 if case == "outcome_scale_x_1p1"
                  else so.tmag_multiplier(raw["tmag"]) if case == "t015v3c" else 1.)
        training.append(scaled_event(event, factor, CASE_RHO.get(case)))
    models = (context["baseline_models"] if case in ("baseline", "journal_anchor")
              else c.fit_methods(c.visit_planets(training)))
    frozen_fit_error = None
    if case == "all_spoc_training":
        expected = context["candidate"]["fits"]["all_spoc"]
        frozen_fit_error = model_difference(models, expected["models"])
        if (len(training) != expected["training_events"]
                or len({e["planet"] for e in training}) != expected["training_planets"] or frozen_fit_error > 1e-6):
            raise RuntimeError("All-SPOC refit fails frozen all_spoc reproduction")
    elif case in ("baseline", "journal_anchor"):
        frozen_fit_error = context["baseline_refit_max_error"]
    eligible_ids, ledger = set(), []
    for original in context["ledger"]:
        row = dict(original)
        forecast = context["forecasts"][row["event_id"]]
        excluded = (journal_status(forecast, context["journal_anchor_jd"]) if case == "journal_anchor"
                    else "excluded_non_C2_sensitivity" if case == "C2_only" and forecast["covariance_tier"] != "C2_candidate" else None)
        if excluded:
            row["status"] = excluded
        else:
            eligible_ids.add(row["event_id"])
            if case == "majority_gate" and row["status"] == A.ACCEPTED:
                raw = context["accepted_by_id"][row["event_id"]]
                if not context["majority_evaluation"].get(product_key(raw), {}).get("passes", False):
                    row["status"] = "excluded_majority_product_gate"
        ledger.append(row)
    accepted_ids = {r["event_id"] for r in ledger if r["status"] == A.ACCEPTED}
    evaluation = []
    for event in context["events"]:
        if event["event_id"] not in accepted_ids:
            continue
        factor = (1 / 1.1 if case == "outcome_scale_div_1p1" else 1.1 if case == "outcome_scale_x_1p1"
                  else so.tmag_multiplier(context["roster_tmag"][event["planet"]]) if case == "t015v3c" else 1.)
        evaluation.append(scaled_event(event, factor, CASE_RHO.get(case)))
    reuse = set(METHODS) if case in ("baseline", "journal_anchor") else {"M0"} if case in (
        "all_spoc_training", "C2_only", "majority_gate") else set()
    score_values = exact_scores(evaluation, models, reuse, context["baseline_scores"])
    metrics, per_planet, intervals = aggregate(evaluation, score_values, case)
    delta = metrics["M2"]["is95_standardised"] - metrics["M0"]["is95_standardised"]
    baseline_point_error = None
    if case == "baseline":
        baseline_point_error = abs(delta - context["primary_summary"]["primary_delta_M2_M0"])
        interval_error = max(abs(np.array(intervals["M2"]) - context["primary_summary"]["conditional_fixed_parameter_ci95"]))
        if baseline_point_error > 1e-10 or interval_error > 1e-10 or len(evaluation) != 2185:
            raise RuntimeError("Baseline point or conditional interval reproduction failed")
    score_rows = []
    for index, event in enumerate(evaluation):
        for model in METHODS:
            score_rows.append({"case": case, "event_id": event["event_id"], "planet": event["planet"],
                "host": event["host"], "method": model,
                **{metric: float(score_values[model][metric][index]) for metric in METRICS}})
    score_path, ledger_path = SCORES / f"{case}.scores.csv.gz", SCORES / f"{case}.terminal_ledger.csv.gz"
    write_csv(score_path, score_rows)
    write_csv(ledger_path, ledger)
    summary = {
        "case": case, "implementation_date": "2026-11-09", "interpretation": "Declared secondary sensitivity; no new verdict",
        "training_original_accepted_events": len(original_development), "training_accepted_events": len(training),
        "training_planets": len({e["planet"] for e in training}), "training_hosts": len({e["host"] for e in training}),
        "training_removed_accepted_events": len(original_development) - len(training),
        "training_baseline_rejection_counts": context["all_spoc_rejected"] if case == "all_spoc_training" else context["development_rejected"],
        "evaluation_original_intended_events": len(context["manifest"]), "evaluation_eligible_intended_events": len(eligible_ids),
        "evaluation_excluded_intended_events": len(context["manifest"]) - len(eligible_ids),
        "evaluation_accepted_events": len(evaluation), "evaluation_planets": len(per_planet),
        "evaluation_hosts": len({e["host"] for e in evaluation}),
        "terminal_status_counts_original_denominator": dict(Counter(r["status"] for r in ledger)),
        "models": models, "frozen_fit_max_parameter_error": frozen_fit_error,
        "metrics_equal_planet": metrics, "delta_M2_minus_M0_standardised": delta,
        "fraction_planets_improved_M2": float(np.mean([r["delta_M2_minus_M0"] < 0 for r in per_planet])),
        "median_planet_delta_M2": float(np.median([r["delta_M2_minus_M0"] for r in per_planet])),
        "conditional_fixed_scenario_fit_ci95": intervals,
        "interval_scope": "CONDITIONAL ON SCENARIO FIT: paired host bootstrap of fixed development-fitted parameters; not joint inference",
        "conditional_bootstrap_replicates": CONDITIONAL_B, "conditional_bootstrap_seed": CONDITIONAL_SEED,
        "scorer": "Frozen adapter; Gaussian order384 interpolate=False; nonGaussian ad.grid_score order384",
        "reused_original_score_models": sorted(reuse), "baseline_point_reproduction_error": baseline_point_error,
        "scores_path": score_path.relative_to(ROOT).as_posix(), "scores_sha256": sha(score_path),
        "terminal_ledger_path": ledger_path.relative_to(ROOT).as_posix(), "terminal_ledger_sha256": sha(ledger_path),
        "runtime_seconds": round(time.monotonic() - started, 3),
    }
    print(f"{case}: accepted={len(evaluation)}, training={len(training)}, M2-M0={delta:.8g}", flush=True)
    return summary, per_planet


def source_input_hashes(context):
    manifest = json.loads((ROOT / "results/freeze/freeze_manifest.json").read_text())
    paths = {"results/freeze/freeze_manifest.json", "configs/protected_access.json",
             "results/final_primary/evaluation_summary.json", "results/final_primary/scores.csv",
             "results/final_primary/terminal_ledger.csv.gz", "data/derived/final_primary/measured/windows.csv.gz",
             "data/derived/final_primary/measured/products.csv", "data/derived/final_primary/measured/coverage.csv"}
    for entries in manifest["files"].values():
        paths.update(entries)
    paths.update(manifest["likelihood_grids"]["sha256"])
    for row in context["accepted_by_id"].values():
        if row.get("posterior_grid_path"):
            path = Path(row["posterior_grid_path"])
            paths.add((path if path.is_absolute() else ROOT / path).resolve().relative_to(ROOT).as_posix())
    return {path: sha(ROOT / path) for path in sorted(paths)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, choices=range(1, 7), default=6)
    args = parser.parse_args()
    started = time.monotonic()
    fe.era_limit("protected")
    context = prepare()
    inputs = source_input_hashes(context)
    if args.workers == 1:
        init_worker(context)
        results = [run_case(case) for case in CASES]
    else:
        with multiprocessing.get_context("spawn").Pool(args.workers, initializer=init_worker, initargs=(context,)) as pool:
            results = pool.map(run_case, CASES, chunksize=1)
    if source_input_hashes(context) != inputs:
        raise RuntimeError("Frozen sensitivity inputs changed during execution")
    summaries = [result[0] for result in results]
    write_csv(OUT / "per_planet.csv", [row for _, rows in results for row in rows])
    majority_rows = []
    for era, groups in (("development", context["majority_development"]), ("evaluation", context["majority_evaluation"])):
        for (planet, sector, product), counts in sorted(groups.items()):
            majority_rows.append({"era": era, "planet": planet, "sector": sector, "product": product, **counts})
    write_csv(OUT / "majority_products.csv", majority_rows)
    write_json(OUT / "summary.json", {"cases": summaries})
    conventions = {
        "declared_settings": "configs/candidate_freeze.json sensitivities; implementations specified post-unblinding 2026-11-09",
        "calibration_population": "Full DRD core-eligible development population; pp.gated_rows plus pp.core_planets; DRC2022-09-28..2024-01-03. Not an evaluation-roster intersection",
        "covariance_and_outcome_changes": "Applied to development fitting and evaluation; M1-M3 refitted only on development; midtimes and residuals fixed",
        "C2_only": "C3 removed from development and original evaluation intended cohort; original and eligible denominators both retained",
        "all_spoc_training": "Remove development core-eligibility restriction only; assert frozen fits.all_spoc; evaluation unchanged",
        "outcome_scales": "sigma and grid coordinates scaled; grid masses unchanged; M0 denominator recomputed using actual grid variance",
        "t015v3c": "Frozen so.tmag_multiplier; frozen development row Tmag and evaluation frozen roster Tmag; no bias correction",
        "journal_anchor": "Original intended IDs selected by frozen predicted BJD versus numeric UTC JD2026-02-12 plus inherited10min conservative boundary exclusion. Restricted numeric sensitivity, not an exact time-system conversion; models unchanged",
        "journal_anchor_numeric_jd": context["journal_anchor_jd"],
        "majority": "All raw recovered windows, including outside-manifest; denominator timed/edge/integration_unresolved; numerator raw timed without integration flags; strict2*num>den, zero fails; extra gate atop original acceptance on both sides; evaluation original intended denominator retained",
        "evaluation_outside_manifest_windows_in_majority_source": context["outside_manifest_windows"],
        "intervals": "CONDITIONAL ON SCENARIO FIT; B10000 seed20261109; paired whole-host multiplicities and equal-planet aggregation; no scenario joint bootstrap and no new verdict rule",
        "primary": "Frozen primary run and its joint-refit verdict are unchanged",
    }
    write_json(OUT / "conventions.json", conventions)
    receipt = {
        "status": "complete", "implementation_date": "2026-11-09", "created_utc": datetime.now(timezone.utc).isoformat(),
        "command": f"UV_NO_CACHE=1 PYTHONDONTWRITEBYTECODE=1 .venv/bin/python scripts/final_sensitivities.py --workers {args.workers}",
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": sha(Path(__file__)), "input_sha256": inputs,
        "output_sha256": {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "receipt.json"},
        "baseline_training_planets": 206, "baseline_training_events": 2186,
        "baseline_refit_max_error": context["baseline_refit_max_error"],
        "environment": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
        "workers": args.workers, "blas_threads_per_worker": 1,
        "runtime_seconds": round(time.monotonic() - started, 3),
        "limits": ["Conditional secondary intervals hold scenario fits fixed; no joint refit inference or new verdict", "Original acceptance, original midtimes and residuals retained; no remeasurement or protected downloads", "Journal anchor is a restricted numeric comparison with a10min screen, not a qualified BJD/UTC conversion", "No extension sensitivity reanalysis"],
    }
    write_json(OUT / "receipt.json", receipt)
    print(json.dumps({"cases": len(summaries), "runtime_seconds": receipt["runtime_seconds"]}), flush=True)


if __name__ == "__main__":
    main()
