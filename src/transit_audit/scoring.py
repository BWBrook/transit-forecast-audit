"""Proper Gaussian scores and planet-balanced summaries; time scores in seconds."""
from math import erf, log, pi, sqrt
from statistics import NormalDist
import numpy as np

SECONDS_PER_DAY = 86400.0


def interval_score(observed, lower, upper, alpha):
    """Central (1-alpha) interval score; smaller is better, in input time units."""
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie strictly between zero and one")
    vals = np.array([observed, lower, upper], dtype=float)
    if not np.all(np.isfinite(vals)) or lower > upper:
        raise ValueError("Invalid interval or observation")
    return float(upper - lower + 2 / alpha * max(lower - observed, 0)
                 + 2 / alpha * max(observed - upper, 0))


def score_one(observed_bjd_tdb, mean_bjd_tdb, forecast_variance_days2,
              observation_sigma_days, levels=(0.682689492, 0.95, 0.997300204)):
    """Score the predictive distribution of an independent measured midpoint.

    Measurement error is convolved before coverage/PIT/proper scoring. These
    coverage values do not directly estimate coverage for the latent true time.
    """
    vals = np.array([observed_bjd_tdb, mean_bjd_tdb,
                     forecast_variance_days2, observation_sigma_days], dtype=float)
    if not np.all(np.isfinite(vals)) or forecast_variance_days2 < 0 or observation_sigma_days < 0:
        raise ValueError("Invalid forecast or observation uncertainty")
    variance = forecast_variance_days2 + observation_sigma_days**2
    if variance <= 0:
        raise ValueError("Predictive variance must be positive")
    residual = float((observed_bjd_tdb - mean_bjd_tdb) * SECONDS_PER_DAY)
    sd = sqrt(variance) * SECONDS_PER_DAY
    z = residual / sd
    result = {
        "error_seconds": residual,
        "absolute_error_seconds": abs(residual),
        "squared_error_seconds2": residual**2,
        "forecast_sigma_seconds": sqrt(forecast_variance_days2) * SECONDS_PER_DAY,
        "measurement_sigma_seconds": observation_sigma_days * SECONDS_PER_DAY,
        "predictive_sigma_seconds": sd,
        "standardized_error": z,
        "pit": 0.5 * (1 + erf(z / sqrt(2))),
        "negative_log_score_seconds": 0.5 * log(2 * pi) + log(sd) + 0.5 * z**2,
    }
    for level in levels:
        if not 0 < level < 1:
            raise ValueError("Coverage levels must lie strictly between zero and one")
        q = NormalDist().inv_cdf((1 + level) / 2)
        suffix = f"{level:.6f}"
        result[f"covered_{suffix}"] = float(abs(residual) <= q * sd)
        result[f"width_seconds_{suffix}"] = 2 * q * sd
        result[f"interval_score_seconds_{suffix}"] = interval_score(
            residual, -q * sd, q * sd, 1 - level
        )
    return result


def planet_means(values, planet_ids):
    vals = np.asarray(values, dtype=float)
    ids = np.asarray(planet_ids, dtype=str)
    if vals.ndim != 1 or vals.size == 0 or vals.shape != ids.shape or not np.all(np.isfinite(vals)):
        raise ValueError("Nonempty finite values and matching planet IDs required")
    if np.any(ids == ""):
        raise ValueError("Planet IDs cannot be empty")
    return {str(p): float(vals[ids == p].mean()) for p in np.unique(ids)}


def planet_balanced_mean(values, planet_ids):
    return float(np.mean(list(planet_means(values, planet_ids).values())))


def cluster_bootstrap_interval(planet_mean_values, host_ids, confidence=0.95,
                               n_resamples=2000, seed=17):
    """Resample hosts, retaining every planet mean in each sampled host.

    Input must already contain one mean per planet within the analysis stratum.
    A repeated host in a bootstrap draw contributes all of its planets again.
    """
    vals = np.asarray(planet_mean_values, dtype=float)
    hosts = np.asarray(host_ids, dtype=str)
    if vals.ndim != 1 or vals.shape != hosts.shape or not np.all(np.isfinite(vals)):
        raise ValueError("Matching finite values and host IDs required")
    unique = np.unique(hosts)
    if len(unique) < 2 or np.any(hosts == ""):
        raise ValueError("At least two identified hosts are required")
    if not 0 < confidence < 1 or not isinstance(n_resamples, int) or n_resamples < 100:
        raise ValueError("Invalid confidence or bootstrap count")
    groups = [vals[hosts == h] for h in unique]
    rng = np.random.default_rng(seed)
    samples = np.empty(n_resamples)
    for i in range(n_resamples):
        chosen = rng.integers(0, len(groups), size=len(groups))
        samples[i] = np.concatenate([groups[j] for j in chosen]).mean()
    alpha = (1 - confidence) / 2
    return tuple(float(x) for x in np.quantile(samples, [alpha, 1 - alpha]))
