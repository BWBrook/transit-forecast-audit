"""Bounded developmental triage comparison; saved authorised timings only."""
from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.special import ndtri

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / 'scripts'), str(ROOT / 'src')]
import sprint1_forecast_core as core
from transit_audit.exoclock import host_of, read_catalogue
from t018_diagnostics import conditional_summary, read_csv, write_csv

OUT = ROOT / 'results/t020_development'
FEATURES = ('forecast_sd_min', 'age_over_baseline', 'issued_line_z_rms',
            'negative_timing_count', 'last_input_age_days', 'space_fraction')
PADS = (0., 15., 30., 60., 120., 240.)
SEED, FOLDS = 2026110920, 5
Z95 = float(ndtri(.975))
INPUTS = ('results/prefreeze/attempt_ledger_development.csv.gz',
          'results/outcomes/t015v3/outcomes.csv.gz',
          'results/sprint2/freeze_candidate/roster.csv',
          'results/information_ledger/release_planets.csv',
          'data/raw/osf/p298n/catalogue_of_ephemerides.txt',
          'results/pilot_v1/covariance_completeness.csv',
          'results/prefreeze/candidate_models_core_matched.json',
          'docs/t020_development_design.md')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def drc_prediction(ephemeris, identification_time):
    n = int(round((identification_time - ephemeris.t0_bjd_tdb) / ephemeris.period_days))
    return n, ephemeris.t0_bjd_tdb + n * ephemeris.period_days


def load_events(setting):
    roster = {r['planet']: r for r in read_csv(ROOT / INPUTS[2])}
    info = {r['planet']: r for r in read_csv(ROOT / INPUTS[3]) if r['release'] == 'DRC'}
    eph = read_catalogue(ROOT / INPUTS[4])
    host_count = Counter(host_of(p) for p in eph)
    covariance = core.covariance_rows()
    windows = {r['event_id']: r for r in read_csv(ROOT / INPUTS[1])}
    if len(windows) != len(read_csv(ROOT / INPUTS[1])):
        raise ValueError('Duplicate measurement identities')
    events, exclusions = [], Counter()
    for m in read_csv(ROOT / INPUTS[0]):
        p = m['planet']
        if p not in roster:
            exclusions['outside_current_roster'] += 1
            continue
        if not 56 <= int(m['sector']) <= 73:
            exclusions['outside_S56_S73'] += 1
            continue
        if p not in eph or p not in info:
            exclusions['no_DRC_forecast_or_inputs'] += 1
            continue
        e, r = eph[p], info[p]
        if (host_count[host_of(p)] != 1 or e.period_days > 12 or
                float(roster[p]['tmag']) >= 13.5 or r['origin_release_ttv_flag'] != 'False'):
            exclusions['outside_DRC_core_metadata'] += 1
            continue
        required = ('input_baseline_days', 'last_input_bjd_tdb', 'issued_line_z_rms', 'valid_timing_rows')
        if any(not r[k] for k in required) or float(r['input_baseline_days']) <= 0:
            raise ValueError('Missing release feature: ' + p)
        id_time = float(m['drd_predicted_bjd_tdb'])
        n, pred = drc_prediction(e, id_time)
        rho = core.correlation('DRC', p, setting, covariance)
        sd = float(np.sqrt(core.forecast_variance(e.sigma_t0_days * 86400,
                                                e.sigma_period_days * 86400, n, rho))) / 60
        if not np.isfinite(sd) or sd <= 0:
            raise ValueError('Invalid forecast scale')
        age = pred - float(r['last_input_bjd_tdb'])
        sources = json.loads(r['row_source_counts'])
        w = windows.get(m['window_event_id']) if m['status'] == 'accepted' else None
        if m['status'] == 'accepted' and (not w or w['status'] != 'timed'):
            raise ValueError('Accepted ledger row has no exact measured window')
        events.append({'event_id': m['event_id'], 'planet': p, 'host': roster[p]['host'],
                       'sector': int(m['sector']), 'drd_identification_epoch': int(m['epoch']),
                       'drc_forecast_epoch': n, 'drd_identification_bjd_tdb': id_time,
                       'drc_prediction_bjd_tdb': pred,
                       'cross_release_offset_over_period': (id_time-pred)/e.period_days,
                       'covariance_setting': setting, 'forecast_sd_min': sd,
                       'age_over_baseline': age / float(r['input_baseline_days']),
                       'issued_line_z_rms': float(r['issued_line_z_rms']),
                       'negative_timing_count': -float(r['valid_timing_rows']),
                       'last_input_age_days': age,
                       'space_fraction': sources.get('space', 0) / float(r['valid_timing_rows']),
                       'status': m['status'],
                       'residual_min': (float(w['tc_bjd_tdb'])-pred)*1440 if w else None,
                       'measurement_sigma_min': float(w['sigma_s'])/60 if w else None})
    if len({e['event_id'] for e in events}) != len(events):
        raise ValueError('Duplicate intended identities')
    return events, dict(exclusions)


def planet_features(events):
    by = defaultdict(list)
    for e in events:
        by[e['planet']].append(e)
    return {p: {k: float(np.median([e[k] for e in es])) for k in FEATURES} for p, es in by.items()}


def select_flags(events, feature, q=.10):
    if feature not in FEATURES or not 0 < q <= 1:
        raise ValueError('Invalid ranking or flagged fraction')
    features = planet_features(events)
    n = int(math.ceil(q * len(features)))
    ranked = sorted(features, key=lambda p: (-features[p][feature], p))
    return set(ranked[:n])


def budget_windows(events, flagged, pad):
    if pad < 0:
        raise ValueError('Negative pad')
    base = Z95 * np.array([e['forecast_sd_min'] for e in events])
    triage = base + np.array([pad if e['planet'] in flagged else 0. for e in events])
    extra = float(np.sum(triage-base))
    proportional = base * (1 + extra / float(base.sum()))
    additive = base + extra / len(base)
    values = {'baseline': base, 'triage': triage, 'proportional': proportional, 'additive': additive}
    if not all(np.isclose(v.sum(), triage.sum(), rtol=1e-13, atol=1e-8)
               for k, v in values.items() if k != 'baseline'):
        raise AssertionError('Budget mismatch')
    return values


def evaluate(events, feature, pad, q=.10):
    flags = select_flags(events, feature, q)
    widths = budget_windows(events, flags, pad)
    rows = []
    for i, e in enumerate(events):
        row = {**e, 'selected_feature': feature, 'pad_min': pad, 'flagged': e['planet'] in flags}
        for k, v in widths.items():
            row[k+'_half_width_min'] = float(v[i])
            row[k+'_capture'] = (int(abs(e['residual_min']) <= v[i]) if e['residual_min'] is not None else None)
        for comparator in ('proportional', 'additive'):
            row['delta_'+comparator] = (row['triage_capture']-row[comparator+'_capture']
                                        if e['residual_min'] is not None else None)
        rows.append(row)
    return rows


def aggregate(rows, key):
    by = defaultdict(list)
    for row in rows:
        if row[key] is not None:
            by[row['planet']].append(row[key])
    return float(np.mean([np.mean(v) for v in by.values()])) if by else None


def select_rule(events):
    candidates = []
    for feature in FEATURES:
        for pad in PADS:
            rows = evaluate(events, feature, pad)
            gains = [aggregate(rows, 'delta_'+c) for c in ('proportional', 'additive')]
            if any(g is None for g in gains):
                raise ValueError('No accepted outcomes in training')
            candidates.append({'feature': feature, 'pad_min': pad,
                               'gain_proportional': gains[0], 'gain_additive': gains[1],
                               'minimum_gain': min(gains)})
    best = min(candidates, key=lambda r: (-r['minimum_gain'], r['pad_min'], FEATURES.index(r['feature'])))
    return best, candidates


def host_folds(events):
    hosts = np.array(sorted({e['host'] for e in events}))
    rng = np.random.default_rng(SEED)
    rng.shuffle(hosts)
    return {str(h): i % FOLDS for i, h in enumerate(hosts)}


def paired_summary(rows, comparator):
    by, hosts = defaultdict(list), {}
    for r in rows:
        if r['delta_'+comparator] is not None:
            by[r['planet']].append(r['delta_'+comparator])
            hosts[r['planet']] = r['host']
    return conditional_summary([(p, hosts[p], float(np.mean(v))) for p, v in sorted(by.items())], seed=SEED)


def completion_bounds(rows, comparator):
    by = defaultdict(list)
    for r in rows:
        if r['delta_'+comparator] is not None:
            lo = hi = r['delta_'+comparator]
        else:
            a, b = r['triage_half_width_min'], r[comparator+'_half_width_min']
            lo, hi = ((0, 0) if a == b else ((0, 1) if a > b else (-1, 0)))
        by[r['planet']].append((lo, hi))
    return [float(np.mean([np.mean([v[i] for v in values]) for values in by.values()])) for i in (0, 1)]


def ambiguity_envelope(rows, comparator):
    by = defaultdict(list)
    for r in rows:
        if r['residual_min'] is None:
            continue
        centre, sigma = r['residual_min'], r['measurement_sigma_min']
        low, high = centre-2*sigma, centre+2*sigma
        a, b = r['triage_half_width_min'], r[comparator+'_half_width_min']
        cuts = sorted({low, high, *[x for x in (-a, a, -b, b) if low <= x <= high]})
        points = cuts + [(x+y)/2 for x, y in zip(cuts, cuts[1:])]
        deltas = [int(abs(x) <= a)-int(abs(x) <= b) for x in points]
        by[r['planet']].append((min(deltas), max(deltas)))
    return [float(np.mean([np.mean([v[i] for v in values]) for values in by.values()])) for i in (0, 1)]


def summarize(rows):
    flags = {r['planet'] for r in rows if r['flagged']}
    planets = {r['planet'] for r in rows}
    accepted_planets = {r['planet'] for r in rows if r['residual_min'] is not None}
    return {'intended_events': len(rows), 'intended_planets': len(planets),
            'hosts': len({r['host'] for r in rows}),
            'accepted_events': sum(r['residual_min'] is not None for r in rows),
            'accepted_planets': len(accepted_planets), 'zero_accepted_planets': sorted(planets-accepted_planets),
            'flagged_planets': sorted(flags), 'flagged_fraction': len(flags)/len(planets),
            'recovery_by_flag': {str(flag): {'intended': sum(r['flagged'] == flag for r in rows),
                   'accepted': sum(r['flagged'] == flag and r['residual_min'] is not None for r in rows)} for flag in (False, True)},
            'capture': {k: aggregate(rows, k+'_capture') for k in ('baseline', 'triage', 'proportional', 'additive')},
            'scheduled_midpoint_window_minutes': {k: float(sum(2*r[k+'_half_width_min'] for r in rows)) for k in ('baseline', 'triage', 'proportional', 'additive')},
            'gain': {c: paired_summary(rows, c) for c in ('proportional', 'additive')},
            'all_intended_binary_completion_bounds': {c: completion_bounds(rows, c) for c in ('proportional', 'additive')},
            'accepted_plus_minus_2sigma_envelope': {c: ambiguity_envelope(rows, c) for c in ('proportional', 'additive')}}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    result, candidate_rows = {}, []
    model = json.loads((ROOT / INPUTS[6]).read_text())['models']['M2']
    m2_multiplier = model['b'] * float(core.mixture_quantiles(np.array([0.]), model['s_log_lambda'], probs=(.975,))[0, 0])
    for setting in ('c2', 'zero'):
        events, exclusions = load_events(setting)
        best, candidates = select_rule(events)
        full = evaluate(events, best['feature'], best['pad_min'])
        folds, cross, choices = host_folds(events), [], []
        for fold in range(FOLDS):
            train = [e for e in events if folds[e['host']] != fold]
            test = [e for e in events if folds[e['host']] == fold]
            selected, _ = select_rule(train)
            scored = evaluate(test, selected['feature'], selected['pad_min'])
            cross.extend([{**r, 'fold': fold} for r in scored])
            choices.append({'fold': fold, **selected, 'train_hosts': len({e['host'] for e in train}),
                            'test_hosts': len({e['host'] for e in test}),
                            'test_planets': len({e['planet'] for e in test})})
        refs = [int(abs(e['residual_min']) <= m2_multiplier*e['forecast_sd_min'])
                for e in events if e['residual_min'] is not None]
        m2rows = [{**e, 'm2_capture': int(abs(e['residual_min']) <= m2_multiplier*e['forecast_sd_min'])
                  if e['residual_min'] is not None else None} for e in events]
        result[setting] = {'selected_full_development_rule': best, 'resubstitution': summarize(full),
                           'host_crossfit': summarize(cross), 'fold_choices': choices,
                           'exclusions': exclusions, 'mapping_offsets_over_P4': sum(abs(e['cross_release_offset_over_period']) > .25 for e in events),
                           'frozen_M2_reference_capture': aggregate(m2rows, 'm2_capture'),
                           'frozen_M2_reference_minutes': sum(2*m2_multiplier*e['forecast_sd_min'] for e in events),
                           'M2_reference_is_not_independent_or_budget_matched': True}
        write_csv(OUT / (setting+'_crossfit_events.csv'), cross)
        write_csv(OUT / (setting+'_candidate_events.csv'), full)
        write_csv(OUT / (setting+'_planet_features.csv'), [{'planet': p, **r} for p, r in sorted(planet_features(events).items())])
        candidate_rows.extend([{'covariance': setting, **r} for r in candidates])
        curve = []
        for q in (.05, .10, .20):
            for pad in PADS:
                rows = evaluate(events, best['feature'], pad, q)
                curve.append({'q': q, 'pad_min': pad, 'feature': best['feature'],
                              **{'capture_'+k: aggregate(rows, k+'_capture') for k in ('baseline', 'triage', 'proportional', 'additive')},
                              **{'scheduled_minutes_'+k: sum(2*r[k+'_half_width_min'] for r in rows) for k in ('baseline', 'triage', 'proportional', 'additive')}})
        write_csv(OUT / (setting+'_capture_cost_curve.csv'), curve)
    write_csv(OUT / 'candidate_search.csv', candidate_rows)
    (OUT / 'summary.json').write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    receipt = {'development_only': True, 'S74_S97_opened': False,
               'design_commit': '6768a75', 'script_sha256': sha(__file__),
               'input_sha256': {p: sha(ROOT / p) for p in INPUTS},
               'output_sha256': {p.name: sha(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != 'receipt.json'},
               'seed': SEED, 'folds': FOLDS, 'bootstrap_draws': 10000,
               'interval_scope': 'Host resampling conditional on realised cross-fitted rules; no selection refit',
               'features_are_release_internal_only': True,
               'limits': ['C2 is reconstructed covariance, not issued posterior.',
                          'Current metadata/release-paper cohort labels need historical availability audit.',
                          'Measured-midpoint capture is not full-transit or latent capture.',
                          'No exact new-test manifest, power qualification or access authority.',
                          'Space-source fraction is the only searched source-mix direction.',
                          'q=.05/.20 curves are descriptive, not alternative selected primary fractions.']}
    (OUT / 'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps({k: {'rule': v['selected_full_development_rule'], 'crossfit_gain': v['host_crossfit']['gain']} for k, v in result.items()}))


if __name__ == '__main__':
    main()
