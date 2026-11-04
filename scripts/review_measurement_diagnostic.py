"""Development-only sensitivity audit of D016/D017; no light-curve access.

Uses the existing parser, independently computes local weighted projections,
and records input hashes. Synthetic counterexamples are separate from data.
"""

import csv
import hashlib
import json
import platform
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from reproduce_table5 import load


def groups(events, span_cap=None):
    current = []
    for event in sorted(events, key=lambda m: m.t_bjd_tdb):
        if current and (
            event.t_bjd_tdb - current[-1].t_bjd_tdb > 20
            or (span_cap is not None and event.t_bjd_tdb - current[0].t_bjd_tdb > span_cap)
        ):
            yield current
            current = []
        current.append(event)
    if current:
        yield current


def project(t, s, period, fit_slope):
    n = np.rint((t - t[0]) / period)
    y = (t - t[0]) - n * period
    x = np.column_stack([np.ones(len(t)), n - n.mean()]) if fit_slope else np.ones((len(t), 1))
    design = x / s[:, None]
    q, _ = np.linalg.qr(design, mode="reduced")
    residual = y / s - q @ (q.T @ (y / s))
    leverage = np.sum(q * q, axis=1)
    usable = 1 - leverage > 1e-10
    z = residual[usable] / np.sqrt(1 - leverage[usable])
    return z, float(residual @ residual), len(t) - x.shape[1]


def write_csv(path, rows):
    with path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main():
    out = ROOT / "results/pilot_v1/independent_review"
    out.mkdir(parents=True, exist_ok=True)
    manifest = list(csv.DictReader((ROOT / "results/pilot_v1/source_manifest.csv").open()))
    inputs = []
    for item in manifest:
        path = ROOT / item["local_path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != item["sha256"]:
            raise ValueError(f"Source hash changed: {item['local_path']}")
        inputs.append({"path": item["local_path"], "sha256": digest})
    for rel in ("data/fixtures/exoclock_ttv_flags.csv", "results/pilot_v1/covariance_completeness.csv"):
        inputs.append({"path": rel, "sha256": hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()})
    ephemerides, events, flags = load()
    if any(e.tess_date > "2024-01-03" for e in events):
        raise ValueError("Outcome file exceeds the already inspected development era")
    summaries, group_rows = [], []
    by_planet = {}
    for event in events:
        by_planet.setdefault(event.planet, []).append(event)
    for selection in ("DRD_nonflagged", "all_DRD"):
        for grouping, cap in (("gap20", None), ("span20", 20.0)):
            for mode in ("DRD_fixed", "local_linear"):
                zs, ps, chis, dfs = [], [], [], []
                spans = []
                for planet, es in sorted(by_planet.items()):
                    if planet not in ephemerides["DRD"] or (selection == "DRD_nonflagged" and planet in flags["DRD"]):
                        continue
                    for j, group in enumerate(groups(es, cap)):
                        if len(group) < 3:
                            continue
                        t = np.array([e.t_bjd_tdb for e in group])
                        s = np.array([e.sigma_days for e in group])
                        z, chi, df = project(t, s, ephemerides["DRD"][planet].period_days, mode == "local_linear")
                        zs.extend(z)
                        ps.extend([planet] * len(z))
                        chis.append(chi)
                        dfs.append(df)
                        spans.append(float(t[-1] - t[0]))
                        if mode == "DRD_fixed":
                            group_rows.append({"selection": selection, "grouping": grouping,
                                "planet": planet, "group": j, "events": len(group),
                                "span_days": spans[-1], "first_record": group[0].record_id,
                                "last_record": group[-1].record_id, "chi2": chi, "df": df})
                z = np.asarray(zs)
                planet_m2 = [np.mean(z[np.array(ps) == p] ** 2) for p in sorted(set(ps))]
                summaries.append({"selection": selection, "grouping": grouping, "fit": mode,
                    "events": len(z), "planets": len(set(ps)), "groups": len(spans),
                    "groups_over_20_days": sum(s > 20 for s in spans), "max_span_days": max(spans),
                    "rms_standardised": float(np.sqrt(np.mean(z*z))),
                    "sqrt_chi2_over_dof": float(np.sqrt(sum(chis) / sum(dfs))),
                    "sqrt_planet_balanced_second_moment": float(np.sqrt(np.mean(planet_m2))),
                    "robust_scale": float(np.median(np.abs(z)) / 0.6744897501960817),
                    "fraction_abs_lt_1": float(np.mean(np.abs(z) < 1))})
    write_csv(out / "measurement_sensitivity.csv", summaries)
    write_csv(out / "measurement_groups.csv", group_rows)

    covariance = list(csv.DictReader((ROOT / "results/pilot_v1/covariance_completeness.csv").open()))
    cov_summary = []
    for release in ("DRB", "DRC", "DRD"):
        rows = [r for r in covariance if r["release"] == release]
        corr = np.array([float(r["corr_t0_p_at_published_epoch"]) for r in rows])
        pivot = np.array([float(r["pivot_minus_published_epoch"]) for r in rows])
        lookup = {r["planet"]: float(r["corr_t0_p_at_published_epoch"]) for r in rows}
        corrections = []
        for event in events:
            if event.planet not in lookup or event.planet in flags["DRD"]:
                continue
            e = ephemerides[release][event.planet]
            n = round((event.t_bjd_tdb - e.t0_bjd_tdb) / e.period_days)
            independent = e.sigma_t0_days**2 + (n * e.sigma_period_days)**2
            cross = 2 * n * lookup[event.planet] * e.sigma_t0_days * e.sigma_period_days
            corrections.append((cross / independent, cross / (independent + event.sigma_days**2)))
        a = np.asarray(corrections)
        cov_summary.append({"release": release, "planet_releases": len(rows),
            "pivot_abs_le_half_epoch": int(np.sum(np.abs(pivot) <= .5)),
            "max_abs_pivot_epochs": float(np.max(np.abs(pivot))),
            "max_abs_reconstructed_correlation": float(np.max(np.abs(corr))),
            "max_abs_fractional_forecast_variance_cross_term_R": float(np.max(np.abs(a[:, 0]))),
            "max_abs_fractional_observed_variance_cross_term_R": float(np.max(np.abs(a[:, 1]))),
            "status": "WLS sensitivity using reconstructed correlation; not issued posterior covariance"})
    write_csv(out / "covariance_review.csv", cov_summary)

    rng = np.random.default_rng(20261104)
    noise = rng.normal(size=(10000, 8))
    jitter = rng.normal(size=noise.shape)
    common = rng.normal(size=(10000, 1))
    scenarios = {"correct_independent_noise": noise,
        "measurement_scale_1.115": 1.115 * noise,
        "correct_noise_plus_white_latent_jitter": noise + np.sqrt(1.115**2 - 1) * jitter,
        "correct_noise_plus_common_offset_2sigma": noise + 2 * common}
    simulated = []
    for label, values in scenarios.items():
        z = (values - values.mean(axis=1, keepdims=True)) / np.sqrt(7 / 8)
        simulated.append({"synthetic_only": True, "scenario": label,
            "groups": len(values), "events_per_group": 8,
            "expected_within_group_rms": 1.115 if label in ("measurement_scale_1.115", "correct_noise_plus_white_latent_jitter") else 1.0,
            "observed_rms": float(np.sqrt(np.mean(z*z))),
            "fraction_abs_lt_1": float(np.mean(np.abs(z) < 1))})
    write_csv(out / "synthetic_identifiability.csv", simulated)
    (out / "measurement_review_receipt.json").write_text(json.dumps({
        "development_only": True, "light_curves_opened": 0,
        "command": "python scripts/review_measurement_diagnostic.py",
        "python": platform.python_version(), "numpy": np.__version__,
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "inputs": inputs, "seed": 20261104,
        "synthetic_white_jitter_sigma": float(np.sqrt(1.115**2 - 1)),
        "shared_parser": "scripts/reproduce_table5.py::load; independent diagnostic algebra",
    }, indent=2) + "\n")
    print(json.dumps(summaries, indent=2))
    print(json.dumps(cov_summary, indent=2))


if __name__ == "__main__":
    main()
