import sys
import unittest
import csv
import tempfile
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

import numpy as np
from scipy.special import ndtr
from scipy.optimize import brentq

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint1_outcome_adapter as adapter
import forecast_variance_components as variance


class ReviewAdapter(unittest.TestCase):
    def test_source_drift_cannot_produce_a_success_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            forecasts, outcomes, scores = [directory/name for name in ("forecasts.csv","outcomes.csv","scores.csv")]
            identity = {"event_id":"synthetic", "observation_id":"synthetic_obs", "planet":"p", "host":"h"}
            for path,row in [(forecasts,identity), (outcomes,{**identity,"status":"id_failed","failure_reason":"synthetic fixture","error_convention":"exoclock_reported"})]:
                with path.open("w") as handle:
                    writer=csv.DictWriter(handle,fieldnames=list(row));writer.writeheader();writer.writerow(row)
            original_digest = adapter.c.digest
            count = 0
            def drifting(path):
                nonlocal count
                if Path(path) == Path(adapter.__file__):
                    count += 1
                    return "0"*64 if count == 1 else "1"*64
                return original_digest(path)
            args = Namespace(forecasts=str(forecasts),outcomes=str(outcomes),error_convention="exoclock_reported",outcome_scale=1.,output=str(scores))
            with patch.object(adapter.c,"digest",side_effect=drifting):
                with self.assertRaisesRegex(RuntimeError,"Source/input drift"):
                    adapter.score_outcomes(args)
            self.assertFalse(scores.with_suffix(".receipt.json").exists())

    def test_scale_mixture_grid_matches_analytic_gaussian_mixture_convolution(self):
        x = np.linspace(-800, 800, 1601)
        density = .8*np.exp(-.5*(x/35)**2)/35 + .2*np.exp(-.5*((x-150)/75)**2)/75
        weights = density/density.sum()
        z, logweights = variance.quadrature(384)
        # The continuous oracle needs a convolution smooth relative to this 1-s grid.
        for vf in (10000., 1000000.):
            with self.subTest(forecast_variance=vf):
                sd = np.sqrt(vf)*np.exp(.5*2.6*z)
                def cdf(value):
                    return np.exp(logweights) @ (.8*ndtr(value/np.sqrt(sd**2+35**2))
                                                + .2*ndtr((value+150)/np.sqrt(sd**2+75**2)))
                lower, upper = [brentq(lambda v: cdf(v)-p, -1e5, 1e5) for p in (.025,.975)]
                residual = 37.
                expected = upper-lower+40*(max(lower-residual,0)+max(residual-upper,0))
                observed = adapter.grid_score(residual, vf, {"b":1.,"s_log_lambda":2.6}, (x,weights), 90.)
                self.assertAlmostEqual(observed["is95_minutes"], expected/60, delta=2e-6)

    def test_skew_grid_quantiles_match_independent_mixture_cdf(self):
        x = np.linspace(-500, 800, 2601)
        density = .8*np.exp(-.5*(x/35)**2)/35 + .2*np.exp(-.5*((x-150)/75)**2)/75
        weights = density / density.sum()
        residual, forecast_sd = 37., 41.
        score = adapter.grid_score(residual, forecast_sd**2, {"b":1., "s_log_lambda":0.}, (x,weights), 90.)
        y = np.linspace(-1000, 1000, 20001)
        cumulative = np.array([weights @ ndtr((value+x)/forecast_sd) for value in y])
        lower, upper = np.interp([.025,.975], cumulative, y)
        expected = upper-lower+40*(max(lower-residual,0)+max(residual-upper,0))
        self.assertAlmostEqual(score["is95_minutes"], expected/60, delta=2e-6)

    def test_timed_unresolved_integration_cannot_bypass_gaussian_route(self):
        required = {"event_id","observation_id","planet","host","tic","sector","camera","ccd",
                    "product","flux","file","file_sha256","data_rel","cadenceno_first","cadenceno_last",
                    "timesys","timeref","bjdrefi","bjdreff","tc_bjd_tdb","sigma_s","gauss_ok",
                    "q025_s","q1587_s","q8413_s","q975_s","posterior_grid_path","shape_group_id",
                    "loo_shift_s","id_method","id_period_d","id_period_source","id_period_source_date",
                    "coverage_window","coverage_in_transit","status","failure_reason","error_convention","rule_version"}
        row = dict.fromkeys(required, "1")
        row.update(status="timed", file_sha256="a"*64, gauss_ok="True", flags="mass_outside_fine")
        with self.assertRaisesRegex(ValueError, "Unresolved timing support"):
            adapter.validate_i1([row])


if __name__ == "__main__":
    unittest.main()
