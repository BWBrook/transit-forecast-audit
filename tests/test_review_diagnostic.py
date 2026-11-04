import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_measurement_diagnostic import groups, project


class LocalScatterReviewTests(unittest.TestCase):
    def test_adjacent_gap_rule_can_chain_across_a_year_but_span_cap_cannot(self):
        events = [SimpleNamespace(t_bjd_tdb=float(t)) for t in range(0, 381, 10)]
        self.assertEqual(len(list(groups(events))), 1)
        bounded = list(groups(events, 20))
        self.assertEqual(sum(map(len, bounded)), len(events))
        self.assertTrue(all(g[-1].t_bjd_tdb - g[0].t_bjd_tdb <= 20 for g in bounded))

    def test_common_timing_offset_is_invisible_to_local_scatter(self):
        t = np.array([0, 2.001, 3.999, 6.002, 8.0])
        s = np.array([.001, .002, .001, .003, .002])
        before, chi, df = project(t, s, 2.0, False)
        after, shifted_chi, shifted_df = project(t + .1, s, 2.0, False)
        np.testing.assert_allclose(after, before, atol=1e-11)
        self.assertAlmostEqual(chi, shifted_chi, places=10)
        self.assertEqual(df, shifted_df)

    def test_local_slope_absorbs_linear_drift_but_constant_does_not(self):
        t = np.arange(8) * 2.001
        s = np.full(8, .001)
        _, constant_chi, constant_df = project(t, s, 2.0, False)
        z, linear_chi, linear_df = project(t, s, 2.0, True)
        self.assertGreater(constant_chi, 10)
        self.assertLess(linear_chi, 1e-18)
        self.assertLess(np.max(np.abs(z)), 1e-9)
        self.assertEqual((constant_df, linear_df), (7, 6))


if __name__ == "__main__":
    unittest.main()
