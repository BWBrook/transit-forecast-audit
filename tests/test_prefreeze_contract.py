"""Synthetic contract check of the shared t015v3a path (D058): acceptance, event mapping, adapter, joint draws."""

import argparse
import csv
import json
import math
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import acceptance as A  # noqa: E402
import prefreeze_package as pp  # noqa: E402
from sprint1_outcome_adapter import score_outcomes  # noqa: E402

DIAG_OK = {"status": "ok", "shape_rchi2": "1.1"}


def grid(path, sigma, truncate=False):
    x = np.linspace(-3600, 3600, 1441) if truncate else np.linspace(-12 * sigma, 12 * sigma, 1201)
    logd = -0.5 * (x / (sigma * (30 if truncate else 1))) ** 2
    path.write_text(json.dumps({"kind": "posterior", "prior": "uniform", "prior_constant_over_support": True,
                                "units": "seconds", "coordinate": "true_midtime_minus_reported_midtime",
                                "offset_s": x.tolist(), "log_density": logd.tolist()}))
    return str(path)


def i1(event, tc, sigma, gauss=True, grid_path="", flags="", status="timed"):
    q = 1.959964 * sigma
    return {"event_id": event, "observation_id": event, "planet": "Pb", "host": "P", "tic": "TIC 1",
            "sector": "60", "camera": "1", "ccd": "1", "product": "SPOC_120", "flux": "PDCSAP", "file": "f.fits",
            "file_sha256": "0" * 64, "data_rel": "1", "cadenceno_first": "1", "cadenceno_last": "9",
            "timesys": "TDB", "timeref": "SOLARSYSTEM", "bjdrefi": "2457000", "bjdreff": "0",
            "tc_bjd_tdb": str(tc), "sigma_s": str(sigma), "gauss_ok": str(gauss),
            "q025_s": str(-q), "q1587_s": str(-sigma), "q8413_s": str(sigma), "q975_s": str(q),
            "posterior_grid_path": grid_path, "shape_group_id": "Pb|60", "loo_shift_s": "0.1",
            "id_method": "catalogue_period", "id_period_d": "3.0", "id_period_source": "DRD",
            "id_period_source_date": "2025-11-18", "coverage_window": "1", "coverage_in_transit": "1",
            "status": status, "failure_reason": "" if status == "timed" else status, "flags": flags,
            "error_convention": "t015v3_beta_chi", "rule_version": "t015v3a-test"}


class PrefreezeContract(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_acceptance_states(self):
        good = grid(self.tmp / "g.json", 60)
        bad = grid(self.tmp / "b.json", 60, truncate=True)
        self.assertEqual(A.accept(i1("a", 2460000.0, 60), DIAG_OK), A.ACCEPTED)
        self.assertEqual(A.accept(i1("b", 2460000.0, 60, gauss=False, grid_path=good), DIAG_OK), A.ACCEPTED)
        self.assertEqual(A.accept(i1("c", 2460000.0, 60, gauss=False, grid_path=bad), DIAG_OK),
                         "likelihood_support_unresolved")
        self.assertEqual(A.accept(i1("d", 2460000.0, 60, gauss=False), DIAG_OK), "likelihood_support_unresolved")
        self.assertEqual(A.accept(i1("e", 2460000.0, 60, flags="mass_outside_fine"), DIAG_OK), "integration_unresolved")
        self.assertEqual(A.accept(i1("f", 2460000.0, float("nan")), DIAG_OK), "timing_value_unresolved")
        self.assertEqual(A.accept(i1("g", 2460000.0, 60), {"status": "ok", "shape_rchi2": ""}),
                         "product_shape_diagnostic_unresolved")
        self.assertEqual(A.accept(i1("h", 2460000.0, 60), {"status": "ok", "shape_rchi2": "nan"}),
                         "product_shape_diagnostic_unresolved")
        self.assertEqual(A.accept(i1("i", 2460000.0, 60), {"status": "ok", "shape_rchi2": "228"}),
                         "product_shape_gate_failed")
        self.assertEqual(A.accept(i1("j", 2460000.0, 60), None), "product_unavailable")
        self.assertEqual(A.accept(i1("k", 2460000.0, 60), DIAG_OK, product="TESS-SPOC_200"), "product_not_in_scope")

    def test_terminal_mapping(self):
        w = i1("a", 2460000.0, 60)
        self.assertEqual(A.terminal_status("ok", [w], DIAG_OK, 2460000.001, 3.0, True), A.ACCEPTED)
        self.assertEqual(A.terminal_status("ok", [w], DIAG_OK, 2460001.0, 3.0, True), "cycle_ambiguous")
        self.assertEqual(A.terminal_status("ok", [w, w], DIAG_OK, 2460000.0, 3.0, True), "ambiguous_multiple_windows")
        self.assertEqual(A.terminal_status("ok", [], DIAG_OK, 2460000.0, 3.0, True), "unmatched_expected_event")
        self.assertEqual(A.terminal_status("ok", [], DIAG_OK, 2460000.0, 3.0, False), "no_cadence_coverage_at_prediction")
        self.assertEqual(A.terminal_status("ok", [], DIAG_OK, 2460000.0, 3.0, None), "unmatched_observability_unknown")
        self.assertEqual(A.terminal_status("product_shape_gate_failed", [w], DIAG_OK, 2460000.0, 3.0, True),
                         "product_shape_gate_failed")

    def test_adapter_scores_only_accepted_rows(self):
        good = grid(self.tmp / "g.json", 90)
        bad = grid(self.tmp / "b.json", 90, truncate=True)
        rows = [i1("e1", 2460000.00, 60), i1("e2", 2460003.00, 90, gauss=False, grid_path=good),
                i1("e3", 2460006.00, 90, gauss=False, grid_path=bad), i1("e4", 2460009.00, 60, flags="coarse_fine_shift"),
                i1("e5", 2460012.00, 60, status="excluded_coverage")]
        for r in rows:
            st = A.accept(r, DIAG_OK)
            if st != A.ACCEPTED:
                r.update(status=st, failure_reason=st)
        out = self.tmp / "outcomes.csv"
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
        fc = self.tmp / "forecasts.csv"
        frows = [{"event_id": r["event_id"], "observation_id": r["observation_id"], "planet": "Pb", "host": "P",
                  "release": "DRC", "predicted_bjd_tdb": str(float(r["tc_bjd_tdb"]) + 30 / 86400),
                  "forecast_variance_s2": "3600", "M0_b": "1", "M0_s_log_lambda": "0", "M1_b": "2", "M1_s_log_lambda": "0",
                  "M2_b": "1", "M2_s_log_lambda": "2", "M3_b": "1.1", "M3_s_log_lambda": "1.9",
                  "parameter_version": "test"} for r in rows]
        with fc.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(frows[0]), lineterminator="\n")
            w.writeheader()
            w.writerows(frows)
        dest = self.tmp / "scores.csv"
        score_outcomes(argparse.Namespace(forecasts=str(fc), outcomes=str(out), error_convention="t015v3_beta_chi",
                                          outcome_scale=1.0, output=str(dest)))
        rec = json.loads(dest.with_suffix(".receipt.json").read_text())
        self.assertEqual(rec["timed_production_events"], 2)
        self.assertEqual(rec["nonGaussian_events"], 1)
        with dest.open() as fh:
            scored = {r["event_id"] for r in csv.DictReader(fh)}
        self.assertEqual(scored, {"e1", "e2"})

    def test_joint_draws_share_host_multiplicities(self):
        train = [{"host": "H1"}, {"host": "H2"}]
        test = [{"host": "H2"}, {"host": "H3"}]
        hosts, draws = pp.joint_draws(train, test, 50, 7, fit=False)
        self.assertEqual(hosts, ["H1", "H2", "H3"])
        for d in draws:
            self.assertEqual(len(d["multiplicity"]), 3)
            self.assertEqual(sum(d["multiplicity"]), 3)
        self.assertTrue(math.isfinite(np.mean([d["multiplicity"][1] for d in draws])))


if __name__ == "__main__":
    unittest.main()
