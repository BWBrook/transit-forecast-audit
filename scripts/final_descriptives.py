"""Post-unblinding descriptive summary of a final scores.csv (D065): per-model planet-balanced IS95,
coverage and width, plus the declared secondary diagnostics fraction of planets improved and median
planet delta (M2 - M0). Descriptive only; the verdict is the frozen evaluate decision.

    .venv/bin/python scripts/final_descriptives.py results/final_primary/scores.csv > results/final_primary/descriptives.json
"""
import csv, sys, json, collections, numpy as np
rows = list(csv.DictReader(open(sys.argv[1])))
by = collections.defaultdict(lambda: collections.defaultdict(list))
for r in rows:
    by[r["method"]][r["planet"]].append(r)
out = {}
for m in sorted(by):
    pl = by[m]
    def pmean(k): return float(np.mean([np.mean([float(r[k]) for r in v]) for v in pl.values()]))
    out[m] = {"planets": len(pl), "events": sum(map(len, pl.values())),
              "planet_balanced_is95_std": pmean("is95_standardised"),
              "planet_balanced_is95_min": pmean("is95_minutes"),
              "planet_balanced_cov68": pmean("covered68"), "planet_balanced_cov95": pmean("covered95"),
              "planet_balanced_width95_min": pmean("width95_minutes"),
              "event_cov95": float(np.mean([float(r["covered95"]) for v in pl.values() for r in v]))}
d = {p: np.mean([float(r["is95_standardised"]) for r in by["M2"][p]]) - np.mean([float(r["is95_standardised"]) for r in by["M0"][p]]) for p in by["M0"]}
dv = np.array(list(d.values()))
out["M2_minus_M0_planets"] = {"mean": float(dv.mean()), "median": float(np.median(dv)), "fraction_improved": float((dv < 0).mean()), "n": len(dv)}
print(json.dumps(out, indent=1))
