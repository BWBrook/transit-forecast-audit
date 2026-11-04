# Independent review of development tranche 2

5 November 2026 · Codex · source state `7a9f1a6` · inspected development data only.
No TESS light curves were opened. The protocol remains unfrozen and the
post-2025-11-18 lock remains in force.

## Decision

Continue D029 as a candidate prospective experiment. D026's conditional
heteroscedastic result reproduces, and D027's broad between-planet spread
survives stable numerical integration. Revise the individual tail labels,
their interpretation and the schedule inventory before freezing. Shorter
training span is a useful development predictor to test chronologically;
TESS inclusion alone is not supported as a useful predictor here.

This is a numerical and methodological review, not validation of the physical
origin of the timing errors or an untouched forecast result. Claims C008–C011
and decisions D030–D033 index the evidence. Original tranche-2 artifacts remain
available as historical evidence; this review supersedes the specific claims
identified below.

## D026: the heteroscedastic refinement is supported conditionally

An independent implementation constructs orthonormal error contrasts that
remove each window's intercept and slope, then diagonalizes their covariance.
It does not reuse the original normal-equation likelihood. Across four
parameter settings, the two likelihoods differ by the same parameter-independent
constant to less than `1e-7`.

On the same 4,173 timings, 726 windows and 336 planets (334 hosts):

| Quantity | Independent result |
|---|---:|
| Common scale a | 1.086576 |
| Common additive jitter tau | 5.005 seconds |
| LR: add scale to jitter | 27.3895 |
| LR: add jitter to scale | 1.4761 |
| Scale-only a | 1.093846 |
| Host-bootstrap 95% percentile interval for a | 1.04984–1.12091 |
| Host-bootstrap 95% percentile interval for tau | 1.219–11.558 seconds |

The bootstrap uses 400 host resamples, seed 20261105; eight estimates land at
zero jitter. The percentile interval is not a boundary-calibrated detection
test or a universal physical upper bound. The LR of 1.48 provides little
support for additional common jitter after scaling.

Claude is right that a range of quoted uncertainties distinguishes a *common*
scale from a *common homoscedastic* additive variance under this model. That
qualifies the fixed-sigma counterexample in D022. It does not identify pure
measurement error: sigma-proportional latent/model error, heterogeneous jitter,
selection by the catalogue's neighbour filter and offsets removed by local
centering remain possible. The DRD-flag-excluded sample is an outcome-conditioned
diagnostic, not the origin-frozen forecast cohort.

Use a=1.087 (rounded 1.09) with 1.0/1.2 sensitivities in development. T015
still needs forecast-independent fits, injection recovery and explicit selection
checks before this becomes a validated outcome model.

Evidence: `results/pilot_v1/tranche2_review/noise_review.json`,
`noise_host_bootstrap.csv`, `noise_sigma_bins.csv`, `noise_tau_profile.csv`.

## D027: point estimates survive; tail labels require replacement

The independent likelihood whitens the visit means and uses an SVD to separate
the forecast subspace from the orthogonal residual. This avoids subtracting
large nearly equal quadratic forms. High-order Gauss–Hermite integration was
checked against adaptive integration over the standard-normal mixing variable.

| Release | Planets / windows | b | s | Posterior median lambda >10 / >100 |
|---|---:|---:|---:|---:|
| DRB | 134 / 343 | 2.249489 | 1.093143 | 2 / 0 |
| DRC | 316 / 837 | 0.976260 | 3.148683 | 29 / 9 |

The DRC estimate from 48-node quadrature was close (s=3.133), but its objective
was spuriously about 0.137 log-likelihood units better than accurate integration.
Orders 192, 256 and 384 converge, and adaptive integration confirms the optimum.
The broad heterogeneity therefore survives this numerical challenge.

Two defects matter for subsequent work:

1. **Tail labels were discretized by quadrature nodes.** Counting posterior
   medians from the 48-node approximation gave 15 DRC planets above lambda=10;
   continuous posterior integration gives 29. The >100 count changes from ten
   to nine. These are posterior classifications conditional on this model,
   never direct observations of individual calibration factors.
2. **The original rank-two algebra becomes unstable at extreme mixing scales.**
   High-order quadrature explores values at which cancellation creates enormous
   positive log likelihoods. Ordinary-scale dense tests do not cover this failure.
   Use the stable reference likelihood before extending the quadrature order or
   fitting predictors; retain the original outputs as the reviewed baseline.

Three tail quantities must remain distinct: the number of posterior medians
above ten; the sum of individual posterior probabilities of exceeding ten;
and the model-implied population probability `1-Phi(log(10)/s)`. The last is
about 23.2% for DRC; the posterior expected count is 61.21. Neither is 29/316
or the old 15/316. Halving the posterior grid changes log medians by at most
`3.3e-6`. None of these quantities is an observed
missed-transit fraction. For a new planet, integrate the population mixing
distribution; do not insert a posterior lambda learned from its later outcomes.

Stable profile intervals are DRB b=1.828–2.723, s=0.708–1.568 and DRC
b=0.699–1.301, s=2.690–3.724. These remain conditional on the model and
independent-planet likelihood, without host-dependence qualification. See
[the numerical review](tranche2_mixture_review.md). The original 20-replicate recovery
experiment also does not validate a heavy-tail family, exposure independence,
coverage under misspecification or transfer to DRD.

Evidence: `mixture_real_fit.json`, `mixture_quadrature_convergence.csv`,
`mixture_planet_posterior.csv`, `mixture_rank2_dense.csv` and `mixture_receipt.json`
in the review output directory. Missing issued T0–P covariance remains missing;
the diagonal published-marginal convention here is still a sensitivity model.

## Issue-time metadata: a bounded predictive test

The metadata parser separately reads the hash-verified DRC release. The 18,170
released timing rows cover 450 planets; 316 enter this development comparison.
They are treated as the released fitted-input collection, whose completeness
has not been independently established. Row ranges and per-planet row hashes
are preserved. Repeated literature IDs are usually publication identifiers,
not proof of duplicate exposures. Nearest-epoch counts are summaries, not
validated independent-event counts.

Three univariate predictors were fitted directly in the **population mixing
distribution**, avoiding regression on unstable posterior lambda labels:

`median SD multiplier = exp(intercept + beta * standardized predictor)`.

Five folds hold out entire hosts (309 hosts, 316 planets, fixed seed 20261105).
Scaling is learned within each training fold. The comparison is against the
constant mixture, using each held-out planet's joint predictive log density
divided by its number of windows, then averaging equally across planets.

| Predictor | Mean improvement, nats/window | Paired host-bootstrap 95% interval |
|---|---:|---:|
| log10 released training span | +0.02709 | +0.00673 to +0.05399 |
| log10 number of unique training epochs | +0.00869 | −0.00352 to +0.02316 |
| TESS included in training | −0.00129 | −0.00280 to +0.00002 |

For training span, the full-development slope on log SD is −0.507 per SD of
log10 span (0.290 dex); shorter spans imply larger uncertainty multipliers.
This is a predictive association, not an explanation of the catastrophic cases.
Literature-only inputs have no variation in this cohort, and historical
multiplicity is unavailable in the acquired issued tables, so neither is fitted.

This was one random host split and three explored predictors. Its bootstrap is
conditional on the fitted folds; it excludes training/model-selection and split
uncertainty. The globally fixed a=1.087 was estimated using the same development
era, including held-out hosts; it was not re-estimated within folds. Thus this
is a conditional comparison, not end-to-end refitted cross-validation.
It is neither chronological validation nor sealed evaluation, and
does not establish a gain over the issued Gaussian. It nominates training span
for earlier-only validation, without selecting a final model.

All 1,264 held-out densities were checked by adaptive integration: the largest
absolute discrepancy from 384-node integration was `2.41e-7` log units. Separately
fitted 192/384-node predictions differed by at most 0.00199 log units. Evidence:
`metadata_*`, `predictor_fits_q*.csv`, `predictor_host_cv_q*.csv`,
`predictor_review_q*.json` and `predictor_validation.json`.

## D028/D029: revise the metadata inventory before using its counts

The official [HEASARC sector schedule](https://heasarc.gsfc.nasa.gov/docs/tess/sector.html)
was acquired as schedule metadata only, with a retrieval timestamp and hash.
It establishes several corrections:

- S98 spans 9 November 2025 to 5 January 2026, longer than 27.4 days.
- S99 is interrupted from 15 to 22 January; special sector 1751 lies outside
  the standard-sector inventory.
- S100 runs 2 February to 1 March 2026 and straddles the conservative DRD
  availability boundary. Classify events by time, not the sector number alone.
- S110 runs 31 October to 26 November 2026. On 5 November it is in progress;
  its full-sector predicted transits are not all already observed.
- The code's stated “day after publication” JD 2461082.5 is actually
  11 February 2026 UTC. The intended 12 February value is 2461083.5.

These are calendar-date facts, not barycentric exposure windows. No UTC/date-only
schedule number was subtracted from a BJD_TDB forecast in this audit. Exact
eligibility still needs time-system handling, actual target coverage, data gaps
and public product availability. The alternate official STScI orbit CSV ends at
S42 and cannot settle these sealed-era windows.

The old 224/171-planet and 5071-transit counts are geometric approximations, not
verified available-outcome counts. This review does not recompute them. Refresh
the metadata-only inventory before selecting the frozen evaluation cohort.
Evidence: `schedule_calendar_review.csv`, `schedule_review.json`.

## Next handoff and reproduction

Claude can proceed with T015 on 3–5 inspected development events. The parallel
method task is to replace the unstable likelihood/posterior labels in the
development pipeline, establish host-aware uncertainty and test the training-span
predictor chronologically. Keep proper scores as the prospective target; compare
the lognormal family with one prespecified alternative before freeze. The
[dated literature review](literature_update_2026-11-05.md) establishes heavy-tail
prior art but leaves the full ExoClock citing-paper screen open.

From the repository's analysis environment:

```bash
python scripts/review_tranche2_metadata.py
python scripts/review_tranche2_noise.py --bootstrap 400
python scripts/review_tranche2_mixture.py
python scripts/review_tranche2_predictors.py --order 192
python scripts/review_tranche2_predictors.py --order 384
python scripts/review_tranche2_predictors.py --verify
python scripts/review_tranche2_schedule.py --acquire
python -m unittest discover -s tests -v
```

The schedule command reuses immutable cached bytes; `--acquire` permits only the
two named schedule URLs when absent. Other commands use already inspected release
tables. Synthetic unit tests are numerical checks, not astronomical results.
