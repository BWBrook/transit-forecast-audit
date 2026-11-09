# D076: synthesise now, with bounded accuracy and calibration claims

Codex (GPT-6.1-sol), 9 November 2026, from `d7f4bea`. I accept D075's decision
to stop the new-block triage experiment and proceed to the integrated rewrite.
T021 is closed unexecuted. S74–S97 remain closed. No release or new access is
authorised; Barry reviews the rewritten products before release.

The saved numerical outputs of `t020_review.py` reproduce exactly without
rewriting them. The principal corrections concern what those outputs prove.
The new independent audits supply stronger evidence for the bounded negative
allocation result, and narrower wording for accuracy, calibration and advice.

## 1. The allocation result is structural within its fixed empirical problem

Mean absolute realised error is a hindsight ranking, not an optimal capture
allocation. A planet with an enormous error may remain uncaptured after a pad,
while one with a small error may be cheaply recovered. Event counts also
change the equal-budget comparison. Correct the review script's docstring:
failure of that ranking alone does not prove every possible ranking fails.

The displayed ceiling also mixes comparators: its earlier entry is the weaker
proportional comparator, while the other two are the stronger additive one.
To beat **both**, compare with the larger capture fraction. The corrected
loose-ceiling margins are −2.052, +1.492 and +0.668 percentage points. The
"at most 1.5 points" statement is defensible after that repair; a positive
loose bound alone does not establish impossibility or that a gain has no value.

An exact finite-allocation calculation now answers the missing question. For
every fixed positive pad, optimise over ALL subsets of ceil(10% of intended
planets), with costs counting all intended events and capture averaging accepted
events within accepted planets. This covers every permitted allocation,
including ones no observer could know in advance. Best achievable joint gains:

| Saved population | Best minimum capture gain against both comparators |
|---|---:|
| S56–S73 | −8.7745 percentage points |
| Inspected 2026 | −3.6937 percentage points |
| Pooled | −4.3786 percentage points |

Every optimum uses the smallest allowed pad, 15 min; every other permitted
positive pad/flag set has an equal or smaller joint gain. The later and pooled
optima DO beat proportional allocation slightly, but lose to additive. Say
"cannot beat both", not "the optimal oracle loses to each".

This is a structural result for these saved accepted outcomes, q and
15/30/60/120/240-minute pad grid. It is not a theorem about every warning rule,
other budgets, true transit capture or future populations. It supports ending
this search without retuning it. Three exhaustive-enumeration regressions
and nine separate parent brute-force cases check the optimisation. The
independent allocation audit also reproduces 87 saved numerical cells.

## 2. Accuracy: observations in a selected population, not an incidence claim

Use this form:

> In the frozen core, 2,185 accepted timings on 151 planets had a pooled-event
> median absolute DRD prediction difference of 1.115 min (equal-planet-mass
> median 1.315 min). For 150 of those 151 planets, every accepted timing lay
> within 27 min of the prediction. HR858b was the sole accepted planet with
> errors exceeding 60 min and three forecast SDs, on all sixteen accepted
> events; its maximum absolute error was 404.04 min.

The non-HR858 maximum is 26.29898 min: "all within 26 min" is false.
Only 149 planets satisfy that literal bound. "Within about 26 min" or
"within 27 min" works with its stated accepted-timing denominator.

DRC earlier and 2026 event-weighted median absolute errors are 0.968 and
1.201 min; their maxima are 30.39 and 36.62 min. All 128 accepted DRC-core
planets in the pooled developmental comparison stay below 37 min on these
observations. Do not imply continuous monitoring or a complete population
of every ExoClock planet. Keep earlier/2026 development separate from the
frozen DRD test and label each quantile's weighting.

The intended frozen core contains 156 planets and 3,103 opportunities. Five
planets have no accepted timings. Recovery, catalogue-period identification,
P/4 matching, shape and numerical-support restrictions select the accepted
sample. Thus "one in 151" is an observed accepted-sample count, not an
estimated catalogue-wide failure probability. No error can be assigned to
unrecovered events from these tables.

## 3. Calibration: conditional measured-time coverage

Use this form:

> Under the reconstructed C2 covariance and supplied measurement-likelihood
> model, M0's nominal 95% intervals covered an average 90.79% of accepted
> measured timings per planet; the conditional host-bootstrap interval was
> [87.78%, 93.40%]. M2 increased this to 97.58%, with a ratio of mean interval
> widths of 1.666. The predeclared joint-refit score comparison remained
> inconclusive.

This is conditional evidence of undercoverage of the **reconstructed,
measurement-convolved** distribution. It does not directly identify the
catalogue SD alone as too small, recover issued covariance, or establish
latent-time calibration. The measurement likelihood, shape treatment,
selection and visit-dependence assumptions remain substantive. Event-weighted
M0 coverage is 91.95%, so "90.8% of transits" without weighting is misleading.

Keep the original joint-refit primary interval [−1.840, +2.196] separate from
the S105 sensitivity's fixed-fit conditional interval [−1.880, +1.124]. The
latter was not a rerun of primary joint uncertainty. Both are consistent with
the qualitative null verdict, but their widths cannot be compared as a
measurement-perturbation effect.

## 4. Measurement noise and observing advice

The precision ratios and gain from quadrature-combining reported sigmas are
consistent with measurement uncertainty contributing substantially to narrow-
window misses. They do not identify which misses were caused by measurement
noise. The combined-sigma calculation is also a Gaussian surrogate, not the
full non-Gaussian convolution used by the frozen score. Replace "most misses
are measurement noise" with that bounded interpretation.

A post-review descriptive check adds 1/2/3 minutes to EVERY forecast half-window.
In the accepted frozen DRD sample, +3 min raises measured-midpoint capture to
94.01%, not complete capture. On the full intended list it adds 18,618 midpoint-
window minutes (310.3 hours), before any duration/baseline/visibility accounting.
This is an illustration of this surrogate endpoint, not a validated scheduling
policy or a new selected T020 rule. Do not prescribe a universal few-minute pad,
claim it fixes the misses, or call the extra observing time negligible.

Full-transit capture requires true timing, durations, baseline and observatory
constraints. Those were not tested here. The useful practical statement is
that small absolute timing differences can coexist with narrow uncertainty
windows, and that operational window design needs its own decision model.

## 5. HR858b: strong case evidence, not a validated warning

Multiple independent implementations on the SAME SPOC photons reproduce its
large timing departure; b early, c late and nearly on-time d support an
astrophysical interpretation and disfavor a simple common clock offset.
No new independent photons or pixel/centroid validation were supplied. Retain
these limits rather than claiming all extraction/identity errors or unique
dynamical attribution are excluded.

HR858b is absent by the matched name from DRB/DRC and appears in DRD. Its
released timing inputs end in November 2020, span 756.48 days and have
standardised residual RMS 2.198 about the issued line. Bonfanti's pre-DRD
TTV evidence and these historical inputs could have prompted scrutiny.
They do not establish a prospective rule that would have caught the eventual
miss. "Rare and visibly failing" or "could have been caught" overstates this
single retrospective case. Say the warning information predated issue, while
its predictive usefulness was not validated. Do not generalise to all new,
old, sparse or TTV-labelled ephemerides from one case.

A hypothetical zero failures among 183 fully observed independent equal-risk
hosts gives a one-sided 95% binomial upper limit 1.624%; a two-sided 95%
Clopper–Pearson interval has upper endpoint 1.996%. The current 183-host lead
is not such a qualified trial, and ascertainment/horizon vary. This is an
optional design illustration, not evidence for a failure rate or a reason
to open the block now.

## 6. Rewrite can proceed

Suggested neutral title: **A frozen test of ExoClock forecasts: minute-scale
agreement and an hour-scale exception.** The article should lead with the
frozen question, selected population, conditional calibration and inconclusive
primary score; the exact allocation result and HR858b are secondary evidence.
The brief must preserve the same denominators and avoid a catalogue-wide rate
or generic padding recommendation. The guide should retain the scoring and
selection traps, evidence map and closed-block status.

Use C043–C061 for original results and C063–C064 for this review's corrected
descriptives/exact allocation result. The D075 review script's numerical tables
are reproducible, but its oracle/ceiling interpretation and the memo's 26-min
bound need explicit corrections during T022. No new results are required before
Claude drafts the three products; Codex reviews the resulting rewrite, then
Barry reviews. Nothing is released by this decision.

Evidence: `docs/audits/d075_accuracy_claims.md`,
`docs/audits/d075_oracle_audit.md`, `results/d075_review_checks/receipt.json`,
and the adjacent audit scripts/receipts. No raw photometry or headers were read.
