# D075 accuracy, calibration and interpretation audit

Codex (GPT-6.1-sol), 9 November 2026. Independent arithmetic from saved
outcome, forecast and score tables, not `scripts/t020_review.py` or its
helpers. No raw photometry, headers, candidate-sector data or network requests
were opened. Reproduce with `.venv/bin/python scripts/d075_accuracy_audit.py`.
Compact output and source hashes are under `results/d075_accuracy_audit/`.

## Decision

Support synthesising the existing evidence without opening S74–S97. Do not
accept D075's general accuracy/calibration, noise-causation or practical-padding
sentences as currently worded. The numerical error description is useful once
its sample, weighting and selection are stated. The mathematical allocation
claim is addressed by the separate oracle audit; this report does not assume
that mean-absolute-error ranking is an optimal capture policy.

## Accuracy: numbers reproduce, scope and one threshold need correction

The frozen DRD primary has 2,185 accepted mid-times on 151 planets, from 3,103
intended events on 156 planets. There are five zero-accepted planets:
HIP94235b, TOI-251b, TOI-262b, TOI-269b and TOI-4308b. Accepted-event accuracy
is not accuracy of all intended events, all catalogue planets or all observing
attempts. Timing recovery/acceptance and the DRD P/4 consistency gate can
remove outcomes; those limits remain material to any failure-rate claim.

- The event-weighted median absolute DRD error is **1.1148 min**. The
  equal-planet-mass error median is **1.3149 min**, and the median of each
  planet's median is **1.3555 min**. These are different summaries; specify
  which one the paper uses. The default planet-balanced analysis should not
  silently use a pooled-event median just because it rounds nearer one.
- Exactly **149**, not 150, of the 151 accepted planets have every accepted
  timing within **26.0 min**. GJ1252b reaches **26.29898 min**. The other 150
  planets besides HR858b have every accepted timing within **26.4 min** (or
  safely round to 27 min); their maximum is 26.3 min when rounded to tenths.
- HR858b's maximum is **404.0423 min**. Sixteen accepted events exceed 60 min,
  all from that planet. This agrees with the recorded one-planet gross-miss
  finding under the >60 min AND >3 forecast-SD definition.
- The DRC earlier slice has 1,078 accepted events on 92 planets (1,493 intended
  events/93 planets); the 2026 slice has 1,974 accepted events on 128 planets
  (2,771/129 intended). Their pooled set has 3,052 accepted events on 128
  planets. These are current-roster hosts restricted to DRC-core metadata,
  not all 450 DRC planets and not a representative all-catalogue panel.
- DRC event-weighted absolute-error medians are **0.9685 min** and **1.2007
  min**; equal-planet-mass medians are **1.0518** and **1.3427 min**.
  The maxima **30.3872** and **36.6157 min** reproduce. None of these accepted
  errors exceeds 60 min. The inspected blocks do not supply continuous
  surveillance of every transit between 2022 and 2026.

Allowed wording:

> Among the accepted timings in the frozen DRD core sample, the median absolute
> forecast error was 1.31 minutes under equal-planet weighting. Apart from
> HR858b, every accepted timing on the other 150 planets was within 26.4 minutes
> of its issued prediction. These statements condition on recovery and the
> declared acceptance rule.

> In the inspected DRC-core development blocks, the largest accepted error was
> 36.6 minutes among 3,052 timings on 128 planets. This is a selected
> development sample, not a catalogue-wide or continuous-time guarantee.

Avoid “issued forecasts are accurate to minutes” as an unqualified title-level
conclusion. “Minute-scale errors among accepted timings, with a coherent
multi-hour departure in one system” preserves both observations.

## Calibration: retain the estimand and covariance convention

Direct independent equal-planet aggregation of saved scores gives:

| Quantity | M0 | M2 |
|---|---:|---:|
| Planet-balanced measured-time coverage95 | 0.9079365 | 0.9757620 |
| Event-weighted measured-time coverage95 | 0.9194508 | 0.9647597 |
| Planet-balanced mean convolved width95 | 10.4851 min | 17.4730 min |

The ratio of mean widths is **1.66646**; it is not the width ratio for every
planet/event or the forecast-only observing window. The existing conditional
host-bootstrap coverage intervals are [0.87779, 0.93403] for M0 and
[0.95821, 0.98891] for M2. The M0 interval is below nominal 0.95 under this
conditional observation/acceptance specification. This is stronger than an
unqualified point comparison but does not identify which source of uncertainty
is misspecified.

“95% intervals contained 90.8% of transits” is inaccurate in two ways:

1. 90.8% is a mean of planet-level coverage fractions; the pooled-event fraction
   is 91.95%.
2. These are **convolved measured-time predictive intervals** under the
   declared measurement likelihood and C2 covariance reconstruction, not the
   original forecast-only intervals or latent transit-capture intervals.

All 2,185 forecast rows explicitly say `released-input WLS reconstruction;
not issued covariance`. Published marginal errors plus reconstructed T0–P
correlation are not the original issued joint posterior. C2 must be visible
in the methods and label for any precision/calibration claim.

Allowed wording:

> Under the declared C2 covariance reconstruction and measurement-likelihood
> convention, M0's nominal 95% measured-time predictive intervals had 90.8%
> planet-balanced coverage among accepted timings. The frozen M2 correction
> raised this to 97.6% while widening mean convolved intervals by
> a factor 1.67; its net score advantage remained inconclusive.

Do not infer that the catalogue's ephemeris SDs alone are too small, or estimate
a universal correction factor, from this aggregate. Measurement-likelihood
misspecification, covariance approximation, system departures, and selection
are not identified separately by this statistic. Also retain the score's
conditional propriety assumptions rather than asserting calibrated latent
capture probabilities.

## Noise and padding: descriptive sensitivity is not causal allocation advice

D075 correctly recomputes event-median reported measurement/forecast sigma
ratios 2.7296 (earlier) and 1.6916 (2026). Replacing a forecast-only Gaussian
width by the quadrature-combined width raises measured-midpoint coverage to
0.9338 and 0.8764. That calculation is a **Gaussian surrogate** using the
reported sigma even for non-Gaussian timings; it is not the exact retained-grid
convolution used by the frozen score.

The increase cannot demonstrate that “most misses are measurement noise”.
Making a window wider necessarily captures more measured points. The sigma
ratio is compatible with an important measurement contribution under the
working observation model, but the data here do not decompose individual
residuals into latent forecast error and measurement error. Nor does this
endpoint force uniform padding to win as a theorem: that depends on the
error distribution, event counts, flag fraction, costs and chosen pads.

The following additional calculations are explicitly illustrative, after
review, and do not extend or retune T020's locked pad grid. They keep C2
forecast-only windows, add the stated pad to each **half-width**, and evaluate
accepted measured midpoints with equal planet weights:

| Accepted measured-midpoint capture | No pad | +1 min | +2 min | +3 min |
|---|---:|---:|---:|---:|
| DRC earlier | 0.5566 | 0.8135 | 0.9002 | 0.9455 |
| DRC 2026 | 0.6229 | 0.8279 | 0.9000 | 0.9438 |
| DRC pooled | 0.5979 | 0.8240 | 0.8993 | 0.9473 |
| DRD frozen primary | 0.5733 | 0.8013 | 0.8959 | 0.9401 |

Thus 1–3 minutes improves this proxy; it does not “fix” all misses or establish
actual observing capture. The added full-window cost is 2–6 minutes per
intended event, before overhead, duration, baseline or visibility. Budgets in
the audit count every intended event, including missing outcomes. For example,
uniform +3 min adds **18,618 midpoint-window minutes** to the 3,103-event
frozen DRD manifest, from 14,540 to 33,158 minutes. This does not demonstrate
that the cost is negligible beside a historically verified transit duration,
which is absent from the exact release inputs.

Allowed wording:

> In a post-review descriptive sensitivity, uniform 1–3 minute half-window
> padding increased capture of accepted measured midpoints. This illustrates
> sensitivity of that proxy to narrow windows; it is not a validated observing
> policy or a full-transit capture probability.

## HR858b and rarity: strong case evidence, not a prospective warning rule

The named HR858b entry is present in DRD and absent from the saved DRB/DRC
ledgers. Its released DRD timing table has 16 rows, ending BJD 2459169.2599
(2020-11-15 as a TDB calendar label), spanning 756.4836 days. The issued-line
standardised residual RMS is **2.19783**; nominal chi-square/(N−2) is
**5.52052**. These descriptors and the existing verified pre-issue Bonfanti
reference were available reasons for caution. The released rows are not an
independently certified mask of observations retained in the catalogue fit.

The independent checkers use different analysis implementations on the same
SPOC photons, with SAP/PDCSAP sensitivities. They are independent **analyses**,
not independent photometry. Coherent b/c/d behaviour strongly supports an
astrophysical departure and consistency with known TTVs; it does not exclude
every extraction/blend/identity error or uniquely establish the dynamical cause.
No pixel/centroid validation is supplied. Do not silently restore the stronger
“physical effect proved”/“could have been caught” language qualified in C050.

A sensible case-study sentence is:

> Multiple analysis implementations reproduce HR858b's large coherent departure.
> Its old input timings, excess issued-line scatter and pre-existing TTV
> literature were reasons for caution available before DRD was issued. No
> predeclared warning policy was tested or shown to catch this failure.

One observed gross-miss planet among the **151 accepted** planets is not an
estimated general ExoClock failure rate. Five intended planets have no accepted
timing, other planets have missing events, and acceptance is not independent of
identification/coverage. Likewise zero positives in a selected DRC development
sample do not prove that triage is intrinsically unlearnable at some universal
rarity. It is sound to conclude that these data do not support training and
validating the proposed gross-miss rule, and to stop without accessing a new
block.

The optional “zero of 183 gives 1.6%” calculation is a **one-sided** binomial
95% upper limit, assuming 183 independent, completely observed host-level
binary outcomes. A two-sided 95% exact interval's upper endpoint is about 2.0%.
Neither number follows merely from 183 metadata candidate hosts.

## Interval scopes must not drift

The original primary interval [−1.83977, +2.19568] is joint host-refit
uncertainty. The perturbed S105 sensitivity [−1.879705, +1.123684] is a
**fixed-fit conditional** interval. D075 lists them in adjacent sentences
without labelling the change. Do not present the latter as a recomputed primary
joint interval or a like-for-like narrowing after measurement correction.

No frozen result, cohort, input, source script or primary verdict is changed
by this review. This audit supports a manuscript rewrite under these limits.
