import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("review_sprint1_timing", ROOT / "scripts" / "review_sprint1_timing.py")
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class Sprint1TimingAuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source = ROOT / "results" / "t015_validation"
        cls.frame = AUDIT.read_csv(source / "frame_and_selection.csv")
        cls.products = AUDIT.read_csv(source / "products.csv")
        cls.runs = AUDIT.read_csv(source / "injection_runs.csv")
        cls.injections = AUDIT.read_csv(source / "injections.csv")

    def test_primary_attempt_ledger_separates_denominators(self):
        result = AUDIT.attempt_denominator(
            self.frame, self.products, self.runs, self.injections, "TESS-SPOC_200", "all"
        )
        self.assertEqual(result["selected_product_attempts"], 24)
        self.assertEqual(result["planned_injection_runs"], 48)
        self.assertEqual(result["runs_ok"], 35)
        self.assertEqual(result["runs_bls_failed"], 3)
        self.assertEqual(result["runs_dropped_window_overlap"], 6)
        self.assertEqual(result["timed_windows"], 263)
        self.assertEqual(result["coverage_excluded_windows"], 24)
        self.assertAlmostEqual(result["reported_mixed_failure_rate"], 5 / 68)
        self.assertAlmostEqual(result["planned_run_non_success_rate"], 13 / 48)

    def test_host_balance_changes_primary_bias_decision(self):
        rows = [
            row
            for row in self.injections
            if row["status"] == "timed"
            and row["product"] == "TESS-SPOC_200"
            and row["flux"] == "pdcsap"
            and row["set"] == "validation"
        ]
        event = AUDIT.point_metrics(rows, host_equal=False)
        host = AUDIT.point_metrics(rows, host_equal=True)
        self.assertAlmostEqual(event["median_bias_sigma"], 0.0819)
        self.assertAlmostEqual(host["median_bias_sigma"], 0.1026)
        self.assertLess(abs(event["median_bias_sigma"]), 0.1)
        self.assertGreater(abs(host["median_bias_sigma"]), 0.1)


if __name__ == "__main__":
    unittest.main()
