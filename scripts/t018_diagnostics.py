"""Post-review descriptive diagnostics of saved authorised outcomes; no photometry."""

from __future__ import annotations

import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import csv
import gzip
import hashlib
import json
import multiprocessing
import platform
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy
from scipy.special import ndtri

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint1_forecast_core as core
import sprint1_outcome_adapter as adapter

OUT = ROOT / "results/revision_stage0/interpretability"
METHODS = ("M0", "M1", "M2", "M3")
METRICS = ("is95_standardised", "is95_forecast_normalised", "is95_minutes")
LEVELS = (.50, .682689492, .80, .90, .95, .99)
BOOTSTRAP, SEED = 10000, 20261109


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    path = Path(path)
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def planet_values(rows, key):
    by_planet = defaultdict(list)
    hosts = {}
    for row in rows:
        by_planet[row["planet"]].append(float(row[key]))
        if row["planet"] in hosts and hosts[row["planet"]] != row["host"]:
            raise ValueError("Planet has multiple hosts")
        hosts[row["planet"]] = row["host"]
    return [(planet, hosts[planet], float(np.mean(values)))
            for planet, values in sorted(by_planet.items())]


def conditional_summary(planets, bootstrap=BOOTSTRAP, seed=SEED):
    """Resample hosts; average events within planet and planets equally."""
    if not planets:
        return {"point": None, "ci95": None, "planets": 0, "hosts": 0}
    hosts = sorted({host for _, host, _ in planets})
    host_sum = np.zeros(len(hosts))
    host_count = np.zeros(len(hosts))
    index = {host: i for i, host in enumerate(hosts)}
    for _, host, value in planets:
        host_sum[index[host]] += value
        host_count[index[host]] += 1
    rng = np.random.default_rng(seed)
    draws = np.empty(bootstrap)
    for i in range(bootstrap):
        multiplicity = np.bincount(rng.integers(0, len(hosts), len(hosts)), minlength=len(hosts))
        draws[i] = multiplicity @ host_sum / (multiplicity @ host_count)
    return {"point": float(sum(v for _, _, v in planets) / len(planets)),
            "ci95": [float(np.quantile(draws, q)) for q in (.025, .975)],
            "planets": len(planets), "hosts": len(hosts)}


def paired_rows(scores, metric):
    events = defaultdict(dict)
    for row in scores:
        if row["method"] in ("M0", "M2"):
            events[row["event_id"]][row["method"]] = row
    result = []
    for event_id, pair in sorted(events.items()):
        if set(pair) != {"M0", "M2"}:
            raise ValueError("Unpaired score event")
        a, b = pair["M0"], pair["M2"]
        if (a["planet"], a["host"]) != (b["planet"], b["host"]):
            raise ValueError("Score identity mismatch")
        result.append({"event_id": event_id, "planet": a["planet"], "host": a["host"],
                       "delta": float(b[metric]) - float(a[metric])})
    return result


def completion_bounds(ledger, scores, metric):
    """Binary completions at intended-planet weighting, not capture estimates."""
    intended = Counter(row["planet"] for row in ledger)
    by_planet = defaultdict(list)
    for row in scores:
        by_planet[row["planet"]].append(float(row[metric]))
    lower, upper = [], []
    for planet, n in sorted(intended.items()):
        observed = by_planet[planet]
        lower.append(sum(observed) / n)
        upper.append((sum(observed) + n - len(observed)) / n)
    return float(np.mean(lower)), float(np.mean(upper))


def _coverage_events_chunk(outcomes, forecasts):
    forecast = {row["event_id"]: row for row in forecasts}
    output = []
    for row in outcomes:
        fc = forecast[row["event_id"]]
        vf = float(fc["forecast_variance_s2"])
        residual = (float(row["tc_bjd_tdb"]) - float(fc["predicted_bjd_tdb"])) * 86400
        grid = None
        if row["gauss_ok"].lower() not in ("true", "1", "yes"):
            path = Path(row["posterior_grid_path"])
            grid = adapter.likelihood_grid(path if path.is_absolute() else ROOT / path)
        for method in METHODS:
            model = {"b": float(fc[method + "_b"]), "s_log_lambda": float(fc[method + "_s_log_lambda"])}
            probabilities = [value for level in LEVELS for value in ((1 - level) / 2, (1 + level) / 2)]
            if grid is not None:
                quantiles = adapter.grid_quantiles(vf, model, grid, probabilities)
            else:
                sf = model["b"] * np.sqrt(vf)
                sy = float(row["sigma_s"])
                positive = core.mixture_quantiles(np.array([sy / sf]), model["s_log_lambda"],
                                                probs=[(1 + level) / 2 for level in LEVELS], order=384)[0]
                quantiles = [value for bound in positive * sf for value in (-bound, bound)]
            for j, level in enumerate(LEVELS):
                lo, hi = quantiles[2*j:2*j+2]
                output.append({"event_id": row["event_id"], "planet": row["planet"], "host": row["host"],
                               "method": method, "nominal": level, "covered": float(lo <= residual <= hi),
                               "width_minutes": (hi - lo) / 60})
    return output


def _coverage_task(pair):
    return _coverage_events_chunk(*pair)


def coverage_events(outcomes, forecasts):
    forecast = {row["event_id"]: row for row in forecasts}
    tasks = [(outcomes[start:start+20], [forecast[row["event_id"]] for row in outcomes[start:start+20]])
             for start in range(0, len(outcomes), 20)]
    result = []
    with multiprocessing.get_context("spawn").Pool(3) as pool:
        for i, chunk in enumerate(pool.imap(_coverage_task, tasks), 1):
            result.extend(chunk)
            if i % 10 == 0 or i == len(tasks):
                print(f"coverage chunks {i}/{len(tasks)}", flush=True)
    return result


def diagnostics(coverage=True):
    OUT.mkdir(parents=True, exist_ok=True)
    input_hashes = {}
    scale_rows, precision_rows, flow_rows, zero_rows, bound_rows, curve_rows = [], [], [], [], [], []
    detail_rows = []
    s_summary = {}
    for label in ("primary", "extension"):
        directory = ROOT / "results" / ("final_" + label)
        paths = {name: directory / name for name in ("scores.csv", "accepted_outcomes.csv", "accepted_forecasts.csv",
                                                     "terminal_ledger.csv.gz", "joint_draws.json.gz")}
        input_hashes.update({str(p.relative_to(ROOT)): sha(p) for p in paths.values()})
        scores, outcomes, forecasts, ledger = (read_csv(paths[name]) for name in
            ("scores.csv", "accepted_outcomes.csv", "accepted_forecasts.csv", "terminal_ledger.csv.gz"))
        for row in outcomes:
            if row["posterior_grid_path"]:
                p = Path(row["posterior_grid_path"])
                p = p if p.is_absolute() else ROOT / p
                input_hashes[str(p.relative_to(ROOT))] = sha(p)
        for selection in ("all", "without_HR858"):
            selected = [r for r in scores if selection == "all" or r["host"] != "HR858"]
            for metric in METRICS:
                paired = paired_rows(selected, metric)
                summary = conditional_summary(planet_values(paired, "delta"))
                scale_rows.append({"set": label, "selection": selection, "metric": metric,
                                   "accepted_events": len(paired), **{k: v for k, v in summary.items() if k != "ci95"},
                                   "ci95_lower": summary["ci95"][0], "ci95_upper": summary["ci95"][1],
                                   "interval": "conditional fixed-fit paired host bootstrap", "B": BOOTSTRAP, "seed": SEED})
        fc = {r["event_id"]: r for r in forecasts}
        ratios = []
        for row in outcomes:
            ratio = float(row["sigma_s"]) / np.sqrt(float(fc[row["event_id"]]["forecast_variance_s2"]))
            ratios.append(ratio)
            detail_rows.append({"set": label, "event_id": row["event_id"], "planet": row["planet"], "host": row["host"],
                                "sigma_reported_over_forecast_SD": ratio})
        precision_rows.append({"set": label, "weighting": "accepted events equally weighted; descriptive sigma, not grid variance",
                               "events": len(ratios), "q25": float(np.quantile(ratios, .25)),
                               "median": float(np.median(ratios)), "q75": float(np.quantile(ratios, .75))})
        with gzip.open(paths["joint_draws.json.gz"], "rt") as stream:
            stored = json.load(stream)
        sv = np.array([r["models"]["M2"]["s_log_lambda"] for r in stored["draws"]])
        s_summary[label] = {"draws": len(sv), "q025": float(np.quantile(sv, .025)), "median": float(np.median(sv)),
                            "q975": float(np.quantile(sv, .975)), "minimum": float(sv.min()), "maximum": float(sv.max()),
                            "scope": "stored joint-refit calibration parameters, not a posterior predictive mixture"}
        accepted = Counter(r["planet"] for r in outcomes)
        planned = Counter(r["planet"] for r in ledger)
        for status, n in sorted(Counter(r["status"] for r in ledger).items()):
            flow_rows.append({"set": label, "level": "terminal_event", "status": status, "events": n,
                              "planets": len({r["planet"] for r in ledger if r["status"] == status})})
        flow_rows.extend([{"set": label, "level": "population", "status": "intended", "events": len(ledger), "planets": len(planned)},
                          {"set": label, "level": "population", "status": "accepted", "events": len(outcomes), "planets": len(accepted)}])
        for planet in sorted(set(planned) - set(accepted)):
            pl = [r for r in ledger if r["planet"] == planet]
            for status, n in sorted(Counter(r["status"] for r in pl).items()):
                zero_rows.append({"set": label, "planet": planet, "intended_events": len(pl), "status": status, "events": n,
                                  "prediction_covered_events": sum(r["coverage_ok_at_prediction"] == "True" for r in pl),
                                  "product_states": ";".join(sorted({r["product_state"] for r in pl}))})
        for method in METHODS:
            method_scores = [r for r in scores if r["method"] == method]
            for key in ("covered68", "covered95"):
                low, high = completion_bounds(ledger, method_scores, key)
                bound_rows.append({"set": label, "method": method, "metric": key, "intended_planets": len(planned),
                                   "completion_lower": low, "completion_upper": high,
                                   "interpretation": "equal-intended-planet binary completion, NOT latent-time or scheduling capture"})
        if coverage:
            events = coverage_events(outcomes, forecasts)
            for method in METHODS:
                for level in LEVELS:
                    selected = [r for r in events if r["method"] == method and r["nominal"] == level]
                    summary = conditional_summary(planet_values(selected, "covered"))
                    curve_rows.append({"set": label, "method": method, "nominal": level, "measured_time_coverage": summary["point"],
                                       "ci95_lower": summary["ci95"][0], "ci95_upper": summary["ci95"][1],
                                       "planets": summary["planets"], "events": len(selected),
                                       "scope": "fixed-forecast measured-time convolution, conditional on accepted timings"})
            for method in METHODS:
                for key, level in (("covered68", LEVELS[1]), ("covered95", .95)):
                    direct = planet_values([r for r in scores if r["method"] == method], key)
                    saved = float(np.mean([v for _, _, v in direct]))
                    new = next(r["measured_time_coverage"] for r in curve_rows if r["set"] == label and r["method"] == method and r["nominal"] == level)
                    if abs(saved - new) > 1e-12:
                        raise RuntimeError("Additional quantiles do not reproduce saved coverage")
    outputs = {"loss_scales.csv": scale_rows, "precision_ratio.csv": precision_rows,
               "precision_ratio_events.csv": detail_rows, "population_flow.csv": flow_rows,
               "zero_accepted_planets.csv": zero_rows, "binary_completion_bounds.csv": bound_rows}
    if coverage:
        outputs["coverage_vs_nominal.csv"] = curve_rows
    for name, rows in outputs.items():
        write_csv(OUT / name, rows)
    write_json(OUT / "s_distribution.json", s_summary)
    if any(sha(ROOT / p) != h for p, h in input_hashes.items()):
        raise RuntimeError("Input changed during diagnostics")
    receipt = {"kind": "post-review descriptive diagnostics, no primary decision change", "B": BOOTSTRAP, "seed": SEED,
               "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "conditional_intervals": "host resampling holds each fitted forecast fixed; no calibration refitting",
               "nominal_levels": list(LEVELS) if coverage else [],
               "binary_completion_limits": "Unknown intended events receive arbitrary binary coverage labels. These are logical completions only; their measurement models, true transit times and capture remain unknown. No ignorability or event-recovery-times-planet-coverage product is assumed.",
               "raw_photometry_or_headers_opened": False, "input_sha256": input_hashes,
               "script_sha256": sha(__file__),
               "output_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted(OUT.iterdir()) if p.name != "receipt.json" and p.is_file()}}
    write_json(OUT / "receipt.json", receipt)
    print(json.dumps({"outputs": len(outputs) + 2, "input_files_verified": len(input_hashes), "coverage": coverage}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-additional-quantiles", action="store_true")
    args = parser.parse_args()
    diagnostics(not args.skip_additional_quantiles)
