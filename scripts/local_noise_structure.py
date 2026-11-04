"""Is the local TESS excess scatter multiplicative (error-bar scale) or additive (jitter)?

Development material only (D014); no light curves. Uses Codex's span-capped
groups (D022) and fits, by exact REML over all groups jointly,
    Var(e_i) = a^2 sigma_i^2 + tau^2,
with a per-group intercept and optionally a local slope. A pure error-bar scale
and white latent jitter give the same variance only when sigma is constant within
and across groups; TESS sigma spans more than an order of magnitude, so the two
predict different dependence of standardised scatter on sigma. Neither model
separates measurement error from jitter whose amplitude happens to scale with
sigma, and the catalogue's neighbour-agreement filter conditions the sample.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_table5 import load  # noqa: E402
from review_measurement_diagnostic import groups  # noqa: E402

MIN = 1440.0


def build(events, eph, flags, slope):
    by_planet = {}
    for e in events:
        if e.planet in eph and e.planet not in flags:
            by_planet.setdefault(e.planet, []).append(e)
    out = []
    for planet, es in sorted(by_planet.items()):
        for g in groups(es, 20.0):
            if len(g) < 3:
                continue
            t = np.array([m.t_bjd_tdb for m in g])
            s = np.array([m.sigma_days for m in g]) * MIN
            n = np.rint((t - t[0]) / eph[planet].period_days)
            y = ((t - t[0]) - n * eph[planet].period_days) * MIN
            y -= y.mean()
            X = np.column_stack([np.ones(len(t)), n - n.mean()]) if slope else np.ones((len(t), 1))
            out.append((planet, y, s, X))
    return out


def neg_reml(theta, data, fix_a=None, fix_tau=None):
    a = np.exp(theta[0]) if fix_a is None else fix_a
    tau = (np.exp(theta[-1]) if fix_tau is None else fix_tau)
    total = 0.0
    for _, y, s, X in data:
        v = a * a * s * s + tau * tau
        w = 1.0 / v
        xtwx = X.T @ (X * w[:, None])
        beta = np.linalg.solve(xtwx, X.T @ (w * y))
        r = y - X @ beta
        total += np.sum(np.log(v)) + np.linalg.slogdet(xtwx)[1] + np.sum(w * r * r)
    return 0.5 * total


def fit(data):
    m_a = minimize(lambda th: neg_reml(th, data, fix_tau=0.0), [0.1], method="Nelder-Mead")
    m_t = minimize(lambda th: neg_reml(th, data, fix_a=1.0), [np.log(0.3)], method="Nelder-Mead")
    m_b = minimize(lambda th: neg_reml(th, data), [0.05, np.log(0.2)], method="Nelder-Mead",
                   options={"xatol": 1e-5, "fatol": 1e-5})
    null = neg_reml([0.0], data, fix_tau=0.0)
    return {
        "null_a1_tau0": {"a": 1.0, "tau_min": 0.0, "nll": null},
        "scale_only": {"a": float(np.exp(m_a.x[0])), "tau_min": 0.0, "nll": float(m_a.fun)},
        "jitter_only": {"a": 1.0, "tau_min": float(np.exp(m_t.x[0])), "nll": float(m_t.fun)},
        "scale_plus_jitter": {"a": float(np.exp(m_b.x[0])), "tau_min": float(np.exp(m_b.x[1])),
                              "nll": float(m_b.fun)},
    }


def binned(data, a, tau, bins=6):
    """Leverage-corrected standardised residual RMS by sigma quantile, under (a, tau)."""
    rows = []
    for _, y, s, X in data:
        w = 1.0 / s**2
        q, _ = np.linalg.qr(X * np.sqrt(w)[:, None], mode="reduced")
        r = y * np.sqrt(w) - q @ (q.T @ (y * np.sqrt(w)))
        h = np.sum(q * q, axis=1)
        ok = 1 - h > 1e-10
        for si, zi in zip(s[ok], (r[ok] / np.sqrt(1 - h[ok]))):
            rows.append((si, zi))
    s, z = np.array(rows).T
    edges = np.quantile(s, np.linspace(0, 1, bins + 1))
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (s >= lo) & (s <= hi)
        sm = float(np.median(s[m]))
        out.append({"sigma_lo_min": round(lo, 4), "sigma_hi_min": round(hi, 4), "events": int(m.sum()),
                    "median_sigma_min": round(sm, 4),
                    "rms_z_quoted_sigma": round(float(np.sqrt(np.mean(z[m] ** 2))), 4),
                    "pred_scale_only": round(a, 4),
                    "pred_jitter_only": round(float(np.sqrt(1 + tau**2 / sm**2)), 4)})
    return out


def planet_bootstrap(data, n_boot, seed):
    rng = np.random.default_rng(seed)
    planets = sorted({d[0] for d in data})
    idx = {p: [i for i, d in enumerate(data) if d[0] == p] for p in planets}
    est = []
    for _ in range(n_boot):
        pick = rng.choice(len(planets), len(planets), replace=True)
        sample = [data[i] for k in pick for i in idx[planets[k]]]
        m = minimize(lambda th: neg_reml(th, sample), [0.05, np.log(0.2)], method="Nelder-Mead")
        est.append((np.exp(m.x[0]), np.exp(m.x[1])))
    return np.array(est)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "pilot_v1" / "local_noise"))
    ap.add_argument("--bootstrap", type=int, default=200)
    args = ap.parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    eph, tess, flags = load()
    if any(e.tess_date > "2024-01-03" for e in tess):
        raise ValueError("outcome beyond inspected development era")
    summary, bins_rows = {}, []
    for slope in (False, True):
        key = "local_linear" if slope else "local_mean"
        data = build(tess, eph["DRD"], flags["DRD"], slope)
        res = fit(data)
        b = res["scale_plus_jitter"]
        res["lr_jitter_given_scale"] = 2 * (res["scale_only"]["nll"] - b["nll"])
        res["lr_scale_given_jitter"] = 2 * (res["jitter_only"]["nll"] - b["nll"])
        res["groups"] = len(data)
        res["events"] = int(sum(len(d[1]) for d in data))
        res["planets"] = len({d[0] for d in data})
        res["sigma_quantiles_min"] = [round(float(q), 4) for q in
                                      np.quantile(np.concatenate([d[2] for d in data]), [0, .1, .5, .9, 1])]
        if slope and args.bootstrap:
            bs = planet_bootstrap(data, args.bootstrap, 20261105)
            res["planet_bootstrap"] = {"n": args.bootstrap, "seed": 20261105,
                                       "a_ci95": [round(float(x), 4) for x in np.quantile(bs[:, 0], [.025, .975])],
                                       "tau_min_ci95": [round(float(x), 4) for x in np.quantile(bs[:, 1], [.025, .975])]}
        summary[key] = res
        for r in binned(data, res["scale_only"]["a"], res["jitter_only"]["tau_min"]):
            bins_rows.append({"local_model": key, **r})
    with (out / "sigma_binned_scatter.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(bins_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(bins_rows)
    (out / "local_noise_structure.json").write_text(json.dumps({
        "development_only": True, "light_curves_opened": 0,
        "selection": "DRD all_mid_time_data TESS 2022-01-01..2024-01-03, DRD TTV-flagged planets excluded, "
                     "span-capped 20-day groups with >=3 events (D022)",
        "model": "Var = a^2 sigma^2 + tau^2 (minutes), exact REML, per-group intercept (+ slope)",
        "command": "uv run --extra analysis python scripts/local_noise_structure.py",
        "results": summary}, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
