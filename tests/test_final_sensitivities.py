import importlib.util
import unittest
from pathlib import Path

import numpy as np

MODULE = Path(__file__).resolve().parents[1] / "scripts/final_sensitivities.py"
spec = importlib.util.spec_from_file_location("final_sensitivities", MODULE)
s = importlib.util.module_from_spec(spec)
spec.loader.exec_module(s)


class FinalSensitivities(unittest.TestCase):
    def test_majority_preserves_old_new_integration_label_and_strict_tie(self):
        base = {"planet": "synthetic-b", "sector": "1", "product": "SPOC_120"}
        good = {**base, "status": "timed", "flags": ""}
        old = {**base, "status": "timed", "flags": "mass_outside_fine"}
        new = {**base, "status": "integration_unresolved", "flags": "mass_outside_fine"}
        key = s.product_key(base)
        old_result = s.majority_products([good, old])[key]
        new_result = s.majority_products([good, new])[key]
        self.assertEqual(old_result, new_result)
        self.assertEqual(old_result["denominator"], 2)
        self.assertFalse(old_result["passes"])
        self.assertTrue(s.majority_products([good, good, new])[key]["passes"])
        empty = s.majority_products([{**base, "status": "excluded_coverage"}])[key]
        self.assertFalse(empty["passes"])

    def test_majority_counts_all_recovered_windows_not_only_manifest(self):
        base = {"planet": "synthetic-b", "sector": "1", "product": "SPOC_120"}
        rows = [{**base, "event_id": "intended", "status": "timed", "flags": ""},
                {**base, "event_id": "outside1", "status": "edge", "flags": ""},
                {**base, "event_id": "outside2", "status": "integration_unresolved", "flags": ""}]
        self.assertFalse(s.majority_products(rows)[s.product_key(base)]["passes"])

    def test_scale_changes_sigma_grid_coordinates_and_actual_variance_only(self):
        grid = np.array([-3., -1., 2., 5.]), np.array([.1, .2, .5, .2])
        event = {"sigma_s": 2., "forecast_variance_s2": 9., "grid": grid,
                 "residual_s": 17., "tc_bjd_tdb": 123.}
        transformed = s.scaled_event(event, 1.1)
        np.testing.assert_array_equal(transformed["grid"][0], grid[0] * 1.1)
        np.testing.assert_array_equal(transformed["grid"][1], grid[1])
        variance = grid[1] @ grid[0] ** 2 - (grid[1] @ grid[0]) ** 2
        self.assertAlmostEqual(transformed["denom"] ** 2, 9 + 1.1 ** 2 * variance)
        self.assertEqual(transformed["sigma_s"], 2.2)
        self.assertEqual(transformed["residual_s"], 17.)
        self.assertEqual(transformed["tc_bjd_tdb"], 123.)
        np.testing.assert_array_equal(event["grid"][0], grid[0])

    def test_covariance_sensitivity_uses_joint_variance(self):
        event = {"sigma_s": 2., "forecast_variance_s2": 1., "grid": None,
                 "sigma_t0_s": 4., "sigma_p_s": 2., "forecast_epoch": 3, "residual_s": 99.}
        self.assertEqual(s.scaled_event(event, rho=-1)["forecast_variance_s2"], 4.)
        self.assertEqual(s.scaled_event(event, rho=0)["forecast_variance_s2"], 52.)
        self.assertEqual(s.scaled_event(event, rho=1)["forecast_variance_s2"], 100.)
        self.assertEqual(s.scaled_event(event, rho=-1)["residual_s"], 99.)

    def test_conditional_bootstrap_keeps_hosts_whole_and_planets_equal(self):
        deltas = np.array([[-4.], [2.], [8.]])
        interval = s.conditional_intervals(["p1", "p2", "p3"], ["h1", "h1", "h2"], deltas,
                                           replicates=1, seed=1)
        self.assertEqual(interval, [[2., 2.]])
        interval = s.conditional_intervals(["p1", "p2", "p3"], ["h1", "h1", "h2"], deltas,
                                           replicates=1000, seed=1)
        self.assertEqual(interval, [[-1., 8.]])

    def test_journal_selection_uses_forecast_never_measured_time(self):
        anchor = s.numeric_jd("2026-02-12T00:00:00Z")
        before = {"predicted_bjd_tdb": anchor - 1., "tc_bjd_tdb": anchor + 2.}
        after = {"predicted_bjd_tdb": anchor + 1., "tc_bjd_tdb": anchor - 2.}
        self.assertEqual(s.journal_status(before, anchor), "excluded_before_numeric_journal_anchor")
        self.assertIsNone(s.journal_status(after, anchor))
        self.assertEqual(s.journal_status({"predicted_bjd_tdb": anchor + 9 / 1440}, anchor),
                         "excluded_numeric_journal_boundary_10min")
        self.assertIsNone(s.journal_status({"predicted_bjd_tdb": anchor + 11 / 1440}, anchor))

    def test_equal_planet_metrics_rebuild_after_subsetting(self):
        events = [{"planet": "p1", "host": "h1"}, {"planet": "p1", "host": "h1"},
                  {"planet": "p2", "host": "h2"}]
        scores = {m: {metric: np.array([1., 1., 9.]) for metric in s.METRICS} for m in s.METHODS}
        metrics, per_planet, intervals = s.aggregate(events, scores, "synthetic")
        self.assertEqual(metrics["M0"]["is95_standardised"], 5.)
        self.assertEqual([row["accepted_events"] for row in per_planet], [2, 1])
        self.assertEqual(intervals["M2"], [0., 0.])


if __name__ == "__main__":
    unittest.main()
