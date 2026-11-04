import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
HAS_SCIPY = importlib.util.find_spec("scipy") is not None


@unittest.skipUnless(HAS_SCIPY, "scipy is in the optional analysis extra")
class ForecastVarianceTests(unittest.TestCase):
    def setUp(self):
        import forecast_variance_components as f
        self.f = f
        rng = np.random.default_rng(3)
        self.planets = [{"se": rng.uniform(0.2, 2, k), "n": np.sort(rng.uniform(500, 1500, k)),
                         "st0": rng.uniform(0.1, 1), "sp": rng.uniform(1e-4, 1e-3), "m": np.zeros(k)}
                        for k in rng.integers(1, 6, 400)]

    def test_rank_two_likelihood_matches_dense_cholesky(self):
        p = self.planets[7]
        y = np.linspace(-1, 2, len(p["n"]))
        for c in (0.01, 1.0, 50.0):
            V = np.diag(p["se"] ** 2) + c * (p["st0"] ** 2 + np.outer(p["n"], p["n"]) * p["sp"] ** 2)
            sign, logdet = np.linalg.slogdet(V)
            dense = -0.5 * (logdet + y @ np.linalg.solve(V, y) + len(y) * np.log(2 * np.pi))
            fast = self.f.planet_ll(self.f.precompute([p], [y]), c)[0]
            self.assertAlmostEqual(dense, float(fast), places=8)

    def test_scale_mixture_recovers_inflation_and_spread(self):
        rng = np.random.default_rng(11)
        ys = self.f.simulate(self.planets, 1.6, 1.0, rng)
        est = self.f.fit(self.planets, ys)
        self.assertLess(abs(np.log(est["b"] / 1.6)), 0.25)
        self.assertLess(abs(est["s_log_lambda"] - 1.0), 0.4)


@unittest.skipUnless(HAS_SCIPY, "scipy is in the optional analysis extra")
class LocalNoiseTests(unittest.TestCase):
    def test_reml_separates_scale_from_additive_jitter_when_sigma_varies(self):
        import local_noise_structure as ln
        rng = np.random.default_rng(5)
        data_scale, data_jit = [], []
        for _ in range(400):
            k = 6
            s = np.full(k, rng.choice([0.2, 0.6, 2.0]))
            X = np.ones((k, 1))
            data_scale.append(("p", 1.15 * s * rng.standard_normal(k), s, X))
            data_jit.append(("p", np.sqrt(s**2 + 0.4**2) * rng.standard_normal(k), s, X))
        fs, fj = ln.fit(data_scale), ln.fit(data_jit)
        self.assertGreater(fs["jitter_only"]["nll"] - fs["scale_only"]["nll"], 5)
        self.assertGreater(fj["scale_only"]["nll"] - fj["jitter_only"]["nll"], 5)
        self.assertAlmostEqual(fs["scale_plus_jitter"]["a"], 1.15, delta=0.05)


if __name__ == "__main__":
    unittest.main()
