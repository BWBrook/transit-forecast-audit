# T015 review and chronological calibration check

5 November 2026 · Codex · starting source state `490ef7b`.

## Decision

Continue development, without freezing the outcome pipeline or adopting the
training-span correction. The timing pilot is useful, but its injections validate
a narrower conditional procedure than D034 claims. The production mixture is
now numerically repaired and has host-cluster uncertainty. A chronological
development check supplies adverse evidence against selecting training span:
its small point gain is unstable when the earlier training sample is resampled.

All light-curve products checked in this turn were the five already downloaded
2022 files in the T015 manifest. Only hashes and FITS headers were needed; the
injection audit used committed tables and source code. No new photometry was
requested and no protected outcome was opened. The post-2025-11-18 lock remains.

## D034: retain feasibility, narrow calibration claims

The 261 injection rows reproduce scaled z-RMS **1.03318**, white-error z-RMS
**1.25435**, and median timing error **−1.68 seconds**. Their 1/2/3-sigma
coverage is 66.28/94.25/98.85%. This supports conditional timing recovery for
known-shape signals injected into selected off-transit regions of five
already processed SPOC 120-second products.

It does not establish calibration of the complete timing pipeline or a
catalogue-wide ExoClock scale factor:

- Generation and recovery use the same fitted shape. Shape estimation,
  misspecification and spot crossings are not tested; injecting into PDCSAP
  also bypasses upstream detrending of the artificial transit.
- Exact replay of the random draws recovers 324 attempts and 261 accepted
  placements. **260 of 261 fitting intervals overlap another**, with 662
  overlapping pairs. The median elapsed-time overlap fraction is 64.2%.
  These are geometric intervals, not exact shared-cadence counts; the 46
  interval-union components are not an effective sample size.
- The reported interval 0.90–1.17 reproduces by resampling **26 parent-transit
  groups**, not 26 independent host stars. There are only **four hosts and five
  products**. All three recoveries beyond 3 sigma reuse one HD209458 noise
  region. Resampling four hosts cannot establish population transfer to the
  proposed faint/FFI target regime.
- Multiplying the sample median uncertainty ratio by injection z-RMS recovers
  the arithmetic 1.12, but does not identify an ExoClock measurement-error
  multiplier. Its quoted confidence interval has no committed generator.

Accept the descriptive same-photon timing comparison and conditional injection
result. Replace “the pipeline is calibrated” and “ExoClock errors are 1.12 times
too small” with that narrower statement. Agreement of WASP-80b's two reductions
supports the discrepancy against DRB surviving this pipeline choice; it cannot
exclude every shared photometric systematic.

The [injection audit](t015_injection_review.md) retains the reconstructed draws,
overlap geometry, weighting sensitivities and bootstrap calculations. The
[primary-method review](t015_method_sources_2026-11-05.md) places the beta
estimator against Winn, Carter & Winn and Cubillos: time averaging is a useful
heuristic, not a generative likelihood for correlated noise.

## Numerical and access corrections required in T015

The cumulative-grid convention has a small deterministic timing bias. A
symmetric Gaussian posterior sampled on the pipeline's two-second grid returns
a median one second early under `cumsum(weights)` interpolated at node centres.
A continuous trapezoid CDF removes this displacement in the synthetic check.
Grid refinement is still needed to check interval-width accuracy. This is a
numerical explanation relevant to the reported −1.68-second injection bias,
not a recalculation of the actual timings. Evidence: `grid_review.json`.

Other corrections before extending the pipeline are timestamp-aware beta bins
that respect gaps, an explicit residual-degrees-of-freedom convention (mid-time
plus two baseline coefficients), convergence/edge checks, and uncertainty from
the shared fitted shape and estimated scale.

All five raw-file hashes match the T015 receipt. Header conventions are
TDB/SOLARSYSTEM with BJDREFI=2457000. However:

1. Lightkurve's `download()` reads the FITS table before `clean()` checks TSTOP.
   The claimed pre-flux TSTOP guard is therefore not implemented. The sector
   search restriction is the actual pre-request protection in this run.
2. MAX_BTJD=3313.5 denotes 4 January 2024 in TDB calendar coordinates, about
   one day later than the comment's intended boundary. A time-scale conversion
   alone does not undo barycentric light travel or supply a universal spacecraft
   UTC cutoff. Correct the boundary using the declared time/reference convention
   and required observer/target information, or exclude ambiguous boundary
   products conservatively before requesting them.

These implementation defects did not cause a protected-era breach: the five
checked products all end in 2022. The [provenance audit](t015_provenance_review.md)
and its header-only script retain the evidence without claiming a fresh
astronomical time conversion.

## Production mixture: corrected summaries and host uncertainty

`scripts/forecast_variance_components.py` now uses the repaired SVD quadratic
with vectorized gradients, 384-node integration checked against 192 nodes,
continuous posterior summaries, explicit optimizer status and host resampling.
The earlier 48-node posterior labels are removed from the production path.
Outputs go to `results/pilot_v1/variance_components_v2/`, preserving the original
tranche-2 artifacts.

| Release | b | Host-bootstrap 95% interval | s | Host-bootstrap 95% interval |
|---|---:|---:|---:|---:|
| DRB | 2.24949 | 1.849–2.703 | 1.09314 | 0.119–1.563 |
| DRC | 0.97626 | 0.712–1.357 | 3.14869 | 1.576–4.211 |

There are 400 resamples per release, preserving all planets/windows within
each sampled host. These percentile intervals are conditional on a=1.087,
the selected cohort, diagonal published-marginal covariance and the model
family. They include training-sample variation, but do not validate model
selection or recover the missing issued covariance. Their difference from
profile intervals should not be attributed solely to host dependence.

The DRC tail quantities remain distinct: 29 posterior medians above lambda=10;
61.21 posterior expected planets above ten; model population probability 0.2323.
The previous independent reference values reproduce. Twenty synthetic replicates
at each of five truths remain a recovery diagnostic, not interval validation.

## Chronological development: small gain, unstable fitted rule

The new check fits population rules to source-record dates in **2022** and
scores dates in **2023 through 3 January 2024**, rebuilding visits separately
within each block. It uses 133 training planets on 131 hosts and 206 later
planets on 200 hosts. Twenty-three later planets belong to hosts represented in
training. Predictions use population rules, without updating individual lambda
from their earlier residuals.

The primary outcome scale is fixed at a=1.0 to avoid importing the full-era
estimated scale into the earlier training fit. Results at 1.087 and 1.2 are
declared sensitivities. Metadata standardization is learned from the early block.
The score is the joint log density for each planet divided by its number of
later windows, then averaged equally across planets.

This remains an **observation-cutoff development hindcast**. The predictor was
nominated after all these outcomes had been inspected. The early outcomes
precede conservative DRC publication, and their first-public availability is
unresolved. It is neither an untouched test nor a historically executable
Track A exercise.

The fitted span rule improves the later mean score over the constant mixture by
**0.01276 nats/window**, with a median improvement of 0.00355. Its point gain
stays about 0.013–0.014 under the two outcome-scale sensitivities. That apparent
stability does not survive training uncertainty.

In 400 joint host resamples, the early calibration is refitted before later
scores are computed. The span-minus-constant percentile interval is
**−9.072 to +0.04295 nats/window**. This is a diagnostic of a highly unstable
fitted rule, not a precise population interval to advertise. Independent
replays of four extreme replicates confirm the losses with higher-order and
adaptive integration. The failure is substantive:

- Some early resamples give nearly zero fitted heterogeneity and reverse the
  span coefficient's sign.
- Short-baseline later systems then receive smaller uncertainty multipliers
  even though they lie far outside the sampled training span distribution.
- In replicate 61, the span model has s approximately 0.000026 and a positive
  slope approximately 0.407. TOI-1130's assigned SD multiplier is about 0.39;
  that host dominates the large negative score difference.

A bootstrap that keeps the trained rule fixed misses this failure mode. Both
conditional and refitted summaries are retained in the output, together with
every replicate's fitted parameters. The
[extreme-case audit](chronological_instability_audit.md) provides a separate
reproducer. **Do not select the span rule on this evidence.** Any regularization,
minimum-tail rule or alternative mixing family must be specified and tested
wholly within development before it can compete for the final protocol.

The constant mixture's large point gain over the issued Gaussian is itself
concentrated: WASP-161 and TOI-1130 contribute about 19.14 of the 21.36 mean
nats/window improvement. Only 24.8% of planets improve and the median change is
−0.0941. This does not negate the proper-score comparison, but it explains why
tail realism and interval-width/coverage evaluation matter before calling the
correction broadly useful.

## Handoff before freeze

Claude can take the T015 corrections and a prespecified stratified validation
design: distinct hosts/products, primary non-overlapping noise windows,
shape-refitting or independent shape draws, detrending sensitivity, and
separate calibration/validation records. Report central and tail coverage along
with scale and bias. A ±3% scale target must be justified by independent
host/product replication and empirical dependence; adding overlapping trials
does not supply that precision.

A frozen algorithm may estimate a sector-specific noise scale from that sector's
flux, provided the entire rule and treatment of its uncertainty are fixed and
validated beforehand, without using the forecast residuals to tune it. The
present 4–12 overlapping placements per parent transit do not qualify that rule.
Retain sensitivity scales until adequate validation exists.

Exact sealed-era target windows/product availability and the complete citation
screen remain open. They are required before freeze; this turn does not replace
the approximate inventory with new counts.

Reproduction commands:

```bash
python scripts/review_t015_injections.py --bootstrap 100000
python scripts/review_t015_grid.py
python scripts/review_t015_provenance.py
python scripts/forecast_variance_components.py --reps 20 --bootstrap 400
python scripts/chronological_calibration.py --bootstrap 400 --a 1.0
python scripts/chronological_calibration.py --bootstrap 0 --a 1.087
python scripts/chronological_calibration.py --bootstrap 0 --a 1.2
python scripts/review_chronological_extremes.py
python -m unittest discover -s tests -v
```

The provenance script uses Astropy in the existing T015 analysis environment;
other scripts use the project's analysis extra. Compact receipts retain hashes,
seeds and commands. Synthetic checks are explicitly labelled.
