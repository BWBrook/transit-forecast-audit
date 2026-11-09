#!/usr/bin/env python3
"""Read-only checks of the pinned transit-forecast-audit outputs.

No project modules are imported. Gaussian convolution is independently evaluated
with adaptive quadrature. Non-Gaussian event grids are not publicly tracked;
their planet-level summaries are audited as saved results, not re-extracted.
All new bootstrap intervals are exploratory, conditional on frozen parameters.
"""
from __future__ import annotations
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.integrate import quad
from scipy.optimize import brentq
from scipy.special import ndtr
from scipy.stats import norm

PIN = '629f466a2567152047d9cd75be336d865a1d68ad'
INPUTS = [
    'results/final_primary/terminal_ledger.csv.gz',
    'results/final_primary/joint_draws.json.gz',
    'results/final_primary/evaluation_summary.json',
    'results/final_primary/descriptives.json',
    'results/final_secondaries/descriptive/planet_metrics.csv',
    'data/derived/final_primary/measured/windows.csv.gz',
    'data/derived/final_primary/measured/coverage.csv',
    'results/prefreeze/forecasts_core_draft.csv.gz',
]

def half_width(vf, sy, b, s):
    """95% predictive half-width in seconds for Gaussian measurement noise."""
    if s == 0:
        return norm.ppf(.975) * np.sqrt(b*b*vf + sy*sy)
    ratio = sy / np.sqrt(vf)
    def cdf(q):
        val, err = quad(lambda z: np.exp(-.5*z*z)/np.sqrt(2*np.pi)
                        * ndtr(q/np.sqrt(b*b*np.exp(s*z)+ratio*ratio)),
                        -12, 12, epsabs=2e-11, epsrel=2e-11, limit=150)
        return val
    upper = 2.0 * np.sqrt(b*b*np.exp(.5*s*s) + ratio*ratio)
    while cdf(upper) < .975:
        upper *= 2
    return brentq(lambda q: cdf(q)-.975, 0, upper, xtol=1e-10) * np.sqrt(vf)

def score(residual, width_half):
    return 2*width_half + 40*max(abs(residual)-width_half, 0)

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--repo', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    ap.add_argument('--skip-gaussian', action='store_true', help='Skip independent quadrature, retain aggregation checks')
    args=ap.parse_args()
    r=args.repo.resolve(); out=args.out.resolve(); out.mkdir(parents=True,exist_ok=True)
    assert r != out and r not in out.parents, 'Write review outputs outside the audited checkout'
    hashes={p:hashlib.sha256((r/p).read_bytes()).hexdigest() for p in INPUTS}
    ledger=pd.read_csv(r/INPUTS[0]); windows=pd.read_csv(r/INPUTS[5],float_precision='round_trip'); forecasts=pd.read_csv(r/INPUTS[7],float_precision='round_trip')
    planets=pd.read_csv(r/INPUTS[4]); planets=planets[(planets.analysis_set=='primary') & (planets.accepted_events>0)]
    metrics=['is95_standardised','is95_minutes','is95_forecast_normalised','covered68','covered95','width95_minutes']
    p=planets.pivot(index='planet',columns='method',values=metrics).sort_index()
    assert len(p)==151 and len(ledger)==3103
    assert ledger.event_id.is_unique and windows.event_id.is_unique and forecasts.event_id.is_unique
    accepted=ledger[ledger.status=='accepted'].copy()
    assert len(accepted)==2185 and accepted.planet.nunique()==151
    events=accepted.merge(windows, left_on='window_event_id', right_on='event_id',validate='one_to_one',suffixes=('','_window'))
    events=events.merge(forecasts[['event_id','predicted_bjd_tdb','forecast_variance_s2','M2_b','M2_s_log_lambda']],on='event_id',validate='one_to_one')
    assert len(events)==2185
    assert (events.planet==events.planet_window).all()
    events['residual_s']=(events.tc_bjd_tdb-events.predicted_bjd_tdb)*86400
    events['sigma_f_s']=np.sqrt(events.forecast_variance_s2)
    events['ratio_measurement_forecast']=events.sigma_s/events.sigma_f_s
    events['denominator_s']=np.hypot(events.sigma_s,events.sigma_f_s)
    saved=json.loads((r/INPUTS[3]).read_text())
    mappings={'is95_standardised':'planet_balanced_is95_std','is95_minutes':'planet_balanced_is95_min',
              'covered68':'planet_balanced_cov68','covered95':'planet_balanced_cov95','width95_minutes':'planet_balanced_width95_min'}
    errors={}
    for m in ['M0','M1','M2','M3']:
        for metric,key in mappings.items():
            errors[m+'/'+metric]=float(p[metric][m].mean()-saved[m][key])
    assert max(abs(v) for v in errors.values()) < 1e-10
    delta=p['is95_standardised']['M2']-p['is95_standardised']['M0']
    assert int((delta<0).sum())==40
    published=json.loads((r/INPUTS[2]).read_text())
    assert abs(delta.mean()-published['primary_delta_M2_M0'])<1e-10
    draws=json.load(gzip.open(r/INPUTS[1],'rt'))
    stored_ci=np.quantile([d['paired_delta_M2_M0'] for d in draws['draws']],[.025,.975])
    assert np.allclose(stored_ci,published['joint_refit_ci95'],rtol=0,atol=1e-10)
    # Recompute percentile endpoints, not the underlying calibration refits.
    s_draw=np.array([d['models']['M2']['s_log_lambda'] for d in draws['draws']])
    n=len(p); rng=np.random.default_rng(20261109)
    mult=rng.multinomial(n,np.full(n,1/n),size=10000)
    summary={}
    for metric in metrics:
        a=p[metric]
        summary[metric]={m:{'mean':float(a[m].mean()),'review_conditional_ci95':np.quantile(mult@a[m].to_numpy()/n,[.025,.975]).tolist()} for m in a}
        d=(a.M2-a.M0).to_numpy()
        summary[metric]['M2_minus_M0']={'mean':float(d.mean()),'review_conditional_ci95':np.quantile(mult@d/n,[.025,.975]).tolist()}
    h=events[events.planet=='HR858b'].copy()
    hr={
        'accepted_events':len(h),'residual_hours_range':(h.residual_s/3600).agg(['min','max']).tolist(),
        'residual_hours_median':float(h.residual_s.median()/3600),
        'forecast_sd_minutes_range':(h.sigma_f_s/60).agg(['min','max']).tolist(),
        'method_summaries':{m:{metric:float(p[metric].loc['HR858b',m]) for metric in metrics} for m in ['M0','M1','M2','M3']},
        'standardised_delta':float(delta.loc['HR858b']),
        'contribution_to_mean':float(delta.loc['HR858b']/n),
        'without_host_standardised_delta':float(delta.drop('HR858b').mean()),
        'without_host_raw_score':p.drop('HR858b')['is95_minutes'].mean().to_dict(),
    }
    assert all(hr['method_summaries'][m]['covered95']==0 for m in ['M0','M1','M2','M3'])
    fraction=p['is95_minutes'].loc['HR858b','M0']/(n*p['is95_minutes']['M0'].mean())
    hr['share_of_total_planet_weighted_M0_raw_score']=float(fraction)
    effect_table=pd.DataFrame({'delta_standardised':delta,'delta_raw_minutes':p['is95_minutes'].M2-p['is95_minutes'].M0,
                              'baseline_95_coverage':p['covered95'].M0,'calibrated_95_coverage':p['covered95'].M2,
                              'baseline_95_width_minutes':p['width95_minutes'].M0,'calibrated_95_width_minutes':p['width95_minutes'].M2})
    effect_table.sort_values('delta_standardised').to_csv(out/'planet_effects_review.csv')
    h[['event_id','sector','forecast_epoch','tc_bjd_tdb','predicted_bjd_tdb','residual_s','sigma_f_s','sigma_s','gauss_ok','t14_min']].to_csv(out/'hr858b_review.csv',index=False)
    gauss_result={'ran':not args.skip_gaussian}
    if not args.skip_gaussian:
        g=events[events.gauss_ok.astype(str).str.lower().isin(['true','1'])].copy()
        rows=[]
        for e in g.itertuples():
            for m in ['M0','M2']:
                q=half_width(e.forecast_variance_s2,e.sigma_s,1.0,0.0 if m=='M0' else e.M2_s_log_lambda)
                raw=score(e.residual_s,q)
                rows.append({'event_id':e.event_id,'planet':e.planet,'method':m,'is95_standardised':raw/e.denominator_s,
                             'is95_minutes':raw/60,'covered95':float(abs(e.residual_s)<=q),'width95_minutes':2*q/60,
                             'halfwidth95_seconds':q})
        gscore=pd.DataFrame(rows);gscore.to_csv(out/'independent_gaussian_scores.csv.gz',index=False,compression='gzip')
        ng=events[~events.index.isin(g.index)].groupby('planet').size()
        complete=sorted(set(g.planet)-set(ng.index))
        actual=gscore[gscore.planet.isin(complete)].groupby(['planet','method']).mean(numeric_only=True)
        checks={}
        for metric in ['is95_standardised','is95_minutes','covered95','width95_minutes']:
            ds=[]
            for planet in complete:
                for m in ['M0','M2']:
                    ds.append(actual.loc[(planet,m),metric]-p[metric].loc[planet,m])
            checks[metric+'_max_abs_diff']=float(np.max(np.abs(ds)))
        assert checks['is95_standardised_max_abs_diff']<1e-6
        assert checks['covered95_max_abs_diff']<1e-14
        gauss_result.update({'events_recomputed':len(g),'planets_with_only_gaussian_accepted_events':len(complete),'saved_planet_metric_comparison':checks,
                            'method':'Independent adaptive quadrature on [-12,12] in standard-normal mixing variable; root solving for .975 quantile; closed-form M0.',
                            'non_gaussian_grids_recomputed':False})
    out_json={
        'pin':PIN,'scope':'Read-only saved-output verification plus independent Gaussian-event score calculation. No raw-photometry extraction or 2000-refit rerun.',
        'new_analyses_status':'Exploratory review diagnostics; original frozen primary remains unchanged. New intervals use fixed parameters and multinomial host multiplicities.',
        'input_sha256':hashes,'terminal_counts':ledger.status.value_counts().to_dict(),
        'counts':{'manifest':len(ledger),'accepted_events':len(accepted),'accepted_planets':len(p),'non_gaussian_events':int((events.gauss_ok.astype(str).str.lower()=='false').sum())},
        'max_saved_aggregate_error':max(abs(v) for v in errors.values()),'primary_delta':float(delta.mean()),
        'stored_joint_ci95_recomputed':stored_ci.tolist(),'stored_joint_s_ci95':np.quantile(s_draw,[.025,.975]).tolist(),
        'planet_count_improved':int((delta<0).sum()),'median_delta':float(delta.median()),
        'summary':summary,'HR858b':hr,'measurement_forecast_sigma_ratio_event_quantiles':events.ratio_measurement_forecast.quantile([.25,.5,.75,.95]).to_dict(),
        'independent_gaussian_check':gauss_result,
        'limitations':['No public per-event score table or likelihood grids in this snapshot.',
                       'Stored-draw quantiles checked; original 2000 calibration refits not rerun.',
                       'Input tables are project products; no independent raw-light-curve identity validation.']}
    (out/'review_check_results.json').write_text(json.dumps(out_json,indent=2,allow_nan=False)+'\n')
    print(json.dumps({'status':'passed','primary_delta':out_json['primary_delta'],'stored_joint_ci95':stored_ci.tolist(),
                      'gaussian_check':gauss_result,'report':str(out/'review_check_results.json')},indent=2))

if __name__=='__main__':
    main()
