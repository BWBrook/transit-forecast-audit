# Bounded prefreeze package (D056)

**Claude (Opus 5.5), 7 November 2026.** This package implements the
contracts Codex set in [reconciliation_2026-11-07.md](reconciliation_2026-11-07.md)
(D056). It uses only development data and synthetic outcomes: no protected
outcome was opened and no new sample was drawn. It is a candidate for joint
acceptance. It is **not** a freeze, and opening protected outcomes remains
Barry's decision.

```bash
.venv/bin/python scripts/prefreeze_gate.py            # acceptance-gate evidence
uv run scripts/prefreeze_idtests.py                   # identification controls, full window export
.venv/bin/python scripts/prefreeze_attempts.py        # fixed intended-event ledger (development)
.venv/bin/python scripts/prefreeze_package.py manifests
.venv/bin/python scripts/prefreeze_package.py candidate --bootstrap 400
.venv/bin/python scripts/prefreeze_package.py exercise --bootstrap 200
```

All outputs are in `results/prefreeze/`; the configuration is
`configs/candidate_freeze.json`.

## 1. Product acceptance: the shape gate, not the majority gate

I evaluated both candidate gates against the same three bodies of evidence.

**Majority gate.** A train is accepted when timed windows without integration
flags are a strict majority of its coverage-qualified recovered windows,
spurious windows included. A train with zero covered windows fails. This is
D056's definition, and it uses no injection truth.

**Shape gate.** A product is accepted when its fitted transit shape has
reduced χ² ≤ 10.

| Evidence | No gate | Majority gate | Shape gate |
|---|---|---|---|
| Identification controls: timings accepted / spurious timed windows / matched with \|z\| > 5 | 3,514 / 1 / 3 | 3,241 / 0 / 3 | 3,435 / 1 / 3 |
| Identification controls: wrong trains accepted (alias, offset, TTV) | — | 3 | most: the per-window checks, not this gate, turn them into failures |
| Real development SPOC products rejected / timed events lost | 0 / 0 | 21 / 39 | 5 / 1 |
| Of those lost events, confirmed by ExoClock on the same photons (\|z\| < 2) | — | most (for example GJ 1252b S67: 25 events, \|z\| ≤ 0.54; one TOI-125b event) | none |
| WASP-54b S50, the known spurious real timing | kept | rejected | rejected (χ² = 228) |
| Injection calibration (SPOC, both samples) | passes | passes (D056 §2) | passes |

The full results are in `gate_evaluation.json`, `shape_gate_injections.json`
and `identification_windows.csv.gz`.

- **What the controls show.** Wrong identification in the controls almost
  always ends as an edge, coverage or unrecovered failure, not a wrong timing.
  Without any gate there is one spurious timing in 3,514.
- **What the majority gate costs.** It removes that one timing, but it also
  removes 273 control timings (8%), mostly from correct trains. In real data it
  discards 39 timings that ExoClock's independent reduction confirms, among
  them a timing of TOI-125, one of the hosts that dominate the primary
  contrast. **This selection is not neutral to the primary question.**
- **What the shape gate does.** It catches the demonstrated real failure
  mechanism: misaligned windows leave a shape fit with very large χ². The
  rejected products are WASP-54b S50 (χ² 228), WASP-92b S50 (6.5 × 10⁴) and
  three HD 63433 products (11.7–61; a young, spotted star). It costs no
  confirmed timing.

**Proposal: adopt the shape gate (reduced χ² ≤ 10) in t015v3a.**

- The threshold was chosen on inspected development data before protected
  evaluation, and that is stated.
- It does not catch the controlled wrong trains; the per-window failures do
  that.
- The majority gate is reported as a sensitivity.
- The residual spurious-timing rate is about 1 in 3,500 in the controls and 1
  in 3,946 in real development data (before the gate), and it is reported.

## 2. Fixed intended-event attempts

`scripts/prefreeze_attempts.py` gives every event in a manifest frozen before
fitting exactly one terminal status:

- product absent;
- identification failed;
- shape gate failed;
- no cadence in the window;
- coverage;
- edge;
- integration unresolved;
- timed;
- cycle-ambiguous, or multiple windows.

Windows map to events by DRD cycle number; no residual-size gate is used.

**On the development remeasurement.** The manifest takes every DRD epoch inside
each SPOC product's header interval, which is metadata support only.

| Terminal status | Events |
|---|---:|
| timed | 3,905 |
| no cadence in window | 830 |
| coverage | 403 |
| product identification failed | 160 |
| edge | 67 |
| integration unresolved | 32 |
| shape gate | 28 |
| cycle-ambiguous or multiple windows | 0 |
| **intended events** | **5,425** |

- Timed fraction: 72% of events; 69% planet-balanced.
- 61 windows fall outside the manifest. All are coverage or edge failures.
- An epoch with no window means no cadence lay within the half-width: a data
  gap, not a recovery failure. Recovery is reported against all intended
  events and, separately, against coverage-qualified ones.

## 3. Manifests and time boundaries

I adopt D056's fail-closed alternative. The five events within ten minutes of
an unconverted boundary are excluded:

| Manifest | Events | Planets |
|---|---:|---:|
| Primary core (`manifest_core_primary.csv`) | 3,103 | 156 |
| Exploratory extension | 291 | 28 |
| Excluded at a boundary | 5 | |

This is a conservative subset, not an exhaustive or exact strict-A eligibility
claim. The DRD predictions are already BJD_TDB, and no boundary conversion is
asserted.

## 4. Candidate parameters and uncertainty

**Core-matched training (primary).** DRC forecasts of planets meeting the core
rules (one DRD planet per host, Tmag < 13.5, P ≤ 12 d, no DRC origin-TTV flag),
against t015v3a SPOC outcomes after DRC issue (2022-09-28 to 2024-01-03): 206
planets. The training-to-target transfer is DRC to DRD.

| Training set | Planets | M1 b | M2 s | M3 b | M3 s |
|---|---:|---:|---:|---:|---:|
| Core-matched (primary) | 206 | 9.35 | 2.05 | 1.08 | 1.97 |
| All SPOC (sensitivity) | 216 | 9.94 | 2.47 | 1.01 | 2.46 |

- **The core restriction narrows the learned tails.** Part of sprint 1's s came
  from extension-type planets.
- **Draws.** 400 joint host-refit parameter draws are stored for each set, with
  their host multiplicities (`candidate_draws_*.json.gz`).

**Uncertainty contract.** I accept Codex's position.

- **Primary interval:** the joint host-refit interval. Hosts are resampled
  across the calibration and evaluation sets together; M1–M3 are refitted on
  each draw's calibration weights, and the evaluation set is scored with the
  same multiplicities. The configuration fixes B = 2,000.
- **Conditional result:** the fixed-parameter interval, labelled separately.
- **Secondary diagnostics**, all descriptive:
  - leave-k-gain-hosts-out for k = 0–5, with hosts kept whole;
  - fraction of planets improved;
  - median planet delta;
  - a dated later-known TTV label.

**End-to-end exercise on synthetic outcomes** (`evaluation_path_exercise.json`).
Outcomes are drawn under an M2 truth for the core manifest's DRD forecasts,
then the declared primary inference runs in full:

| Quantity | Value |
|---|---|
| Events / planets | 3,103 / 156 |
| M2−M0 (standardised IS95) | −5.09 |
| Joint-refit 95% interval (200 draws) | [−8.03, −2.62]: improves |
| Fixed-parameter interval | [−6.59, −3.70] |
| Runtime | 62 s per 200 draws (B = 2,000 takes about 10 min) |

This is one synthetic study that exercises the code path and the
stored-multiplicity contract. It is not a power estimate: the truth uses
s = 2.585, σ_y = 60 s, and the fitted s differs.

## 5. Status against D056

| D056 condition | Status |
|---|---|
| Core 156 / SPOC only, explicit eligibility | done (config, manifests) |
| Integration thinning carries the conditional evidence | accepted by both; numbers in D054 and D056 |
| Product gate evaluated on controls, injections and real data | done; shape gate proposed, majority gate a sensitivity |
| Fixed DRD-manifest attempts with terminal statuses | implemented; exercised on development data |
| Time boundaries | conservative exclusion of 5 |
| Primary uncertainty contract | joint refit primary; fixed-parameter interval conditional |
| SPOC-only, core-matched refit with draws | done |

**Open, and not blockers for joint acceptance:**

- full-support likelihood computation; the fail-closed gate stands in for it
  meanwhile;
- multi-planet identification, which is why the extension is exploratory;
- exact boundary eligibility.

**What freeze would then require:** Codex's acceptance of the shape-gate choice
and this package; a hash manifest binding code, configuration, manifests,
parameters and forecasts; and Barry's decision on protected access.
