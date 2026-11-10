# ExoClock transit forecasts agreed with later TESS timings to minutes, with one hours-long miss

<!--
Reconstruction step 3c: full draft. Claude (Opus 5.5), 10 November 2026,
expanded from the reconciled paragraph abstracts in 11_paragraph_abstracts.md.
Written in the voice of the finished paper. Not yet built or released:
Fig. 1, Fig. 2, Fig. 3a, Fig. 4b and Table 3 are planned (04_display_items.md);
Table 2 cells marked [compute] await the display build. manuscript/paper.md,
docs/brief.md and references/references.bib are unchanged. Claim IDs for each
paragraph are in trailing comments; the journal build strips them. Citation
keys marked † are verified candidates (13_step3b_reference_checks.md) not yet
in the bibliography.
-->

## Abstract

Observers schedule exoplanet transit observations from catalogue predictions
and their stated uncertainties, but refitting a catalogue does not show how
its earlier predictions performed. We compared one issued release of the
ExoClock catalogue, DRD, with 2,185 transit times of 151 planets that TESS
measured after its release, under measurement, acceptance and scoring rules
fixed before those data were opened. We provide the comparison as a per-planet
table with a replayable scoring package. The pooled median absolute error was
1.1 minutes, and every accepted timing of 150 planets fell within 26.4 minutes
of prediction. Nominal 95% intervals, combined with measurement uncertainty,
covered 91% of timings per planet, a modest shortfall. A correction learned
from the previous release widened the intervals 1.7-fold; its prespecified
interval-score comparison was inconclusive. The one large failure, HR 858 b,
arrived six hours early. Its neighbouring planets drifted in the pattern
expected from mutual gravitational perturbations, and its catalogue inputs were
old and scattered. One case cannot validate a warning rule, but such features
could be published beside each forecast and tested in future releases.

<!-- claims: C043, C046, C050, C054, C063 -->

## 1. Introduction

Many measurements of exoplanet atmospheres can be made only while the planet
transits its star, an event lasting from about one to a few hours. JWST
transmission spectroscopy and the planned Ariel survey both depend on it
[@Gardner2023JWST†; @Tinetti2018Ariel†]. Each visit is scheduled from a
predicted mid-time and its uncertainty, with baseline either side; one JWST
observation of WASP-39 b, for example, spanned 8.2 hours around a 2.8-hour
transit. The uncertainty matters as much as the prediction. Users treat it as
a forecast of how wrong the prediction may be: too narrow, and the transit may
be partly missed; too wide, and scarce telescope time is spent waiting.

ExoClock maintains transit ephemerides for Ariel's candidate targets, combining
timings from amateur and professional telescopes and from space
[@Kokori2022ExoClockI]. It issues them as numbered, dated releases: DRB in
2021, DRC in 2022 and DRD in November 2025 [@Kokori2022ExoClockII;
@Kokori2023ExoClockIII; @Kokori2026ExoClockIV]. Each release fixes, for every
planet, a linear ephemeris (a reference mid-time and a period) and their
uncertainties, at a known public time. A release is therefore an issued
forecast: it was made before the transits it predicts, and later observations
can test it.

A linear ephemeris predicts the mid-time of transit $n$ as $T_0 + nP$. Error in
the period accumulates with $n$, and the covariance between epoch and period
governs how fast [@Deeg2015; @KayeAigrain2025]. Gravitational interactions
with other planets can also shift transits early or late, producing
transit-timing variations (TTVs) [@Agol2005TTV†; @HolmanMurray2005TTV†]. The
formal fit errors of a linear ephemeris do not describe such shifts, and
ephemerides degrade with time as a result [@Dragomir2020;
@Lissauer2020Ephemerides; @Lissauer2024KeplerPeriods]. A published forecast of
TRAPPIST-1 transits, for example, drifted by tens of minutes
[@Agol2024TRAPPIST1Forecast]. Whether stated uncertainties stay honest after
release is an empirical question.

Several studies have compared predictions with later TESS timings. Shan et al.
compared archived ephemeris predictions for 262 hot Jupiters with TESS timings
and found offsets for 31 [@Shan2023TESSTimings]. Large
compilations have refitted hundreds of ephemerides from TESS and ground-based
timings [@IvshinaWinn2022; @Mallonn2019; @Edwards2021ORBYTS;
@Wang2024PeriodVariation]. For TRAPPIST-1, Agol et al. inflated forecast
uncertainties by a factor of about three, estimated from leave-one-out
predictions, and checked them against five later timings
[@Agol2024TRAPPIST1Forecast]. Closest to our aim, ExoClock IV compared the
DRB, DRC and DRD predictions with later TESS timings. It noted that the DRD
comparison is optimistic, because some of those timings were used to build DRD
[@Kokori2026ExoClockIV].

Fields that issue probabilistic forecasts, weather forecasting foremost, judge
them by proper scoring rules. These reward accuracy and honest spread together
and are applied to outcomes the forecaster could not see
[@GneitingRaftery2007; @GneitingBalabdaouiRaftery2007]. Ecology adopted the
same logic: Brook et al. fitted population-viability models to the first half
of long time series and scored their predictions on the second half
[@Brook2000PVA], and near-term ecological forecasting now tests predictions
iteratively against new data [@Dietze2018†]. In a bounded search of the 82
works citing ExoClock III and IV, we found no study that froze an issued
ephemeris release, measured later timings independently and scored its stated
uncertainties this way.

Here we compare DRD's issued predictions with transit times that TESS measured
after DRD's release, for 156 planets. We publish the comparison as a per-planet
table with a replayable scoring package (Table 3), recording for every intended
planet the issued forecast, which transits were measured, and how far and how
often they departed from prediction. Before any of these data were opened, we
recorded four questions. H1 asked whether the stated uncertainties describe
measured times. H2 asked whether the span of historical information behind an
ephemeris predicts its performance beyond its nominal precision. H3, the
prespecified primary test, asked whether a correction learned from the previous
release improves the next. H4 asked what observing-window cost follows from the
stated uncertainty. We answer H1 and H3, report why H2 remains open, and answer
part of H4.

<!-- claims: C019 (search, docs/sprint1_literature_review.md); hypotheses at bc85326:docs/project_brief.md; freeze D065 -->

## 2. Data and Methods

### 2.1 Releases and their dates

We use the DRB, DRC and DRD ephemeris files deposited on OSF (Data
availability), treating each file as an issued forecast. We date each release
by its first verified public availability, from OSF logs for the project and
each file: 27 October 2021 (DRB), 27 September 2022 (DRC) and 18 November 2025
(DRD), in UTC. DRD's files were uploaded on 17 November while the project was
private, so its date is the public transition. These logs establish when the
files became public, not whether they were shared earlier. Evaluation begins
on 19 November 2025, the first full UTC day after DRD's release; the journal
publication of February 2026 serves as a sensitivity date (Appendix C).
Transit times are in BJD_TDB [@Eastman2010]. Five transits predicted within
ten minutes of an eligibility boundary set in UTC are excluded rather than
converted.

<!-- claims: C019 -->

### 2.2 Forecast models

For transit $n$, counted from the reference epoch, the issued forecast is
$T_0 + nP$ with variance
$\sigma_{T_0}^2 + 2n\rho\,\sigma_{T_0}\sigma_P + n^2\sigma_P^2$.
ExoClock does not publish the correlation $\rho$, so we reconstruct it by
weighted least squares on each release's own input timings. For DRD the
reconstruction changes the total predictive variance by at most about 3%, and
we test correlations of 0 and ±1 as sensitivities. M0 is this Gaussian
forecast. M2 multiplies M0's variance by a log-normal factor with median one
and log-variance SD $s$, which adds tail mass without moving the centre.

We chose a tails-only correction because development data showed that a single
scale does not transfer between releases. DRB's forecasts were about 2.2 times
too narrow at the median, whereas DRC's were calibrated at the median but had
heavy tails between planets. Two further models complete the fixed set: M1
scales M0's SD by one fitted factor, and M3 fits both a scale and a tail.
Each correction was fitted once, by maximum likelihood, on DRC's errors for
206 planets, using 2,186 timings that our own pipeline measured between
28 September 2022 and 3 January 2024. The fits gave $s = 2.05$ for M2 and a
scale of 9.35 for M1.

<!-- claims: C004, C009, C039; frozen parameters D065 -->

### 2.3 Cohort and intended transits

We selected the cohort from TESS pointing predictions and sector calendars,
without opening any photometry. The core cohort comprises 156 planets with one
DRD-listed planet per host, TESS magnitude below 13.5, period of at most
12 days and no TTV flag in DRD. They offer 3,103 intended transits from
19 November 2025 in SPOC two-minute light curves [@Ricker2015TESS;
@Jenkins2016SPOC]. Planets whose TTVs were recognised only after DRD stay in,
because that difficulty belongs to the forecast being tested. A 28-planet
extension (291 transits), with longer periods or several catalogued planets
per host, is exploratory, because our identification step is not validated in
multi-planet systems. Four planets with unresolved cohort status are outside
both sets.

<!-- claims: C021, C043, C044; D015 -->

### 2.4 Measuring a transit time

For each planet and sector, a box least-squares search [@Kovacs2002BLS†]
within ±0.5% of the catalogue period scans every phase, so the predicted epoch
does not centre the search. A detection needs a depth signal-to-noise ratio of
at least 7, and other DRD planets on the host are masked. A transit shape is
then fitted to the sector light curve, and each transit's mid-time receives a
posterior on a grid centred on the data's own epoch, not the forecast. Where
that posterior is not Gaussian within 10%, the full likelihood grid is kept for
scoring.

Each fitted timing is assigned to the nearest DRD cycle and accepted only if
it lies within a quarter period ($P/4$) of that cycle's prediction. Acceptance
also requires a valid SPOC light curve, a shape fit without gross failure
(reduced $\chi^2 \le 100$) and a well-resolved timing estimate. These checks
do not guarantee that every transit is found, or that a timing displaced by a
whole orbit is recognised (Section 4).

<!-- claims: C038, C039; scripts/acceptance.py, scripts/final_evaluation.py; D061, D080 -->

### 2.5 Qualifying the measurement

Before protected access, we injected artificial transits into real
development-era light curves, after removing the real transits, and reran
identification, shape fitting and timing. Every intended injection received a
row before fitting, so failures stayed in the denominator. The final
acceptance rule passed all eight declared criteria on two frozen samples:
104 hosts with 1,477 timed injections, and 100 hosts with 1,361. Nominal 95%
intervals contained 94.7% and 95.0% of injected times (90% host-bootstrap
intervals 93.4–95.9% and 93.8–96.1%), with a small late bias of 0.07 SD in
the second sample. This shows that accepted timings carry honest
uncertainties, not that every transit is found. The rule was tuned on these
same samples, so this is not an independent replication (Appendix D).

<!-- claims: C038; D061–D062 -->

### 2.6 The freeze

Before any later photometry was opened, a manifest bound by SHA-256 hashes
75 files and 780 likelihood grids: the code, locked environments, cohort,
issued forecasts, fitted corrections, injection evidence and decision rule. A
verifier recomputes every hash, and two agents built and checked it
independently. The protected run refuses to start unless an access record
cites the manifest and records the human lead's decision. That record was
committed on 8 November 2026, before any data were requested. Fixing the
analysis in advance separates a test of predictions from an explanation after
the fact [@Nosek2018†]; we used no external registry, and the repository
history is the record.

One deviation occurred. The first measurement run failed to write likelihood
grids for 71 of 304 light curves because of a relative output path, a fault
that depended on the shape of the measured likelihood but not on any forecast
or score. We reran the identical code on the whole manifest. An independent
audit confirmed that every product, window and grid completed in the first
attempt was unchanged in the rerun, and both attempts are archived.

<!-- claims: C041, C042, C045; D064–D066 -->

### 2.7 Scoring and decision

Each forecast is convolved with the measurement uncertainty of its timing (a
Gaussian, or the tabulated likelihood), so that it predicts the measured, not
the true, mid-time. We score it by the 95% interval score,
$\mathrm{IS} = (u-l) + \tfrac{2}{\alpha}(l-x)_+ + \tfrac{2}{\alpha}(x-u)_+$
with $\alpha = 0.05$, where $[l, u]$ is the central 95% interval and $x$ the
measured mid-time [@GneitingRaftery2007]. The score penalises width and misses
together; smaller is better. Each event's score is divided by M0's predictive
SD, measurement error included, so planets with tight and loose forecasts
count comparably. Scores are averaged within planets, then across planets, and
describe accepted timings only.

The H3 statistic is the difference M2 − M0. Its uncertainty comes from 2,000
resamples of host stars, drawn jointly from the calibration and evaluation
sets, refitting the corrections in every draw [@DavisonHinkley1997†]. A 95%
interval wholly below zero decides improvement, wholly above zero harm, and
otherwise an inconclusive result. Coverage and other summaries use a
fixed-parameter host bootstrap of 10,000 draws and are labelled conditional.

<!-- claims: C039, C043, C049 -->

### 2.8 Other evidence and where it appears

Two kinds of evidence surround the primary test. Development evidence, from
TESS timings of 2022 to early 2024 that we inspected while designing the
protocol, shaped the models, the measurement rule and its criteria; it cannot
serve as an untouched test (Appendix E). After an external review of an
earlier draft, we added analyses of the saved held-out outputs and of
inspected development data. These are independent re-timing, coverage and
loss-scale diagnostics, release-input features, a sensitivity for HR 858 b
and a bounded allocation screen. Each is labelled as post-review where it
appears, and none changes the primary decision. TESS sectors 74–97 (January
2024 to November 2025) have never been opened by this project.

<!-- claims: C050–C064, C055; D014, D071–D076 -->

## 3. Results

### 3.1 Which transits were measured

Of 3,103 intended transits, 2,185 (70%) were accepted, on 151 of 156 planets
(Table 1). Most losses were for lack of data: 730 of the 918 transits without
an accepted timing had no qualifying TESS cadence at the predicted time. Of the
2,369 transits with qualifying coverage, 2,181 (92%) were accepted, and four
further timings were accepted outside that set. Of the accepted timings, 399
were scored from non-Gaussian likelihood grids. Five planets have no accepted
timing; Table 3 retains them with their statuses. The exploratory extension
accepted 72 transits of only 5 planets and is uninformative (Appendix H).

<!-- claims: C043, C046; terminal_ledger.csv.gz recount 10 Nov 2026 -->

### 3.2 Accuracy

The issued forecasts agreed with the accepted measurements to about a minute.
The median absolute error was 1.1 minutes pooling all timings, and 1.3 minutes
with each planet weighted equally (Fig. 2a; Table 2). For 150 of the 151
planets, every accepted timing fell within 26.4 minutes of its prediction
(Fig. 2b). The exception, HR 858 b, missed on all 16 of its accepted transits,
by 355 to 404 minutes against a forecast SD of about 16 minutes. These figures
describe accepted timings. Transits that were not recovered have no error, so
the figures are not a catalogue-wide failure rate.

<!-- claims: C048, C062, C063 -->

### 3.3 Accuracy over four years

The earlier DRC release, public in September 2022, gives a longer view. After
the review, we scored its forecasts against already-inspected timings from
2022–2023 and from 2026, with DRD used only to label transit cycles. Every
accepted planet stayed within 37 minutes in both periods: 92 planets in
2022–2023 and 128 in 2026, reaching nearly four years after issue (Fig. 2c).
Median errors were 1.0 and 1.2 minutes, and no error exceeded an hour. Because
these outcomes had been inspected, this comparison is descriptive, not a
second untouched test.

<!-- claims: C060, C062; D014 -->

### 3.4 Calibration (H1)

Under the reconstructed covariance and the supplied timing likelihoods, M0's
nominal 95% intervals covered 90.8% of accepted timings per planet (Fig. 3b).
The 95% host-bootstrap interval, 87.8–93.4%, excludes 95%: the combined
uncertainties were somewhat too narrow. Pooling events instead gives 92.0%,
and coverage falls short of nominal at every level from 50% to 99%.
Measurement uncertainty is a large part of the combined interval: the
timing SD is a median 1.9 times the forecast SD with planets weighted equally,
and 2.7 times pooling events. Fig. 3a shows the full distribution of the
standardised outcomes.

<!-- claims: C043, C052, C063; D076 -->

### 3.5 The prespecified test (H3)

M2 raised coverage to 97.6%, with intervals 1.67 times wider. Its effect on the
planet-balanced score was −0.12, with a 95% interval of −1.84 to +2.20
(Table 2): by the prespecified rule, inconclusive. The interval spans both
substantial benefit and substantial harm, so the data establish neither, nor
equivalence. Under M2, 111 of 151 planets scored worse, each by a bounded
amount, and 40 scored better. Most of the average gain came from HR 858 b, and
the sign of the contrast reverses when scores are divided by the forecast-only
SD instead (Appendix B). The single-scale M1, whose factor of 9.35 was learned
from DRC's errors, covered 99.3% and scored worst of the four models.

<!-- claims: C043, C046, C052 -->

### 3.6 HR 858 b: a real departure

HR 858 b's 16 accepted timings, in sectors 105–107, arrived 5.9 to 6.7 hours
early, outside every tested model's 95% interval (Fig. 4b). They form a
coherent sequence, with a local period of 3.58395 days against DRD's 3.585266
and a scatter of 4.3 minutes about a line. Two programs that share no code with
our pipeline reproduced all 16 timings from the same light curves, to median
differences of 0.5 and 2.2 minutes. One of them also timed the system's other
planets against published ephemerides [@Bonfanti2025TOI396]: b ran 6.2 to 7.0
hours early, c ran 9.0 to 10.0 hours late, and d was within 13 minutes
(Fig. 4a). Opposite drifts of b and c with d on time are the pattern expected
from mutual perturbations near their 5:3 period ratio, and they argue against
a common clock offset.

These checks share photons with ours, so they cannot exclude every blend or
identity error. In sector 105, the independent timings differed from three
frozen ones by up to 22 minutes. Re-centring those three on the independent
programs' median and doubling their uncertainty left the primary comparison
inconclusive (−0.09; conditional interval −1.88 to +1.12).

<!-- claims: C048, C050, C051, C057, C059 -->

### 3.7 HR 858 b: visible beforehand

Several features of HR 858 b's forecast were visible before DRD was issued.
The planet was new to DRD. Its 16 released input timings, all from space,
spanned 756 days and ended in November 2020, so the forecast extrapolated more
than five years beyond a two-year baseline. They scattered about the issued
line by 2.2 times their quoted errors. Bonfanti et al. had reported
significant TTVs for b and c, with simulated amplitudes up to about five
hours, in a preprint posted a year before DRD [@Bonfanti2025TOI396]. DRD's own
TTV flag follows its detection criterion and was not raised. These are
documented features of one case, not validated predictors.

<!-- claims: C048, C054 -->

### 3.8 Information span (H2)

H2 asked whether the span of historical information behind an ephemeris
predicts its performance beyond its nominal precision. In development data,
the released training span gave a small improvement in predictive score in one
split between hosts. In a chronological split the gain was unstable, so we did
not carry it into the frozen test. The question remains unresolved; the
release-input features in Table 3 make it testable in future releases.

<!-- claims: C010, C015, C054 -->

### 3.9 Measured midpoints and observing cost (H4)

H4 asked what observing time the stated uncertainties cost; we can answer only
part of it. Illustratively, padding each forecast-only 95% window by three
minutes per side contained 94% of accepted mid-times, averaging equally across
planets. Across all intended transits, the padding added 18,618 window-minutes.
This describes measured midpoints and is not advice. It does not measure
full-transit capture, which depends on transit duration and baseline, or
telescope cost; those require durations and records of attempted observations.

<!-- claims: C063; D076 §4 -->

### 3.10 Could the failures have been targeted?

After the review, we asked whether information released with a forecast could
direct wider windows to the planets most likely to miss. The screen flagged
10% of intended planets and padded their windows by 15, 30, 60, 120 or
240 minutes. It compared them with two ways of spending the same minutes
evenly: scaling every window, or padding every window equally. On inspected
DRC-era data, none of six release-file rankings beat both comparators. Even
the best flagged set chosen with hindsight lost to at least one comparator, by
3.7 to 8.8 percentage points of captured midpoints. Hour-scale misses were too
rare in these samples for any allocation to pay; the result applies to this
policy and to measured midpoints.

<!-- claims: C061, C062, C064 -->

### 3.11 The comparison table

Table 3 lists all 156 core planets, including the five without accepted
timings, and is provided in full as a machine-readable table. Each row gives
the issued DRD ephemeris and its uncertainties, the reconstructed covariance
and its provenance, counts of intended and accepted transits by status, error
summaries and coverage. It also gives dated release-input features: input
age, baseline and scatter about the issued line. Unknown values are recorded
as unknown, not as absent, and each row links to the full ledger of intended
transits. A portable package of 499 hash-bound files, including 463 timing
likelihood grids, rescores every accepted event under all four models and
replays the saved scores exactly, so other forecasts can be scored against the
same outcomes.

<!-- claims: C053, C054 -->

## 4. Discussion

For observers, the answer is reassuring, with one important exception. In this
sample, ExoClock's issued forecasts agreed with later measured mid-times to
about a minute at the median and within half an hour for 150 of 151 planets.
The earlier DRC release stayed within 37 minutes up to four years after issue.
One planet missed by six hours. Observers can weigh this as evidence when
choosing margins, but it does not guarantee a safe window, which also depends
on transit duration, baseline and scheduling. Table 3 shows, planet by planet,
where agreement held and where it failed.

The combined 95% intervals covered about 91% of accepted timings, a modest but
clear shortfall. Minute-scale accuracy and undercoverage are compatible: the
forecast windows are only minutes wide, so small absolute differences can fall
outside them. Forecast errors, unmodelled timing variations, measurement error
and our reconstructed covariance can all contribute, and testing their
combination cannot say which is responsible. Published epoch–period
covariances would remove one of these unknowns.

The correction raised coverage by widening intervals, but the interval score
charges for width as well as misses. Most planets paid a small width penalty,
while a few with large misses gained much more. Once a timing lies beyond both
of two fixed intervals, the score difference between them stops growing, so
widening can earn large gains on a far miss without capturing it
(Appendix B). HR 858 b shows this: it supplied most of the mean gain, yet none
of its timings fell inside any tested model's 95% interval, and removing it
reverses the sign of the contrast. In this sample, a uniform tail correction
bought coverage for typical planets at a cost without protecting against the
failure that mattered most. Whether some other correction could do better is
untested.

Our results agree in pattern with earlier comparisons. Shan et al. found
offsets for a minority of archival hot-Jupiter ephemerides
[@Shan2023TESSTimings], and Agol et al. needed to inflate TRAPPIST-1 forecast
uncertainties [@Agol2024TRAPPIST1Forecast]. ExoClock IV's DRD comparison partly
reused its own fit data [@Kokori2026ExoClockIV]. Our test differs in three
ways: it scores one issued release, against later timings measured
independently of the catalogue, over a fixed list of intended transits that
keeps losses visible. Cohorts, horizons and selection differ, so we compare
patterns, not failure rates [@IvshinaWinn2022; @Wang2024PeriodVariation].

HR 858 b was new to the release, with old, scattered inputs and previously
published TTVs. Most of these features can be computed from the release files
themselves (Table 3). Publishing them beside each forecast would let users
judge similar cases for themselves. Whether they predict failure is untested:
one case cannot validate a warning rule, but future releases could test it
prospectively [@Lissauer2024KeplerPeriods].

Our conclusions are conditional in six ways. Only accepted timings are scored,
70% of intended transits, so the rate of missed transits cannot be estimated.
Because each timing is assigned to the nearest DRD cycle before the $P/4$
gate, a transit displaced by more than a quarter period would be rejected, or
attributed to the wrong cycle, rather than scored as a miss. HR 858 b's
six-hour error lies well inside its 21.5-hour quarter period. Coverage depends
on the reconstructed covariance and on measurement likelihoods whose
calibration was qualified on the samples used to tune the rule. The test
covers one release's first year and stars with one DRD-listed planet, which
may host others. Our independent re-timings share photons with the frozen
pipeline, so they test the software, not the data. Finally, a single gross
failure carries most of the score contrast.

The approach is not specific to ExoClock. Fixing forecasts and scoring rules
before inspecting outcomes applies to other ephemeris catalogues, and to
forecasts in other fields, including ecological models [@Brook2000PVA;
@Dietze2018†]. The table and scoring package let future methods, such as a new
correction, a TTV-aware ephemeris or another catalogue's predictions, be scored
against the same outcomes. Interpretation requires the same explicit
assumptions about which transits were observed and accepted.

TESS sectors 74–97 remain unopened by this project. They could support a
separately authorised study of how often issued forecasts fail by hours, on
hosts we have never examined. Such a study needs a fixed cohort, forecasts
issued before the data and qualified recovery and cycle identification, so
that a gross failure is measured rather than lost. For scale, no failures among
180 independent, fully observed hosts would bound the failure rate below
about 2% (exact binomial 95% interval).

<!-- claims: C043, C045, C046, C049, C050, C053, C054, C055, C062, C063; D076, D080 -->

## Display items

**Figure 1.** What is tested. (a) One forecast: the predicted mid-time and its
95% interval, a measured mid-time with its own uncertainty, the
measurement-convolved interval used for scoring, and a full observing window
for contrast. (b) Timeline in two lanes. Observations: DRC issue, development
blocks, sectors 74–97 (never opened), DRD issue on 18 November 2025 and later
TESS exposures. Analyst access: the freeze and authorisation on 8 November
2026, then first access to the later timings. *[planned drawing]*

**Figure 2.** Accuracy of issued forecasts. (a) Absolute errors of 2,185
accepted timings on a logarithmic minute scale, with the pooled median marked.
(b) Each planet's largest accepted error, ranked, with the number of accepted
timings shown; 150 planets lie within 26.4 minutes, and HR 858 b at about
400 minutes. (c) DRC errors against years since issue, for the already-inspected
2022–2023 and 2026 periods. *[planned, from saved tables]*

**Figure 3.** Calibration. (a) Distribution of standardised outcomes under M0
*[diagnostic choice open: Gaussian-surrogate residuals or predictive PIT from
saved likelihood grids]*. (b) Planet-balanced coverage of accepted timings
against nominal central-interval probability for M0 and M2, with conditional
host intervals.

**Figure 4.** HR 858. (a) Observed minus calculated transit times of planets b,
c and d in sectors 105–107 against the published ephemerides of Bonfanti et
al. (2025), from the independent checker, with frozen b timings overlaid.
(b) HR 858 b's released input timings, ending in 2020, the issued DRD line and
its forecast interval, and the 16 accepted 2026 timings; 24 transits were
intended. *[(a) exists; (b) planned]*

**Table 1.** Fate of the 3,103 intended transits in the core cohort.

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

**Table 2.** Headline results. Planet-balanced over 151 planets unless stated;
smaller interval scores are better; coverage is of accepted measured timings
under the measurement-convolved forecast.

| Quantity | M0 (issued) | M2 (tails) |
|---|---:|---:|
| Median absolute error, pooled / equal-planet (min) | 1.11 / 1.31 | — |
| 95th and 99th percentile absolute error (min) | [compute] | — |
| Largest error excluding HR 858 b / HR 858 b (min) | 26.3 / 404 | — |
| 95% coverage | 0.908 | 0.976 |
| Mean 95% width (min) | 10.5 | 17.5 |
| Standardised IS95 | 11.33 | 11.21 |
| IS95 (min) | 106.3 | 97.8 |
| **M2 − M0, standardised IS95** | | **−0.121 [−1.84, 2.20]**, inconclusive |

**Table 3.** The comparison table, one row per core planet (10 rows printed;
all 156 machine-readable; the 28 extension planets in a separate file).
Columns: planet and host; DRD $T_0$, $P$ and their uncertainties; reconstructed
correlation and tier; intended, coverage-qualified and accepted transits;
terminal statuses; median and maximum absolute error; M0 and M2 coverage;
release-input age, baseline and scatter; dated TTV-literature status, with
unknown kept distinct from absent. *[planned build]*

## Appendices (moved from the main text)

- A. Release dating and the DRC timing-table chronology.
- B. Loss scales, the per-planet contrast and influence diagnostics, and the
  bound on interval-score differences.
- C. Declared sensitivities, including the journal-date anchor and the
  sector-105 rescore.
- D. Measurement qualification: injection design, criteria and results.
- E. Development evidence: benchmark reproduction, release transfer and the
  outcome-convention comparison.
- F. Independent timing checks and their adjudication.
- G. The allocation screen and its exact optimum.
- H. The exploratory extension.
- Online figure set: observed-minus-calculated plots for all 151 planets.

## Data availability

Code, results, the claims ledger and the decision log are at
github.com/BWBrook/transit-forecast-audit (code MIT; text, figures and derived
data CC BY-SA 4.0). The ExoClock releases are on OSF under CC BY 4.0
(10.17605/OSF.IO/WNA5E, 10.17605/OSF.IO/P298N, 10.17605/OSF.IO/WPJTN). TESS
SPOC light curves are from MAST [@Ricker2015TESS; @Jenkins2016SPOC]. The
comparison table and scoring package will be deposited on Zenodo with this
snapshot *[DOI on release]*.

## Author contributions and use of AI

Barry W. Brook set the question, required that the later TESS data stay
unopened until the protocol was frozen, authorised access on 8 November 2026
and reviews the final text before release. Claude (Anthropic; Claude Opus 5.5) and Codex
(OpenAI; GPT-6.1-sol, earlier gpt-6 and gpt-5.6-luna) designed and ran the
analyses, wrote the code and drafted the paper, each reviewing the other's
work; GPT-6 Pro (OpenAI) suggested the topic and reviewed an earlier draft.
The full record of roles and the human–AI correspondence are in the
repository. *[expand per AAS LLM policy at journal build]*

## Acknowledgments

We acknowledge TESS observations obtained through MAST at STScI. The NASA
Explorer Program supports TESS work at US institutions; AURA operates STScI
under NASA contract NAS5-26555. We thank the ExoClock contributors.

## References to import (†)

Gardner2023JWST (10.1088/1538-3873/acd1b5); Tinetti2018Ariel
(10.1007/s10686-018-9598-x); Agol2005TTV (10.1111/j.1365-2966.2005.08922.x);
HolmanMurray2005TTV (10.1126/science.1107822); Kovacs2002BLS
(10.1051/0004-6361:20020802); Dietze2018 (10.1073/pnas.1710231115); Nosek2018
(10.1073/pnas.1708274114); DavisonHinkley1997 (10.1017/CBO9780511802843).
