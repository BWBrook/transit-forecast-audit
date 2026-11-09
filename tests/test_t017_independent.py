import importlib.util
import sys
import unittest
from pathlib import Path

HAS_SCIENCE = all(importlib.util.find_spec(name) for name in ("numpy", "scipy", "astropy"))
if HAS_SCIENCE:
    import numpy as np
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    import t017_independent as independent


@unittest.skipUnless(HAS_SCIENCE, "Independent photometry runtime required")
class IndependentTimingTests(unittest.TestCase):
    def settings(self):
        return {"fit_window_duration_multiplier": 2.5,
                "maximum_local_half_window_fraction_period": .45,
                "minimum_points_each_outside_side": 8, "timing_profile_step_s": 15}

    def test_profile_matches_direct_nuisance_regression(self):
        t = np.linspace(-.3, .3, 301)
        error = np.linspace(.0003, .0006, len(t))
        y = 1.001 + .002 * t - .006 * independent.trapezoid(t, .027, .13, .2)
        profile = independent.LocalProfile(t, y, error)
        centres = np.array([-.02, .027, .06])
        chis, depths = profile.many(centres, .13, .2)
        for i, centre in enumerate(centres):
            x = np.column_stack((np.ones(len(t)), t, -independent.trapezoid(t, centre, .13, .2)))
            beta = np.linalg.lstsq(x / error[:, None], y / error, rcond=None)[0]
            direct = np.sum(((y - x @ beta) / error) ** 2)
            self.assertAlmostEqual(chis[i], direct, places=7)
            self.assertAlmostEqual(depths[i], beta[2], places=10)

    def test_recovers_time_with_joint_depth_and_sloped_baseline(self):
        rng = np.random.default_rng(73)
        t = 4231. + np.linspace(-.32, .32, 461)
        truth = 4231.021
        error = np.full(len(t), .0003)
        y = 1.002 + .006 * (t - 4231.) - .006 * independent.trapezoid(t, truth, .12, .2)
        y += rng.normal(0, error)
        shape = {"duration_d": .12, "ingress_fraction": .2}
        result = independent.profile_transit(t, y, error, 4231., shape, 2., self.settings(), np.zeros(len(t), bool))
        self.assertEqual(result["status"], "timed")
        self.assertLess(abs(result["tc_btjd"] - truth) * 1440, 1.)
        self.assertLess(result["q025_btjd"], truth)
        self.assertGreater(result["q975_btjd"], truth)
        joint = independent.joint_nuisance(t, y, error, 4231., shape, 2., self.settings(), np.zeros(len(t), bool))
        self.assertEqual(joint["status"], "joint_fit")
        self.assertLess(abs(joint["tc_btjd"] - truth) * 1440, 1.)

    def test_missing_baseline_is_not_a_timing(self):
        t = np.linspace(-.04, .04, 100)
        result = independent.profile_transit(t, np.ones(len(t)), np.ones(len(t)), 0.,
                                             {"duration_d": .12, "ingress_fraction": .2}, 2.,
                                             self.settings(), np.zeros(len(t), bool))
        self.assertEqual(result["status"], "insufficient_window_coverage")

    def test_forbidden_sector_rejected_before_file_access(self):
        for sector in (74, 86, 97):
            with self.assertRaisesRegex(ValueError, "Forbidden"):
                independent.allowed_product({"sector": sector,
                    "relative_fits_path": f"data/raw/mast/TIC_1/tess2024000000000-s{sector:04d}-0000000000000001-0000-s_lc.fits"})

    def test_continuum_does_not_bridge_segment_offsets(self):
        t = np.r_[np.arange(0, 1, .01), np.arange(2, 3, .01)]
        y = np.r_[np.ones(100), np.ones(100) * 1.2]
        trend = independent.continuum(t, y)
        np.testing.assert_allclose(trend, y)

    def test_phase_search_does_not_require_an_issued_epoch(self):
        t = np.arange(0, 12, .01)
        period, truth_epoch = 1.7, .427
        folded = independent.phase(t, truth_epoch, period)
        error = np.full(len(t), .0005)
        y = 1 - .01 * independent.trapezoid(folded, 0, .12, .2)
        settings = {"blind_period_range_d": [.3, 15.], "period_grid_size": 20000,
                    "durations_d": [.03, .05, .08, .12, .18, .24],
                    "maximum_sequential_signals": 3, "minimum_bls_snr": 5,
                    "target_period_tolerance_fraction": .05}
        signals, selected, _ = independent.identify(t, y, error, period, settings)
        self.assertIsNotNone(selected)
        self.assertLess(abs(signals[selected]["period_d"] / period - 1), .002)
        self.assertLess(abs(independent.phase(np.array([truth_epoch]), signals[selected]["epoch_btjd"], period)[0]), .03)

    def test_residual_target_harmonics_cannot_mask_away_target(self):
        t = np.arange(0, 8, .002)
        signals = [{"period_d": 2., "epoch_btjd": .4, "duration_d": .12},
                   {"period_d": 2., "epoch_btjd": .405, "duration_d": .08},
                   {"period_d": .5, "epoch_btjd": .4, "duration_d": .04}]
        mask, diagnostics = independent.companion_mask(t, signals, 0)
        centres = np.abs(independent.phase(t, .4, 2.)) < .04
        self.assertFalse(mask[centres].any())
        self.assertTrue(all(row["harmonic_candidate"] for row in diagnostics))
        self.assertGreater(sum(row["target_cadences_protected_from_harmonic_mask"] for row in diagnostics), 0)
        opposite = [{"period_d": 2., "epoch_btjd": .4, "duration_d": .12},
                    {"period_d": 2., "epoch_btjd": 1.4, "duration_d": .08}]
        mask, _ = independent.companion_mask(t, opposite, 0)
        self.assertTrue(mask[np.abs(independent.phase(t, 1.4, 2.)) < .02].all())
        nonharmonic = [{"period_d": 2., "epoch_btjd": .4, "duration_d": .12},
                       {"period_d": 3.3, "epoch_btjd": .4, "duration_d": .08}]
        mask, diag = independent.companion_mask(t, nonharmonic, 0)
        self.assertTrue(mask[np.abs(t - .4) < .02].all())
        self.assertFalse(diag[0]["harmonic_candidate"])


if __name__ == "__main__":
    unittest.main()
