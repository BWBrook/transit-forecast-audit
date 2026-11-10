# Reconstruction, Step 3b: paragraph abstracts

Working draft, 10 November 2026, by Claude (Opus 5.5), built from the
reconciled section abstracts in `09_section_abstracts.md`. Each section gives
four things:

1. the paragraph framework, one key message per paragraph;
2. a one-sentence summary of each paragraph;
3. a check of order and coverage against the section abstract;
4. each paragraph as an abstract of three or four short sentences.

References in brackets are bibliography keys from `references/references.bib`.
**[add: …]** marks a source still to find and verify against its DOI before it
is cited. Numbers come from the claims ledger.

---

## 1. Introduction (6 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| I1 | Why timing matters | Transits are brief, so observing them depends on predicted mid-times and on the uncertainty users read as a forecast of error. |
| I2 | ExoClock as issued forecasts | ExoClock's numbered releases are dated, public forecasts, which makes them testable. |
| I3 | Why predictions drift | Linear ephemerides drift through propagated period error and fail outright where transit times vary. |
| I4 | What earlier comparisons did | Comparisons with later TESS timings exist but test refitted, archival or partly in-sample predictions. |
| I5 | The missing test | Forecasting practice scores stated uncertainty on outcomes unseen when the test was fixed, and we found no such test of an ephemeris release. |
| I6 | This study | We provide a per-planet table for DRD against later TESS timings and address four questions recorded before access. |

**Order and coverage check.** The order runs from need (I1) to the product
tested (I2), how it fails (I3), what is known (I4), the gap (I5) and our
response (I6). Every item in the section abstract is covered: transit
scheduling, ExoClock's releases, error growth and TTVs, Shan et al. and
ExoClock IV, proper scores and the bounded-search gap, Brook et al. (2000),
the table, and H1–H4.

### Paragraph abstracts

**I1.** Many measurements of exoplanets, including transmission spectra of
their atmospheres, can only be made during a transit lasting a few hours. Observatories schedule
these windows from a predicted mid-time and its uncertainty. Users read that
uncertainty as a forecast of how wrong the prediction may be: too narrow
risks missing the event, too wide wastes scarce time.
[Ricker2015TESS; add: JWST overview, e.g. Gardner et al. 2023 PASP; add:
Ariel mission, Tinetti et al. 2018 Exp. Astron.]

**I2.** ExoClock maintains ephemerides for Ariel's targets and issues them as
numbered, dated releases. DRB appeared in 2021, DRC in 2022 and DRD in
November 2025. Each release fixes, for every planet, a linear ephemeris and
its uncertainties at a known public time. That makes each one an issued
forecast that later observations can test.
[Kokori2022ExoClockI; Kokori2022ExoClockII; Kokori2023ExoClockIII;
Kokori2026ExoClockIV]

**I3.** A linear ephemeris's timing uncertainty grows with the number of
orbits, through the period error and its covariance with the reference epoch.
Real errors can grow faster, because gravitational interactions between
planets make transits arrive early or late (TTVs). Formal period
uncertainties do not capture TTVs, and forecasts have drifted by tens of
minutes even in well-studied systems.
[Deeg2015; KayeAigrain2025; Dragomir2020; Lissauer2020Ephemerides;
Lissauer2024KeplerPeriods; Agol2024TRAPPIST1Forecast; add: TTV theory,
Agol et al. 2005 and Holman & Murray 2005]

**I4.** Several studies have compared predictions with later TESS timings.
Shan et al. found offsets for 31 of 262 hot Jupiters, and large compilations
have refitted hundreds of ephemerides. ExoClock IV compared its releases with
later timings, but its DRD comparison included timings used to build DRD.
These studies locate discrepant planets; none scores a release's stated
uncertainties on data held out from it.
[Shan2023TESSTimings; IvshinaWinn2022; Kokori2026ExoClockIV; Mallonn2019;
Edwards2021ORBYTS; Wang2024PeriodVariation; Ma2025ExoEchoI]

**I5.** Weather and other forecasting fields judge a forecast by proper
scoring rules, which reward accuracy and honest spread together, applied to
outcomes the forecaster could not see. Ecology adopted the same logic early:
fit a model to the first part of a record and test its stated uncertainty on
the rest. In a bounded search, we found no study that froze an issued
ephemeris release, measured later timings independently, and scored them this
way.
[GneitingRaftery2007; GneitingBalabdaouiRaftery2007; Brook2000PVA; add:
near-term ecological forecasting, Dietze et al. 2018 Ecol. Appl.; search
record C019, `docs/sprint1_literature_review.md`]

**I6.** We compare DRD's issued forecasts with TESS transit times measured
after its release, for 156 planets. We provide the comparison as a per-planet
table that records every intended transit's outcome. Before opening those
data we recorded four questions:

- H1: calibration;
- H2: information span;
- H3: transferable correction, the prespecified primary test;
- H4: practical window cost.

Section 2 describes the test, Section 3 its results and Section 4 what they
mean.
[project brief `bc85326`; freeze D065]

---

## 2. Data and Methods (8 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| M1 | Releases and their dates | We treat DRB, DRC and DRD as issued forecasts and date each by its first verified public availability. |
| M2 | Two forecast models | M0 is the issued Gaussian forecast with reconstructed covariance, and M2 widens its tails by an amount learned from DRC's errors. |
| M3 | Cohort and opportunities | The core cohort is 156 planets with 3,103 intended transits after DRD's release, plus an exploratory extension. |
| M4 | Measuring a transit time | A period-constrained search, a per-transit timing fit, nearest-cycle assignment and a fixed acceptance contract turn light curves into accepted timings. |
| M5 | Qualifying the measurement | Artificial transits showed, before access, that the timing uncertainties were calibrated given successful identification. |
| M6 | The freeze | Everything was hashed and the access authorisation recorded before later photometry was opened, and one rerun is disclosed. |
| M7 | Scoring and decision | Forecasts are scored on measured times by a standardised, planet-balanced interval score, and H3 is decided by joint host resampling. |
| M8 | What else is reported, and where | Development evidence and analyses added after external review are labelled and placed in appendices. |

**Order and coverage check.** The order follows the path of a forecast
through the test: what was issued (M1–M2), for whom (M3), how outcomes were
measured and trusted (M4–M5), how the test was fixed (M6), how it was scored
(M7), and what lies outside the primary test (M8). Every item in the section
abstract is covered:

- DRD's release date;
- M0 and its covariance;
- M2 and the 206-planet fit;
- the cohort criteria and 3,103 transits;
- the extension;
- the box search, nearest-cycle assignment, acceptance checks and P/4;
- the artificial-transit coverage;
- the hashes, authorisation and rerun;
- the convolution, standardisation, weighting, conditional interpretation,
  joint resampling and decision rule;
- the analyses added after review.

M1 adds the release-dating detail that the section abstract compressed.

### Paragraph abstracts

**M1.** We use the DRB, DRC and DRD ephemeris files deposited on OSF, treating
each as an issued forecast. Each is dated by its first verified public
availability: 27 October 2021, 27 September 2022 and 18 November 2025. The
first full day after DRD's release, 19 November 2025, opens the evaluation.
Times are BJD_TDB throughout.
[Kokori2022ExoClockII; Kokori2023ExoClockIII; Kokori2026ExoClockIV; OSF
DOIs; Eastman2010; C019]

**M2.** M0 is the issued linear ephemeris, with a Gaussian uncertainty built
from the published epoch and period errors. ExoClock does not publish the
correlation between them, so we reconstruct it from each release's own
timings. M2 inflates M0's variance by a log-normal factor with median one,
which adds tail mass without changing the centre. Its single parameter was
fitted once, on DRC's errors for 206 planets in 2022–early-2024 development
data.
[Deeg2015; KayeAigrain2025; C004, C009; frozen parameters D065]

**M3.** The core cohort is 156 planets:

- one DRD-catalogued planet per star;
- TESS magnitude below 13.5;
- period of 12 days or less;
- no TTV flag at issue.

Together they give 3,103 intended transits from 19 November 2025 in SPOC
two-minute light curves. A 28-planet extension, with longer periods or
several catalogued planets per star, is exploratory and reported in an
appendix. Planets whose TTVs were recognised after issue stay in, because
that difficulty belongs to the forecast.
[Ricker2015TESS; Jenkins2016SPOC; Caldwell2020TESSSPOC; MAST2020TESSSPOCData;
C021; D015]

**M4.** A box least-squares search within ±0.5% of the catalogue period scans
every phase, so the prediction does not centre it. Each transit's mid-time
posterior is then fitted, and the transit is assigned to the nearest DRD
cycle. A fixed contract accepts a timing only if every check passes:

- a valid product;
- reduced χ² ≤ 100;
- no integration warning;
- a supported likelihood;
- an assigned residual within a quarter period (P/4).

[add: Kovács, Zucker & Mazeh 2002 for BLS; Jenkins2016SPOC;
`scripts/acceptance.py`; D061]

**M5.** We qualified the measurement before access by injecting artificial
transits into real development-era light curves and re-measuring them. Two
independent samples passed every prespecified criterion; their nominal 95%
timing intervals covered 94.7% and 95.0% of true times. This shows the timing
uncertainties are calibrated given successful identification, not that every
transit is recovered.
[C038; C022–C025]

**M6.** Before any later photometry was opened, SHA-256 hashes bound the
protocol: 75 files and 780 likelihood grids, covering the code, cohort,
forecasts, fitted correction and decision rule. The human lead authorised
access on 8 November 2026, and that record was committed before any data
were requested. An output-path fault forced one complete rerun of unchanged
code. Every earlier result was preserved, and both attempts are archived.
[add: preregistration practice, e.g. Nosek et al. 2018 PNAS; C041–C042;
D065; C045]

**M7.** Each forecast is convolved with that timing's measurement-error
distribution, Gaussian or tabulated, and scored by the 95% interval score,
which charges for width and penalises misses. Scores are divided by M0's
predictive SD and averaged with each planet weighted equally. H3 is decided
by 2,000 joint resamples of calibration and evaluation stars, each refitting
M2. The difference counts as an improvement only if its interval lies wholly
below zero, and as harm only if wholly above.
[GneitingRaftery2007; add: cluster bootstrap reference, e.g. Davison &
Hinkley 1997; C039; C049]

**M8.** Development evidence that shaped the protocol is summarised in
appendices and was never treated as a held-out test. An external review
prompted further analyses after unblinding:

- re-timing by two independent programs;
- release-input features;
- a screen of window allocations.

These are labelled as post hoc and do not alter the primary decision.
[D014; D071–D076; C050–C064]

---

## 3. Results (9 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| R1 | Who was measured | We accepted 70% of intended transits and 92% of those with enough data, for 151 of 156 planets. |
| R2 | Accuracy, held out | Accepted timings agreed with DRD's predictions to a median of about a minute, and within 26.4 minutes for 150 planets. |
| R3 | Accuracy over four years | DRC's 2022 forecasts stayed within 37 minutes for 128 planets in development data reaching nearly four years. |
| R4 | Calibration (H1) | The combined 95% intervals covered about 91% of accepted timings per planet, a measurable shortfall. |
| R5 | The primary test (H3) | The correction widened intervals and raised coverage, but its effect on the score was inconclusive. |
| R6 | HR 858 b: a real departure | HR 858 b ran six hours early, reproduced independently, with a b/c/d pattern that favours TTVs. |
| R7 | HR 858 b: visible beforehand | Its inputs were old and scattered, and its system's TTVs had been published before DRD. |
| R8 | H2, H4 and targeting | H2 is unresolved, H4 needs data we lack, and no tested allocation of wider windows helped. |
| R9 | The product | Table 3 gives every planet's forecast, outcome status, errors, coverage and input features. |

**Order and coverage check.** The order is sample (R1); then the main message
held out and over a longer horizon (R2–R3); then the uncertainty statements,
H1 and H3 (R4–R5); then the exception and its warning signs (R6–R7); then
the remaining questions (R8); then the deliverable (R9). Every item in the
section abstract is covered, including the illustrative 3-minute pad in R4
and the dependence on loss scale in R5.

### Paragraph abstracts

**R1.** Of 3,103 intended transits, we accepted 2,185 (70%), for 151 of 156
planets (Table 1). Most losses were transits that TESS did not observe well
at the predicted time. Of the 2,369 transits with enough data, 2,181 were
accepted (92%), and four further timings were accepted outside that set. The
five planets with no accepted timing remain in every table.
[C043; C046; C052]

**R2.** The pooled median absolute error was 1.1 minutes; with planets
weighted equally it was 1.3 minutes (Fig. 2a). Every accepted timing of 150
planets fell within 26.4 minutes of its prediction (Fig. 2b). HR 858 b, the
one exception, missed by up to 404 minutes. These figures describe accepted
timings, not a catalogue-wide failure rate.
[C063]

**R3.** DRC's forecasts, issued in September 2022, give a longer view on data
inspected during design. In development blocks reaching nearly four years
after issue, every accepted timing of 128 planets fell within 37 minutes
(Fig. 2c). This is descriptive and not a second untouched test.
[C062; D014]

**R4.** Nominal 95% intervals, combined with measurement error, covered 90.8%
of accepted timings per planet. The interval was 87.8–93.4%, conditional on
the reconstructed covariance and the measurement likelihoods (Fig. 3b). The
residuals' shape against a Gaussian is shown in Fig. 3a. Illustratively,
adding 3 minutes to each side of every forecast window captured 94% of
measured mid-times.
[C043; C063; D076 §4 wording; check: whether Kokori2022ExoClockII's drift
scatter is comparable, as an unverified subagent report suggested]

**R5.** The correction raised coverage to 97.6% with intervals 1.67 times
wider. Its effect on the planet-balanced score was −0.12, with a 95% interval
of −1.84 to +2.20: inconclusive under the prespecified rule (Table 2). In all,
111 of 151 planets scored worse. Most of the average gain came from HR 858 b,
and the sign changes with the loss scale.
[C043; C046; C052]

**R6.** HR 858 b's 16 accepted timings arrived 5.9–6.7 hours early, outside
every model's 95% interval (Fig. 4a). Two further programs, sharing no code
with ours, reproduced the offset from the same light curves. Against
published ephemerides, its neighbour c ran 9–10 hours late while d was on
time. That pattern favours TTVs over a shared clock or measurement error.
[Bonfanti2025TOI396; C050; C051; C057]

**R7.** HR 858 b first appeared in DRD. Its released input timings ended in
2020 and scattered about the issued line by roughly twice their quoted
errors. TTVs in the system had been published a year before DRD. A sector-105
measurement sensitivity leaves the primary verdict inconclusive.
[Bonfanti2025TOI396; C054; C059]

**R8.** H2 remains unresolved: an information-span predictor from development
did not transfer reliably, and the held-out data have one gross miss. H4
needs transit durations and attempted-observation records, so we report only
midpoint containment. We also tested allocating wider windows to 10% of
planets. No allocation, even chosen with hindsight, beat both equal-budget
ways of spreading the time.
[C010; C015; C061; C064]

**R9.** Table 3 lists all 156 planets, including the five without accepted
timings, in a machine-readable version. For each it gives:

- the issued forecast and reconstructed covariance;
- the status of every intended transit;
- timing counts, errors and coverage;
- release-input features with dated sources.

A portable package re-scores every accepted timing exactly.
[C053; C054; add: AAS machine-readable table guidance]

---

## 4. Discussion (7 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| D1 | The answer for users | Within this sample, issued forecasts agreed with later measurements to minutes, with one hours-long failure. |
| D2 | What H1 shows | The combined intervals under-cover, but coverage cannot say whether forecast, measurement or covariance is at fault. |
| D3 | Why widening did not help (H3) | A population correction buys a few large gains with width paid by most planets, so it cannot be clearly better. |
| D4 | Against earlier work | Our patterns agree with earlier comparisons, but cohorts and selection differ, so rates are not comparable. |
| D5 | HR 858 b and curators | The one failure had visible antecedents, which suggests a flag that future releases could test. |
| D6 | Limitations | The test is conditional on acceptance, cycle assignment, the covariance reconstruction, one release, shared photons and one failure. |
| D7 | Beyond this paper | The approach generalises to any issued forecast, and the table and unopened sectors support next steps. |

**Order and coverage check.** The order is the answer (D1); then the two
uncertainty questions (D2–D3); then context (D4); then the exception's
practical lesson (D5); then the limits (D6); then where it leads (D7). Every
item in the section abstract is covered, including all five limitations and
all three next steps.

### Paragraph abstracts

**D1.** For the planets tested, ExoClock's issued forecasts agreed with
measurements made months later to within minutes. One of 151 planets missed
by hours. Observers can weigh this as evidence, though it does not guarantee
a safe window, which also depends on durations and scheduling. The table
shows where agreement failed.
[C063; C062]

**D2.** Coverage of about 91% for nominal 95% intervals is a real departure
under our assumptions. It cannot identify the cause:

- forecast uncertainties that are too small;
- unmodelled timing noise;
- measurement error;
- the reconstructed covariance.

Only the combination is tested, conditional on accepted timings.
[C043; C052; C063; Lissauer2020Ephemerides]

**D3.** Widening every interval charges width to most planets so as to reduce
penalties on a few large misses. Under the interval score, a few planets
therefore decide the average. Here those were HR 858 b and a handful of
others, while 111 of 151 planets lost. Even the widened intervals never
contained HR 858 b, so no uniform rescaling would have caught it.
[GneitingRaftery2007; C049; C046]

**D4.** Shan et al. found offsets in archival ephemerides of mixed age, and
ExoClock IV's DRD comparison partly reused its own fit data. Our test differs
in three ways: a single issued release, later independent measurements, and
a fixed opportunity list. Cohorts, horizons and selection differ, so we
compare patterns, not failure rates.
[Shan2023TESSTimings; Kokori2026ExoClockIV; IvshinaWinn2022;
Wang2024PeriodVariation]

**D5.** HR 858 b had three warning features at issue:

- it was new to the release;
- its inputs were old and scattered;
- its system's TTVs were already published.

Showing such features beside each prediction would cost curators little. One
case cannot validate a warning rule, and development data had too few
failures to train one. Future releases could test such a flag
prospectively.
[Bonfanti2025TOI396; C054; C061; Lissauer2024KeplerPeriods]

**D6.** Only accepted timings are scored. Because nearest-cycle assignment
precedes the P/4 gate, displaced transits can be rejected or aliased by whole
cycles. Coverage depends on the reconstructed covariance and measurement
likelihoods. The test covers one release's first year, stars with one
DRD-listed planet (which may host others), re-timings that share photons,
and a single gross failure.
[C043; C045; C046; C050; D080]

**D7.** Fixing an issued forecast and its test before seeing outcomes applies
to any prediction that states its uncertainty. Examples are other ephemeris
catalogues and ecological forecasts. The table lets new ephemeris methods be
scored on the same outcomes. TESS sectors 74–97, never opened by this
project, could support a separately authorised study of how often forecasts
fail grossly, once recovery and cycle identification are qualified.
[Brook2000PVA; add: Dietze et al. 2018; C055; C053]

---

## References to add or verify before drafting

Each needs DOI verification before it enters the bibliography:

- Gardner et al. 2023 (JWST overview);
- Tinetti et al. 2018 (Ariel);
- Agol et al. 2005 and Holman & Murray 2005 (TTV theory);
- Kovács, Zucker & Mazeh 2002 (BLS);
- Dietze et al. 2018 (ecological forecasting);
- Nosek et al. 2018 (preregistration);
- Davison & Hinkley 1997 (bootstrap);
- AAS machine-readable table guidance.

The ApJS fit note also calls for wider citation of the timing,
orbital-decay and TTV literature, to be chosen while drafting.
