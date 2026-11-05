# T015: forecast-independent TESS timing pipeline, development validation

**Independent review update (5 November):** retain this as the original report.
[Review and handoff](third_turn_review_2026-11-05.md) reproduces the injection
point estimates but narrows them to conditional known-shape recovery on four
hosts/five products. The 26 clusters are parent transits; overlapping placements
do not supply 261 independent noise realizations. The ExoClock multiplier and
per-outcome scaling proposal are not accepted. Grid quantiles, access-guard
ordering and the stated boundary also require correction before extension.
**Corrected and validated (Claude, 5 November):** see
[t015_validation_report.md](t015_validation_report.md) (D038–D039).

**Claude (Opus 5.5), 5 November 2026. Development material only (D014).** All
light curves are SPOC 120-s products from sectors S49–S56 (2022). The pipeline
refuses any sector outside S46–S73, and any file whose TSTOP is after
2024-01-03, before it reads flux. Nothing after 2025-11-18 was requested
(D023).

```bash
uv run scripts/t015_timing_pipeline.py          # PEP 723 env: lightkurve 2.5.1, batman, astropy
```

Outputs are in `results/t015/`:

| File | Contents |
|---|---|
| `t015_products.csv` | MAST file names, SHA-256, time-system keywords, data release |
| `t015_events.csv` | Per-transit lineage (cadence-number range, coverage) and timing |
| `t015_shapes.csv` | Fitted transit shapes |
| `t015_injections.csv` | Injection–recovery results |
| `t015_summary.json` | Summary statistics |

Raw FITS files are under `data/raw/mast/` (gitignored, 10 MB).

## Method (fixed before fitting)

- **Sample.** Four pilot-queue planets with SPOC 120-s data in the inspected
  era, chosen to span σ_Tmid from 0.13 to 0.7 min and to include the one
  unflagged DRB miss (WASP-80b, about 4σ). The choice was made before any
  fitting and is not random.

  | Planet | Sector(s) |
  |---|---|
  | HD209458b | S56 |
  | WASP-69b | S55 |
  | WASP-80b | S54 |
  | HAT-P-12b | S49, S50 |

- **Forecast independence.** No ExoClock or DRD ephemeris is used to find,
  window or fit a transit.
  - Period and epoch come from a blind BLS search (0.5–12 d) of each sector.
    The BLS periods match archive values to within 2×10⁻⁴ d.
  - Each transit time has a uniform prior over ±60 min, on a 2-s grid.
  - The baseline is linear per transit and solved at each trial time.
  - The posterior is exp(−χ²/2).
- **Shape.** rp, a/R*, inclination and Kipping q1, q2 are fitted to the
  sector's phase-folded data, following Ivshina & Winn (2022). A leave-one-out
  shape, which excludes the transit being timed, is the shared-shape
  sensitivity.
- **Uncertainty.** Two versions are kept.
  - White: the PDCSAP errors.
  - Scaled: the white errors times sqrt(max(χ²_ν, 1)) times β, where β is the
    time-averaging red-noise factor over 10–30-min bins.
- **Quality.** A transit is excluded unless at least 75% of the expected
  cadences are present both in the window and in transit; two failed. No other
  cut was applied.
- **Injection–recovery.** The fitted model is injected into real out-of-transit
  flux at phases 0.25–0.40 and 0.60–0.75, with random offsets of ±15 min, up to
  12 times per transit (seed 20261105). It is then refitted with the same
  procedure.
- **Lineage and time system.** Each event records its SPOC file, CADENCENO
  range, data release (97 or 98), TIMESYS = TDB, TIMEREF and BJDREFI = 2457000.
  BJD_TDB = TIME + 2457000 as stated by SPOC. It has not been independently
  reconverted.

## Results

| Check | Value |
|---|---|
| Transits timed / excluded on coverage | 27 / 2 |
| Matched to an ExoClock DRD mid-time for the same epoch | 27 / 27 |
| Ours − ExoClock: median; z-RMS; max \|z\| | −2.7 s; 0.31; 0.66 |
| Our σ / ExoClock σ, median (per planet) | 1.08 (0.96–1.17) |
| Injections (26 host-transit clusters) | 261 |
| Injection bias, median [95% cluster bootstrap] | −1.7 s [−3.9, +0.1] |
| Injection z-RMS, scaled σ | **1.03** [0.90, 1.17] |
| Injection z-RMS, white σ only | 1.25 [1.03, 1.50] |
| Implied scale on ExoClock's quoted σ (ours × z-RMS) | 1.12 [0.96, 1.29] |
| Leave-one-out shape shift, median \|Δ\| (max) | 0.3 s (16 s, HAT-P-12b S50) |

## What this establishes, and what it does not

1. **The pipeline is calibrated on real TESS noise for these four stars.**
   White-noise errors are about 25% too small. β- and χ²-scaled errors are
   consistent with unit scatter, and bias is at most about 4 s.
2. **ExoClock's DRD outcome timings are reproduced** to a few seconds for all
   27 events. This is a pipeline check on the same photons, not independent
   replication; the agreement z-RMS of 0.31 reflects shared data.
3. **The outcome-scale estimate is consistent across methods, though weakly.**
   Injections imply ExoClock's quoted σ are about 1.12× too small
   [0.96, 1.29]. The local-scatter estimate is a = 1.087 [1.04–1.12]
   (D026/D030). The two methods share no assumption about astrophysical jitter,
   but four planets cannot narrow a. A larger injection sample, stratified by
   Tmag and cadence, is the way to pin it down.
4. **WASP-80b's 4σ miss against DRB is not an outcome-measurement artefact.**
   Our times agree with ExoClock's within 5 s, against an O−C of about −1.1 min.
5. **Limits.**
   - Four bright to moderate stars, 120-s cadence only. FFI, 200-s and faint
     targets, which dominate the sealed era (median Tmag about 11.2), are
     untested.
   - HD209458b's shape fit has χ²_ν = 8.4, so its PDCSAP errors are
     underestimated. The scaling absorbs this, and injection z-RMS is 1.17.
   - HAT-P-12b S50 has q2 at its bound with only four transits, and its
     leave-one-out shift is up to 16 s, a third of σ.
   - Injections test noise calibration with a known shape. They do not test
     shape error or spot crossings.

## Proposed freeze items for the sealed-era pipeline (T009)

- **Inputs:** SPOC 2-min (and 20-s) products where they exist; one prespecified
  FFI route (TESS-SPOC or QLP) for the rest, validated in the same way first.
- **Fit:** blind BLS, a ±60-min uniform timing prior, the sector-shared shape,
  and β × sqrt(χ²_ν) scaling.
- **Quality:** coverage ≥ 0.75 is the only quality cut.
- **Injections:** run per sector and report them with every outcome.
- **Reporting:** carry each outcome's own injection z-RMS into the outcome-error
  scale, instead of a catalogue-wide a.
