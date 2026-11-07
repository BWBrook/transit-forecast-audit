"""Single fail-closed acceptance contract for rule t015v3a (D058).

Used by calibration (candidate fits), the fixed attempt ledger, injection
evidence and scoring. Every input that cannot be verified returns an explicit
non-accepted state; nothing passes because a diagnostic is missing or nonfinite.

Product level: SPOC 120-s PDCSAP only; identification ok; finite shape-fit
reduced chi-square <= SHAPE_RCHI_MAX (gross-fit QC, selected in development
review, D058). Event level: timed; no integration flag; finite positive sigma
and mid-time; Gaussian certification consistent with the exact 95% quantiles,
otherwise a likelihood grid that passes the I1 adapter's support check.

Likelihood representation (declared): calibration fits use the Gaussian
approximation with sigma = the 68% posterior half-width for every accepted
event; scoring uses the adapter's representation (Gaussian when gauss_ok,
otherwise the accepted likelihood grid).
"""

from __future__ import annotations

import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHAPE_RCHI_MAX = 100.0
INTEGRATION_FLAGS = frozenset({"mass_outside_fine", "coarse_fine_shift"})
PRODUCT = "SPOC_120"
ACCEPTED = "accepted"


def _finite(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def product_state(diag, product=PRODUCT):
    """diag: identification/shape row for one product (planet-sector-product), or None."""
    if product != PRODUCT:
        return "product_not_in_scope"
    if diag is None:
        return "product_unavailable"
    st = str(diag.get("status", ""))
    if st.startswith("read_failed") or st.startswith("download_failed"):
        return "product_read_failed"
    if st.startswith("exception"):
        return "product_exception"
    if st != "ok":
        return "product_id_failed"
    r = _finite(diag.get("shape_rchi2"))
    if r is None:
        return "product_shape_diagnostic_unresolved"
    if r > SHAPE_RCHI_MAX:
        return "product_shape_gate_failed"
    return "ok"


def support_ok(grid_path):
    from sprint1_outcome_adapter import likelihood_grid
    if not grid_path:
        return False
    p = Path(grid_path)
    p = p if p.is_absolute() else ROOT / p
    if not p.exists():
        return False
    try:
        likelihood_grid(p)
    except ValueError:
        return False
    return True


def event_state(row, check_support=True):
    """One measured window (I1 row or injection ledger row)."""
    st = row.get("status", "")
    if st != "timed":
        return st or "status_missing"
    if INTEGRATION_FLAGS & set((row.get("flags") or "").split(";")):
        return "integration_unresolved"
    sig = _finite(row.get("sigma_s"))
    if sig is None or sig <= 0:
        return "timing_value_unresolved"
    if "tc_bjd_tdb" in row and _finite(row.get("tc_bjd_tdb")) is None:
        return "timing_value_unresolved"
    gauss = str(row.get("gauss_ok", "")).lower() in ("true", "1", "yes")
    if gauss:
        if "q025_s" in row:
            lo, hi = _finite(row.get("q025_s")), _finite(row.get("q975_s"))
            if lo is None or hi is None or lo >= 0 or hi <= 0 or any(
                    abs(abs(q) / (1.959964 * sig) - 1) > 0.10 for q in (lo, hi)):
                return "gauss_certification_inconsistent"
        return ACCEPTED
    if not check_support:
        return "likelihood_support_not_exported"
    return ACCEPTED if support_ok(row.get("posterior_grid_path")) else "likelihood_support_unresolved"


def accept(row, diag, product=PRODUCT, check_support=True):
    ps = product_state(diag, product)
    return ps if ps != "ok" else event_state(row, check_support)


def terminal_status(product_st, windows, diag, predicted, period, coverage_ok):
    """Terminal state of one intended event.

    product_st: product_state(...); windows: recovered windows mapped to this DRD cycle;
    predicted/period: DRD prediction (locates checks only); coverage_ok: directly checked
    quality-0 cadence coverage at the prediction (window and in-transit >= 0.75), or None if unchecked.
    """
    if product_st != "ok":
        return product_st
    if len(windows) > 1:
        return "ambiguous_multiple_windows"
    if windows:
        w = windows[0]
        st = accept(w, diag)
        tc = _finite(w.get("tc_bjd_tdb"))
        if st == ACCEPTED and (tc is None or abs(tc - predicted) > period / 4):
            return "cycle_ambiguous"
        return st
    if coverage_ok is None:
        return "unmatched_observability_unknown"
    return "unmatched_expected_event" if coverage_ok else "no_cadence_coverage_at_prediction"
