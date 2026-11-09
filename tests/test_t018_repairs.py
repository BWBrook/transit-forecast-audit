"""Synthetic failure modes for the post-review descriptive/benchmark contracts."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import t018_diagnostics as diagnostics
import t018_benchmark as benchmark
import t018_selection as selection
import sprint1_forecast_core as core


class T018InterpretabilityTests(unittest.TestCase):
    def test_event_imbalance_does_not_replace_equal_planet_weight(self):
        rows = ([{"planet": "a", "host": "h1", "delta": 1}] * 100
                + [{"planet": "b", "host": "h2", "delta": -1}])
        planets = diagnostics.planet_values(rows, "delta")
        result = diagnostics.conditional_summary(planets, bootstrap=20, seed=1)
        self.assertEqual(result["point"], 0)
        self.assertGreater(np.mean([r["delta"] for r in rows]), .9)

    def test_host_resampling_keeps_same_host_planets_together(self):
        planets = [("a", "shared", -10), ("b", "shared", 10)]
        result = diagnostics.conditional_summary(planets, bootstrap=20, seed=2)
        self.assertEqual(result["hosts"], 1)
        self.assertEqual(result["ci95"], [0, 0])

    def test_incomplete_pair_is_not_a_matched_comparison(self):
        with self.assertRaisesRegex(ValueError, "Unpaired"):
            diagnostics.paired_rows([{"event_id": "e", "method": "M0", "planet": "a",
                                      "host": "h", "is95_minutes": "1"}], "is95_minutes")

    def test_binary_completion_bounds_use_intended_planet_weights(self):
        ledger = ([{"planet": "a"}] * 100 + [{"planet": "b"}])
        scores = [{"planet": "a", "covered95": 1}, {"planet": "b", "covered95": 0}]
        lower, upper = diagnostics.completion_bounds(ledger, scores, "covered95")
        self.assertAlmostEqual(lower, .005)
        self.assertAlmostEqual(upper, .5)
        self.assertNotAlmostEqual(lower, 1 / 101)

    def test_precision_quantile_respects_declared_mass(self):
        self.assertEqual(selection.weighted_quantile([1., 2., 100.], [.05, .05, .90], .5), 100.)
        self.assertNotEqual(selection.weighted_quantile([1., 2., 100.], [.05, .05, .90], .5), np.median([1., 2., 100.]))

    def test_measured_time_coverage_is_not_latent_schedule_capture(self):
        event = {"forecast_variance_s2": 1., "sigma_s": 3., "outcome_scale": 1., "residual_s": 4.}
        score = core.predictive_scores([event], {"b": 1., "s_log_lambda": 0.}, order=384, interpolate=False)
        self.assertEqual(float(score["covered95"][0]), 1.)
        true_midtime = 3.
        latent_forecast_limits = (-1.95996398454, 1.95996398454)
        self.assertFalse(latent_forecast_limits[0] <= true_midtime <= latent_forecast_limits[1])
        self.assertGreater(float(score["width95_minutes"][0]) * 60,
                           latent_forecast_limits[1] - latent_forecast_limits[0])


class T018BenchmarkTests(unittest.TestCase):
    def score(self):
        row = {key: "0" for key in benchmark.METRICS}
        row.update(event_id="e", method="M0", observation_id="e", planet="a", host="h", release="DRD",
                   parameter_version="hash", shape_group_id="visit")
        return row

    def test_replay_detects_metric_or_identity_changes(self):
        original = self.score()
        self.assertEqual(max(benchmark.compare_scores([original], [original]).values()), 0.)
        changed = {**original, "is95_minutes": "0.001"}
        with self.assertRaisesRegex(RuntimeError, "tolerance"):
            benchmark.compare_scores([original], [changed])
        changed = {**original, "host": "other"}
        with self.assertRaisesRegex(RuntimeError, "metadata"):
            benchmark.compare_scores([original], [changed])

    def test_manifest_refuses_path_escape_before_read(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            (path / "SHA256.json").write_text(json.dumps({"../outside": "hash"}))
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                benchmark.verify(path)


if __name__ == "__main__":
    unittest.main()
