# Sprint 2 statistical review and corrections

Codex, 7 November 2026. Table-only review of the designs committed at
`2c39f0a` and `9375b3c`, analysis code and committed development results. No
photometry, FITS header, posterior grid or remote data source was opened.
Original sprint-2 results remain unchanged. Corrected results are separate in
`results/sprint2_review/statistics/`.

## Decision changed by two analysis defects

**t015v3 passes its prespecified replication on the fixed production product
set. t015v3c still fails confirmation.** The original replication failure and
its attribution to sparse hosts cannot support a scope restriction.

1. **Product preference was conditioned on success.** `analyse()` passed only
   timed rows to `production()`. A host with an available but failed SPOC product
   could consequently contribute its FFI timing. The fixed rule specifies SPOC
   when available, and FFI only when SPOC is absent. Availability must be read
   from the full attempt ledger, before filtering to successful timings.
2. **Asymmetric interval containment was reversed.** The ledger defines
   `err_s = fitted - truth`, `lo95_s = fitted - q025`, and
   `hi95_s = q975 - fitted`. Correct containment is
   `-hi95_s <= err_s <= lo95_s`; analysis used
   `-lo95_s <= err_s <= hi95_s`. The same correction applies after multiplying
   the two interval widths. Among successful SPOC removal injections, the
   incorrect expression disagrees with the ledger on 14 confirmation and 28
   replication events. Correct containment agrees with the ledger on every
   successful injection in all three samples.

The repair changes the analysis and figure product selector; it does not change
the frozen timing rule, source photometry, matching, host weights, margins or
sampling design. Two regression tests cover failed-product preference and
asymmetric interval containment. `analyse --output` writes a separate summary.

## Corrected prespecified calculations

These are the repaired production implementation's original sequential RNG
schedule, seed 20261107, with 10,000 host resamples and 90% percentile intervals.
Every noise-ratio control also passes. The independent script reconstructs all
historical production point estimates to their recorded four-decimal precision
and reproduces the corrected estimates and decisions using separate aggregation
and closed-form weighted regression; its independent bootstrap stream gives
slightly different Monte Carlo endpoints.

| Sample and rule | Hosts / injections | z-RMS [90%] | Coverage [90%] | Mean z [90%] | Tmag 9 interval | Tmag 13.5 interval | Decision |
|---|---|---|---|---|---|---|---|
| Confirmation, t015v3c primary | 105 / 1495 | 1.0576 [1.0206, 1.0941] | .9309 [.9171, .9439] | -.0003 [-.0563, .0555] | [.9468, 1.0471] | [1.0604, 1.1932] | fails coverage and faint endpoint |
| Confirmation, t015v3 secondary | 105 / 1495 | .9891 [.9558, 1.0213] | .9470 [.9349, .9583] | -.0003 [-.0516, .0518] | [.9769, 1.0693] | [.8762, 1.0004] | passes, secondary |
| Replication, t015v3 primary | 100 / 1374 | 1.0144 [.9787, 1.0509] | .9502 [.9382, .9611] | .0690 [.0116, .1239] | [.9666, 1.1252] | [.8611, 1.0697] | passes every criterion |

SPOC assessed separately passes every criterion in both samples. The replication
production set consists entirely of SPOC products. FFI assessed separately fails
replication: z-RMS 1.0883 [.9896, 1.2069] and coverage .9336 [.9106, .9534],
with endpoint failures too. The declared qualifying product scope is therefore
**SPOC 120 s**, conditional on successful identification and timing, within the
sample's single-DRD-planet, Tmag < 13.5, S56–S73, PDCSAP domain. The specified
rule does not become qualified for FFI or multi-planet hosts through pooling.

This is a pass of the stated injection-calibration criteria. It does not
qualify the identification procedure, establish calibration of every stratum,
resolve the real-data WASP-54b defect, or freeze the protected experiment.
Corrected bright-stratum production coverage is .9288 and .9262; its uncertainty
is broad and its mean-bias bound is not qualified separately.

## Sparse-host explanation

The erroneous fallback contributes TOI-712 in confirmation (one FFI injection),
and HD23472 (two FFI injections, z = 2.7842 and .9079) and K2-403 (one FFI
injection, z = -3.8762) in replication. Both replication hosts have failed SPOC
identification, so neither belongs in the fixed production calibration subset.
Development has a corresponding K2-3 fallback.

Correct production replication retains only two hosts with at most three timed
injections. They supply six injections, with equal-host z-RMS 1.1180 and coverage
.8333. Those two hosts cannot establish a sparse-host calibration failure. The
full corrected 100-host sample passes without excluding them. The original
98-host >=4 split still has z-RMS 1.0122, but its apparent improvement over the
full sample was predominantly created by the invalid product fallback.

The split counts *successful injections across two phase runs*. It is not a
count of four observed physical transits in a sector. It is also selected after
seeing the residuals and success statuses. A future metadata restriction would
define a new population and cannot inherit confirmation from this split.
Retain equal-host weighting for this prespecified target. Switching to expected
sealed-era event weights now would change the estimand, not repair an error.

## Margins: correct illustrative arithmetic, limited interpretation

For independent Gaussian forecast error with SD sigma_f and outcome error with
SD k*sigma_y and mean delta*sigma_y, let r = sigma_y/sigma_f and
q = Phi^-1(.975). Nominal forecast coverage is exactly

```
Phi(( q*sqrt(1+r*r) - delta*r)/sqrt(1+k*k*r*r))
- Phi((-q*sqrt(1+r*r) - delta*r)/sqrt(1+k*k*r*r)).
```

The design's table reproduces: outcome-dominant coverage is .925216 for k=1.10,
delta=0; .968913 for k=1/1.10, delta=0; .947419 for k=1, delta=.15; and .922513
for k=1.10, delta=.15. The largest stated loss is 2.749 percentage points. At
r=2.6 the last scenario gives .926113. The analytic JSON also records the
corresponding expected standardized IS95 under these assumptions.

These numbers justify an explicit scientific tolerance under the stated
Gaussian shift/scale scenario. They are not a distribution-free bound, a
validated tolerance for the primary M2-minus-M0 score contrast, or a consequence
of that inconclusive contrast. They also do not bind every Tmag group: the
allowed endpoint scale 1.15 with bias .15 gives outcome-dominant coverage
.908971. Global RMS and mean constraints do not rule out heterogeneous tails.
The directly tested coverage criterion supplies additional injection evidence;
its interpretation remains conditional on the injection design and population.

## Regression and bootstrap qualification

The host mean square is unbiased for that host's second moment. Replacing its
logarithm with an arithmetic response fixes the previous log-MSE bias. The
square root itself is nonlinear and is not exactly unbiased. OLS estimates the
linear projection of host second moment on Tmag; interpreting its two endpoint
predictions as conditional calibration requires an adequate linear mean model.
The endpoints do not certify every stratum or tail of the conditional
distribution. Negative fitted endpoint predictions are clipped to zero; none
affects the decisive full-sample corrected intervals.

The original negative controls omit the coverage estimator, although coverage
was a decisive criterion. Their 300-replicate ranges also have appreciable Monte
Carlo uncertainty. A bounded independent control now uses the corrected
replication's actual host counts and Tmag design, 600 synthetic replicates and
600 host resamples per replicate:

| Truth | RMS interval coverage | Coverage interval coverage | Tmag 9 / 13.5 interval coverage |
|---|---|---|---|
| Unit Gaussian | .900 | .880 | .887 / .885 |
| Unit-variance t5 | .868 | .875 | .840 / .870 |
| Gaussian with true coverage .930 | .890 | .902 | .882 / .868 |
| Gaussian with true coverage .925 | .872 | .880 | .870 / .895 |

Monte Carlo SE near 90% is .0122. At the .930 coverage boundary, the lower-bound
criterion passes in .065 of runs (Monte Carlo SE .0101), versus the nominal
one-sided .05 interpretation; at true .925 it passes in .0167. This is a
bounded check, not a proof of uniform error control. Keep the published
percentile rule and its finite-sample limitations visible; do not silently
reinterpret its pass as an exact 95% guarantee. No margin or interval method was
changed to obtain the corrected pass.

The existing `check` command also looked for uncompressed `dev/ledger.csv` and
otherwise used D039, whereas the committed ledger is compressed. The repair now
reads the actual sprint-2 development ledger through the existing plain/gzip
loader and declares that source. A compressed-ledger regression test verifies
the supplied host-product counts and stops before simulation. Historical controls
were not regenerated or overwritten.

## Replication legitimacy and prior contact

The two confirmation samples contain disjoint hosts. Committing a fixed t015v3
replication after the primary t015v3c failure is defensible as a new prespecified
test; it does not convert the first sample's secondary pass into confirmation.
The second design and selection precede its injection run, and the frozen timing
source hash remains the same. No optional third test is needed after correcting
arithmetic errors in this test.

The claim that replication hosts were never sampled is too broad: 82/120 had
already been remeasured in R5, and 81/120 have the same host-sector in that
remeasurement. First confirmation has 85/120 overlapping R5 hosts, all in the
same sector. New phases are a distinct calibration target, but reused noise,
shape fits and prior inspection are not independent raw evidence. Code freeze,
the hash draw, no feedback into rule tuning and separate reporting support the
bounded conditional test. The design's blanket assertion that a fixed test
"keeps its error rate whatever motivated the test" needs independence or an
appropriate conditional argument; it does not follow from code freeze alone.
Report the actual contact and avoid calling either R5-overlapping sample an
untouched-host validation.

## Reproduction and verification

```
.venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm --bootstrap 10000 --output results/sprint2_review/statistics/confirm_corrected_summary.json
.venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm2 --bootstrap 10000 --output results/sprint2_review/statistics/confirm2_corrected_summary.json
OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 .venv/bin/python scripts/review_sprint2_statistics.py
.venv/bin/python -m unittest discover -s tests -v
```

The complete suite passed after the final loader repair: 83 tests at the
shared-workspace state of this review.
The separate reconstruction checks historical arithmetic, corrected containment,
host metrics and criteria without importing the timing pipeline. Input SHA-256
hashes, corrected per-host values, independent summaries, analytic margins and
synthetic-control results accompany this review. Original summaries are retained
as the record of the error. The highest-value integration step is to correct the
scientific products and keep conditional SPOC calibration, identification
readiness and protocol freeze as separate decisions.
