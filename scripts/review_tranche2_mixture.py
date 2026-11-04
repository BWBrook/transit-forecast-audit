"""Independent numerical audit of the tranche-2 planet scale mixture.

Development data only (D014).  This deliberately does not reuse the production
rank-two likelihood algebra: an SVD of the whitened rank-two design computes
the residual orthogonal to the forecast subspace without catastrophic
subtraction.  Robust high-order Gauss-Hermite fits are checked against adaptive
one-dimensional integration and dense Cholesky calculations.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import platform
import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy.integrate import quad
from scipy.optimize import brentq, minimize, minimize_scalar
from scipy.special import logsumexp, roots_hermitenorm
from scipy.stats import norm

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import forecast_variance_components as original  # noqa: E402

Z_LIMIT = 12.0
LOG2PI = float(np.log(2 * np.pi))


def stable_precompute(planets, ys):
    """Whiten and decompose y into forecast-subspace and orthogonal parts."""
    out = []
    for planet, y in zip(planets, ys):
        y = np.asarray(y, float)
        d = np.asarray(planet["se"], float) ** 2
        u = np.column_stack([
            np.full(len(y), planet["st0"]),
            planet["sp"] * planet["n"],
        ])
        a = u / np.sqrt(d)[:, None]
        yw = y / np.sqrt(d)
        q, singular, _ = np.linalg.svd(a, full_matrices=False)
        tol = max(a.shape) * np.finfo(float).eps * (singular[0] if singular.size else 0.0)
        keep = singular > tol
        q = q[:, keep]
        singular = singular[keep]
        alpha = q.T @ yw
        orthogonal = yw - q @ alpha
        out.append({
            "planet": planet["planet"],
            "q_perp": float(orthogonal @ orthogonal),
            "eigenvalues": singular * singular,
            "alpha2": alpha * alpha,
            "logd": float(np.sum(np.log(d))),
            "k": len(y),
            "d": d,
            "u": u,
            "y": y,
        })
    return out


def stable_planet_ll(item, c):
    """Stable log N(y; 0, D + c UU') for scalar or array c > 0."""
    c = np.asarray(c, float)
    cc = c[..., None]
    eigenvalues = item["eigenvalues"]
    quad_term = item["q_perp"] + np.sum(item["alpha2"] / (1 + cc * eigenvalues), axis=-1)
    logdet = item["logd"] + np.sum(np.log1p(cc * eigenvalues), axis=-1)
    return -0.5 * (quad_term + logdet + item["k"] * LOG2PI)


def dense_planet_ll(item, c):
    variance = np.diag(item["d"]) + c * item["u"] @ item["u"].T
    chol = np.linalg.cholesky(variance)
    solved = np.linalg.solve(chol, item["y"])
    return -0.5 * (
        solved @ solved + 2 * np.sum(np.log(np.diag(chol))) + item["k"] * LOG2PI
    )


def quadrature(order):
    nodes, weights = roots_hermitenorm(order)
    return nodes, np.log(weights) - 0.5 * LOG2PI


def quadrature_nll(theta, pre, nodes, logweights):
    logb, logs = theta
    s = float(np.exp(logs))
    if not (-8 < logb < 8 and 1e-5 < s < 5):
        return 1e100
    c = np.exp(2 * logb + s * nodes)
    total = 0.0
    for item in pre:
        total += float(logsumexp(stable_planet_ll(item, c) + logweights))
    return -total


def multistart_fit(pre, order, extra_start=None):
    nodes, logweights = quadrature(order)
    starts = [
        np.log([b, s])
        for b in (0.6, 1.0, 1.8, 3.0)
        for s in (0.5, 1.5, 3.0, 4.3)
    ]
    if extra_start is not None:
        starts.append(np.log(extra_start))
    fits = []
    for start in starts:
        fit = minimize(
            quadrature_nll,
            start,
            args=(pre, nodes, logweights),
            method="Nelder-Mead",
            options={"xatol": 2e-7, "fatol": 2e-6, "maxiter": 2500},
        )
        fits.append(fit)
    best = min(fits, key=lambda x: x.fun)
    return {
        "order": order,
        "b": float(np.exp(best.x[0])),
        "s": float(np.exp(best.x[1])),
        "nll": float(best.fun),
        "success": bool(best.success),
        "iterations": int(best.nit),
        "start_spread_nll": float(max(x.fun for x in fits) - min(x.fun for x in fits)),
        "converged_starts": int(sum(x.success for x in fits)),
        "total_starts": len(fits),
    }


def adaptive_log_integral(item, b, s):
    def log_integrand(z):
        c = b * b * np.exp(s * z)
        return float(stable_planet_ll(item, c) - 0.5 * z * z - 0.5 * LOG2PI)

    mode = minimize_scalar(
        lambda z: -log_integrand(z),
        bounds=(-Z_LIMIT, Z_LIMIT),
        method="bounded",
        options={"xatol": 2e-9},
    )
    peak = log_integrand(mode.x)
    value, error = quad(
        lambda z: np.exp(log_integrand(z) - peak),
        -Z_LIMIT,
        Z_LIMIT,
        epsabs=2e-11,
        epsrel=2e-10,
        limit=250,
    )
    return peak + np.log(value), float(mode.x), float(error / value)


def adaptive_nll_at(pre, b, s):
    values = [adaptive_log_integral(item, b, s) for item in pre]
    return -float(sum(x[0] for x in values)), values


def adaptive_refine(pre, start):
    """Refine the converged high-order fit with the adaptive integral."""
    cache = {}

    def objective(theta):
        key = tuple(np.round(theta, 11))
        if key not in cache:
            b, s = np.exp(theta)
            if not (1e-4 < b < 100 and 1e-4 < s < 5):
                return 1e100
            cache[key] = adaptive_nll_at(pre, float(b), float(s))[0]
        return cache[key]

    fit = minimize(
        objective,
        np.log(start),
        method="Nelder-Mead",
        options={"xatol": 2e-6, "fatol": 2e-5, "maxiter": 350},
    )
    b, s = np.exp(fit.x)
    nll, details = adaptive_nll_at(pre, float(b), float(s))
    return {
        "b": float(b),
        "s": float(s),
        "nll": float(nll),
        "success": bool(fit.success),
        "iterations": int(fit.nit),
        "evaluations": int(fit.nfev),
        "cache_size": len(cache),
        "max_relative_quad_error": max(x[2] for x in details),
        "max_abs_posterior_mode_z": max(abs(x[1]) for x in details),
    }


def profile_intervals(pre, b_hat, s_hat, order=384):
    nodes, logweights = quadrature(order)
    theta_hat = np.log([b_hat, s_hat])
    minimum = quadrature_nll(theta_hat, pre, nodes, logweights)
    target = minimum + 1.920729

    def profile_b(logb):
        return minimize_scalar(
            lambda logs: quadrature_nll([logb, logs], pre, nodes, logweights),
            bounds=(np.log(0.05), np.log(4.999)), method="bounded",
            options={"xatol": 2e-7},
        ).fun

    def profile_s(logs):
        return minimize_scalar(
            lambda logb: quadrature_nll([logb, logs], pre, nodes, logweights),
            bounds=(np.log(0.05), np.log(10)), method="bounded",
            options={"xatol": 2e-7},
        ).fun

    intervals = {}
    for name, function, lower, estimate, upper in (
        ("b", profile_b, np.log(0.05), theta_hat[0], np.log(10)),
        ("s", profile_s, np.log(0.05), theta_hat[1], np.log(4.999)),
    ):
        lo = brentq(lambda x: function(x) - target, lower, estimate, xtol=1e-6)
        hi = brentq(lambda x: function(x) - target, estimate, upper, xtol=1e-6)
        intervals[name] = [float(np.exp(lo)), float(np.exp(hi))]
    return {"order": order, "delta_nll": 1.920729, **intervals}


def posterior_summary(pre, b, s, dz=0.0025):
    grid = np.arange(-Z_LIMIT, Z_LIMIT + dz / 2, dz)
    rows = []
    for item in pre:
        logpost = stable_planet_ll(item, b * b * np.exp(s * grid)) - 0.5 * grid * grid
        logpost -= np.max(logpost)
        density = np.exp(logpost)
        masses = 0.5 * (density[1:] + density[:-1]) * dz
        cdf = np.concatenate([[0.0], np.cumsum(masses)])
        cdf /= cdf[-1]
        quantile_z = np.interp([0.025, 0.5, 0.975], cdf, grid)
        median_lambda = float(np.exp(s * quantile_z[1]))
        probability_gt_10 = float(1 - np.interp(np.log(10) / s, grid, cdf))
        probability_gt_100 = float(1 - np.interp(np.log(100) / s, grid, cdf))
        rows.append({
            "planet": item["planet"],
            "posterior_median_lambda": median_lambda,
            "posterior_q025_lambda": float(np.exp(s * quantile_z[0])),
            "posterior_q975_lambda": float(np.exp(s * quantile_z[2])),
            "posterior_median_sd_scale": float(b * np.sqrt(median_lambda)),
            "posterior_probability_lambda_gt_10": probability_gt_10,
            "posterior_probability_lambda_gt_100": probability_gt_100,
        })
    return rows


def write_csv(path, rows):
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def verify_manifest():
    rows = list(csv.DictReader((ROOT / "results/pilot_v1/source_manifest.csv").open()))
    checked = []
    for row in rows:
        path = ROOT / row["local_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != row["sha256"]:
            raise ValueError(f"source hash changed: {row['local_path']}")
        checked.append({"path": row["local_path"], "sha256": digest})
    return checked


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--reuse-converged-fit",
        action="store_true",
        help="Recompute diagnostics/posteriors from an existing converged mixture_real_fit.json",
    )
    args = parser.parse_args()
    manifest_inputs = verify_manifest()
    output = ROOT / "results/pilot_v1/tranche2_review"
    output.mkdir(parents=True, exist_ok=True)
    convergence = []
    fit_path = output / "mixture_real_fit.json"
    fits = json.loads(fit_path.read_text()) if args.reuse_converged_fit else {}
    pre_by_release = {}
    for release in ("DRB", "DRC"):
        planets, clipped = original.visits(release, 1.087)
        ys = [p["m"] for p in planets]
        pre = stable_precompute(planets, ys)
        pre_by_release[release] = pre
        if not args.reuse_converged_fit:
            prior = None
            for order in (32, 48, 64, 96, 128, 192, 256, 384):
                fit = multistart_fit(pre, order, prior)
                fit.update({"release": release, "planets": len(planets), "clipped": clipped})
                convergence.append(fit)
                prior = (fit["b"], fit["s"])
            fits[release] = adaptive_refine(pre, prior)
        fits[release]["planets"] = len(planets)
        fits[release]["visits"] = int(sum(len(p["m"]) for p in planets))

    dense_rows = []
    drc = pre_by_release["DRC"]
    suspect_names = {
        "TOI-1130b", "TOI-1130c", "TOI-125b", "TOI-201b", "HD332231b", "L98-59c"
    }
    check_items = [x for x in drc if x["planet"] in suspect_names]
    for item in check_items:
        for c in (1e-8, 1.0, 1e4, 1e8, 1e12, 1e16, 1e32, 1e48):
            stable = float(stable_planet_ll(item, c))
            try:
                dense = float(dense_planet_ll(item, c))
            except np.linalg.LinAlgError:
                dense = float("nan")
            old_pre = original.precompute(
                [{"se": np.sqrt(item["d"]), "n": item["u"][:, 1], "st0": item["u"][0, 0],
                  "sp": 1.0, "m": item["y"]}],
                [item["y"]],
            )
            old = float(original.planet_ll(old_pre, c)[0])
            dense_rows.append({
                "planet": item["planet"], "c": c, "stable_ll": stable,
                "dense_ll": dense, "old_ll_reconstructed_design": old,
                "stable_minus_dense": stable - dense if np.isfinite(dense) else float("nan"),
            })

    posterior_rows = []
    for release in ("DRB", "DRC"):
        fits[release]["stable_profile_ci95"] = profile_intervals(
            pre_by_release[release], fits[release]["b"], fits[release]["s"]
        )
        rows = posterior_summary(pre_by_release[release], fits[release]["b"], fits[release]["s"])
        fine_rows = posterior_summary(
            pre_by_release[release], fits[release]["b"], fits[release]["s"], dz=0.00125
        )
        for row in rows:
            posterior_rows.append({"release": release, **row})
        fits[release]["posterior_median_lambda_gt_10"] = int(sum(r["posterior_median_lambda"] > 10 for r in rows))
        fits[release]["posterior_median_lambda_gt_100"] = int(sum(r["posterior_median_lambda"] > 100 for r in rows))
        fits[release]["model_population_probability_lambda_gt_10"] = float(
            norm.sf(np.log(10) / fits[release]["s"])
        )
        fits[release]["model_population_probability_lambda_gt_100"] = float(
            norm.sf(np.log(100) / fits[release]["s"])
        )
        fits[release]["posterior_expected_planets_lambda_gt_10"] = float(
            sum(r["posterior_probability_lambda_gt_10"] for r in rows)
        )
        fits[release]["posterior_expected_planets_lambda_gt_100"] = float(
            sum(r["posterior_probability_lambda_gt_100"] for r in rows)
        )
        fits[release]["max_abs_log_median_lambda_change_halved_grid"] = float(max(
            abs(np.log(a["posterior_median_lambda"] / b["posterior_median_lambda"]))
            for a, b in zip(rows, fine_rows)
        ))

    if convergence:
        write_csv(output / "mixture_quadrature_convergence.csv", convergence)
    write_csv(output / "mixture_rank2_dense.csv", dense_rows)
    write_csv(output / "mixture_planet_posterior.csv", posterior_rows)
    fit_path.write_text(json.dumps(fits, indent=2) + "\n")
    inputs = []
    for relative in (
        "scripts/forecast_variance_components.py",
        "results/pilot_v1/source_manifest.csv",
        "data/raw/osf/wpjtn/all_mid_time_data.txt",
        "data/raw/osf/wna5e/updated_ephemerides.txt",
        "data/raw/osf/p298n/catalogue_of_ephemerides.txt",
        "data/fixtures/exoclock_ttv_flags.csv",
    ):
        path = ROOT / relative
        inputs.append({"path": relative, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()})
    receipt = {
        "development_only": True,
        "protected_light_curves_opened": 0,
        "command": ".venv/bin/python scripts/review_tranche2_mixture.py"
        + (" --reuse-converged-fit" if args.reuse_converged_fit else ""),
        "source_commit": subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True
        ).strip(),
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "python": platform.python_version(),
        "numpy": np.__version__,
        "quadrature": "scipy roots_hermitenorm; adaptive scipy.integrate.quad over z in [-12,12]",
        "manifest_inputs_verified": manifest_inputs,
        "other_inputs": inputs,
    }
    (output / "mixture_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(fits, indent=2))


if __name__ == "__main__":
    main()
