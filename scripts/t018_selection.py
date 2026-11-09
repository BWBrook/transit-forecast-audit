"""Additional selection/weighting tables and labelled interpretation examples."""

import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import scipy

import t018_diagnostics as d

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/revision_stage0/selection"


def weighted_quantile(values, weights, probability):
    values, weights = np.asarray(values), np.asarray(weights)
    if np.any(weights < 0) or weights.sum() <= 0:
        raise ValueError("Invalid quantile weights")
    order = np.argsort(values, kind="stable")
    index = np.searchsorted(np.cumsum(weights[order]) / weights.sum(), probability, side="left")
    return float(values[order[min(index, len(values)-1)]])


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cross, planets, precision, gains = [], [], [], []
    hashes = {}
    for label in ("primary", "extension"):
        directory = ROOT / ("results/final_" + label)
        paths = [directory / name for name in ("terminal_ledger.csv.gz", "accepted_outcomes.csv", "accepted_forecasts.csv", "scores.csv")]
        hashes.update({str(p.relative_to(ROOT)): d.sha(p) for p in paths})
        ledger, outcomes, forecasts, scores = [d.read_csv(p) for p in paths]
        for metric in ("covered68", "covered95"):
            paired = d.paired_rows(scores, metric)
            summary = d.conditional_summary(d.planet_values(paired, "delta"))
            gains.append({"set": label, "metric": metric, "M2_minus_M0": summary["point"],
                          "ci95_lower": summary["ci95"][0], "ci95_upper": summary["ci95"][1],
                          "scope": "paired fixed-fit measured-time coverage, conditional on accepted timings"})
        for state in ("True", "False", ""):
            selected = [r for r in ledger if r["coverage_ok_at_prediction"] == state]
            for accepted in (True, False):
                part = [r for r in selected if (r["status"] == "accepted") == accepted]
                cross.append({"set": label, "prediction_coverage": state or "unknown", "accepted": accepted,
                              "events": len(part), "planets": len({r["planet"] for r in part})})
        for planet in sorted({r["planet"] for r in ledger}):
            part = [r for r in ledger if r["planet"] == planet]
            counts = Counter(r["status"] for r in part)
            planets.append({"set": label, "planet": planet, "host": part[0]["host"], "intended_events": len(part),
                            "accepted_events": counts["accepted"], "recovery_fraction": counts["accepted"] / len(part),
                            "prediction_coverage_qualified": sum(r["coverage_ok_at_prediction"] == "True" for r in part),
                            "terminal_counts_json": json.dumps(dict(sorted(counts.items())), separators=(",", ":"))})
        fc = {r["event_id"]: r for r in forecasts}
        n = Counter(r["planet"] for r in outcomes)
        ratios = np.array([float(r["sigma_s"]) / np.sqrt(float(fc[r["event_id"]]["forecast_variance_s2"])) for r in outcomes])
        weights = np.array([1 / len(n) / n[r["planet"]] for r in outcomes])
        precision.append({"set": label, "weighting": "equal accepted planet, events equally within planet",
                          "quantile_convention": "weighted empirical inverse CDF",
                          "q25": weighted_quantile(ratios, weights, .25),
                          "median": weighted_quantile(ratios, weights, .5),
                          "q75": weighted_quantile(ratios, weights, .75),
                          "scope": "reported timing sigma convention / forecast SD, not full non-Gaussian variance"})
    d.write_csv(OUT / "prediction_coverage_cross_table.csv", cross)
    d.write_csv(OUT / "per_planet_recovery.csv", planets)
    d.write_csv(OUT / "planet_balanced_precision_ratio.csv", precision)
    d.write_csv(OUT / "coverage_gain_saved_levels.csv", gains)
    example = {"label": "synthetic numerical counterexamples, not photometry qualification",
               "selection": {"planet_a": {"intended": 100, "accepted": 1, "covered_accepted": 1},
                             "planet_b": {"intended": 1, "accepted": 1, "covered_accepted": 0},
                             "equal_planet_binary_completion_bounds": [.005, .5],
                             "event_recovery_times_accepted_planet_coverage": (2/101)*.5,
                             "why_invalid": "Event and planet denominators differ; product is not intended-planet coverage."},
               "capture": {"forecast_sd": 1., "measurement_sd": 3., "true_time": 3., "measured_time": 4.,
                           "latent_95_limits": [-1.95996398454, 1.95996398454],
                           "convolved_measured_95_limits": [-1.95996398454*np.sqrt(10), 1.95996398454*np.sqrt(10)],
                           "measured_interval_covers_Y": True, "latent_schedule_captures_T": False,
                           "why_distinct": "Later measurement error is used for verification, not scheduling padding."}}
    d.write_json(OUT / "synthetic_interpretation_examples.json", example)
    if any(d.sha(ROOT / path) != digest for path, digest in hashes.items()):
        raise RuntimeError("Selection inputs changed")
    d.write_json(OUT / "receipt.json", {"input_sha256": hashes, "script_sha256": d.sha(__file__),
        "runtime": {"numpy": np.__version__, "scipy": scipy.__version__},
        "raw_photometry_or_headers_opened": False,
        "output_sha256": {str(p.relative_to(ROOT)): d.sha(p) for p in sorted(OUT.iterdir()) if p.name != "receipt.json"}})
    print(json.dumps({"planet_rows": len(planets), "cross_table_rows": len(cross)}))


if __name__ == "__main__":
    main()
