"""Post-unblinding HR858b S105 measurement sensitivity on saved outcomes only."""

from __future__ import annotations

import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import copy
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint1_outcome_adapter as adapter
import t018_benchmark as benchmark
import t018_diagnostics as diagnostics

OUT = ROOT / "results/d073_s105_rescore"
EVENTS = tuple(f"HR858b|S105|DRD{epoch}" for epoch in (645, 647, 649))
SCENARIOS = {"baseline": (False, 1.), "shift_only": (True, 1.),
             "width_only": (False, 2.), "shift_and_width": (True, 2.)}
METRICS = diagnostics.METRICS


def transform_grid(raw, factor):
    if not np.isfinite(factor) or factor <= 0:
        raise ValueError("Width factor must be finite and positive")
    result = copy.deepcopy(raw)
    result["offset_s"] = (np.asarray(raw["offset_s"], dtype=float) * factor).tolist()
    result["log_density"] = (np.asarray(raw["log_density"], dtype=float) - np.log(factor)).tolist()
    if "support_s" in raw:
        result["support_s"] = (np.asarray(raw["support_s"], dtype=float) * factor).tolist()
    return result


def transform_outcome(row, shift_s, factor, grid_path=None):
    if not np.isfinite(shift_s) or not np.isfinite(factor) or factor <= 0:
        raise ValueError("Invalid timing transformation")
    result = row.copy()
    result["tc_bjd_tdb"] = repr(float(row["tc_bjd_tdb"]) + shift_s / 86400)
    for key in ("sigma_s", "q025_s", "q1587_s", "q8413_s", "q975_s"):
        result[key] = repr(float(row[key]) * factor)
    if grid_path is not None:
        result["posterior_grid_path"] = str(grid_path)
    return result


def consensus_times(rows, c050, t017):
    result = {}
    period = 3.585287
    for row in rows:
        tc = float(row["tc_bjd_tdb"])
        estimates = {}
        for flux in ("PDCSAP_FLUX", "SAP_FLUX"):
            hits = [p for p in c050["comparison_with_frozen"][flux]["pairs"]
                    if abs(float(p["frozen_tc"]) - tc) < 1e-8]
            if len(hits) != 1:
                raise ValueError("C050 event is not uniquely paired")
            estimates["C050_" + flux] = float(hits[0]["independent_tc"])
            hits = [p for p in t017["fluxes"][flux]["transits"]
                    if p["status"] == "timed" and abs(p["tc_bjd_tdb"] - tc) < period / 4]
            if len(hits) != 1:
                raise ValueError("T017 event is not uniquely paired")
            estimates["T017_" + flux] = float(hits[0]["tc_bjd_tdb"])
        centre = float(np.median(list(estimates.values())))
        result[row["event_id"]] = {"frozen_tc_bjd_tdb": tc, "consensus_tc_bjd_tdb": centre,
                                   "shift_s": (centre - tc) * 86400,
                                   "route_tc_bjd_tdb": estimates,
                                   "route_difference_min": {k: (v - tc) * 1440 for k, v in estimates.items()}}
    if len({v["consensus_tc_bjd_tdb"] for v in result.values()}) != len(rows):
        raise ValueError("Consensus events are not one-to-one")
    return result


def merge_scores(saved, changes):
    expected = {(r["event_id"], r["method"]): r for r in saved}
    updated = {(r["event_id"], r["method"]): r for r in changes}
    identities = {(event, method) for event in EVENTS for method in diagnostics.METHODS}
    if len(updated) != len(changes) or set(updated) != identities or not identities <= set(expected):
        raise ValueError("Changed score identity set differs")
    result = []
    for row in saved:
        identity = row["event_id"], row["method"]
        if identity in updated:
            change = updated[identity].copy()
            change["weight"] = row["weight"]
            result.append(change)
        else:
            result.append(row.copy())
    if any(a != b for a, b in zip(saved, result) if a["event_id"] not in EVENTS):
        raise RuntimeError("An unaffected score row changed")
    return result


def summaries(scores, label):
    report = []
    for scope, scoped in (("primary", scores), ("HR858b", [r for r in scores if r["planet"] == "HR858b"])):
        for metric in METRICS:
            for method in diagnostics.METHODS:
                rows = [r for r in scoped if r["method"] == method]
                planets = diagnostics.planet_values(rows, metric)
                report.append({"scenario": label, "scope": scope, "metric": metric, "method": method,
                               "point": float(np.mean([v for _, _, v in planets])), "ci95_lower": "", "ci95_upper": ""})
            planets = diagnostics.planet_values(diagnostics.paired_rows(scoped, metric), "delta")
            if scope == "primary":
                summary = diagnostics.conditional_summary(planets)
            else:
                summary = {"point": float(np.mean([v for _, _, v in planets])), "ci95": ("", "")}
            report.append({"scenario": label, "scope": scope, "metric": metric, "method": "M2_minus_M0",
                           "point": summary["point"], "ci95_lower": summary["ci95"][0], "ci95_upper": summary["ci95"][1]})
    return report


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / ".gitignore").write_text("working/\n")
    work = OUT / "working"
    work.mkdir(exist_ok=True)
    outcomes_path = ROOT / "results/final_primary/accepted_outcomes.csv"
    forecasts_path = ROOT / "results/final_primary/accepted_forecasts.csv"
    scores_path = ROOT / "results/final_primary/scores.csv"
    c050_path = ROOT / "results/independent_validation/hr858/summary.json"
    t017_path = ROOT / "results/independent_validation/t017/HR858b_S105.json"
    outcomes, forecasts, saved = map(diagnostics.read_csv, (outcomes_path, forecasts_path, scores_path))
    selected = [r for r in outcomes if r["event_id"] in EVENTS]
    if len(selected) != 3 or any(r["gauss_ok"].lower() != "false" for r in selected):
        raise ValueError("Expected exactly three saved non-Gaussian outcomes")
    sources = [Path(__file__), ROOT / "docs/d073_s105_rescore.md", outcomes_path, forecasts_path, scores_path,
               c050_path, t017_path, Path(adapter.__file__), Path(adapter.c.__file__), Path(adapter.f.__file__),
               Path(diagnostics.__file__), Path(benchmark.__file__)]
    sources += [ROOT / r["posterior_grid_path"] for r in selected]
    before = {str(p.relative_to(ROOT)): diagnostics.sha(p) for p in sources}
    consensus = consensus_times(selected, json.loads(c050_path.read_text()), json.loads(t017_path.read_text()))
    diagnostics.write_json(OUT / "consensus.json", consensus)
    subset_forecast = work / "forecasts.csv"
    diagnostics.write_csv(subset_forecast, [r for r in forecasts if r["event_id"] in EVENTS])
    summary_rows, coverage, baselines, generated = [], [], {}, []
    for label, (shift, factor) in SCENARIOS.items():
        directory = work / label
        directory.mkdir(exist_ok=True)
        altered = []
        for row in selected:
            if label == "baseline":
                altered.append(row.copy())
                continue
            grid_path = directory / (row["event_id"].split("|")[-1] + ".json")
            raw = json.loads((ROOT / row["posterior_grid_path"]).read_text())
            transformed = transform_grid(raw, factor)
            diagnostics.write_json(grid_path, transformed)
            original_x, original_mass = adapter.likelihood_grid(ROOT / row["posterior_grid_path"])
            new_x, new_mass = adapter.likelihood_grid(grid_path)
            if not np.allclose(new_mass, original_mass, rtol=0, atol=1e-15) or not np.array_equal(new_x, original_x * factor):
                raise RuntimeError("Grid transformation failed mass preservation")
            altered.append(transform_outcome(row, consensus[row["event_id"]]["shift_s"] if shift else 0.,
                                             factor, grid_path.relative_to(ROOT)))
            generated.append(grid_path)
        output = directory / "scores.csv"
        outcome_path = directory / "outcomes.csv"
        diagnostics.write_csv(outcome_path, altered)
        adapter.score_outcomes(argparse.Namespace(forecasts=str(subset_forecast), outcomes=str(outcome_path),
            output=str(output), outcome_scale=1., error_convention="t015v3_beta_chi", max_tc_bjd=None))
        merged = merge_scores(saved, diagnostics.read_csv(output))
        if label == "baseline":
            baseline_rows = [r for r in merged if r["event_id"] in EVENTS]
            expected_rows = [r for r in saved if r["event_id"] in EVENTS]
            baselines = benchmark.compare_scores(expected_rows, baseline_rows)
            merged = saved
        diagnostics.write_csv(directory / "full_scores.csv", merged)
        full_outcomes = [next(a for a in altered if a["event_id"] == r["event_id"]) if r["event_id"] in EVENTS else r
                         for r in outcomes]
        if any(a != b for a, b in zip(outcomes, full_outcomes) if a["event_id"] not in EVENTS):
            raise RuntimeError("An unaffected outcome changed")
        summary_rows.extend(summaries(merged, label))
        for method in diagnostics.METHODS:
            hr = [r for r in merged if r["planet"] == "HR858b" and r["method"] == method]
            coverage.append({"scenario": label, "method": method, "HR858b_events": len(hr),
                             "HR858b_covered95": sum(int(float(r["covered95"])) for r in hr)})
        generated.extend((output, outcome_path, directory / "full_scores.csv"))
    if any(diagnostics.sha(ROOT / p) != value for p, value in before.items()):
        raise RuntimeError("A source or frozen input changed")
    diagnostics.write_csv(OUT / "summary.csv", summary_rows)
    diagnostics.write_csv(OUT / "coverage.csv", coverage)
    receipt = {"kind": "post-unblinding measurement sensitivity; frozen outcomes unchanged",
               "changed_events": EVENTS, "scenarios": SCENARIOS,
               "source_sha256": before, "source_inputs_unchanged": True,
               "baseline_maximum_absolute_metric_error": baselines,
               "unaffected_outcomes_unchanged": len(outcomes) - 3,
               "unaffected_score_rows_unchanged": len(saved) - 12,
               "conditional_host_bootstrap": {"draws": diagnostics.BOOTSTRAP, "seed": diagnostics.SEED,
                                                "models_refitted": False, "primary_interval_replaced": False},
               "generated_working_sha256": {str(p.relative_to(OUT)): diagnostics.sha(p) for p in generated},
               "output_sha256": {p.name: diagnostics.sha(p) for p in (OUT / "summary.csv", OUT / "coverage.csv", OUT / "consensus.json")},
               "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
               "raw_photometry_or_headers_opened": False, "network_requests": False}
    diagnostics.write_json(OUT / "receipt.json", receipt)
    print(json.dumps({"baseline_max_error": max(baselines.values()), "changed_events": len(EVENTS), "coverage": coverage}))


if __name__ == "__main__":
    main()
