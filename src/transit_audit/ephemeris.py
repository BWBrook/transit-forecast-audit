"""Linear transit ephemerides with explicit covariance and day units.

Epoch numbers must be assigned and verified upstream. This module never guesses
cycles, converts time standards, or assumes a missing covariance is zero.
"""
from dataclasses import dataclass
import numpy as np


def _finite(value, name):
    a = np.asarray(value, dtype=float)
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must be finite")
    return a


@dataclass(frozen=True)
class Prediction:
    mean_bjd_tdb: np.ndarray
    forecast_variance_days2: np.ndarray
    observation_variance_days2: np.ndarray

    @property
    def predictive_variance_days2(self):
        return self.forecast_variance_days2 + self.observation_variance_days2


@dataclass(frozen=True)
class LinearEphemeris:
    reference_epoch: float
    t_ref_bjd_tdb: float
    period_days: float
    covariance_days2: np.ndarray

    def __post_init__(self):
        for name in ("reference_epoch", "t_ref_bjd_tdb", "period_days"):
            if np.ndim(_finite(getattr(self, name), name)) != 0:
                raise ValueError(f"{name} must be scalar")
        if self.period_days <= 0:
            raise ValueError("period_days must be positive")
        if self.covariance_days2 is None:
            raise ValueError("Covariance is missing: use a declared sensitivity analysis")
        cov = _finite(self.covariance_days2, "covariance_days2").copy()
        if cov.shape != (2, 2):
            raise ValueError("covariance_days2 must have shape (2, 2)")
        scale = max(float(np.max(np.abs(cov))), np.finfo(float).tiny)
        if not np.allclose(cov, cov.T, atol=scale * 1e-12, rtol=1e-12):
            raise ValueError("Covariance must be symmetric")
        cov = (cov + cov.T) / 2
        if np.any(np.diag(cov) < 0):
            raise ValueError("Covariance must be positive semidefinite")
        # A tolerance relative to the largest eigenvalue alone can accept a
        # grossly invalid correlation when epoch and period variances differ
        # by many orders of magnitude. This 2x2 PSD condition is scale-aware.
        bound = np.sqrt(cov[0, 0]) * np.sqrt(cov[1, 1])
        if abs(cov[0, 1]) > bound * (1 + 1e-12):
            raise ValueError("Covariance must be positive semidefinite")
        cov.setflags(write=False)
        object.__setattr__(self, "covariance_days2", cov)

    def predict(self, epochs, observation_sigma_days=0.0,
                ephemeris_scale=1.0, extra_scatter_days=0.0):
        """Forecast moments, then convolve with independent measurement error.

        A calibration scale multiplies ephemeris standard deviations only. It
        must be estimated from development data, never the evaluated outcomes.
        extra_scatter_days is optional forecast discrepancy, not measurement noise.
        """
        e = _finite(epochs, "epochs")
        obs = _finite(observation_sigma_days, "observation_sigma_days")
        for name, value in (("ephemeris_scale", ephemeris_scale),
                            ("extra_scatter_days", extra_scatter_days)):
            if np.ndim(_finite(value, name)) != 0:
                raise ValueError(f"{name} must be scalar")
        if np.any(obs < 0) or ephemeris_scale <= 0 or extra_scatter_days < 0:
            raise ValueError("Invalid uncertainty or scale")
        delta = e - self.reference_epoch
        cov = self.covariance_days2
        variance = cov[0, 0] + 2 * delta * cov[0, 1] + delta**2 * cov[1, 1]
        magnitude = cov[0, 0] + 2 * np.abs(delta * cov[0, 1]) + delta**2 * cov[1, 1]
        if np.any(variance < -1e-12 * np.maximum(magnitude, np.finfo(float).tiny)):
            raise ValueError("Negative propagated variance")
        variance = ephemeris_scale**2 * np.maximum(variance, 0) + extra_scatter_days**2
        mean, variance, obs = np.broadcast_arrays(
            self.t_ref_bjd_tdb + delta * self.period_days, variance, obs
        )
        return Prediction(mean, variance, obs**2)

    def recenter(self, new_reference_epoch):
        """Transform both parameters and covariance to a new epoch pivot."""
        delta = float(new_reference_epoch) - self.reference_epoch
        transform = np.array([[1.0, delta], [0.0, 1.0]])
        return LinearEphemeris(
            float(new_reference_epoch),
            self.t_ref_bjd_tdb + delta * self.period_days,
            self.period_days,
            transform @ self.covariance_days2 @ transform.T,
        )


@dataclass(frozen=True)
class LinearFit:
    ephemeris: LinearEphemeris
    chi_square: float
    degrees_of_freedom: int


def fit_linear(epochs, midtimes_bjd_tdb, sigma_days):
    """Weighted least squares with supplied, independent Gaussian timing errors.

    The weighted epoch pivot makes the formal covariance diagonal. Absolute
    uncertainties are used as supplied: no automatic residual-based inflation.
    A common origin is subtracted from Julian dates for numerical stability.
    """
    e = _finite(epochs, "epochs")
    t = _finite(midtimes_bjd_tdb, "midtimes_bjd_tdb")
    s = _finite(sigma_days, "sigma_days")
    if e.ndim != 1 or e.shape != t.shape or e.shape != s.shape or len(e) < 3:
        raise ValueError("Provide three or more matching one-dimensional arrays")
    if np.any(s <= 0):
        raise ValueError("All timing uncertainties must be positive")
    weights = 1 / s**2
    total = weights.sum()
    pivot = float(np.dot(weights, e) / total)
    x = e - pivot
    centered_t = t - t[0]
    mean_t = float(np.dot(weights, centered_t) / total)
    spread = float(np.dot(weights, x**2))
    if spread <= 0:
        raise ValueError("At least two distinct epochs are required")
    period = float(np.dot(weights * x, centered_t - mean_t) / spread)
    cov = np.diag([1 / total, 1 / spread])
    eph = LinearEphemeris(pivot, float(t[0] + mean_t), period, cov)
    # Residuals in centered coordinates avoid repeated subtraction of large JDs.
    residual = centered_t - (mean_t + period * x)
    return LinearFit(eph, float(np.sum((residual / s)**2)), len(e) - 2)


def missing_covariance_variance_bounds(sigma_t0_days, sigma_period_days, delta_epochs):
    """Extremal variances over all correlations rho in [-1, 1].

    These are sensitivity bounds, not a probability distribution for rho and not
    automatically usable as calibrated predictive intervals.
    """
    st = _finite(sigma_t0_days, "sigma_t0_days")
    sp = _finite(sigma_period_days, "sigma_period_days")
    d = _finite(delta_epochs, "delta_epochs")
    if np.any(st < 0) or np.any(sp < 0):
        raise ValueError("Standard deviations cannot be negative")
    return (st - np.abs(d) * sp)**2, (st + np.abs(d) * sp)**2
