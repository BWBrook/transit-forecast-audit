# Reconstruction, Step 3a: section abstracts (300 words each)

Working draft, 10 November 2026, by Claude (Opus 5.5), built from steps 1–2.
It uses the AAS sections: Introduction, Data and Methods, Results, Discussion,
then appendices. Display numbers follow `04_display_items.md`. Numbers come
from C019, C021, C038, C041–C043, C045, C046, C049–C054, C062 and C063. Each
section is at most 300 words.

## 1. Introduction

**Section abstract**

Many exoplanet observations, including most studies of atmospheres, happen
during transits lasting a few hours. Telescopes and missions such as JWST and
Ariel schedule them from ephemeris catalogues. These give each transit's
predicted mid-time and an uncertainty, which users treat as a forecast of
future error. ExoClock, built for Ariel, issues such catalogues as numbered
releases: DRB (2021), DRC (2022) and DRD (2025).

Ephemerides are known to drift as their errors propagate. Formal
uncertainties also miss transit-timing variations (TTVs) (Lissauer et al.
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

We provide a per-planet table comparing DRD's issued forecasts with TESS
transit times measured after its release, for 156 planets. It records every
predicted transit and its outcome. Before opening those data we recorded four
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

**Forecasts.** DRD became public on 18 November 2025. Each forecast is a
linear ephemeris whose variance needs the epoch–period correlation; ExoClock
does not publish it, so we reconstruct it from the release's own timings,
giving the issued Gaussian forecast M0. The correction, M2, widens the tails
by a log-normal variance mixture. Its one parameter was fitted to DRC
forecast errors for 206 planets in 2022–2024 development data.

**Cohort.** The core cohort has 156 planets: one DRD planet per star, TESS
magnitude below 13.5, period of 12 days or less, and no TTV flag at issue.
These give 3,103 predicted transits after 19 November 2025 in TESS SPOC
two-minute light curves. A 28-planet extension is exploratory (Appendix).

**Measurement.** A box search within ±0.5% of the catalogue period
scans all phases, not centring on the prediction. Each transit's mid-time
posterior is fitted. A fixed contract accepts a timing only for a valid
product and fit, and only within a quarter period of the predicted transit
(the P/4 gate). Two samples of artificial
transits qualified the rule beforehand (95% coverage 0.93–0.96).

**Freeze.** Before any later photometry was opened, SHA-256 hashes bound 75
files and 780 likelihood grids: the code, cohort, forecasts, fitted
correction and decision rule. Access was authorised on 8 November 2026. An
output-path fault forced one full rerun of unchanged code (Appendix).

**Scoring.** Each forecast is convolved with the measurement likelihood and
scored by the 95% interval score, divided by M0's predictive SD. Planets are
weighted equally. The H3 decision uses 2,000 joint resamples of stars, each
refitting M2. An interval excluding zero decides improvement or harm;
otherwise the result is inconclusive. Errors and coverage are
descriptive.

**After review.** Analyses added after external review are labelled and
placed in the Appendix: two independent re-timing programs, release-input
features and a window-allocation screen.

## 3. Results

**Section abstract**

**Sample (Table 1).** We accepted 2,185 of 3,103 predicted
transits (70%), for 151 of 156 planets, and 2,181 of the 2,369 with
enough TESS data at the predicted time (92%).

**Accuracy (Fig. 2).**

- The pooled median absolute error was 1.1 minutes (1.3 with planets
  weighted equally).
- Every accepted timing of 150 planets fell within 26.4 minutes.
- HR 858 b's errors reached 404 minutes.
- DRC forecasts stayed within 37 minutes for 128 planets, up to nearly four
  years after issue (development data).

**Calibration, H1 (Fig. 3).**

- Nominal 95% intervals, combined with measurement error, covered 90.8% of
  timings per planet (interval 87.8–93.4%).
- This is a departure of minutes, under the reconstructed covariance.
- M2 raised coverage to 97.6%, with intervals 1.67 times wider.

**The primary test, H3 (Table 2).** M2 − M0 was −0.12 (95% interval
−1.84 to +2.20): inconclusive. Most planets scored worse under M2;
the average gain came mainly from HR 858 b and depends on the loss scale.

**The exception (Fig. 4).**

- HR 858 b's 16 transits arrived 5.9–6.7 hours early. Two independent
  programs reproduced this from the same light curves.
- Against published ephemerides, HR 858 c ran 9–10 hours late and HR 858 d
  was on time, which favours TTVs over a shared clock error.
- New to DRD, its inputs ended in 2020 and scattered by roughly twice their
  quoted errors; the system's TTVs were already published.

**H2 and H4.**

- H2 is untestable with one gross miss; development associations were weak
  and unstable.
- H4 needs transit durations and attempted-observation records.
- No window-allocation rule, even one chosen with hindsight, beat spreading
  time evenly.

**The product (Table 3).** All 156 planets appear with forecasts, status,
timing counts, errors, coverage and release-input features, in full as a
machine-readable table.

## 4. Discussion

**Section abstract**

**What the hypotheses showed.**

- **H1:** the stated uncertainties are slightly too narrow once measurement
  error is added, by minutes, not hours. The cause is unidentified: missing
  noise terms, measurement error or covariance reconstruction.
- **H3:** a population correction does not clearly help. Widening every
  interval charges most planets width to insure against rare misses, so a
  few planets decide the average.

**The finding for observers.** For planets like these, the issued forecasts
were good to minutes. Rare failures were large and are not fixed by uniform
widening.

**How the work compares.**

- Shan et al. (2023) studied archival ephemerides of mixed age. Cohorts,
  horizons and selection differ, so we compare patterns, not rates.
- ExoClock IV's DRD comparison was optimistic by construction. Ours is held
  out.

**What curators could do.** HR 858 b was new to the release, with old,
scattered inputs and published TTVs. Flagging such ephemerides is a
hypothesis for future releases to test, not a validated rule.

**Limitations.**

- Scores exist only for accepted timings. The P/4 gate keeps misses beyond a
  quarter period out of the score, and some displaced transits may go
  unmeasured.
- Coverage is conditional on the reconstructed covariance and the
  measurement likelihoods.
- The test covers one release, one TESS season, and single-planet stars only.
- The independent re-timings share the same photons.
- There is one gross failure.

**Generalisation.** Freezing an issued forecast, measuring later outcomes
independently and scoring them with a proper rule suits any published
prediction that states its uncertainty. Examples are other ephemeris catalogues and
ecological forecasts.

**Next steps.**

- A descriptive gross-failure rate could come from the never-opened TESS
  sectors 74–97.
- Flags could be tested on future releases.
- The per-planet table lets other methods be scored against the same
  outcomes.
