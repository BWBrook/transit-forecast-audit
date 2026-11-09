"""Read-only reproduction of D075's script outputs and bound arithmetic."""
import hashlib
import json
import itertools
import math
from pathlib import Path

import numpy as np

import t020_review as review
import d075_oracle_audit as allocation

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/d075_review_checks'


def brute_force_checks():
    rng=np.random.default_rng(2026110926)
    checked=0
    for scenario in range(3):
        events=[]
        for planet in range(7):
            for _ in range(planet%3+1):
                events.append({'planet':str(planet),'forecast_sd_min':str(rng.uniform(.1,3)),
                               'status':'accepted' if planet!=6 else 'excluded_coverage',
                               'residual_min':str(rng.uniform(-15,15)) if planet!=6 else ''})
        names=sorted({e['planet'] for e in events})
        number=math.ceil(.3*len(names))
        accepted=[e for e in events if e['status']=='accepted']
        denominator=len({e['planet'] for e in accepted})
        counts={p:sum(e['planet']==p for e in accepted) for p in names}
        for pad in (.5,3,15):
            best=-math.inf
            for chosen in itertools.combinations(names,number):
                widths=[allocation.Z*float(e['forecast_sd_min']) for e in events]
                extra=pad*sum(e['planet'] in chosen for e in events)
                triage=prop=add=0.
                for e in accepted:
                    h=allocation.Z*float(e['forecast_sd_min']);r=abs(float(e['residual_min']))
                    weight=1/(denominator*counts[e['planet']])
                    triage+=weight*int(r<=h+pad*(e['planet'] in chosen))
                    prop+=weight*int(r<=h*(1+extra/sum(widths)))
                    add+=weight*int(r<=h+extra/len(events))
                best=max(best,triage-max(prop,add))
            actual=allocation.optimal_allocation(events,pad,.3)['minimum_gain']
            assert abs(actual-best)<1e-12,(actual,best)
            checked+=1
    return checked


def main():
    inputs = [Path(review.__file__), Path(allocation.__file__), *review.TABLES.values()]
    expected_summary = json.loads((review.OUT/'summary.json').read_text())
    actual_summary = {name: {'describe': review.describe(review.read(path)),
                            'oracle_ceiling': review.oracle(review.read(path))}
                      for name,path in review.TABLES.items()}
    assert actual_summary == expected_summary
    actual_ceiling = review.ceiling()
    assert actual_ceiling == json.loads((review.OUT/'rule_free_ceiling.json').read_text())
    actual_gross = review.drd_2026_gross()
    assert json.loads(json.dumps(actual_gross)) == json.loads((review.OUT/'drd_2026_gross_misses.json').read_text())
    corrected=[]
    for name,path in review.TABLES.items():
        events=review.read(path)
        sd=np.array([float(e['forecast_sd_min']) for e in events])
        base=review.Z*sd
        planets=sorted({e['planet'] for e in events})
        accepted={e['planet'] for e in events if e['status']=='accepted'}
        count={p:sum(e['planet']==p for e in events) for p in planets}
        nflag=int(np.ceil(.10*len(planets)))
        minimum_flag_events=sum(sorted(count.values())[:nflag])
        budget=base.sum()+15*minimum_flag_events
        factor=budget/base.sum()
        additive=15*minimum_flag_events/len(events)
        b=review.capture(events,base)
        upper=min(1.,b+nflag/len(accepted))
        prop=review.capture(events,base*factor)
        add=review.capture(events,base+additive)
        corrected.append({'scope':name,'baseline':b,'loose_ceiling':upper,
                          'minimum_budget_flagged_events':minimum_flag_events,
                          'minimum_budget_proportional':prop,'minimum_budget_additive':add,
                          'stronger_comparator':max(prop,add),'weaker_comparator':min(prop,add),
                          'upper_gain_for_beating_both':upper-max(prop,add),
                          'upper_gain_over_weaker':upper-min(prop,add)})
    inputs += [review.OUT/p for p in ('summary.json','rule_free_ceiling.json','drd_2026_gross_misses.json')]
    inputs += [ROOT/'results/final_primary/accepted_forecasts.csv',ROOT/'results/final_primary/accepted_outcomes.csv',
               ROOT/'data/raw/osf/p298n/catalogue_of_ephemerides.txt']
    out={'parent_independent_bruteforce_oracle_cases':brute_force_checks(),
         'saved_outputs_reproduced_exactly':True,'original_results_mutated':False,
         'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
         'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
         'corrected_loose_ceiling':corrected,
         'hypothetical_zero_of_183_one_sided_95_binomial_upper':1-.05**(1/183),
         'hypothetical_zero_of_183_two_sided_95_CP_upper':1-.025**(1/183),
         'binomial_limit_scope':'Idealised independent equal-rate trials with complete detection, not qualified cohort or incidence inference',
         'new_photometry_or_headers_opened':False}
    OUT.mkdir(exist_ok=True)
    (OUT/'receipt.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'exact_reproduction':True,'ceiling_margins_for_both':[r['upper_gain_for_beating_both'] for r in corrected]}))


if __name__=='__main__':
    main()
