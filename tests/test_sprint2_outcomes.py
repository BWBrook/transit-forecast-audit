import math
import sys
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint2_analysis as sa  # noqa: E402
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402


class Sprint2Outcomes(unittest.TestCase):
    def test_tmag_multiplier_frozen_values_and_clamp(self):
        self.assertAlmostEqual(so.tmag_multiplier(9), math.sqrt(0.88566859 + 2 * 0.09191112), places=12)
        self.assertAlmostEqual(so.tmag_multiplier(13.5), math.sqrt(0.88566859 - 2.5 * 0.09191112), places=12)
        self.assertEqual(so.tmag_multiplier(6.0), so.tmag_multiplier(8.0))
        self.assertEqual(so.tmag_multiplier(15.0), so.tmag_multiplier(13.5))

    def test_short_period_window_rule(self):
        t14 = 0.08
        self.assertAlmostEqual(so.half_width(1.0, t14), t14 / 2 + 90 / 1440)
        self.assertAlmostEqual(so.half_width(3.0, t14), 1.5 * t14 + 60 / 1440)

    def test_assignment_is_one_to_one_and_gated(self):
        truths = [1.0, 1.001, 3.0]
        wins = [(0, 1.0004), (1, 2.0), (2, 3.0 + 70 / 1440)]
        m = so.assign(truths, wins)
        self.assertEqual(len({j for j, _ in m.values()}), len(m))
        self.assertEqual(sum(1 for i in (0, 1) if i in m and m[i][0] == 0), 1)
        self.assertNotIn(2, m)
        self.assertTrue(all(d <= so.GATE for _, d in m.values()))

    def test_exact_95_quantiles(self):
        grid = np.arange(-3600, 3601, 1.0)
        q, _ = tp._quantiles(grid, (grid / 60.0) ** 2)
        self.assertAlmostEqual(q[5], -1.959964 * 60, delta=0.5)
        self.assertAlmostEqual(q[6], 1.959964 * 60, delta=0.5)

    def test_equal_host_weights(self):
        hs = sa.Hosts([2.0, 0.0, 0.0, 0.0], [0, 1, 1, 1], ["a", "b", "b", "b"], [9, 12, 12, 12])
        s = hs.stats(np.ones(2, int))
        self.assertAlmostEqual(s[0], math.sqrt((4.0 + 0.0) / 2))
        self.assertAlmostEqual(s[1], 0.5)
        self.assertAlmostEqual(s[6], 1.0)


if __name__ == "__main__":
    unittest.main()
