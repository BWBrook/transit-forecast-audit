"""Affine measurement sensitivity must preserve mass and unaffected identities."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import d073_s105_rescore as sensitivity


class S105SensitivityTests(unittest.TestCase):
    def test_asymmetric_grid_width_change_preserves_mass_and_support(self):
        x = np.linspace(-9., 12., 85)
        log_density = -.5 * ((x - .6) / 1.1) ** 2
        raw = {"units": "seconds", "coordinate": "true_midtime_minus_reported_midtime",
               "kind": "likelihood", "offset_s": x.tolist(), "log_density": log_density.tolist(),
               "support_s": [-9., 12.]}
        changed = sensitivity.transform_grid(raw, 2.)
        with tempfile.TemporaryDirectory() as temporary:
            a, b = Path(temporary) / "a.json", Path(temporary) / "b.json"
            a.write_text(json.dumps(raw)); b.write_text(json.dumps(changed))
            old_x, old_mass = sensitivity.adapter.likelihood_grid(a)
            new_x, new_mass = sensitivity.adapter.likelihood_grid(b)
        np.testing.assert_array_equal(new_x, 2 * old_x)
        np.testing.assert_allclose(new_mass, old_mass, atol=1e-15, rtol=0)
        np.testing.assert_allclose(changed["log_density"], log_density - np.log(2))
        self.assertEqual(changed["support_s"], [-18., 24.])
        self.assertEqual(raw["support_s"], [-9., 12.])

    def test_reported_centre_and_quantiles_transform_together(self):
        row = {"tc_bjd_tdb": "2460000", "sigma_s": "3", "q025_s": "-8", "q1587_s": "-4",
               "q8413_s": "2", "q975_s": "5", "gauss_ok": "False", "posterior_grid_path": "old"}
        changed = sensitivity.transform_outcome(row, 864., 2., "new")
        self.assertAlmostEqual(float(changed["tc_bjd_tdb"]), 2460000.01)
        self.assertEqual(float(changed["q025_s"]), -16.)
        self.assertEqual(float(changed["q8413_s"]), 4.)
        self.assertEqual(float(changed["sigma_s"]), 6.)
        self.assertEqual(changed["gauss_ok"], "False")
        with self.assertRaises(ValueError):
            sensitivity.transform_outcome(row, 0., -1.)

    def test_subset_score_weight_is_restored_and_unaffected_rows_preserved(self):
        saved = [{"event_id": event, "method": method, "weight": "0.001", "metric": "old"}
                 for event in sensitivity.EVENTS for method in sensitivity.diagnostics.METHODS]
        saved.append({"event_id": "unaffected", "method": "M0", "weight": "0.25", "metric": "untouched"})
        changed = [{**row, "weight": "0.333", "metric": "new"} for row in saved[:-1]]
        result = sensitivity.merge_scores(saved, changed)
        self.assertEqual(result[-1], saved[-1])
        self.assertEqual(result[0]["weight"], "0.001")
        self.assertEqual(result[0]["metric"], "new")
        self.assertEqual(saved[0]["metric"], "old")
        with self.assertRaises(ValueError):
            sensitivity.merge_scores(saved, changed[:-1])

    def test_far_tail_shift_changes_absolute_losses_but_not_model_contrast(self):
        def scores(residual):
            event = {"forecast_variance_s2": 1., "sigma_s": .1,
                     "outcome_scale": 1., "residual_s": residual}
            return [float(sensitivity.adapter.c.predictive_scores(
                [event], {"b": factor, "s_log_lambda": 0.}, order=384,
                interpolate=False)["is95_minutes"][0]) for factor in (1., 2.)]
        a, b = scores(-50.), scores(-70.)
        self.assertGreater(b[0], a[0])
        self.assertGreater(b[1], a[1])
        self.assertAlmostEqual(a[1] - a[0], b[1] - b[0], places=12)


if __name__ == "__main__":
    unittest.main()
