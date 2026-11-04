# Independent review of the T015 injection diagnostic

**Decision, 5 November 2026:** accept the committed injection point estimates as
conditional development diagnostics. Do not accept them as an estimate of a
catalogue-wide TESS or ExoClock uncertainty multiplier, and do not freeze the
proposal to apply each outcome's own injection z-RMS. The reported 1.03 central
scale is numerically correct; its stated uncertainty and scope need narrower
language.

This review used only the committed T015 CSV/JSON outputs and source code. It did
not open FITS flux, acquire data, or inspect any protected outcome. The compact
reproducer is `python scripts/review_t015_injections.py`; exact input and source
SHA-256 hashes are recorded in
`results/t015_review/injection_review.json`.

## Scientific target and scope of inference

The injection experiment estimates the conditional RMS of

\[
z = (\hat t_c-t_{c,\mathrm{inj}})/\hat\sigma_{t_c}
\]

for accepted artificial transits placed in selected off-transit regions of five
already detrended SPOC 120-s light curves. The recovery uses the same fitted
transit shape that generated the injection, while its error is rescaled from the
same local residual window by beta times the square root of reduced chi-square.

This is a useful test of the timing fitter and its self-scaling rule conditional
on these products and a known shape. It is not an end-to-end test of SPOC
detrending, shape estimation, spot crossings, faint targets, other cadences, or
the population of ExoClock outcomes. The sampling units are four host stars,
five host-sector products, and 27 parent transits; 26 parent transits yielded at
least one accepted injection. “26 host-transit clusters” must not be shortened
to 26 host clusters.

## Numerical reproduction

The RNG replay exactly recovers all 261 recorded phase and offset pairs from
seed 20261105, to the committed rounding. The pipeline attempted 324 placements
(12 for each of 27 timed transits), rejected 63 on coverage, and retained none
for HAT-P-12b S49 epoch 2. All exact phases lie in the specified 0.25–0.40 or
0.60–0.75 bands. The closest injection fitting window remains 860 min clear of
the nearest nominal real-transit centre after allowing for its full half-window,
so accidental overlap with a real transit is not the issue.

| Quantity | Independent result |
|---|---:|
| Injection rows | 261 |
| Mean z; z-RMS with scaled sigma | -0.134; **1.03318** |
| z-RMS with white sigma | **1.25435** |
| Median recovered-minus-injected time | -1.68 s |
| Coverage within 1, 2, 3 sigma | 66.28%, 94.25%, 98.85% |
| Low-phase / high-phase scaled z-RMS | 1.08496 / 0.97278 |

Thus the statements “scaled z-RMS 1.03” and “white z-RMS 1.25” reproduce. The
central 1-sigma coverage is also close to nominal. Tail calibration is less
settled: three rows exceed 3 sigma, and all three are HD209458b S56 epoch 6
placements at phases 0.392–0.396 that reuse almost the same flux window. They
are one noise-region failure, not three independent failures.

## Flux reuse and dependence

The injections are not 261 independent real-noise realizations. Multiple
placements around each parent transit reuse the same off-transit cadences.
Using the exact replayed phases and the pipeline's fitting half-windows:

| Geometry diagnostic | Result |
|---|---:|
| Rows overlapping at least one other injection window | 260 / 261 |
| Overlapping window pairs | 662 |
| Median shared fraction among overlapping pairs | 64.16% |
| Connected interval-union components across five products | 46 |
| Union support / sum of nominal window lengths | 32.18% |

The same calculation from the rounded CSV phases gives 260 rows, 662 pairs, 46
components and 32.17%, so rounding does not drive the finding. Per-product
details are in `injection_overlap_by_product.csv`.
These are overlaps and support fractions of elapsed-time fitting intervals,
not counts of shared quality-selected cadences. Gaps are not reconstructed by
this CSV-only calculation, and 46 components is not an effective sample size.

The committed report's interval is reproducible as a bootstrap over the 26
**parent-transit** clusters while retaining row weighting:

| Aggregation or resampling level | Clusters | Row-weighted bootstrap 95% interval | Cluster-balanced z-RMS |
|---|---:|---:|---:|
| Parent transit | 26 | 0.899–1.173 | 0.992 |
| Host-sector product | 5 | 0.886–1.133 | 1.014 |
| Host star | 4 | 0.910–1.134 | 1.020 |

The first row reproduces the reported 0.90–1.17 interval. The latter intervals
must not be read as stronger population evidence: nonparametric bootstraps with
only five or four top-level clusters are highly discrete and cannot learn the
between-host population. They are sensitivity calculations. Leave-one-host-out
row-weighted z-RMS ranges from 0.969 to 1.071, supporting stability within this
small selected sample. Event balancing changes the point estimate from 1.033 to
0.992 because accepted injection counts vary from 4 to 12 per parent transit.

The median-bias parent-transit bootstrap independently gives -3.91 to +0.14 s,
matching the reported rounded interval. This is conditional evidence against a
large median bias in these products, not a general upper bound of 4 s.

## Error-scaling estimator

The beta times square-root-chi-square procedure is empirically useful here, but
the implementation has limits relevant to freezing it:

- `beta_factor()` ignores its error-array argument, computes unweighted residual
  standard deviations, and forms bins by array order rather than actual elapsed
  time. A permitted cadence gap can therefore be binned as if adjacent. This is
  likely minor for these high-coverage windows but is not assured for FFI or
  interrupted products.
- Beta and reduced chi-square are estimated from the same injected window whose
  timing error is standardized. The experiment tests this self-normalized
  procedure, which is appropriate if that exact procedure will be reused, but
  does not estimate an independent transferable noise multiplier.
- The injected signal is multiplied into already processed PDCSAP flux and is
  recovered with the identical fixed shape. The test cannot reveal distortion
  introduced by detrending an actual transit, shape uncertainty, or a
  misspecified transit model. The original report correctly notes the known-shape
  limitation; it should also state the post-detrending limitation.
- The reduced chi-square denominator subtracts the two fitted baseline
  coefficients but not the fitted mid-time. With hundreds of cadences per
  window this makes only a small numerical difference, but the convention should
  be corrected or justified before freeze.

These limits do not invalidate the descriptive 1.033 result. They prevent the
stronger statement that the pipeline's full outcome errors are calibrated.

## ExoClock scale claim

The committed arithmetic is close but the inferential claim is not identified.
Across all 27 matched events, the median ratio of this pipeline's sigma to
ExoClock's sigma is 1.08292. Multiplying it by the injection z-RMS gives 1.11886,
which explains the quoted 1.12.

No committed generator produces the reported 0.96–1.29 interval. Holding the
observed 1.08292 ratio fixed and bootstrapping parent transits gives 0.973–1.271.
Jointly recomputing the median ratio and z-RMS in the same parent-transit
bootstrap gives 0.955–1.325. Neither exactly reproduces the quoted interval;
both are sensitivity calculations. Neither solves the scientific problem: four selected hosts do not
identify a population scale, and multiplying two sample summaries does not
propagate shape, selection, host, or product uncertainty.

The defensible statement is:

> For known-shape injections into accepted off-transit regions of these five
> selected SPOC 120-s products, the beta- and chi-square-scaled timing errors have
> z-RMS 1.03; white errors alone have z-RMS 1.25. The result is consistent with,
> but does not independently estimate, an approximately 1.1 outcome-error scale.

Do not state that this experiment shows “ExoClock sigma are 1.12 times too
small.”

## Recommendation before protocol freeze

Retain T015 as successful development evidence for numerical feasibility and
conditional central-scale calibration. Replace the per-outcome z-RMS freeze
proposal: 4–12 highly overlapping injections cannot support an outcome-specific
multiplier. Learn any correction hierarchically from a larger development set
of distinct hosts and products, with host-level uncertainty and non-overlapping
noise windows, then carry that pre-estimated rule into the sealed analysis.

The next validation tranche should stratify cadence, magnitude and product,
re-fit or perturb the injected shape, test transit-aware detrending, and use
time-aware beta bins. It should predefine whether the estimand is an event,
product, or host-population average. Independent light-curve-method review would
materially improve confidence before freeze because the remaining uncertainty
is about detrending and generative realism, not the arithmetic reproduced here.
