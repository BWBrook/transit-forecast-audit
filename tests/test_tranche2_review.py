import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
HAS_SCIPY = importlib.util.find_spec("scipy") is not None


@unittest.skipUnless(HAS_SCIPY, "scipy is in the optional analysis extra")
class IndependentReviewTests(unittest.TestCase):
    def test_error_contrasts_remove_linear_ephemeris_and_recover_scale_only(self):
        from review_tranche2_noise import make_contrasts, estimate
        rng = np.random.default_rng(40)
        epoch = np.arange(200)
        sigma = np.linspace(.1, 1, len(epoch))
        time = 2450000 + epoch*2 + 1.2*sigma*rng.normal(size=len(epoch))/1440
        eigen, values, _, _ = make_contrasts(time, sigma, 2)
        shifted = time + .01 + epoch*.00001
        eigen2, values2, _, _ = make_contrasts(shifted, sigma, 2)
        np.testing.assert_allclose(eigen, eigen2)
        np.testing.assert_allclose(values, values2, atol=1e-6)
        fit = estimate(eigen, values)
        self.assertAlmostEqual(fit["scale_only_a"], 1.2, delta=.15)

    def test_vectorized_predictor_density_and_gradient(self):
        from review_tranche2_predictors import pack, objective
        from review_tranche2_mixture import stable_precompute, stable_planet_ll, quadrature
        from scipy.special import logsumexp
        rng = np.random.default_rng(7)
        planets = [{"planet": str(k), "se": rng.uniform(.1, 1, k),
                    "n": np.arange(k)*20+500, "st0": .2, "sp": .001}
                   for k in range(1, 6)]
        ys = [rng.normal(size=len(p["se"]))*3 for p in planets]
        pre = stable_precompute(planets, ys)
        packed = pack(pre)
        x = np.linspace(-1, 1, len(pre))
        nodes, weights = quadrature(192)
        theta = np.array([.2, .5, -.3])
        got = objective(theta, packed, x, nodes, weights, False)
        expected = [logsumexp(stable_planet_ll(p, np.exp(2*(theta[0]+theta[2]*xx)+np.exp(theta[1])*nodes))+weights)
                    for p, xx in zip(pre, x)]
        np.testing.assert_allclose(got, expected, rtol=1e-12, atol=1e-12)
        _, grad = objective(theta, packed, x, nodes, weights)
        finite = []
        for j in range(3):
            step = np.eye(3)[j]*1e-5
            finite.append((objective(theta+step, packed, x, nodes, weights)[0]
                           - objective(theta-step, packed, x, nodes, weights)[0])/2e-5)
        np.testing.assert_allclose(grad, finite, rtol=1e-7, atol=1e-7)


if __name__ == "__main__":
    unittest.main()
