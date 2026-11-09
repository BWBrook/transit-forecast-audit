"""Synthetic orchestration audit: unchanged DRD identification, separate DRC scoring.

No photometry, headers or network requests are read. Download/read and the two
expensive fit functions are explicit synthetic stubs; measurement row generation,
coverage calculation, cycle matching, acceptance and scoring are the real frozen
functions. This is an interface proof, not timing-method qualification.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import acceptance as A
import final_evaluation as fe
import final_measure as fm
import reproduce_table5
from transit_audit.exoclock import Ephemeris


def synthetic_measurement():
    drd = {"Pb": Ephemeris("Pb", 2460000., .001, 3., .00001)}
    manifest = [{"event_id": "synthetic|Pb|S60|DRD10", "observation_id": "synthetic|Pb|S60|DRD10",
                 "planet": "Pb", "host": "P", "sector": "60", "forecast_epoch": "10",
                 "identification_release": "DRD", "identification_epoch": "10", "drc_epoch": "2"}]
    t = np.arange(29.6, 30.4, 120 / 86400)
    sigma = 60 / 86400
    tc = 30.
    quantiles = [tc - sigma, tc - sigma, tc, tc + sigma, tc + sigma,
                 tc - 1.959964 * sigma, tc + 1.959964 * sigma]
    fitted = {"local_epoch": 0, "centre": tc, "tc": tc, "status": "timed", "failure_reason": "",
              "coverage_window": 1., "coverage_in_transit": 1., "q": quantiles,
              "sig": sigma, "sig_white": sigma, "beta": 1., "rchi": 1., "flags": "",
              "n": 200, "gauss_ok": True, "cadenceno_first": 1, "cadenceno_last": len(t),
              "loo_shift_s": "not_estimable"}
    sol = {"id_fail": "", "id": {"snr": 20., "per": 3.}, "t14": .1, "half": .2,
           "rchi_shape": 1., "at_bound": []}
    meta = {"BJDREFI": 2460000, "BJDREFF": 0., "SECTOR": 60, "CAMERA": 1, "CCD": 1,
            "DATA_REL": 1, "TIMESYS": "TDB", "TIMEREF": "SOLARSYSTEM", "exp_s": 120.}
    item = ("tess-synthetic-0000000000000001-s0001", manifest,
            {"t_max_mjd": "60001"}, "development", "synthetic_grids_not_written")
    with patch.object(reproduce_table5, "load", return_value=({"DRD": drd}, None)), \
            patch.dict(fm._ERA, {"era": "development"}), \
            patch.object(fm.tp, "download", return_value=Path("synthetic_not_opened.fits")) as download, \
            patch.object(fm.tp, "read", return_value=(t, np.ones(len(t)), np.ones(len(t)) * .001,
                                                     np.arange(len(t)), meta)), \
            patch.object(fm.tp, "sha256", return_value="0" * 64), \
            patch.object(fm.so, "solution", return_value=sol) as solution, \
            patch.object(fm.so, "time_windows", return_value=[fitted]):
        windows, diagnostics, coverage = fm.measure_product(item)
        supplied_period = solution.call_args.args[-1]
        request_guard = download.call_args.args[0]["guard_ok"]
    return {"drd": drd, "manifest": manifest, "windows": windows, "diagnostics": diagnostics,
            "coverage": coverage, "solution_period": supplied_period, "request_guard": request_guard}


def contract(out):
    case = synthetic_measurement()
    products = {(r["planet"], str(int(r["sector"]))): r for r in case["diagnostics"]}
    coverage = {r["event_id"]: r for r in case["coverage"]}
    ledger, outside = fe.terminal_ledger(case["manifest"], case["windows"], products, coverage, case["drd"])
    fc = {"event_id": case["manifest"][0]["event_id"],
          "observation_id": case["manifest"][0]["observation_id"], "planet": "Pb", "host": "P",
          "release": "DRC", "forecast_epoch": "2", "identification_epoch": "10",
          "predicted_bjd_tdb": "2460031.0", "forecast_variance_s2": "3600",
          "parameter_version": "synthetic-interface-test"}
    for model in fe.c.METHODS:
        fc[model + "_b"], fc[model + "_s_log_lambda"] = "1", "0"
    outcomes, forecasts = fe.scoring_inputs(ledger, case["windows"], [fc])
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    fe.write_csv(out / "outcomes.csv", outcomes)
    fe.write_csv(out / "forecasts.csv", forecasts)
    fe.ad.score_outcomes(argparse.Namespace(forecasts=str(out / "forecasts.csv"),
                                           outcomes=str(out / "outcomes.csv"), error_convention=fe.CONVENTION,
                                           outcome_scale=1., output=str(out / "scores.csv"),
                                           max_tc_bjd=fe.era_limit("development")))
    with (out / "scores.csv").open() as handle:
        scores = list(csv.DictReader(handle))
    m0 = next(r for r in scores if r["method"] == "M0")
    wrong_epoch = [{**case["manifest"][0], "forecast_epoch": "2"}]
    wrong, _ = fe.terminal_ledger(wrong_epoch, case["windows"], products, coverage, case["drd"])
    wrong_catalogue_status = A.terminal_status("ok", case["windows"], case["diagnostics"][0],
                                             2460031., 3., True)
    report = {"label": "synthetic interface contract; no astronomical observations",
              "fit_stubs": ["download", "read", "source-file digest", "solution", "time_windows"],
              "actual_functions": ["final_measure.measure_product", "final_measure.coverage_at",
                                   "final_evaluation.terminal_ledger", "acceptance.terminal_status",
                                   "final_evaluation.scoring_inputs", "sprint1_outcome_adapter.score_outcomes"],
              "identification_release": "DRD", "identification_epoch": 10, "scored_release": "DRC",
              "scored_epoch": 2, "solution_period_days": case["solution_period"],
              "identification_prediction_bjd_tdb": ledger[0]["drd_predicted_bjd_tdb"],
              "scored_prediction_bjd_tdb": float(fc["predicted_bjd_tdb"]),
              "forecast_residual_s": (float(outcomes[0]["tc_bjd_tdb"]) - float(fc["predicted_bjd_tdb"])) * 86400,
              "p_over_4_s": 3 * 86400 / 4, "terminal_status": ledger[0]["status"],
              "measurement_coverage": case["coverage"], "outside_windows": len(outside),
              "m0_covered95": float(m0["covered95"]), "m0_is95_minutes": float(m0["is95_minutes"]),
              "wrong_manifest_epoch_status": wrong[0]["status"],
              "wrong_gate_catalogue_status": wrong_catalogue_status,
              "request_guard_was_development": bool(case["request_guard"]),
              "candidate_photometry_or_headers_read": False,
              "source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                                for p in [Path(__file__), ROOT / "scripts/final_measure.py",
                                          ROOT / "scripts/final_evaluation.py", ROOT / "scripts/acceptance.py",
                                          ROOT / "scripts/sprint1_outcome_adapter.py"]}}
    (out / "contract.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=str(ROOT / "results/d073_identification"))
    args = ap.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        result = contract(temp)
        destination = Path(args.out)
        destination.mkdir(parents=True, exist_ok=True)
        for name in ("contract.json", "outcomes.csv", "forecasts.csv", "scores.csv"):
            (destination / name).write_bytes((Path(temp) / name).read_bytes())
    print(json.dumps({k: result[k] for k in ("terminal_status", "forecast_residual_s", "m0_covered95",
                                            "wrong_manifest_epoch_status", "wrong_gate_catalogue_status")}))
