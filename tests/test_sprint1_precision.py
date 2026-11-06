import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sprint1_precision", ROOT / "scripts" / "sprint1_precision.py"
)
PRECISION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PRECISION
SPEC.loader.exec_module(PRECISION)


class Sprint1PrecisionTests(unittest.TestCase):
    def test_future_design_uses_declared_core_and_extension_only(self):
        core, core_summary = PRECISION.load_future_events({"core"})
        union, union_summary = PRECISION.load_future_events({"core", "extension"})

        self.assertEqual((core_summary["planets"], core_summary["hosts"], len(core)), (156, 156, 3107))
        self.assertEqual((union_summary["planets"], union_summary["hosts"], len(union)), (184, 175, 3399))
        self.assertEqual(union_summary["planets_by_cohort"], {"core": 156, "extension": 28})
        self.assertEqual(len({row["event_id"] for row in union}), len(union))
        self.assertFalse({row["cohort"] for row in union} - {"core", "extension"})

    def test_selected_weights_remain_planet_balanced(self):
        planet_index = np.asarray([0, 0, 1, 1, 1, 2])
        mask = np.asarray([[True, False, True, True, False, False]])
        weights, active = PRECISION.selected_weights(mask, planet_index, 3)

        self.assertEqual(active.tolist(), [2])
        self.assertAlmostEqual(weights.sum(), 1.0)
        self.assertAlmostEqual(weights[0, planet_index == 0].sum(), 0.5)
        self.assertAlmostEqual(weights[0, planet_index == 1].sum(), 0.5)
        self.assertAlmostEqual(weights[0, planet_index == 2].sum(), 0.0)

    def test_tmag_match_is_local_median_not_single_host(self):
        references = [
            {"host": f"h{index}", "tmag": float(index), "sigma_s": float(10 * index)}
            for index in range(1, 8)
        ]
        sigma, status = PRECISION.matched_sigma(4.1, references, neighbours=5)

        self.assertEqual(sigma, 40.0)
        self.assertEqual(status, "nearest_5_tmag_median")

    def test_model_half_widths_and_primary_weights_are_valid(self):
        design = PRECISION.load_development_design("release_transfer")

        self.assertAlmostEqual(design.weights.sum(), 1.0)
        self.assertTrue(np.all(design.denominator > 0))
        for method in PRECISION.METHODS:
            self.assertTrue(np.all(np.isfinite(design.half_widths[method])))
            self.assertTrue(np.all(design.half_widths[method] > 0))


if __name__ == "__main__":
    unittest.main()
