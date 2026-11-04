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
        for c in (0.01, 1.0, 50.0, 1e8):
            V = np.diag(p["se"] ** 2) + c * (p["st0"] ** 2 + np.outer(p["n"], p["n"]) * p["sp"] ** 2)
            sign, logdet = np.linalg.slogdet(V)
            dense = -0.5 * (logdet + y @ np.linalg.solve(V, y) + len(y) * np.log(2 * np.pi))
            fast = self.f.planet_ll(self.f.precompute([p], [y]), c)[0]
            self.assertAlmostEqual(dense, float(fast), delta=1e-7 * max(1.0, abs(dense)))
        pre = self.f.precompute([p], [y])
        rank = int(np.sum(pre[0][1] > 0))
        limit = [float(self.f.planet_ll(pre, c)[0]) + 0.5 * rank * np.log(c) for c in (1e16, 1e32)]
        self.assertAlmostEqual(limit[0], limit[1], places=6)

    def test_scale_mixture_recovers_inflation_and_spread(self):
        rng = np.random.default_rng(11)
        ys = self.f.simulate(self.planets, 1.6, 1.0, rng)
        est = self.f.fit(self.planets, ys)
        self.assertLess(abs(np.log(est["b"] / 1.6)), 0.25)
        self.assertLess(abs(est["s_log_lambda"] - 1.0), 0.4)

    def test_continuous_posterior_returns_prior_for_uninformative_forecast_design(self):
        from scipy.special import ndtr
        p = {"planet":"synthetic", "se":np.array([1.]), "n":np.array([0.]),
             "st0":0., "sp":0.}
        result = self.f.posterior_lambda([p],[np.array([3.])],{"b":1.,"s_log_lambda":3.2})[0]
        self.assertAlmostEqual(result["lambda_median"],1.,places=10)
        self.assertAlmostEqual(result["probability_lambda_gt_10"],ndtr(-np.log(10)/3.2),places=6)

    def test_weighted_predictor_gradient_and_adaptive_density(self):
        from review_tranche2_mixture import stable_precompute, adaptive_log_integral
        p = self.planets[:5]
        ys = [np.linspace(-2,3,len(x["n"])) for x in p]
        for i,planet in enumerate(p):
            planet["planet"] = str(i)
        pre = self.f.precompute(p,ys)
        data = self.f.packed(pre)
        x = np.linspace(-1,1,len(p))
        weights = np.array([2,0,1,3,1])
        theta = np.array([.1,np.log(2.5),-.2])
        _,grad = self.f.objective(theta,data,True,384,x,weights)
        fd = []
        for d in np.eye(3)*1e-5:
            fd.append((self.f.objective(theta+d,data,True,384,x,weights)[0]
                       - self.f.objective(theta-d,data,True,384,x,weights)[0])/2e-5)
        np.testing.assert_allclose(grad,fd,rtol=1e-7,atol=1e-7)
        ll = self.f.objective(theta,data,True,384,x,weights,False)
        ref = stable_precompute(p,ys)
        expected = [adaptive_log_integral(item,np.exp(theta[0]+theta[2]*xx),np.exp(theta[1]))[0]
                    for item,xx in zip(ref,x)]
        np.testing.assert_allclose(ll,expected,atol=1e-6)


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
