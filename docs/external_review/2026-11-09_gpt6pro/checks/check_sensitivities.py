#!/usr/bin/env python3
"""Reaggregate saved sensitivity results; do not refit or change the primary test."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

def main():
    a=argparse.ArgumentParser();a.add_argument('--repo',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a=a.parse_args()
    paths=['results/final_secondaries/sensitivities/per_planet.csv','results/final_secondaries/sensitivities/summary.json']
    p=pd.read_csv(a.repo/paths[0],float_precision='round_trip');s=json.loads((a.repo/paths[1]).read_text())
    rows=[]
    for c in s['cases']:
        g=p[p['case']==c['case']];d=g.delta_M2_minus_M0.to_numpy()
        err=float(d.mean()-c['delta_M2_minus_M0_standardised'])
        assert abs(err)<1e-10 and len(g)==c['evaluation_planets']
        assert int(g.accepted_events.sum())==c['evaluation_accepted_events']
        for m in ['M0','M1','M2','M3']:
            assert abs(g[m+'_is95_standardised'].mean()-c['metrics_equal_planet'][m]['is95_standardised'])<1e-10
        lo,hi=c['conditional_fixed_scenario_fit_ci95']['M2']
        rows.append({'case':c['case'],'planets':len(g),'events':int(g.accepted_events.sum()),'delta_reaggregated':float(d.mean()),
                     'difference_from_summary':err,'saved_conditional_interval':[lo,hi],
                     'saved_interval_spans_zero':bool(lo<=0<=hi)})
    out={'scope':'Independent saved-table arithmetic only. Conditional scenario intervals read, not regenerated; calibration fits not rerun.',
         'pin':'629f466a2567152047d9cd75be336d865a1d68ad',
         'input_sha256':{p:hashlib.sha256((a.repo/p).read_bytes()).hexdigest() for p in paths},'cases':rows,
         'delta_range':[min(c['delta_reaggregated'] for c in rows),max(c['delta_reaggregated'] for c in rows)]}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'passed','cases':len(rows),'delta_range':out['delta_range'],'all_saved_intervals_span_zero':all(r['saved_interval_spans_zero'] for r in rows)}))

if __name__=='__main__':main()
