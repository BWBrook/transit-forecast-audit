"""Historical gap-grouped local scatter diagnostic (development).

Consecutive gaps <=20 days can chain across much longer intervals; these are
not established TESS visits. The fixed DRD period uses the scored outcomes.
Reported leverage-adjusted residual RMS is not a pure measurement-error scale
or sqrt(chi2/dof). Preserve this first-turn calculation for reproduction; use
review_measurement_diagnostic.py for capped-span and local-slope sensitivities.
See D022 and docs/independent_review.md for the corrected interpretation.
"""
import csv
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_table5 import load  # noqa: E402


def visits(events, gap_days=20.0):
    events = sorted(events, key=lambda m: m.t_bjd_tdb)
    group = [events[0]]
    for m in events[1:]:
        if m.t_bjd_tdb - group[-1].t_bjd_tdb > gap_days:
            yield group
            group = []
        group.append(m)
    yield group


def main():
    eph, tess, flags = load()
    D = eph["DRD"]
    by = {}
    for m in tess:
        if m.planet in D and m.planet not in flags["DRD"]:
            by.setdefault(m.planet, []).append(m)
    rows = []
    for p, evs in by.items():
        P = D[p].period_days
        for g in visits(evs):
            if len(g) < 3:
                continue
            t = np.array([m.t_bjd_tdb for m in g])
            s = np.array([m.sigma_days for m in g])
            n = np.round((t - t[0]) / P)
            x = t - n * P
            w = 1 / s**2
            mu = np.sum(w * x) / np.sum(w)
            for si, ri in zip(s, (x - mu) / s):
                rows.append((p, len(g), si * 1440, ri, np.sqrt(1 - (1 / si**2) / np.sum(w))))
    s_min = np.array([r[2] for r in rows])
    zr = np.array([r[3] / r[4] for r in rows])
    out = []
    edges = [0, 0.5, 1, 2, 4, np.inf]
    for lo, hi in [(0, np.inf)] + list(zip(edges[:-1], edges[1:])):
        k = (s_min >= lo) & (s_min < hi)
        if k.sum() < 10:
            continue
        z = zr[k]
        out.append({"sigma_tmid_min_bin": f"[{lo},{hi})", "n_events": int(k.sum()),
                    "planets": len({rows[i][0] for i in np.flatnonzero(k)}),
                    "rms_standardised": round(float(np.sqrt(np.mean(z**2))), 3),
                    "frac_abs_lt_1": round(float(np.mean(np.abs(z) < 1)), 3),
                    "frac_abs_lt_3": round(float(np.mean(np.abs(z) < 3)), 4),
                    "median_abs_over_0.6745": round(float(np.median(np.abs(z)) / 0.6745), 3)})
    path = ROOT / "results" / "pilot_v1" / "tess_measurement_calibration.csv"
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for r in out:
        print(r)


if __name__ == "__main__":
    main()
