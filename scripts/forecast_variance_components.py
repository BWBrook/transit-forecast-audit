"""T014 identifiability: two-stage forecast-calibration model on the development era.

Development material only (D014); no light curves. Why two stages: a one-stage
Gaussian likelihood over events with shared ephemeris covariance is dominated by
heavy tails at two levels (gross planet failures of tens to hundreds of issued
sigma, and event outliers within visits), returns b ~ 98 and is multimodal once a
planet-failure mixture is added. Here:

Stage 1. Each planet's outcomes are split into span-capped 20-day visits (D022).
  Events with |local z| > CLIP after a visit-mean fit are dropped and counted.
  The visit mean has standard error a * sqrt(1 / sum w), with `a` fixed from the
  local REML fit (scripts/local_noise_structure.py) or varied as a sensitivity.
Stage 2. Visit means m_v at weighted epochs n_v against the issued ephemeris:
    V_p = diag(se_v^2) + b^2 lambda_p X C X',   log lambda_p ~ N(0, s^2)
  with C the issued diagonal (T0, P) covariance (D021). b is the median
  inflation of the issued forecast SD across planets; s is the between-planet
  spread of miscalibration (s = 0: one common factor). Gross failures appear as
  planets with very large posterior lambda_p. A one-component failure mixture
  (offset kappa with probability pi) was tried first and rejected: the
  discrepancies are continuous from ~2 to ~600 min, so it returned b ~ 20 (DRC)
  or pi = 1 (DRB). The rank-2 structure of X C X' gives a closed-form likelihood;
  lambda_p is integrated by 48-node Gauss-Hermite quadrature.

Recovery is checked by simulating from fitted-scale truths on the real DRC
visit design and refitting with the same multi-start optimiser.
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
sys.path.insert(0, str(ROOT / "src"))
from reproduce_table5 import load  # noqa: E402
from review_measurement_diagnostic import groups  # noqa: E402
from transit_audit.exoclock import host_of, residuals_without_covariance  # noqa: E402

MIN = 1440.0
CLIP = 5.0


def visits(release, a, flag_rule="origin"):
    eph, tess, flags = load()
    E = eph[release]
    excl = flags[release] if flag_rule == "origin" else flags["DRD"]
    ev = [m for m in tess if m.planet in E and m.planet not in excl]
    if any(m.tess_date > "2024-01-03" for m in ev):
        raise ValueError("outcome beyond inspected development era")
    by = {}
    for m in ev:
        by.setdefault(m.planet, []).append(m)
    planets, clipped = [], 0
    for p, ms in sorted(by.items()):
        e = E[p]
        m_v, se_v, n_v = [], [], []
        for g in groups(ms, 20.0):
            n, oc, _, _ = residuals_without_covariance(E, g)
            oc, s = oc * MIN, np.array([x.sigma_days for x in g]) * MIN
            keep = np.ones(len(g), bool)
            if len(g) >= 3:
                for _ in range(3):
                    w = 1 / s[keep] ** 2
                    mu = np.sum(w * oc[keep]) / w.sum()
                    new = np.abs(oc - mu) / (a * s) <= CLIP
                    if new.sum() < 2 or (new == keep).all():
                        break
                    keep = new
            clipped += int((~keep).sum())
            w = 1 / s[keep] ** 2
            m_v.append(np.sum(w * oc[keep]) / w.sum())
            n_v.append(np.sum(w * n[keep]) / w.sum())
            se_v.append(a / np.sqrt(w.sum()))
        planets.append({"planet": p, "host": host_of(p), "m": np.array(m_v), "se": np.array(se_v),
                        "n": np.array(n_v), "st0": e.sigma_t0_days * MIN, "sp": e.sigma_period_days * MIN,
                        "events": len(ms)})
    return planets, clipped


GH_X, GH_W = np.polynomial.hermite_e.hermegauss(48)
GH_LW = np.log(GH_W / np.sqrt(2 * np.pi))
S_MAX = 5.0  # lambda spans exp(+-5 s) at the outer nodes; s > 5 is not a scale-mixture any more


def precompute(planets, ys):
    """Rank-2 forecast covariance X C X' = U U', U = [sigma_T0 1, sigma_P n]."""
    pre = []
    for p, y in zip(planets, ys):
        d = p["se"] ** 2
        U = np.column_stack([np.full(len(y), p["st0"]), p["sp"] * p["n"]])
        G = U.T @ (U / d[:, None])
        lam, Q = np.linalg.eigh(G)
        r = Q.T @ (U.T @ (y / d))
        pre.append((float(np.sum(y * y / d)), np.maximum(lam, 0.0), r * r,
                    float(np.sum(np.log(d))), len(y)))
    return pre


def planet_ll(pre, c):
    """log N(y; 0, D + c U U') for each planet, vectorised over an array of c."""
    out = []
    for q, lam, r2, logd, k in pre:
        cc = np.asarray(c)[..., None]
        quad = q - np.sum(r2 / (1 / cc + lam), axis=-1)
        logdet = logd + np.sum(np.log1p(cc * lam), axis=-1)
        out.append(-0.5 * (quad + logdet + k * np.log(2 * np.pi)))
    return np.array(out)


def nll(theta, pre, mixture):
    b2 = np.exp(2 * theta[0])
    if not mixture:
        return -float(np.sum(planet_ll(pre, b2)))
    s = np.exp(theta[1])
    if s > S_MAX or not -10 < theta[0] < 10:
        return 1e300
    ll = planet_ll(pre, b2 * np.exp(s * GH_X))
    return -float(np.sum(np.logaddexp.reduce(ll + GH_LW, axis=1)))


def fit(planets, ys, mixture=True, pre=None):
    pre = precompute(planets, ys) if pre is None else pre
    starts = ([[np.log(b)] for b in (0.7, 1.0, 1.5, 3.0)] if not mixture else
              [[np.log(b), np.log(s)] for b in (0.8, 1.2, 2.0) for s in (0.3, 1.0, 3.0)])
    best = None
    for x0 in starts:
        r = minimize(nll, x0, args=(pre, mixture), method="Nelder-Mead",
                     options={"xatol": 1e-5, "fatol": 1e-5, "maxiter": 4000})
        if best is None or r.fun < best.fun:
            best = r
    out = {"b": float(np.exp(best.x[0])), "nll": float(best.fun)}
    if mixture:
        out["s_log_lambda"] = float(np.exp(best.x[1]))
    return out


def posterior_lambda(planets, ys, est):
    """Posterior median of each planet's forecast-variance inflation lambda_p."""
    pre = precompute(planets, ys)
    ll = planet_ll(pre, est["b"] ** 2 * np.exp(est["s_log_lambda"] * GH_X)) + GH_LW
    post = np.exp(ll - np.logaddexp.reduce(ll, axis=1)[:, None])
    cdf = np.cumsum(post, axis=1)
    idx = np.argmax(cdf >= 0.5, axis=1)
    return np.exp(est["s_log_lambda"] * GH_X[idx]), post


def simulate(planets, b, s, rng):
    ys = []
    for p in planets:
        lam = np.exp(s * rng.standard_normal())
        V = np.diag(p["se"] ** 2) + b * b * lam * (p["st0"] ** 2 + np.outer(p["n"], p["n"]) * p["sp"] ** 2)
        ys.append(rng.multivariate_normal(np.zeros(len(p["m"])), V))
    return ys


def profile(pre, est, key, grid):
    rows = []
    for v in grid:
        if key == "b":
            f = lambda th: nll([np.log(v), th[0]], pre, True)
            x0 = [np.log(est["s_log_lambda"])]
        else:
            f = lambda th: nll([th[0], np.log(v)], pre, True)
            x0 = [np.log(est["b"])]
        r = minimize(f, x0, method="Nelder-Mead", options={"xatol": 1e-5, "fatol": 1e-5})
        rows.append((float(v), float(r.fun)))
    inside = [v for v, f in rows if f - est["nll"] <= 1.92]
    return [min(inside), max(inside)] if inside else None


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "pilot_v1" / "variance_components"))
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--a", type=float, default=1.087, help="local REML scale, local_linear scale_plus_jitter")
    args = ap.parse_args(argv)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261105)
    summary = {"development_only": True, "light_curves_opened": 0, "clip_local_z": CLIP, "a_fixed": args.a,
               "issued_covariance": "diagonal (Cov(T0,P) missing; D021)",
               "cohort": "TESS 2022-01-01..2024-01-03 in DRD mid-times; origin-only flags excluded (D015)",
               "command": "uv run --extra analysis python scripts/forecast_variance_components.py"}

    real, fails, sens = {}, [], []
    for rel in ("DRB", "DRC"):
        planets, clipped = visits(rel, args.a)
        ys = [p["m"] for p in planets]
        pre = precompute(planets, ys)
        g = fit(planets, ys, mixture=False, pre=pre)
        x = fit(planets, ys, mixture=True, pre=pre)
        lam, _ = posterior_lambda(planets, ys, x)
        real[rel] = {"planets": len(planets), "visits": int(sum(len(p["m"]) for p in planets)),
                     "events": int(sum(p["events"] for p in planets)), "events_clipped": clipped,
                     "gaussian_b": round(g["b"], 4), "gaussian_nll": round(g["nll"], 3),
                     **{k: round(v, 4) for k, v in x.items()},
                     "b_profile_ci95": profile(pre, x, "b", np.exp(np.linspace(np.log(0.3), np.log(5), 121))),
                     "s_profile_ci95": profile(pre, x, "s", np.exp(np.linspace(np.log(0.05), np.log(8), 121))),
                     "lr_mixture_vs_gaussian": round(2 * (g["nll"] - x["nll"]), 2),
                     "planets_lambda_gt_10": int(np.sum(lam > 10)), "planets_lambda_gt_100": int(np.sum(lam > 100))}
        for p, y, l in zip(planets, ys, lam):
            if l > 10:
                fails.append({"release": rel, "planet": p["planet"], "visits": len(y),
                              "median_visit_oc_min": round(float(np.median(y)), 2),
                              "issued_sigma_t0_min": round(p["st0"], 3), "issued_sigma_p_s": round(p["sp"] * 60, 4),
                              "max_issued_pred_sd_min": round(float(np.sqrt(p["st0"]**2 + np.max(p["n"]**2) * p["sp"]**2)), 3),
                              "posterior_median_lambda": round(float(l), 1)})
        for a in (1.0, 1.2):
            pl, _ = visits(rel, a)
            sens.append({"release": rel, "a": a, **{k: round(v, 4) for k, v in fit(pl, [p["m"] for p in pl]).items()}})
        if rel == "DRC":
            design, xfit = planets, x
        print(rel, real[rel], flush=True)
    summary["real_fit"] = real
    summary["a_sensitivity"] = sens
    with (out / "planet_miscalibration.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(fails[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(fails)

    truths = [(1.0, 0.0), (1.0, 1.0), (1.5, 1.0), (1.0, 2.5), (xfit["b"], xfit["s_log_lambda"])]
    rec, sim_rows = [], []
    for b, sd in truths:
        est = []
        for rep in range(args.reps):
            e = fit(design, simulate(design, b, sd, rng))
            est.append(e)
            sim_rows.append({"synthetic_only": True, "true_b": round(b, 4), "true_s": round(sd, 4), "rep": rep,
                             **{k: round(v, 5) for k, v in e.items()}})
        rec.append({"truth": {"b": round(b, 4), "s_log_lambda": round(sd, 4)},
                    **{k: {"median": round(float(np.median([e[k] for e in est])), 4),
                           "q10": round(float(np.quantile([e[k] for e in est], .1)), 4),
                           "q90": round(float(np.quantile([e[k] for e in est], .9)), 4)}
                       for k in ("b", "s_log_lambda")}})
        print("truth", (b, sd), rec[-1]["b"], rec[-1]["s_log_lambda"], flush=True)
    with (out / "identifiability_simulation.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(sim_rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(sim_rows)
    summary["simulation"] = {"design": "real DRC origin-flag visit design", "reps_per_truth": args.reps,
                             "seed": 20261105, "recovery": rec}
    (out / "variance_components_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
