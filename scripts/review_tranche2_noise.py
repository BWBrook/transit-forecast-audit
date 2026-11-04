"""Independent error-contrast REML audit of D026 on inspected timing records.

The contrast likelihood is independent of the normal-equation implementation
in local_noise_structure.py. Zero additive variance is allowed explicitly.
No light curves or new timing products are accessed.
"""

import argparse
import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import minimize, minimize_scalar

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "src"))
from reproduce_table5 import load
from review_measurement_diagnostic import groups
from transit_audit.exoclock import host_of


def make_contrasts(t, sigma, period):
    epoch = np.rint((t - t[0]) / period)
    y = ((t - t[0]) - epoch * period) * 1440
    design = np.column_stack([np.ones(len(t)), epoch - epoch.mean()])
    if np.linalg.matrix_rank(design) != 2:
        raise ValueError("Degenerate local design")
    q, _ = np.linalg.qr(design, mode="complete")
    contrast = q[:, 2:]
    eigenvalues, rotation = np.linalg.eigh(contrast.T @ (sigma[:, None] ** 2 * contrast))
    values = rotation.T @ (contrast.T @ y)
    return eigenvalues, values, y, design


def objective(theta, eigenvalues, values, weights):
    a2 = np.exp(2 * theta[0])
    variance = a2 * eigenvalues + theta[1]
    derivative = (1 / variance - values * values / variance**2) * weights
    value = .5 * np.sum(weights * (np.log(variance) + values * values / variance))
    gradient = np.array([np.sum(derivative * a2 * eigenvalues), .5 * np.sum(derivative)])
    return float(value), gradient


def estimate(eigenvalues, values, weights=None):
    weights = np.ones_like(values) if weights is None else weights
    scale = np.sqrt(np.sum(weights * values**2 / eigenvalues) / weights.sum())
    scale_nll = objective([np.log(scale), 0], eigenvalues, values, weights)[0]
    jitter = minimize_scalar(lambda q: objective([0, q], eigenvalues, values, weights)[0],
                             bounds=(0, 25), method="bounded", options={"xatol": 1e-12})
    jitter_q = float(jitter.x)
    if objective([0, 0], eigenvalues, values, weights)[0] < jitter.fun:
        jitter_q = 0.0
    fits = [minimize(objective, [np.log(scale), q], args=(eigenvalues, values, weights),
                     jac=True, bounds=[(np.log(.2), np.log(5)), (0, 25)], method="L-BFGS-B",
                     options={"ftol": 1e-12, "gtol": 1e-7, "maxiter": 1000, "maxls": 50})
            for q in (0, .01, .1)]
    converged = [f for f in fits if f.success]
    if not converged:
        raise RuntimeError("No converged independent REML solution")
    best = min(converged, key=lambda f: f.fun)
    if min(f.fun for f in fits) < best.fun - 1e-7:
        raise RuntimeError("Unconverged fit improves the objective materially")
    return {"a": float(np.exp(best.x[0])), "tau_seconds": float(np.sqrt(best.x[1]) * 60),
            "nll": float(best.fun), "scale_only_a": float(scale), "scale_only_nll": scale_nll,
            "jitter_only_tau_seconds": np.sqrt(jitter_q) * 60,
            "jitter_only_nll": objective([0, jitter_q], eigenvalues, values, weights)[0],
            "lr_jitter_given_scale": 2 * (scale_nll - best.fun),
            "lr_scale_given_jitter": 2 * (objective([0, jitter_q], eigenvalues, values, weights)[0] - best.fun)}


def csv_write(path, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bootstrap", type=int, default=400)
    args = parser.parse_args()
    out = ROOT / "results/pilot_v1/tranche2_review"
    out.mkdir(parents=True, exist_ok=True)
    sources = []
    for item in csv.DictReader((ROOT / "results/pilot_v1/source_manifest.csv").open()):
        actual = hashlib.sha256((ROOT / item["local_path"]).read_bytes()).hexdigest()
        if actual != item["sha256"]:
            raise ValueError("Source checksum mismatch: " + item["local_path"])
        sources.append({"path": item["local_path"], "sha256": actual})
    eph, events, flags = load()
    if any(e.tess_date > "2024-01-03" for e in events):
        raise ValueError("Outcome exceeds development boundary")
    by = {}
    for event in events:
        if event.planet in eph["DRD"] and event.planet not in flags["DRD"]:
            by.setdefault(event.planet, []).append(event)
    vals, eig, hosts, group_info, originals, residual_rows = [], [], [], [], [], []
    for planet, event_list in sorted(by.items()):
        for j, g in enumerate(groups(event_list, 20)):
            if len(g) < 3:
                continue
            t = np.array([e.t_bjd_tdb for e in g])
            sigma = np.array([e.sigma_days for e in g]) * 1440
            d, z, y, X = make_contrasts(t, sigma, eph["DRD"][planet].period_days)
            vals.extend(z)
            eig.extend(d)
            hosts.extend([host_of(planet)] * len(z))
            originals.append((planet, y, sigma, X))
            group_info.append({"planet": planet, "host": host_of(planet), "group": j,
                               "n": len(g), "df": len(z), "span_days": t[-1] - t[0]})
            qw, _ = np.linalg.qr(X / sigma[:, None], mode="reduced")
            projection = np.eye(len(g)) - qw @ qw.T
            h = np.sum(qw**2, axis=1)
            normalized = projection @ (y / sigma)
            jitter_factor = ((projection * projection) @ (1 / sigma**2)) / (1 - h)
            for s, r, factor in zip(sigma, normalized / np.sqrt(1 - h), jitter_factor):
                residual_rows.append((s, r, factor))
    d, z = np.array(eig), np.array(vals)
    fit = estimate(d, z)
    from local_noise_structure import neg_reml
    differences = []
    for a, tau in ((1, 0), (1.09, 0), (1.08, .08), (1, .2)):
        original = neg_reml([np.log(a)], originals, fix_tau=tau)
        independent = objective([np.log(a), tau*tau], d, z, np.ones_like(z))[0]
        differences.append(float(original - independent))
    if np.ptp(differences) > 1e-7:
        raise AssertionError("Independent REML differs by more than a parameter-independent constant")

    profile = []
    for tau in np.linspace(0, 20, 81):
        f = minimize_scalar(lambda loga: objective([loga, (tau/60)**2], d, z, np.ones_like(z))[0],
                            bounds=(np.log(.2), np.log(5)), method="bounded")
        profile.append({"tau_seconds": float(tau), "a_profile": float(np.exp(f.x)),
                        "twice_nll_difference": float(2 * (f.fun - fit["nll"]))})
    csv_write(out / "noise_tau_profile.csv", profile)
    host_ids, inverse = np.unique(hosts, return_inverse=True)
    rng = np.random.default_rng(20261105)
    boot = []
    for rep in range(args.bootstrap):
        counts = np.bincount(rng.integers(0, len(host_ids), len(host_ids)), minlength=len(host_ids))
        estimate_boot = estimate(d, z, counts[inverse])
        boot.append({"replicate": rep, "a": estimate_boot["a"],
                     "tau_seconds": estimate_boot["tau_seconds"]})
    if boot:
        csv_write(out / "noise_host_bootstrap.csv", boot)
    sr = np.array(residual_rows)
    cuts = np.quantile(sr[:, 0], np.linspace(0, 1, 7))
    bins = []
    for j, (lo, hi) in enumerate(zip(cuts[:-1], cuts[1:])):
        use = (sr[:, 0] >= lo) & ((sr[:, 0] <= hi) if j == 5 else (sr[:, 0] < hi))
        bins.append({"sigma_lower_min": lo, "sigma_upper_min": hi, "n": int(use.sum()),
                     "observed_z_rms": float(np.sqrt(np.mean(sr[use, 1]**2))),
                     "scale_only_predicted_rms": fit["scale_only_a"],
                     "jitter_only_projected_rms": float(np.sqrt(np.mean(1 + (fit["jitter_only_tau_seconds"]/60)**2 * sr[use, 2]))),
                     "joint_projected_rms": float(np.sqrt(np.mean(fit["a"]**2 + (fit["tau_seconds"]/60)**2 * sr[use, 2])))})
    csv_write(out / "noise_sigma_bins.csv", bins)
    summary = {"development_only": True, "light_curves_opened": 0, "source_commit": "7a9f1a6",
        "command": f"python scripts/review_tranche2_noise.py --bootstrap {args.bootstrap}",
        "python": platform.python_version(), "numpy": np.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inputs": sources, "groups": len(group_info), "events": len(residual_rows),
        "residual_df": len(z), "hosts": len(host_ids), "planets": len({r["planet"] for r in group_info}),
        "independent_fit": fit, "normal_equation_minus_contrast_nll": differences,
        "bootstrap_seed": 20261105, "host_bootstrap_replicates": len(boot),
        "a_host_percentile95": list(np.quantile([r["a"] for r in boot], [.025, .975])) if boot else None,
        "tau_seconds_host_percentile95": list(np.quantile([r["tau_seconds"] for r in boot], [.025, .975])) if boot else None,
        "bootstrap_tau_at_boundary": sum(r["tau_seconds"] == 0 for r in boot),
        "inference": "Supports a common scale over a common homoscedastic jitter under the conditional REML model; does not identify measurement versus sigma-proportional physical/model error."}
    (out / "noise_review.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "inputs"}, indent=2))


if __name__ == "__main__":
    main()
