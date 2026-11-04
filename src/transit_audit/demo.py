"""Reproducible synthetic demonstration. No astronomical observations are used."""
from datetime import date, timedelta
import csv
import json
from pathlib import Path
import platform
import numpy as np
from .ephemeris import fit_linear
from .provenance import Timing, chronological_split
from .scoring import score_one, planet_means, planet_balanced_mean, cluster_bootstrap_interval
from . import __version__


def run_demo(output_dir, seed=2000):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    if any((out / name).exists() for name in ("synthetic_scores.csv", "synthetic_summary.json")):
        raise FileExistsError("Use a new output directory; demonstration outputs are not overwritten")
    rng = np.random.default_rng(seed)
    all_scores = []
    for index in range(24):
        planet = f"SYNTHETIC-{index:03d}-b"
        host = f"SYNTHETIC-{index:03d}"
        period = float(rng.uniform(1.5, 4.0))
        epochs = np.r_[np.arange(0, 241, 20), np.arange(420, 541, 20)]
        sigma = float(rng.uniform(25, 60) / 86400)
        # Calendar dates are synthetic metadata. BJD values carry no real source identity.
        origin = date(2018, 1, 1)
        timings = []
        for e in epochs:
            observed = origin + timedelta(days=float(e * period))
            available = observed + timedelta(days=7)
            is_training = e <= 240
            # Known late drift in half the synthetic planets, never fitted away.
            drift_seconds = 0 if index % 2 == 0 or is_training else 0.002 * (e - 240)**2
            measured = 2458119.5 + e * period + rng.normal(0, sigma) + drift_seconds / 86400
            timings.append(Timing(
                f"{planet}-{e}", planet, host, f"{planet}-event-{e}", int(e), float(measured), sigma,
                observed.isoformat(), available.isoformat(), "synthetic-generator-v1",
                (f"{planet}-exposure-{e}",),
            ))
        cutoff = origin + timedelta(days=240 * period + 8)
        training, outcomes, quarantined = chronological_split(timings, cutoff.isoformat())
        if quarantined:
            raise RuntimeError("Unexpected synthetic ledger quarantine")
        fit = fit_linear([t.epoch for t in training], [t.midtime_bjd_tdb for t in training],
                         [t.sigma_days for t in training])
        for timing in outcomes:
            pred = fit.ephemeris.predict(timing.epoch)
            row = score_one(timing.midtime_bjd_tdb, float(pred.mean_bjd_tdb),
                            float(pred.forecast_variance_days2), timing.sigma_days)
            row.update({
                "planet_id": planet, "host_id": host, "measurement_id": timing.measurement_id,
                "synthetic_truth": "linear" if index % 2 == 0 else "late_drift",
                "horizon_days": (date.fromisoformat(timing.observed_date) - cutoff).days,
                "data_kind": "SYNTHETIC_ONLY",
            })
            all_scores.append(row)
    numeric = [k for k, v in all_scores[0].items() if isinstance(v, (int, float))]
    summary = {
        "warning": "SYNTHETIC ONLY. Demonstrates software behaviour; no scientific inference.",
        "seed": seed, "package_version": __version__, "python": platform.python_version(),
        "numpy": np.__version__, "planets": 24, "timings": len(all_scores),
        "model": "Formal weighted linear ephemeris; no recalibration fitted",
        "planet_balanced_metrics": {}, "truth_group_metrics": {},
    }
    for metric in numeric:
        summary["planet_balanced_metrics"][metric] = planet_balanced_mean(
            [r[metric] for r in all_scores], [r["planet_id"] for r in all_scores]
        )
    for truth in ("linear", "late_drift"):
        subset = [r for r in all_scores if r["synthetic_truth"] == truth]
        means = planet_means([r["covered_0.950000"] for r in subset], [r["planet_id"] for r in subset])
        summary["truth_group_metrics"][truth] = {
            "coverage_95": float(np.mean(list(means.values()))),
            "host_bootstrap_interval_95": cluster_bootstrap_interval(
                list(means.values()), list(means), n_resamples=1000, seed=seed
            ),
        }
    with (out / "synthetic_scores.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(all_scores[0]))
        writer.writeheader()
        writer.writerows(all_scores)
    (out / "synthetic_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    return summary
