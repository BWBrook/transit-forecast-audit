# Protected evaluation: frozen primary and exploratory results (D065)

**Claude (Opus 5.5), 8 November 2026.** Barry authorised freezing manifest
`5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1` (D064) and
opening the protected outcomes. His words: "Authorised." (through the board
messenger, replying to Codex's D064 question), then, directly in the Claude
session, "approve writing the D065 access record". The record
`configs/protected_access.json` was committed as `b2f54de` before any protected
product was requested.

## Verdict

**Inconclusive.** For the primary core set (3,103 manifest events, 2,185
accepted events on 151 planets and hosts), the planet-balanced standardised
IS95 difference M2 − M0 is −0.121. Its 95% joint host-refit interval
(B = 2,000, seed 20261107) is [−1.84, 2.20]. The interval spans zero, so by the
rule fixed before unblinding the calibration neither improves nor worsens the
interval score. The conditional fixed-parameter interval (B = 10,000, seed
20261109) is [−1.98, 1.12], and it also spans zero.

The fail-closed checks pass: adapter reproduction 2.2e-12, calibration refit
reproduction 0.0. The freeze manifest verifies unchanged after the run, and all
99 tests pass.

## What the calibration does (descriptive)

Values are planet-balanced over 151 planets, from `results/final_primary/descriptives.json`.

| Model | IS95 (standardised) | IS95 (min) | 68% coverage | 95% coverage | 95% width (min) |
|---|---:|---:|---:|---:|---:|
| M0, issued uncertainties | 11.33 | 106.3 | 0.619 | 0.908 | 10.5 |
| M1 | 19.90 | 78.7 | 0.985 | 0.993 | 56.4 |
| M2, frozen calibration | 11.21 | 97.8 | 0.679 | 0.976 | 17.5 |
| M3 | 11.26 | 97.6 | 0.692 | 0.977 | 17.8 |

- **Coverage:** M2 repairs the issued intervals' 95% coverage, from 0.908 to
  0.976 by planet and from 0.919 to 0.965 by event.
- **Width:** to do so it widens the planet-balanced mean 95% interval width
  about 1.7-fold, from 10.5 to 17.5 min.
- **Interval score:** the gain in coverage and the cost in width almost exactly
  cancel in the planet-balanced standardised score.
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
uninformative at this size. It is reported as exploratory, as declared.

## Execution record

1. **First core measurement, set aside.** It ran with the recorded relative
   `--out` path. Every product whose timing writes a non-Gaussian grid then
   failed in `sprint2_outcomes` at `path.relative_to(ROOT)`, which needs an
   absolute path. That was 71 products. Nine more lost their MAST connection.
   - These are execution failures, independent of outcome values. The
     development chain check had used absolute paths, so it never hit this.
   - The attempt is kept on disk unchanged. Its status classes and receipt are
     in `results/final_primary/measure_attempt1_relpath_summary.json`; the raw
     products file is not committed because it contains local paths.
   - The identical command was rerun with an absolute `--out`. No frozen file
     changed.
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

## Not yet done

The config declares further secondary results that `evaluate` does not
compute. Each needs a separate script written after unblinding, applied exactly
as declared, and reported whatever it shows:

- **Strata:** lead time, Tmag, covariance tier, core vs extension, product type.
- **Sensitivities:** covariance settings, all-SPOC training, journal anchor,
  C2 only, outcome σ × 1/1.1 and × 1.1, the majority-of-windows gate,
  t015v3c.
- **Diagnostics:** the leave-k-gain-hosts-out curve and the TTV label
  diagnostic.

None of them can change the primary verdict. Independent review of this run
(T012) should precede them.
