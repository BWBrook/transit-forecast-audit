"""Exact-oracle regressions against enumerated finite allocations."""
import itertools
import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
import d075_oracle_audit as a


def row(planet, sd, residual, accepted=True):
    return {'planet':planet,'forecast_sd_min':str(sd), 'status':'accepted' if accepted else 'edge',
            'residual_min':str(residual) if accepted else ''}


class AllocationOracleTests(unittest.TestCase):
    def test_matches_exhaustive_search_with_unequal_costs_and_missing_events(self):
        events=[]
        for i,n in enumerate((1,2,3,4,2,1)):
            events += [row(str(i), .2+.3*i, (j+1)*(i+2), accepted=i!=5)
                       for j in range(n)]
        planets=sorted({r['planet'] for r in events})
        fraction=.34
        count=math.ceil(fraction*len(planets))
        for pad in (.5,3.,15.):
            exact=a.optimal_allocation(events,pad,fraction)
            brute=max(a.direct_policy(events,set(chosen),pad)['minimum_gain']
                      for chosen in itertools.combinations(planets,count))
            self.assertAlmostEqual(exact['minimum_gain'],brute,places=13)
            self.assertEqual(len(exact['flagged_planets']),count)

    def test_largest_realised_error_ranking_need_not_maximise_capture(self):
        events=[row('A',1.,100.),row('B',1.,5.),row('C',1.,.5)]
        hindsight=a.direct_policy(events,{'A'},15.)
        exact=a.optimal_allocation(events,15.,fraction=.3)
        self.assertGreater(exact['minimum_gain'],hindsight['minimum_gain'])
        self.assertEqual(exact['flagged_planets'],['B'])

    def test_success_against_both_uses_stronger_comparator(self):
        events=[row('A',.2,2.),row('B',2.,1.),row('C',3.,3.)]
        result=a.direct_policy(events,{'A'},3.)
        self.assertAlmostEqual(result['minimum_gain'],
                               min(result['gain_vs_proportional'],result['gain_vs_additive']))
        bounds=a.ceiling_values(events)
        self.assertAlmostEqual(bounds['upper_gain_against_both_comparators'],
                               bounds['triage_upper_bound']-max(bounds['minimum_budget_proportional'],
                                                               bounds['minimum_budget_additive']))


if __name__=='__main__':unittest.main()
