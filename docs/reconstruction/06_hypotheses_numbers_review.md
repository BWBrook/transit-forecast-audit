# Reconstruction review: hypotheses and numerical wording

Reviewer draft by Codex, 10 November 2026, from `0f390f3`. This is input to
thread 156 and Barry's reconstruction exercise, not a change to the frozen
article, brief, bibliography, analysis or scrivmark round. Saved tables only;
no raw photometry, headers, candidate-sector data or new fitting were used.

## Overall judgment

Support the reader-first reconstruction and keeping the reusable comparison
product prominent. The new narrative must preserve the distinction between
questions fixed before the protected test, development-motivated expectations,
and explanations suggested after seeing the results. An expectation can be
reasonable physics without being a documented prior prediction of this study.

## 1. Which hypotheses were actually recorded before unblinding?

The checked pre-access record is `bc85326` (the source commit bound by the
freeze). Its `docs/project_brief.md`, headed "Proposed hypotheses, before
seeing the final outcomes", has a DIFFERENT hypothesis set:

- H1: conditional calibration under a correct linear model/reliable input
  errors, explicitly without assuming a direction of departure;
- H2: information span/patchiness may predict performance beyond nominal
  precision, stated as an association rather than a causal claim;
- H3: earlier errors may contain transferable calibration information;
- H4: precision can have an observing-window cost, requiring attempted-
  observation denominators before claiming a missed-transit rate.

The bound `configs/candidate_freeze.json` fixes the later empirical question
and the primary M2–M0 standardised interval-score comparison, including its
joint host-refit decision rule. It does not preregister the reconstruction's
new H1–H3 formulations or tests of their proposed mechanisms. The old IDs
must not be silently reassigned as if this were the original hypothesis list.
This checks the named design/protocol records, not an assertion that no similar
idea ever appeared anywhere in the project's correspondence.

| Reconstruction item | Status and recommendation |
|---|---|
| H1: minute-level accuracy because period error grows linearly | A theoretical motivation/descriptive question, not the recorded prior hypothesis. Linear growth says how error propagates, not that its size is minutes: that also needs the period error, covariance, horizon and stable-period assumptions. Report observed minute-scale agreement without "H1 holds strongly". |
| H2: undercoverage because omitted TTV/activity/instrumental noise | Directional undercoverage is a plausible development-motivated expectation, but the recorded initial calibration hypothesis had no preferred direction. Coverage is conditional on reconstructed covariance and the supplied measurement likelihood; it cannot identify omitted physical/instrumental noise as the cause. Do not say the causal H2 is supported. |
| H3: failures concentrate in interacting/new/sparse/old systems | There is earlier motivation for span/TTV sensitivity, but the specific concentration claim is not a tested predeclared comparison. One accepted gross-miss case cannot establish an association, its concentration or a warning rule. Keep it as a post-outcome future hypothesis/case interpretation, not a supported prior prediction. |
| H4: previous-release tail correction improves the later release | This has the strongest prospective standing: transferable recalibration was an original hypothesis and the specific M2–M0 contrast was frozen before protected access. Keeping it as a question/aim in the short narrative is fine, provided the original prespecified primary comparison is still identified. Its result is inconclusive, not evidence of no effect. |

A compact honest framing for step 2 is:

> We asked whether issued uncertainties describe later measured timings and
> whether a correction learned from an earlier release improves a frozen
> interval-score comparison. We describe accuracy and the exceptional case;
> possible warning features remain hypotheses for future testing.

The abstract need not carry a hypothesis list. If step 1a requires one, mark
historical status beside each candidate; do not call the reconstructed set
"genuine prior predictions" without a dated source.

## 2. Three requested number checks

### Recovery: 92% is numerically right, its current denominator label is wrong

From `results/final_primary/terminal_ledger.csv.gz`:

- all intended opportunities: 3,103;
- accepted timings: 2,185, or **70.4157%**;
- opportunities with qualifying cadence coverage **around the predicted time**:
  2,369;
- accepted among that coverage-qualified subset: 2,181, or **92.0642%**;
- four additional accepted timings have unqualified prediction-time coverage.

Thus "92% of those TESS observed" is too broad. Cadence qualification is not
simply whether TESS observed the target or caught the actual displaced transit.
Nor is 2,185 the numerator of that 92% fraction. Use:

> We accepted 70% of intended opportunities and 92% of those with sufficient
> TESS data around their predicted times.

Keep the two exact numerator/denominator pairs in the product/flow table.

### Released-input scatter: 2.198 is standardised RMS, not a hard error limit

Independently recomputing HR858b's sixteen released input rows about the
issued DRD line gives:

- sum of squared standardised residuals = **77.2872429152**;
- RMS of standardised residuals = **2.19782908394**;
- chi-square divided by nominal N−2 = **5.52051735109**.

"Twice as widely as their errors allowed" risks treating quoted errors as
hard bounds or claiming a noise mechanism. Use:

> Its input timings ended in 2020 and had standardised residual RMS 2.2
> about the issued line.

For a new reader: "its inputs scattered about the forecast line by roughly
twice their quoted errors" is an acceptable descriptive shorthand, if the
metric/conditional fitting-membership qualification is supplied later. These
released rows are not independently certified as the exact retained fit mask.
The observation cannot distinguish forecast-fit inadequacy from a particular
error source or validate a warning policy.

### DRC horizon: about four years is defensible

The latest accepted DRC comparison is `WASP-53b|S107|DRD1179`:

- fixed DRC prediction BJD_TDB **2461288.9637577003**, calendar label
  **2026-09-05 11:07:48 TDB**;
- corresponding measured time BJD_TDB **2461288.96531764**;
- forecast first-public anchor **2022-09-27 15:25:16 UTC**.

Numerically comparing those date labels gives about **1,438.82 days** or
**3.9393 Julian years**. This is a coarse horizon description, not an exact
UTC-to-barycentric elapsed-time conversion or eligibility calculation. The
minute-scale reference difference does not change "up to about four years".
The earlier slice reaches about 1.182 years after issue. Use:

> In inspected development blocks reaching about 3.94 years after DRC's issue,
> every accepted timing on 128 planets was within 37 minutes of its prediction.

This does not mean every planet was followed continuously for four years, or
that the whole DRC catalogue had that performance.

## 3. Other material wording in steps 1a, 1b and 2

- **"Blind to/without reference to forecasts":** the search is epoch-blind
  within a catalogue-period range, but terminal acceptance requires the
  quarter-period forecast match. The present step 2 names that gate; steps
  1a/1b should not claim complete forecast independence. Use "catalogue-period
  searches, with the measurement and acceptance rule frozen in advance".
- **Accuracy denominators/weights:** 1.1148 min is the pooled-event median
  absolute error; the equal-planet-mass median is 1.3149 min. The 26.4-min
  statement concerns every ACCEPTED timing of 150 of 151 ACCEPTED planets.
  Do not write "every transit" without that qualifier.
- **Coverage:** 0.90794 is the mean within-planet coverage of accepted measured
  times under C2 covariance reconstruction and supplied measurement
  likelihoods. Its [0.87779,0.93403] interval is conditional. It does not show
  catalogue SDs alone are too narrow or the physical cause in proposed H2.
- **Primary uncertainty:** −0.121 [−1.840,+2.196] is the frozen joint host-refit
  result. A short methods sentence can say "we jointly resampled stars and
  refitted the correction"; plain resampling omits why its uncertainty differs
  from conditional secondary intervals.
- **HR858b:** the pattern supports an astrophysical interpretation and
  disfavors a simple common timing offset, not every measurement/identity
  error. Independent algorithms share the same SPOC photons. Replace "the
  signature of TTVs, not measurement error" accordingly.
- **Use:** observed minute-scale agreement in selected accepted timings is
  not assurance that an observing window is safe. Replace "Observers can
  trust ExoClock's windows to minutes" with a statement of the product's use
  for inspecting errors and testing methods; operational capture still needs
  duration, baseline, selection and observation constraints.
- **Prior art:** step 1a's blanket "not tested on an issued transit catalogue"
  and step 2's "almost never" are not established by the bounded literature
  screen. ExoClock IV/Shan and the later-timing checks already discussed in
  D076/D078 require an accurately limited contribution statement. A simple
  motivation is: "Refitting an ephemeris does not by itself test how an
  earlier forecast performed on later observations."
- **Product-first framing:** it can guide presentation, but cannot retrospectively
  change which comparison was prespecified as primary. The table/DOI is a
  planned deliverable until actually built and released.

## Evidence and reproducibility

The compact reviewer receipt `results/reconstruction_review/number_check.json`
records independently checked counts, the scatter calculation, horizons,
source hashes and the pre-access design commit. It is saved-table arithmetic,
not a new scientific analysis. The original reconstruction drafts and all
frozen products remain unchanged by this reviewer.

Next: Codex parent — integrate the clear wording fixes and preserve unresolved
framing choices for thread 156/Barry.
