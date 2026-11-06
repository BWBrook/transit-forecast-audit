# Independent sprint-1 forecast and scoring review

**Review date:** 6 November 2026. **Protected outcomes accessed:** none.

## 1. Scientific decision

The forecast likelihood, predictive convolution, interval score and
planet-balanced aggregation are numerically sound for the inspected development
experiments. The current evidence does **not** establish that M2 improves the
primary score under the adopted outcome convention. At `a = 1.087` and the C2
covariance reconstruction, the joint-host bootstrap interval crosses zero in
both comparisons:

| Development comparison | Training design | Scoring design | M2 − M0 standardised IS95 | 95% host-refit percentile interval | Decision |
|---|---:|---:|---:|---:|---|
| Release-transfer proxy | 15 planets / 15 hosts | 238 planets / 232 hosts | −2.44494 | [−5.75623, 0.18733] | Inconclusive |
| Chronological proxy | 133 planets / 131 hosts | 206 planets / 200 hosts | −2.62847 | [−6.35065, 0.06749] | Inconclusive |
| Delayed-origin reconstruction | 15 planets / 15 hosts | 235 planets / 229 hosts | −2.43456 | [−5.72904, 0.37275] | Inconclusive |
| Later-published training proxy | 66 planets / 66 hosts | 238 planets / 232 hosts | −2.49666 | [−5.86210, 0.24243] | Inconclusive |

Smaller loss is better. The delayed-origin reconstruction is the cleanest
availability-aware hindcast: both DRC artifacts were public by 27 September
2022 15:26:09 UTC, the calibration origin is the next UTC day, and civil-date
scoring starts on 29 September. It establishes historical input availability
for a rule reconstructed now. The rule was not actually issued, its family was
chosen after later development outcomes were inspected, and it is neither
Track A nor untouched validation.

The appropriate sprint-1 conclusion is therefore **continue to sprint 2, but
do not freeze or claim improvement**. M2 remains a scientifically motivated
candidate because it repairs severe undercoverage and tail density. Sprint 2
must determine the outcome-error convention, independent event-cycle mapping,
complete I1 provenance and a genuinely frozen evaluation before the primary
contrast can support a population claim.

## 2. Evidence and assumptions

### What the point estimates mean

M2 changes predictive width even though its median latent forecast scale is
fixed at `b = 1`. With the release-transfer fit
`s_log_lambda = 2.16188`, its central 95% half-width relative to M0 is 2.75
when measurement error is negligible, 2.02 when outcome and forecast SDs are
equal, and approximately 1 when outcome error is 100 times the forecast SD.
The implementation therefore matches the intended population scale-mixture
semantics.

For release transfer, M0 planet-balanced 95% coverage is 0.8840 and M2 coverage
is 0.9561; mean 95% width rises from 10.13 to 16.44 minutes. Mean negative log
score falls from 19.55 to 6.46. For the chronological comparison, coverage
rises from 0.8975 to 0.9545, width rises from 10.82 to 19.12 minutes, and mean
negative log score falls from 21.60 to 6.49.

Those mean gains are not typical-planet gains. Only 23.5% of release-transfer
planets and 19.4% of chronological planets improve in standardised IS95; the
median planet changes are +0.931 and +1.174, respectively, so most planets get
worse. TOI-1130 and TOI-125 contribute about 69% of the release-transfer mean
gain and 86% of the chronological gain. Removing those two hosts leaves point
deltas of −0.780 and −0.364. The proper score is correctly rewarding avoidance
of catastrophic tail failures, but the result must be described as tail-risk
reduction rather than broad per-planet improvement.

### Outcome-error and covariance dependence

The primary standardisation divides every method's IS95 by the common M0
predictive SD, including the supplied outcome error. Because that error is
estimated after issue and may depend on the observed flux, this is a
conditional weighted loss, not an unconditionally proper issue-time score.
The raw minute score and forecast-only normalisation remain necessary
sensitivities.

The decision changes close to `a = 1`: at C2, both comparisons' 95% bootstrap
intervals fall just below zero for `a <= 1.0` and cross zero for `a >= 1.05`.
At `a = 1`, only 3 of 200 sensitivity-bootstrap replicates are positive in
each comparison; the empirical 99th percentiles are positive. The nominal
classification is therefore tail-resolution-sensitive as well as dependent on
an outcome scale that remains a conditional development estimate. It should
not be presented as a robust threshold.

At `a = 1.087`, the M2 point delta ranges from −5.89 under `rho = -1` to −1.47
under `rho = +1` for release transfer, and from −6.43 to −1.54 chronologically.
Every corresponding host-refit interval crosses zero. C2 and zero-covariance
results are nearly identical, but this does not identify the missing issued
covariance. No C3 planet occurs in the current training or scoring cohorts; the
interface must still preserve C3 for future cohorts.

### Data-generating and observation assumptions

The forecast is a catalogue linear ephemeris fitted to heterogeneous timings.
The scored observations are successful catalogue mid-times, conditional on
timing extraction and catalogue inclusion. The experimental unit for the
population contrast is a planet; events are weighted equally within planet and
hosts are the resampling clusters. Repeated events, shared reductions and
shared shape fits are not new planets. The released catalogue does not contain
the denominator of failed or missed observations, and current exposure lineage
is incomplete.

All four comparisons use inspected development outcomes and model choices made
after inspecting this development era. Their scale of inference is the stated
catalogue cohort under the fixed reconstruction and error convention, not all
transiting planets, attempted observations or genuinely prospective forecasts.

## 3. Checks performed

The executable review is
`scripts/review_sprint1_scores.py`; its machine-readable output is
`results/sprint1/scoring_review/numerical_checks.json`.

- In 851 random dense covariance comparisons with condition number below
  `1e10`, the stable rank-two SVD likelihood agreed within `3.90e-6` log units.
  Another 149 deliberately ill-conditioned dense solves were excluded as an
  oracle because their condition numbers approach machine precision; this is
  the cancellation the SVD implementation is designed to avoid.
- Analytic likelihood gradients agreed with central finite differences within
  `3.07e-8` absolute and `5.52e-9` scaled error across 60 comparisons.
- Against adaptive integration over `s = 0.1..5` and outcome-to-forecast SD
  ratios `0.01..100`, the maximum predictive-quantile error was `9.46e-5`
  forecast-SD units and the maximum negative-log-density error was `8.85e-6`.
- Two hundred Gaussian score cases agreed with closed forms to at most
  `4.55e-13`; an asymmetric likelihood-grid convolution agreed with its
  analytic Gaussian convolution to `8.89e-16` and confirmed the offset sign.
- The four primary-detail artifacts contain 2,324, 1,925, 2,320 and 2,324
  events, with exactly four method rows per scored event. Forecast variances
  recompute exactly, parameter hashes agree, planet weights sum correctly, and
  all reported aggregate metrics reaggregate from `scores.csv` to floating
  point precision.
- Repaired interface counterexamples now reject blank product/flux metadata,
  reject unequal forecast/attempt sets, reject a non-Gaussian likelihood with
  zero forecast variance, and emit a valid header plus receipt when every
  production attempt fails.
- Current development cycle assignment produces no realised adjacent-cycle
  wrap: the maximum absolute residual is 0.1093 period and no event exceeds a
  quarter period. This numerical fact does not establish an independent epoch
  assignment.
- `.venv/bin/python -m unittest discover -s tests -v` passes all 70 tests. The
  expected pre-existing DRD Table 5 one-boundary-count mismatch is printed by
  the reproduction test and remains scientifically qualified under D020; it is
  not a test failure.

## 4. Uncertainties, limitations and next decisions

One scientific interface issue remains, and two demonstrated implementation
gaps were repaired during this review without changing the current catalogue-
development numbers:

1. `development_events()` derives cycle number by rounding the scored mid-time
   against the issued ephemeris. No current residual is wrapped, but sprint 2
   must supply an independently mapped scheduled/local epoch so a future
   catastrophic miss cannot select its own adjacent cycle.
2. The reusable outcome adapter now enforces the I1 column set, core provenance,
   file hash, cadence order, BJD reference, identification method and period,
   detector location, coverage, leave-one-out status and failure reason. The
   complete synthetic I1 row passes and a blank identification method is
   rejected. This closes the demonstrated schema-gate defect.
3. `make_forecasts` now emits planet-specific C2/C3 tiers and labels C2, zero
   and `rho = +/-1` sources separately. The pre-fix direct experiment already
   carried the correct numerical rho and tier, so this repaired I2 metadata
   defect did not change the reviewed scores.

The final integration reruns all four comparisons under a start/end
source/config hash guard. The reviewed numerical findings are unchanged; final
receipts are checked by `scripts/sprint1_handoff.py`, which also verifies source
and summary hashes. Earlier receipts were superseded because integration
changed source files after those runs. No protected data were accessed.

The next scientific decision is not which model has the best inspected point
estimate. It is whether sprint 2 can produce a complete attempted-outcome
ledger and independently qualified uncertainty convention, then freeze M0–M3,
cycle identity, covariance sensitivities and the host-resampling estimand
before any protected outcome is opened. If it cannot, the correct result is a
well-documented development finding about tail undercoverage, not a forecast-
improvement claim.
