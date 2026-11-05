import importlib.util
import unittest
from pathlib import Path

import numpy as np

spec = importlib.util.spec_from_file_location(
    "t015", Path(__file__).resolve().parents[1] / "scripts" / "t015_timing_pipeline.py")
tp = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tp)


class T015Numerics(unittest.TestCase):
    def test_trapezoid_quantiles_unbiased_on_grid(self):
        for step in (2.0, 10.0):
            grid = np.arange(-3600, 3600 + step / 2, step)
            for sigma in (5.0, 30.0, 120.0):
                q, _ = tp._quantiles(grid, (grid / sigma) ** 2)
                self.assertAlmostEqual(q[2], 0.0, delta=1e-9)
                if sigma >= 4 * step:
                    self.assertAlmostEqual(0.5 * (q[3] - q[1]) / sigma, 1.0, delta=0.01)

    def test_beta_white_noise_and_gaps(self):
        rng = np.random.default_rng(1)
        cad = 120 / 86400
        t = np.arange(0, 0.4, cad)
        t = np.r_[t[:100], t[160:]]
        betas = [tp.beta_factor(t, rng.normal(0, 1e-3, len(t)), cad) for _ in range(200)]
        self.assertLess(np.median(betas), 1.15)
        red = np.repeat(rng.normal(0, 1e-3, len(t) // 10 + 1), 10)[: len(t)]
        self.assertGreater(tp.beta_factor(t, red + rng.normal(0, 3e-4, len(t)), cad), 1.8)

    def test_guard_constants(self):
        self.assertAlmostEqual(tp.MAX_BTJD + 2457000.0, 2460313.5 - 0.01)
        self.assertLessEqual(tp.MAX_MJD, 60313.0 - 0.02)


if __name__ == "__main__":
    unittest.main()
