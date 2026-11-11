# ExoClock transit forecasts agreed with later TESS timings to minutes, with one hours-long miss

<!--
Reconstruction step 4: final detailing. Claude (Opus 5.5), 11 November 2026,
from the reconciled step 3c draft (14_full_draft.md, after D083). Step 4 adds
references, AAS front and back matter, standalone display legends and a hard
edit; a second pass then edits for context, clarity and audience without
restructuring. Appendices are in 19_final_appendices.md. Displays are in
results/reconstruction_displays/. Citation keys marked † are verified
entries in references_additions.bib, not yet in references/references.bib.
Claim IDs follow each paragraph in comments that the journal build strips.
Nothing is released. manuscript/paper.md, docs/brief.md and
references/references.bib are unchanged.
-->

## Abstract

Observers schedule exoplanet transit observations from catalogue predictions
and their stated uncertainties, but refitting a catalogue does not show how
its earlier predictions performed. We tested one issued release of the
ExoClock catalogue, DRD, against 2,185 transit times of 151 planets measured
from later TESS observations, under measurement, acceptance and scoring rules
fixed before those data were opened, and we release the comparison as a
per-planet table with a replayable scoring package. The forecasts were
accurate to minutes: the pooled median absolute error was 1.1 minutes, and
every accepted timing of 150 planets fell within 26.4 minutes of prediction.
Nominal 95% intervals, combined with measurement uncertainty and a
reconstructed epoch–period correlation, covered 91% of timings per planet, a
modest shortfall. A correction learned from the previous release widened the
intervals 1.7-fold; its prespecified interval-score difference was −0.12
(95% interval −1.84 to +2.20), inconclusive. The one large failure, HR 858 b,
transited six hours early. Its neighbouring planets drifted in the pattern
expected from mutual gravitational perturbations, and its catalogue inputs
were old and scattered. One case cannot validate a warning rule, but such
features could be published beside each forecast and tested in future
releases.

*Unified Astronomy Thesaurus concepts:* Exoplanets (498); Ephemerides (464);
Transit photometry (1709); Transit timing variation method (1710);
Astrostatistics (1882); Catalogs (205)

<!-- claims: C043, C046, C050, C054, C063 -->

## 1. Introduction

Many measurements of exoplanet atmospheres can be made only while the planet
crosses the face of its star, a transit lasting from about one to a few hours.
Transmission spectroscopy with the James Webb Space Telescope (JWST) and the
planned Ariel survey both depend on it [@Gardner2023JWST†;
@Tinetti2018Ariel†]. Each visit is scheduled from a predicted mid-time and its
uncertainty, with baseline either side: one JWST observation of WASP-39 b
spanned 8.2 hours around a 2.8-hour transit [@Gardner2023JWST†]. The
uncertainty is, in effect, a forecast of how wrong the prediction may be. Too
narrow, and the transit may be partly missed; too wide, and scarce telescope
time is spent waiting.

ExoClock maintains transit ephemerides for Ariel's candidate targets
[@EdwardsTinetti2022ArielTargets†], combining timings from amateur and
professional telescopes and from space [@Kokori2022ExoClockI]. It issues them
as numbered, dated releases: DRB in 2021, DRC in 2022 and DRD in November 2025
[@Kokori2022ExoClockII; @Kokori2023ExoClockIII; @Kokori2026ExoClockIV]. Each
release fixes, for every planet, a linear ephemeris (a reference mid-time and
a period) and their uncertainties, at a known public time. A release is
therefore an issued forecast: it predates the transits it predicts, and later
observations can test it.

A linear ephemeris predicts the mid-time of transit $n$ as $T_0 + nP$. Error in
the period accumulates with $n$, at a rate governed by the covariance between
epoch and period [@Deeg2015; @KayeAigrain2025]. Gravitational interactions
with other planets shift transits early or late, producing transit-timing
variations (TTVs) [@Agol2005TTV†; @HolmanMurray2005TTV†], and slower changes
such as orbital decay do the same [@Yee2020WASP12†]. The formal errors of a
linear fit do not describe such shifts, so ephemerides degrade with time
[@Dragomir2020; @Lissauer2020Ephemerides; @Lissauer2024KeplerPeriods]. A
published forecast of TRAPPIST-1 h transits, for example, drifted by tens of
minutes [@Agol2024TRAPPIST1Forecast].

Several studies have compared predictions with later timings.
@Shan2023TESSTimings compared archived ephemeris predictions for 262 hot
Jupiters with TESS timings and found offsets for 31. Large compilations have
refitted hundreds of ephemerides from space and ground-based timings
[@IvshinaWinn2022; @Mallonn2019; @Edwards2021ORBYTS;
@Wang2024PeriodVariation; @Ma2025ExoEchoI]. @Agol2024TRAPPIST1Forecast
inflated TRAPPIST-1 forecast uncertainties 3.14-fold from leave-one-out
predictions and checked five later timings. Closest to our aim, @Kokori2026ExoClockIV compared
the DRB, DRC and DRD predictions with later TESS timings, noting that the DRD
comparison is optimistic because some of those timings were used to build DRD.

Fields that issue probabilistic forecasts, weather forecasting foremost, judge
them with proper scoring rules, which reward accuracy and honest spread
together, on outcomes the forecaster could not see [@GneitingRaftery2007;
@GneitingBalabdaouiRaftery2007]. Ecology adopted the same logic, for example by
testing population-viability models on the withheld second halves of long
time series [@Brook2000PVA] and now in iterative near-term forecasting [@Dietze2018†]. In a bounded search of the 82 works citing ExoClock III and
IV, we found no study that froze an issued ephemeris release, measured later
timings independently and scored its stated uncertainties this way.

Here we test DRD's issued predictions for 156 planets against transit times
measured from later TESS observations, and publish the comparison as a
per-planet table with a replayable scoring package (Table 3). Before any of
these data were opened, we recorded four questions. H1 asked whether the
stated uncertainties describe measured times. H2 asked whether the span of
historical information behind an ephemeris predicts its performance beyond
its nominal precision. H3, the prespecified primary test, asked whether a
correction learned from the previous release improves the next. H4 asked what
observing-window cost follows from the stated uncertainty. We answer H1 and
H3, report why H2 remains open, and answer part of H4. In brief, the issued
forecasts were good to minutes for all but one planet, which missed by hours.

<!-- claims: C019 (search, docs/sprint1_literature_review.md); hypotheses at bc85326:docs/project_brief.md; freeze D065 -->

## 2. Data and Methods

### 2.1 Releases and their dates

We treat the DRB, DRC and DRD ephemeris files deposited on the Open Science
Framework (OSF) as issued forecasts, each dated by its first verified public
availability in the OSF logs: 27 October 2021 (DRB), 27 September 2022 (DRC)
and 18 November 2025 (DRD), in UTC (Appendix A gives the logs and their
limits). Evaluation begins on 19 November 2025, the first full UTC day after DRD's
release; its journal publication in February 2026 serves as a sensitivity
date (Appendix C). Transit times are Barycentric Julian Dates in Barycentric
Dynamical Time (BJD_TDB) [@Eastman2010]. Because the eligibility boundaries
are in UTC and we did not convert them, we excluded four transits (and one in
the extension) predicted within ten minutes of a boundary.

<!-- claims: C019 -->

### 2.2 Forecast models

For transit $n$, counted from the reference epoch, the issued forecast is
$T_0 + nP$ with variance
$\sigma_{T_0}^2 + 2n\rho\,\sigma_{T_0}\sigma_P + n^2\sigma_P^2$.
ExoClock does not publish the correlation $\rho$, so we reconstruct it by
weighted least squares on each release's own input timings, with correlations
of 0 and ±1 as sensitivities. M0 combines this reconstructed correlation with
the published errors in a Gaussian forecast. M2 multiplies M0's variance by a
log-normal factor with median one and log-variance standard deviation (SD)
$s$, which adds tail mass without moving the centre.

We chose a tails-only correction because fitted scales were unstable in
development data, differing more than twofold between releases and between
designs (Appendix E). Two further models complete the fixed set: M1 scales
M0's SD, and M3 fits both a scale and a tail parameter. We fitted the
corrections by maximum likelihood to DRC's errors on 2,186 timings of
206 planets, which our own pipeline measured between 28 September 2022 and
3 January 2024. The fits gave $s = 2.05$ for M2 and a scale of 9.35 for M1.

<!-- claims: C004, C009, C039; frozen parameters D065 -->

### 2.3 Cohort and intended transits

We selected the cohort from pointing predictions and sector calendars of the
Transiting Exoplanet Survey Satellite (TESS), without opening any photometry.
The core cohort comprises 156 planets with one DRD-listed planet per host,
TESS magnitude below 13.5, period of at most 12 days and no TTV flag in DRD.
They offer 3,103 intended transits from 19 November 2025 in two-minute light
curves from the TESS Science Processing Operations Center (SPOC)
[@Ricker2015TESS; @Jenkins2016SPOC]. Planets whose TTVs were recognised only
after DRD stay in, because that difficulty belongs to the forecast under
test. A 28-planet extension (291 transits), with longer periods or several
catalogued planets per host, is exploratory, because our identification step
is not validated in multi-planet systems. Four planets with unresolved cohort
status are in neither set.

<!-- claims: C021, C043, C044; D015 -->

### 2.4 Measuring a transit time

For each planet and sector, a box least-squares search [@Kovacs2002BLS†]
within ±0.5% of the catalogue period scans every phase, so the predicted epoch
does not centre the search. A detection needs a depth signal-to-noise ratio of
at least 7, and other DRD planets on the host are masked. A transit shape is
then fitted to the sector light curve, and each transit's timing likelihood
is computed on a grid centred on the data's own epoch, holding the fitted
shape and noise level fixed. Where a Gaussian matches that likelihood's 95%
limits within 10%, scoring uses the Gaussian; otherwise it uses the grid. The
correction fits use the Gaussian approximation throughout.

Each timing is assigned to the nearest DRD cycle and accepted only if it lies
within a quarter period ($P/4$) of that cycle's prediction. Acceptance also
requires a valid SPOC light curve, a shape fit without gross failure (reduced
$\chi^2 \le 100$) and a well-resolved timing estimate. These checks do not
guarantee that every transit is found, or that a timing displaced by a whole
orbit is recognised (Section 4).

<!-- claims: C038, C039; scripts/acceptance.py, scripts/final_evaluation.py; D061, D080 -->

### 2.5 Qualifying the measurement

Before access, we injected artificial transits into real development-era
light curves, with the original transits masked, and reran identification,
shape fitting and timing. The final acceptance rule passed all eight declared
criteria on two frozen samples: 104 hosts with 1,477 timed injections, and
100 hosts with 1,361. Nominal 95% intervals contained 94.7% and 95.0% of
injected times, with a small late bias of 0.07 SD in the second sample. The
uncertainties of accepted timings were therefore well calibrated, though not
every transit is found. The rule was tuned on these same samples, so this is
not an independent replication (Appendix D).

<!-- claims: C038; D061–D062 -->

### 2.6 The freeze

Before any later photometry was opened, a manifest bound by SHA-256 hashes
75 files and 780 likelihood grids: the code, locked environments, cohort,
issued forecasts, fitted corrections, injection evidence and decision rule.
Two independently written verifiers check every hash. Barry W. Brook's access authorisation, tied to that
manifest, was committed on 8 November 2026 before any data were requested.
Fixing the analysis in advance separates prediction from explanation after
the fact [@Nosek2018†]; the repository history, not an external registry, is
the record.

One deviation occurred: a relative output path stopped the first measurement
run from writing likelihood grids for 71 of 304 light curves. The fault arose
when a non-Gaussian grid was written, and no forecast error or score entered
that code. We reran the identical code on the whole manifest; an independent
audit confirmed that everything completed in the first attempt was unchanged,
and both attempts are archived.

<!-- claims: C041, C042, C045; D064–D066 -->

### 2.7 Scoring and decision

Each forecast is convolved with the measurement uncertainty of its timing (a
Gaussian, or the tabulated likelihood), so that it predicts the measured, not
the true, mid-time. We score it by the 95% interval score,
$\mathrm{IS95} = (u-l) + \tfrac{2}{\alpha}(l-x)_+ + \tfrac{2}{\alpha}(x-u)_+$
with $\alpha = 0.05$, where $[l, u]$ is the central 95% interval and $x$ the
measured mid-time [@GneitingRaftery2007]. The score charges for interval
width and, heavily, for misses; smaller is better. Each event's score is
divided by M0's predictive SD, measurement error included, with the same
divisor for every model. Scores are averaged within planets, then across
planets, and describe accepted timings only. Because the divisor and the
likelihood come from the measurements, the score is proper only under
unverifiable assumptions about measurement error and selection (Appendix B).

The H3 statistic is the difference M2 − M0. Its uncertainty comes from 2,000
resamples of host stars, drawn jointly from the calibration and evaluation
sets, refitting the corrections in every draw [@DavisonHinkley1997†]. A 95%
interval wholly below zero decides improvement, wholly above zero harm, and
otherwise an inconclusive result. Coverage and other summaries use a
fixed-parameter host bootstrap of 10,000 draws and are labelled conditional.

<!-- claims: C039, C043, C049 -->

### 2.8 Other evidence and where it appears

Development evidence, from TESS timings of 2022 to early 2024 that we
inspected while designing the protocol, shaped the models, the measurement
rule and its criteria; it cannot serve as an untouched test (Appendix E).
After an external review of an earlier draft, we added diagnostics computed
from saved outputs and inspected data. Each is labelled post-review where it
appears, and none changes the primary decision. TESS sectors 74–97
(January 2024 to November 2025) have never been opened by this project.

<!-- claims: C050–C064, C055; D014, D071–D076 -->

## 3. Results

### 3.1 Which transits were measured

Of 3,103 intended transits, 2,185 (70%) were accepted, on 151 of 156 planets
(Table 1). Most losses were for lack of data: 730 of the 918 transits without
an accepted timing had no qualifying TESS cadence at the predicted time; of
the 2,369 transits with such coverage, 2,181 (92%) were accepted. Of the
accepted timings, 399 were scored from non-Gaussian likelihood grids. Five planets have no
accepted timing; Table 3 keeps them with their statuses. The exploratory
extension accepted 72 transits of only 5 planets and is uninformative
(Appendix H).

<!-- claims: C043, C046; terminal_ledger.csv.gz recount 10 Nov 2026 -->

### 3.2 Accuracy

The issued forecasts agreed with the measurements to about a minute. The
median absolute error was 1.1 minutes pooling all timings, and 1.3 minutes
with each planet weighted equally (Fig. 2a; Table 2). For 150 of the 151
planets, every accepted timing fell within 26.4 minutes of its prediction
(Fig. 2b). The exception, HR 858 b, missed on all 16 of its accepted
transits, by 355 to 404 minutes against a forecast SD of about 16 minutes.
Errors of unrecovered transits are unknown, so these figures do not estimate
a catalogue-wide failure rate.

<!-- claims: C048, C062, C063 -->

### 3.3 Accuracy over four years

The earlier DRC release, public in September 2022, gives a longer view. After
the review, we scored its forecasts against already-inspected timings from
2022–2023 and from 2026, using DRD to set search periods and cycle numbers.
Every accepted planet stayed within 37 minutes in both periods: 92 planets in
2022–2023 and 128 in 2026, nearly four years after issue (Fig. 2c). Median
errors were 1.0 and 1.2 minutes, and no error exceeded an hour. Because these
outcomes had been inspected, this comparison is descriptive, not a second
untouched test.

<!-- claims: C060, C062; D014 -->

### 3.4 Calibration (H1)

Under the reconstructed covariance and the supplied timing likelihoods, M0's
nominal 95% intervals covered 90.8% of accepted timings per planet (Fig. 3b).
The 95% host-bootstrap interval, 87.8–93.4%, excludes 95%: the combined
uncertainties were somewhat too narrow. Pooling events gives 92.0%, and
coverage falls short of nominal at every level from 50% to 99%. Measurement
uncertainty is a large part of the combined interval: the reported timing
uncertainty (a 68% half-width for non-Gaussian timings) is a median 1.9 times
the forecast SD per planet, and 2.7 times pooling events.
A post-review diagnostic places each timing within its full predictive
distribution (the probability integral transform, PIT; Fig. 3a)
[@GneitingBalabdaouiRaftery2007]. The misses were lopsided: 6.4% of timings,
planet-weighted, fell below M0's 95% interval (early) and 2.8% above it
(late); HR 858 b supplies 0.7 points of the early share. The asymmetry is not
a sign error in the calculation; we have not identified its cause.

<!-- claims: C043, C052, C063, C065; D076; PIT and percentiles: results/reconstruction_displays/pit_table2.json (scripts/reconstruction_pit_table2.py) -->

### 3.5 The prespecified test (H3)

M2 raised coverage to 97.6%, with intervals 1.67 times wider. Its effect on
the planet-balanced score was −0.12, with a 95% interval of −1.84 to +2.20
(Table 2): by the prespecified rule, inconclusive. The interval spans both
substantial benefit and substantial harm, so the data establish neither, nor
equivalence. Under M2, 111 of 151 planets scored worse, each by a bounded
amount, and 40 scored better. Most of the average gain came from HR 858 b,
and the sign of the contrast reverses when scores are divided by the
forecast-only SD instead (Appendix B). The single-scale M1, whose factor of
9.35 was learned from DRC's errors, covered 99.3% and had the worst
standardised IS95.

<!-- claims: C043, C046, C052 -->

### 3.6 HR 858 b: the one large miss

HR 858 b, the innermost of three small planets that TESS found around a
naked-eye star [@Vanderburg2019HR858†], transited 5.9 to 6.7 hours early on
all 16 accepted timings in sectors 105–107, outside every tested model's 95%
interval (Fig. 4b). The timings form a coherent sequence, with a local period
of 3.58395 days against DRD's 3.585266 and a scatter of 4.3 minutes about a
line. Two independently written timing programs reproduced all 16 timings
from the same light curves, to median differences of 0.5 and 2.2 minutes.
One of them also timed the system's other planets against published
ephemerides [@Bonfanti2025TOI396]: b ran 6.2 to 7.0 hours early, c 9.0 to
10.0 hours late, and d within 13 minutes (Fig. 4a). Opposite drifts of b and
c, with d on time, are the pattern expected from mutual perturbations near
their 5:3 period ratio, and they argue against a common clock offset.

These checks share photons with ours, so they cannot exclude every blend or
identity error. Where they disagreed most, by up to 22 minutes on three
sector-105 timings, substituting the independent values gave a contrast of
−0.09, still inconclusive under fixed-fit resampling (Appendix C).

<!-- claims: C048, C050, C051, C057, C059 -->

### 3.7 HR 858 b: visible beforehand

Several features of HR 858 b's forecast were visible before DRD was issued.
The planet was new to DRD. Its 16 released input timings, all from space,
spanned 756 days and ended in November 2020, so the forecast extrapolated
more than five years beyond a two-year baseline. They scattered about the
issued line by 2.2 times their quoted errors. A preprint posted a year before
DRD reported TTVs for b and c, with simulated semi-amplitudes of about two
and five hours [@Bonfanti2025TOI396]. DRD's own TTV flag follows its
detection criterion and was not raised. These are documented features of one
case, not validated predictors.

<!-- claims: C048, C054 -->

### 3.8 Information span (H2)

H2 asked whether the span of historical information behind an ephemeris
predicts its performance beyond its nominal precision. In development data,
the released training span gave a small improvement in predictive score in
one split between hosts, but the gain was unstable in a chronological split,
so we did not carry it into the frozen test. The question remains open; the
release-input features in Table 3 make it testable in future releases.

<!-- claims: C010, C015, C054 -->

### 3.9 Measured midpoints and observing cost (H4)

We can answer only part of H4. Illustratively, padding each forecast-only 95%
window by three minutes per side contained 94% of accepted mid-times,
averaging equally across planets, and added 18,618 window-minutes across all
intended transits. This describes measured midpoints and is not scheduling
advice: full-transit capture and telescope cost depend on transit durations
and records of attempted observations, which we did not have.

<!-- claims: C063; D076 §4 -->

### 3.10 Could the failures have been targeted?

After the review, we asked whether information released with a forecast
could direct wider windows to the planets most likely to miss. A screen
padded the windows of the 10% of planets flagged by each of six release-file
rankings, by 15 to 240 minutes, and compared them with spending the same
minutes evenly across all windows (Appendix G). On inspected DRC-era data, no
ranking beat both even-spending comparators; even the best flagged set chosen
with hindsight lost to at least one by 3.7 to 8.8 percentage points of
captured midpoints.

<!-- claims: C061, C062, C064 -->

### 3.11 The comparison table

Table 3 lists all 156 core planets, including the five without accepted
timings, as a machine-readable table: the issued ephemeris, the reconstructed
covariance, the fate of every intended transit, error and coverage summaries,
and dated release-input features (input age, baseline and scatter about the
issued line). Unknown values are kept distinct from absent ones, and each row
links to the full ledger of intended transits. A portable package of 499 hash-bound files, including 463 timing
likelihood grids, rescores every accepted event under all four models and
replays the saved scores exactly, so other forecasts can be scored against
the same outcomes.

<!-- claims: C053, C054 -->

## 4. Discussion

For observers, the answer is reassuring, with one exception. ExoClock's
issued forecasts matched the measured transits to about a minute at the
median and within half an hour for 150 of 151 planets; even the earlier DRC
release stayed within 37 minutes nearly four years after issue. One planet
missed by six hours. Scheduling a full transit also needs its duration and
baseline, which we did not test.

The combined 95% intervals covered about 91% of accepted timings, a modest
but clear shortfall. Minute-scale accuracy and undercoverage are compatible:
the forecast windows are only minutes wide, so small absolute differences can
fall outside them. Forecast errors, unmodelled timing variations, measurement
error and our reconstructed covariance can all contribute, and a test of
their combination cannot say which is responsible. Publishing epoch–period
covariances would remove the need for our reconstruction.

The correction raised coverage by widening intervals, but the interval score
charges for width as well as misses. Most planets paid a small width penalty,
while a few with large misses gained much more: once a timing lies beyond two
fixed intervals, the score difference between them stops growing, so widening
can earn large gains on a far miss without capturing it (Appendix B). HR 858 b
supplied most of the mean gain, and without it the contrast changes sign, yet
none of its timings fell inside any tested model's 95% interval. Widening bought coverage for typical planets at a cost,
without containing the one failure that mattered.

Mostly accurate forecasts with a few large offsets resemble
@Shan2023TESSTimings's finding for archival hot-Jupiter ephemerides. Our test
differs in combining one issued release, independently measured later
timings and a fixed opportunity list that keeps losses visible. Earlier
comparisons differ in cohorts, horizons and selection, so patterns, not
failure rates, can be compared [@Kokori2026ExoClockIV; @IvshinaWinn2022;
@Wang2024PeriodVariation].

HR 858 b was new to the release, with old, scattered inputs and previously
published TTVs. Most of these features can be computed from the release files
(Table 3), and publishing them beside each forecast would let users judge
similar cases. Whether they predict failure is untested: our allocation screen
found no ranking that beat spending the same minutes evenly, and one case
cannot validate a warning rule. Future releases could test one prospectively
[@Lissauer2024KeplerPeriods].

Our conclusions are conditional in six ways. First, only accepted timings,
70% of intended transits, are scored, so the rate of missed transits cannot
be estimated. Second, because each timing is assigned to the nearest DRD cycle
before the $P/4$ gate, a transit displaced by more than a quarter period would
be rejected, or attributed to the wrong cycle, rather than scored as a miss;
HR 858 b's six-hour error lies well inside its 21.5-hour quarter period.
Third, coverage depends on the reconstructed covariance and on measurement
likelihoods qualified on the samples used to tune the rule. Fourth, the test
covers one release's first year and stars with one DRD-listed planet, which
may host others. Fifth, our independent re-timings share photons with the
frozen pipeline, so they test the software, not the data. Sixth, a single
gross failure carries most of the score contrast.

The table and scoring package let new corrections, TTV-aware ephemerides or
another catalogue's predictions be scored against the same outcomes, and the
issued-forecast design applies equally to ecological and other models
[@Brook2000PVA; @Dietze2018†]. The unopened TESS sectors 74–97 could support a
separately authorised study of hour-scale misses on previously unexamined
hosts, given a fixed cohort, forecasts issued before the observations, and
qualified recovery and cycle identification.

Observers can plan on minute-level accuracy from an issued ExoClock forecast
for nearly every planet we tested. They should not assume it for every
planet: the one exception transited six hours early, outside every interval
we tested.

<!-- claims: C043, C045, C046, C049, C050, C053, C054, C055, C062, C063; D076, D080 -->

## Display items

**Figure 1.** What is tested, and when. (a) One forecast, with illustrative
values not to scale: the predicted mid-time (diamond) and its forecast-only
95% interval (dark blue), a measured mid-time with its own 95% uncertainty
(orange), the scoring interval, which convolves the forecast with the
measurement error (light blue), and a full observing window of transit
duration plus baseline (grey) for contrast. (b) Timeline. Upper lane,
observations: DRC issued on 27 September 2022; the window of TESS timings
used to fit the corrections (28 September 2022 to 3 January 2024); sectors
74–97 (January 2024 to November 2025, hatched), never opened by this project;
DRD issued on 18 November 2025; and the later TESS exposures that supply the
scored timings. Lower lane, analyst access: none to the scored timings until
the freeze and authorisation on 8 November 2026. [`fig1_schematic.png`]

**Figure 2.** The issued forecasts were accurate to minutes, with one
exception. (a) Histogram of absolute errors of the 2,185 accepted timings of
151 planets, on a logarithmic minute scale; the vertical line marks the
pooled median, 1.11 minutes, and the arrow HR 858 b's timings, up to
404 minutes. (b) Each planet's largest accepted error, ranked, with marker
area proportional to its number of accepted timings; the dashed line marks
26.4 minutes, at or below which 150 of 151 planets lie. HR 858 b (orange) is
the outlier. (c) DRC forecast errors against years since DRC's issue, for
3,052 accepted timings of 128 planets in two blocks: 2022–2023 (sectors 56–73,
development data) and 2026 (held out for the DRD test and inspected after
it). Points are individual timings and the line joins binned medians; the
gap between blocks is omitted. This panel is a retrospective comparison on
already-inspected timings. [`fig2_accuracy.png`]

**Figure 3.** The stated uncertainties were somewhat too narrow, with more
early than late misses. (a) Planet-weighted histograms of the predictive
probability integral transform (PIT) of each accepted timing under M0 (blue)
and M2 (yellow), computed from the saved forecasts and likelihood grids. Low
values mean the transit came earlier than forecast; shaded strips mark the
tails outside the central 95% interval, which contains 0.908 of timings under
M0 and 0.976 under M2. The dashed line is the flat histogram that calibrated
forecasts would give if timing uncertainties are correctly stated and
acceptance does not depend on the timing error. (b) Planet-weighted coverage
of accepted timings against nominal central-interval probability for M0 and
M2; vertical bars are conditional 95% host-bootstrap intervals, and the dashed
line marks perfect calibration. [`fig3_calibration.png`]

**Figure 4.** HR 858: the one large miss. (a) Observed minus published
transit times, in hours, of planets b (blue), c (yellow) and d (grey) in TESS
sectors 105–107 (June to September 2026), measured by an independent timing
program against the ephemerides of @Bonfanti2025TOI396. Planet b runs about
six hours early and c about nine to ten hours late, while d stays on time.
(b) HR 858 b against the issued DRD ephemeris (horizontal line at zero): its
16 released input timings of 2018–2020 (black), the forecast-only 95%
interval over the 2026 transits (blue band), and the 16 accepted 2026
timings (orange), which lie 5.9 to 6.7 hours early. Of 24 intended transits,
6 had no cadence at the prediction, one timing was at the edge of its prior
and one integration was unresolved. The axis gap between 2021 and 2026 is
omitted. [`fig4_hr858.png`]

**Table 1.** Fate of the 3,103 intended transits of the 156 core planets.
Each transit has one terminal status. The italic row counts transits whose
predicted time had qualifying TESS cadence; four further timings were
accepted outside that set.

| Status | Transits |
|---|---:|
| Accepted and scored | 2,185 |
| No cadence coverage at the predicted time | 431 |
| Window excluded for coverage | 290 |
| Timing integration unresolved | 75 |
| Timing at the edge of its prior | 71 |
| Light-curve identification failed | 39 |
| Likelihood support unresolved | 12 |
| *Qualifying coverage at prediction: accepted / total* | *2,181 / 2,369* |

**Table 2.** Headline results for the 2,185 accepted timings of 151 planets.
M0 is the issued forecast with the reconstructed epoch–period correlation; M2
adds the tails-only correction learned from DRC. Coverage, widths and scores
weight planets equally and use the forecast convolved with each timing's
measurement uncertainty. IS95 is the 95% interval score (smaller is better);
the standardised score divides each event's IS95 by M0's predictive SD. The
M2 − M0 interval comes from 2,000 joint host resamples with refitting.
Percentiles are the smallest error whose cumulative weight reaches the stated
level, without interpolation; each planet's weight is split equally among its
timings.

| Quantity | M0 (reconstructed) | M2 (tails) |
|---|---:|---:|
| Median absolute error, pooled / equal-planet (min) | 1.11 / 1.31 | — |
| 95th / 99th percentile absolute error, pooled (min) | 6.4 / 17.9 | — |
| 95th / 99th percentile absolute error, equal-planet (min) | 9.0 / 18.7 | — |
| Largest error excluding HR 858 b / HR 858 b (min) | 26.3 / 404 | — |
| 95% coverage | 0.908 | 0.976 |
| Mean 95% width (min) | 10.5 | 17.5 |
| Standardised IS95 | 11.33 | 11.21 |
| IS95 (min) | 106.3 | 97.8 |
| **M2 − M0, standardised IS95** | | **−0.121 [−1.84, 2.20]**, inconclusive |

**Table 3.** The comparison table: one row for each of the 156 core planets,
including the five without an accepted timing. Ten rows are printed here,
the first ten planets alphabetically, to show the format; they are not a
representative sample. The full table and the 28 extension planets are
machine-readable files, with a data dictionary. Columns: planet and host;
DRD $T_0$, $P$ and their uncertainties; reconstructed correlation and its
provenance tier; intended, coverage-qualified and accepted transits; terminal
statuses; median and maximum absolute error (minutes); M0 and M2 coverage;
release-input age, baseline and scatter; and dated TTV-literature status,
with unknown kept distinct from absent. [`table3_planets.csv`,
`table3_extension.csv`, `table3_dictionary.md`, `table3_excerpt.md`]

## Appendices (in `19_final_appendices.md`)

- A. Release dating and the DRC timing-table chronology.
- B. Loss scales, the per-planet contrast and influence diagnostics, the bound
  on interval-score differences, all four models' parameters and outcomes,
  and the post-review PIT and error-quantile methods.
- C. Declared sensitivities, including the journal-date anchor and the
  sector-105 rescore.
- D. Measurement qualification: injection design, criteria and results.
- E. Development evidence: benchmark reproduction, release transfer and the
  outcome-convention comparison.
- F. Independent timing checks and their adjudication.
- G. The allocation screen and its exact optimum.
- H. The exploratory extension.
- Online figure set: observed-minus-calculated plots for all 151 planets
  (`results/reconstruction_displays/online_figure_set_oc.pdf`).

## Data availability

Code, results, the claims ledger and the decision log are at
github.com/BWBrook/transit-forecast-audit (code MIT; text, figures and derived
data CC BY-SA 4.0). The ExoClock releases are on OSF under CC BY 4.0
(10.17605/OSF.IO/WNA5E, 10.17605/OSF.IO/P298N, 10.17605/OSF.IO/WPJTN). The
held-out timings use TESS SPOC two-minute light curves from the Mikulski
Archive for Space Telescopes (MAST) [@MAST2021TESSLightCurves†]; development
used TESS-SPOC full-frame-image light curves [@Caldwell2020TESSSPOC;
@MAST2020TESSSPOCData]. The comparison table and scoring package will be
deposited on Zenodo with this snapshot *[DOI on release]*.

*Facilities:* TESS, MAST.

*Software:* NumPy [@Harris2020NumPy†], SciPy [@Virtanen2020SciPy†],
Astropy [@Astropy2013†; @Astropy2018†; @Astropy2022†], Matplotlib
[@Hunter2007Matplotlib†], tess-point *[ascl:2003.001, entry to import]*.

## Author contributions and use of AI

Barry W. Brook set the question, required that the later TESS data stay
unopened until the protocol was frozen, authorised access on 8 November 2026
and reviews the final text before release. Claude (Anthropic; Claude Opus 5.5)
and Codex (OpenAI; GPT-6.1-sol and earlier models listed in the repository)
designed and ran the analyses, wrote the code and reviewed each other's work.
Claude Sonnet 5.5 drafted the initial article, brief and agent guide, and the
first draft of the appendices in this reconstruction; both agents revised
them. GPT-6 Pro (OpenAI) suggested the topic and reviewed an earlier draft.
Detailed roles and reviewed correspondence snapshots are in the repository.
*[expand per AAS LLM policy at journal build]*

## Acknowledgments

This paper includes data collected by the TESS mission, obtained from MAST at
the Space Telescope Science Institute (STScI). Funding for the TESS mission
is provided by the NASA Explorer Program. STScI is operated by the
Association of Universities for Research in Astronomy, Inc., under NASA
contract NAS5-26555. We thank the ExoClock contributors, whose open releases
made this test possible.

## References to import (†, entries in `references_additions.bib`)

Step 3c: Gardner2023JWST, Tinetti2018Ariel, Agol2005TTV, HolmanMurray2005TTV,
Kovacs2002BLS, Dietze2018, Nosek2018, DavisonHinkley1997.
Step 4 (verified from doi.org metadata, 11 November 2026):
EdwardsTinetti2022ArielTargets (10.3847/1538-3881/ac6bf9), Yee2020WASP12
(10.3847/2041-8213/ab5c16), Vanderburg2019HR858 (10.3847/2041-8213/ab322d),
MAST2021TESSLightCurves (10.17909/t9-nmc8-f686), Harris2020NumPy
(10.1038/s41586-020-2649-2), Virtanen2020SciPy (10.1038/s41592-019-0686-2),
Hunter2007Matplotlib (10.1109/MCSE.2007.55), Astropy2013
(10.1051/0004-6361/201322068), Astropy2018 (10.3847/1538-3881/aabc4f),
Astropy2022 (10.3847/1538-4357/ac7c74). Not DOI-registered: tess-point,
ascl:2003.001.
