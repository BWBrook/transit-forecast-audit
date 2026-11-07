---
title: "How well do published transit ephemerides predict later transits?"
subtitle: "An availability-aware audit of ExoClock forecasts against independently measured TESS mid-times, with a population calibration trained on an earlier release"
author:
  - "Barry W. Brook"
date: "Repository draft v0.2, 7 November 2026 (development evidence only; no final evaluation exists)"
bibliography: ../references/references.bib
link-citations: true
---

<!--
DRAFT STATUS. Repository draft, not a submission. Written to be rebuilt from the living repository: every number carries a claim ID from coordination/claims.md.
Sprint-2 claims: C022 development calibration and white-noise tests; C023 negative controls; C024 identification tests; C025 confirmation, replication and exploratory split; C026 remeasurement, convention transfer and the WASP-54b diagnostic; C027 candidate freeze package and access receipt.
Open slot: {{S2-INTERFACE}} (production-I1 scoring receipt). Missing citations are written [CITATION NEEDED: ...]. Do not hand-write bibliography entries.
-->

# Abstract

**Question.** ExoClock publishes linear transit ephemerides with timing uncertainties. We ask how well those uncertainties describe later, independently measured TESS transit mid-times, and whether a population calibration learned from an earlier release improves the predictive distribution of the next one.

**Development findings (inspected data only).** Scoring DRC ephemerides against 2,324 catalogue timings of 238 planets on 232 hosts, nominal 95% intervals cover 88.40% of outcomes; a calibration fitted to DRB-era errors raises coverage to 95.61% at the cost of mean interval width rising from 10.13 to 16.44 minutes (C018). The prespecified contrast, the planet-balanced change in the standardised 95% interval score, is −2.445 in favour of the tails-only mixture (M2) with a 95% host-refit interval of [−5.756, +0.187]: inconclusive (C018). A chronological split gives −2.628 [−6.351, +0.067] (C018). Only 23.5% and 19.4% of planets improve, and two hosts, TOI-1130 and TOI-125, supply about 69% and 86% of the mean gains (C018). The gain is tail-risk reduction in a few planets, not typical-planet improvement.

**Outcome measurement: not ready.** The final evaluation needs mid-times we measure ourselves from TESS photometry, and that pipeline failed its prespecified tests. The primary rule, with a Tmag multiplier fitted on the development hosts (`t015v3c`), failed a 120-host confirmation: equal-host 95% coverage 0.936 with a lower bound of 0.922 against 0.93, and a Tmag-13.5 z-RMS endpoint of [1.062, 1.195] against [0.80, 1.15]. The multiplier over-corrected (C025). The uncorrected rule (`t015v3`) passed every criterion on that sample, but only as a prespecified secondary analysis that could not qualify it. One prespecified replication of `t015v3` on 120 never-sampled hosts then failed: z-RMS 1.095 [1.002, 1.214], coverage 0.929 [0.908, 0.947] and both Tmag endpoints (C025). No margin was relaxed and no host added or dropped. An exploratory split, defined after the replication, finds hosts with at least four timed transits calibrated in both samples (z-RMS 0.992 and 1.012; coverage 0.944 and 0.953), with the failure concentrated in hosts with one to three transits (C025). That proposes a narrower scope but needs its own prespecified test. Calibration transfer between outcome conventions (R5) is accepted: with ExoClock timings, `t015v3c` or `t015v3` outcomes, every matched M2 minus M0 contrast is negative and inconclusive (C026).

**Boundary.** No final evaluation has been run. TESS outcomes after 2025-11-18 are unopened. The planned test scores the issued DRD ephemerides of 184 planets on 175 hosts (3,399 predicted opportunities). A candidate package exists but is not freeze-ready: its outcome rule is unqualified, a defect remains open and reciprocal review has not happened (C021, C027).

# 1. Introduction

Planning a transit observation requires a predicted mid-time and an honest statement of how wrong it may be. Ephemeris catalogues supply both. A user who schedules telescope time, or a space mission that must point at a window, relies on the quoted uncertainty being a calibrated description of future error. Whether it is has been tested less often than the ephemerides have been refitted.

**Prior work.** ExoClock IV compares DRB, DRC and DRD predictions with later TESS timings in its Section 5.1 and Table 5, and states that the DRD comparison is optimistic because those timings entered that release [@Kokori2026ExoClockIV]. The release series is documented in @Kokori2022ExoClockI, @Kokori2022ExoClockII and @Kokori2023ExoClockIII. Shan et al. compare an archive of predictions with TESS timings for 262 hot Jupiters and then study 31 discrepant systems [@Shan2023TESSTimings]. Large TESS timing compilations and ephemeris refits supply alternative outcome products [@IvshinaWinn2022; @Mallonn2019; @Edwards2021ORBYTS; @Wang2024PeriodVariation]. Kaye and Aigrain propagate epoch-period covariance into forecasts for Kepler and K2 planets [@KayeAigrain2025], following the pivot argument of @Deeg2015. @Dragomir2020 model how ephemerides degrade with time, and @Lissauer2020Ephemerides document unreliability from timing variations. @Eastman2010 set the time-standard conventions we rely on. Proper scoring rules and the calibration-sharpness framework are standard [@GneitingRaftery2007; @GneitingBalabdaouiRaftery2007]. [CITATION NEEDED: Ma et al. 2025, ExoEcho I, HST timings with leave-one-out and error-floor checks, arXiv 2501.05704] and [CITATION NEEDED: robust or heavy-tailed transit-timing residual models, as screened in docs/literature_update_2026-11-05.md] are the other closest methods we screened.

**What this work adds, and what it does not.** Retrospective validation of old ephemerides against later timings is not new, and neither are covariance propagation, heavy-tailed timing models or proper scores. The candidate contribution is a combination, conditional on the experiment succeeding. It joins five features that we did not find together in the 82 forward citations of ExoClock III and IV returned by OpenAlex (a bounded search; other indexes return different totals): (i) exact issued ephemeris files with documented public-availability times; (ii) probabilistic scoring of measured outcomes with forecast and outcome uncertainty kept distinct; (iii) a proper interval score as the primary comparison; (iv) planet-balanced summaries with host-cluster uncertainty; and (v) a calibration trained before, and applied unchanged to, a later block that the investigators have not inspected (C019, `docs/sprint1_literature_review.md`).

**Retrospective evaluation as method.** The design follows the logic of Brook et al., who estimated population-viability models on the first half of long ecological time series and scored their predictions on the second half [@Brook2000PVA]. The physical processes differ. The shared principle is that a model's stated uncertainty is a hypothesis about its future errors and should be tested on replicated, later data.

**Central question.** For the DRC and DRD releases, do the issued uncertainties support their intended interpretation for later independent TESS mid-times, and does a calibration learned from the earlier release improve the predictive distribution? The prespecified primary contrast is the planet-balanced change in the standardised 95% interval score between the issued Gaussian forecast and the tails-only calibrated forecast (M2 minus M0).

**Scope of evidence in this draft.** The article is a snapshot of a living repository. It reports development evidence: analyses that used TESS outcomes dated 2022-01-01 to 2024-01-03, all of which the investigators have inspected and none of which can serve as untouched validation (D014). The final evaluation block (outcomes after 2025-11-18) has not been opened. Where a section would hold final-evaluation results it says so.

# 2. Methods

## 2.1 Cohort and release availability

The forecast products are the DRB, DRC and DRD ephemeris catalogues deposited on OSF (DOIs in Data availability). We treat each file as an issued forecast and record, separately for each, the end of its input observations, the first verified public availability, the forecast origin used in our analysis and the retrieval time.

Availability comes from OSF API logs for the node and for each exact file. Under the assumption that a file present in an already-public node, or added to one, is retrievable at the later of the two timestamps, the public anchors are 2021-10-27 12:03:15 UTC (DRB), 2022-09-27 15:25:16 UTC (DRC) and 2025-11-18 09:43:24 UTC (DRD) (C019). DRD's files were uploaded on 17 November while the node was private, so its anchor is the 18 November public transition. The first whole UTC day, 2025-11-19, is the primary eligibility anchor for the final evaluation. The February 2026 journal date is a sensitivity anchor (C019). These logs establish public availability, not discoverability, and do not exclude earlier private sharing.

The DRC timing table was added 53 seconds after the DRC forecast file (C019). It carries no observation-time or first-availability field. A DRB-to-DRC transfer that trains on DRC-file timings is therefore an event-date proxy and not a historical deployment, and we label it so throughout.

**Final-evaluation cohort (metadata only).** A metadata inventory, using TESS pointing predictions and official sector calendars and without opening photometry, identifies planets with a public eligible product, a predicted opportunity after the availability anchor and no DRD origin-TTV flag. The core cohort (single DRD planet per host, TESS magnitude Tmag < 13.5, period P ≤ 12 d) has 156 planets. An extension (P > 12 d, or hosts with several DRD planets) adds 28, for 184 planets on 175 hosts and 3,399 conservative predicted opportunities; the extension adds 17.95% to the core (C021). Four planets with unresolved cohort status and their 134 opportunities are outside this union. Opportunities are not outcomes: capture, identification and recovery are unknown until the photometry is opened (C021).

**Development cohort.** The development comparisons use the planets of DRB and DRC with catalogue timings in 2021-10-28 to 2024-01-03 (Section 2.5). The remeasurement experiment (Section 2.4) targets every supported S46-S73 transit of the 321 sprint-1 cohort planets on 314 hosts, in 618 sector products. The run attempted 4,615 events and timed 3,946 (failures: 470 for coverage, 116 for identification, 83 at the prior edge); 294 planets have timings (C026).

**Origin-known flags.** A planet whose timing variations became apparent after the forecast stays in the cohort, because that difficulty belongs to the historical prediction (D015). Only flags known at the origin define strata or exclusions. Hindsight flags appear solely in the reproduction of the published benchmark.

## 2.2 Forecasts, covariance tiers and the closed model set

For epoch n counted from the issued reference epoch, the issued forecast is T_pred(n) = T0 + nP. Its forecast variance is σ²_T0 + 2nρσ_T0σ_P + n²σ²_P. ExoClock does not publish ρ. We reconstruct it by weighted least squares on the release's own timings and carry a tier:

| Tier | Meaning |
|---|---|
| C1 | covariance or joint posterior available and verified (none for ExoClock) |
| C2 | reconstructed ρ whose refitted period agrees with the published period within 3σ_P; approximately decorrelated at the published pivot |
| C3 | refit disagrees with the published period; retained, flagged and analysed with and without |
| C4 | unresolved uncertainty or time provenance; excluded and counted |

Reconstructed correlations change total forecast variance by at most about 0.27%, 0.98% and 2.94% for DRB, DRC and DRD (C004). These are sensitivities and not recovery of an issued covariance. We never treat missing covariance as zero without labelling it. No C3 planet occurs in the development cohorts (C018).

**Closed comparator set.** Four methods, fixed before the sprint-1 fits (D041, D042):

| Method | Predictive distribution of the forecast error |
|---|---|
| M0 | Issued Gaussian with reconstructed covariance |
| M1 | M0 forecast SD multiplied by one fitted factor b |
| M2 | Tails only: b = 1; the forecast SD is multiplied by a lognormal factor with median 1 and log-scale SD s, fitted |
| M3 | Both: b and s fitted |

The latent forecast error is convolved with the independent measurement error of the outcome, so each predictive distribution describes the measured mid-time, not the latent true time. The convolution is a Gaussian sum for M0 and M1, and numerical integration (384 quadrature nodes, checked against 192) for the mixtures. Fitting is bounded maximum likelihood with no regularisation prior. M0 is a reconstruction of an issued ephemeris and not a recovered issued joint posterior. M2 holds the median multiplier at one but still changes predictive width, because the mixture adds tail mass.

**Why M2 is the primary comparator.** Release-to-release transfer is the main risk for a learned correction. DRB forecasts are about 2.25 times overconfident at the median (b = 2.249, s = 1.093), while DRC is calibrated at the median (b = 0.976) and has a heavy tail between planets (s = 3.149) (C009). A single scale learned on DRB would widen DRC intervals by a factor near 2.3 and would probably hurt most planets. A tails-only correction can in principle transfer. The development results below support that reasoning and also show its limits.

## 2.3 Scoring, weighting and host-cluster uncertainty

**Interval score.** The 95% interval score is IS(l, u; x) = (u − l) + (2/α)(l − x)₊ + (2/α)(x − u)₊ with α = 0.05, where [l, u] is the central 95% interval of the predictive distribution and x the measured mid-time [@GneitingRaftery2007]. Smaller is better. It penalises width and misses together.

**Standardised IS95 (primary).** Each event's IS95 is divided by the **M0 predictive SD at that event, outcome error included**, the same divisor for every method. This stops a few long-extrapolation planets, whose errors are hours, from dominating a minutes-scale average (the earlier influence result was in log score, D037). Because the outcome-error term is measured after the forecast is issued and depends on the photometry, this is a conditional weighted loss and not an unconditionally proper issue-time score (D042). We report alongside it the raw score in minutes, the score divided by the forecast-only SD, the negative log score, 68.27% and 95% coverage, mean 95% width, the fraction of planets that improve, and a leave-top-two-hosts-out influence check.

**Weighting.** Each planet has weight one. Events within a planet are weighted equally. Each comparison uses one forecast origin.

**Host-cluster uncertainty.** The paired difference in planet-balanced standardised IS95, M2 minus M0, is the decision statistic. Hosts are resampled jointly across fitting and scoring, and M1-M3 are refitted in every resample. We use 400 resamples for primary comparisons and 200 for sensitivities. A 95% percentile interval wholly below zero is "improves", wholly above is "worsens", otherwise "inconclusive". These intervals are conditional development uncertainty, not a validated population procedure for a 15-host training sample. Resampling at the host level treats planets of one star and repeated transits of one planet as dependent. Counts of events, planets and hosts accompany every comparison.

Coverage of measured outcomes does not establish coverage of the unobserved true mid-time at the stated rate. We do not interpret it as such.

## 2.4 Independent outcome measurement

The final evaluation scores forecasts against mid-times we measure from TESS photometry with a forecast-independent pipeline, because catalogue timings after 2025-11-18 would not be independent of the next release and carry unknown exposure lineage. The rule is `t015v3` with the multiplier variant `t015v3c`, prespecified in `docs/sprint2_outcome_design.md` and frozen at commit 2c39f0a before any confirmation photometry was requested.

**Products and access guards.** The production product is SPOC 120-s PDCSAP flux where it exists for the sector, otherwise TESS-SPOC 200-s PDCSAP flux; a paired product of one observation is never scored twice. Two guards act on the development era: MAST `t_max` is checked before a product is requested, and the FITS header TSTOP is checked before flux is read (limit BTJD 3313.49, 2024-01-03). The access receipt for the candidate freeze scanned the headers of 996 FITS files, all in S46-S73, with a maximum TSTOP of BTJD 3312.66 and no violations (C027).

**Identification.** A box-least-squares search runs within the catalogue period ± 0.5% with the epoch searched blind over the full phase, so a forecast error of any size cannot steer the window. A detection needs depth SNR ≥ 7. Other DRD planets on the host are masked. If 0.5% of the baseline is shorter than the BLS duration, the period is fixed at the catalogue value. A fitted T14 under a quarter of the BLS duration is an identification failure and not a timing.

**Timing.** Each transit window is 1.5·T14 + 60 min, or T14/2 + 90 min when P < 1.4 d. A transit shape is fitted per planet-sector-product (a/R* bounded to a quarter to four times the BLS-implied guess) and mid-times carry posterior quantiles on a flat-prior grid centred on the data's own epoch, not the forecast. The reported σ is the posterior 68% half-width, with an error convention β·√max(χ²_ν, 1). Exact 2.5% and 97.5% quantiles are recorded; a likelihood grid is written when a posterior is not Gaussian within 10%.

**Outcome-error convention and Tmag multiplier.** `t015v3c` multiplies σ, its quantiles and any likelihood grid by g(Tmag) = √max(0.8857 − 0.0919(T − 11), 0.25), with T clamped to [8, 13.5]. g is 1.034 at Tmag 9 and 0.810 at Tmag 13.5. The coefficients are an equal-host least-squares fit of host mean z² on Tmag − 11 using all 45 development hosts, so the multiplier is fitted in-sample. A split-half check overshot (slope −0.18 from 22 hosts), so the slope is uncertain. `t015v3` without the multiplier is analysed in full as a prespecified secondary rule and cannot replace a failed `t015v3c` after the fact (C022).

**Injection calibration and the attempt ledger.** To calibrate the posterior timing error without photometry from the protected era, we inject synthetic transit trains into real development-era light curves and rerun identification, shape fit and timing. The real transits are removed (primary) or subtracted (control) from the host. One row per intended injected truth is written before any fit, so recovery has an explicit denominator. Recovered windows are assigned to truths one-to-one (Hungarian assignment, 60-min gate, equal to the prior half-width). Every attempt receives a terminal status: timed, excluded_coverage, product_id_failed, run_id_failed, edge or not_recovered. Injected phases are 0.27 and 0.73 (± U(0.02)), with per-transit offsets U(±2 min).

**Estimands and criteria.** The target is the calibration of the timing posterior for a new transit of an eligible host, given successful identification and timing. Each host has total weight one and its timed events share it equally. The criteria (90% host-cluster percentile bootstrap, B = 10,000) were fixed before any confirmation photometry was requested:

| Quantity | Estimator | Criterion |
|---|---|---|
| Adequacy | hosts with at least one timed injection | at least 60 |
| z-RMS | √(mean over hosts of host mean z²) | interval within [1/1.10, 1.10] |
| 95% coverage | mean over hosts of host coverage of the exact limits | lower bound at least 0.93 |
| Bias | mean over hosts of host mean z | interval within ±0.15 |
| Tmag trend | equal-host OLS of host mean z² on Tmag − 11; endpoint √prediction | intervals at Tmag 9 and 13.5 within [0.80, 1.15] |
| Window-removal control | median of injection-to-real-window ratios of β and residual RMS | within [0.95, 1.05] |
| Recovery | mean over hosts of timed / observable intended truths, all failures included | reported per stratum with 90% interval; no threshold |

The margins are derived from the score, not from the inconclusive forecast contrast. If outcome errors are mis-scaled by a factor k or biased by δσ_y, the nominal 95% predictive interval covers at a different rate, with the largest distortion when outcome error dominates the forecast error. Outcome error does dominate: σ_y·a/σ_f has median 2.6 (interquartile range 1.7-3.6) over the release-transfer development events. For k = 1.10 coverage falls to 93.8% (σ_y/σ_f = 1) or 92.5% (σ_y dominant); for k = 1/1.10 it rises to 96.0% or 96.9%; for δ = 0.15 it is 94.9% or 94.7%; jointly 93.6% or 92.3% (C022, `docs/sprint2_outcome_design.md` section 4). The margins bound the measurement-induced coverage distortion at about 2.5 percentage points (2.8 jointly), a third or less of the 5-7-point miscalibration of the issued forecasts (M0 coverage 88.4-89.8%). They replace a null tolerance, since the sprint-1 sensitivity grid does not certify a measurement tolerance (D044).

**Interval calibration of the estimators.** `sprint2_analysis.py check` simulates 120 hosts with the development per-host event counts (1-56, median 12), 300 replicates per scenario, under Gaussian, heteroscedastic, shared-shape, t₅-tailed and Tmag-trend truths. The estimators are unbiased: mean estimates are within 0.007 of the truth in every scenario (for example, pooled z-RMS 1.0026 for a truth of 1). The nominal 90% intervals cover 0.853-0.927 of the time, so the percentile bootstrap is slightly anti-conservative and the criteria inherit that (C023). This is a stated limitation, not adjusted. An earlier proposal to regress log host mean-square on Tmag is retired: its endpoint intervals covered 0.56-0.68 in a Gaussian negative control (C020).

**Decision rule.** If every criterion passes, the rule is qualified for single-DRD-planet hosts with Tmag < 13.5, S56-S73, catalogue-period identification and PDCSAP. If only a Tmag endpoint fails, the declared population narrows to the Tmag range whose endpoint at the stratum boundary passes. If the z-RMS, coverage or bias criterion fails, the rule is not ready and the failure evidence and strongest supported scope are delivered instead. Each product type is assessed separately.

**Confirmation sample.** The frame is the 278 hosts of the earlier validation frame that were never reached: single-DRD-planet hosts with Tmag < 13.5 and S56-S73 pointing. Thirty hosts per Tmag stratum are drawn in a fixed SHA-256 rank order, requiring at least one SPOC 120-s or TESS-SPOC 200-s product that passes the guard (one host had none). The sector is chosen by hash among SPOC 120-s sectors where available, otherwise among FFI sectors. The result is 120 hosts, all with TESS-SPOC 200 s and 119 also with SPOC 120 s for the same sector; 12 have P > 12 d and 10 have P < 1.4 d, all retained. Sample size is fixed: no top-ups, replacements or post-outcome exclusions, and every failure stays in the ledger. Of the 120 hosts, 106 produced timed injections (1,496 events) (C025).

**Replication.** The primary rule failed this confirmation (Section 3.6), while uncorrected `t015v3` passed as a secondary analysis. A rule chosen after seeing the data cannot be confirmed by that data. We therefore prespecified one replication of fixed `t015v3` on hosts never sampled, before requesting any replication photometry (design committed at 9375b3c, `docs/sprint2_replication_design.md`). The frame is the earlier validation frame hosts reached by neither earlier sample (37, 36, 51 and 33 hosts in strata A to D), 30 drawn per stratum in the same hash order, with sectors drawn by hash. All 120 hosts have SPOC 120-s and TESS-SPOC 200-s products. Criteria, estimands, bootstrap and seed are unchanged, and the two samples are reported separately and never pooled for the decision. No further replication will be run. Many replication hosts (82 of 120) were also in the development remeasurement, which timed their real transits with the same frozen rule; this contact is disclosed and not used as an exclusion (C025).

## 2.5 Development designs for the forecast comparison

All four designs use the same scoring, resampling and decision rule (Section 2.3) and the catalogue-reported outcome convention (σ × a with a = 1.087, the conditional REML estimate of the excess scatter scale of TESS timings; C005, C008).

| Design | Training | Scored | Status |
|---|---|---|---|
| Release transfer | DRB forecasts against DRC-file timings, 2021-10-28 to 2022-09-26 | DRC forecasts against DRD-file timings, 2022-09-28 to 2024-01-03 | event-date proxy: the training file was uploaded after DRC's forecast |
| Chronological | DRC forecasts, outcomes in 2022 | DRC forecasts, outcomes 2023-01-01 to 2024-01-03 | observation-date proxy: some training events predate DRC issue |
| Delayed origin | as release transfer, origin the day after both DRC files were public | scoring from 2022-09-29 | inputs historically available; correction built now after inspection, never issued |
| Later-published sensitivity | DRB forecasts against DRD-file timings in 2022-01-01 to 2022-09-26 | as release transfer | calibration-sample sensitivity only |

Release transfer and the chronological split are the primary development comparisons. If they disagree, the disagreement is the finding (plan R1). None of the four is an issued correction, a historically deployable rule or an untouched test.

**Sensitivities.** The primary contrast is also computed with zero covariance and with ρ at ±1, and over an outcome-scale grid a = 0.85-1.25 (reference 1.087).

**Remeasured-outcome refit (R5).** To test whether a calibration fitted under catalogue outcome errors transfers to our pipeline, we remeasure every supported development-era transit of the cohort with the frozen rule and refit M1-M3 under four conventions: ExoClock timings × a restricted to the transits our pipeline also timed ("exoclock_matched"); our mid-times and σ × 1 for the same transits ("ours_matched"); every transit our pipeline timed ("ours_all"); and the unrestricted catalogue comparison of sprint 1 ("exoclock_all"). Transfer is accepted if the matched comparisons agree in the sign of the primary contrast and in its decision. Otherwise the final evaluation uses only our convention (C026). The paired differences between our mid-times and ExoClock's for the same photons (Section 3.7) show whether the conventions differ in scale or in centre.

# 3. Results (development evidence only)

## 3.1 The published benchmark reproduces

An independent base-R calculation reproduces every DRB and DRC count and percentage of ExoClock IV Table 5 from hash-verified release files. DRD differs by one 1-σ count; the "Initial" column is not reproduced (C001). The published rule excludes 42 DRD planets flagged for timing variations, which screens on information that postdates the forecasts; the project's primary cohort rule uses origin-known flags only (D015). The numerical reproduction does not recover the authors' event list or code.

## 3.2 Issued uncertainties are overconfident in the tails

Table 1 gives the release-transfer and chronological comparisons at the reference convention (a = 1.087, C2 covariance).

**Table 1. Forecast comparison, development data (C018).** Standardised IS95 is planet-balanced; smaller is better. Events/planets/hosts scored: release transfer 2,324/238/232; chronological 1,925/206/200. Training: 15 planets on 15 hosts (172 events); 133 planets on 131 hosts (1,696 events).

| Design | Method | Fitted parameters | Standardised IS95 | 95% coverage | 68% coverage | Mean 95% width (min) | Negative log score | Planets improved |
|---|---|---|---:|---:|---:|---:|---:|---:|
| Release transfer | M0 | none | 32.86 | 0.884 | 0.619 | 10.13 | 19.55 | n/a |
| | M1 | b = 2.685 | 30.50 | 0.957 | 0.789 | 16.53 | 9.80 | 23.1% |
| | M2 | s = 2.162 | 30.41 | 0.956 | 0.674 | 16.44 | 6.46 | 23.5% |
| | M3 | b = 2.685, s ≈ 0 | 30.50 | 0.957 | 0.789 | 16.53 | 9.80 | 23.1% |
| Chronological | M0 | none | 36.60 | 0.898 | 0.638 | 10.82 | 21.60 | n/a |
| | M1 | b = 7.343 | 34.94 | 0.982 | 0.946 | 41.23 | 7.77 | 7.3% |
| | M2 | s = 2.310 | 33.97 | 0.955 | 0.698 | 19.12 | 6.49 | 19.4% |
| | M3 | b = 1.349, s = 1.985 | 33.83 | 0.955 | 0.729 | 20.33 | 6.50 | 18.5% |

The primary contrast, M2 minus M0, is **−2.445 [−5.756, +0.187]** for release transfer and **−2.628 [−6.351, +0.067]** chronologically (C018). Both intervals include zero. The delayed-origin reconstruction gives −2.435 [−5.729, +0.373] and the later-published training sensitivity −2.497 [−5.862, +0.242] (C018). All four are inconclusive. We do not claim a forecast improvement.

**What the point estimates do show.**

- *Coverage and tails.* M0's nominal 95% intervals cover 88.40% of release-transfer outcomes and 89.75% of chronological outcomes. M2 brings both near nominal (95.61%, 95.45%) and its 68% coverage lands near nominal (0.674, 0.698). The host-refit intervals for the coverage gain exclude zero in both designs, as do those for log score, and the interval width grows: release transfer from 10.13 to 16.44 minutes, chronological from 10.82 to 19.12 minutes (C018).
- *Most planets do not improve.* 23.5% (release transfer) and 19.4% (chronological) of planets have a lower standardised IS95 under M2, so the typical planet is scored worse; the median planet difference is positive (+0.93 and +1.17) (C018).
- *Two hosts carry the mean.* TOI-1130 and TOI-125 account for about 69% and 86% of the mean gains. Leaving them out leaves the M2 point contrast at −0.780 (release transfer) and −0.364 (chronological) (C018). We introduced no exclusions of future residuals to remove these hosts.
- *Training planets lose, new planets gain.* In release transfer, the 14 planets common to training and scoring score worse under M2 (+0.352) while the 224 new planets score better (−2.620) (C018).

**M1 is unstable and M3 collapses.** A single scale learned in the chronological split is b = 7.34. It widens mean 95% intervals to 41.2 minutes and improves only 7.3% of planets, with a point contrast of −1.660 and an interval of [−8.868, +9.785]. In release transfer M3 converges to M1 (s ≈ 0), so the data do not support both parameters. These results are the actual reason for the tails-only comparator: a scale learned on a miscalibrated release does not transfer cleanly, and the tail parameter is the more stable quantity (C018, C009).

**Sensitivity to outcome error and covariance (C018).** The M2 point contrast stays negative across a = 0.85-1.25. The decision is inconclusive on the tested grid from a = 1.05 through 1.25. At a ≤ 1.00 the 200-resample intervals exclude zero, but that nominal improvement is sensitive to bootstrap tail resolution. This does not establish a continuous threshold or a measurement tolerance, and the handoff records `certified_measurement_tolerance: null`. With zero covariance, or ρ at −1 or +1, the M2 interval still includes zero; the point contrast ranges from −5.887 to −1.472 in release transfer and −6.430 to −1.544 chronologically. Zero covariance and C2 are almost identical here, which is not recovery of the missing issued covariance.

![Outcome-scale sensitivity of the M1-M3 contrasts with 95% host-refit intervals. The dashed line marks the reference a = 1.087 (C018). Development data.](../results/sprint1/outcome_scale_sensitivity.png)

## 3.3 What earlier development fits found about forecast error

These results motivated the model set and are retained as context, with their limits (all development):

- Conditional REML gives an outcome-error scale a = 1.087 for TESS timings, with a host-bootstrap interval of 1.050-1.121 (C005, C008). This identifies a conditional dispersion and does not attribute it to measurement error alone (C003).
- A stable mixture fit gives DRB b = 2.249, s = 1.093 and DRC b = 0.976, s = 3.149 (C009). DRC host-bootstrap intervals are 0.712-1.357 for b and 1.576-4.211 for s (C014).
- A training-span predictor of the mixing scale improved held-out log score by 0.027 nats per window [0.007, 0.054] on one split (C010), but a chronological version is unstable. Its point gain of 0.013 nats per window ranges from −9.07 to +0.043 over 400 joint-host resamples, and four extreme losses were independently reproduced (C015). The span predictor is not selected.

## 3.4 The outcome measurement: calibration on injected transits

**Ledger and denominators.** The development run covers the 48 earlier-validation hosts. Across all modes and products, the ledger records 4,063 timed injections, 391 excluded for timing coverage, 356 not recovered, 276 from products whose identification failed, 16 from runs whose identification failed and 7 at the sector edge. By status, 520 runs succeeded, 42 failed because their product failed identification and 8 failed their own identification; 88 of 95 products identified. There are no spurious windows and no duplicate truth assignments; the largest match distance is 857 s against the 3,600 s gate (C022). Product failures, run failures and event failures have separate denominators and are never summed into one rate. This repairs the earlier 7.4% figure, which divided products plus runs by a mixture of both (C020).

**Calibration of the multiplier-free and multiplier rules.** Table 2 gives equal-host estimates on the production set with real transits removed (45 hosts with at least one timed injection, 682 timed injections, 1-56 per host).

**Table 2. Injected-transit calibration, development hosts (C022).** Intervals are 90% host-cluster percentile bootstrap (B = 10,000). The multiplier of `t015v3c` was fitted on these hosts.

| Quantity | `t015v3` (no multiplier) | `t015v3c` (Tmag multiplier) | Criterion |
|---|---|---|---|
| Equal-host z-RMS | 0.944 [0.884, 1.005] | 1.000 [0.942, 1.057] | within [0.909, 1.10] |
| Equal-host 95% coverage | 0.958 [0.940, 0.975] | 0.945 [0.924, 0.964] | lower bound ≥ 0.93 |
| Equal-host mean z | +0.054 [−0.035, +0.144] | +0.057 [−0.038, +0.152] | within ±0.15 |
| z-RMS at Tmag 9 | [0.934, 1.176] | [0.926, 1.149] | within [0.80, 1.15] |
| z-RMS at Tmag 13.5 | [0.633, 0.905] | [0.840, 1.061] | within [0.80, 1.15] |
| Equal-host recovery of observable truths | 0.906 [0.833, 0.969] | same | reported |
| Window-removal control, median ratios | β 1.000, residual RMS 1.001 (IQR 0.989-1.016) | same | within [0.95, 1.05] |

Applying the confirmation criteria mechanically to these inspected hosts: `t015v3c` passes the z-RMS, both Tmag-endpoint and both window-removal criteria, but narrowly misses two. The lower coverage bound is 0.924 against 0.93, and the upper mean-z bound is +0.152 against 0.15. The sample (45 hosts, 43 for SPOC 120 s alone) is below the 60-host adequacy criterion. `t015v3` passes coverage and bias but fails z-RMS (lower bound 0.884) and both Tmag endpoints, because its faint-star intervals are conservative (C022). The development sample is not a test of the rule. These verdicts show where the margins bind.

- *Faint-star conservatism is real in these light curves and does not come from the estimator.* Raw-error z-RMS in the faintest stratum is 0.84 although χ²_ν ≈ 0.88. In synthetic white noise, the same code is calibrated at σ = 43, 118 and 241 s (raw-error z-RMS 1.00, 1.00 and 1.03; 1,000-1,338 transits each), with no late bias (median z −0.04 ± 0.03). The mechanism in real faint-star PDCSAP data is not identified (C022).
- *Window removal has no detectable effect.* Removal and subtraction give the same per-host z-RMS to two decimals (paired 1,355 timed windows: 0.938 and 0.937; coverage 0.965 and 0.964) (C022).
- *Positive bias persists at a small size, and one stratum is clearly biased.* The equal-host mean z is +0.05, as against D039's borderline median z of +0.08 to +0.10. Under `t015v3c`, stratum B (Tmag 10-11, 12 hosts, 190 events) has mean z +0.215 [+0.049, +0.391], an interval above zero. Stratum A (Tmag below 10, 10 hosts, 159 events) has 95% coverage 0.916 [0.844, 0.975], and stratum D (Tmag 12-13.5, 11 hosts, 188 events) has 0.974 [0.957, 0.989] (C022). The earlier per-stratum failure stands (C017, D039). The prespecified per-stratum bias margin of 0.1σ was retired as unattainable at affordable size (D041, sizing in `scripts/t015_confirmation_sizing.py`); the narrower statement is that it is poorly powered with 30 hosts per stratum (C020).
- *The old pooled pass is conditional.* The earlier validation reported coverage 0.958 [0.934, 0.981] and z-RMS 0.981 [0.920, 1.045] on 18 hosts (C017). Those event-weighted successful-event estimates reproduce, but readiness does not follow: 13 of 48 planned primary runs did not succeed (27.1%), truth events for those runs were never written, equal-host weighting moves the median bias beyond the old 0.1σ criterion (+0.103 against +0.082), and the proposed log host-MSE endpoint failed a Gaussian control (C020).

**Shape misspecification is a stress test, not a criterion.** With the injected impact parameter raised by 0.2, limb darkening changed (q1 +0.2, q2 −0.15) and Gaussian spot bumps on half the transits, z-RMS rises to 1.503 and 95% coverage falls to 0.848 (same transits: 0.939 and 0.964 for removal). Spot crossings bias timings by construction. The result bounds how far real systematic shape error could move the calibration (C022).

![Host timing z-RMS against TESS magnitude for injected transits in the 45 inspected hosts, with the equal-host linear model of mean z² for each rule and the endpoint criterion band [0.80, 1.15]. The t015v3c multiplier was fitted to these points. Development data (C022).](../results/sprint2/figures/fig_timing_calibration.png)

## 3.5 Identification boundary tests

We injected, with real transits subtracted and epochs uniform over phase, trains with true period P_cat(1 + δ), aliases at 0.5, 2 and 3 × P_cat, and trains in which every third transit is displaced from the linear ephemeris (44 trials per scenario, `results/sprint2/dev/identification_summary.json`; C024):

- *Period offsets.* For |δ| ≤ 0.4%, all 44 trials identify. At δ = 0 the timed z-RMS is 1.033 and 342 of 343 observable events are timed. At δ = ±0.4%, 294 of 330 and 297 of 338 observable events are timed, with 23-25 edge exclusions and 12-16 not recovered. At δ = ±0.6%, outside the window, only 18 of 44 trials identify and all 26 failures are recorded as `id_period_at_search_boundary`. Outside the window the outcome is a recorded failure, not a silent mistiming. Recovery near the boundary is lower, and an unusually large |z| occurs at some offsets (largest 4.28 at δ = 0, 5.33 at −0.2% and 7.45 at +0.4%).
- *Aliases.* Injection at 0.5 × P_cat identifies in 37 of 44 trials (the failures are shape-consistency rejections, in which the fitted T14 collapses against the BLS duration, and one low-SNR case) and times 327 of 629 observable events, as expected when every other injected transit lies between catalogue epochs. At 2 × and 3 × P_cat, 42 of 44 trials identify and the timed z-RMS is 0.32 and 0.28. These timings are not mistimed but their σ is conservative; we have not examined why. One spurious timed window appears at 2 ×.
- *Displaced transits.* Displacements of 30 min are all timed (93 of 93, z-RMS 0.89). At 50 min, 85 of 93 are timed. At 70 min, 13 of 96 are timed (71 flagged at the edge). At 90 and 120 min, one and none are timed. Per-transit TTVs above about an hour are therefore a declared selection of the rule, and forecast tails are not affected because forecast error enters only through the blind epoch search.

## 3.6 Confirmation and replication of the outcome rule: not ready

Table 3 gives the prespecified tests. Production set: SPOC 120 s, or TESS-SPOC 200 s where SPOC is absent; PDCSAP; removal mode; equal-host estimates; 90% host-cluster percentile intervals (B = 10,000) (C025).

**Table 3. Confirmation and replication, injected transits.** Bold marks a failed criterion.

| Sample and rule | Hosts / events | z-RMS | 95% coverage | Mean z | z-RMS at Tmag 9 | at Tmag 13.5 | Verdict |
|---|---|---|---|---|---|---|---|
| Confirmation, `t015v3c` (primary) | 106 / 1,496 | 1.053 [1.015, 1.091] | 0.936 [**0.922**, 0.950] | 0.000 [−0.055, 0.056] | [0.934, 1.040] | [**1.062**, 1.195] | fail |
| Confirmation, `t015v3` (secondary) | 106 / 1,496 | 0.985 [0.951, 1.017] | 0.944 [0.930, 0.957] | +0.001 [−0.051, 0.053] | [0.966, 1.063] | [0.878, 1.000] | passes; cannot qualify |
| Replication, `t015v3` (primary) | 102 / 1,377 | 1.095 [1.002, **1.214**] | 0.929 [**0.908**, 0.947] | +0.048 [−0.045, 0.131] | [1.002, **1.221**] | [0.846, **1.319**] | fail |

**Outcome.** The pipeline is not ready under the criteria fixed before each test. Both verdicts stand, and no margin was relaxed.

- *The multiplier over-corrected.* The faint-star conservatism seen in the development hosts did not recur. `t015v3c` made faint stars anti-conservative (stratum D z-RMS 1.138 in the confirmation).
- *`t015v3` passes only on the first sample, and only as the production set.* Assessed by product type, as the design requires, SPOC 120 s alone misses the coverage criterion in the confirmation (lower bound 0.9291 against 0.93), while TESS-SPOC 200 s passes every criterion (C025). That pass does not qualify the rule, since it was selected after the primary failed.
- *The replication failure comes from hosts with few transits.* The largest contributors have one or two timed injections each, for example K2-403 (one transit, z = 3.9) and HD 23472. Under equal-host weighting each carries a full host weight. Dropping the three largest host contributions gives z-RMS 1.006. That is a diagnostic, not a result (sprint-2 report; not recomputed here).
- *Recovery.* Equal-host recovery of observable truths is 0.896 [0.845, 0.940] in the confirmation (strata A to D: 0.79, 0.86, 1.00, 0.93) and 0.859 [0.804, 0.909] in the replication (0.92, 0.79, 0.81, 0.93). Product, run and window failures remain in the denominators; 14 confirmation runs and 40 replication runs were dropped for window overlap (C025).
- *Controls pass.* The noise-ratio control is 1.000 (β) and 1.004 or 1.000 (residual RMS) in the confirmation and replication. Window removal and subtraction give the same calibration (paired z-RMS 0.971 and 0.973 in the confirmation, 1.009 and 1.011 in the replication). There are no duplicate truth assignments. The confirmation had 28 spurious windows and the replication 16 (C025).
- *Bright stars.* Coverage in stratum A is 0.915 to 0.918 for `t015v3` in both samples, with low recovery in the confirmation (0.79) (open item S2-03).

**Exploratory split, defined after the replication.** Hosts are divided by their number of timed injections (`results/sprint2/exploratory_transit_count.json`). This is not a test: the grouping is outcome-dependent and was chosen after seeing the replication.

| Sample | ≥ 4 timed: hosts, z-RMS [90%], 95% coverage (lower bound) | ≤ 3 timed: hosts, z-RMS |
|---|---|---|
| Development | 42, 0.939 [0.882, 0.995], 0.963 (0.945) | 3, 1.02 |
| Confirmation | 99, 0.992 [0.959, 1.025], 0.944 (0.931) | 7, 0.88 |
| Replication | 98, 1.012 [0.976, 1.049], 0.953 (0.941) | 4, 2.34 |

Hosts with at least four timed transits meet the z-RMS and coverage criteria in both confirmations. The replication failure sits in four hosts with one to three transits (z-RMS 2.34, coverage 0.54), mostly long-period planets (C025). Turning this into a rule needs a metadata definition available before measurement (for example, predicted transits per sector), a fresh sample and its own prespecified criteria (open item S2-02). Equal-host weighting also gives single-transit hosts a full host's weight, and whether the estimand should weight hosts by their expected final-evaluation transit counts is a design question for review (S2-04).

The extension to multi-planet hosts is not covered by either sample. It rests on the identification tests and the same-photon agreement.

![Host timing z-RMS against TESS magnitude for injected transits, for the development hosts and the first confirmation, with the equal-host linear model of mean z² for each rule and the endpoint criterion band [0.80, 1.15]. Development panel: the t015v3c multiplier was fitted to those points. Confirmation panel: the same multiplier applied to new hosts (C022, C025).](../results/sprint2/figures/fig_timing_calibration.png)

## 3.7 Transfer of the calibration to our outcome convention

We remeasured the development cohort with the frozen rule and refitted M1-M3 under each convention (Section 2.5; C026). Table 4 gives the M2 minus M0 contrast (planet-balanced standardised IS95, 95% host-refit interval, 400 resamples).

**Table 4. Convention comparison, development data.** Negative favours M2. Every cell is inconclusive.

| Design (training / scored planets) | ExoClock × 1.087 | `t015v3c` | `t015v3` |
|---|---|---|---|
| Release transfer, matched transits (7 / 216) | −1.249 [−3.897, 2.657] | −2.195 [−5.063, 1.722] | −2.031 [−4.844, 1.738] |
| Chronological, matched transits (123 / 185) | −1.080 [−3.623, 1.324] | −1.465 [−4.753, 1.528] | −1.376 [−4.647, 1.534] |
| Release transfer, all timed (70 / 217) | −2.445 [−5.756, 0.187] (sprint 1, 15 / 238) | −2.154 [−5.148, 0.122] | −1.972 [−4.997, 0.278] |
| Chronological, all timed (124 / 186) | −2.628 [−6.351, 0.067] (sprint 1, 133 / 206) | −0.026 [−5.100, 15.04] | −0.082 [−5.108, 14.84] |

- *R5 transfer is accepted in both designs.* The sign and decision of the matched contrasts agree across the three conventions. The ExoClock "all" row reproduces sprint 1 exactly.
- *Coverage.* M2 again raises 95% coverage, for example from 0.883 to 0.962 in the matched release transfer under `t015v3c`. Fewer than a quarter of planets improve individually in the matched designs (0.185 to 0.243).
- *Same photons.* Our mid-times differ from ExoClock's for the same transits by a median of −0.18 s (chronological) and −0.33 s (release transfer), with z-RMS 0.365 and 0.366 (3,416 and 2,230 matched pairs). The conventions differ in scale, not in centre. The sprint-2 report additionally quotes 3,748 matched transits and a raw `t015v3` σ median 1.055 times ExoClock's; those figures are not in the comparison file and are not used here.
- *One spurious timing drives the chronological all-timed row.* In WASP-54b sector 50, a product-level ephemeris misalignment put the windows about 12 hours from the real transits. Two windows were edge-flagged and one was falsely timed: z = 55 against the forecast, σ = 797 s. It is the only such case among 3,946 timings. The chronological all-timed fit shifts accordingly: M2's s rises from 2.33 to 3.24 and its contrast moves from −1.37 [−4.55, 1.07] to −0.08. The single-scale M1 fit has b near 190 in that row. The primary results keep the event, and the without-event fit is a diagnostic (`results/sprint2/forecasts/diagnostic_wasp54_s50.json`). A rule requiring most covered windows in a product to time successfully would catch it (open defect S2-01). The episode shows how fragile the mixture calibration is to one identification defect (C026).

**Candidate parameters.** The candidate calibration is a release-transfer fit of DRC forecasts against all `t015v3` development outcomes after DRC issue (2022-09-28 to 2024-01-03): 217 planets, 216 hosts, 2,328 events, with 400 host-refit parameter sets. M1: b = 10.02. M2: s = 2.585. M3: b = 0.996, s = 2.591 (`results/sprint2/forecasts/candidate_parameters_t015v3.json`; C027). They are development fits for the draft forecasts and not adopted parameters, and the t015v3c version is kept for comparison only. They differ from the sprint-1 fits (b = 2.69, s = 2.16 trained on 15 DRB planets) because the training set is larger and uses a different outcome convention.

**Interface.** Replaying `make_forecasts` then `score` reproduces sprint 1's `scores.csv` byte for byte; all 70 sprint-1 tests pass, and 75 with the sprint-2 tests. Production I1 scoring by the adapter: {{S2-INTERFACE: counts from data/derived/sprint2/interface/scores.receipt.json}}.

![Standardised IS95 contrasts, method minus M0, for the release-transfer and chronological designs under four outcome conventions, with 95% host-refit intervals. Negative favours the method. Intervals that run off the scale (chronological M1 and the all-timed rows) are drawn as arrows. Development data (C026).](../results/sprint2/figures/fig_convention_contrasts.png)

# 4. Discussion

**What the evidence supports.** Issued DRC uncertainties are too narrow in the tails for later TESS timings. Their nominal 95% intervals cover about 88-90% of outcomes. A tails-only calibration restores nominal coverage and improves log score at the cost of wider intervals. These are development findings, with outcomes inspected during design.

**What it does not support.** The prespecified primary contrast is inconclusive in all four development designs. The mean improvement comes from tail risk in a few planets: most planets score worse under M2, and two hosts supply about 69% to 86% of the mean gain. We therefore report no forecast improvement and no typical-planet benefit. A user who wanted the narrower interval for a well-behaved planet would be worse off under M2. A user who wanted protection against the rare planet that is hours off would be better off. Whether that trade is worthwhile depends on the cost of a missed window, which this work does not model.

**Release transfer is the crux.** DRB's overconfidence (b = 2.249) is not DRC's (b = 0.976), so a correction learned on one does not carry to the next unchanged. M1's chronological scale of 7.3 and M3's collapse to M1 in release transfer show how fragile a scale parameter is. That transfer relies on a proxy, since the DRC timing file followed its forecast by 53 seconds. The delayed-origin reconstruction has historically available inputs but was constructed after the outcomes were inspected, and it was never issued. We therefore cannot call any development contrast a deployable improvement.

**The outcome measurement is the binding constraint, and it is not ready.** Outcome error dominates forecast error for most development events (σ_y·a/σ_f median 2.6), so a miscalibrated outcome σ distorts coverage as much as a miscalibrated forecast does. The pipeline is accurate for most planets: hosts with at least four timed transits are calibrated in both confirmations. It failed its prespecified tests, however. The Tmag multiplier fitted on 45 development hosts over-corrected on new hosts, and the uncorrected rule failed a single replication that was fixed in advance. The failure sits in hosts with one to three transits. We state that scope as exploratory, because we defined it after seeing the replication, and we do not call the rule qualified for it. The final evaluation therefore waits for a prespecified test of a narrower, metadata-defined scope, or for a repaired rule on new evidence. Calibration transfer between catalogue and our outcome conventions is accepted in development (every matched contrast has the same sign and decision), so the open question concerns the outcome rule and not the transfer.

**Prior art and novelty.** ExoClock IV's Table 5 is the direct benchmark, and we reproduce it. We do not claim the first retrospective validation of ephemerides. The bounded combination in Section 1 is novel only if the final evaluation succeeds, and the literature screen cannot show absence of earlier work (C019).

## 4.1 Limitations

1. *No final evaluation exists.* All results are inspected development material and several designs were chosen after seeing them. They are not untouched tests (D014).
2. *Covariance is reconstructed.* ExoClock does not publish Cov(T0, P). C2 is an approximation tested with zero and ±1 correlations, and it is not recovery of the issued covariance (C004, C018).
3. *Availability and epoch mapping are partly proxy.* The release-transfer and chronological designs are event-date and observation-date proxies, and per-row first-public dates are unknown (C019). In the remeasured development designs, the forecast epoch of a timed transit is the epoch nearest its measured time. That convention cannot represent a forecast error above half a period. The final evaluation instead fixes each event's epoch from the issued ephemeris before any photometry is read (`results/sprint2/freeze_candidate/events_drd.csv`).
4. *Selection.* Successful catalogue timings condition on success, and our own outcomes condition on identification. Missed-transit frequency is not estimable from either. Identification excludes planets whose period error exceeds 0.5% and per-transit TTVs above about an hour (Section 3.5). A transit timing catalogue cannot identify how many attempts missed transits altogether (D010).
5. *Dependence.* Transits of one planet share an ephemeris error and a fitted shape. Host-cluster resampling addresses this. The measured intraclass correlation of z is about zero (D039), but that is a check and not an assumption, and a 15-host training sample cannot support a validated confidence procedure.
6. *The multiplier was fitted in-sample and failed.* The `t015v3c` coefficients use all 45 development hosts, a split-half check was unstable, and the rule failed confirmation (C025). The uncorrected rule failed its replication.
7. *The bootstrap is slightly anti-conservative.* Nominal 90% intervals cover 0.853-0.927 in negative controls (C023).
8. *Shared outcome lineage is incompletely known.* Exposure lineage across ExoClock rows, TESS timings and our remeasurement is incomplete, so independence of calibration inputs from scored observations is assumed in places (S1-05, open).
9. *Score semantics.* The standardised IS95 is a conditional weighted loss, because outcome error is estimated after issue (D042).
10. *Metadata is not recovery.* The 3,399 predicted opportunities and 184 planets are metadata counts. Capture and recovery are unknown until photometry is opened (C021).
11. *Population.* Results describe the ExoClock cohort of planets with usable TESS timings, not all transiting planets, future Ariel targets or attempted ground-based observations.

12. *Few-transit hosts.* Equal-host weighting gives a host with one transit the weight of a host with many, and the replication failure sits in such hosts (S2-02, S2-04).
13. *Bright stars.* Tmag below 10 shows coverage of 0.915 to 0.918 in both confirmations and low recovery in the first (S2-03).

**Open defects at this draft** (`results/sprint1/handoff.json` and `docs/sprint2_report.md`): the sprint-1 defects on the attempt ledger, host-balanced estimand and controls (S1-01, S1-02, S1-04) are addressed by the sprint-2 outcome rule and need review. Open: a product-level consistency rule against spurious windows (S2-01); a prespecified test of the at-least-four-transit scope (S2-02); bright-star undercoverage (S2-03); the estimand's weighting of few-transit hosts (S2-04); and the 21 of 404 non-Gaussian grids truncated by the ±60-min prior, which the adapter refuses and which are recorded as failed attempts, as stated in the sprint-2 hand-off (S2-05, not yet in a committed receipt). Reciprocal Codex and Claude review has not occurred (S1-05).

# 5. Planned final evaluation

The final evaluation has not been run and its outcomes have not been opened. It will not run until the outcome rule is qualified, the open defects are resolved and the reciprocal reviews have finished. The candidate protocol is in `configs/candidate_freeze.json` and `results/sprint2/freeze_candidate/` (C027). It is a candidate, not a freeze, and is described here as it stands:

- *Question and forecasts.* How well do issued DRD ephemerides predict later independent TESS mid-times, and does a population calibration learned from the previous release improve the predictive distribution? M0 is the issued DRD linear ephemeris, Gaussian with C2 reconstructed T0-P correlation. M1-M3 apply the candidate calibration of Section 3.7 (M1 b = 10.02; M2 s = 2.585; M3 b = 0.996, s = 2.591). It is fitted on DRC forecasts against `t015v3` outcomes after DRC issue (2022-09-28 to 2024-01-03), with no regularisation prior. The configuration file still names `t015v3c` as the outcome rule and must be updated to follow the confirmation outcome.
- *Roster and events.* The metadata roster has 184 planets on 175 hosts (156 core, 28 extension) and a manifest of 3,399 event-level opportunities with strict-A start 2025-11-19, with the DRD event epoch computed from the issued ephemeris and not from the data (C027, C021).
- *Outcomes.* Outcome rule to be decided: neither `t015v3c` nor `t015v3` is qualified. A narrower scope (hosts with at least four predicted or timed transits per sector) needs a metadata definition and a fresh prespecified test (S2-02). The products are SPOC 120-s PDCSAP where present, otherwise TESS-SPOC 200-s PDCSAP. Every attempted event is retained with a status. Scoring is conditional on timed events, and recovery is reported separately and never imputed.
- *Primary contrast.* Planet-balanced standardised IS95, M2 minus M0, with a 95% host-cluster percentile interval (B = 10,000) at fixed parameters. Parameter uncertainty is reported by rescoring with the 400 development host-refit parameter sets and is not part of the decision. The decision is improves, worsens or inconclusive as in Section 2.3.
- *Secondary summaries and strata.* Raw minute IS95, score divided by forecast-only SD, negative log score, 68% and 95% coverage and width; strata by operational lead time, Tmag, covariance tier, core versus extension and product type.
- *Sensitivities.* Covariance settings, `t015v3` without the multiplier, the journal availability anchor, core only, C2 only, and outcome σ × 1/1.1 and × 1.1.
- *Precision.* Four-thousand-replicate simulations under fixed rules give a mean contrast of −2.953 (study SD 1.572) for the union cohort when M2 is true, weakened to −2.390 (SD 1.506) with informative failure and a simulation interval that crosses zero. The extension increases conditional SE by 6-34% across the declared cells, so it is a population choice and not a precision gain (C021). These simulations condition on fitted rules and assumed measurement errors and do not predict real performance.
- *Amendments.* Any change after the freeze is dated and justified in `coordination/decisions.md`. The frozen analysis is reported first and in full.
- *Gates before the freeze.* A qualified outcome rule, resolution of S2-01 to S2-05, reciprocal review by Codex and Claude, reconciliation, a hashed record of forecasts, parameters, cohort and code together, and an access receipt showing that protected outcomes remain unopened.

# 6. Data, code and reproducibility

**Repository.** `github.com/BWBrook/transit-forecast-audit`, public. Code is MIT-licensed. Text, figures and derived data written for this project are CC BY-SA 4.0. The repository holds the claims ledger (`coordination/claims.md`), decision log (`coordination/decisions.md`), results and a machine-readable handoff (`results/sprint1/handoff.json`). The agent guide (`docs/agent_guide.md`) gives every decisive command, the access guards and the evidence location of every claim. The brief (`docs/brief.md`) states the findings for a broad audience.

**Source data.** The ExoClock DRB, DRC and DRD ephemeris and timing releases (OSF, CC BY 4.0; DOIs 10.17605/OSF.IO/WNA5E, 10.17605/OSF.IO/P298N and 10.17605/OSF.IO/WPJTN) and TESS photometry from MAST, which follows MAST's terms and the mission acknowledgement. Raw files are not committed. `scripts/acquire_osf.py` re-fetches the release bytes and verifies their hashes, and the raw TESS products carry SHA-256 hashes in the product tables. Preserve observer credit and the acknowledgement each database requests. [CITATION NEEDED: TESS mission, SPOC pipeline and TESS-SPOC high-level science product citations required by MAST]

**Environments.** A locked Python environment (`.venv`, `uv.lock`) runs analysis, tests and scoring. Photometry scripts are PEP 723 files run with `uv run`. Sprint-2 evidence commit: the sprint-2 commit recorded in `docs/sprint2_report.md`'s git history. Sprint-1 evidence is at commit 6d69f0e.

**Access guards.** Development-era photometry only: MAST `t_max` before request and FITS TSTOP before flux read, limit BTJD 3313.49. No product after 2025-11-18 has been requested.

**Tests.** The full suite passes (70 tests at sprint 1, 75 with the sprint-2 tests). The known one-count DRD benchmark discrepancy is reported, not hidden.

**Correspondence record.** The human-AI correspondence record is published as reviewed snapshots in `docs/correspondence/`, with addresses, home paths and listed hostnames redacted and flagged messages withheld.

# 7. Contributions

**Human lead.** Barry W. Brook (University of Tasmania) set the question, the open-by-default and repository-as-paper model, the instruction that TESS outcomes after 2025-11-18 stay unopened until protocol freeze, the sequence of work between the two AI systems, and the scientific decisions recorded in the log. He reviews at least the final version of any paper or research artefact before release. This repository draft has not yet been reviewed by him.

**AI systems and their roles.** The analysis, code and drafts are by AI systems, working through the repository and the project's correspondence board. The record below follows the coordination files (`coordination/decisions.md`, `docs/correspondence/`).

- *Claude (Anthropic, Claude Opus 5.5)* ran the pilot (acquired the release files and reproduced ExoClock IV Table 5, Track R); wrote the revision of the two-sprint plan (R1-R9, I1-I3); built and validated the forecast-independent timing pipeline and the injection validation; wrote the sprint-2 outcome rule `t015v3`/`t015v3c`, its attempt ledger, identification and shape controls, estimand criteria and negative controls, the confirmation design, the remeasurement and convention-comparison code, the candidate freeze package and the figures; ran the sprint-2 analyses; and directed the drafts.
- *Claude (Anthropic, Claude Sonnet 5.5)* wrote the first drafts of this article, the brief and the agent guide as a delegated subagent under Claude Opus 5.5, from the claims ledger and result files, without running analyses or opening raw data.
- *Codex (OpenAI; the board records the models gpt-6 and gpt-5.6-luna)* independently reproduced Table 5 in base R, audited covariance and measurement-error claims, completed the stable mixture and variance-components fits, built the sprint-1 forecast experiment and scoring interface (M0-M3, host-refit uncertainty), reconstructed release availability from OSF logs, screened the forward citations, audited the timing validation, built the metadata inventory and precision simulations, and reviewed the scoring. The coordination record does not assign individual tasks to each of the two Codex models.
- *GPT-6 Pro (OpenAI)* supplied the initial topic ideation conversation, tracked unchanged as `docs/gpt-6-pro_ideation.md` and recorded as historical ideation, not findings (D025).

Each AI system contributed ideas and criticism as an equal participant. Barry weighed them on their merits. Agreement between the two systems is not treated as independent validation: each key result carries an independent implementation, numerical check or primary-source check where one exists, and disagreements stay visible in the record. Reciprocal Codex and Claude review of sprint 2 is pending.

**Data providers.** ExoClock contributors, MAST and the TESS mission, whose data this work builds on.

# References

::: {#refs}
:::
