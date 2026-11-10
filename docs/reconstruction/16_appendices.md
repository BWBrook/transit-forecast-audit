# Appendices

<!--
Reconstruction step 3c: appendices A-H for 14_full_draft.md, drafted by Claude
Sonnet 5.5 (delegated by Claude Opus 5.5, which reviewed and edited it) from manuscript/paper.md (v0.6.1), the corrections in 12 and 15,
and coordination/claims.md. Claim IDs and decision IDs are in trailing
comments; the journal build strips them. Table 3 of the main text is the
comparison table, so appendix tables are numbered by appendix. Citation keys
marked with a dagger are verified candidates not yet in the bibliography.
-->

## Appendix A. Release dating and the DRC timing-table chronology

### A.1 Public availability of the three releases

We dated each release from OSF API logs for the project node and for each exact file. We assume that a file present in an already-public node, or added to one, is retrievable at the later of the two timestamps. DRD's files were uploaded on 17 November 2025 while the node was private, so its anchor is the public transition on 18 November. These logs show when a file was public, not whether it was discoverable or shared privately earlier. Evaluation opens on the first whole UTC day after the DRD anchor, 19 November 2025. The February 2026 journal date is a sensitivity anchor (Appendix C). Because those calendars are in UTC and event times in BJD_TDB, we conservatively excluded four core and one extension opportunity that were numerically near a boundary, without converting those boundaries.

**Table A1.** Release dates and the lag of each timing table behind its forecast file.

| Release | Public by (UTC) | Timing table added after forecast file |
|---|---|---:|
| DRB | 2021-10-27 12:03:15 | 44,926 s (12.5 h) |
| DRC | 2022-09-27 15:25:16 | 53 s |
| DRD | 2025-11-18 09:43:24 | 0 s |

<!-- claims: C019, C054; D014, C011 -->

### A.2 What the DRC timing table can and cannot date

The DRC table contains event mid-times but no per-row first-availability timestamps. Its addition followed the forecast by 53 seconds on the same day; that timestamp does not establish deployability at the exact forecast origin. The development designs of Appendix E are labelled accordingly. No training event of the chronological split appears in the DRC timing table, and the release-transfer training events fall between 28 October and 30 December 2021. The inputs of every DRD source type stop before 4 January 2024 (nominal TDB).

<!-- claims: C019, C032, C054, C055 -->

## Appendix B. Scoring: loss scales, influence, the score bound and the four models

### B.1 The contrast on three loss scales

The primary statistic divides each event's interval score by M0's predictive SD, measurement error included. Table B1 repeats the contrast with the forecast-only SD and with raw minutes. The intervals hold the fitted parameters fixed (10,000 host resamples) and are conditional; only the primary row's joint-refit interval, −1.84 to +2.20, decides H3. Omitting HR 858 b, an influence diagnostic chosen after the outcomes were known, moves all three contrasts towards M0 and defines no decision.

**Table B1.** M2 − M0 on three loss scales, primary set of 151 planets.

| Divisor | M2 − M0 | Conditional 95% interval | Without HR 858 b |
|---|---:|---|---:|
| M0 predictive SD (primary) | −0.121 | [−1.98, 1.12] | +0.602 |
| Forecast-only SD | +0.082 | [−2.07, 1.67] | +0.834 |
| Raw minutes | −8.46 | [−34.2, 5.68] | +3.65 |

<!-- claims: C043, C046, C052 -->

### B.2 Per-planet contrast and influence

Under M2, 111 of 151 planets score worse; the median planet difference is +1.05 standardised units and no planet loses more than 6. The 40 planets that score better include four whose issued forecasts missed badly: HR 858 b (−109), TOI-905 b (−48), WASP-184 b (−14) and TOI-559 b (−12). HR 858 b alone contributes −0.720 to the mean of −0.121. The declared influence curve fixes the frozen parameters and removes hosts in order of their contribution to the mean gain. Removing HR 858 moves the mean to +0.602 and removing the five largest-gain hosts to +1.165; no host was removed from the primary analysis.

We matched all 184 frozen targets to the default parameter rows of the NASA Exoplanet Archive, retrieved without reference to scores. Eight carry a TTV flag; three of those are in the accepted set (HR 858 b, WASP-18 b and WASP-43 b) and average −36.7, almost wholly HR 858 b, against +0.619 for the other 148. An unflagged row does not show that a planet lacks timing variations, and the archive does not date when variations became known, so the label is a current diagnostic and never defines the cohort.

<!-- claims: C046; D067 -->

### B.3 Bound on interval-score differences

Let M2's central 95% interval contain M0's, with the lower limit moved outward by $d_L \ge 0$ and the upper by $d_U \ge 0$, and let $\Delta w = d_L + d_U$. At $\alpha = 0.05$ the difference in interval score for one outcome $x$ is $\Delta w$ plus the change in the two penalty terms, each weighted by $2/\alpha = 40$. Each penalty can fall by at most $d_L$ or $d_U$ respectively, and $x$ cannot lie beyond both limits at once, so
$$\Delta w - 40\max(d_L, d_U) \;\le\; \mathrm{IS}_2 - \mathrm{IS}_0 \;\le\; \Delta w.$$
For symmetric widening the bounds are $-19\Delta w$ and $+\Delta w$. The difference is constant once $x$ lies beyond both intervals, so a far miss earns the maximum gain whatever its size, and the loss from widening never exceeds the added width. A common positive divisor rescales both sides. The bounds hold event by event for fixed endpoints. In the saved scores no event's penalty exceeds the added standardised width, which is consistent with the bound but does not show that the intervals are nested. Synthetic cases reproduce the bounds exactly.

<!-- claims: C049; D068 -->

### B.4 Conditional propriety and the likelihood approximation

We score the measured mid-time, and both the divisor and the likelihood come from the measurement. The score therefore keeps its propriety only conditionally: the measurement descriptors must be ancillary, the observation model correct and acceptance ignorable. Appendix D supports the observation model for accepted timings on two tuned samples; nothing here establishes the other two conditions. A small synthetic control shows that the convention matters: in a complete-white Gaussian case, the M2 − M0 score contrast in minutes was +6.06 against the latent time, −50.33 against the measured time with no measurement convolution, and −0.72 with the reported likelihood convolved (12 runs, 48 truths; no inference).

Each timing likelihood is computed on a flat-prior grid over ±60 minutes about the fitted epoch, holding the fitted transit shape and noise level fixed instead of marginalising over them. We turn this likelihood into a distribution of measurement error by a location-family approximation: the grid is stored as true minus reported mid-time, and its shape, reflected, is used as the distribution of the reported mid-time about the true one. Where a Gaussian reproduces the 2.5% and 97.5% posterior quantiles within 10%, scoring uses the Gaussian; this applies to all but 399 accepted timings, which are scored from the grid. The forecast is convolved with the measurement error exactly for M0 and M1, and for the mixtures by quadrature with 384 nodes, checked against 192. The calibration fits use the Gaussian approximation throughout.

<!-- claims: C030, C039, C043, C052, C056; scripts/acceptance.py, scripts/final_evaluation.py -->

### B.5 The four models

M1 scales M0's SD by one factor $b$. M2 multiplies M0's variance by $\lambda = \exp(sZ)$ with $Z$ standard normal, so $b = 1$, the median multiplier is one and $s$ is a log-variance SD; its conditional forecast SD is $\sigma_f\sqrt{\lambda}$. M3 fits $b$ and $s$ together. All three were fitted once by bounded maximum likelihood without a regularisation prior, on DRC's errors for the 206 core-eligible planets against 2,186 development timings made by the final acceptance rule between 28 September 2022 and 3 January 2024. Across the 2,000 stored joint refits, the 95% range of $s$ was 1.24 to 2.72, a measure of parameter uncertainty.

**Table B2.** Frozen parameters and held-out scores, primary set. Planet-balanced; smaller scores are better; coverage is of accepted measured timings.

| Model | Fitted parameters | Standardised IS95 | IS95 (min) | 68% coverage | 95% coverage | Mean 95% width (min) |
|---|---|---:|---:|---:|---:|---:|
| M0, issued | none | 11.33 | 106.3 | 0.619 | 0.908 | 10.5 |
| M1, single scale | $b$ = 9.35 | 19.90 | 78.7 | 0.985 | 0.993 | 56.4 |
| M2, tails only | $s$ = 2.047 | 11.21 | 97.8 | 0.679 | 0.976 | 17.5 |
| M3, both | $b$ = 1.080, $s$ = 1.968 | 11.26 | 97.6 | 0.692 | 0.977 | 17.8 |

M1 has the worst standardised score and the best raw-minute score, so its rank depends on the loss scale. M2 improved on M0 for 26.5% of planets. The scorer reproduces the independent scoring adapter to 2.2e-12 and the refit reproduces the frozen parameters.

<!-- claims: C043, C052, C063 -->

### B.6 Post-review PIT and error quantiles

The predictive probability integral transform (PIT) evaluates each measured
time in its modelled predictive CDF. Write the signed residual as
$r = t_{\rm reported} - t_{\rm forecast}$ and the saved grid coordinate as
$x = t_{\rm true} - t_{\rm reported}$. Measurement error is therefore $-x$,
so a grid row contributes $\Phi((r+x)/(b\sigma_f\exp(sZ/2)))$, averaged over
grid weights and standard-normal $Z$, with $\sigma_f$ the M0 forecast SD.
For Gaussian timing errors their variance
adds to the forecast variance instead. The calculation uses the frozen
384-node convention; an independent adaptive integration reproduces it to
$1.4\times10^{-12}$. This numerical agreement does not validate the observation
or acceptance assumptions needed for a uniform PIT reference.

Planets receive equal total weight and events within each planet equal weight.
Error quantiles use the smallest observed error whose cumulative weight
reaches the requested probability, without interpolation. Pooled quantiles
instead give every event equal weight. The PIT asymmetry and percentile
calculations were added after the outcomes were inspected.

<!-- claims: C065; results/reconstruction_review/pit_independent_check.json -->

## Appendix C. Declared sensitivities

### C.1 Sensitivities refitted and rescored

The configuration named these sensitivities before the held-out data were opened; their executable conventions were fixed in a dated document before any variant was computed. Each was refitted on development data where it changes the calibration and rescored on the held-out set. Table C1 gives the M2 − M0 contrast with a conditional interval from fixed-parameter host resampling (10,000 draws), which is not a decision interval. The journal-date anchor, which starts evaluation at the February 2026 publication, removes 475 accepted timings and 29 planets. The common M0 divisor is recomputed within each row, so standardised magnitudes are not comparable between rows.

**Table C1.** M2 − M0 under declared sensitivities.

| Setting | Accepted events / planets | Standardised | Conditional 95% interval | Raw (min) |
|---|---:|---:|---|---:|
| Frozen baseline | 2,185 / 151 | −0.121 | [−1.98, 1.12] | −8.46 |
| Correlation 0 | 2,185 / 151 | −0.121 | [−1.98, 1.13] | −8.47 |
| Correlation −1 | 2,185 / 151 | −0.723 | [−5.93, 2.48] | −22.80 |
| Correlation +1 | 2,185 / 151 | +0.346 | [−1.06, 1.28] | −5.98 |
| Training on all-SPOC timings (216 planets) | 2,185 / 151 | +0.640 | [−2.14, 2.40] | −11.41 |
| Journal availability anchor | 1,710 / 122 | −0.477 | [−2.79, 1.07] | −11.25 |
| Outcome σ × 1/1.1 | 2,185 / 151 | −0.408 | [−2.32, 0.92] | −8.96 |
| Outcome σ × 1.1 | 2,185 / 151 | +0.085 | [−1.71, 1.25] | −7.99 |
| Majority-of-windows product gate | 2,147 / 151 | −0.104 | [−1.98, 1.15] | −8.51 |
| Brightness multiplier on outcome σ | 2,185 / 151 | −0.422 | [−2.30, 0.88] | −9.06 |
| C2 correlation tier only | 2,185 / 151 | −0.121 | [−1.98, 1.12] | −8.46 |

The C2 row equals the baseline because every accepted event carries that tier. The standardised point contrast ranges from −0.72 to +0.64 and changes sign, and every interval spans zero. In raw minutes M2 has the lower mean in every setting, because raw scores weight hours-scale misses more heavily.

<!-- claims: C047; D067 -->

### C.2 Rescoring three sector-105 events of HR 858 b

In sector 105, the noisiest of HR 858 b's three sectors, four independent route-and-flux timings depart from three frozen timings (events DRD645, DRD647 and DRD649) by 7 to 11, −8 to −16 and −4 to −22 minutes, in a consistent direction within each event. We re-centred those three likelihoods on the median of the independent timings and doubled their widths, leaving the other 2,182 outcomes unchanged. This is a post-review perturbation with the fitted parameters held fixed. It gives −0.089 (conditional interval −1.88 to +1.12), +0.096 on the forecast-only scale and −8.23 minutes in raw units. It does not recompute the primary joint-refit interval, which stays at −1.84 to +2.20. A shift alone cancels the contrast in the far-tail regime; the change comes from the doubled width. All 16 HR 858 b timings remain outside the 95% interval of every model. Because the checkers share the photons, taking their median does not add precision.

<!-- claims: C057, C059; D073 -->

## Appendix D. Qualifying the measurement

### D.1 Injection design

To calibrate timing uncertainty without protected photometry, we injected transit trains into real development-era light curves, masked the original transit windows, and ran identification, shape fitting and timing unchanged. A control subtracted the original transits instead of masking them. Injected phases were 0.27 and 0.73 (each ±U(0.02)) with per-transit offsets of U(±2 min). The ledger wrote one row per intended injected transit before any fit. Recovered windows were assigned to injected transits one to one by a Hungarian assignment with a 60-minute gate, equal to the prior half-width, and every attempt received a terminal status. Recovery is therefore counted with all failures in the denominator, while calibration is assessed among timed injections.

Two samples were drawn from hosts with a single DRD-listed planet, Tmag below 13.5 and sector 56 to 73 pointing, thirty per Tmag stratum in a fixed SHA-256 order. The confirmation sample came from the 278 hosts of an earlier validation frame never reached, and the replication sample from the hosts that neither earlier sample had used (37, 36, 51 and 33 in the four strata). Each has 120 hosts. Sample sizes were fixed; failures stayed in the ledger. The replication was prespecified after the first rule failed confirmation and before its injection analysis, so it is an adaptive follow-up, and 82 of its hosts had already been remeasured in development with the same rule.

<!-- claims: C023, C025, C028, C038; D061, D062 -->

### D.2 Criteria and results

The criteria were fixed before any confirmation photometry was requested, with a 90% host-cluster percentile bootstrap of 10,000 draws. Each host has weight one. The margins come from a Gaussian coverage sensitivity: if outcome error is mis-scaled by 1.10, the nominal 95% interval covers 93.8% (outcome error equal to forecast error) or 92.5% (outcome error dominant), and 96.0% or 96.9% if mis-scaled by 1/1.10; a bias of 0.15 SD gives 94.9% or 94.7%. Individual perturbations permit about 2.5 percentage points of coverage distortion; the joint scale/bias example permits about 2.75 points, compared with the 5–7-point development shortfall. Outcome error does dominate, at a median 2.6 times the forecast SD in the release-transfer events. In simulation the estimators are unbiased to within 0.007, but nominal 90% intervals cover 0.853 to 0.927, so the criteria are slightly anti-conservative.

**Table D1.** The final acceptance rule on the two injection samples, estimates with 90% intervals.

| Criterion (threshold) | Confirmation | Replication |
|---|---|---|
| Hosts with a timed injection (at least 60) | 104 | 100 |
| Timed injections | 1,477 | 1,361 |
| z-RMS (interval within 0.909 to 1.10) | 0.988 [0.953, 1.021] | 1.016 [0.980, 1.052] |
| 95% coverage (lower bound at least 0.93) | 0.947 [0.934, 0.959] | 0.950 [0.938, 0.961] |
| Mean z (within ±0.15) | −0.002 [−0.055, 0.051] | +0.070 [0.013, 0.126] |
| z-RMS at Tmag 9 (within 0.80 to 1.15) | [0.971, 1.064] | [0.963, 1.123] |
| z-RMS at Tmag 13.5 (within 0.80 to 1.15) | [0.881, 1.003] | [0.866, 1.074] |
| Window-removal control, β ratio (0.95 to 1.05) | 1.000 | 1.000 |
| Window-removal control, residual RMS ratio (0.95 to 1.05) | 1.005 | 1.000 |
| Accepted / intended-injection rows | 1,477 / 2,021 | 1,361 / 1,931 |

All eight criteria passed in both samples. The adapter's support check accepted 136 of 137 and 232 of 239 non-Gaussian timings, and all criteria also passed in sensitivity scenarios in which every unexported non-Gaussian support check passed or every one failed. Calibration is conditional on successful identification and the fitted shape family; the replication's late bias of 0.07 SD is reported, not corrected. The original rule, which multiplied outcome errors by a brightness factor, failed its confirmation on coverage and the faint-star endpoint. After two implementation defects were corrected (a reversed side of the asymmetric coverage test, and product fallback conditioned on success), the uncorrected rule passed both samples. The final acceptance rule, replayed on the same samples with its likelihood grids checked, reproduced every saved timing. The acceptance threshold was chosen on these samples, so Table D1 is not an independent replication of the final rule.

<!-- claims: C022, C023, C028, C036, C038; evidence results/prefreeze/injection_evidence_t015v3a.json; D061 -->

### D.3 Identification boundary tests

With real transits subtracted and epochs uniform in phase, we injected trains offset from the catalogue period by up to ±0.6%, trains at 0.5, 2 and 3 times the period, and trains with every third transit displaced from the linear ephemeris (44 trials per scenario). Every trial identified for period offsets up to ±0.4%; at ±0.6%, outside the ±0.5% window, 18 of 44 identified and the 26 failures were all recorded as search-boundary failures. At 0.5 times the period, 37 of 44 identified and 327 of 629 observable events were timed; at 2 and 3 times, 42 of 44 identified and timings were conservative (z-RMS 0.32 and 0.28). At 30- and 50-minute displacements, identification succeeded in 43/44 and 42/44 trials; within identified trials, 93/93 and 85/93 observable events were timed. The corresponding conditional counts were 13/96 at 70 minutes, one at 90 and none at 120. Transits displaced by more than about an hour from the sector's own ephemeris are therefore lost or mistimed, a finite stress test, not a universal cutoff, that bears on the selection limit in Section 4.

<!-- claims: C024 -->

## Appendix E. Development evidence

This evidence comes from inspected TESS timings of 2022 to early 2024. It shaped the models, the measurement rule and its criteria, and none of it is a test of the frozen protocol.

### E.1 Reproducing the published benchmark

An independent base-R calculation, run on hash-verified release files, reproduces every DRB and DRC count and percentage of Table 5 of ExoClock IV [@Kokori2026ExoClockIV]. DRD differs by one count at 1σ, and the table's "Initial" column is not reproduced. The published rule drops the 42 DRD planets flagged for timing variations, a screen that uses information postdating the forecasts. We use flags known at the forecast origin only, and use hindsight flags solely in this reproduction. The calculation does not recover the authors' event lists or code.

<!-- claims: C001; D015 -->

### E.2 Release transfer and the chronological split

Four development designs use the same scoring with 400 host-refit resamples, rather than the final test's 2,000, and take outcome errors as the catalogue-reported σ times 1.087, the conditional REML estimate of the excess scatter of TESS timings (host-bootstrap interval 1.050 to 1.121). In release transfer, DRB forecasts are fitted against DRC-file timings of 2021 and DRC forecasts are scored against DRD-file timings from 28 September 2022 to 3 January 2024, with 15 training planets and 238 scored. In the chronological split, DRC forecasts are fitted on 2022 outcomes (133 planets) and scored from 2023 (206 planets). A delayed-origin reconstruction and a later-published training sensitivity vary the origin and the training sample. All four use proxy dates (Appendix A), and none is an issued correction or an untouched test.

**Table E1.** Development scores for M0, M1 and M2 (planet-balanced).

| Design | Method | Parameter | Standardised IS95 | 95% coverage | Mean 95% width (min) |
|---|---|---|---:|---:|---:|
| Release transfer | M0 | none | 32.86 | 0.884 | 10.13 |
| | M1 | $b$ = 2.685 | 30.50 | 0.957 | 16.53 |
| | M2 | $s$ = 2.162 | 30.41 | 0.956 | 16.44 |
| Chronological | M0 | none | 36.60 | 0.897 | 10.82 |
| | M1 | $b$ = 7.343 | 34.94 | 0.982 | 41.23 |
| | M2 | $s$ = 2.310 | 33.97 | 0.955 | 19.12 |

M2 − M0 is −2.445 [−5.756, +0.187] in release transfer and −2.628 [−6.351, +0.067] in the chronological split; the delayed-origin and later-published variants give −2.435 and −2.497, and all four intervals include zero. M2 brought 95% coverage close to nominal and raised 68% coverage to 0.674 and 0.698; the host-refit intervals for the coverage gain exclude zero. Only 23.5% and 19.4% of planets improve. TOI-1130 and TOI-125 supply about 69% and 86% of the mean gains, and removing them leaves −0.780 and −0.364. In release transfer, the 14 planets common to training and scoring score worse (+0.352) and the 224 new planets better (−2.620). M3 converges to M1 in release transfer ($s \approx 0$), and the chronological M1 fit is unstable (contrast −1.660, interval −8.87 to +9.79, 7.3% of planets improved). The M2 point contrast stays negative for outcome scales 0.85 to 1.25, and with zero covariance or correlations of ±1 the interval still includes zero.

Mixture fits to the development residuals gave DRB $b$ = 2.249, $s$ = 1.093 and DRC $b$ = 0.976, $s$ = 3.149, values that describe fitted mixtures and are not calibration statements. The scale-only fits above differ 2.7-fold between release transfer and the chronological split, and the mixture scales 2.3-fold between DRB and DRC; this instability motivated a tails-only correction. A training-span predictor of the mixing scale improved held-out log score by 0.027 nats per window [0.007, 0.054] in one split between hosts, but its chronological gain of 0.013 ranged from −9.07 to +0.043 over 400 joint resamples, so we did not carry it into the frozen test.

<!-- claims: C005, C008, C009, C010, C014, C015, C018, C032 -->

### E.3 The outcome-convention comparison

To test whether a correction fitted under catalogue outcome errors transfers to our pipeline, we remeasured every supported development transit of 321 planets with the frozen timing rule and refitted M1 to M3 under the catalogue and our own outcome conventions (4,615 events attempted, 3,946 timed, 294 planets). Table E2 gives M2 − M0 under the catalogue convention and two versions of our timing rule, with and without a brightness multiplier. On matched transits the sign and decision agree across the three, and every cell is inconclusive. M2 again raised 95% coverage, for example from 0.883 to 0.962 in matched release transfer.

**Table E2.** M2 − M0 by outcome convention, with 95% host-refit intervals (400 resamples); training / scored planets in brackets. The catalogue-convention cells for all timed transits are the earlier development fits (15 and 133 training planets; 238 and 206 scored).

| Design | Catalogue σ × 1.087 | Our rule, brightness multiplier | Our rule, no multiplier |
|---|---|---|---|
| Release transfer, matched transits (7 / 216) | −1.249 [−3.90, 2.66] | −2.195 [−5.06, 1.72] | −2.031 [−4.84, 1.74] |
| Chronological, matched transits (123 / 185) | −1.080 [−3.62, 1.32] | −1.465 [−4.75, 1.53] | −1.376 [−4.65, 1.53] |
| Release transfer, all timed (70 / 217) | −2.445 [−5.76, 0.19] | −2.154 [−5.15, 0.12] | −1.972 [−5.00, 0.28] |
| Chronological, all timed (124 / 186) | −2.628 [−6.35, 0.07] | −0.026 [−5.10, 15.04] | −0.082 [−5.11, 14.84] |

For the same photons, our mid-times differ from ExoClock's by a median of −0.18 s (chronological, 3,416 pairs) and −0.33 s (release transfer, 2,230), with z-RMS 0.37. The two share photons, so agreement of centres does not calibrate either set of errors. One falsely timed window drives the last row. In WASP-54 b sector 50, the recorded search windows sit about 12.18 hours from the true train, two were flagged at the prior edge and one was timed with z = 55; the chronological fit then moves $s$ from 2.33 to 3.24 and the contrast from −1.37 to −0.08, and the single-scale fit gives $b$ near 190. It is one case among 3,946 timings, and the final rule's shape gate excludes it.

On 2,291 development events retained by the guarded replay, exact grid convolution gives M2 − M0 of −1.897 against −1.922 under the Gaussian approximation, a point-score check with no refitting.

<!-- claims: C026, C029, C030, C034 -->

## Appendix F. Independent timing checks and their adjudication

Two timing programs sharing no code with the frozen pipeline were written after the frozen result, and neither uses the predicted epoch to find transits. One, written by Claude, runs a phase-blind box search and a batman transit fit on PDCSAP or SAP flux. The other, written by Codex, fits an empirical trapezoid with a profiled baseline. A fixed sample of 35 existing products was drawn for influential, calibration and control cases, with the design and triggers committed before fitting; it yielded 340 flux-route pairs, rising to 347 after a recorded amendment to the pairing rule. An earlier masking defect was retained and amended before the same sample was replayed.

**Table F1.** Independent PDCSAP timings against the frozen timings. Rows other than the first two are from Codex's checker.

| Planet or group | Matched / frozen | Median absolute difference (min) |
|---|---:|---:|
| HR 858 b, Claude's checker | 16 / 16 | 0.53 |
| HR 858 b, Codex's checker | 16 / 16 | 2.25 |
| TOI-905 b | 21 / 22 | 0.15 |
| WASP-184 b | 4 / 4 | 0.77 |
| TOI-559 b | 2 / 2 | 0.49 |
| Five calibration products | 19 / 20 | 0.12 to 2.04 |

For HR 858 b, Claude's checker on SAP flux gives a median absolute difference of 0.78 minutes and a maximum of 12.3. Against the published ephemerides of Bonfanti et al. [@Bonfanti2025TOI396], PDCSAP timings put planet b 374 to 422 minutes early, c 541 to 599 minutes late (SAP reaches 631) and d within −12.8 to +0.7 minutes. We did not verify the published time scale as TDB. Opposite offsets of b and c with d on time disfavour a simple common clock shift, not every extraction, blend or identity error.

Seven control triggers fired in the original comparison. After the pairing amendment, the 25 route rows still unpaired were all checker coverage refusals, each timed by another route or by the HR 858 checker, and no control showed a large discrepancy. Six raw control flags remain and are explained. The half-phase signal in WASP-18 b is consistent with its secondary eclipse (phase 0.503). The three sector-105 timings of HR 858 b flagged as local-shape departures led to the sensitivity in C.2. No broader sampling of 2026 products was warranted by these controls. All checks use the same photons, so they test software, not data, and the combined-error z-RMS of the pairs is not an independent calibration of the uncertainties.

<!-- claims: C050, C051, C057, C058; D071, D073 -->

## Appendix G. The allocation screen and its exact optimum

### G.1 Design

We asked whether a feature of the release files could pick a tenth of planets for wider observing windows and so capture more measured midpoints than spending the same window minutes evenly. The test scored DRC forecasts against inspected timings, with DRD supplying search periods and cycle labels. The slices are DRC-era timings from sectors 56 to 73, the 2026 timings rescored under DRC, and both pooled, on current-roster hosts. A flagged set had ⌈10%⌉ of the intended planets, with a pad of 15, 30, 60, 120 or 240 minutes. The budget counted every intended event. The two comparators spent that budget by scaling all windows proportionally or adding one pad to all. Capture was the share of accepted measured midpoints inside the window, averaged within and then across planets. Six single release-file features ranked planets; the search was committed before it was run. All six full fits and 30 host-held-out folds selected no pad, and no positive pad beat both comparators in any slice, including under zero covariance and the C2 correlation.

<!-- claims: C060, C061; D075, D076 -->

### G.2 Exact optimum

Because the policy class is finite, we also computed the best possible flagged set by dynamic programming, checked against exhaustive search in three regression cases and nine further cases. The largest achievable minimum gain against both comparators is negative in every slice.

**Table G1.** DRC-era accepted timings and the exact optimum of the allocation screen.

| Slice | Accepted planets / timings | Median / 99th percentile / maximum error (min) | Capture at ±1.96 forecast SD / with measurement SD | Largest minimum gain against both comparators (points) |
|---|---|---|---|---:|
| Sectors 56–73 | 92 / 1,078 | 1.0 / 10.6 / 30.4 | 0.557 / 0.934 | −8.77 |
| 2026 sectors | 128 / 1,974 | 1.2 / 25.6 / 36.6 | 0.623 / 0.876 | −3.69 |
| Pooled | 128 / 3,052 | — | 0.598 / 0.892 | −4.38 |

No accepted DRC error exceeded an hour. In the 2026 and pooled slices the best sets beat proportional scaling slightly and lose to the additive pad. A hindsight ranking by mean absolute error also lost, by 11 to 38 points. The measurement-inclusive capture is a Gaussian surrogate, not the full convolution. The result is a negative within the tested policy class, flagged fraction, pads, endpoint and samples; it does not identify why no allocation won, and it says nothing about full-transit capture or other populations.

<!-- claims: C061, C062, C064; D076 -->

## Appendix H. The exploratory extension

The extension adds 28 planets to the core's 156 (17.95%), with a period over 12 days or several DRD-listed planets per host, and brings the union to 184 planets on 175 hosts. The inventory had 3,399 opportunities before the four core and one extension boundary exclusions; the final manifests contain 3,103 core plus 291 extension events, or 3,394 in total. Our identification step is not validated in multi-planet systems, so the extension is exploratory. Of its 291 transits, 72 on 5 planets were accepted and 72 failed identification. M2 − M0 is −11.2 with a 95% interval from −56.4 to +6.3, inconclusive. The interval comes from 1,989 defined joint draws of 2,000: 11 draws select no extension host in the evaluation sample, so their scores are undefined and the frozen rule omits them. One host, TOI-178, carries the mean gain. The result is uninformative at five planets, and the extension events are scored under all four models in the replay package.

<!-- claims: C021, C044, C053 -->

## Online figure set

The eight-page online figure set gives an observed-minus-calculated plot for each of the 151 planets with accepted timings, against the DRD prediction. Bands show forecast-only 95% intervals and bars the reported 68% timing half-widths. Single-timing panels show the forecast band over a local one-day display span. The five planets with no accepted timing have no plot and appear in Table 3 with their statuses. *[location and file names on release]*

<!-- claims: C043, C046 -->
