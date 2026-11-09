"""Exact retrospective allocation oracle for the fixed D075 policy class.

Saved tables only. This maximises accepted-planet midpoint capture at fixed
flag count and budget, not a forecastable rule or a latent-capture policy.
"""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/d075_oracle_audit'
TABLES = {'earlier_S56_S73': ROOT/'results/t020_development/c2_candidate_events.csv',
          'inspected_2026': ROOT/'results/t020_development/longer_horizon/c2_inspected_2026_candidate_events.csv.gz',
          'pooled': ROOT/'results/t020_development/longer_horizon/c2_pooled_candidate_events.csv.gz'}
PADS = (15., 30., 60., 120., 240.)
Z = 1.959964


def read(path):
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as stream:
        return list(csv.DictReader(stream))


def population(events):
    planets = sorted({r['planet'] for r in events})
    counts = Counter(r['planet'] for r in events)
    accepted = [r for r in events if r['status'] == 'accepted']
    accepted_counts = Counter(r['planet'] for r in accepted)
    if not accepted_counts:
        raise ValueError('No accepted planets')
    base = np.array([float(r.get('baseline_half_width_min') or Z*float(r['forecast_sd_min'])) for r in events])
    a_base = np.array([float(r.get('baseline_half_width_min') or Z*float(r['forecast_sd_min'])) for r in accepted])
    error = np.array([abs(float(r['residual_min'])) for r in accepted])
    weight = np.array([1/(len(accepted_counts)*accepted_counts[r['planet']]) for r in accepted])
    return planets, counts, accepted, accepted_counts, base, a_base, error, weight


def capture_vectors(events, pad, max_cost):
    _, _, _, _, base, a_base, error, weight = population(events)
    indices = np.arange(max_cost+1)
    proportional, additive = np.empty(max_cost+1), np.empty(max_cost+1)
    for start in range(0, max_cost+1, 128):
        s = indices[start:start+128]
        proportional[start:start+len(s)] = weight @ (error[:,None] <= a_base[:,None]*(1+pad*s/base.sum()))
        additive[start:start+len(s)] = weight @ (error[:,None] <= a_base[:,None]+pad*s/len(events))
    return proportional, additive


def direct_policy(events, flagged, pad):
    _, counts, accepted, _, base, a_base, error, weight = population(events)
    cost = sum(counts[p] for p in flagged)
    triage = float(weight @ (error <= a_base+pad*np.array([r['planet'] in flagged for r in accepted])))
    proportional = float(weight @ (error <= a_base*(1+pad*cost/base.sum())))
    additive = float(weight @ (error <= a_base+pad*cost/len(events)))
    return {'triage':triage, 'proportional':proportional, 'additive':additive,
            'gain_vs_proportional':triage-proportional, 'gain_vs_additive':triage-additive,
            'minimum_gain':triage-max(proportional,additive), 'flagged_intended_events':cost,
            'scheduled_midpoint_window_minutes':float(2*(base.sum()+pad*cost))}


def optimal_allocation(events, pad, fraction=.1):
    planets, counts, accepted, accepted_counts, base, a_base, error, weight = population(events)
    k = math.ceil(fraction*len(planets))
    max_cost = sum(sorted(counts.values(), reverse=True)[:k])
    benefit = defaultdict(float)
    for row, b, err in zip(accepted, a_base, error):
        benefit[row['planet']] += (int(err <= b+pad)-int(err <= b))/accepted_counts[row['planet']]
    dp = np.full((k+1, max_cost+1), -np.inf)
    dp[0,0] = 0.
    take = np.zeros((len(planets),k+1,max_cost+1), dtype=bool)
    for i,p in enumerate(planets):
        cost = counts[p]
        for j in range(min(k,i+1),0,-1):
            candidate = dp[j-1,:max_cost+1-cost]+benefit[p]
            improves = candidate > dp[j,cost:]
            take[i,j,cost:] = improves
            dp[j,cost:] = np.maximum(dp[j,cost:],candidate)
    proportional, additive = capture_vectors(events,pad,max_cost)
    baseline = float(weight @ (error <= a_base))
    value = baseline+dp[k]/len(accepted_counts)-np.maximum(proportional,additive)
    cost = int(np.argmax(value))
    optimum = float(value[cost])
    chosen, j, s = [], k, cost
    for i in range(len(planets)-1,-1,-1):
        if take[i,j,s]:
            chosen.append(planets[i]); s -= counts[planets[i]]; j -= 1
    assert j == s == 0 and len(chosen) == k
    result = direct_policy(events,set(chosen),pad)
    assert abs(result['minimum_gain']-optimum)<1e-12
    return {'pad_min':pad, 'flag_count':k, 'accepted_planets':len(accepted_counts),
            'flagged_planets':sorted(chosen), 'baseline':baseline,
            'feasible_integer_budgets':int(np.isfinite(dp[k]).sum()),
            'objective':'maximum minimum gain against both equal-budget comparators', **result}


def ceiling_values(events):
    planets,counts,_,ac,base,_,_,_ = population(events)
    k=math.ceil(.1*len(planets))
    fewest=sorted(planets,key=lambda p:(counts[p],p))[:k]
    p=direct_policy(events,set(fewest),15.)
    baseline=direct_policy(events,set(),0.)['triage']
    upper=min(1.,baseline+k/len(ac))
    return {'intended_planets':len(planets),'accepted_planets':len(ac),'flag_count':k,
            'baseline':baseline,'triage_upper_bound':upper,
            'minimum_flagged_intended_events':sum(counts[x] for x in fewest),
            'minimum_budget_proportional':p['proportional'],'minimum_budget_additive':p['additive'],
            'upper_gain_against_weaker_comparator':upper-min(p['proportional'],p['additive']),
            'upper_gain_against_both_comparators':upper-max(p['proportional'],p['additive'])}


def reproduce_review():
    saved=json.loads((ROOT/'results/t020_review/summary.json').read_text())
    ceiling_saved=json.loads((ROOT/'results/t020_review/rule_free_ceiling.json').read_text())
    differences=[]
    for name,path in TABLES.items():
        events=read(path)
        planets=sorted({r['planet'] for r in events})
        errors=defaultdict(list)
        for r in events:
            if r['status']=='accepted':errors[r['planet']].append(abs(float(r['residual_min'])))
        mean={p:sum(errors[p])/len(errors[p]) if errors[p] else -1. for p in planets}
        flagged=set(sorted(planets,key=lambda p:-mean[p])[:math.ceil(.1*len(planets))])
        for row in saved[name]['oracle_ceiling']:
            expected=direct_policy(events,flagged,row['pad_min'])
            for k in ('triage','proportional','additive','gain_vs_proportional','gain_vs_additive'):
                differences.append(abs(round(expected[k],4)-row[k]))
        ceiling=ceiling_values(events)
        for actual, key in (('baseline','baseline'),('triage_upper_bound','triage_upper_bound'),
                            ('minimum_budget_proportional','min_budget_proportional'),
                            ('minimum_budget_additive','min_budget_additive')):
            differences.append(abs(round(ceiling[actual],4)-ceiling_saved[name][key]))
    assert max(differences)<1e-12
    return {'saved_numeric_cells_checked':len(differences),'maximum_rounded_cell_difference':max(differences),
            'interpretation':'The MAE-ranking and coarse-ceiling tables reproduce; the structural argument needs the exact allocation optimum.'}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    result={}
    reproduction=reproduce_review()
    for name,path in TABLES.items():
        events=read(path)
        result[name]={'ceiling':ceiling_values(events),'exact_oracle':[optimal_allocation(events,p) for p in PADS]}
    (OUT/'review_reproduction.json').write_text(json.dumps(reproduction,indent=2)+'\n')
    (OUT/'summary.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    inputs=[*TABLES.values(),ROOT/'scripts/t020_review.py',ROOT/'results/t020_review/rule_free_ceiling.json',
            ROOT/'results/t020_review/summary.json',ROOT/'docs/d075_scope_2026-11-09.md']
    receipt={'saved_tables_only':True,'new_photometry_or_headers_opened':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
             'output_sha256':{name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('summary.json','review_reproduction.json')},
             'objective':'exact hindsight allocation optimum for fixed q and pad grid; accepted-midpoint endpoint only',
             'limits':['Not a forecastable rule or an out-of-sample result.',
                       'Measurement noise attribution is not established by this oracle.',
                       'Unrecovered events contribute budgets, not known capture outcomes.',
                       'Flag-count/variable per-planet event counts and both comparators are respected.']}
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:{'ceiling':v['ceiling'], 'best_exact_oracle_minimum_gain':max(r['minimum_gain'] for r in v['exact_oracle'])} for k,v in result.items()}))


if __name__=='__main__':main()
