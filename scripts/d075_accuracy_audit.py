"""Independent saved-table accuracy/calibration audit; no photometry or headers."""
import csv
import gzip
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/d075_accuracy_audit'
Z95 = NormalDist().inv_cdf(.975)
INPUTS = ['results/final_primary/accepted_outcomes.csv',
          'results/final_primary/accepted_forecasts.csv',
          'results/final_primary/scores.csv',
          'results/final_primary/evaluation_summary.json',
          'results/final_primary/terminal_ledger.csv.gz',
          'results/t020_development/c2_candidate_events.csv',
          'results/t020_development/longer_horizon/c2_inspected_2026_candidate_events.csv.gz',
          'results/t020_development/longer_horizon/c2_pooled_candidate_events.csv.gz',
          'results/revision_stage0/interpretability/coverage_vs_nominal.csv',
          'results/information_ledger/release_planets.csv',
          'results/d073_s105_rescore/summary.csv',
          'results/prefreeze/forecasts_core_draft.csv.gz']


def read(path):
    path = Path(path)
    with (gzip.open(path, 'rt') if path.suffix == '.gz' else path.open()) as h:
        return list(csv.DictReader(h))


def balanced_mean(rows, key):
    by = defaultdict(list)
    for r in rows:
        by[r['planet']].append(float(r[key]))
    return float(np.mean([np.mean(v) for v in by.values()]))


def balanced_median(rows, key):
    counts = Counter(r['planet'] for r in rows)
    ordered = sorted((float(r[key]), 1/len(counts)/counts[r['planet']]) for r in rows)
    acc = 0.
    for v, w in ordered:
        acc += w
        if acc >= .5:
            return v
    raise AssertionError('Median mass missing')


def error_description(rows):
    by = defaultdict(list)
    for r in rows:
        by[r['planet']].append(float(r['absolute_error_min']))
    maxima = sorted([(max(v), p) for p, v in by.items()], reverse=True)
    a = [float(r['absolute_error_min']) for r in rows]
    return {'events': len(rows), 'planets': len(by),
            'event_weighted_median_absolute_error_min': float(np.median(a)),
            'equal_planet_mass_median_absolute_error_min': balanced_median(rows, 'absolute_error_min'),
            'median_of_planet_median_absolute_errors_min': float(np.median([np.median(v) for v in by.values()])),
            'event_p99_absolute_error_min': float(np.quantile(a, .99)),
            'maximum_absolute_error_min': max(a),
            'top_planet_maxima_min': [{'planet': p, 'maximum': v} for v, p in maxima[:8]],
            'planets_all_accepted_within_26_min': sum(v <= 26 for v, _ in maxima),
            'planets_all_accepted_within_26_4_min': sum(v <= 26.4 for v, _ in maxima),
            'events_over_60_min': sum(v > 60 for v in a)}


def main():
    forecasts = {r['event_id']: r for r in read(ROOT / INPUTS[1])}
    outcomes = read(ROOT / INPUTS[0])
    assert len({r['event_id'] for r in outcomes}) == len(outcomes)
    drd = []
    for o in outcomes:
        f = forecasts[o['event_id']]
        drd.append({'planet': o['planet'], 'absolute_error_min': abs(float(o['tc_bjd_tdb'])-float(f['predicted_bjd_tdb']))*1440,
                    'forecast_sd_min': float(f['forecast_variance_s2'])**.5/60,
                    'measurement_sigma_min': float(o['sigma_s'])/60})
    result = {'DRD_2026_accepted': error_description(drd), 'DRC_slices': {}}
    all_drd_forecasts = read(ROOT / INPUTS[11])
    assert len(all_drd_forecasts) == 3103
    for pad in (0, 1, 2, 3):
        for r in drd:
            r['capture'] = int(r['absolute_error_min'] <= Z95*r['forecast_sd_min']+pad)
        result['DRD_2026_accepted']['uniform_'+str(pad)+'min_measured_capture'] = balanced_mean(drd,'capture')
        result['DRD_2026_accepted']['uniform_'+str(pad)+'min_all_intended_midpoint_window_minutes'] = float(sum(2*(Z95*(float(f['forecast_variance_s2'])**.5)/60+pad) for f in all_drd_forecasts))
    for name, path in zip(('earlier', '2026', 'pooled'), INPUTS[5:8]):
        intended = read(ROOT / path)
        accepted = [{**r, 'absolute_error_min': abs(float(r['residual_min']))} for r in intended if r['status'] == 'accepted']
        ds = error_description(accepted)
        ds.update(intended_events=len(intended), intended_planets=len({r['planet'] for r in intended}),
                  forecast_sd_event_median_min=float(np.median([float(r['forecast_sd_min']) for r in accepted])),
                  measurement_sigma_over_forecast_event_median=float(np.median([float(r['measurement_sigma_min'])/float(r['forecast_sd_min']) for r in accepted])))
        for pad in (0, 1, 2, 3):
            for r in accepted:
                r['capture'] = int(r['absolute_error_min'] <= Z95*float(r['forecast_sd_min'])+pad)
            ds['uniform_'+str(pad)+'min_measured_capture'] = balanced_mean(accepted, 'capture')
            ds['uniform_'+str(pad)+'min_all_intended_midpoint_window_minutes'] = float(sum(2*(Z95*float(r['forecast_sd_min'])+pad) for r in intended))
        for r in accepted:
            r['capture'] = int(r['absolute_error_min'] <= Z95*np.hypot(float(r['forecast_sd_min']),float(r['measurement_sigma_min'])))
        ds['combined_sigma_gaussian_surrogate_measured_capture'] = balanced_mean(accepted, 'capture')
        result['DRC_slices'][name] = ds
    scores = read(ROOT / INPUTS[2])
    model = {}
    for method in ('M0','M2'):
        rows = [r for r in scores if r['method']==method]
        model[method] = {'coverage95_planet_balanced': balanced_mean(rows,'covered95'),
                         'coverage95_event_weighted': float(np.mean([float(r['covered95']) for r in rows])),
                         'mean_width95_planet_balanced_min': balanced_mean(rows,'width95_minutes')}
    model['M2_to_M0_ratio_of_mean_widths'] = model['M2']['mean_width95_planet_balanced_min']/model['M0']['mean_width95_planet_balanced_min']
    model['M0_covariance_metadata'] = dict(Counter((r['covariance_setting']+'; '+r['rho_source']) for r in forecasts.values()))
    ci = read(ROOT / INPUTS[8])
    model['conditional_coverage_ci95'] = {r['method']:[float(r['ci95_lower']),float(r['ci95_upper'])] for r in ci if r['set']=='primary' and float(r['nominal'])==.95 and r['method'] in ('M0','M2')}
    result['coverage_width'] = model
    ledger = read(ROOT / INPUTS[4])
    result['selection'] = {'intended_planets': len({r['planet'] for r in ledger}), 'intended_events': len(ledger),
                           'accepted_planets': len({r['planet'] for r in ledger if r['status']=='accepted'}),
                           'terminal_status_counts':dict(Counter(r['status'] for r in ledger)),
                           'zero_accepted_planets':sorted({r['planet'] for r in ledger}-{r['planet'] for r in ledger if r['status']=='accepted'})}
    inputs = read(ROOT / INPUTS[9])
    result['HR858_named_release_membership'] = {release:any(r['release']==release and r['planet']=='HR858b' for r in inputs) for release in ('DRB','DRC','DRD')}
    result['HR858_DRD_inputs'] = next(r for r in inputs if r['release']=='DRD' and r['planet']=='HR858b')
    s105 = next(r for r in read(ROOT / INPUTS[10]) if r['scenario']=='shift_and_width' and r['scope']=='primary' and r['metric']=='is95_standardised' and r['method']=='M2_minus_M0')
    result['S105_CI_scope'] = {'original_joint95':json.loads((ROOT / INPUTS[3]).read_text())['joint_refit_ci95'],
                              'perturbed_fixed_fit_conditional95':[float(s105['ci95_lower']),float(s105['ci95_upper'])],
                              'warning':'Different uncertainty scopes; do not present perturbed CI as recomputed primary joint interval.'}
    OUT.mkdir(exist_ok=True)
    (OUT / 'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    receipt = {'raw_photometry_or_headers_opened':False,'S74_S97_accessed':False,
               'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               'input_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS},
               'output_sha256':{'audit.json':hashlib.sha256((OUT/'audit.json').read_bytes()).hexdigest()}}
    (OUT/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({'DRD':result['DRD_2026_accepted'],'coverage':model,'DRC':result['DRC_slices']},indent=1))


if __name__=='__main__':
    main()
