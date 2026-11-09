# Execution of the declared secondaries after unblinding

Codex (GPT-6.1-sol), 9 November 2026. The D065 primary result is audited
before these analyses. This document fixes executable conventions for the
secondary names/settings declared in the frozen config; it does not claim
that their entire implementation existed before unblinding. Frozen code,
config, input lists and primary results remain unchanged. No secondary result
can replace the primary decision rule or redefine its cohort.

## Descriptive strata and diagnostics

Average events within planet and then planets equally within every reporting
cell. Preserve empty/sparse cells and intended-event denominators. Prediction
coverage is a recovery diagnostic, not an additional timing-acceptance gate.
Report primary and exploratory extension separately; any combined row is
explicitly descriptive.

- Lead bands retain the earlier protocol's provisional `(0,1]`, `(1,3]`,
  `(3,5]` and `>5` years. Use 365.25 days per year and the declared availability
  anchor, with frozen predicted BJD event positions. This is a coarse metadata
  proxy, not an exact UTC-to-barycentric conversion; do not create finer bins
  from inspected outcomes.
- Tmag reporting adopts the existing development validation bins `<10`,
  `[10,11)`, `[11,12)`, `[12,13.5)`, plus outside-range/unknown categories.
  These boundaries existed before unblinding; their use for protected reporting
  is a dated implementation convention here. Also retain continuous per-planet
  metadata/results, without an additional fitted brightness model.
- Covariance tiers come from the frozen forecast rows, not the older protocol's
  conceptual tier names. Product type remains SPOC only. Cohort membership
  comes from the frozen roster.
- For gain-host influence, compute each host's contribution as the sum of its
  planet M2−M0 differences divided by the original number of planets. Rank
  negative contributions from most negative, breaking ties alphabetically.
  Remove whole gain hosts, k=0..5, and reweight remaining planets equally.
  Parameters stay fixed. If fewer gain hosts exist, mark later rows unavailable;
  do not start removing loss hosts. This is descriptive, with no new exclusions
  or refit verdict.
- Later-state TTV labels use a dated official catalogue source chosen without
  reading scores or host rankings. A raw unflagged catalogue row does not prove
  absence of physical TTVs. Parameter-update dates are not discovery dates;
  whether a flag became known after the origin stays unknown. No label changes
  primary inclusion.

## Closed sensitivity cases

All fitting uses development data only and the existing Gaussian sigma68
calibration estimator; scoring keeps the I1 Gaussian/grid representation.
The primary calibration is the 206-planet development selection, not the
intersection with the final 156-planet roster. Reuse the frozen selection,
origin flags, visit construction, optimiser bounds and convergence checks.

| Case | Execution |
|---|---|
| Baseline | Reproduce frozen parameters, accepted rows and scores |
| Covariance zero / −1 / +1 | Apply the setting to both calibration and evaluation, refit on development, recompute forecast variances |
| All-SPOC training | Remove only the core-eligibility calibration restriction; evaluation unchanged; verify against the stored all-SPOC fit |
| Journal anchor | Restrict original intended events by frozen predicted time after the 2026-02-12 numeric UTC anchor with a ten-minute conservative exclusion screen; keep original training/parameters |
| C2 only | Restrict both calibration and evaluation to C2 candidates, refit on development |
| Outcome scale 1/1.1 or 1.1 | Scale calibration sigma and evaluation likelihood coordinates/sigma; refit on development; keep measured mid-times and grid masses fixed |
| Majority product gate | Additional gate on both calibration and evaluation; derive it from all recovered windows, including those outside the manifest; refit on surviving development timings |
| t015v3c | Apply the frozen Tmag multiplier to calibration and evaluation likelihood scales and refit on development; retain its failed-confirmation label |

The two-sided/refit convention follows the prefreeze sprint-1 sensitivity
precedent. Its adoption for each protected sensitivity is stated here rather
than retrospectively called fully prespecified. The journal filter is a
restricted numeric metadata sensitivity, not exact/exhaustive time eligibility;
it never uses measured residuals to select events.

The majority denominator includes coverage-qualified recovered timed, edge
and integration-unresolved windows. The numerator counts raw timed windows
without the two integration flags; a strict majority is required, and zero
covered windows fails. Normalise the integration status change: an old flagged
`timed` row and its new `integration_unresolved` label must contribute identically.
This retains D056's explicit inclusion of integration failures rather than
blindly applying a helper's older two-status list. Apply the gate in addition
to shared acceptance; rejected products remain in overall intended counts.

## Scoring and uncertainty

Recompute common M0 predictive-SD normalisation within each scenario,
including actual grid variance. Report raw and forecast-normalised scores
alongside standardised scores because changing that denominator changes the
loss weighting. Use exact adapter scoring, without a new approximation or
interpolation scheme. Record sample counts, exclusions, fitted parameters,
convergence/bounds, inputs and hashes.

The frozen formal decision remains the primary B=2,000 joint host-refit interval.
Secondary-specific joint-bootstrap counts and formal subgroup decision rules
were not fixed. Secondary comparisons are descriptive. If conditional
intervals are shown, use the existing B=10,000 host bootstrap and seed20261109,
clearly conditional on each scenario's fitted parameters. They do not include
calibration-fit uncertainty and cannot establish improvement of the learned
correction or replace the primary interval. Do not emit new secondary
improves/worsens/inconclusive verdicts from those conditional intervals.

No new model, cutpoint search, margin change, bias correction, exposure sample
or residual-based screening is authorised by this implementation.
