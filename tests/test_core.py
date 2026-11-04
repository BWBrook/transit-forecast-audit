import unittest
from dataclasses import replace
from pathlib import Path
from statistics import NormalDist
from tempfile import TemporaryDirectory
import numpy as np
from transit_audit.ephemeris import LinearEphemeris, fit_linear, missing_covariance_variance_bounds
from transit_audit.scoring import score_one, interval_score, planet_balanced_mean, cluster_bootstrap_interval
from transit_audit.provenance import Timing, chronological_split, assert_published_forecast_eligible
from transit_audit.demo import run_demo


class EphemerisTests(unittest.TestCase):
    def test_exact_fit_and_analytic_variance(self):
        e = np.arange(5)
        sigma = np.full(5, 1e-3)
        fitted = fit_linear(e, 2450000.0 + 3.0 * e, sigma)
        self.assertAlmostEqual(fitted.ephemeris.period_days, 3.0)
        self.assertAlmostEqual(fitted.ephemeris.reference_epoch, 2.0)
        np.testing.assert_allclose(fitted.ephemeris.covariance_days2, np.diag([1e-6 / 5, 1e-6 / 10]))
        self.assertAlmostEqual(fitted.chi_square, 0.0)

    def test_recenter_preserves_predictions(self):
        eph = LinearEphemeris(0, 2450000, 2.0, np.array([[4e-6, -2e-8], [-2e-8, 9e-10]]))
        before = eph.predict(np.array([10, 300, 2000]))
        after = eph.recenter(800).predict(np.array([10, 300, 2000]))
        np.testing.assert_allclose(before.mean_bjd_tdb, after.mean_bjd_tdb, rtol=0, atol=1e-9)
        np.testing.assert_allclose(before.forecast_variance_days2, after.forecast_variance_days2, rtol=1e-12)

    def test_covariance_cross_term_is_used(self):
        eph = LinearEphemeris(0, 2450000, 2, np.array([[4e-6, -2e-8], [-2e-8, 9e-10]]))
        self.assertAlmostEqual(float(eph.predict(10).forecast_variance_days2), 4e-6 - 4e-7 + 9e-8)

    def test_measurement_error_convolution_and_scale(self):
        eph = LinearEphemeris(0, 2450000, 2, np.diag([1e-6, 1e-10]))
        pred = eph.predict(0, observation_sigma_days=.002, ephemeris_scale=3)
        self.assertAlmostEqual(float(pred.forecast_variance_days2), 9e-6)
        self.assertAlmostEqual(float(pred.predictive_variance_days2), 13e-6)

    def test_missing_covariance_rejected(self):
        with self.assertRaises(ValueError):
            LinearEphemeris(0, 2450000, 2, None)

    def test_invalid_covariance_rejected(self):
        with self.assertRaises(ValueError):
            LinearEphemeris(0, 2450000, 2, [[1e-6, 2e-6], [2e-6, 1e-6]])

    def test_invalid_correlation_rejected_for_unequal_variance_scales(self):
        # Correlation is 2 despite a negative eigenvalue tiny relative to T0 variance.
        with self.assertRaises(ValueError):
            LinearEphemeris(0, 2450000, 2, [[1e-6, 2e-16], [2e-16, 1e-26]])
        # A correlation of 0.5 at the same scales is valid.
        LinearEphemeris(0, 2450000, 2, [[1e-6, 5e-17], [5e-17, 1e-26]])

    def test_unknown_covariance_bounds_enclose_all_correlations(self):
        lower, upper = missing_covariance_variance_bounds(.01, .001, -8)
        for rho in np.linspace(-1, 1, 101):
            variance = .01**2 + 64 * .001**2 - 16 * rho * .01 * .001
            self.assertLessEqual(float(lower) - 1e-15, variance)
            self.assertGreaterEqual(float(upper) + 1e-15, variance)

    def test_degenerate_epochs_rejected(self):
        with self.assertRaises(ValueError):
            fit_linear([1, 1, 1], [2, 2, 2], [.1, .1, .1])

    def test_negative_uncertainty_rejected(self):
        with self.assertRaises(ValueError):
            fit_linear([1, 2, 3], [2, 4, 6], [.1, -.1, .1])


class ScoreTests(unittest.TestCase):
    def test_correct_measured_outcome_variance(self):
        scored = score_one(100.002, 100.0, 1e-6, .002)
        self.assertAlmostEqual(scored["standardized_error"], .002 / np.sqrt(5e-6), places=9)
        self.assertEqual(scored["covered_0.950000"], 1.0)

    def test_gaussian_pit_at_mean(self):
        self.assertEqual(score_one(100, 100, 1e-6, .001)["pit"], .5)

    def test_interval_score_penalizes_misses(self):
        self.assertEqual(interval_score(0, -1, 1, .1), 2)
        self.assertEqual(interval_score(2, -1, 1, .1), 22)

    def test_planet_balance_unchanged_by_repeated_identical_measurements(self):
        self.assertEqual(planet_balanced_mean([0, 1], ["a", "b"]), .5)
        self.assertEqual(planet_balanced_mean([0] * 100 + [1], ["a"] * 100 + ["b"]), .5)

    def test_log_score_uses_seconds_units(self):
        sd_days = 1 / 86400
        expected = .5 * np.log(2 * np.pi)
        self.assertAlmostEqual(score_one(0, 0, sd_days**2, 0)["negative_log_score_seconds"], expected)

    def test_bootstrap_is_deterministic(self):
        first = cluster_bootstrap_interval([0, 1, 2], ["a", "a", "b"], n_resamples=200, seed=7)
        second = cluster_bootstrap_interval([0, 1, 2], ["a", "a", "b"], n_resamples=200, seed=7)
        self.assertEqual(first, second)

    def test_host_bootstrap_keeps_planet_weighting_in_multiplanet_hosts(self):
        # Host a has two planets with mean 0; host b has one with mean 3.
        # Drawing both hosts gives the planet-balanced value 1, not the
        # host-balanced value 1.5. This occupies the central half of draws.
        interval = cluster_bootstrap_interval(
            [0, 0, 3], ["a", "a", "b"], confidence=.1, n_resamples=1000, seed=7
        )
        self.assertEqual(interval, (1.0, 1.0))

    def test_measurement_convolution_calibration_simulation(self):
        # Deterministic quantiles of the actual measured-outcome distribution.
        # Demonstrates why comparing noisy observations to latent-only intervals is wrong.
        z = np.array([NormalDist().inv_cdf((i + .5) / 1000) for i in range(1000)])
        observed = z * np.sqrt(1 + 9) / 86400
        covered = [score_one(float(y), 0, (1 / 86400)**2, 3 / 86400)["covered_0.950000"] for y in observed]
        self.assertAlmostEqual(np.mean(covered), .95)
        self.assertLess(np.mean(np.abs(observed * 86400) <= 1.96), .6)


class ProvenanceTests(unittest.TestCase):
    def timing(self, name, observed, available, exposure=None):
        return Timing(name, "p", "host", f"event-{name}", 1, 2450000., .001,
                      observed, available, "fixture", (exposure or name,))

    def test_old_observation_released_late_is_quarantined(self):
        a = self.timing("a", "2020-01-01", "2020-02-01")
        b = self.timing("b", "2020-03-01", "2021-01-01")
        c = self.timing("c", "2021-02-01", "2021-03-01")
        training, outcomes, quarantine = chronological_split([a, b, c], "2020-12-31")
        self.assertEqual([t.measurement_id for t in training], ["a"])
        self.assertEqual([t.measurement_id for t in outcomes], ["c"])
        self.assertEqual([t.measurement_id for t in quarantine], ["b"])

    def test_reused_exposure_rejected_across_split(self):
        a = self.timing("a", "2020-01-01", "2020-01-02", "same")
        b = self.timing("b", "2021-01-01", "2021-01-02", "same")
        with self.assertRaises(ValueError):
            chronological_split([a, b], "2020-12-31")

    def test_reused_exposure_rejected_within_each_split(self):
        for observed, available in (("2020-01-01", "2020-01-02"),
                                    ("2021-01-01", "2021-01-02"),
                                    ("2020-01-01", "2021-01-02")):
            with self.subTest(observed=observed, available=available):
                a = self.timing("a", observed, available, "same")
                b = self.timing("b", observed, available, "same")
                with self.assertRaises(ValueError):
                    chronological_split([a, b], "2020-12-31")

    def test_distinct_cadences_from_same_product_are_allowed(self):
        a = self.timing("a", "2020-01-01", "2020-01-02", "target:product:cadence-1")
        b = self.timing("b", "2021-01-01", "2021-01-02", "target:product:cadence-2")
        training, outcomes, quarantine = chronological_split([a, b], "2020-12-31")
        self.assertEqual((len(training), len(outcomes), len(quarantine)), (1, 1, 0))

    def test_exposure_identifiers_require_sequence_of_nonempty_strings(self):
        event = self.timing("a", "2020-01-01", "2020-01-02")
        for invalid in ("exposure", (1,), (None,), ("  ",)):
            with self.subTest(exposure_ids=invalid):
                with self.assertRaises(ValueError):
                    replace(event, exposure_ids=invalid)
        converted = replace(event, exposure_ids=["one", "two"])
        self.assertEqual(converted.exposure_ids, ("one", "two"))

    def test_preissue_outcome_rejected_even_if_after_training(self):
        event = self.timing("a", "2022-06-01", "2022-06-02")
        with self.assertRaises(ValueError):
            assert_published_forecast_eligible("2022-10-01", "2021-12-31", event, (), True)

    def test_unknown_lineage_rejected(self):
        event = self.timing("a", "2023-01-01", "2023-01-02")
        with self.assertRaises(ValueError):
            assert_published_forecast_eligible("2022-10-01", "2021-12-31", event, (), False)

    def test_lineage_requires_explicit_boolean_not_truthy_import(self):
        event = self.timing("a", "2023-01-01", "2023-01-02")
        for value in ("false", "true", 1):
            with self.subTest(lineage_verified=value):
                with self.assertRaises(ValueError):
                    assert_published_forecast_eligible("2022-10-01", "2021-12-31", event, (), value)

    def test_published_forecast_training_exposure_types_and_overlap(self):
        event = self.timing("a", "2023-01-01", "2023-01-02", "e1")
        for invalid in ("e1", None, {"e1"}, (1,), (None,), ("  ",)):
            with self.subTest(training_exposure_ids=invalid):
                with self.assertRaises(ValueError):
                    assert_published_forecast_eligible(
                        "2022-10-01", "2021-12-31", event, invalid, True
                    )
        for overlapping in (["e1"], ("e1",)):
            with self.subTest(training_exposure_ids=overlapping):
                with self.assertRaisesRegex(ValueError, "share exposures"):
                    assert_published_forecast_eligible(
                        "2022-10-01", "2021-12-31", event, overlapping, True
                    )
        # These sequences do not themselves prove independence; the caller
        # must establish it before making the explicit lineage assertion.
        for permitted in ([], (), ["other"], ("other",)):
            assert_published_forecast_eligible(
                "2022-10-01", "2021-12-31", event, permitted, True
            )

    def test_time_system_not_silently_converted(self):
        event = self.timing("a", "2020-01-01", "2020-01-02")
        with self.assertRaises(ValueError):
            replace(event, time_system="HJD_UTC")

    def test_duplicate_measurement_rejected(self):
        event = self.timing("a", "2020-01-01", "2020-01-02")
        with self.assertRaises(ValueError):
            chronological_split([event, event], "2020-12-31")

    def test_same_issue_day_not_treated_as_future(self):
        event = self.timing("a", "2022-10-01", "2022-10-02")
        with self.assertRaises(ValueError):
            assert_published_forecast_eligible("2022-10-01", "2021-12-31", event, (), True)

    def test_valid_published_forecast_passes(self):
        event = self.timing("a", "2023-01-01", "2023-01-02")
        assert_published_forecast_eligible("2022-10-01", "2021-12-31", event, ("different",), True)


class DemoTests(unittest.TestCase):
    def test_synthetic_demo_is_reproducible_and_preserves_existing_outputs(self):
        with TemporaryDirectory() as temporary:
            first = Path(temporary) / "first"
            second = Path(temporary) / "second"
            a = run_demo(first, seed=2000)
            b = run_demo(second, seed=2000)
            self.assertEqual(a, b)
            self.assertEqual(a["planets"], 24)
            self.assertEqual(a["timings"], 168)
            files = ("synthetic_scores.csv", "synthetic_summary.json")
            snapshots = {name: (first / name).read_bytes() for name in files}
            for name in files:
                self.assertEqual(snapshots[name], (second / name).read_bytes())
            with self.assertRaises(FileExistsError):
                run_demo(first, seed=999)
            for name in files:
                self.assertEqual(snapshots[name], (first / name).read_bytes())


if __name__ == "__main__":
    unittest.main()
