# T015 stratified validation: prespecified design

**Claude (Opus 5.5), 5 November 2026.** Written and committed before any new
photometry is requested, in response to D035
([review](third_turn_review_2026-11-05.md)). Development era only (D014).
Products are restricted to S56–S73 and must end on or before 2024-01-03 UTC.
Nothing after 2025-11-18 is requested (D023). Departures from this design
after the first run are recorded as deviations, with their reason.

## Question

Does the forecast-independent timing pipeline give unbiased mid-times with
calibrated uncertainties across the target regime of the sealed era? That
regime is bright to faint stars, with a median Tmag of about 11.2, and
includes 200-s FFI photometry. The test must also cover shape estimation,
avoid reusing noise, and keep calibration hosts apart from validation hosts.

## Corrections to the pipeline (from D035)

1. **Posterior quantiles.**
   - The posterior is the density exp(−χ²/2) on a grid; its CDF is taken by
     the trapezoid rule.
   - A coarse 10-s grid over the ±60-min prior finds the mode. A refined grid
     with step min(1 s, σ/25) covers ±10σ around the median.
   - Diagnostics are recorded. A transit is flagged if its coarse and refined
     medians differ by more than 0.1σ, or if more than 10⁻³ of the posterior
     mass lies within 5 min of a prior edge.
2. **β with gaps.**
   - Residuals are binned in fixed elapsed-time intervals (10, 15, 20 and
     30 min). A bin is kept only if it holds at least 80% of its expected
     cadences.
   - Each bin mean is standardised by σ₁/√nᵢ, where σ₁ is the residual RMS
     using N − 3 degrees of freedom (mid-time plus two baseline
     coefficients). β is the median over bin widths of the standardised
     scatter, with a floor of 1.
   - The transit-window reduced χ² also uses N − 3.
3. **Access guard, ordered before any data are read.**
   - The MAST search is restricted to S56–S73.
   - Before requesting a product, its MAST `t_max` must be no later than
     MJD 60312.98: the end of 2024-01-03, less 0.02 d.
   - The file is written with astroquery and is not read by lightkurve. Its
     header TSTOP must be no later than BTJD 3313.49 before the flux table
     is opened. That limit is the end of 2024-01-03 (JD 2460313.5) less
     0.01 d, which exceeds the largest barycentric light-time (8.4 min) plus
     TDB−UTC (69.2 s).
   - A product too close to the boundary to judge is excluded, not converted.
4. **Cadence.** The model integrates over each product's own exposure (header
   TIMEDEL), supersampled to 30 s or finer. The 120-s value is no longer
   hard-coded.

## Sample frame and selection

- **Frame.**
  - DRD catalogue planets on hosts with exactly one DRD planet. A blind BLS
    search on a multi-planet host may lock onto a different planet, so those
    hosts need a planet-targeted search and are out of scope here.
  - Coordinates, TIC and Tmag come from the archived `pscomppars` table
    (`data/raw/exoplanet_archive/`).
  - Each host must have tess-point coverage in at least one sector from S56
    to S73.
  - The four D034 hosts are excluded: they were used to build the pipeline.
- **Strata.** Tmag < 10, 10–11, 11–12 and 12–13.5, the TESS-SPOC FFI limit.
- **Order.**
  - Hosts within each stratum are ranked by SHA-256 of `t015v2:<TIC>`.
  - Walking down the ranking, a host is eligible if MAST lists a TESS-SPOC
    200-s light curve in S56–S73 that passes the guard.
  - The first 12 eligible hosts per stratum are taken, 48 in all.
  - When a host has several eligible sectors, the one whose
    `t015v2:<TIC>:<sector>` hash ranks first is used.
- **Products.** Each host contributes:
  - the TESS-SPOC 200-s light curve for its selected sector;
  - the SPOC 120-s light curve for the same sector, where one exists. This
    gives a paired cadence comparison on the same transits.
- **Split.** Odd ranks within each stratum go to calibration and even ranks
  to validation, giving 6 of each per stratum. The split is fixed before any
  fit.

## Real transits

- **Fit.**
  - Blind BLS search (0.5–12 d).
  - The BLS period must match the archive period within 0.5%. A mismatch is
    recorded as a failure and the product is not used further. The archive
    period is an identification check only, not a forecast.
  - Shape fit as in D034.
  - Each transit has a ±60-min uniform timing prior, and its errors are
    scaled by β·√max(χ²_ν, 1).
  - Coverage of at least 0.75 is required.
  - A leave-one-out shape is the shared-shape sensitivity.
- **Comparisons.** Both are agreement checks on shared photons, not tests of
  calibration:
  - against ExoClock DRD mid-times for the same epoch;
  - within each host, SPOC 120 s against TESS-SPOC 200 s.

## Injection–recovery through the full pipeline

For each product, there are two injection runs, at phase offsets φ = 0.27 and
0.73. Each offset gets an independent jitter drawn from U(−0.02, 0.02), with
seed 20261106.

- **Signal.**
  - Each run builds one copy of the light curve. It has a synthetic transit
    train at the real BLS period, using the real fitted shape as the truth.
  - Each injected transit gets its own timing offset, drawn from
    U(−2, +2) min.
  - The real transit windows (from the blind real-data BLS) are removed.
- **Recovery.**
  - The whole pipeline is rerun on the injected copy: blind BLS, a fresh
    shape fit, and timing of every injected transit.
  - BLS must recover the injected period within 0.1%, otherwise the run is
    recorded as a failure.
  - Generation and recovery therefore no longer share a fitted shape.
- **Disjoint noise.**
  - A run is dropped if either injected train's windows (half-width
    1.5·T14 + 60 min) overlap each other or a real window.
  - Within a product, every injected transit therefore uses distinct
    cadences.
  - Phases near 0.5 (secondary eclipse) are avoided.
- **Detrending sensitivity.** Each injection run is repeated with the same
  draws on SAP flux, which has no cotrending. This brackets the effect of
  PDC, which cannot be re-run on an injected signal. Real transits are also
  timed on SAP.

## Metrics and uncertainty

- **Per injected transit.**
  - z = (posterior median − truth)/σ, where σ is the half-width of the
    68.27% central posterior interval.
  - Coverage of the 68.27% and 95.45% central posterior intervals.
  - Whether |z| > 3.
- **Groups.** Results are reported by stratum, by product type (TESS-SPOC
  200 s or SPOC 120 s), by flux (PDCSAP or SAP), and by calibration or
  validation set.
- **Statistics.** For each group:
  - the number of hosts and of injections;
  - z-RMS and median bias, in seconds and in units of σ;
  - both coverages and the |z| > 3 rate;
  - BLS, coverage and edge failure rates.
- **Uncertainty.** Host-cluster percentile bootstrap, B = 10 000. The host is
  the resampling unit, keeping all its products and runs together.
- **Primary result.** Validation hosts, TESS-SPOC 200 s, PDCSAP, all strata
  pooled, using the error rule β·√max(χ²_ν, 1).
- **Secondary rule.** One multiplier k per product type, estimated as z-RMS
  on the calibration hosts, then applied to the validation hosts.

## Acceptance criteria (fixed now)

The pipeline is freeze-ready for a product type and stratum if, on the
validation hosts:

- 95.45%-interval coverage is at least 0.90, with a host-bootstrap lower
  bound of at least 0.85;
- the z-RMS interval includes 1, with an upper bound no higher than 1.25;
- the median bias is below 0.1σ in absolute value;
- BLS and edge failures together are at most 20% of products.

A stratum that fails is not usable with this rule. For that stratum, the
protocol must either exclude it or carry a validated multiplier, which needs
a further, separately prespecified validation. Six validation hosts per
stratum will not narrow the scale to ±3%. The pooled interval reports the
precision actually achieved, together with the between-host spread.

## What this still does not test

- Spot crossings and other shape misspecification beyond refitting the same
  model family.
- PDC's response to a real transit, which is bracketed by SAP only.
- QLP products.
- Multi-planet hosts.
- 20-s data.
- Population transfer beyond single-planet DRD hosts with Tmag below 13.5.
