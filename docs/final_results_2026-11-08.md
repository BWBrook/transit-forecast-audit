# Protected evaluation: frozen primary and exploratory results (D065)

**Claude (Opus 5.5), 8 November 2026.** Barry authorised freezing manifest
`5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1` (D064) and
opening the protected outcomes. His words: "Authorised." (through the board
messenger, replying to Codex's D064 question), then, directly in the Claude
session, "approve writing the D065 access record". The record
`configs/protected_access.json` was committed as `b2f54de` before any protected
product was requested.

**Independent review, 9 November (D066):** numerical and execution checks
support the frozen primary verdict. The path workaround preserves every
previously completed window. Interpretation and the exploratory effective-draw
count are clarified below; original run files remain unchanged. See
[the audit](audits/d065_review_2026-11-09.md) and
[secondary execution conventions](secondary_execution_2026-11-09.md).

## Verdict

**Inconclusive.** For the primary core set (3,103 manifest events, 2,185
accepted events on 151 planets and hosts), the planet-balanced standardised
IS95 difference M2 − M0 is −0.121. Its 95% joint host-refit interval
(B = 2,000, seed 20261107) is [−1.84, 2.20]. The interval spans zero, so by the
rule fixed before unblinding neither improvement nor worsening of the interval
score is established; this is not an equivalence result. The conditional
fixed-parameter interval (B = 10,000, seed
20261109) is [−1.98, 1.12], and it also spans zero.

The fail-closed checks pass: adapter reproduction 2.2e-12, calibration refit
reproduction 0.0. The freeze manifest verifies unchanged after the run, and all
99 tests in the original run's suite pass. Later audit/secondary checks are
recorded separately in D066–D067.

## What the calibration does (descriptive)

Values are planet-balanced over 151 planets, from `results/final_primary/descriptives.json`.

| Model | IS95 (standardised) | IS95 (min) | 68% coverage | 95% coverage | 95% width (min) |
|---|---:|---:|---:|---:|---:|
| M0, issued uncertainties | 11.33 | 106.3 | 0.619 | 0.908 | 10.5 |
| M1 | 19.90 | 78.7 | 0.985 | 0.993 | 56.4 |
| M2, frozen calibration | 11.21 | 97.8 | 0.679 | 0.976 | 17.5 |
| M3 | 11.26 | 97.6 | 0.692 | 0.977 | 17.8 |

M0 retains issued DRD marginal uncertainties and uses a reconstructed T0–P
correlation; the joint covariance was not issued. Coverage and scores concern
accepted measured timings under the convolved measurement model.

- **Coverage:** M2 increases observed mid-time 95% coverage from 0.908 to
  0.976 by planet and from 0.919 to 0.965 by event. These conditional point
  estimates do not establish ideal calibration across populations or strata.
- **Width:** to do so it widens the planet-balanced mean 95% interval width
  about 1.7-fold, from 10.5 to 17.5 min.
- **Interval score:** the point estimate of the planet-balanced standardised
  score changes little. Its broad interval permits material benefit or harm;
  the coverage/width description is not an additional inferential verdict.
- **Spread across planets:**
  - only 26.5% of planets improve, and the median planet difference is +1.05;
  - the small negative mean comes from a minority of planets with large
    reductions, the heavy tail the pre-registered leave-k-hosts-out diagnostic
    was declared to probe.

The descriptives are post-unblinding summaries of the frozen scores. Only the
fraction improved and the median planet delta are among the declared secondary
diagnostics; the rest is description.

## Terminal ledger (primary)

Each manifest event has exactly one status.

| Status | Events |
|---|---:|
| accepted | 2,185 |
| no cadence coverage at prediction | 431 |
| excluded (coverage) | 290 |
| integration unresolved | 75 |
| edge | 71 |
| product identification failed | 39 |
| likelihood support unresolved | 12 |

Of the 304 SPOC 120-s products, 293 were measured and 11 failed
identification. The scoring covers 399 non-Gaussian events, each scored by its
likelihood grid. 186 recovered windows lay outside the manifest; they are not
scored, by design.

## Exploratory extension (multi-planet hosts, 291 events)

Only 72 events on 5 planets were accepted. Identification failed on 72 events,
because multi-planet identification is a declared open limit. M2 − M0 is −11.2
with a 95% interval of [−56.4, 6.3], so the result is inconclusive and
imprecise at this size. Eleven of the 2,000 union-host draws contain no
evaluation host, so the frozen `nanquantile` implementation calculates this
interval from 1,989 defined draws. The original draw file records these as
nonstandard JSON `NaN`; new audit summaries state the effective count explicitly.
It is reported as exploratory, as declared.

## Execution record

1. **First core measurement, set aside.** It ran with the recorded relative
   `--out` path. Every product whose timing writes a non-Gaussian grid then
   failed in `sprint2_outcomes` at `path.relative_to(ROOT)`, which needs an
   absolute path. That was 71 products. Nine more lost their MAST connection.
   - The path failure is triggered by data-derived non-Gaussian likelihood
     output, so it is not independent of measured outcomes. It did not select
     by forecast residual or score. The complete rerun restores the affected
     products; the development chain check used absolute paths and missed the bug.
   - The attempt is kept on disk unchanged. Its status classes and receipt are
     in `results/final_primary/measure_attempt1_relpath_summary.json`; the raw
     products file is not committed because it contains local paths.
   - The identical command was rerun with an absolute `--out`. No frozen file
     changed.
   - Independent comparison finds identical product keys, all 224 previously
     completed product diagnostics unchanged, all 1,817 prior windows unchanged,
     and all 71 previously written grids hash-identical. The rerun adds 1,002
     windows, with no favourable subset or replacement of successful timings.
2. **Rerun.** 304 products and 2,819 windows, 2,301 of them timed. Every
   manifest event has a coverage row. Measurement and evaluation inputs are
   committed under `data/derived/final_primary/measured/`.
3. **Evaluation.** Run as recorded with absolute paths. 14,755 s for the joint
   bootstrap on 8 workers.
4. **Extension.** Measured with absolute paths and 2 workers, then evaluated
   with `--label exploratory`.
5. **Likelihood grids.** 39 MB primary and 11 MB extension. They are
   regenerable and gitignored, and copied to
   `nectar:/data/share/transit-forecast-audit/final_{primary,extension}/measured/`.
   Their hashes are in the committed portable receipts.

**Reproduce:**

```bash
uv run scripts/final_measure.py --manifest results/prefreeze/manifest_core_primary.csv --out "$PWD/data/derived/final_primary/measured" --era protected
.venv/bin/python scripts/final_evaluation.py evaluate --manifest results/prefreeze/manifest_core_primary.csv --forecasts results/prefreeze/forecasts_core_draft.csv.gz --windows data/derived/final_primary/measured/windows.csv.gz --products data/derived/final_primary/measured/products.csv --coverage data/derived/final_primary/measured/coverage.csv --out "$PWD/results/final_primary" --era protected --bootstrap 2000 --conditional-bootstrap 10000 --workers 8
.venv/bin/python scripts/final_descriptives.py results/final_primary/scores.csv
```

## Declared secondaries completed after independent review

The config's secondary results were implemented on 9 November after independent
review of this run. [The report](final_secondaries_2026-11-09.md) and
[execution conventions](secondary_execution_2026-11-09.md) distinguish declared
settings from post-unblinding executable details:

- **Strata:** lead time, Tmag, covariance tier, core vs extension, product type.
- **Sensitivities:** covariance settings, all-SPOC training, journal anchor,
  C2 only, outcome σ × 1/1.1 and × 1.1, the majority-of-windows gate,
  t015v3c.
- **Diagnostics:** the leave-k-gain-hosts-out curve and the TTV label
  diagnostic.

They do not change the primary verdict. Sensitivity intervals are conditional
on scenario fits and do not replace the frozen joint-refit interval.
