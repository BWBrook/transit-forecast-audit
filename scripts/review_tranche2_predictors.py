"""Exploratory host-held-out prediction with issued-release metadata.

Fits covariates in the population mixing distribution, not regressions on
estimated posterior lambda labels. All outcomes are inspected development data.
"""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize
from scipy.special import logsumexp, roots_hermitenorm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from forecast_variance_components import visits
from review_tranche2_mixture import adaptive_log_integral, stable_precompute


def pack(items):
    lam, alpha = np.zeros((len(items), 2)), np.zeros((len(items), 2))
    for i, p in enumerate(items):
        lam[i, :len(p["eigenvalues"])], alpha[i, :len(p["alpha2"])] = p["eigenvalues"], p["alpha2"]
    constant = np.array([p["q_perp"] + p["logd"] + p["k"]*np.log(2*np.pi) for p in items])
    return lam, alpha, constant


def objective(theta, packed, x, nodes, logweights, gradient=True):
    lam, alpha, constant = packed
    logb, logs = theta[:2]
    beta = theta[2] if len(theta) == 3 else 0.0
    s = np.exp(logs)
    c = np.exp(2*(logb + beta*x[:, None]) + s*nodes[None, :])
    q = c[:, :, None] * lam[:, None, :]
    inv = 1/(1+q)
    ll = -.5*(constant[:, None] + np.sum(alpha[:, None, :]*inv + np.log1p(q), axis=2))
    joint = ll + logweights[None, :]
    lp = logsumexp(joint, axis=1)
    if not gradient:
        return lp
    post = np.exp(joint - lp[:, None])
    derivative = .5*np.sum(alpha[:, None, :]*q*inv**2 - q*inv, axis=2)
    g = [-np.sum(post*derivative*2), -np.sum(post*derivative*s*nodes[None, :])]
    if len(theta) == 3:
        g.append(-np.sum(post*derivative*2*x[:, None]))
    return -float(lp.sum()), np.array(g)


def fit(packed, x, nodes, logweights, has_predictor):
    starts = [[np.log(b), np.log(s)] + ([v] if has_predictor else [])
              for b, s, v in ((.8, 2, 0), (1.2, 3, 0), (2, 4, 0), (1, 3, -.5), (1, 3, .5))]
    fits = [minimize(objective, start, args=(packed, x, nodes, logweights), jac=True,
                    method="L-BFGS-B", bounds=[(-8, 8), (-8, np.log(5))] + ([(-4, 4)] if has_predictor else []),
                    options={"maxiter": 1000, "maxls": 50, "ftol": 1e-11, "gtol": 1e-6}) for start in starts]
    good = [r for r in fits if r.success]
    if not good:
        raise RuntimeError("No predictor fit converged")
    best = min(good, key=lambda r: r.fun)
    if min(r.fun for r in fits) < best.fun - 1e-5:
        raise RuntimeError("Unconverged fit has materially better likelihood")
    return best.x, {"b_at_mean_predictor": float(np.exp(best.x[0])), "s": float(np.exp(best.x[1])),
                    "beta_log_sd_per_training_sd": float(best.x[2]) if has_predictor else None,
                    "nll": float(best.fun), "success": bool(best.success),
                    "multistart_nll_spread": float(max(r.fun for r in fits)-best.fun),
                    "gradient_max": float(np.max(np.abs(best.jac)))}


def csv_write(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader(); w.writerows(rows)


def validate_saved(out, pre, candidates, ids):
    fits = list(csv.DictReader((out / "predictor_fits_q384.csv").open()))
    scores = list(csv.DictReader((out / "predictor_host_cv_q384.csv").open()))
    low = {(r["model"], r["planet"]): float(r["joint_log_predictive_density"])
           for r in csv.DictReader((out / "predictor_host_cv_q192.csv").open())}
    by_fit = {(r["model"], int(r["test_fold"])): r for r in fits}
    by_planet = {p: i for i, p in enumerate(ids)}
    rows = []
    for row in scores:
        fitrow = by_fit[row["model"], int(row["fold"])]
        i = by_planet[row["planet"]]
        x = (candidates[row["model"]][i] - float(fitrow["predictor_center"])) / float(fitrow["predictor_sd"])
        beta = float(fitrow["beta_log_sd_per_training_sd"] or 0)
        b = float(fitrow["b_at_mean_predictor"]) * np.exp(beta*x)
        adaptive, mode, error = adaptive_log_integral(pre[i], b, float(fitrow["s"]))
        q384 = float(row["joint_log_predictive_density"])
        rows.append({"model": row["model"], "planet": row["planet"],
                     "q384_minus_adaptive": q384-adaptive,
                     "q384_minus_q192": q384-low[row["model"], row["planet"]],
                     "adaptive_relative_error": error, "abs_posterior_mode_z": abs(mode)})
    csv_write(out / "predictor_integration_checks.csv", rows)
    report = {"held_out_densities_checked": len(rows),
              "max_abs_q384_minus_adaptive": max(abs(r["q384_minus_adaptive"]) for r in rows),
              "max_abs_q384_minus_q192": max(abs(r["q384_minus_q192"]) for r in rows),
              "max_adaptive_relative_error": max(r["adaptive_relative_error"] for r in rows),
              "max_abs_posterior_mode_z": max(r["abs_posterior_mode_z"] for r in rows),
              "note": "q192 versus q384 includes separately fitted parameter changes; adaptive uses q384 fitted parameters",
              "command": "python scripts/review_tranche2_predictors.py --verify",
              "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "inputs": [{"path": str(p.relative_to(ROOT)), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                         for p in (out / "predictor_fits_q384.csv", out / "predictor_host_cv_q384.csv", out / "predictor_host_cv_q192.csv")]}
    if report["max_abs_q384_minus_adaptive"] > 1e-4:
        raise AssertionError(report)
    (out / "predictor_validation.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--order", type=int, default=384)
    parser.add_argument("--verify", action="store_true", help="Check saved q192/q384 held-out densities by adaptive integration")
    args = parser.parse_args()
    out = ROOT / "results/pilot_v1/tranche2_review"
    for r in csv.DictReader((ROOT / "results/pilot_v1/source_manifest.csv").open()):
        if hashlib.sha256((ROOT/r["local_path"]).read_bytes()).hexdigest() != r["sha256"]:
            raise ValueError("Source changed")
    metadata = {r["planet"]:r for r in csv.DictReader((out/"metadata_per_planet.csv").open())}
    planets, clipped = visits("DRC", 1.087)
    if clipped:
        raise ValueError("This review requires the untrimmed development cohort")
    pre = stable_precompute(planets, [p["m"] for p in planets])
    assert len(planets) == 316
    ids = [p["planet"] for p in planets]
    hosts = np.array([p["host"] for p in planets])
    candidates = {"constant_mixture": np.zeros(len(ids)),
        "log10_training_span": np.array([np.log10(float(metadata[p]["training_span_days"])) for p in ids]),
        "log10_unique_training_epochs": np.array([np.log10(float(metadata[p]["n_unique_epochs"])) for p in ids]),
        "training_includes_TESS": np.array([float(metadata[p]["n_tess_ids"]) > 0 for p in ids], dtype=float),
        "literature_only": np.array([metadata[p]["literature_only"] == "True" for p in ids], dtype=float)}
    unavailable = {"historical_multiplicity": "Not established by acquired issued-release artifacts"}
    for name in list(candidates):
        if name != "constant_mixture" and np.std(candidates[name]) == 0:
            unavailable[name] = "No variation in the 316-planet development cohort"
            del candidates[name]
    if args.verify:
        validate_saved(out, pre, candidates, ids)
        return
    rng = np.random.default_rng(20261105)
    unique_hosts = np.unique(hosts)
    shuffled = rng.permutation(unique_hosts)
    host_fold = {h:i%5 for i,h in enumerate(shuffled)}
    folds = np.array([host_fold[h] for h in hosts])
    nodes, weights = roots_hermitenorm(args.order)
    lw = np.log(weights) - .5*np.log(2*np.pi)
    results, scores = [], []
    fullpack = pack(pre)
    for name, values in candidates.items():
        has_x = name != "constant_mixture"
        for fold in [-1,0,1,2,3,4]:
            train = np.ones(len(pre), bool) if fold == -1 else folds != fold
            test = np.ones(len(pre), bool) if fold == -1 else ~train
            center = float(values[train].mean())
            scale = float(values[train].std()) if has_x else 1.0
            if not scale:
                raise ValueError("Predictor constant within a training fold")
            x = (values-center)/scale
            theta, fitted = fit(tuple(v[train] for v in fullpack), x[train], nodes, lw, has_x)
            results.append({"model": name,"test_fold": fold,"training_planets":int(train.sum()),
                            "predictor_center":center,"predictor_sd":scale,**fitted})
            if fold != -1:
                lp = objective(theta, tuple(v[test] for v in fullpack), x[test], nodes, lw, False)
                for i, value in zip(np.flatnonzero(test), lp):
                    scores.append({"model":name,"fold":fold,"planet":ids[i],"host":hosts[i],
                                   "windows":len(planets[i]["m"]),"joint_log_predictive_density":float(value)})
            print(name, fold, fitted, flush=True)
    baseline = {r["planet"]:r["joint_log_predictive_density"] for r in scores if r["model"]=="constant_mixture"}
    for r in scores:
        r["delta_joint_log_density_vs_constant"] = r["joint_log_predictive_density"] - baseline[r["planet"]]
        r["delta_joint_log_density_per_window"] = r["delta_joint_log_density_vs_constant"] / r["windows"]
    comparisons = []
    for name in candidates:
        rows = [r for r in scores if r["model"]==name]
        delta = np.array([r["delta_joint_log_density_per_window"] for r in rows])
        byhost = {}
        for i,r in enumerate(rows):
            byhost.setdefault(r["host"],[]).append(i)
        hs=list(byhost)
        boot=[]
        for _ in range(2000):
            selected = rng.integers(0,len(hs),len(hs))
            boot.append(float(np.mean(delta[[i for h in selected for i in byhost[hs[h]]]])))
        comparisons.append({"model":name,"planet_balanced_mean_delta_log_density_per_window":float(delta.mean()),
                            "paired_host_bootstrap_low":float(np.quantile(boot,.025)),
                            "paired_host_bootstrap_high":float(np.quantile(boot,.975)),
                            "median_delta_per_window":float(np.median(delta)),
                            "fraction_planets_improved":float(np.mean(delta>0))})
    csv_write(out / f"predictor_fits_q{args.order}.csv", results)
    csv_write(out / f"predictor_host_cv_q{args.order}.csv", scores)
    summary = {"development_only":True,"light_curves_opened":0,"source_commit":"7a9f1a6",
        "command":f"python scripts/review_tranche2_predictors.py --order {args.order}",
        "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "dependencies": [{"path": rel, "sha256": hashlib.sha256((ROOT/rel).read_bytes()).hexdigest()}
                         for rel in ("scripts/review_tranche2_mixture.py", "scripts/forecast_variance_components.py", "results/pilot_v1/source_manifest.csv")],
        "metadata_sha256":hashlib.sha256((out/"metadata_per_planet.csv").read_bytes()).hexdigest(),
        "quadrature_order":args.order,"fold_seed":20261105,"hosts":len(unique_hosts),"planets":len(pre),
        "population_model":"median SD multiplier exp(intercept + beta*x); log(lambda) ~ N(0,s^2)",
        "comparison":comparisons,"unavailable_predictors":unavailable,
        "limitations":["Host-held-out development exercise, not chronological or sealed evaluation",
            "Three univariate covariates explored; no final model selected or frozen",
            "Single random host split; intervals do not account for model search or split variability",
            "Fixed a=1.087 was estimated from the whole development era, including held-out hosts; this is conditional comparison, not end-to-end refitted cross-validation",
            "Log score is joint per-planet predictive density divided by number of retained windows",
            "Bootstrap is conditional on fitted folds; no nested refitting or parameter-uncertainty integration",
            "Predictors describe issued-release inputs, not verified cadence independence or event-level first availability",
            "Diagonal published covariance convention and fixed a=1.087 remain sensitivities"]}
    (out/f"predictor_review_q{args.order}.json").write_text(json.dumps(summary,indent=2)+"\n")


if __name__ == "__main__":
    main()
