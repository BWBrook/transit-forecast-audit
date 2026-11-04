# Independent pilot review — 4 November 2026

**Decision: continue the development pilot, with narrower claims. Do not freeze
the proposed variance-components model or open the protected TESS outcomes.**

Codex reviewed Claude's `5ab90eb` pilot and Correspondence thread 137, message
2882. A separate base-R implementation checks Track R from raw files; the
Python diagnostic below uses the existing parser but independent projection
algebra. Specialist review checked that algebra and its interpretation. This is
development work, not held-out validation. No light curves were opened.

## 1. Independent reproduction and traceability

Run from the repository root:

```bash
Rscript scripts/independent_table5.R
python scripts/review_measurement_diagnostic.py
python -m unittest discover -s tests -v
```

The R implementation verifies all eight source-manifest SHA-256 hashes before
analysis. It reads the OSF bytes directly without importing the Python readers
or scoring code. Results are in
`results/pilot_v1/independent_review/table5_independent_summary.csv`.

| Release | Planets | Timings | <1 sigma (%) | <2 sigma (%) | <3 sigma (%) | <4 sigma (%) |
|---|---:|---:|---:|---:|---:|---:|
| DRB | 130 | 1585 | 48.01 | 76.53 | 93.50 | 98.30 |
| DRC | 308 | 3604 | 62.32 | 91.32 | 98.34 | 99.61 |
| DRD | 424 | 4716 | 66.41 | 93.70 | 99.28 | 99.96 |

The DRB/DRC columns match Table 5 exactly. DRD's published 66.39% differs by
one timing at the 1-sigma boundary. Unrounded publisher parameters are a
plausible explanation, not an established explanation. The Initial column
remains unreproduced. Thus **two complete columns reproduce exactly**, not the
whole table. The journal Table 5 was checked in the
[version-of-record repository copy](https://orca.cardiff.ac.uk/id/eprint/184907/1/pdf.pdf),
and its definitions against [arXiv v1 Section V.1](https://arxiv.org/html/2511.14407v1#S5.SS1).

The 42-planet exclusion and absolute-residual denominator reproduce the printed
numbers, but the Table 5 text does not specify that entire algorithm. Treat
this as a numerically supported reconstruction, not recovered author code or
proof that no alternative event list gives the same rounded aggregates.

`table5_event_trace_subset.csv` adds forecast and outcome raw line numbers for
the eligible members of the existing ten-planet queue. Join its release to
`table5_manifest_check.csv` for file identity and checksum. Full event tables
are regenerated under ignored `data/derived/independent_table5/`. The existing
pilot dossiers retain absent-outcome planets and the excluded WASP-12b control;
absence from the Track R subset does not erase those cases.

This establishes **file-to-row-to-calculation traceability**. Cadence/exposure
identities, original extraction windows and timing-prior bounds remain
unresolved; no strict Track A pair is certified exposure-independent yet.
Source-ID calendar dates are source fields, not independently verified UTC
timestamps. BJD_TDB remains release-stated, not independently converted.

## 2. D017: real excess scatter, unsupported attribution

The original diagnostic's 20-day threshold applies to successive gaps. It does
not constrain total group duration and does not identify a TESS sector/visit.
Among the 425 retained nonflagged groups, **333 span more than 20 days**, with a
maximum of **378.575 days**. This invalidates the stated short-visit justification.

`measurement_sensitivity.csv` preserves the original calculation and compares
total-span-limited groups and a fitted local slope. These are sensitivity
analyses on already inspected outcomes, not a selected production model.

| Grouping and local model, DRD flags excluded | Timings | Planets | Groups | Standardised RMS | sqrt(chi-square / df) |
|---|---:|---:|---:|---:|---:|
| Successive gaps <=20 days; DRD period fixed | 4563 | 349 | 425 | 1.1149 | 1.1107 |
| Total span <=20 days; DRD period fixed | 4173 | 336 | 726 | 1.1064 | 1.1020 |
| Total span <=20 days; local slope fitted | 4173 | 336 | 726 | 1.0968 | 1.0938 |

The local-slope fit uses two parameters and leverage-corrected residuals; its
residuals remain correlated. The table contains descriptive summaries, not
independent-event confidence intervals. Shortening groups changes membership;
these rows are not a paired causal estimate of the grouping effect.

The excess survives the grouping correction. However, a local residual contains
measurement noise, short-timescale physical timing variation, activity and
model error. The DRD period itself was estimated using these outcomes. Removing
a local mean also removes any common timing bias. Consequently the quantity is
**conditional local dispersion**, not an identified measurement multiplier `a`.

`synthetic_identifiability.csv` gives reproducible counterexamples (10,000
synthetic eight-event groups, seed 20261104). Measurement noise with scale 1.115
and correctly scaled noise plus independent Gaussian latent timing jitter of
SD 0.4932 have the same total variance and hence the same residual distribution.
A group-common offset of SD 2 is invisible after centering. These examples
demonstrate non-identifiability; they do not assert such jitter exists in TESS.

The published outcome selection requires agreement with nearby timings. That
conditions the local-scatter sample and prevents an unconditional calibration
claim. Its effect on coverage against an older ephemeris can have either sign:
it is a filter around contemporary neighbours, not necessarily around that
older forecast. No numerical correction for selection is supported yet.

The forecast's median share of the *reported variance* is 0.129 for the DRC
reproduction cohort (0.135 under origin-only flags). This is useful evidence
that measurement uncertainty dominates the denominator. It does **not** prove
that measurement error causes most observed misses.

The 5.06% result is the mean of planet-specific event failure fractions. It is
not the fraction of planets with any failure: that is 51/316 = 16.14% in the
origin-flag sensitivity, with unequal opportunities to observe a failure.

## 3. D016: useful covariance approximation, not posterior recovery

The weighted-pivot fitting method in ExoClock IV Section 3.1 supports approximate
decorrelation. The released inputs yield small WLS correlations at the published
pivot. But the published pivot is within half an epoch for 178/180 DRB,
425/450 DRC and 591/620 DRD cases, **not every case**. The issued MCMC joint
posterior has not been recovered, and agreement of refitted point estimates is
not proof of equality of posterior covariance.

`covariance_review.csv` quantifies the cross term using the reconstructed
correlation and published marginal errors. This is a hybrid **C2/WLS
sensitivity**, conditional on the source's linear-Gaussian fitting approximation
and the released input weights. It is not C1 covariance evidence.

Do not assign C2 blanket eligibility to all rows: material input/refit mismatches
require individual investigation or C3 sensitivity treatment.

For the Track R events, the largest absolute fractional changes in forecast
variance are 0.77% (DRB), 1.36% (DRC) and 8.14% (DRD); including measurement
variance reduces these to 0.27%, 0.98% and 2.94%. The correlations used are rounded
in the earlier audit, so these are approximate sensitivities, not rigorous
bounds on an unknown posterior. DRD is in-sample. Retain unrestricted covariance
sensitivity wherever the C2 assumptions cannot be justified.

## 4. Availability and the sealed era

Barry explicitly prohibited opening TESS light curves dated after 2025-11-18
until protocol freeze. That entire interval stays sealed. No new photometry
was fetched or inspected during this review.

D018's OSF upload date is not enough to establish public availability; D012
already recognizes this. The arXiv record gives submission on 2025-11-18, not
an independently verified public announcement time for the exact OSF artifact.
The [journal copy](https://orca.cardiff.ac.uk/id/eprint/184907/1/pdf.pdf) records
publication on 2026-02-11. Until earlier exact-parameter availability is verified,
strict Track A must use that conservative date with the protocol's boundary
rule. The protected interval and the eventually eligible evaluation interval
are different concepts. An investigator-unseen retrospective test must not be
described as a newly issued real-time prediction merely because it was sealed.

## 5. Next gate and scientific contribution

[The source review](literature_update_2026-11-04.md) finds prior art for TESS-only
timing-error diagnostics and extra variance (Ivshina & Winn 2022), as well as
injection-recovery timing validation. Neither local scatter nor a variance
multiplier is the novelty. The complete citing-literature sweep remains open.

Next, establish cadence-level lineage and validate a timing pipeline on 3–5
**pre-cutoff development events**, including controlled injections, failures,
timing-prior/window checks and shared-shape sensitivity. Agreement of two
reductions of the same photons is a pipeline check, not independent replication.
Do not open protected data to test this pipeline.

Before T014 fitting or T009 freeze, demonstrate what is identifiable. A model
for repeated residuals needs shared ephemeris covariance,
`b^2 X C_beta X'`, in addition to measurement covariance and a declared model
for discrepancies. A host bootstrap does not supply that fitting likelihood.
Start with a fixed outcome-error sensitivity and one forecast multiplier;
add an extra-variance term only if simulation with the actual metadata design
separates it. This is a proposal for the next methodological decision, not an
adopted fitted model.

The first-turn deliverable is therefore a strengthened, auditable development
pilot and a precise next feasibility gate. It is not a completed population
calibration study, a closed novelty claim, or a frozen evaluation protocol.

## Roles and verification

Codex (GPT-6) integrated the review, diagnostic implementation and decisions.
The base-R reproduction was delegated to the `gpt-5.6-luna` executor;
`gpt-5.6-sol` specialists reviewed primary literature and the diagnostic
algebra independently. Their agreement is supplementary; raw-byte reproduction,
numerical invariants, counterexamples and cited methods support the findings.
Runtime and hash receipts accompany the results. The initial 38-test suite and
a fresh 168-score synthetic demo passed; the final suite additionally checks
gap chaining, common-offset blindness and local-slope removal: **41 tests
passed** with `.venv/bin/python -m unittest discover -s tests -v`.
