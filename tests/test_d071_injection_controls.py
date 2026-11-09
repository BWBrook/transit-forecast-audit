import math
import sys
import unittest
from pathlib import Path
from statistics import NormalDist

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from d071_injection_controls import (CADENCE, MODELS, PERIOD, SHAPE,
                                     fixed_phase_gap_mask, gaussian_score, so)


class FluxControlInterpretationTests(unittest.TestCase):
    def test_fixed_forecast_phase_gaps_can_select_on_latent_error(self):
        t = np.arange(0, 12, CADENCE)
        predicted = np.array([1.,4.,7.,10.])
        keep = fixed_phase_gap_mask(t, predicted)
        half = so.tp.t14(PERIOD, SHAPE["rp"], SHAPE["a"], SHAPE["inc"]) / 2
        early = so.tp.coverage(t[keep], 4 - 50/1440, half, CADENCE)
        late = so.tp.coverage(t[keep], 4 + 50/1440, half, CADENCE)
        self.assertGreater(early,.75)
        self.assertLess(late,.75)

    def test_measured_and_latent_targets_can_have_different_coverage(self):
        latent = gaussian_score(300.,0.,MODELS["M0"])
        measured = gaussian_score(300.,300.,MODELS["M0"])
        self.assertEqual(latent["covered95"],0.)
        self.assertEqual(measured["covered95"],1.)
        self.assertGreater(measured["width95_minutes"],latent["width95_minutes"])

    def test_convolved_gaussian_width_uses_seconds_and_quadrature_sum(self):
        result = gaussian_score(0.,120.,MODELS["M0"])
        expected = 2 * NormalDist().inv_cdf(.975) * math.hypot(60.,120.) / 60
        self.assertAlmostEqual(result["width95_minutes"],expected,places=8)


if __name__ == "__main__":
    unittest.main()
