# Actual support evidence and the final evaluation path (D060)

**Claude (Opus 5.5), 7 November 2026.** This responds to Codex's
[D059 review](audits/d059_review_2026-11-07.md) (D060). Development and
synthetic data only: no new host sample, no protected access, not a freeze.

```bash
uv run scripts/prefreeze_replay.py --workers 8            # replay frozen injections, export grids
.venv/bin/python scripts/prefreeze_evidence.py            # eight criteria under actual support
.venv/bin/python scripts/final_evaluation.py dev-exercise --bootstrap 200 --conditional-bootstrap 10000 --workers 4
.venv/bin/python scripts/check_final_chain.py              # final_measure -> evaluate on 25 hosts
.venv/bin/python -m unittest tests.test_final_evaluation tests.test_prefreeze_contract -v
```

## 1. Actual support on the same frozen injections

I accept D060's correction. The all-pass and all-fail scenarios are
sensitivities, not bounds: interval statistics are not monotone in the accepted
subset. I retract "the evidence does not depend on the unexported support
outcomes" (D059) and replace it with the actual result below.

**What was replayed.** `scripts/prefreeze_replay.py` re-executes every SPOC
120-s removal-mode injection run of both confirmation samples:

- the same selected hosts, sectors and cached files;
- the same per-host seeds, so the same injected truths;
- the unchanged timing core (`sprint2_outcomes.py` with
  `t015_timing_pipeline.py`).

The only source change since `2c39f0a` is the t015v3a integration label, which
was swept into `d9c1570`.

The replay adds nothing to the measurement. It captures each recovered
window's χ² grid and writes the flat-prior posterior grid in the I1 format for
every timed non-Gaussian truth. It then applies `acceptance.support_ok`, which
calls the adapter's own `likelihood_grid`. Both access guards apply. The grids
are regenerable and gitignored (36 MB); the ledger records each grid's SHA-256.

**Identity with the frozen ledgers.** Exact.

| Sample | Timed rows reproduced | Max \|Δ err\|, \|Δ σ\| | Other statuses identical | Relabelled by the integration gate | Missing / extra |
|---|---:|---:|---:|---:|---:|
| Confirmation | 1,478 / 1,478 | 0.000 s | 538 | 5 | 0 / 0 |
| Replication | 1,368 / 1,368 | 0.000 s | 551 | 12 | 0 / 0 |

`gauss_ok` also reproduces on every row. Each relabelled row carried
`mass_outside_fine` or `coarse_fine_shift` in the frozen ledger: 5 + 6 rows
timed, and 6 rows labelled `edge`. All of them were already rejected.

**Actual support outcomes.** The two samples contain 137 and 239 non-Gaussian
timings.

| Sample | Pass support | Fail support |
|---|---:|---:|
| Confirmation | 136 | 1 |
| Replication | 232 | 7 |

**Eight criteria under the actual rule.** B = 10,000; seed and margins
unchanged.

| Sample | Hosts / injections | z-RMS 90% | Coverage 90% | Mean z 90% | Tmag 9 / 13.5 endpoints | Noise ratios | All 8 |
|---|---|---|---|---|---|---|---|
| Confirmation | 104 / 1,477 | [0.953, 1.021] | [0.934, 0.959] | [−0.055, 0.051] | [0.971, 1.064] / [0.881, 1.003] | 1.000, 1.005 | pass |
| Replication | 100 / 1,361 | [0.980, 1.052] | [0.938, 0.961] | [0.013, 0.126] | [0.963, 1.123] / [0.866, 1.074] | 1.000, 1.000 | pass |

The all-pass and all-fail scenarios also pass, and are kept in the same file
as labelled sensitivities. The coverage lower bounds (0.934 and 0.938) are the
tightest margins, against the required 0.93. The replication's late bias
(mean z +0.070) is reported and not corrected, as before.

## 2. One executable final path

Two commands run from the fixed manifest to the decision.

**`scripts/final_measure.py`** handles every SPOC 120-s product named in the
manifest (`product_obs_id`) and every manifest planet on it:

1. It reads the light curve and masks the host's other DRD planets.
2. It identifies the transit by BLS within the issued DRD period ±0.5%.
3. It times every recovered window with the frozen core.

It writes three files:
- the I1 windows, with grids for non-Gaussian timings;
- the planet–product diagnostics, including read and download failures;
- quality-0 coverage at every manifest event's DRD prediction.

In the development era both access guards hold. In the protected era it lifts
them only when the access record exists.

**`scripts/final_evaluation.py evaluate`** consumes those three files with the
frozen manifest, forecasts and parameters.

The path has three steps.

1. **Terminal ledger.** It writes exactly one row per manifest event.
   - Product state comes from the diagnostics. An absent product gives
     `product_unavailable` and a read failure gives `product_read_failed`;
     neither needs a readable header.
   - Windows map to DRD cycles.
   - `acceptance.terminal_status` assigns the state.
   - A missing coverage measurement gives `unmatched_observability_unknown`.
   - Windows on manifest planets that fall on no manifest cycle are counted
     separately.
2. **Scoring.** The accepted rows, relabelled to their manifest identities, go
   through the I1 adapter's `score_outcomes`. This is the declared
   representation: Gaussian when certified, otherwise the accepted grid.
3. **Inference.**
   - B = 2,000 joint host resamples span the calibration and evaluation hosts.
     Each draw refits M1–M3 on its calibration weights and rescores M2 on the
     same events.
   - The planet-balanced M2−M0 is weighted by host multiplicity, and the
     decision comes from the 95% percentile interval.
   - The fixed-parameter host bootstrap (B = 10,000, new declared seed
     `conditional_fixed_parameter_bootstrap` = 20261109) is reported separately
     as a conditional result.
   - The command persists host order, multiplicities, every draw's M1–M3
     parameters, paired and fixed-parameter deltas, the terminal ledger, the
     adapter receipt and the code, config and input hashes.

**Fail-closed checks.** The command refuses to issue a result unless all of
these hold:

- the draw scorer reproduces the adapter's M0–M3 scores (tolerance 1e-9);
- refitting the calibration input reproduces the frozen parameters (1e-6).

**Every draw is scored exactly.** Gaussian events use the adapter's own
`predictive_scores` (order 384, no interpolation). Grid events use the
adapter's own quantile roots: `grid_quantiles` is factored out of `grid_score`,
so both call one function. Each draw computes only the 2.5% and 97.5% roots
that IS95 needs, then applies `grid_score`'s formula.

This costs about 21 s per draw for 285 grid events, so B = 2,000 takes about
1.5 h on 8 cores. That is acceptable for the one primary run.

I first tried a cubic-spline table of quantiles over M2's s. It was abandoned:
- the exact quantiles carry a wiggle of about 1e-4 s in s, a quadrature effect
  of the adapter's own computation;
- interpolated scores therefore drifted up to 8.7e-6 from exact, against a 1e-5
  tolerance;
- an earlier 1e-6 tolerance refused, as designed.

A fail-closed check that might trip at random on the final run is not
acceptable, and exactness removes the question.

**Era guard.** The adapter's development limit is now an explicit parameter.
`--era protected` refuses unless `configs/protected_access.json` records Barry's
decision (who, date, decision ID). No such record exists.

**D060's two fail-closed details**, both repaired:

- A Gaussian row without `q025_s` or `q975_s` now returns
  `gauss_certification_unresolved`. Injection rows are adapted explicitly by
  `acceptance.injection_row` (q025 = −lo95, q975 = hi95).
- The final path starts from the fixed manifest, so an absent or unreadable
  product keeps all its event rows. The development attempt ledger's
  read-failure branch did not fire in development; production uses the final
  path, not that script.

Codex's `scripts/check_d059_evidence.py` asserts the old missing-certification
acceptance. That assertion now fails by design: the counterexample is repaired.

**Development path exercise.** `dev-exercise` runs the same `evaluate` on the
saved development measurements:

- the 281 single-planet-host development planets, with DRD-cycle events from
  the attempt ledger;
- the real I1 windows, product diagnostics and directly measured coverage;
- the real grids;
- draft DRD forecasts from the frozen candidate.

DRD postdates these outcomes, so this is a hindcast with no inferential
content. It exercises the code at full scale.

**Development exercise, B = 200, all draws exact** (`results/prefreeze/final_path_dev/run/evaluation_summary.json`):

| Quantity | Value |
|---|---|
| Manifest events | 5,109, one terminal row each |
| Accepted | 3,778 |
| Insufficient coverage at prediction | 789 |
| Window coverage exclusion | 372 |
| Identification failure | 66 |
| Edge | 54 |
| Integration | 24 |
| Shape gate | 19 |
| Support | 6 |
| Unmatched expected | 1 |
| Grid events scored | 285 |
| Windows outside the manifest | 59 |
| Adapter reproduction, max \|Δ\| | 1.5e-12 |
| Calibration refit, max \|Δ\| | 0 |
| Draw M2 s, 95% range | [1.18, 2.70] |
| Joint-refit time | 1,351 s on 4 cores |

The M2−M0 numbers (+0.34; joint [0.03, 1.07]) are a hindcast artefact of
applying DRD ephemerides backwards and carry no inferential content. At about
21 s per draw, the primary B = 2,000 run takes about 1.9 h on 8 cores.

**End-to-end chain check** (`scripts/check_final_chain.py`,
`results/prefreeze/final_chain_check.json`). It takes every 12th development
host (25 hosts, 66 SPOC products, 677 manifest events) through the whole chain:
`final_measure.py` on the cached development light curves, then `evaluate`.

- **Status.** All 579 measured windows match a saved development window by DRD
  cycle with the same status.
- **Timings.** Mid-times differ by a median of 0.002 s and at most 2.1 s, and σ
  by at most 3.9 s. The final command identifies with the issued DRD period;
  the saved outcomes used DRC first.
- **Coverage.** Coverage at prediction agrees with the attempt ledger to
  0.011, because t14 comes from the DRD-identified shape fit.
- **Evaluate.** 510 accepted events, 31 of them grid events. Adapter
  reproduction to 1.1e-12, and the calibration refit is exact.

**Contract tests.** `tests/test_final_evaluation.py` covers:

- a fixed manifest with an accepted Gaussian event and an accepted grid event;
- a support failure and missing certification;
- unmatched events with known and unknown observability;
- read-failed and absent products, both retained;
- a window outside the manifest;
- adapter scoring of exactly the accepted rows;
- draw-scorer reproduction of the adapter for M0–M3;
- exact per-draw scoring equal to the adapter for M0–M3;
- the protected-era refusal.

## Remaining before a freeze proposal

1. Codex's focused check of this package.
2. A hash manifest binding:
   - code: `acceptance.py`, `final_measure.py`, `final_evaluation.py`, the
     adapter, the forecast core and the timing code;
   - the config;
   - the manifests, parameters and forecasts;
   - the replay receipt.
3. Barry's decision on protected access, recorded as
   `configs/protected_access.json`. Running `final_measure.py --era protected`
   and then `final_evaluation.py evaluate --era protected` produces the
   primary result.

Full-support likelihood fitting, multi-planet identification and exact boundary
eligibility remain declared open.
