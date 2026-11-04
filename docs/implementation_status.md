# Implementation status and reproducibility

## Implemented and checked on synthetic/analytic examples

| Component | File | Scope |
|---|---|---|
| Linear ephemeris and full covariance | `src/transit_audit/ephemeris.py` | Explicit pivot, stable weighted fit, covariance transformation, sensitivity bounds |
| Observed-outcome scoring | `src/transit_audit/scoring.py` | Measurement-error convolution, PIT, errors, log score, central interval score, coverage/width |
| Dependence helpers | `scoring.py` | Equal-planet means and host-cluster bootstrap of precomputed planet means |
| Chronology and lineage guards | `src/transit_audit/provenance.py` | Explicit normalised records, historical availability, duplicate atomic exposures, strict issued-date checks |
| Executable example | `src/transit_audit/demo.py` | 24 artificial planets, 168 later timing scores, one origin per planet |
| ExoClock release readers | `src/transit_audit/exoclock.py` | DRB 17-col TSV with flags; DRC/DRD catalogues and mid-time files; nearest-epoch O−C with the Table 5 sigma |
| OSF acquisition | `scripts/acquire_osf.py` | Pinned GUIDs, OSF version metadata, SHA-256, refuses hash drift |
| Track R reproduction | `scripts/reproduce_table5.py` | Exact DRB/DRC Table 5; origin-flag, availability and planet-balanced sensitivities |
| Covariance audit | `scripts/covariance_completeness.py` | Refit from released inputs; implied corr(T0,P) at published epoch |
| Measurement calibration | `scripts/tess_measurement_calibration.py` | Forecast-free within-visit test of TESS σ_Tmid |
| Pilot dossiers | `scripts/pilot_dossiers.py` | DRB flow, 10-planet dossiers, pair codes, plots (`uv run --extra analysis`) |
| CLI | `src/transit_audit/__main__.py` | `demo --output NEW_DIRECTORY`; refuses to overwrite demonstration outputs |

`docs/scaffold_review.md` records an independent review of these components.
The review found and repaired concrete exposure-identity and covariance checks.
The test suite also verifies analytical variance, recentering invariance,
measurement convolution, historical leakage and deterministic workflow behaviour.

## Intentionally still to implement after feasibility

- Archive acquisition adapters and validated real-data fixtures.
- File-level historical version and first-availability resolution.
- Exposure/event alias reconciliation and overlapping cadence-range detection.
- Astronomy time conversion and independent transit midpoint fitting.
- Exact ExoClock Table 5 reproduction, including original uncertainty conventions.
- Full hierarchy of equal planet / equal origin / equal event weights. The
  current mean helper is sufficient for the one-origin demonstration only;
  production must first calculate origin/horizon means explicitly.
- A fitted, chronological recalibration procedure and its calibration uncertainty.
- Full-distribution handling for asymmetric/non-Gaussian timing posteriors.
- Production cohort construction, frozen horizon bins and source-quality rules.
- The full simulation matrix, sample-precision analysis, real figures and results.
- An observing-opportunity model or genuine telescope-allocation evaluation.

These are task-board items, not silently stubbed production functions.

## What the demonstration establishes

It demonstrates that the package can construct a chronological synthetic split,
fit a linear ephemeris, forecast later events and write correctly labelled
scores. Half the artificial planets have a deliberately introduced late drift.
That contrast is an illustration of model misspecification, not a fitted
description of exoplanets and not evidence that real forecasts are miscalibrated.

The included output records the RNG seed, Python and NumPy versions. Re-run in a
new directory to compare semantic outputs. Small floating-point differences
across numerical-library versions are possible; exact bitwise portability is
not a scientific requirement.

## Environment

Core: Python >=3.11, NumPy >=1.26,<3. Tests use `unittest`; no external test runner
is needed. Astronomy-specific dependencies should be added only when an audited
adapter or light-curve task needs them. Capture exact dependency versions and
platform details for every real analysis using `scripts/capture_environment.py`.

Dependency ranges enable installation; they are not a frozen scientific runtime.
After the real pipeline is selected, commit a reproducible lock/environment
specification and its platform limitations. Do not call the seed environment
capture a universal dependency lock.
