import sys
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import review_sprint2_timing as review
import sprint2_outcomes as so
import t015_timing_pipeline as tp


class Sprint2TimingIntegration(unittest.TestCase):
    def test_separated_secondary_mode_cannot_be_certified_gaussian(self):
        result = review.secondary_mode_control()
        self.assertAlmostEqual(result["mass_outside_fine"], 0.03, places=8)
        self.assertTrue(result["quantile_gaussian_check_alone"])
        self.assertLess(max(result["endpoint_relative_density"]), 1e-20)
        self.assertEqual(result["current_status"], "integration_unresolved")
        self.assertFalse(result["current_gauss_ok"])

    def test_unstable_coarse_fine_integration_fails_and_resolved_profile_passes(self):
        t = np.linspace(-0.14, 0.14, 29)
        sol = {"wins": [(0, 0.0)], "half": 0.15, "t14": 0.05, "per": 3.0, "shape": {}}
        q = np.array([-2, -1, 0, 1, 2, -1.959964, 1.959964]) / 86400
        result = {"tc": 0.0, "q": q, "sig": 1 / 86400, "n": len(t), "resid": np.zeros(len(t)),
                  "grid": np.linspace(-10, 10, 21) / 86400, "chi": np.linspace(-10, 10, 21) ** 2,
                  "edge_mass": 0.0, "mass_outside_fine": 0.0, "coarse_shift_sig": 0.11, "fine_step_s": 1.0}
        with patch.object(tp, "timed", return_value=(result, result, 1.0, 1.0, 1.0)):
            row = so.time_windows(t, np.ones(len(t)), np.ones(len(t)), sol, 120, 0.01)[0]
        self.assertEqual(row["status"], "integration_unresolved")
        self.assertIn("coarse_fine_shift", row["failure_reason"])
        self.assertFalse(row["gauss_ok"])
        result["coarse_shift_sig"] = 0.0
        with patch.object(tp, "timed", return_value=(result, result, 1.0, 1.0, 1.0)):
            row = so.time_windows(t, np.ones(len(t)), np.ones(len(t)), sol, 120, 0.01)[0]
        self.assertEqual(row["status"], "timed")
        self.assertTrue(row["gauss_ok"])


if __name__ == "__main__":
    unittest.main()
