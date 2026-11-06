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
  lambda_p is integrated by 384-node Gauss-Hermite quadrature, with 192-node
convergence and continuous posterior summaries (D031).

Recovery is checked by simulating from fitted-scale truths on the real DRC
visit design and refitting with the same multi-start optimiser.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp, roots_hermitenorm, ndtr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from reproduce_table5 import load  # noqa: E402
from review_measurement_diagnostic import groups  # noqa: E402
from transit_audit.exoclock import host_of, residuals_without_covariance  # noqa: E402

MIN = 1440.0
CLIP = 5.0


def visits(release, a, flag_rule="origin", start="2022-01-01", end="2024-01-03"):
    eph, tess, flags = load()
    E = eph[release]
    excl = flags[release] if flag_rule == "origin" else flags["DRD"]
    ev = [m for m in tess if m.planet in E and m.planet not in excl and start <= m.tess_date <= end]
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


QUADRATURE_ORDER = 384
S_MAX = 5.0


@lru_cache(maxsize=4)
def quadrature(order):
    nodes, weights = roots_hermitenorm(order)
    return nodes, np.log(weights) - .5*np.log(2*np.pi)


def precompute(planets, ys):
    """Rank-2 forecast covariance X C X' = U U', allowing a supplied correlation.

    Whitened by D = diag(se^2) and split by SVD, so the quadratic form is a sum
    of non-negative terms (no subtractive cancellation at large c; D031).
    """
    pre = []
    for p, y in zip(planets, ys):
        d = p["se"] ** 2
        yw = y / np.sqrt(d)
        rho = float(p.get("rho", 0.0))
        if not -1 <= rho <= 1:
            raise ValueError("Ephemeris correlation outside its PSD envelope")
        U = np.column_stack([p["st0"] + rho*p["sp"]*p["n"],
                             np.sqrt(max(0., 1-rho*rho))*p["sp"]*p["n"]])
        Uw = U / np.sqrt(d)[:, None]
        W, sv, _ = np.linalg.svd(Uw, full_matrices=False)
        active = sv > 0
        W, sv = W[:, active], sv[active]
        proj = W.T @ yw
        q_perp = float(np.sum((yw - W @ proj) ** 2))
        pre.append((q_perp, sv**2, proj**2, float(np.sum(np.log(d))), len(y)))
    return pre


def planet_ll(pre, c):
    """log N(y; 0, D + c U U') for each planet, vectorised over an array of c."""
    out = []
    for q_perp, lam, w2, logd, k in pre:
        cc = np.asarray(c)[..., None]
        quad = q_perp + np.sum(w2 / (1 + cc * lam), axis=-1)
        logdet = logd + np.sum(np.log1p(cc * lam), axis=-1)
        out.append(-0.5 * (quad + logdet + k * np.log(2 * np.pi)))
    return np.array(out)


def packed(pre):
    lam, w2 = np.zeros((len(pre), 2)), np.zeros((len(pre), 2))
    const = []
    for i, (q, ev, proj2, logd, k) in enumerate(pre):
        lam[i, :len(ev)], w2[i, :len(proj2)] = ev, proj2
        const.append(q + logd + k*np.log(2*np.pi))
    return lam, w2, np.asarray(const)


def objective(theta, data, mixture, order, x, weights, gradient=True):
    lam, w2, const = data
    if mixture:
        nodes, logweights = quadrature(order)
        s = np.exp(theta[1])
    else:
        nodes, logweights, s = np.zeros(1), np.zeros(1), 0.0
    beta = theta[2] if len(theta) == 3 else 0.0
    c = np.exp(2*(theta[0]+beta*x[:, None]) + s*nodes[None, :])
    u = c[:, :, None]*lam[:, None, :]
    inverse = 1/(1+u)
    ll = -.5*(const[:, None] + np.sum(w2[:, None, :]*inverse + np.log1p(u), axis=2))
    joint = ll + logweights
    lp = logsumexp(joint, axis=1)
    if not gradient:
        return lp
    posterior = np.exp(joint-lp[:, None])*weights[:, None]
    deriv = .5*np.sum(w2[:, None, :]*u*inverse**2-u*inverse, axis=2)
    grad = [-np.sum(posterior*deriv*2)]
    if mixture:
        grad.append(-np.sum(posterior*deriv*s*nodes[None, :]))
    if len(theta) == 3:
        grad.append(-np.sum(posterior*deriv*2*x[:, None]))
    return -float(weights @ lp), np.asarray(grad)


def nll(theta, pre, mixture, order=QUADRATURE_ORDER):
    return objective(theta, packed(pre), mixture, order, np.zeros(len(pre)), np.ones(len(pre)))[0]


def fit(planets, ys, mixture=True, pre=None, order=QUADRATURE_ORDER, x=None, weights=None):
    pre = precompute(planets, ys) if pre is None else pre
    has_x = x is not None
    if has_x and not mixture:
        raise ValueError("Predictor is defined for the population mixture")
    x = np.zeros(len(pre)) if x is None else np.asarray(x)
    weights = np.ones(len(pre)) if weights is None else np.asarray(weights)
    if len(pre) == 0 or weights.sum() <= 0 or np.any(weights < 0):
        raise ValueError("Empty or invalid fitting weights")
    starts = ([[np.log(b)] for b in (0.7, 1.0, 1.5, 3.0)] if not mixture else
              [[np.log(b), np.log(s)] + ([0.0] if has_x else []) for b,s in ((.8,.3), (1,1), (1,3), (2,4))])
    fits = []
    data = packed(pre)
    bounds = [(-8, 8)] + ([(-12, np.log(S_MAX))] if mixture else []) + ([(-4,4)] if has_x else [])
    for x0 in starts:
        r = minimize(objective, x0, args=(data, mixture, order, x, weights), jac=True,
                     method="L-BFGS-B", bounds=bounds,
                     options={"ftol": 1e-11, "gtol": 1e-6, "maxiter": 1000, "maxls": 50})
        fits.append(r)
    good = [r for r in fits if r.success and np.isfinite(r.fun)]
    if not good:
        raise RuntimeError("No converged scale-mixture fit")
    best = min(good, key=lambda r: r.fun)
    if min(r.fun for r in fits) < best.fun-1e-5:
        raise RuntimeError("Nonconverged solution has materially better likelihood")
    out = {"b": float(np.exp(best.x[0])), "nll": float(best.fun), "converged": True,
           "order": order, "gradient_max": float(np.max(np.abs(best.jac))),
           "at_bound": bool(any(min(abs(v-lo),abs(v-hi)) < 1e-5 for v,(lo,hi) in zip(best.x,bounds)))}
    if mixture:
        out["s_log_lambda"] = float(np.exp(best.x[1]))
    if has_x:
        out["beta_log_sd"] = float(best.x[2])
    return out


def posterior_lambda(planets, ys, est):
    """Continuous-grid posterior summaries; no quadrature-node classifications."""
    pre = precompute(planets, ys)
    z = np.linspace(-12,12,9601)
    s = est["s_log_lambda"]
    ll = planet_ll(pre, est["b"]**2*np.exp(s*z)) - .5*z*z
    density = np.exp(ll-np.max(ll,axis=1)[:,None])
    mass = .5*(density[:,1:]+density[:,:-1])*np.diff(z)
    cdf = np.column_stack([np.zeros(len(pre)), np.cumsum(mass,axis=1)])
    cdf /= cdf[:,-1,None]
    rows = []
    for p, c in zip(planets,cdf):
        qq = np.exp(s*np.interp([.025,.5,.975],c,z))
        rows.append({"planet":p["planet"], "lambda_q025":float(qq[0]), "lambda_median":float(qq[1]),
                     "lambda_q975":float(qq[2]), "probability_lambda_gt_10":float(1-np.interp(np.log(10)/s,z,c)),
                     "probability_lambda_gt_100":float(1-np.interp(np.log(100)/s,z,c))})
    return rows


def simulate(planets, b, s, rng):
    ys = []
    for p in planets:
        lam = np.exp(s * rng.standard_normal())
        rho = float(p.get("rho", 0.0))
        forecast = (p["st0"] ** 2 + np.outer(p["n"], p["n"]) * p["sp"] ** 2
                    + rho*p["st0"]*p["sp"]*(p["n"][:, None]+p["n"][None, :]))
        V = np.diag(p["se"] ** 2) + b * b * lam * forecast
        ys.append(rng.multivariate_normal(np.zeros(len(p["m"])), V))
    return ys


def source_manifest():
    checked = []
    for row in csv.DictReader((ROOT / "results/pilot_v1/source_manifest.csv").open()):
        actual = hashlib.sha256((ROOT/row["local_path"]).read_bytes()).hexdigest()
        if actual != row["sha256"]:
            raise ValueError("Source hash changed: " + row["local_path"])
        checked.append({"path":row["local_path"], "sha256":actual})
    return checked


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def host_bootstrap(planets, pre, replicates, rng):
    hosts, inverse = np.unique([p["host"] for p in planets], return_inverse=True)
    rows = []
    for rep in range(replicates):
        counts = np.bincount(rng.integers(0,len(hosts),len(hosts)), minlength=len(hosts))
        est = fit(planets, [], pre=pre, weights=counts[inverse])
        rows.append({"replicate":rep, **est})
    intervals = {key:list(np.quantile([r[key] for r in rows],[.025,.975]))
                 for key in ("b","s_log_lambda")} if rows else None
    return rows, {"hosts":len(hosts), "replicates":replicates,
                  "percentile95":intervals, "fits_at_parameter_bound":sum(r["at_bound"] for r in rows),
                  "interpretation":"Host-cluster bootstrap, fixed outcome scale and selected cohort/model; no model-selection uncertainty"}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results/pilot_v1/variance_components_v2"))
    ap.add_argument("--reps", type=int, default=20)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--a", type=float, default=1.087)
    args = ap.parse_args(argv)
    if args.reps < 0 or args.bootstrap < 0 or args.a <= 0:
        raise ValueError("Invalid replication count or outcome scale")
    sources = source_manifest()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(20261105)
    boot_rng = np.random.default_rng(20261106)
    summary = {"development_only":True, "light_curves_opened":0, "clip_local_z":CLIP, "a_fixed":args.a,
               "issued_covariance":"diagonal published-marginal sensitivity; Cov(T0,P) remains missing",
               "cohort":"TESS 2022-01-01..2024-01-03 in DRD mid-times; origin flags",
               "quadrature_order":QUADRATURE_ORDER, "source_manifest":sources,
               "source_commit":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
               "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
               "python":platform.python_version(), "numpy":np.__version__,
               "command":f"python scripts/forecast_variance_components.py --reps {args.reps} --bootstrap {args.bootstrap} --a {args.a}",
               "outcome_scale_sensitivity":"Fixed a is not an independently established measurement scale"}
    real, posteriors, boots, sensitivity = {}, [], [], []
    for release in ("DRB","DRC"):
        planets, clipped = visits(release,args.a)
        ys = [p["m"] for p in planets]
        pre = precompute(planets,ys)
        g = fit(planets,ys,mixture=False,pre=pre)
        est = fit(planets,ys,pre=pre)
        lower = fit(planets,ys,pre=pre,order=192)
        if abs(est["nll"]-lower["nll"]) > .01 or abs(est["s_log_lambda"]-lower["s_log_lambda"]) > .01:
            raise RuntimeError("Quadrature order convergence failed")
        rows = posterior_lambda(planets,ys,est)
        posteriors.extend({"release":release, **r} for r in rows)
        bootstrap_rows, bootstrap_summary = host_bootstrap(planets,pre,args.bootstrap,boot_rng)
        boots.extend({"release":release, **r} for r in bootstrap_rows)
        real[release] = {"planets":len(planets),"visits":sum(len(p["m"]) for p in planets),
                         "events":sum(p["events"] for p in planets),"events_clipped":clipped,
                         "gaussian":g,"mixture":est,"order192":lower,"host_bootstrap":bootstrap_summary,
                         "lr_mixture_vs_gaussian":2*(g["nll"]-est["nll"]),
                         "model_population_probability_lambda_gt_10":float(ndtr(-np.log(10)/est["s_log_lambda"])),
                         "posterior_expected_planets_lambda_gt_10":sum(r["probability_lambda_gt_10"] for r in rows),
                         "posterior_median_lambda_gt_10":sum(r["lambda_median"] > 10 for r in rows),
                         "posterior_median_lambda_gt_100":sum(r["lambda_median"] > 100 for r in rows)}
        for a in (1.0,1.2):
            pl,_ = visits(release,a)
            sensitivity.append({"release":release,"a":a,**fit(pl,[p["m"] for p in pl])})
        if release == "DRC":
            design,xfit = planets,est
        print(release,json.dumps(real[release]),flush=True)
    summary["real_fit"],summary["a_sensitivity"] = real,sensitivity
    rec,sim_rows = [],[]
    truths = [(1,0),(1,1),(1.5,1),(1,2.5),(xfit["b"],xfit["s_log_lambda"])]
    for b,s in truths:
        estimates = []
        for rep in range(args.reps):
            est = fit(design,simulate(design,b,s,rng))
            estimates.append(est)
            sim_rows.append({"synthetic_only":True,"true_b":b,"true_s":s,"replicate":rep,**est})
        if estimates:
            rec.append({"true_b":b,"true_s":s,
                        **{key:{"median":float(np.median([r[key] for r in estimates])),
                                "q10":float(np.quantile([r[key] for r in estimates],.1)),
                                "q90":float(np.quantile([r[key] for r in estimates],.9))}
                           for key in ("b","s_log_lambda")}})
    summary["simulation"] = {"design":"real DRC origin-flag visit design","replicates_per_truth":args.reps,
                             "seed":20261105,"recovery":rec}
    summary["bootstrap_seed"] = 20261106
    write_csv(out/"planet_posteriors.csv",posteriors)
    write_csv(out/"host_bootstrap.csv",boots)
    write_csv(out/"identifiability_simulation.csv",sim_rows)
    (out/"variance_components_summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
