"""Distinct ephemeris epochs and large scored misses must survive DRD identification."""

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from d073_identification_contract import contract, synthetic_measurement
import acceptance as A


class IdentificationContract(unittest.TestCase):
    def test_large_drc_miss_is_accepted_against_drd_then_scored(self):
        with tempfile.TemporaryDirectory() as temp:
            report = contract(temp)
        self.assertEqual(report["terminal_status"], A.ACCEPTED)
        self.assertGreater(abs(report["forecast_residual_s"]), report["p_over_4_s"])
        self.assertEqual(report["forecast_residual_s"], -86400.)
        self.assertEqual(report["m0_covered95"], 0.)
        self.assertGreater(report["m0_is95_minutes"], 1000.)
        self.assertNotEqual(report["identification_epoch"], report["scored_epoch"])
        self.assertNotEqual(report["wrong_manifest_epoch_status"], A.ACCEPTED)
        self.assertEqual(report["wrong_gate_catalogue_status"], "cycle_ambiguous")

    def test_measurement_orchestration_uses_drd_period_and_coverage(self):
        case = synthetic_measurement()
        self.assertEqual(case["solution_period"], 3.)
        self.assertTrue(case["request_guard"])
        self.assertEqual(case["windows"][0]["drd_epoch"], 10)
        self.assertEqual(case["windows"][0]["id_period_source"], "ExoClock DRD catalogue (OSF wpjtn)")
        self.assertGreater(case["coverage"][0]["coverage_window_at_prediction"], .75)
        self.assertIn("DRD prediction", case["coverage"][0]["coverage_basis"])

    def test_missing_identification_coverage_remains_unknown(self):
        case = synthetic_measurement()
        self.assertEqual(A.terminal_status("ok", [], case["diagnostics"][0], 2460030., 3., None),
                         "unmatched_observability_unknown")
        self.assertEqual(A.terminal_status("ok", [], case["diagnostics"][0], 2460030., 3., False),
                         "no_cadence_coverage_at_prediction")


if __name__ == "__main__":
    unittest.main()
