# Claude's reciprocal review: counter-review of sprint-2 corrections, and review of sprint 1

**Claude (Opus 5.5), 7 November 2026.** This review follows Barry's order. Codex
reviewed and fixed sprint 2 (D051–D053, at `f9e2840`); I counter-review those
fixes here and review sprint 1. Both feed reconciliation (§4). Development only;
nothing protected was opened.

```bash
.venv/bin/python scripts/review_sprint1_claude.py   # tails, chronology, influence
uv run scripts/sprint2_white_noise.py               # restored white-noise reproducer
```

The amended-gate check, recomputed from the committed ledgers, is in
`results/sprint2_review/claude_amended_gate_check.json`.

## 1. Counter-review of Codex's sprint-2 corrections

### Both analysis defects are real. I accept the reversed verdict.

I recomputed both defects from the committed ledgers with my own code; I did
not use Codex's scripts.

- **Interval containment.** With err = fitted − truth, lo95 = fitted − q025
  and hi95 = q975 − fitted, so truth is covered iff −hi95 ≤ err ≤ lo95. My
  analysis had the sides reversed. The corrected formula agrees with the
  ledger's direct truth-containment flag on 100% of rows; my formula agreed
  on 97.9–99.0%.
- **Product fallback.** `production()` took its "has SPOC" set from timed rows.
  A host whose SPOC product failed therefore fell back to FFI, against the
  frozen rule. The hosts affected were TOI-712 in the confirmation, and
  HD23472 and K2-403 in the replication.
- **Corrected replication.** Fixed t015v3 on 100 hosts, 1,374 injections:
  - z-RMS 1.0144 [0.9783, 1.0506]
  - coverage 0.9502 (lower bound 0.9382)
  - mean z +0.069 [+0.013, +0.125]
  - Tmag endpoints [0.963, 1.123] and [0.862, 1.070]

  It passes every criterion, matching D051 to rounding.
- **Corrected t015v3c confirmation.** Still fails: coverage lower bound 0.917;
  Tmag-13.5 endpoint [1.060, 1.193].

The fault was mine, and so was the conclusion I drew from it. The "≥4 timed
transits" scope I proposed (C025, S2-02) came largely from the fallback bug.
Codex is also right that it pooled injections across two phase runs rather
than counting observed transits per sector. I withdraw it.

### The amended integration gate is evaluable now, and it passes

D053 says the amended timing source ("integration_unresolved" for rows flagged
`mass_outside_fine` or `coarse_fine_shift`) "requires separate qualification".
I agree it has a new rule hash. But the amendment changes no timing value, only
which rows count as timed, and the frozen ledgers store those flags. So its
injection calibration on both samples can be computed exactly, with no rerun.

| Sample, production set | Flagged injections removed | Hosts / events | z-RMS [90%] | Coverage (lower) | Mean z [90%] | Verdict |
|---|---:|---|---|---|---|---|
| Confirmation | 5 | 105 / 1,490 | 0.990 [0.956, 1.023] | 0.946 (0.934) | −0.004 [−0.056, 0.049] | pass |
| Replication | 6 | 100 / 1,368 | 1.016 [0.980, 1.052] | 0.950 (0.938) | +0.070 [+0.013, +0.126] | pass |
| Replication, FFI only | 13 | 102 / 1,347 | 1.105 [0.997, 1.228] | 0.929 (0.902) | +0.048 | **fail** |

**Proposal.** The amended SPOC rule, call it t015v3a, inherits the frozen
rule's injection evidence. The table is the same evidence with the same
estimand, restricted to rows the amendment still times. It is not
independent qualification of the amended code path. A regression test that
the amended code reproduces the frozen timings, bit for bit, on unflagged rows
would close that gap; Codex's existing fixtures nearly do this.

### Other corrections I accept, with two refinements

- **R5 narrowed to descriptive agreement** (D053). Accepted. With every
  interval inconclusive, matching signs and decisions cannot show equivalence.
- **The exact-grid and Gaussian replays agree** to 0.026 standardised IS95
  (−1.897 vs −1.922). This supports scoring the non-Gaussian rows as Gaussian
  in development fits. It is a point check, not a verdict.
- **Refinement 1: a small late bias.** The replication's mean z of +0.069
  [+0.013, +0.125] excludes zero. D039 (+0.08) and the development rerun
  (+0.05) point the same way, and the white-noise control shows no such bias.
  The margin of ±0.15 is satisfied. Scored outcomes may still carry a late shift
  of about 0.07 σ_y, a few seconds. Report it and do not correct it.
- **Refinement 2: FFI is out.** FFI fails the replication by itself. The
  declared product scope for the sealed evaluation should be SPOC 120 s only.
  Sprint 1's inventory finds that the sealed-era eligible products are SPOC
  120 s anyway.

### Provenance: my own error

My commit `d9c1570` ("Remove stale placeholder note") was made with
`git commit -am` while Codex was editing the same checkout. It swept Codex's
uncommitted edits into my commit under my message. Five files:

- `scripts/sprint2_outcomes.py`
- `scripts/sprint1_outcome_adapter.py`
- `scripts/sprint2_analysis.py`
- `scripts/sprint2_figures.py`
- `coordination/task_board.md`

The same concurrency explains D053's finding that my interface receipt hashed
adapter bytes the running process had not loaded. I record it here rather than
rewriting shared history. From now on I stage explicit paths only.

**White-noise reproducer.** Codex rightly noted that my σ = 43/118/241 s claim
lacked a retained reproducer. `scripts/sprint2_white_noise.py` now regenerates
it with fixed seeds. 120 synthetic sectors per noise level, about 1,000 transits each:

| Median σ | Raw-error z-RMS | Scaled z-RMS | Mean z |
|---|---|---|---|
| 42 s | 0.959 | 0.928 | −0.060 ± 0.029 |
| 113 s | 1.009 | 0.975 | −0.001 ± 0.030 |
| 232 s | 1.045 | 1.009 | +0.019 ± 0.032 |

Raw-error calibration holds, and there is no consistent late bias across the three noise levels. The 42-s mean is −2.1 event-naive SE from zero. Transits share fitted shapes within each synthetic sector, so that SE is optimistic; no host-cluster interval was computed. The scaled errors are slightly conservative at high SNR, as the β and χ² floors of 1 imply. The output is `results/sprint2_review/white_noise.json`. These numbers replace my unretained earlier ones, which agree within Monte Carlo error.

## 2. Review of sprint 1

### Numerical tails: exact

I computed predictive quantiles and log densities by adaptive integration over
the latent multiplier, which is independent of the Gauss–Hermite quadrature,
for s ∈ {1, 2.16, 2.6, 3.2} and σ_y/σ_f ∈ {0.05 … 10}. Agreement with
`predictive_scores`:

| Quantity | Maximum relative error |
|---|---|
| 97.5% quantile | 1.5 × 10⁻⁹ |
| Log density | 7 × 10⁻⁸ (at s = 3.2) |

This confirms Codex's internal numerical audit with a method it did not use.

### Chronology: no in-sample leakage, and a narrower training window than labelled

- **Chronological design.** I matched each of the 1,696 2022 training events
  against DRC's own timing table (±0.02 d). None appear; the latest TESS record
  in that table is 2021-12-30. DRC's fit therefore did not use them. The design
  is an observation-date proxy, as labelled, and not an in-sample artefact.
- **Release transfer.** All 172 training events come from DRC's table, and
  they all fall between 2021-10-28 and 2021-12-30. So the DRB→DRC calibration
  rests on about nine weeks of TESS data on 15 planets, not "2021-10-28 to
  2022-09-26". Add this to the proxy label. It explains the matched-set
  fragility in sprint 2: 7 training planets after S46.

### Resampling: the decision rests on two to five hosts

| | Release transfer | Chronological |
|---|---|---|
| M2−M0, all hosts | −2.445 | −2.628 |
| Host-refit interval (sprint 1) | [−5.756, +0.187] | [−6.351, +0.067] |
| Fixed-parameter host bootstrap | **[−5.443, −0.137]** | [−6.554, +0.454] |
| Drop TOI-1130 | −1.42 | −1.24 |
| Drop TOI-1130 and TOI-125 | −0.78 | −0.36 |
| Drop top 3 gain hosts | −0.42 | **+0.14** |
| Drop top 5 gain hosts | **+0.17** | +0.97 |
| P(Δ > 0), fixed parameters, both top-2 hosts absent from the resample | 0.11 | 0.36 |
| P(Δ > 0), fixed parameters, either present | 0.001 | 0.011 |
| Planets improved | 23.5% | 19.4% |

Rows that drop hosts hold the fitted parameters fixed.

- **What the bootstrap measures.** The resamples leave out both dominant hosts
  about 13.6% of the time, and those resamples make up the inconclusive tail.
- **Refitting matters.** With parameters fixed, release transfer would be
  declared an improvement; refitting M2's s is what makes it inconclusive. That
  is the correct uncertainty for a learned correction, and Codex's choice is
  right.
- **Interpretation.** M2's advantage is a statement about a handful of
  catastrophic forecast failures. TOI-1130b, a TTV system, has residuals of
  about 10.7 h. Sprint 2's remeasurement confirmed it to within seconds of
  ExoClock. For the typical planet, M2 is a cost.

**Recommendation for the sealed analysis.** Pre-specify, as secondary
summaries:

- the leave-k-gain-hosts-out curve for k = 0–5, with fixed parameters;
- the fraction of planets improved;
- the median planet delta;
- the primary contrast restricted to planets without origin- or later-known
  TTV evidence.

None of these changes the primary contrast. They make its dependence on a few
hosts visible at freeze, not after.

### Inventory, covariance and novelty

- **Inventory.** My freeze-package code reproduces the inventory's 3,399
  opportunities independently, under the same window definition (C027).
  Codex's five near-boundary events (D053) should be resolved by an explicit
  UTC→BJD_TDB conversion before freeze, not just annotated.
- **Covariance.** The variance formula (σ_T0 + ρσ_P n)² + (1 − ρ²)(σ_P n)² is
  algebraically the full bivariate form. The C2 correlations are small, which
  is consistent with sprint 1's near-identical C2 and zero-covariance results.
  No defect.
- **Novelty.** Not re-audited beyond confirming that the bounded-combination
  framing is used consistently in the drafts. The literature screen is
  documented as bounded.

## 3. Defects found in sprint 1

No numerical or leakage defect. Two record corrections:

1. The release-transfer training window is in effect 2021-10-28 to 2021-12-30
   (172 events, 15 planets). The proxy label should say so.
2. "Inconclusive" should be reported together with its host dependence: the
   sign reverses after removing 3–5 gain hosts. This is a framing requirement,
   not an error.

## 4. Reconciliation proposal (for Codex's agreement)

**Joint recommendation: ready only for a narrower declared question, once a
short list of fail-closed declarations is implemented. Barry approves the
freeze.**

The declared question:

- **Population.** The issued DRD ephemerides for the core cohort: 156 planets,
  single DRD planet per host, Tmag < 13.5, P ≤ 12 d.
- **Extension.** The 28 extension planets are reported separately as
  exploratory. Their multi-planet identification is not validated.
- **Outcomes.** SPOC 120-s PDCSAP only, timed by t015v3a: the frozen t015v3
  plus the integration fail-closed gate, qualified as in §1 (conditional
  injection calibration).

Items to settle before freeze, each fail-closed and none needing a new
qualification sample:

| Item | Resolution |
|---|---|
| S2-01 spurious windows | Pre-declare a product acceptance gate: more than 50% of covered windows must time successfully. Report its development rejection count (Codex: 4 products). It uses no forecast information. |
| S2-05 / integration support | t015v3a fail-closed gate, plus the adapter refusal already installed. Report the failure fraction (about 1% in development). |
| Real-event attempt denominator | Attempts are the DRD-manifest events (`events_drd.csv`) with coverage evaluated from metadata, not BLS windows. Recovery is reported against that fixed list. |
| Time boundaries | Convert UTC → BJD_TDB for the 5 flagged events, then include or exclude them by rule before freeze. |
| Secondary robustness summaries | As in §2 (leave-k-hosts-out, fraction improved, median delta). |
| Parameters | Refit the candidate M1–M3 under the t015v3a convention on SPOC-only development outcomes; hash them with the forecasts, code and roster at freeze. |

Opening protected outcomes stays Barry's decision after reconciliation.

*Corrections after Codex's D056 review: release-transfer single-host deletion −1.42 (JSON), not −1.23; the chronology script now uses the stated ±0.02-d match; white-noise wording narrowed.*
