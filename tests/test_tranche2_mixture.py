import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
HAS_SCIPY = importlib.util.find_spec("scipy") is not None


@unittest.skipUnless(HAS_SCIPY, "scipy is in the optional analysis extra")
class StableMixtureReviewTests(unittest.TestCase):
    def setUp(self):
        import review_tranche2_mixture as review

        self.review = review

    def test_stable_rank_one_extreme_scale_matches_scalar_answer(self):
        planet = {
            "planet": "synthetic",
            "se": np.array([1e-8]),
            "n": np.array([0.0]),
            "st0": 1.0,
            "sp": 0.0,
        }
        y = np.array([1.0])
        item = self.review.stable_precompute([planet], [y])[0]
        for c in (1e-8, 1.0, 1e16, 1e48):
            variance = planet["se"][0] ** 2 + c
            expected = -0.5 * (y[0] ** 2 / variance + np.log(variance) + np.log(2 * np.pi))
            self.assertAlmostEqual(float(self.review.stable_planet_ll(item, c)), expected, places=10)

    def test_high_order_quadrature_converges_for_narrow_synthetic_posterior(self):
        planet = {
            "planet": "synthetic",
            "se": np.array([0.2, 0.3, 0.25]),
            "n": np.array([400.0, 800.0, 1200.0]),
            "st0": 0.1,
            "sp": 0.001,
        }
        item = self.review.stable_precompute([planet], [np.array([40.0, 80.0, 120.0])])
        theta = np.log([1.0, 3.2])
        n192, w192 = self.review.quadrature(192)
        n384, w384 = self.review.quadrature(384)
        q192 = self.review.quadrature_nll(theta, item, n192, w192)
        q384 = self.review.quadrature_nll(theta, item, n384, w384)
        self.assertLess(abs(q192 - q384), 2e-4)


if __name__ == "__main__":
    unittest.main()
