import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import t020_development as t


def event(planet, host, sd, measured=True):
    return {'planet': planet, 'host': host, 'forecast_sd_min': sd,
            'age_over_baseline': sd, 'issued_line_z_rms': sd,
            'negative_timing_count': -10., 'last_input_age_days': sd,
            'space_fraction': .2, 'residual_min': 100. if measured else None,
            'measurement_sigma_min': 2. if measured else None}


class DevelopmentContractTests(unittest.TestCase):
    def test_budget_includes_unrecovered_opportunities(self):
        rows = [event('a', 'a', 1.), event('b', 'b', 10., False), event('b', 'b', 10., False)]
        values = t.budget_windows(rows, {'b'}, 30.)
        self.assertAlmostEqual(values['triage'].sum()-values['baseline'].sum(), 60.)
        self.assertAlmostEqual(values['additive'][0]-values['baseline'][0], 20.)
        for k in ('proportional', 'additive'):
            self.assertAlmostEqual(values[k].sum(), values['triage'].sum())

    def test_ranking_uses_fixed_population_not_outcomes(self):
        rows = [event(str(i), str(i), i+1.) for i in range(11)]
        flags = t.select_flags(rows, 'forecast_sd_min')
        self.assertEqual(flags, {'9', '10'})
        for row in rows:
            row['residual_min'] = None
        self.assertEqual(flags, t.select_flags(rows, 'forecast_sd_min'))

    def test_host_split_does_not_separate_planets(self):
        rows = [event('a', 'shared', 1.), event('b', 'shared', 1.), event('c', 'other', 1.)]
        fold = t.host_folds(rows)
        self.assertEqual(len(fold), 2)
        self.assertEqual(fold, t.host_folds(rows))

    def test_missing_nested_capture_bounds_use_intended_denominator(self):
        rows = t.evaluate([event('a', 'a', 1.), event('b', 'b', 5., False)], 'forecast_sd_min', 60., .5)
        self.assertEqual(t.completion_bounds(rows, 'additive'), [0., .5])
        rows = t.evaluate([event('a', 'a', 1., False), event('b', 'b', 5.)], 'forecast_sd_min', 60., .5)
        self.assertEqual(t.completion_bounds(rows, 'additive'), [-.5, 0.])

    def test_cross_release_epoch_is_assigned_from_identification_reference(self):
        e = SimpleNamespace(t0_bjd_tdb=100., period_days=3.)
        epoch, prediction = t.drc_prediction(e, 131.)
        self.assertEqual((epoch, prediction), (10, 130.))


if __name__ == '__main__':
    unittest.main()
