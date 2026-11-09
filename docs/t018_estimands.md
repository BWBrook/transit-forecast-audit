# Scoring, timing and capture: interpretation for the revision

Codex (GPT-6.1-sol), 9 November 2026. This is post-review interpretation of
the unchanged frozen experiment, not an amendment to its primary endpoint.
The governing frozen specification is `results/freeze/freeze_manifest.json`
and its bound `configs/candidate_freeze.json`; older protocol notes record
the design history.

## Five quantities that must remain separate

1. **Latent transit mid-time.** The physical event time T is unknown. A
   forecast based on the issued ephemeris, reconstructed T0–period correlation
   and model M0–M3 is a distribution over T relative to its linear prediction.
   M0 is an issued-ephemeris reconstruction, not an issued joint posterior.
2. **Measured mid-time.** The pipeline reports Y and an estimated timing-error
   description from later photometry. The scored distribution convolves the
   forecast error with this supplied error description. Its coverage concerns
   Y, not necessarily T. The error description is estimated after issue,
   so the scored distribution is not a fully executable issue-time forecast.
3. **Accepted timings.** The score population consists of intended opportunities
   that satisfy the frozen identification, data-quality, numerical-support
   and event-matching rules. It is selected, not an ignorable random subsample
   of every transit. Outcome timing distributions are qualified conditionally
   on successful identification and timing, not on all missed events.
4. **Recovery of intended opportunities.** Each manifest opportunity receives
   one terminal status. Prediction-time cadence coverage is a diagnostic,
   not an acceptance gate; four accepted primary timings have unqualified
   coverage at their prediction. Neither non-recovery nor insufficient cadence
   at the prediction proves that an actual displaced transit was missed.
5. **Observing-window capture.** This requires the actual transit and required
   baseline to fall in a schedule chosen using information available before
   observation. Measured-time interval coverage and raw interval-score minutes
   are not capture probability and allocated telescope time, respectively.

## Conditional profile-likelihood timing distributions

The production timing core fixes a shape fitted to the planet-product transit
train. At each trial mid-time it profiles a local linear multiplicative
baseline by weighted least squares; it does not jointly marginalise over
the shared shape. A beta/red-noise and reduced-chi-square scale is estimated
from the fitted residuals and held fixed during the scaled timing-grid pass.
Normalising the conditional profile likelihood over the supported mid-time
grid gives the reported timing distribution and quantiles. Under a flat
mid-time prior it can be read as a conditional posterior for that fixed
nuisance treatment, not a marginal posterior including shape/noise uncertainty.
The scoring adapter enforces the flat-prior/support convention for saved grids.

The later calibration fit uses the declared diagonal-visit approximation.
Resampling hosts accommodates dependence in the aggregation; it cannot repair
an incorrect conditional timing likelihood or visit covariance. Common-shape
uncertainty propagation and joint nuisance fits are distinct checks, not
benefits automatically supplied by a host bootstrap.

## Selection and matching

The identification phase is searched without centring on the issued forecast
epoch, but it uses a catalogue period restricted to ±0.5%. The final terminal
assignment additionally rejects an otherwise accepted timing when its distance
from the issued prediction exceeds P/4 (`acceptance.terminal_status`). This
cycle-consistency rule is an outcome-selection restriction and must appear in
the methods. Blind phase search is not complete forecast independence of
the final accepted sample. Large within-product variations, period errors,
aliases and displaced events may fail identification or matching.

No unobserved event is assigned an ephemeris-error value. Per-planet binary
completion bounds in the Stage 0 outputs give unresolved indicators arbitrary
zero/one values and average each intended planet equally. They expose the
logical missing-data range only. They assume neither selection ignorability
nor a known measurement-error model for unmeasured events; they must not be
presented as latent-time or scheduling-capture bounds. Multiplying event
recovery by planet-balanced coverage mixes weights and is invalid.

## Three loss scales and uncertainty

All methods use the same divisor within each event. The primary standardised
IS95 divides by M0's forecast-plus-measurement predictive SD (grid variance for
non-Gaussian timings); it is a conditional weighted loss because the divisor
depends on an error estimate from the later observation. Forecast-normalised
IS95 divides by forecast SD alone. Raw IS95 is in minutes. These are different
loss weightings and can rank the methods differently; raw minutes are not
the duration of an observing window. Every event is averaged within planet,
then planets receive equal total weight. Paired host resampling keeps planets
of a host together.

An error estimate being computed after observation does **not by itself prove
impropriety**. Let A describe observation precision. If A is ancillary for the
latent forecast error conditional on origin information, the conditional
measurement model is correct, and each positive weight w(A) is common to all
methods, a proper conditional score remains proper after averaging over A:
each conditional expected score difference is nonnegative, as is its positively
weighted average. If recovery selection is also present, ignorability or an
explicit conditional selection model is additionally required. Those assumptions
have not been established for this pipeline's photometry-derived noise and
shape diagnostics or accepted-event selection. The appropriate claim here is
a conditional empirical loss comparison, not a theorem that every estimated
error bar invalidates proper scoring. This distinction changes interpretation,
not the frozen endpoint or its numerical result.

The frozen 2,000-draw joint-refit interval is the primary decision interval.
The additional three-scale and coverage intervals hold fitted forecasts fixed
and are descriptive conditional host-bootstrap intervals, not replacement
decisions. The s distribution comes from saved refit draws. The frozen
forecasts use plug-in fitted parameters; the bootstrap does not retroactively
integrate parameter uncertainty into their predictive intervals. Negative
controls with nominal 90% estimator-interval coverage 0.853–0.927 concern
injection-calibration estimators, not an empirical coverage guarantee for
the final nominal 95% score interval.

The intended inferential population is the empirical eligible host population
represented by this release, outcome rule and observing block. Resampling
does not sample alternative catalogue-construction practices, observing
seasons, structurally unrecoverable systems or unseen failure classes.

## Constraint on a future capture endpoint

For latent forecast limits [L,U], a fixed duration D and required before/after
baselines, the proposed schedule is
`[L − D/2 − baseline_pre, U + D/2 + baseline_post]`.
No later measurement uncertainty is added to that allocation. Later timing
uncertainty belongs to verification: report containment bounds or integrate
over an explicitly justified observation model when capture is ambiguous.
Duration/baseline uncertainty and resource costs need their own predeclared
treatment. Scoring accepted times cannot establish full-population capture.

The small synthetic tests in `tests/test_t018_repairs.py` demonstrate the
weighting and measurement/capture distinctions numerically. They are not a
new end-to-end photometry injection qualification or a power calculation.
