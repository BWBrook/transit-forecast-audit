# Reconstruction, Step 3a: section abstracts (300 words each)

Working draft, 10 November 2026, by Claude (Opus 5.5), built from steps 1–2.
It uses the AAS sections: Introduction, Data and Methods, Results, Discussion,
then appendices. Display numbers follow `04_display_items.md`. Numbers come
from C019, C021, C038, C041–C043, C045, C046, C049–C054, C062 and C063. Each
section is at most 300 words.

Codex's 10 November review corrections are incorporated below; rationale and
saved-source checks are in `10_step3a_review.md`. These remain section plans,
not changes to the article or completed new data products.

## 1. Introduction

**Section abstract**

Many studies of planets and their atmospheres rely on observing transits
lasting hours. Scheduling requires predicted mid-times and uncertainties.
Catalogue ephemerides supply these forecasts. ExoClock, built for Ariel,
issues such catalogues as numbered
releases: DRB (2021), DRC (2022) and DRD (2025).

Prediction errors grow as period errors accumulate. Interacting planets can
also shift transit times away from a linear prediction (TTVs) (Lissauer et al.
2020, 2024; Agol et al. 2024). Earlier comparisons of predictions with later
TESS timings flagged discrepant planets: Shan et al. (2023) found 31 offsets
among 262 hot Jupiters. ExoClock IV compared its own releases with later
timings, but its DRD comparison included timings that went into DRD.

Proper scoring rules, which judge forecast spread and accuracy together, are
standard in forecasting. In a bounded
search we found no study that froze an issued release, measured later timings
independently, and scored the stated uncertainties on data unopened when the
test was fixed. The logic follows retrospective model testing in ecology
(Brook et al. 2000): a stated uncertainty is a hypothesis about future errors.

Our planned table compares DRD's issued forecasts with later TESS observations
for all 156 intended planets, recording every intended transit's status.
Before opening those data we recorded four
questions:

- **H1:** do measured times follow the stated uncertainty once measurement
  error is included?
- **H2:** do planets with short or patchy histories do worse than their
  precision implies?
- **H3:** does a correction learned from the previous release improve the
  next? This is the prespecified primary test.
- **H4:** do windows based on stated uncertainty hold the intended share of
  transits?

## 2. Data and Methods

**Section abstract**

**Forecasts.** DRD became public on 18 November 2025. Gaussian M0 uses its published
linear ephemeris and errors, with unpublished epoch–period correlation
reconstructed from released timings. M2 widens the tails through a log-normal
variance mixture. Its one parameter was fitted to DRC errors for 206 planets
in 2022–early-2024 development data.

**Cohort.** The core has 156 planets: one DRD-catalogued planet per star, TESS
magnitude below 13.5, period of 12 days or less, and no TTV flag at issue.
These give 3,103 intended transits from 19 November 2025 in TESS SPOC
two-minute light curves. A 28-planet extension is exploratory (Appendix).

**Measurement.** A box search within ±0.5% of the catalogue period scans all
phases. Recovered timings are assigned to the nearest DRD cycle. Acceptance
requires a shape-fit reduced χ² ≤ 100, resolved integration, valid timing
diagnostics and likelihood support, and an assigned residual within P/4.
Two artificial-transit samples passed the conditional calibration criteria:
nominal 95% timing intervals covered 94.7% and 95.0%.

**Freeze.** Before later photometry was opened, hashes bound 75 files and 780
likelihood grids. Access was authorised on 8 November 2026. An output-path
fault required a full rerun of unchanged code (Appendix).

**Scoring.** Forecasts are convolved with Gaussian or grid measurement-error
distributions. The 95% interval score is divided by M0's predictive SD,
including measurement error, equally weighting planets. Interpretation
conditions on the estimated timing model and acceptance; alternative loss
scales are reported. H3 uses 2,000 joint resamples of calibration and evaluation
stars, refitting M2. A 95% interval below zero decides improvement, above zero
harm, otherwise inconclusive.

**After review.** Labelled appendix analyses cover independent re-timing,
release-input features and a window-allocation screen.

## 3. Results

**Section abstract**

**Sample (Table 1).** We accepted 2,185 of 3,103 predicted
transits (70%), for 151 of 156 planets, and 2,181 of the 2,369 with
enough TESS data at the predicted time (92%).

**Accuracy (Fig. 2).**

- The pooled median absolute error was 1.1 minutes (1.3 with planets
  weighted equally).
- Every accepted timing of 150 planets fell within 26.4 minutes.
- Development comparisons of DRC reached nearly four years: 128 planets
  stayed within 37 minutes.

**Calibration, H1 (Fig. 3).**

- Nominal 95% intervals, combined with measurement error, covered 90.8% of
  accepted timings per planet (conditional interval 87.8–93.4%), under the
  reconstructed covariance and supplied timing likelihoods.
- M2 raised coverage to 97.6%, with intervals 1.67 times wider.

**The primary test, H3 (Table 2).** M2 − M0 was −0.12 (95% interval
−1.84 to +2.20): inconclusive. 111 of 151 planets scored worse under M2;
the average gain came mainly from HR 858 b and depends on the loss scale.

**The exception (Fig. 4).**

- HR 858 b's 16 timings arrived 5.9–6.7 hours early. Independent programs
  reproduced this from shared light curves.
- Against published ephemerides, HR 858 c ran 9–10 hours late and HR 858 d
  was on time, favouring TTVs over a shared clock error.
- New to DRD, its inputs ended in 2020 and scattered by roughly twice their
  quoted errors; the system's TTVs were already published.

**H2 and H4.**

- The development span predictor did not transfer reliably; H2 remains unresolved.
- H4: midpoint containment is described; operational capture needs
  durations and attempted-observation records.
- Within the tested 10% policy and padding grid, hindsight selection never
  beat both equal-budget comparisons.

**The planned product (Table 3).** A machine-readable table will cover all 156
planets: forecasts, status, timing counts, errors, coverage and input features;
five without accepted timings retain null results.

## 4. Discussion

**Section abstract**

**What the hypotheses showed.**

- **H1:** combined 95% intervals under-cover accepted measured timings under
  the covariance reconstruction and timing model. This does not identify
  the catalogue uncertainty alone as too small, or the cause.
- **H3:** the correction's benefit is inconclusive. Wider intervals increase
  width costs for most planets and reduce penalties for a few large residuals.
  All 16 HR 858 b timings remain outside every model's 95% interval.

**The finding for observers.** Accepted timings mostly agreed with issued
predictions to minutes. The table will show where they did not and provide
a benchmark for checking future methods.

**How the work compares.**

- Shan et al. (2023) studied archival ephemerides of mixed age. Cohorts,
  horizons and selection differ, so we compare patterns, not rates.
- ExoClock IV's DRD comparison reused fit data; ours uses later observations.

**What curators could do.** HR 858 b's old, scattered inputs, prior TTV reports
and first appearance in DRD suggest a candidate flag for future testing.

**Limitations.**

- Only accepted timings are scored. Nearest-cycle matching and P/4 selection
  can exclude displaced events or alias whole-cycle errors; neither guarantees
  completeness within P/4.
- Coverage is conditional on the reconstructed covariance and the
  measurement likelihoods.
- The test covers one release's first year and hosts with one DRD-listed planet,
  including physically multiple systems.
- The independent re-timings share the same photons.
- There is one gross failure.

**Generalisation.** Fixing a published forecast and protocol before inspecting
later outcomes also suits other ephemeris catalogues and ecological forecasts,
with explicit observation and selection assumptions.

**Next steps.**

- Unopened sectors 74–97 could support a separately authorised study, with
  recovery and cycle identification qualified before estimating gross-failure rates.
- Flags could be tested on future releases.
- The per-planet table lets other methods be scored against the same
  outcomes.
