# Sprint 2 outcome rule t015v3 and its confirmation experiment

**Claude (Opus 5.5), 7 November 2026. Prespecified before any confirmation
photometry was requested.** Development era only (D014); every product passes
both access guards (MAST `t_max` before the request, header TSTOP before flux
is read). This document amends A2 of the
[two-sprint plan](two_sprint_plan_2026-11-05.md) for the reasons given in §4,
and answers open defects S1-01, S1-02, S1-04 and S1-06 from
`results/sprint1/handoff.json`.

The rule is frozen at the commit that adds this file. `scripts/sprint2_outcomes.py`
and `scripts/t015_timing_pipeline.py` do not change between that commit and the
confirmation analysis. Each run receipt records `rule_version` (commit plus
source hash). Any later change creates a new rule version, for which this
confirmation does not count.

## 1. What changed from t015v2 (D039), and why

| Change | Reason |
|---|---|
| Identification: BLS restricted to the catalogue period ±0.5%, epoch searched over the full phase; depth SNR ≥ 7; other DRD planets on the host masked (DRD ephemeris, ±max(0.25 d, 2·T14 guess) + 3σ). If 0.5% × baseline is shorter than the BLS duration, the period is not identifiable within the sector and is fixed at the catalogue value. | Covers P > 12 d and multi-planet hosts (R4, R8). The epoch remains blind, so a forecast error, however large, cannot steer the window. |
| Shape fit: a/R* bounded to [¼, 4] × the BLS-implied guess (cap 300, was a fixed 40); a fitted T14 below ¼ of the BLS duration is an identification failure | The fixed bound truncated long-period planets; degenerate grazing fits are failures, not timings. |
| Windows: 1.5·T14 + 60 min; T14/2 + 90 min when P < 1.4 d | R7. All 10 short-period development runs dropped by D039 now inject. |
| Exact 2.5/97.5% posterior quantiles, `gauss_ok`, flat-prior likelihood grids | I1 / D042: q0228/q9772 bound 95.45%, not 95%. |
| One ledger row per intended injected truth, written before fitting; one-to-one assignment of recovered windows (Hungarian, 60-min gate = prior half-width); terminal status for every truth | S1-01. Recovery and calibration now have separate, explicit denominators. |
| Controls: (i) **subtract** the fitted real transits instead of removing their windows; (ii) **shape** misspecification: impact parameter +0.2, limb darkening (q1 +0.2, q2 −0.15), Gaussian spot bumps (0.2 × depth, width 0.12·T14) on half the transits | S1-04 and the window-removal question. |

## 2. Development evidence (inspected; the 48 D039 hosts)

Commands: `uv run scripts/sprint2_outcomes.py run --sample dev`, then
`.venv/bin/python scripts/sprint2_analysis.py analyse --sample dev`. Output in
`results/sprint2/dev/summary.json`. Production set: SPOC 120 s where the host
has it, otherwise TESS-SPOC 200 s; PDCSAP; removal mode.

| Quantity | t015v3 (no multiplier) | t015v3c (Tmag multiplier) |
|---|---|---|
| Hosts / timed injections | 45 / 682 | 45 / 682 |
| Equal-host z-RMS [90% CI] | 0.944 [0.884, 1.005] | 1.000 [0.942, 1.057] |
| Equal-host 95% coverage | 0.958 [0.940, 0.975] | 0.945 [0.924, 0.964] |
| Equal-host mean z | +0.054 [−0.035, +0.144] | +0.057 [−0.038, +0.152] |
| z-RMS at Tmag 9 (arithmetic model) | [0.934, 1.176] | [0.926, 1.149] |
| z-RMS at Tmag 13.5 | **[0.633, 0.905]** | [0.840, 1.061] |
| Equal-host recovery of observable truths | 0.906 [0.833, 0.969] | same |

- **Faint-star conservatism is real in these light curves and is not the
  estimator.** Raw-error z-RMS in stratum D is 0.84 although χ²_ν ≈ 0.88. In
  synthetic white noise the same code is calibrated at σ = 43, 118 and 241 s
  (raw-error z-RMS 1.00, 1.00, 1.03; 1,000–1,338 transits each), with no late
  bias (median z −0.04 ± 0.03). The mechanism in real faint-star PDCSAP data is
  not identified.
- **Multiplier.** t015v3c multiplies σ, its quantiles and any likelihood grid by
  g(Tmag) = √max(0.8857 − 0.0919 (T − 11), 0.25), with T clamped to [8, 13.5].
  Fitted by equal-host least squares of host mean z² on Tmag − 11, using all 45
  development hosts. g = 1.034 at Tmag 9 and 0.810 at Tmag 13.5. A split-half
  check overshot (slope −0.18 from 22 hosts), so the slope is uncertain. That is
  why t015v3 without the multiplier is analysed alongside as a prespecified
  secondary rule.
- **Window removal has no detectable effect.** Removal and subtraction give the
  same per-host z-RMS to two decimals. Injection-window and real-window β and
  residual RMS have median ratios 1.000 and 1.001 (IQR 0.989–1.016).
- **Shape misspecification** (§1, control ii) is a stress test, reported in
  `summary.json`. It is not a criterion: spot crossings bias timings by
  construction.
- **D039's positive bias recurs at a smaller size.** Equal-host mean z is
  +0.05. Under the old point criterion, D039's median z of +0.08 to +0.10 was
  borderline. Stratum B has mean z +0.215 [+0.049, +0.391] on 10–11 hosts.
- **The development hosts do not pass the amended criteria**, and are not
  meant to qualify anything. With 45 hosts, below the 60-host minimum,
  t015v3c misses the coverage bound (lower limit 0.924 against 0.93) and the
  mean-z bound (upper limit 0.152 against 0.15). t015v3 without the
  multiplier misses z-RMS and both Tmag endpoints. The multiplier was fitted
  on these same hosts.

## 3. Confirmation sample (fixed; `results/sprint2/confirm/selection.csv`)

- **Frame.** The 278 D039 frame hosts never reached: single-DRD-planet hosts,
  Tmag < 13.5, with S56–S73 pointing.
- **Draw.** 30 per Tmag stratum, in the existing SHA-256 rank order. Each host
  needs at least one SPOC 120-s or TESS-SPOC 200-s product passing the guard
  (one D-stratum host had none). The sector is chosen by the hash
  `t015v2:confirm:<TIC>:<sector>` among SPOC 120-s sectors when any exist,
  otherwise among FFI sectors.
- **Result.** 120 hosts, all with TESS-SPOC 200 s; 119 also have SPOC 120 s for
  the same sector. 12 have P > 12 d and 10 have P < 1.4 d, all retained.
- **Fixed size.** No top-ups, replacements or post-outcome exclusions. Every
  failure stays in the ledger.
- **Runs.** Phases 0.27 and 0.73 (± U(0.02)), per-transit offsets U(±2 min),
  seed [20261107, TIC]. Removal mode is primary, subtraction is the control.
  Both products, PDCSAP.

## 4. Estimands and criteria (amended A2)

**Target.** Calibration of the timing posterior for a new transit of an
eligible host, given successful identification and timing. Each host has total
weight one, and its timed events share that weight equally.

| Quantity | Estimator | Criterion (90% host-cluster percentile bootstrap, B = 10,000) |
|---|---|---|
| Adequacy | hosts with ≥ 1 timed injection | ≥ 60 |
| z-RMS | √(mean over hosts of host mean z²) | CI within [1/1.10, 1.10] |
| 95% coverage | mean over hosts of host coverage of exact 2.5/97.5% limits | CI lower bound ≥ 0.93 |
| Bias | mean over hosts of host mean z (median reported) | CI within ±0.15 |
| Tmag trend | equal-host OLS of host mean z² on Tmag − 11; endpoint √prediction | CIs at Tmag 9 and 13.5 within [0.80, 1.15] |
| Window-removal control | median over host-products of the injection/real-window ratios of β and residual RMS | within [0.95, 1.05] |
| Recovery | mean over hosts of timed / observable intended truths, all failures included | reported per stratum with 90% CI; no threshold |

**Why these margins.** The forecast audit scores the residual T_obs − T_pred
against a predictive variance of σ_f² + σ_y². Suppose the outcome errors are
mis-scaled by a factor k, or biased by δσ_y. Then the nominal 95% predictive
interval covers at a different rate, and the distortion is largest when σ_y
dominates. That is the usual case here: σ_y·a/σ_f has median 2.6 (IQR
1.7–3.6) over the release-transfer development events. With σ_y dominant:

| k, δ | Coverage of nominal 95% (σ_y/σ_f = 1) | (σ_y dominant) |
|---|---|---|
| 1.10, 0 | 93.8% | 92.5% |
| 1/1.10, 0 | 96.0% | 96.9% |
| 1, 0.15 | 94.9% | 94.7% |
| 1.10, 0.15 | 93.6% | 92.3% |

The margins therefore bound the measurement-induced distortion of forecast
coverage at about 2.5 percentage points, or 2.8 jointly, a third or less of the
5–7-point miscalibration that sprint 1 found in the issued forecasts (M0
coverage 88.4–89.8%). This replaces the null A1 tolerance (D044). It is derived
from the score, not from the inconclusive contrast. The bias tolerance moves
from 0.10 on the median to 0.15 on the mean. The mean is the more efficient
estimator of a location shift, and at 0.15 the bias costs 0.3 points of
coverage on its own.

**Interval calibration (negative controls).**
`.venv/bin/python scripts/sprint2_analysis.py check`, output in
`results/sprint2/estimand_negative_controls.json`. It simulates 120 hosts with
the development per-host event counts, 300 replicates per scenario.

- The estimators are unbiased: mean estimates are within 0.007 of the truth.
- The 90% intervals cover 0.853–0.927, across Gaussian, heteroscedastic,
  shared-shape, t₅-tailed and Tmag-trend truths.
- The percentile bootstrap is therefore slightly anti-conservative, and the
  criteria inherit that. It is a stated limitation, not adjusted after the
  fact.
- The uncorrected log-MSE endpoint that D041 proposed is retired (S1-02). Its
  intervals covered 0.56–0.68 in Codex's audit.

**Decision.**

1. The primary rule is **t015v3c on the production set**: SPOC 120 s, or
   TESS-SPOC 200 s where SPOC is absent. If every criterion passes, it is
   qualified for single-DRD-planet hosts with Tmag < 13.5, S56–S73, catalogue
   period identification and PDCSAP.
2. If only a Tmag endpoint fails, the declared population narrows to the Tmag
   range whose endpoint, re-evaluated at the stratum boundary (12 or 11), passes.
   That narrowing is reported as such.
3. If the z-RMS, coverage or bias criterion fails, the rule is not ready. The
   failure evidence and the strongest supported scope are delivered instead.
4. Each product type is assessed separately with the same criteria. A product
   type that fails is removed from the declared population.
5. t015v3 without the multiplier is reported in full. It cannot replace a
   failed t015v3c after the fact.
6. The extension to multi-planet hosts is not covered by this sample. It rests
   on the identification tests (§5) and on the remeasured same-photon
   agreement, and it is labelled accordingly.

## 5. Identification tests (development hosts; reported, not criteria)

`uv run scripts/sprint2_outcomes.py idtests` injects, with real transits
subtracted and epochs uniform over phase:

- trains with true period P_cat × (1 + δ), δ ∈ {0, ±0.2, ±0.4, ±0.6}%;
- aliases at 0.5, 2 and 3 × P_cat;
- every third transit displaced by 30, 50, 70, 90 or 120 min from the linear
  ephemeris.

Expected behaviour:

- **Period offsets.** Inside ±0.5%, recovery does not depend on δ or phase.
  Outside it, the result is an identification failure or a misidentification,
  never silent mistiming.
- **Displaced transits.** Displacements under about 55 min are timed.
  Displacements beyond the 60-min prior are unmatched (failures), so
  per-transit TTVs above about an hour are a declared selection of this rule.
- **Forecast errors.** These enter only through the epoch, which is searched
  blind. A forecast residual of hours does not affect identification.

## 6. Development remeasurement (R5) under the same frozen rule

`uv run scripts/sprint2_remeasure.py select|run` times every supported
S46–S73 transit of the 321 sprint-1 cohort planets on 314 hosts. That is 618
sector products (617 SPOC 120 s and one TESS-SPOC 200 s), written as I1 rows
for every attempted event. 190 cohort hosts are also in the confirmation frame.

Both runs use the rule frozen here, and neither feeds back into the other's
analysis. The remeasurement times real transits; the confirmation calibrates
injections. Both can therefore run after this commit. The convention
comparison and refit are in `scripts/sprint2_forecasts.py` (R5 acceptance as
in the plan). Outcome σ for t015v3c is σ × g(Tmag).

*Reporting corrections after the freeze commit (rule code unchanged): negative-control ranges taken from the JSON; development verdict and stratum-B bias stated explicitly.*
