# Sprint 2: outcome qualification, convention transfer and candidate freeze package

**Claude (Opus 5.5), 7 November 2026. Development evidence only. No protocol is
frozen, and no protected outcome has been opened.** Decisions D046–D050 and claims
C022–C027 index this evidence. The machine-readable entry point is
`results/sprint2/handoff.json`.

**Review correction, 7 November 2026:** this is the preserved sprint-2 handoff
account, whose replication-failure interpretation is superseded by C028 and
[the independent review](sprint2_review.md). Product selection after success and
reversed asymmetric coverage caused that verdict. Corrected t015v3 SPOC
replication passes; end-to-end readiness remains unresolved. Use the review
for current claims and the original result tables for historical evidence.

## Decision

**The outcome-measurement pipeline is not ready**, under the criteria fixed
before each test.

- The prespecified rule t015v3c failed its 120-host confirmation.
- The uncorrected rule t015v3 passed every criterion on that same sample, but
  only as a secondary analysis.
- t015v3 then failed a single prespecified replication on 120 hosts that had
  never been sampled.

Both verdicts stand. No margin was relaxed, and no host was added or dropped.

The strongest supported scope is narrower. It was identified only after the
replication, so it is exploratory. Hosts with **at least four timed transits in
the sector** are calibrated in both confirmations: z-RMS 0.992 and 1.012, 95%
coverage 0.944 and 0.953. The replication failure comes almost entirely from
hosts with one to three transits, mostly long-period planets. Turning that
observation into a rule needs its own prespecified test, with a metadata
definition (for example, predicted transits per sector) and a fresh sample.

On the forecast side, **outcome-convention transfer (R5) is accepted**. Both
designs keep their sign and their inconclusive decision whether matched
transits are scored with ExoClock timings, t015v3c or t015v3. The primary
M2−M0 contrast stays negative and inconclusive throughout. One spurious
real-data timing showed how fragile the mixture calibration is to a single
identification defect.

A candidate freeze package exists: roster, event manifest, draft DRD forecasts,
configuration and access receipt. It is not freeze-ready, because its outcome
rule is not qualified.

## 1. Interface acceptance (R9)

- **Replay.** `make_forecasts` followed by `score` reproduces sprint 1's
  `scores.csv` byte for byte. All 70 sprint-1 tests pass, and there are 75 with
  the sprint-2 tests.
- **Production I1.** Every DRC-window production row (2,777 attempts) passes
  the I1 schema check. The adapter scores 2,310 timed events, 309 of them
  through likelihood grids. The other 467 attempts stay as explicit failures,
  18 of them because the grid support is truncated (S2-05).
  Receipt: `results/sprint2/interface/scores.receipt.json`.

## 2. Repairs (S1-01, S1-02, S1-04)

Rule t015v3 was frozen at `2c39f0a`; the source hash is `4b5c9602a29b` in every
run receipt. The changes are set out in
[sprint2_outcome_design.md](sprint2_outcome_design.md) §1.

- **Ledger.** One row per intended injected truth, written before fitting, with
  a Hungarian assignment of recovered windows to truths under a 60-min gate. No
  duplicate assignments occurred in any sample.
- **Equal-host estimands.** These replace event pooling, and an arithmetic
  Tmag model replaces the log-MSE endpoint. In negative controls the estimators
  are unbiased, and the 90% intervals cover 0.853–0.927 (C023).
- **Identification.** Catalogue period ±0.5% with the epoch searched blind;
  other planets masked. The R7 short-period window applies.
- **Exact 95% quantiles and likelihood grids**, as I1 requires.

On development hosts (C022, C024):

- **Window removal is neutral.** Removing and subtracting the real windows give
  the same calibration: paired z-RMS 0.971 and 0.973 in the first
  confirmation.
- **Identification is phase-independent** within ±0.4% of the catalogue period.
- **TTVs are a declared selection.** Transits displaced more than about 60 min
  from their own sector's linear ephemeris are lost or mistimed.
- **No algorithmic bias in white noise.** Synthetic tests at σ = 43–241 s show
  no bias and calibrated raw errors.

## 3. Confirmation and replication (C025)

Production set: SPOC 120 s, or TESS-SPOC 200 s where SPOC is absent; PDCSAP;
removal mode. Intervals are 90% equal-host bootstraps, B = 10,000. Criteria are
in [sprint2_outcome_design.md](sprint2_outcome_design.md) §4.

| Sample / rule | Hosts / events | z-RMS | 95% coverage | Mean z | z-RMS at Tmag 9 | at Tmag 13.5 | Verdict |
|---|---|---|---|---|---|---|---|
| Confirmation / t015v3c (primary) | 106 / 1,496 | 1.053 [1.015, 1.091] | 0.936 [**0.922**, 0.950] | 0.000 [−0.055, 0.056] | [0.934, 1.040] | [**1.062**, 1.195] | **fail** |
| Confirmation / t015v3 (secondary) | 106 / 1,496 | 0.985 [0.951, 1.017] | 0.944 [0.930, 0.957] | +0.001 [−0.051, 0.053] | [0.966, 1.063] | [0.878, 1.000] | passes; not qualifying |
| Replication / t015v3 (primary) | 102 / 1,377 | 1.095 [1.002, **1.214**] | 0.929 [**0.908**, 0.947] | +0.048 [−0.045, 0.131] | [1.002, **1.221**] | [0.846, **1.319**] | **fail** |

| Sample | Equal-host recovery of observable truths [90% CI] | A | B | C | D |
|---|---|---|---|---|---|
| Confirmation | 0.896 [0.845, 0.940] | 0.79 | 0.86 | 1.00 | 0.93 |
| Replication | 0.859 [0.804, 0.909] | 0.92 | 0.79 | 0.81 | 0.93 |

- **The multiplier over-corrected.** The faint-star conservatism seen in
  development did not recur. t015v3c then made faint stars anti-conservative.
- **The replication failure is driven by few-transit hosts.** Its largest
  contributors are hosts with one or two timed injections, such as K2-403 (one
  transit, z = 3.9) and HD 23472. Under equal-host weighting each carries a full
  host weight. Dropping the three largest host contributions gives 1.006. That
  figure is a diagnostic, not a result.
- **Exploratory split, defined after the fact.** Hosts are divided by the number
  of timed injections, using results in
  `results/sprint2/exploratory_transit_count.json`.

| Sample | ≥ 4 timed: hosts, z-RMS [90%], coverage (lower) | ≤ 3 timed: hosts, z-RMS |
|---|---|---|
| Development | 42, 0.939 [0.882, 0.995], 0.963 (0.945) | 3, 1.02 |
| Confirmation | 99, 0.992 [0.959, 1.025], 0.944 (0.931) | 7, 0.88 |
| Replication | 98, 1.012 [0.976, 1.049], 0.953 (0.941) | 4, 2.34 |

- **Product types.** t015v3 passed on the production set. Assessed alone,
  SPOC 120 s misses the first confirmation's coverage bound (0.9291 against
  0.93).
- **Spurious windows** (recovered windows with no matching truth) number 28 in
  the confirmation and 16 in the replication. They are counted in the ledgers
  and excluded from the denominators.
- **Other failures stayed in the denominators.** The noise-ratio control passes
  in all samples, at 1.000 and 1.000–1.004. 40 replication runs and 14
  confirmation runs were still dropped for window overlap. Bright-star (A)
  coverage was 0.915–0.918 in both confirmations.

## 4. Development remeasurement and convention transfer (C026)

- **Remeasurement.**
  - Scope: the 321 sprint-1 cohort planets on 314 hosts, across 618 S46–S73
    products (617 SPOC 120 s).
  - Events: 4,615 attempted, 3,946 timed. The failures are 470 for coverage,
    116 for identification and 83 at the prior edge.
  - Planets: 294 have timings.
- **Same-photon agreement.** All 3,748 remeasured transits with a DRD record
  give a median difference of −0.1 s and a z-RMS of 0.36. Raw t015v3 σ is a
  median 1.055 times ExoClock's σ (`results/sprint2/handoff.json`).
  - Within the scored designs (2,230 release-transfer and 3,416 chronological
    pairs), the medians are −0.33 and −0.18 s. t015v3c σ is a median 0.985 and
    0.986 times ExoClock's (`convention_comparison.json`).

| Design / events | ExoClock × 1.087 | t015v3c | t015v3 | Decision (all) |
|---|---|---|---|---|
| Release transfer, matched (7 training / 216 scored planets) | −1.249 [−3.897, 2.657] | −2.195 [−5.063, 1.722] | −2.031 [−4.844, 1.738] | inconclusive |
| Chronological, matched (123 / 185) | −1.080 [−3.623, 1.324] | −1.465 [−4.753, 1.528] | −1.376 [−4.647, 1.534] | inconclusive |
| Release transfer, all timed (70 / 217) | −2.445 [−5.756, 0.187] (sprint 1) | −2.154 [−5.148, 0.122] | −1.972 [−4.997, 0.278] | inconclusive |
| Chronological, all timed (124 / 186) | −2.628 [−6.351, 0.067] (sprint 1) | −0.026 [−5.100, 15.04] | −0.082 [−5.108, 14.84] | inconclusive |

Each cell is the planet-balanced standardised IS95 of M2 minus M0, with a 95%
host-refit interval over 400 resamples. The matched rows are R5's acceptance
test. The ExoClock "all" row reproduces sprint 1 exactly.

- **R5 transfer is accepted for both conventions.** Sign and decision agree in
  both designs.
- **Coverage.** M2 again raises 95% coverage (for example, 0.883 to 0.962 in
  the matched release transfer). Fewer than a quarter of planets improve
  individually.
- **One defect is identified.** In WASP-54b S50 a product-level ephemeris
  misalignment put the windows about 12 h from the real transits. Two windows
  were edge-flagged, and one was falsely timed: z = 55 against the forecast,
  σ = 797 s. This was the only such case found among 3,946 timings.
- **Its influence.** That one event drives the chronological "all timed"
  results.
  - M1's b rises to 191, against 7.5 without the event.
  - M2's log-SD s rises from 2.33 to 3.24, and its contrast moves from −1.37
    [−4.55, 1.07] to −0.08.
  - Diagnostic in `results/sprint2/forecasts/diagnostic_wasp54_s50.json`; the
    primary results keep the event.
- **Implication.** A rule that requires most covered windows in a product to
  time successfully would catch this case. It is open defect S2-01 for review.

## 5. Candidate freeze package (C027)

| Item | Path |
|---|---|
| Configuration | `configs/candidate_freeze.json` |
| Roster: 184 planets on 175 hosts (156 core, 28 extension) | `results/sprint2/freeze_candidate/roster.csv` |
| Event manifest: 3,399 DRD-epoch events, identical to the sprint-1 inventory count | `results/sprint2/freeze_candidate/events_drd.csv` |
| Draft DRD forecasts (not frozen) | `results/sprint2/freeze_candidate/forecasts_drd_draft.csv.gz` |
| Candidate parameters | `results/sprint2/forecasts/candidate_parameters_t015v3.json` (t015v3c version kept for comparison) |
| Access receipt | `results/sprint2/freeze_candidate/access_receipt.json` |

- **Draft forecasts and candidate parameters.**
  - The draft forecasts are the M0–M3 predictive parameters at each event.
  - The candidate parameters are a release-transfer fit of DRC forecasts
    against all t015v3 development outcomes after DRC issue: 217 planets and
    2,328 events, with 400 host-refit parameter sets.
- **Access receipt.** A header-only scan of every FITS file under
  `data/raw/mast/`. All are in S46–S73, the maximum TSTOP is below the
  development boundary, and there are no violations.

**Not freeze-ready, for three reasons:**

1. the outcome rule is unqualified (§3);
2. defect S2-01 is open;
3. the reciprocal reviews have not happened yet.

## 6. Open items

| ID | Owner | Issue |
|---|---|---|
| S2-01 | Claude/Codex review | Product-level consistency rule against spurious windows (WASP-54b S50) |
| S2-02 | next design | Prespecified test of the ≥4-transit (metadata-defined) scope, and a decision on whether the sealed evaluation is restricted to it |
| S2-03 | next design | Bright-star (Tmag < 10) undercoverage of 0.915–0.918 and low recovery in stratum A |
| S2-04 | Codex review | Equal-host weighting gives single-transit hosts full weight. Decide whether the estimand should weight hosts by their expected sealed-era transit counts |
| S1-05 | both | Missing issued covariance, exposure lineage, selection denominator and limited calibration availability |
| — | Claude | Reciprocal review of sprint 1 (Barry's order: Codex reviews sprint 2 first) |

## Reproduce

```bash
uv run scripts/sprint2_outcomes.py run --sample dev
uv run scripts/sprint2_outcomes.py idtests
uv run scripts/sprint2_outcomes.py run --sample confirm
uv run scripts/sprint2_confirm2.py run
.venv/bin/python scripts/sprint2_analysis.py check
.venv/bin/python scripts/sprint2_analysis.py analyse --sample dev|confirm|confirm2
.venv/bin/python scripts/sprint2_analysis.py idsummary
uv run scripts/sprint2_remeasure.py select && uv run scripts/sprint2_remeasure.py run
.venv/bin/python scripts/sprint2_forecasts.py run --bootstrap 400
.venv/bin/python scripts/sprint2_forecasts.py candidate --convention t015v3 --output candidate_parameters_t015v3.json
.venv/bin/python scripts/sprint2_forecasts.py interface
.venv/bin/python scripts/sprint2_freeze_package.py roster
.venv/bin/python scripts/sprint2_freeze_package.py forecasts --parameters results/sprint2/forecasts/candidate_parameters_t015v3.json
.venv/bin/python scripts/sprint2_freeze_package.py receipt
.venv/bin/python scripts/sprint2_figures.py
.venv/bin/python -m unittest discover -s tests
```

Raw photometry stays in `data/raw/mast/` (gitignored); its SHA-256 hashes are
in the product tables. The I1 outcomes table and the likelihood grids are in
`data/derived/outcomes/t015v3/`. A gzipped copy of the outcomes is committed at
`results/outcomes/t015v3/outcomes.csv.gz`.
