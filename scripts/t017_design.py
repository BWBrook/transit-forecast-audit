"""Select T017 cases from saved tables before any independent light-curve fit."""

import csv
import argparse
import gzip
import hashlib
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import final_evaluation as final
import forecast_variance_components as fvc
from reproduce_table5 import load

OUT = ROOT / "results/independent_validation/t017"
DESIGN = ROOT / "configs/independent_validation/t017_design.json"
SEED = 2026110917


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as handle:
        return list(csv.DictReader(handle))


def m2_fit(data, weights):
    def objective(theta):
        value, gradient = fvc.objective([0., theta[0]], data, True, 384,
                                         np.zeros(len(weights)), weights)
        return value, gradient[1:]
    trials = [minimize(objective, [np.log(start)], jac=True, method="L-BFGS-B",
                       bounds=[(-12, np.log(fvc.S_MAX))],
                       options={"ftol": 1e-11, "gtol": 1e-6, "maxiter": 1000})
              for start in (.3, 1., 3., 4.)]
    valid = [trial for trial in trials if trial.success and np.isfinite(trial.fun)]
    if not valid:
        raise RuntimeError("No converged leave-one-out M2 fit")
    best = min(valid, key=lambda trial: trial.fun)
    return float(np.exp(best.x[0]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reuse-ranking", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    planets = final.calibration_planets()
    ranking_path = OUT / "calibration_loo_ranking.json"
    if args.reuse_ranking:
        rank = json.loads(ranking_path.read_text())
        assert {row["planet"] for row in rank} == {p["planet"] for p in planets}
        baseline = rank[0]["s_full"]
        frozen = json.loads((ROOT / "results/prefreeze/candidate_models_core_matched.json").read_text())
        assert abs(baseline - frozen["models"]["M2"]["s_log_lambda"]) < 1e-6
    else:
        data = fvc.packed(fvc.precompute(planets, [p["m"] for p in planets]))
        weights = np.ones(len(planets))
        baseline = m2_fit(data, weights)
        rank = []
        for index, planet in enumerate(planets):
            weights[index] = 0
            value = m2_fit(data, weights)
            weights[index] = 1
            rank.append({"planet": planet["planet"], "host": planet["host"],
                         "s_without": value, "s_full": baseline,
                         "absolute_change": abs(value - baseline)})
        rank.sort(key=lambda row: (-row["absolute_change"], row["planet"]))
        ranking_path.write_text(json.dumps(rank, indent=2) + "\n")
    eph, _, _ = load()
    primary = read(ROOT / "results/final_primary/accepted_outcomes.csv")
    development = read(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    prod_primary = read(ROOT / "data/derived/final_primary/measured/products.csv")
    prod_development = read(ROOT / "results/outcomes/t015v3/product_identification.csv")
    ledger = read(ROOT / "results/final_primary/terminal_ledger.csv.gz")
    influential = ["HR858b", "TOI-905b", "WASP-184b", "TOI-559b"]
    controls = random.Random(SEED).sample(sorted({r["planet"] for r in primary} - set(influential)), 10)
    zero = sorted({r["planet"] for r in ledger} - {r["planet"] for r in primary})
    counts = Counter((r["planet"], str(r["sector"])) for r in primary)
    counts.update((r["planet"], str(r["sector"])) for r in development if r.get("status") == "timed")
    selections = []
    def select(name, category, all_products=False):
        source = prod_development if category == "calibration_influence" else prod_primary
        products = [r for r in source if r["planet"] == name and r["product"] == "SPOC_120"
                    and (46 <= int(r["sector"]) <= 73 or int(r["sector"]) >= 98)]
        products.sort(key=lambda r: (-counts[name, str(r["sector"])], int(r["sector"]), r["uri"]))
        if not all_products:
            products = products[:1]
        selections.append({"planet": name, "category": category,
                           "period_hint_d": eph["DRD"][name].period_days,
                           "products": [{"sector": int(r["sector"]), "tic": r["tic"],
                              "relative_fits_path": str(Path("data/raw/mast") / ("TIC_" + r["tic"].split()[-1]) / r["uri"].split("/")[-1]),
                              "expected_sha256": r.get("file_sha256", ""), "original_status": r["status"]}
                              for r in products]})
    for name in influential:
        select(name, "evaluation_influence", all_products=True)
    for row in rank[:5]:
        select(row["planet"], "calibration_influence")
    for name in controls:
        select(name, "seeded_control")
    for name in zero:
        select(name, "zero_accepted")
    failed_classes = sorted({r["status"] for r in ledger
                             if r["status"] not in ("accepted", "no_cadence_coverage_at_prediction")})
    for status in failed_classes:
        candidates = sorted({(r["planet"], int(r["sector"])) for r in ledger
                             if r["status"] == status})
        existing = {(s["planet"], p["sector"]) for s in selections for p in s["products"]}
        candidate = next(((name, sector) for name, sector in candidates if (name, sector) not in existing), None)
        if candidate:
            name, sector = candidate
            select(name, "covered_failure_" + status)
            selections[-1]["products"] = [p for p in selections[-1]["products"] if p["sector"] == sector] or [
                {"sector": sector, "tic": r["tic"],
                 "relative_fits_path": str(Path("data/raw/mast") / ("TIC_" + r["tic"].split()[-1]) / r["uri"].split("/")[-1]),
                 "expected_sha256": r.get("file_sha256", ""), "original_status": r["status"]}
                for r in prod_primary if r["planet"] == name and int(r["sector"]) == sector]
    design = {
        "task": "T017", "status": "pre-fit sample; requires parent review and commit before raw access",
        "seed": SEED, "calibration_planets": len(planets), "baseline_s": baseline,
        "cases": selections, "raw_products_opened_by_this_design": False,
        "forbidden_sectors": [74, 97], "download_allowed": False,
        "selection": "All products for four evaluation gain hosts; top five development-only absolute leave-one-out s changes; ten seeded accepted controls excluding four leaders; one maximum-saved-timing product per ordinary/calibration/zero-accepted case; one lexical unrepresented product per covered-failure class.",
        "method": "Independent broad-phase BoxLeastSquares identification, empirical symmetric trapezoid fit and per-window local linear baseline/depth profiling; no issued epoch used to find or fit transits; report SAP and PDCSAP separately. The use of the shared standard Astropy BLS library is disclosed; no pipeline extraction/fitting code is imported.",
        "method_settings": {"blind_period_range_d": [0.3, 15.0], "period_grid_size": 20000,
                            "durations_d": [0.03, 0.05, 0.08, 0.12, 0.18, 0.24],
                            "maximum_sequential_signals": 3, "minimum_bls_snr": 5,
                            "target_period_tolerance_fraction": 0.05,
                            "detrend_bin_width_d": 0.5, "continuum_quantile": 0.8,
                            "fit_window_duration_multiplier": 2.5,
                            "maximum_local_half_window_fraction_period": 0.45,
                            "minimum_points_each_outside_side": 8,
                            "timing_profile_step_s": 15,
                            "joint_nuisance_check": "Every influential event marked non-Gaussian by the frozen run; free depth/duration/ingress plus local baseline with empirical trapezoid shape."},
        "discrepancy_triggers": {
            "product_review": "Median absolute timing difference >max(3 minutes, 0.5 median frozen sigma), any event difference >max(10 minutes, 3 frozen sigma), >10% of accepted frozen windows unmatched, or alias/companion ambiguity.",
            "shape_review": "For influential non-Gaussian events, compare fixed shape with a joint local depth/duration/ingress fit. A shift >max(3 minutes, 0.5 frozen sigma) requires explicit shape-driven discrepancy review.",
            "wider_remeasurement": "Any influential product with a coherent discrepant train or at least two large event discrepancies, or at least two seeded controls passing the product-review trigger, warrants a separately agreed broader measurement tranche. Complete/report this fixed sample first; no automatic enlargement or frozen replacement.",
            "interpretation": "These are diagnostic triggers on shared photons, not calibrated significance tests. Non-detection/ambiguity is not an ephemeris miss. Trapezoid model differences and lack of pixels remain limits."
        },
        "source_sha256": {str(path.relative_to(ROOT)): hashlib.sha256(path.read_bytes()).hexdigest()
                          for path in [ROOT / "results/final_primary/accepted_outcomes.csv", ROOT / "results/outcomes/t015v3/outcomes.csv.gz", ROOT / "results/prefreeze/candidate_parameters.json"]},
    }
    DESIGN.parent.mkdir(parents=True, exist_ok=True)
    DESIGN.write_text(json.dumps(design, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"cases": len(selections), "products": sum(len(s["products"]) for s in selections),
                      "calibration_top5": [r["planet"] for r in rank[:5]], "controls": controls, "zero_accepted": zero}))


if __name__ == "__main__":
    main()
