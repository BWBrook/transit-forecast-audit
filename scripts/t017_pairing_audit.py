"""Independently verify amended T017 pair identities and D073 saved-output claims.

Uses sorted dynamic programming instead of the comparison's Hungarian solver.
Reads CSV/JSON only, including the pre-amendment CSV retained in Git.
"""

import csv, gzip, hashlib, json, subprocess
from collections import defaultdict, Counter
from functools import lru_cache
from pathlib import Path

root = Path(__file__).resolve().parents[1]
out = root/'results/independent_validation/t017_pairing_review'
out.mkdir(parents=True, exist_ok=True)
inputs = set()
def read(path):
    p = root/path
    inputs.add(p)
    with gzip.open(p, 'rt') if p.suffix == '.gz' else p.open() as h:
        return list(csv.DictReader(h))
def load(path):
    p = root/path
    inputs.add(p)
    return json.loads(p.read_text())
def optimal(ref, ind, gate):
    a = sorted(enumerate(ref), key=lambda v:v[1])
    b = sorted(enumerate(ind), key=lambda v:v[1])
    @lru_cache(None)
    def dp(i,j):
        if i == len(a) or j == len(b):
            return 0, 0., ()
        options = [dp(i+1,j), dp(i,j+1)]
        d = abs(a[i][1]-b[j][1])
        if d < gate:
            n,c,p = dp(i+1,j+1)
            options.append((n+1,c+d,((a[i][0],b[j][0]),)+p))
        return min(options, key=lambda x:(-x[0],x[1],x[2]))
    return list(dp(0,0)[2])

def main():
    refs = defaultdict(list)
    primary = read(Path('results/final_primary/accepted_outcomes.csv'))
    dev = read(Path('results/outcomes/t015v3/outcomes.csv.gz'))
    accepted = {r['window_event_id'] for r in read(Path('results/prefreeze/attempt_ledger_development.csv.gz')) if r['status']=='accepted'}
    for row in primary + [r for r in dev if r['event_id'] in accepted]:
        refs[row['planet'],int(row['sector'])].append(row)
    design = load(Path('configs/independent_validation/t017_design.json'))
    cases = defaultdict(set)
    period = {}
    for c in design['cases']:
        period[c['planet']] = c['period_hint_d']
        for p in c['products']:
            cases[c['planet'],p['sector']].add(c['category'])
    updated = read(Path('results/independent_validation/t017/timing_comparison.csv'))
    updated_set = {(r['planet'],int(r['sector']),r['flux'],r['reference_event_id'],float(r['independent_tc_bjd_tdb'])) for r in updated}
    old_blob = subprocess.check_output(['git','show','2661f82:results/independent_validation/t017/timing_comparison.csv'],cwd=root)
    old = list(csv.DictReader(old_blob.decode().splitlines()))
    old_counts = Counter((r['planet'],int(r['sector']),r['flux']) for r in old)
    new_counts = Counter((r['planet'],int(r['sector']),r['flux']) for r in updated)
    expected_set, unpaired, signals = set(), [], []
    control_large = []
    for (planet,sector), categories in sorted(cases.items()):
        result = load(Path(f'results/independent_validation/t017/{planet}_S{sector}.json'))
        ref = refs[planet,sector]
        gate = period[planet]/4
        fluxes = result.get('fluxes',{})
        for column in ('PDCSAP_FLUX','SAP_FLUX'):
            flux = fluxes.get(column,{})
            windows = flux.get('transits',[])
            timed = [w for w in windows if w.get('status')=='timed']
            matches = optimal([float(r['tc_bjd_tdb']) for r in ref], [w['tc_bjd_tdb'] for w in timed],gate)
            for i,j in matches:
                r,w = ref[i],timed[j]
                expected_set.add((planet,sector,column,r['event_id'],float(w['tc_bjd_tdb'])))
                delta = (w['tc_bjd_tdb']-float(r['tc_bjd_tdb']))*1440
                if 'seeded_control' in categories and abs(delta)>max(10,3*float(r['sigma_s'])/60):
                    control_large.append((r['event_id'],column,delta))
            for i,r in enumerate(ref):
                if i in {i for i,j in matches}: continue
                tc = float(r['tc_bjd_tdb'])
                nearby = [w for w in windows if abs(w['window_centre_btjd']+2457000-tc)<gate]
                other_column = 'SAP_FLUX' if column=='PDCSAP_FLUX' else 'PDCSAP_FLUX'
                other = [w for w in fluxes.get(other_column,{}).get('transits',[]) if w.get('status')=='timed' and abs(w['tc_bjd_tdb']-tc)<gate]
                assert len(nearby)==1, (r['event_id'],column,'window ambiguity',len(nearby))
                assert len(other)<=1, (r['event_id'],column,'other ambiguity')
                checker_delta = None
                if not other and planet in ('HR858b','TOI-157b'):
                    subdir = 'hr858' if planet=='HR858b' else 'toi157_s98'
                    checker = load(Path(f'results/independent_validation/{subdir}/summary.json'))
                    ps = [p for p in checker['comparison_with_frozen'][column]['pairs'] if abs(p['frozen_tc']-tc)<1e-7]
                    assert len(ps)==1, (r['event_id'],column,'checker missing',len(ps))
                    checker_delta = ps[0]['diff_min']
                unpaired.append({'event_id':r['event_id'],'planet':planet,'sector':sector,'flux':column,
                    'independent_status':nearby[0]['status'], 'other_route_timed':bool(other),
                    'other_route_difference_min':(other[0]['tc_bjd_tdb']-tc)*1440 if other else None,
                    'c050_checker_difference_min':checker_delta})
            if planet=='WASP-18b':
                sel = flux['signals'][flux['selected_signal']]
                for k,s in enumerate(flux['signals']):
                    if k==flux['selected_signal']: continue
                    ratio = s['period_d']/sel['period_d']
                    if abs(ratio-1)<.01:
                        signals.append({'flux':column,'period_ratio':ratio,
                            'phase':((s['epoch_btjd']-sel['epoch_btjd'])/sel['period_d'])%1,
                            'depth_ppm':s['depth']*1e6,'duration_days':s['duration_d'],
                            'target_duration_days':sel['duration_d']})
    assert expected_set==updated_set, {'missing':len(expected_set-updated_set),'extra':len(updated_set-expected_set)}
    assert len(unpaired)==25
    assert all(r['independent_status']=='insufficient_window_coverage' for r in unpaired)
    assert all(r['other_route_timed'] or r['c050_checker_difference_min'] is not None for r in unpaired)
    assert not control_large
    changes = [{'planet':p,'sector':s,'flux':f,'old_pairs':old_counts[p,s,f],'amended_pairs':new_counts[p,s,f]}
               for p,s,f in sorted(old_counts.keys() | new_counts.keys()) if old_counts[p,s,f]!=new_counts[p,s,f]]
    receipt = {
        'source_base_commit':'2661f82','amendment_commit':'506ab58',
        'independent_verification':'Sorted noncrossing dynamic programming maximizes admissible count then minimizes total distance; exact pair identities compared against amended Hungarian output.',
        'source_sha256':hashlib.sha256((root/'scripts/t017_compare.py').read_bytes()).hexdigest(),
        'audit_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'old_comparison_csv_sha256':hashlib.sha256(old_blob).hexdigest(),
        'old_pairs':len(old),'amended_pairs':len(updated), 'exact_independent_pair_set_match':True,
        'product_route_changes':changes,'remaining_unpaired_flux_route_rows':len(unpaired),
        'unpaired_status_counts':dict(Counter(r['independent_status'] for r in unpaired)),
        'all_remaining_unpaired_have_other_route_or_c050_timing':True,
        'control_large_discrepancies':control_large,'wasp18_same_period_signal_evidence':signals,
        'wasp18_interpretation':'Half-phase SAP signal is consistent with a secondary eclipse. Phase and depth alone do not independently prove astrophysical identity; PDCSAP near-phase broad feature is consistent with a phase curve or detrending residual, not uniquely one or the other.',
        'opens_photometry_or_headers':False,
        'input_sha256':{str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(inputs)},
    }
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
    (out/'unpaired_check.json').write_text(json.dumps(unpaired,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:receipt[k] for k in ['old_pairs','amended_pairs','exact_independent_pair_set_match','product_route_changes','remaining_unpaired_flux_route_rows','unpaired_status_counts','control_large_discrepancies','wasp18_same_period_signal_evidence']},indent=2))


if __name__ == "__main__":
    main()
