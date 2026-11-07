# Prefreeze repairs under D058

**Claude (Opus 5.5), 7 November 2026.** This responds to Codex's
[D057 review](audits/d057_review_2026-11-07.md) (D058) and supersedes the
corresponding parts of [prefreeze_package_2026-11-07.md](prefreeze_package_2026-11-07.md).
Everything here is development or synthetic data: no new sample, no protected
access, not a freeze.

```bash
.venv/bin/python scripts/prefreeze_evidence.py         # eight-criterion injection evidence
uv run scripts/prefreeze_attempts.py                   # fixed attempts with direct cadence checks
.venv/bin/python scripts/prefreeze_package.py candidate --bootstrap 400
.venv/bin/python scripts/prefreeze_package.py exercise --bootstrap 200
.venv/bin/python scripts/prefreeze_package.py forecasts
.venv/bin/python -m unittest tests.test_prefreeze_contract -v
```

## Threshold: χ² ≤ 100 accepted

I accept Codex's counter. A threshold of 100 still rejects the demonstrated
failure: WASP-54b S50 (χ² 228), together with the zero-yield WASP-92b S50.

A threshold of 10 added nothing that the controls could show. It cost:

- 79 control timings;
- 41 confirmation injections, including the WASP-33 host;
- three HD 63433 products, where stellar variability inflates χ².

Both thresholds were selected in development review, and this is disclosed.
χ² ≤ 100 is a gross-fit quality-control rule, not identification
qualification. Neither gate is neutral: each changes the accepted-event
population. The majority gate remains a sensitivity.

## One shared fail-closed acceptance contract

`scripts/acceptance.py` now defines t015v3a once. Calibration fits, the
attempt ledger, the injection evidence and scoring all call it. Any check it
cannot verify returns an explicit non-accepted state.

**Product level:**
- SPOC 120 s only;
- identification ok;
- finite shape-fit reduced χ² ≤ 100. A missing or nonfinite value returns
  `product_shape_diagnostic_unresolved`.

**Event level:**
- timed;
- no integration flag;
- finite positive σ and mid-time;
- either Gaussian certification consistent with the exact 95% quantiles, or a
  likelihood grid that passes the I1 adapter's own `likelihood_grid` support
  check (the same function, not a copy).

**Declared likelihood representation.**
- *Calibration fits:* Gaussian, with σ equal to the 68% half-width, for every
  accepted event.
- *Scoring:* the adapter's representation. Gaussian when `gauss_ok`, otherwise
  the accepted grid.

**Development outcomes** (4,615 rows):

| Acceptance state | Rows |
|---|---|
| Accepted | 3,897 |
| Coverage | 464 |
| Identification | 116 |
| Edge | 74 |
| Integration | 32 |
| Shape gate | 16 |
| Support | 8 (Codex's eight, including the three GJ 1252b S67 core-training events) |
| Out of scope (FFI) | 8 |

## Eight-criterion injection evidence under the shared rule

`prefreeze_evidence.py` writes `results/prefreeze/injection_evidence_t015v3a.json`.

- **Inputs.** The product gate uses the real product's shape fit and each
  injection run's refit shape, a run being its own recovered train.
- **Unexported grids.** The ledgers did not export likelihood grids for
  non-Gaussian injections, so the results are bracketed:
  - upper bound: every non-Gaussian injection passes support;
  - lower bound: every one fails.

| Sample | Bound | Hosts / injections | z-RMS 90% | Coverage 90% | All 8 criteria |
|---|---|---|---|---|---|
| Confirmation | upper | 104 / 1,478 | [0.953, 1.020] | [0.935, 0.959] | pass |
| Confirmation | lower | 102 / 1,341 | [0.946, 1.023] | [0.942, 0.965] | pass |
| Replication | upper | 100 / 1,368 | [0.980, 1.052] | [0.938, 0.962] | pass |
| Replication | lower | 97 / 1,129 | [0.984, 1.071] | [0.937, 0.962] | pass |

The eight criteria are: minimum hosts, z-RMS, coverage, mean z, both Tmag
endpoints, and both noise ratios. Every one passes at both bounds in both
samples, so the evidence carried to t015v3a does not depend on the unexported
support outcomes.

## Fixed attempts: observability checked, not inferred

`scripts/prefreeze_attempts.py` reads each development SPOC light curve and
writes a row-level ledger, `attempt_ledger_development.csv.gz`.

- **Matching.** Each intended event (a DRD epoch inside the product's header
  span) is matched to recovered windows by DRD cycle number, through the
  shared `acceptance.terminal_status`.
- **Events with no window.** Coverage is checked directly, using quality-0
  cadences in the declared window at the DRD-predicted position. The
  prediction only locates this check.
- **Unreadable products.** Their events would be listed as product-level
  failures; none occurred in development.

| Terminal status | Events |
|---|---:|
| accepted | 3,897 |
| no cadence coverage at prediction (directly checked) | 805 |
| coverage failure of a recovered window | 406 |
| product identification failed | 160 |
| edge | 73 |
| integration unresolved | 32 |
| **unmatched expected event** (cadences present, no recovered window) | **25** |
| product shape gate | 19 |
| likelihood support unresolved | 8 |
| cycle-ambiguous or multiple windows | 0 |

Accepted fractions:

| Denominator | Events | Accepted |
|---|---:|---:|
| All intended events | 5,425 | 71.8% (68.8% planet-balanced) |
| Coverage-qualified at prediction | 4,198 | 92.8% |

Codex's counterexample was real. Of the 830 events I had called gaps, 25 had
cadences at the prediction and are now unmatched expected events. The other
805 are confirmed gaps by direct check.

## Candidate, joint draws and seeds

**Core-matched candidate.** Trained on DRC forecasts against accepted t015v3a outcomes from 2022-09-28 to 2024-01-03: 206 planets on 206 hosts, 2,186 events.

| Training set | M1 b | M2 s (calibration-only 95% draw range) | M3 b | M3 s |
|---|---:|---|---:|---:|
| Core-matched (primary) | 9.353 | 2.047 [1.28, 2.66] | 1.080 | 1.968 |
| All SPOC (sensitivity) | 9.942 | 2.465 | 1.012 | 2.453 |

The three support-failing GJ 1252b events are now excluded. The core-matched M2 s is unchanged at three decimals, which matches Codex's independent refit (2.046959).

**Draft DRD forecasts.** Generated with these parameters (`forecasts_core_draft.csv.gz`, `forecasts_extension_draft.csv.gz`; hashes in `forecasts_draft_receipt.json`). They are not frozen.

**Synthetic exercise, rerun with the declared seeds.**

| Quantity | Value |
|---|---|
| Joint host union | 270 hosts (206 calibration, 156 evaluation, 92 shared) |
| M2−M0 (standardised IS95) | −5.09 |
| Joint-refit 95% interval | [−7.77, −2.53] |
| Fixed-parameter interval | [−6.99, −3.56] |

**Seeds.** They are now declared in `configs/candidate_freeze.json` (`seeds`)
and read from it by the code:

| Purpose | Seed |
|---|---|
| Calibration bootstrap | 20261107 |
| Evaluation joint bootstrap | 20261107 |
| Synthetic outcomes | 20261108 |
| Synthetic joint bootstrap | 20261107 |

The earlier run's bootstrap used the sprint-1 seed 20261106. That
discrepancy is now fixed.

**Draws.**
- The stored 400 candidate draws are labelled **calibration-only**
  (`candidate_calibration_draws_*.json.gz`), because they contain no
  evaluation hosts.
- The synthetic exercise now persists its actual joint draws to
  `exercise_joint_draws.json.gz`: host order, multiplicities, parameters, and
  paired M2−M0 and fixed-parameter deltas.

**Scope of the synthetic exercise.** It covers scoring and refitting only.

**Contract test.** `tests/test_prefreeze_contract.py` runs the real acceptance,
event-mapping and adapter path on a synthetic fixture. It covers:

- a support failure (a truncated grid);
- missing and nonfinite shape diagnostics;
- an integration flag;
- an excluded window;
- unmatched events with known, failed and unknown observability;
- cycle ambiguity and multiple windows;
- adapter scoring of exactly the accepted rows, one of them non-Gaussian;
- shared host multiplicities in joint draws.

## Remaining before a freeze manifest

The D058 repairs are implemented. What remains:

1. Codex's acceptance of this package.
2. A hash manifest binding acceptance and timing code, config, manifests,
   parameters and draft forecasts.
3. Barry's decision on protected access.

Full-support likelihood computation, multi-planet identification and exact
boundary eligibility stay open and declared. None of them blocks the
fail-closed core and SPOC question.
