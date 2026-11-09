"""Compare already fitted T017 outputs with saved timings, after extraction."""

import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/independent_validation/t017"


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as handle:
        return list(csv.DictReader(handle))


def assignments(reference, independent, period):
    if not reference or not independent:
        return []
    distance = np.abs(np.array([float(r["tc_bjd_tdb"]) for r in reference])[:, None]
                      - np.array([r["tc_bjd_tdb"] for r in independent])[None, :])
    gate = period / 4
    if not np.isfinite(gate) or gate <= 0:
        raise ValueError("Pairing period must be finite and positive")
    admissible = distance < gate
    # Losing one admissible pair must outweigh every possible within-gate cost.
    cost = np.where(admissible, distance / gate, min(distance.shape) + 1)
    a, b = linear_sum_assignment(cost)
    return [(int(i), int(j)) for i, j in zip(a, b) if admissible[i, j]]


def main():
    design = json.loads((ROOT / "configs/independent_validation/t017_design.json").read_text())
    primary = read(ROOT / "results/final_primary/accepted_outcomes.csv")
    primary_ledger = read(ROOT / "results/final_primary/terminal_ledger.csv.gz")
    development = read(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    dev_ledger = read(ROOT / "results/prefreeze/attempt_ledger_development.csv.gz")
    dev_accepted = {r["window_event_id"] for r in dev_ledger if r["status"] == "accepted"}
    development = [r for r in development if r["event_id"] in dev_accepted]
    references = defaultdict(list)
    for row in primary + development:
        references[row["planet"], int(row["sector"])].append(row)
    categories = defaultdict(list)
    for case in design["cases"]:
        for product in case["products"]:
            categories[case["planet"], product["sector"]].append(case["category"])
    period_hints = {case["planet"]: case["period_hint_d"] for case in design["cases"]}
    summaries, pairs, unknown, candidates = [], [], [], []
    for key, cats in sorted(categories.items()):
        planet, sector = key
        path = OUT / f"{planet}_S{sector}.json"
        result = json.loads(path.read_text())
        for column in ("PDCSAP_FLUX", "SAP_FLUX"):
            flux = result.get("fluxes", {}).get(column, {})
            ref = references[key]
            timed = [r for r in flux.get("transits", []) if r.get("status") == "timed"]
            intended = [r for r in primary_ledger if r["planet"] == planet and int(r["sector"]) == sector]
            if not ref or any(category.startswith("covered_failure_") for category in cats):
                for measured in timed:
                    nearest = min(intended, key=lambda r: abs(float(r["drd_predicted_bjd_tdb"]) - measured["tc_bjd_tdb"])) if intended else None
                    offset = (measured["tc_bjd_tdb"] - float(nearest["drd_predicted_bjd_tdb"])) * 1440 if nearest else None
                    within = nearest is not None and abs(offset) < period_hints[planet] * 360
                    candidates.append({"planet": planet, "sector": sector, "flux": column,
                                       "independent_tc_bjd_tdb": measured["tc_bjd_tdb"],
                                       "conditional_sigma_min": measured["sigma_min"],
                                       "weak_profile": measured["weak_profile"], "profile_edge": measured["profile_edge"],
                                       "nearest_intended_event_id": nearest["event_id"] if within else None,
                                       "original_terminal_status": nearest["status"] if within else "cycle_unresolved",
                                       "prediction_coverage_qualified": nearest["coverage_ok_at_prediction"] if within else None,
                                       "candidate_minus_prediction_min": offset,
                                       "cycle_basis": "Nearest declared prediction within P/4, after blind fitting only; identity not independently established."})
            matches = assignments(ref, timed, period_hints[planet])
            sigma = np.array([float(r["sigma_s"]) / 60 for r in ref])
            diffs, large_count, joint_count, joint_max = [], 0, 0, 0.
            for i, j in matches:
                old, new = ref[i], timed[j]
                diff = (new["tc_bjd_tdb"] - float(old["tc_bjd_tdb"])) * 1440
                frozen_sigma = float(old["sigma_s"]) / 60
                large = abs(diff) > max(10., 3 * frozen_sigma)
                diffs.append(diff)
                large_count += int(large)
                joint = new.get("joint_nuisance")
                joint_shift = None
                if joint and joint.get("status") == "joint_fit":
                    joint_shift = (joint["tc_btjd"] - new["tc_btjd"]) * 1440
                    joint_max = max(joint_max, abs(joint_shift))
                    joint_count += int(abs(joint_shift) > max(3., .5 * frozen_sigma))
                pairs.append({"planet": planet, "sector": sector, "categories": ";".join(cats),
                              "flux": column, "reference_event_id": old["event_id"],
                              "frozen_tc_bjd_tdb": old["tc_bjd_tdb"],
                              "independent_tc_bjd_tdb": new["tc_bjd_tdb"],
                              "difference_min": diff, "frozen_sigma_min": frozen_sigma,
                              "independent_conditional_sigma_min": new["sigma_min"],
                              "weak_profile": new["weak_profile"], "profile_edge": new["profile_edge"],
                              "large_discrepancy_trigger": large,
                              "joint_shape_shift_min": joint_shift})
            median_abs = float(np.median(np.abs(diffs))) if diffs else None
            median_sigma = float(np.median(sigma)) if len(sigma) else None
            unmatched_fraction = (len(ref) - len(matches)) / len(ref) if ref else None
            triggers = {
                "median_shift": bool(median_abs is not None and median_abs > max(3., .5 * median_sigma)),
                "large_event": bool(large_count),
                "unmatched": bool(unmatched_fraction is not None and unmatched_fraction > .1),
                "phase_ambiguity": bool(flux.get("phase_ambiguity", False)),
                "shape_shift": bool(joint_count),
            }
            summaries.append({"planet": planet, "sector": sector, "categories": cats, "flux": column,
                              "status": flux.get("status", result["status"]), "reference_timings": len(ref),
                              "independent_timed_windows": len(timed), "matched": len(matches),
                              "median_difference_min": float(np.median(diffs)) if diffs else None,
                              "median_absolute_difference_min": median_abs,
                              "maximum_absolute_difference_min": float(np.max(np.abs(diffs))) if diffs else None,
                              "median_frozen_sigma_min": median_sigma,
                              "unmatched_fraction": unmatched_fraction,
                              "weak_profiles": sum(r["weak_profile"] for r in timed),
                              "profile_edges": sum(r["profile_edge"] for r in timed),
                              "large_discrepancies": large_count,
                              "joint_shape_review_events": joint_count, "maximum_joint_shape_shift_min": joint_max,
                              "review_triggers": triggers, "review_required": any(triggers.values()),
                              "independent_status_counts": dict(Counter(r["status"] for r in flux.get("transits", [])))})
            if not ref:
                unknown.append({"planet": planet, "sector": sector, "flux": column,
                                "status": flux.get("status", result["status"]),
                                "independent_candidate_times_bjd_tdb": [r["tc_bjd_tdb"] for r in timed],
                                "informative_nonedge_candidates": sum(not r["weak_profile"] and not r["profile_edge"] for r in timed),
                                "interpretation": "Independent light-curve candidates; no prior accepted timing is not itself a forecast miss."})
    control_triggers = sorted({r["planet"] for r in summaries
                               if "seeded_control" in r["categories"] and r["review_required"]})
    influential_large = sorted({r["planet"] for r in summaries
                               if "evaluation_influence" in r["categories"] and r["large_discrepancies"] >= 2})
    report = {"descriptive_shared_photon_comparison": True, "products": len(categories),
              "products_with_primary_reference": sum(bool(references[k]) for k in categories),
              "summary_rows": summaries, "no_reference_cases": unknown,
              "seeded_control_planets_requiring_review": control_triggers,
              "influential_planets_with_at_least_two_large_discrepancies": influential_large,
              "wider_tranche_trigger_from_counts": len(control_triggers) >= 2 or bool(influential_large),
              "wider_tranche_note": "Diagnostic trigger only. First inspect weak/gapped/model-mismatch cases; no frozen correction or automatic expansion.",
              "limits": ["Shared photons: differences and reported sigma summaries are not independent sampling tests.",
                         "After phase-blind extraction, one-to-one pairing maximizes the number strictly within P/4, then minimizes their total distance; it never finds/fixes a timing.",
                         "Empirical trapezoid/profile uncertainty differs from the frozen physical model; disagreements require adjudication."]}
    (OUT / "comparison_summary.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    with (OUT / "timing_comparison.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(pairs[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(pairs)
    with (OUT / "unscored_candidates.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(candidates[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(candidates)
    source_paths = [ROOT / "results/final_primary/accepted_outcomes.csv",
                    ROOT / "results/final_primary/terminal_ledger.csv.gz",
                    ROOT / "results/outcomes/t015v3/outcomes.csv.gz",
                    ROOT / "results/prefreeze/attempt_ledger_development.csv.gz",
                    OUT / "measurement_receipt.json"]
    receipt = {"comparison_only_after_blind_fitting": True,
               "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in source_paths},
               "output_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in [OUT / "comparison_summary.json", OUT / "timing_comparison.csv", OUT / "unscored_candidates.csv"]}}
    (OUT / "comparison_receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"products": len(categories), "matched_pairs": len(pairs),
                      "controls_requiring_review": control_triggers,
                      "influential_large_discrepancies": influential_large,
                      "wider_tranche_trigger": report["wider_tranche_trigger_from_counts"]}))


if __name__ == "__main__":
    main()
