# T015 stratified validation: results

**Claude (Opus 5.5), 5 November 2026. Development material only (D014).** This
executes the design committed at `26590c3`
([t015_validation_design.md](t015_validation_design.md)), with the
corrections from D035. All products are from S56–S73 and passed both guard
stages: MAST `t_max` before the request, and header TSTOP before the flux was
read. Nothing after 2025-11-18 was requested.

```bash
uv run scripts/t015_timing_pipeline.py                 # corrected re-timing of the D034 hosts
uv run scripts/t015_stratified_validation.py select    # frame + MAST metadata
uv run scripts/t015_stratified_validation.py run       # 48 hosts, 8 workers, about 25 min
uv run scripts/t015_stratified_validation.py analyse
```

Outputs are in `results/t015_validation/` and `results/t015_corrected/`. Raw
FITS files are in `data/raw/mast/` (gitignored); their SHA-256 hashes are in
`products.csv`.

## Corrections (D035) and their effect on D034

Re-timing the 27 D034 transits with the corrected pipeline (the same five
files, hashes matching):

| Quantity | Value |
|---|---|
| v1 minus corrected mid-time | median −1.0 s (−1.85 to −0.73) |
| v1 σ / corrected σ | median 0.99 (0.91–1.06) |
| Agreement with ExoClock | z-RMS 0.29, median −1.7 s |
| Convergence or edge flags | none |

Codex's grid finding is confirmed on real data. The cumulative-sum
convention placed medians about 1 s early, which is most of D034's −1.7 s
injection bias. The access guard now acts before any request and again before
any flux is read. The boundary is the end of 2024-01-03 less a light-time
margin.

## Sample

- **Frame.** 327 single-DRD-planet hosts with S56–S73 pointing.
  - Excluded: 220 with no pointing in that range, 25 with more than one DRD
    planet, 7 outside the Tmag strata, the 4 D034 hosts, and 1 without a TIC
    ID.
- **Selection.** 12 hosts per stratum, by hash rank. One host was skipped for
  having no TESS-SPOC 200-s product. 47 of the 48 hosts also have SPOC 120-s
  data for the same sector.
- **Products.** 190 product–flux combinations: 176 ok and 14 with the BLS
  period misidentified. These come from five hosts:
  - EPIC 211945201 (P = 19.5 d) and K2-333 (P = 14.8 d) are beyond the
    prespecified 12-d BLS limit. This is a design oversight: the frame did
    not exclude them.
  - K2-3 (P = 10.1 d, shallow).
  - TOI-122, FFI PDCSAP only (BLS found a 1/10 alias).
  - TOI-2497, FFI PDCSAP only (P = 10.7 d, period off by 2%).
- **Injection runs.** 352 runs:
  - 293 succeeded;
  - 35 failed BLS recovery, mostly long-period or bright, large-amplitude
    hosts;
  - 24 were dropped because their windows overlapped, all from 55 Cnc,
    WASP-121 and WASP-173A, whose periods are under 1.4 d.
- **Timed transits.** 2,096 injected transits, each from a distinct cadence
  range within its product. 1,295 real transits.

## Primary result (prespecified)

TESS-SPOC 200 s, PDCSAP flux, validation hosts, all strata pooled, rule
β·√max(χ²_ν, 1). Intervals are 95% percentile bootstraps over hosts.

| Metric | Value [95% host bootstrap] | Criterion | Pass |
|---|---|---|---|
| Hosts / injections | 18 / 263 | — | — |
| 95.45% interval coverage | 0.958 [0.934, 0.981] | ≥ 0.90, lower bound ≥ 0.85 | yes |
| 68.27% coverage | 0.700 [0.653, 0.750] | reported | — |
| z-RMS | 0.981 [0.920, 1.045] | CI includes 1, upper ≤ 1.25 | yes |
| Median bias | +6.7 s; +0.082σ [−0.065, +0.188] | \|bias\| < 0.1σ | yes |
| \|z\| > 3 | 0.4% | reported | — |
| BLS and edge failures | 7.4% | ≤ 20% | yes |

**The primary test passes**, and SPOC 120-s PDCSAP passes on the same
criteria:

- z-RMS 0.970 [0.896, 1.039];
- 95% coverage 0.951 [0.936, 0.969];
- bias +0.09σ;
- failures 4.5%.

Calibration hosts tell the same story:

| Calibration hosts | z-RMS | 95% coverage |
|---|---|---|
| FFI | 0.920 | 0.973 |
| 2-min | 0.991 | 0.954 |

The secondary multiplier k makes things worse. Estimated on the calibration
hosts, k = 0.92 for FFI, which gives validation z-RMS 1.07 and 95% coverage
0.943. The primary rule is retained, with no extra multiplier.

## Per stratum (prespecified): not freeze-ready

Validation hosts, PDCSAP:

| Stratum | Product | Hosts | z-RMS [CI] | 95% coverage | Bias (σ) [CI] | Fails |
|---|---|---|---|---|---|---|
| A (Tmag < 10) | FFI | 3 | 0.92 [0.80, 1.02] | 0.97 | +0.24 [−0.01, 0.45] | bias; failures 25% |
| B (10–11) | FFI | 4 | 1.01 [0.91, 1.17] | 0.97 | −0.41 [−0.48, −0.18] | bias |
| C (11–12) | FFI | 5 | 1.05 [0.90, 1.14] | 0.94 | +0.13 [0.08, 0.31] | bias |
| D (12–13.5) | FFI | 6 | 0.92 [0.83, 0.99] | 0.96 | +0.16 [−0.06, 0.22] | bias; z-RMS below 1 |
| A | 2-min | 3 | 1.01 | 0.95 | +0.21 | bias |
| B | 2-min | 4 | 1.07 [0.95, 1.28] | 0.93 | −0.23 | bias; z-RMS upper bound |
| C | 2-min | 5 | 0.95 | 0.95 | +0.16 | bias |
| D | 2-min | 6 | 0.88 [0.79, 0.95] | 0.98 | +0.15 | bias; z-RMS below 1 |

By the prespecified rule, no stratum is freeze-ready with PDCSAP. I am not
relaxing that rule after seeing the data. The diagnostics below bear on how
the next validation should be designed. They do not change this verdict.

- **Bias test.** Nearly every per-stratum failure is the point-estimate bias
  criterion, tested on 3–6 hosts.
- **No shared bias component.** A one-way variance decomposition of z finds
  none, either between injection runs or between hosts:
  - FFI: ICC 0.00 by run and by host;
  - 2-min: ICC 0.03, with a between-host SD of z of 0.16.
  - Per-host median z varies by about ±0.4, which is consistent with sampling
    error (SE ≈ 0.3 for 10–20 transits).
- **Few clusters.** Percentile bootstraps over 4–5 hosts undercover. The B
  and C bias intervals that exclude zero are not by themselves evidence of a
  Tmag-dependent bias. They are also opposite in sign.
- **Faint stars.** Stratum D's failure is conservative: σ is about 8–12% too
  large and coverage is 0.96–0.98. Its z-RMS interval excludes 1 for both
  products.
- **Bright stars.** Stratum A's 25% failure rate comes from one host beyond
  the BLS period range and from injection BLS failures on bright hosts. It is
  not a timing-calibration failure.

## Sensitivities and cross-checks

- **SAP instead of PDCSAP.**
  - FFI: z-RMS 1.00, 95% coverage 0.954, bias +0.11σ.
  - 2-min: z-RMS 0.94, 95% coverage 0.951, bias +0.18σ.
  - Coverage holds; the bias is slightly larger. Without cotrending, the
    per-transit linear baseline still gives calibrated intervals for these
    targets. PDC's response to a real transit remains bracketed rather than
    tested.
- **White-noise errors alone** are nearly calibrated in this sample: FFI
  z-RMS 1.03 and coverage 0.951. D034's 25% excess was dominated by
  HD209458b's strongly correlated residuals, which make it unrepresentative.
- **Real transits, FFI against 2-min, same transits.** 322 pairs: median
  difference +0.5 s, z-RMS 0.35 (shared photons), median σ ratio
  FFI/2-min 1.01. For these hosts, 200-s FFI timing loses no precision.
- **Real transits against ExoClock DRD.** 623 matches; z-RMS 0.36, max |z|
  1.5. This is again a same-photon pipeline check.
- **Leave-one-out shape shift.** Median |Δ| is 1.3 s.

## Deviations from the design

1. Each host uses its own random stream, seeded with [20261106, TIC]. Each
   phase's draws are reused across that host's products and fluxes, which
   pairs the comparisons. The design named only the seed.
2. Calibration-set stratum summaries use B = 2,000. All criteria use
   B = 10,000.
3. A per-host exception wrapper was added before the full run. No host raised
   an exception.
4. Each injected truth is matched to the nearest recovered window, within
   one window half-width.
5. As noted above, the frame should have excluded periods beyond the
   prespecified BLS range. Those cases are kept and counted as failures, as
   the design specified.

## Consequences for the freeze (T009)

Proposed, pending Codex review:

- **Outcome error rule.** The pooled rule (PDCSAP, β·√max(χ²_ν, 1), no
  multiplier) can be the frozen outcome-error rule, for single-planet hosts
  with Tmag below 13.5 and periods inside the search range. On validation
  hosts, the pipeline's own errors need no extra scale.
- **Comparison with ExoClock's quoted σ.** For the same real transits, our σ
  is larger than ExoClock's: the median per-host ratio is 1.107
  [1.064, 1.152] for FFI and 1.091 [1.063, 1.122] for 2-min, across 40
  hosts. That is numerically close to the REML a = 1.087 (D026/D030).
  - It does not identify an ExoClock error multiplier (D035). A reduction
    that adopts literature shape parameters can legitimately quote smaller σ.
  - It does establish that outcomes measured by this pipeline carry σ about
    10% wider than ExoClock's. Scoring therefore cannot mix the two error
    conventions.
- **Per-stratum readiness** needs a confirmation sample. The frame has 278
  further hosts that were never reached. The criteria should be stated as
  interval tests with a minimum host count, prespecified before that sample is
  drawn.
- **Coverage gaps before production.**
  - Periods above 12 d and multi-planet hosts need a planet-identification
    step. Whether that step may use the catalogue period without leaking
    forecast information is a decision still to make.
  - Periods below about 1.4 d need a narrower window rule.
- **Still untested.**
  - Spot crossings and other shape misspecification beyond the fitted model
    family.
  - QLP products.
  - Tmag above 13.5.
