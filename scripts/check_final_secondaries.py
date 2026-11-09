"""Independent aggregation and conditional-bootstrap checks for declared secondaries."""

import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def rows(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return list(csv.DictReader(fh))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    base = ROOT / "results/final_secondaries"
    for folder, filename, ikey, okey in (("sensitivities", "receipt.json", "input_sha256", "output_sha256"),
                                         ("descriptive", "receipt.json", "inputs_sha256", "outputs_sha256")):
        rec = json.loads((base / folder / filename).read_text())
        for rel, value in rec[ikey].items():
            assert digest(ROOT / rel) == value, rel
        for rel, value in rec[okey].items():
            path = ROOT / rel if (ROOT / rel).exists() else base / folder / rel
            assert digest(path) == value, rel
    cases = json.loads((base / "sensitivities/summary.json").read_text())["cases"]
    outcomes = {r["event_id"]: r for r in rows(ROOT / "results/final_primary/accepted_outcomes.csv")}
    forecasts = {r["event_id"]: r for r in rows(ROOT / "results/final_primary/accepted_forecasts.csv")}
    tmag = {r["planet"]: float(r["tmag"]) for r in rows(ROOT / "results/sprint2/freeze_candidate/roster.csv")}
    gaussian_checks, gaussian_error, gaussian_standardised_error = 0, 0., 0.
    result = {}
    for case in cases:
        data = rows(ROOT / case["scores_path"])
        assert digest(ROOT / case["scores_path"]) == case["scores_sha256"]
        assert digest(ROOT / case["terminal_ledger_path"]) == case["terminal_ledger_sha256"]
        for r in data:
            out = outcomes[r["event_id"]]
            if r["method"] != "M0" or out["gauss_ok"].lower() not in ("true", "1", "yes"):
                continue
            fc = forecasts[r["event_id"]]
            factor = 1 / 1.1 if case["case"] == "outcome_scale_div_1p1" else 1.1 if case["case"] == "outcome_scale_x_1p1" else 1.
            if case["case"] == "t015v3c":
                x = min(max(tmag[out["planet"]], 8.), 13.5) - 11.
                factor = math.sqrt(max(.88566859 - .09191112 * x, .25))
            vf = float(fc["forecast_variance_s2"])
            if case["case"] in ("rho_zero", "rho_minus1", "rho_plus1"):
                rho = {"rho_zero": 0., "rho_minus1": -1., "rho_plus1": 1.}[case["case"]]
                st0, sp, n = [float(fc[k]) for k in ("sigma_t0_s", "sigma_p_s", "forecast_epoch")]
                vf = (st0 + rho * sp * n) ** 2 + (1 - rho * rho) * (sp * n) ** 2
            variance = vf + (float(out["sigma_s"]) * factor) ** 2
            sd = math.sqrt(variance)
            y = (float(out["tc_bjd_tdb"]) - float(fc["predicted_bjd_tdb"])) * 86400
            q95 = NormalDist().inv_cdf(.975) * sd
            interval_score = 2 * q95 + 40 * max(abs(y) - q95, 0.)
            expected = {"is95_standardised": interval_score / sd, "is95_minutes": interval_score / 60,
                        "is95_forecast_normalised": interval_score / math.sqrt(vf),
                        "negative_log_score_seconds": .5 * (math.log(2 * math.pi * variance) + y * y / variance),
                        "width95_minutes": 2 * q95 / 60, "m0_predictive_sd_s": sd}
            gaussian_error = max(gaussian_error, *(abs(float(r[k]) - value) for k, value in expected.items()))
            gaussian_standardised_error = max(gaussian_standardised_error,
                                              abs(float(r["is95_standardised"]) - expected["is95_standardised"]))
            assert float(r["covered95"]) == float(abs(y) <= q95)
            assert float(r["covered68"]) == float(abs(y) <= NormalDist().inv_cdf(.841344746) * sd)
            gaussian_checks += 1
        grouped = defaultdict(list)
        hosts = {}
        for r in data:
            grouped[r["method"], r["planet"]].append(r)
            hosts[r["planet"]] = r["host"]
        planets = sorted(hosts)
        model_means = {}
        error = 0.
        for model, reference in case["metrics_equal_planet"].items():
            model_means[model] = {}
            for metric, expected in reference.items():
                values = [np.mean([float(r[metric]) for r in grouped[model, p]]) for p in planets]
                model_means[model][metric] = np.asarray(values)
                error = max(error, abs(float(np.mean(values)) - expected))
        assert error < 1e-10
        contrasts = np.column_stack([model_means[m]["is95_standardised"] - model_means["M0"]["is95_standardised"]
                                     for m in ("M1", "M2", "M3")])
        assert abs(float(contrasts[:, 1].mean()) - case["delta_M2_minus_M0_standardised"]) < 1e-10
        hnames = sorted(set(hosts.values()))
        sums = np.zeros((len(hnames), 3)); counts = np.zeros(len(hnames))
        hindex = {h: i for i, h in enumerate(hnames)}
        for p, value in zip(planets, contrasts):
            sums[hindex[hosts[p]]] += value
            counts[hindex[hosts[p]]] += 1
        rng = np.random.default_rng(20261109)
        draws = []
        for _ in range(10000):
            multiplicity = np.bincount(rng.integers(0, len(hnames), len(hnames)), minlength=len(hnames))
            draws.append((multiplicity @ sums) / (multiplicity @ counts))
        intervals = np.quantile(draws, [.025, .975], axis=0)
        interval_error = max(float(np.max(np.abs(intervals[:, j] - case["conditional_fixed_scenario_fit_ci95"][m])))
                             for j, m in enumerate(("M1", "M2", "M3")))
        assert interval_error < 1e-10
        result[case["case"]] = {"equal_planet_metric_max_error": error,
                               "conditional_interval_max_error": interval_error,
                               "accepted_planets": len(planets), "score_and_ledger_hashes_match": True}
    curves = rows(base / "descriptive/leave_gain_hosts_out.csv")
    primary = [r for r in curves if r["analysis_set"] == "primary"]
    assert len(primary) == 6 and primary[1]["removed_hosts"] == "HR858"
    original = rows(ROOT / "results/final_primary/scores.csv")
    values = defaultdict(list)
    for r in original:
        values[r["planet"], r["method"]].append(float(r["is95_standardised"]))
    delta = {p: np.mean(v) - np.mean(values[p, "M0"]) for (p, m), v in values.items() if m == "M2"}
    assert abs(np.mean(list(delta.values())) - float(primary[0]["mean_planet_delta"])) < 1e-12
    assert abs(np.mean([v for p, v in delta.items() if p != "HR858b"]) - float(primary[1]["mean_planet_delta"])) < 1e-12
    output = {"all_checks_pass": True, "cases": result, "primary_influence_k0_k1_independent": True,
              "closed_form_Gaussian_M0_scenario_events": gaussian_checks,
              "closed_form_Gaussian_M0_max_metric_error": gaussian_error,
              "closed_form_Gaussian_M0_standardised_score_error": gaussian_standardised_error,
              "interval_limit": "Conditional on scenario fit; not joint-refit inference or a new verdict.",
              "raw_photometry_or_headers_read": False,
              "summary_sha256": digest(base / "sensitivities/summary.json")}
    assert gaussian_checks == 19240 and gaussian_error < 1e-10
    dest = ROOT / "results/final_review/secondary_checks.json"
    dest.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"cases": len(cases), "all_checks_pass": True}))


if __name__ == "__main__":
    main()
