"""Claude's reciprocal review of sprint 1: tails, chronology leakage and bootstrap influence.

    .venv/bin/python scripts/review_sprint1_claude.py
"""

from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy import integrate, optimize, stats

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint1_forecast_core as c  # noqa: E402
from transit_audit.exoclock import read_mid_times  # noqa: E402

OUT = ROOT / "results" / "sprint2_review"
D = ROOT / "data" / "derived" / "sprint1"


def mixture_density(y, sf, sy, s):
    f = lambda z: stats.norm.pdf(z) * stats.norm.pdf(y, 0, np.sqrt(sy ** 2 + sf ** 2 * np.exp(s * z)))  # noqa: E731
    return integrate.quad(f, -12, 12, limit=400, epsabs=0, epsrel=1e-10)[0]


def mixture_cdf(y, sf, sy, s):
    f = lambda z: stats.norm.pdf(z) * stats.norm.cdf(y / np.sqrt(sy ** 2 + sf ** 2 * np.exp(s * z)))  # noqa: E731
    return integrate.quad(f, -12, 12, limit=400, epsabs=1e-13, epsrel=1e-11)[0]


def tails():
    rows = []
    for s in (1.0, 2.16, 2.6, 3.2):
        for ratio in (0.05, 0.3, 1.0, 3.0, 10.0):
            sf, sy = 1.0, ratio
            q975 = optimize.brentq(lambda y: mixture_cdf(y, sf, sy, s) - 0.975, 0, 1e4, xtol=1e-10)
            q84 = optimize.brentq(lambda y: mixture_cdf(y, sf, sy, s) - 0.841344746, 0, 1e4, xtol=1e-10)
            ev = [{"forecast_variance_s2": 1.0, "sigma_s": sy, "outcome_scale": 1.0, "residual_s": y}
                  for y in (0.0, 1.0, 5.0, 30.0)]
            sc = c.predictive_scores(ev, {"b": 1.0, "s_log_lambda": s}, order=384, interpolate=False)
            dens = [mixture_density(y, sf, sy, s) for y in (0.0, 1.0, 5.0, 30.0)]
            rows.append({"s": s, "ratio_sy_sf": ratio, "q975_quad": q975, "q975_core": sc["width95_minutes"][0] * 60 / 2,
                         "q975_rel_err": sc["width95_minutes"][0] * 60 / 2 / q975 - 1,
                         "q84_quad": q84,
                         "logdens_abs_err_max": float(np.max(np.abs(-sc["negative_log_score_seconds"] - np.log(dens))))})
    return rows


def chronology_leakage():
    """Chronological training events (DRC forecasts vs 2022 TESS timings) that DRC's own timing table contains."""
    drc = read_mid_times(ROOT / "data" / "raw" / "osf" / "p298n" / "all_mid_time_data.txt")
    drc_keys = {(m.planet, round(m.t_bjd_tdb, 3)) for m in drc}
    out = {}
    for exp in ("chronological", "release_transfer"):
        tr = list(csv.DictReader((D / exp / "a_1.087" / "c2" / "training_events.csv").open()))
        te = list(csv.DictReader((D / exp / "a_1.087" / "c2" / "events.csv").open()))
        for part, rows in (("train", tr), ("test", te)):
            inside = [r for r in rows if (r["planet"], round(float(r["tc_bjd_tdb"]), 3)) in drc_keys]
            out[f"{exp}|{part}"] = {"release": rows[0]["release"], "events": len(rows),
                                    "events_in_DRC_timing_table": len(inside),
                                    "planets_with_any": len({r["planet"] for r in inside}),
                                    "planets": len({r["planet"] for r in rows}),
                                    "pre_issue_events": sum(int(r["horizon_days"]) <= 0 for r in rows)}
    return out


def bootstrap_influence():
    """How the host-refit interval depends on resampling the two dominant hosts."""
    out = {}
    for exp in ("release_transfer", "chronological"):
        b = list(csv.DictReader((D / exp / "a_1.087" / "c2" / "host_refit_bootstrap.csv").open()))
        b = [r for r in b if r["method"] == "M2"]
        d = np.array([float(r["delta_is95_standardised"]) for r in b])
        out[exp] = {"replicates": len(d), "q025": float(np.quantile(d, .025)), "q975": float(np.quantile(d, .975)),
                    "fraction_above_zero": float(np.mean(d > 0)),
                    "note": "replicate host multiplicities are not stored; see leave-hosts-out below"}
        ev = list(csv.DictReader((D / exp / "a_1.087" / "c2" / "scores.csv").open()))
        by = {}
        for r in ev:
            if r["method"] in ("M0", "M2"):
                by.setdefault((r["planet"], r["host"]), {}).setdefault(r["method"], []).append(float(r["is95_standardised"]))
        planets = [(p, h, np.mean(v["M2"]) - np.mean(v["M0"])) for (p, h), v in by.items()]
        delta = np.array([x[2] for x in planets])
        hosts = np.array([x[1] for x in planets])
        order = sorted(set(hosts), key=lambda h: delta[hosts == h].sum())
        drop = {}
        for k in (0, 1, 2, 3, 5):
            keep = ~np.isin(hosts, order[:k])
            drop[f"drop_top_{k}_gain_hosts"] = {"hosts": order[:k], "delta": float(delta[keep].mean())}
        out[exp]["fixed_parameter_leave_hosts_out"] = drop
        out[exp]["fraction_planets_improved"] = float(np.mean(delta < 0))
        out[exp]["median_planet_delta"] = float(np.median(delta))
        rng = np.random.default_rng(1)
        hs = sorted(set(hosts))
        hix = np.array([hs.index(h) for h in hosts])
        top2 = [hs.index(h) for h in order[:2]]
        sims, inc = [], []
        for _ in range(20000):
            m = np.bincount(rng.integers(0, len(hs), len(hs)), minlength=len(hs))
            w = m[hix]
            sims.append(np.sum(w * delta) / w.sum())
            inc.append(int(m[top2[0]] > 0) + int(m[top2[1]] > 0))
        sims, inc = np.array(sims), np.array(inc)
        out[exp]["fixed_parameter_bootstrap"] = {
            "ci95": [float(np.quantile(sims, .025)), float(np.quantile(sims, .975))],
            "P_above_zero": float(np.mean(sims > 0)),
            "P_above_zero_given_both_top2_absent": float(np.mean(sims[inc == 0] > 0)),
            "P_above_zero_given_any_top2_present": float(np.mean(sims[inc > 0] > 0)),
            "P_both_absent": float(np.mean(inc == 0))}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"tails": tails(), "chronology": chronology_leakage(), "influence": bootstrap_influence()}
    (OUT / "claude_sprint1_review.json").write_text(json.dumps(res, indent=1, default=float) + "\n")
    for r in res["tails"]:
        print("s %.2f r %5.2f q975 quad %.4f core %.4f rel %.2e logdens err %.1e" %
              (r["s"], r["ratio_sy_sf"], r["q975_quad"], r["q975_core"], r["q975_rel_err"], r["logdens_abs_err_max"]))
    print(json.dumps(res["chronology"], indent=1))
    print(json.dumps(res["influence"], indent=1, default=float))


if __name__ == "__main__":
    main()
