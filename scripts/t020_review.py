"""D075 independent review of the T020 negative development screen.

Reads Codex's saved pooled/era event tables (forecast-only budgets and
measured residuals); no photometry. Separately written from t020_*.py.

1. Describes DRC errors: |residual|, |residual|/forecast SD, measurement SD /
   forecast SD, and capture at +/-1.96 forecast SD versus +/-1.96 combined SD.
2. Oracle ceiling: rank planets by their *realised* planet-mean |residual|
   (unavailable to any real rule) and apply the same q=10% / pad grid /
   equal-budget comparators. If the oracle cannot beat both comparators, the
   endpoint cannot reward any pre-event rule in this population.
"""
import csv
import gzip
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results/t020_development"
OUT = ROOT / "results/t020_review"
Z = 1.959964
PADS = (15, 30, 60, 120, 240)
TABLES = {"earlier_S56_S73": SRC / "c2_candidate_events.csv",
          "inspected_2026": SRC / "longer_horizon/c2_inspected_2026_candidate_events.csv.gz",
          "pooled": SRC / "longer_horizon/c2_pooled_candidate_events.csv.gz"}


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as handle:
        return list(csv.DictReader(handle))


def capture(events, half):
    by_planet = defaultdict(list)
    for e, h in zip(events, half):
        if e["status"] == "accepted":
            by_planet[e["planet"]].append(abs(float(e["residual_min"])) <= h)
    return float(np.mean([np.mean(v) for v in by_planet.values()]))


def scale_to_budget(sd, budget):
    return budget / (Z * sd.sum())


def oracle(events):
    sd = np.array([float(e["forecast_sd_min"]) for e in events])
    planets = sorted({e["planet"] for e in events})
    realised = defaultdict(list)
    for e in events:
        if e["status"] == "accepted":
            realised[e["planet"]].append(abs(float(e["residual_min"])))
    score = {p: (np.mean(realised[p]) if realised[p] else -1.0) for p in planets}
    n_flag = math.ceil(0.10 * len(planets))
    flagged = set(sorted(planets, key=lambda p: -score[p])[:n_flag])
    base = Z * sd
    rows = []
    for pad in PADS:
        mask = np.array([e["planet"] in flagged for e in events])
        triage = base + pad * mask
        budget = triage.sum()
        k = scale_to_budget(sd, budget)
        a = (budget - base.sum()) / len(events)
        t, p_, ad = capture(events, triage), capture(events, k * base), capture(events, base + a)
        rows.append({"pad_min": pad, "flagged_planets": n_flag, "triage": round(t, 4), "proportional": round(p_, 4),
                     "additive": round(ad, 4), "gain_vs_proportional": round(t - p_, 4),
                     "gain_vs_additive": round(t - ad, 4), "proportional_factor": round(k, 3),
                     "additive_pad_min": round(a, 2)})
    return rows


def describe(events):
    acc = [e for e in events if e["status"] == "accepted"]
    r = np.array([abs(float(e["residual_min"])) for e in acc])
    sf = np.array([float(e["forecast_sd_min"]) for e in acc])
    sm = np.array([float(e["measurement_sigma_min"]) for e in acc])
    planets = defaultdict(list)
    for e in acc:
        planets[e["planet"]].append(abs(float(e["residual_min"])))
    worst = sorted(((max(v), p) for p, v in planets.items()), reverse=True)[:5]
    return {"intended_events": len(events), "accepted_events": len(acc), "accepted_planets": len(planets),
            "abs_residual_min_median": round(float(np.median(r)), 2),
            "abs_residual_min_p99": round(float(np.percentile(r, 99)), 2),
            "abs_residual_min_max": round(float(r.max()), 2),
            "events_over_60_min": int((r > 60).sum()), "events_over_30_min": int((r > 30).sum()),
            "forecast_sd_min_median": round(float(np.median(sf)), 2),
            "measurement_over_forecast_sd_median": round(float(np.median(sm / sf)), 3),
            "capture_forecast_sd_planet_balanced": round(capture(events, [Z * float(e["forecast_sd_min"]) for e in events]), 4),
            "capture_combined_sd_planet_balanced": round(capture(events, [Z * math.hypot(float(e["forecast_sd_min"]), float(e["measurement_sigma_min"] or 0)) for e in events]), 4),
            "event_fraction_abs_z_combined_over_3": round(float(np.mean(r / np.hypot(sf, sm) > 3)), 4),
            "worst_planets_max_abs_residual_min": [[p, round(m, 1)] for m, p in worst]}


def main():
    result = {}
    for name, path in TABLES.items():
        events = read(path)
        result[name] = {"describe": describe(events), "oracle_ceiling": oracle(events)}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "summary.json").write_text(json.dumps(result, indent=1) + "\n")
    json.dump(result, sys.stdout, indent=1)


if __name__ == "__main__" and len(sys.argv) == 1:
    main()


def drd_2026_gross():
    """Gross misses in the frozen 2026 DRD primary, and DRC membership."""
    fc = {r["event_id"]: r for r in read(ROOT / "results/final_primary/accepted_forecasts.csv")}
    drc = {line.split()[0] for line in (ROOT / "data/raw/osf/p298n/catalogue_of_ephemerides.txt").read_text().splitlines()[1:] if line.strip()}
    per = defaultdict(list)
    for o in read(ROOT / "results/final_primary/accepted_outcomes.csv"):
        f = fc[o["event_id"]]
        resid = (float(o["tc_bjd_tdb"]) - float(f["predicted_bjd_tdb"])) * 1440
        sd = math.sqrt(float(f["forecast_variance_s2"])) / 60
        per[o["planet"]].append((abs(resid), abs(resid) / sd))
    gross = {p: {"events": len(v), "max_abs_min": round(max(a for a, _ in v), 1),
                 "events_gross": sum(a > 60 and z > 3 for a, z in v), "in_DRC": p in drc}
             for p, v in per.items() if any(a > 60 and z > 3 for a, z in v)}
    over30 = sorted(((round(max(a for a, _ in v), 1), p, p in drc) for p, v in per.items()), reverse=True)[:8]
    return {"planets": len(per), "planets_in_DRC": sum(p in drc for p in per),
            "gross_miss_planets": gross, "top8_max_abs_min_planet_inDRC": over30}


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "drd2026":
    r = drd_2026_gross()
    (OUT / "drd_2026_gross_misses.json").write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps(r, indent=1))


def ceiling():
    """Rule-free bound: triage capture <= baseline + flagged/accepted planets;
    compare with the weaker comparator at the smallest possible budget
    (flag the planets with fewest intended events, 15-min pad)."""
    out = {}
    for name, path in TABLES.items():
        events = read(path)
        sd = np.array([float(e["forecast_sd_min"]) for e in events])
        base = Z * sd
        planets = sorted({e["planet"] for e in events})
        n_flag = math.ceil(0.10 * len(planets))
        count = defaultdict(int)
        for e in events:
            count[e["planet"]] += 1
        fewest = set(sorted(planets, key=lambda p: count[p])[:n_flag])
        budget = (base + 15 * np.array([e["planet"] in fewest for e in events])).sum()
        k = budget / base.sum()
        a = (budget - base.sum()) / len(events)
        accepted_planets = len({e["planet"] for e in events if e["status"] == "accepted"})
        b = capture(events, base)
        out[name] = {"baseline": round(b, 4), "triage_upper_bound": round(b + n_flag / accepted_planets, 4),
                     "min_budget_proportional": round(capture(events, k * base), 4),
                     "min_budget_additive": round(capture(events, base + a), 4)}
    return out


if __name__ == "__main__" and len(sys.argv) > 1 and sys.argv[1] == "ceiling":
    r = ceiling()
    (OUT / "rule_free_ceiling.json").write_text(json.dumps(r, indent=1) + "\n")
    print(json.dumps(r, indent=1))
