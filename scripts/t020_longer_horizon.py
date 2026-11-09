"""Same bounded T020 search on inspected longer-horizon DRC forecasts."""
import json
import gzip
from collections import Counter
from pathlib import Path

import numpy as np

import t020_development as d

ROOT = d.ROOT
OUT = d.OUT / 'longer_horizon'
INPUTS = ('results/final_primary/terminal_ledger.csv.gz', 'results/final_extension/terminal_ledger.csv.gz',
          'results/final_primary/accepted_outcomes.csv', 'results/final_extension/accepted_outcomes.csv')


def longer_events(setting):
    roster = {r['planet']: r for r in d.read_csv(ROOT / d.INPUTS[2])}
    info = {r['planet']: r for r in d.read_csv(ROOT / d.INPUTS[3]) if r['release'] == 'DRC'}
    eph = d.read_catalogue(ROOT / d.INPUTS[4])
    host_count = Counter(d.host_of(p) for p in eph)
    covariance = d.core.covariance_rows()
    windows = {r['event_id']: r for p in INPUTS[2:] for r in d.read_csv(ROOT / p)}
    ledger = [r for p in INPUTS[:2] for r in d.read_csv(ROOT / p)]
    result, exclusions = [], Counter()
    for m in ledger:
        p = m['planet']
        if p not in roster or p not in eph or p not in info:
            exclusions['outside_roster_or_no_DRC'] += 1
            continue
        e, r = eph[p], info[p]
        if (host_count[d.host_of(p)] != 1 or e.period_days > 12 or float(roster[p]['tmag']) >= 13.5 or
                r['origin_release_ttv_flag'] != 'False'):
            exclusions['outside_DRC_core_metadata'] += 1
            continue
        required = ('input_baseline_days', 'last_input_bjd_tdb', 'issued_line_z_rms', 'valid_timing_rows')
        if any(not r[k] for k in required) or float(r['input_baseline_days']) <= 0:
            raise ValueError('Missing DRC feature')
        id_time = float(m['drd_predicted_bjd_tdb'])
        n, pred = d.drc_prediction(e, id_time)
        rho = d.core.correlation('DRC', p, setting, covariance)
        sd = float(np.sqrt(d.core.forecast_variance(e.sigma_t0_days*86400, e.sigma_period_days*86400, n, rho)))/60
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError('Invalid DRC scale')
        age, sources = pred-float(r['last_input_bjd_tdb']), json.loads(r['row_source_counts'])
        w = windows.get(m['event_id']) if m['status'] == 'accepted' else None
        if m['status'] == 'accepted' and not w:
            raise ValueError('Accepted row missing from outcome table')
        result.append({'event_id': m['event_id'], 'planet': p, 'host': roster[p]['host'],
                       'sector': int(m['sector']), 'drd_identification_epoch': int(m['forecast_epoch']),
                       'drc_forecast_epoch': n, 'drd_identification_bjd_tdb': id_time,
                       'drc_prediction_bjd_tdb': pred, 'cross_release_offset_over_period': (id_time-pred)/e.period_days,
                       'covariance_setting': setting, 'forecast_sd_min': sd,
                       'age_over_baseline': age/float(r['input_baseline_days']),
                       'issued_line_z_rms': float(r['issued_line_z_rms']),
                       'negative_timing_count': -float(r['valid_timing_rows']),
                       'last_input_age_days': age, 'space_fraction': sources.get('space',0)/float(r['valid_timing_rows']),
                       'status': m['status'], 'residual_min': (float(w['tc_bjd_tdb'])-pred)*1440 if w else None,
                       'measurement_sigma_min': float(w['sigma_s'])/60 if w else None, 'era': 'inspected_2026'})
    if len({r['event_id'] for r in result}) != len(result):
        raise ValueError('Duplicate longer-horizon opportunity')
    return result, dict(exclusions)


def run_search(events):
    best, candidates = d.select_rule(events)
    full = d.evaluate(events, best['feature'], best['pad_min'])
    folds, cross, choices = d.host_folds(events), [], []
    for fold in range(d.FOLDS):
        train = [e for e in events if folds[e['host']] != fold]
        test = [e for e in events if folds[e['host']] == fold]
        selected, _ = d.select_rule(train)
        scored = d.evaluate(test, selected['feature'], selected['pad_min'])
        cross.extend([{**r, 'fold': fold} for r in scored])
        choices.append({'fold': fold, **selected, 'train_hosts': len({e['host'] for e in train}),
                        'test_hosts': len({e['host'] for e in test})})
    gross = sorted({e['planet'] for e in events if e['residual_min'] is not None and
                    abs(e['residual_min']) > max(60, 3*e['forecast_sd_min'])})
    positive = max((r for r in candidates if r['pad_min'] > 0), key=lambda r:r['minimum_gain'])
    return {'selected_rule': best, 'best_positive_pad': positive,
            'resubstitution': d.summarize(full), 'host_crossfit': d.summarize(cross), 'fold_choices': choices,
            'gross_miss_planets': gross, 'cross_release_offsets_over_P4': sum(abs(e['cross_release_offset_over_period']) > .25 for e in events)}, candidates, full, cross


def write_events(path, rows):
    d.write_csv(path, rows)
    path.with_suffix(path.suffix+'.gz').write_bytes(gzip.compress(path.read_bytes(), mtime=0))
    path.unlink()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    summary, search = {}, []
    for setting in ('c2','zero'):
        early, _ = d.load_events(setting)
        early = [{**e,'era':'S56_S73'} for e in early]
        late, exclusions = longer_events(setting)
        for label, events in (('inspected_2026',late), ('pooled',early+late)):
            key = setting+'_'+label
            report, candidates, full, cross = run_search(events)
            report['longer_horizon_exclusions'] = exclusions
            summary[key] = report
            write_events(OUT / (key+'_candidate_events.csv'), full)
            write_events(OUT / (key+'_crossfit_events.csv'), cross)
            search.extend([{'covariance':setting,'scope':label,**r} for r in candidates])
            curve=[]
            for q in (.05,.10,.20):
                for pad in d.PADS:
                    rows=d.evaluate(events,report['selected_rule']['feature'],pad,q)
                    curve.append({'q':q,'pad_min':pad,**{'capture_'+k:d.aggregate(rows,k+'_capture') for k in ('baseline','triage','proportional','additive')},
                                  **{'scheduled_minutes_'+k:sum(2*r[k+'_half_width_min'] for r in rows) for k in ('baseline','triage','proportional','additive')}})
            d.write_csv(OUT / (key+'_capture_cost_curve.csv'),curve)
    d.write_csv(OUT / 'candidate_search.csv',search)
    (OUT / 'summary.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    paths=(*d.INPUTS,*INPUTS,'scripts/t020_development.py','scripts/t020_longer_horizon.py')
    receipt={'development_only':True,'S74_S97_opened':False,'extension_design_commit':'2e8c9e9',
             'input_sha256':{p:d.sha(ROOT / p) for p in paths},
             'output_sha256':{p.name:d.sha(p) for p in OUT.iterdir() if p.is_file() and p.name not in ('receipt.json','independent_check.json')},
             'seed':d.SEED,'folds':d.FOLDS,'bootstrap_draws':10000,
             'limits':['All outcomes already inspected; no confirmatory inference.',
                       'Same six rankings and pad grid; no new tuning dimensions.',
                       'Fold intervals condition on realised selected rules.',
                       'Gross misses concern measured times, not known latent events.',
                       'Canonical cycles map from DRD opportunities, never observed timings.']}
    (OUT / 'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:{'rule':v['selected_rule'],'crossfit':v['host_crossfit']['gain'],'gross_miss_planets':v['gross_miss_planets']} for k,v in summary.items()}))


if __name__=='__main__':
    main()
