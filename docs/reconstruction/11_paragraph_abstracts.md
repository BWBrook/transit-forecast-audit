# Reconstruction, Step 3b: paragraph abstracts

Working draft, 10 November 2026, by Claude (Opus 5.5), built from the
reconciled section abstracts in `09_section_abstracts.md`. Each section gives
four things:

1. the paragraph framework, one key message per paragraph;
2. a one-sentence summary of each paragraph;
3. a check of order and coverage against the section abstract;
4. each paragraph as an abstract of three or four short sentences.

Existing references in brackets use keys from `references/references.bib`.
**[add: …]** now marks an identity-checked candidate awaiting later bibliography
import; verified identifiers and claim-level support are in
`13_step3b_reference_checks.md`. The AAS format guide is a website, not a
DOI-bearing paper. Numbers come from the claims ledger.

Codex reviewed this draft on 10 November (`12_step3b_review.md`). Results and
Discussion now have 11 and 8 paragraphs, giving 33 overall; every paragraph
abstract has three or four sentences. These remain reconstruction drafts.

---

## 1. Introduction (6 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| I1 | Why timing matters | Transits are brief, so observing them depends on predicted mid-times and on the uncertainty users read as a forecast of error. |
| I2 | ExoClock as issued forecasts | ExoClock's numbered releases are dated, public forecasts, which makes them testable. |
| I3 | Why predictions drift | Period errors accumulate, and unmodelled timing variations can undermine linear predictions. |
| I4 | What earlier comparisons did | Earlier work tests old forecasts and archival ephemerides, as well as refitting timings; DRD's own comparison partly reuses fit data. |
| I5 | The missing test | Forecasting practice scores stated uncertainty on outcomes unseen when the test was fixed, and we found no such test of an ephemeris release. |
| I6 | This study | We compare DRD with later TESS timings, plan a per-planet table and address four questions recorded before access. |

**Order and coverage check.** The order runs from need (I1) to the product
tested (I2), how it fails (I3), what is known (I4), the gap (I5) and our
response (I6). Every item in the section abstract is covered: transit
scheduling, ExoClock's releases, error growth and TTVs, Shan et al. and
ExoClock IV, proper scores and the bounded-search gap, Brook et al. (2000),
the table, and H1–H4.

### Paragraph abstracts

**I1.** Measurements such as exoplanet transmission spectra require
observations during transits, which often last a few hours. Observatories schedule
these windows from a predicted mid-time and its uncertainty. Users read that
uncertainty as a forecast of how wrong the prediction may be: too narrow
risks missing the event, too wide wastes scarce time.
[add: JWST overview, Gardner et al. 2023 PASP; add:
Ariel mission, Tinetti et al. 2018 Exp. Astron.]

**I2.** ExoClock maintains ephemerides for Ariel's targets and issues them as
numbered, dated releases. DRB appeared in 2021, DRC in 2022 and DRD in
November 2025. Each release fixes, for every planet, a linear ephemeris and
its uncertainties at a known public time. That makes each one an issued
forecast that later observations can test.
[Kokori2022ExoClockI; Kokori2022ExoClockII; Kokori2023ExoClockIII;
Kokori2026ExoClockIV]

**I3.** Period errors accumulate between observations, and epoch–period
covariance determines their propagation.
Gravitational interactions can also shift transits early or late, producing TTVs.
A linear forecast's formal fit errors need not describe these unmodelled shifts.
Observed offsets of tens of minutes motivate testing the uncertainty statements.
[Deeg2015; KayeAigrain2025; Dragomir2020; Lissauer2020Ephemerides;
Lissauer2024KeplerPeriods; Agol2024TRAPPIST1Forecast; add: TTV theory,
Agol et al. 2005 and Holman & Murray 2005]

**I4.** Several studies have compared predictions with later TESS timings.
Shan et al. found offsets for 31 of 262 hot Jupiters.
Large compilations have also refitted hundreds of ephemerides.
ExoClock IV tested older releases against later timings, while its DRD
comparison included timings used to build DRD.
[Shan2023TESSTimings; IvshinaWinn2022; Kokori2026ExoClockIV; Mallonn2019;
Edwards2021ORBYTS; Wang2024PeriodVariation; Ma2025ExoEchoI]

**I5.** Weather and other forecasting fields judge a forecast by proper
scoring rules, which reward accuracy and honest spread together, applied to
outcomes the forecaster could not see. Ecological studies likewise test
predictions against held-back population records. In a bounded search, we found no study that froze an issued
ephemeris release, measured later timings independently, and scored them this
way.
[GneitingRaftery2007; GneitingBalabdaouiRaftery2007; Brook2000PVA; add:
near-term ecological forecasting, Dietze et al. 2018 PNAS; search
record C019, `docs/sprint1_literature_review.md`]

**I6.** We compare issued DRD predictions with later TESS observations for
156 intended planets in a planned per-planet table.
Before access, H1 asked whether uncertainties describe measured times, and
H2 whether historical information span matters beyond nominal precision.
H3, the prespecified primary, asked whether correction from an earlier release
improves the next.
H4 asked what observing-window cost follows from stated uncertainty.
[project brief `bc85326`; freeze D065]

---

## 2. Data and Methods (8 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| M1 | Releases and their dates | We treat DRB, DRC and DRD as issued forecasts and date each by its first verified public availability. |
| M2 | Two forecast models | M0 reconstructs Gaussian uncertainty for the issued ephemeris, and M2 widens its tails using DRC's errors. |
| M3 | Cohort and opportunities | The core cohort is 156 planets with 3,103 intended transits after DRD's release, plus an exploratory extension. |
| M4 | Measuring a transit time | A period-constrained search, a per-transit timing fit, nearest-cycle assignment and a fixed acceptance contract turn light curves into accepted timings. |
| M5 | Qualifying the measurement | Successful artificial-transit injections support conditional timing calibration within the declared margins. |
| M6 | The freeze | The test package was hashed and access authorised before later photometry was opened, with one rerun disclosed. |
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
availability: 27 October 2021, 27 September 2022 and 18 November 2025, in UTC.
Evaluation begins on 19 November 2025, the first full UTC day after DRD's release.
Event times use BJD_TDB; five opportunities near unconverted metadata
boundaries are conservatively excluded.
[Kokori2022ExoClockII; Kokori2023ExoClockIII; Kokori2026ExoClockIV; OSF
DOIs; Eastman2010; C019]

**M2.** M0 uses the issued linear ephemeris, with a Gaussian uncertainty built
from the published epoch and period errors. ExoClock does not publish the
correlation between them, so we reconstruct it from each release's own
timings. M2 inflates M0's variance by a log-normal factor with median one,
which adds tail mass without changing the centre. Its single parameter was
fitted on DRC's errors for 206 planets in 2022–early-2024 development
data.
[Deeg2015; KayeAigrain2025; C004, C009; frozen parameters D065]

**M3.** The 156 core planets have one DRD-listed planet per host, TESS
magnitude below 13.5, periods at most 12 days and no origin TTV flag.
They offer 3,103 intended transits from 19 November 2025 in SPOC two-minute light curves.
The 28-planet extension, with longer periods or several catalogued planets
per host, is exploratory.
Later-recognised TTV systems stay in because they belong to the issued forecast's test.
[Ricker2015TESS; Jenkins2016SPOC; Caldwell2020TESSSPOC; MAST2020TESSSPOCData;
C021; D015]

**M4.** A box least-squares search within ±0.5% of the catalogue period scans
every phase, without centring on the prediction.
Fitted timings are assigned to the nearest DRD cycle, then must lie within
P/4 of that assigned prediction.
Acceptance also requires a valid product, shape-fit reduced χ² ≤ 100,
resolved integration and valid timing/support diagnostics.
These checks do not establish completeness or exclude whole-cycle aliases.

[add: Kovács, Zucker & Mazeh 2002 for BLS; Jenkins2016SPOC;
`scripts/acceptance.py`; `scripts/final_evaluation.py`; D080]

**M5.** Artificial transits injected into development-era light curves tested
conditional timing calibration before protected access.
The amended rule passed the declared criteria on two frozen samples,
with nominal 95% timing coverage of 94.7% and 95.0%.
This supports calibration among successful injections; it does not establish
identification completeness or constitute fresh independent replication of the amended rule.
[C038; D061–D062]

**M6.** Before any later photometry was opened, SHA-256 hashes bound the
protocol: 75 files and 780 likelihood grids, covering the code, cohort,
forecasts, fitted correction and decision rule. The human lead authorised
access on 8 November 2026, and that record was committed before any data
were requested. An output-path fault forced one complete rerun of unchanged
code. Every earlier result was preserved, and both attempts are archived.
[add: preregistration practice, Nosek et al. 2018 PNAS; C042; C045;
D064–D065]

**M7.** Forecasts are convolved with Gaussian or tabulated timing errors and
scored by the 95% interval score, penalising width and misses.
Each event uses M0's predictive SD, measurement error included, as a common
divisor across methods; planet-balanced interpretation conditions on timing and acceptance.
H3 uses 2,000 joint resamples of calibration and evaluation stars, refitting M2.
A 95% interval wholly below zero decides improvement, above zero harm,
and otherwise an inconclusive result.
[GneitingRaftery2007; add: cluster bootstrap reference, e.g. Davison &
Hinkley 1997; C039; C049]

**M8.** Appendices distinguish development evidence from the untouched test.
Post-review additions include independent re-timing, coverage and loss-scale
diagnostics, release-input features and a bounded allocation screen.
These additions are labelled by their timing and preserve the frozen primary decision.
[D014; D071–D076; C050–C064]

---

## 3. Results (11 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| R1 | Who was measured | We accepted 70% of intended transits and 92% of those with enough data, for 151 of 156 planets. |
| R2 | Accuracy, held out | Accepted timings agreed with DRD's predictions to a median of about a minute, and within 26.4 minutes for 150 planets. |
| R3 | Accuracy over four years | A post-review DRC comparison stays within 37 minutes for 128 planets in selected blocks reaching nearly four years. |
| R4 | Calibration (H1) | The combined 95% intervals covered about 91% of accepted timings per planet, a measurable shortfall. |
| R5 | The primary test (H3) | The correction widened intervals and raised coverage, but its effect on the score was inconclusive. |
| R6 | HR 858 b: a real departure | HR 858 b ran six hours early, reproduced independently, with a b/c/d pattern that favours TTVs. |
| R7 | HR 858 b: visible beforehand | Its inputs were old and scattered, and its system's TTVs had been published before DRD. |
| R8 | Information span (H2) | Unstable development transfer leaves the original information-span question unresolved. |
| R9 | Midpoints versus observing capture (H4) | A three-minute padding illustration describes accepted measured midpoints, while operational capture needs other data. |
| R10 | Bounded allocation screen | Within the tested 10% policy and padding grid, hindsight selection failed to beat both equal-budget comparisons. |
| R11 | The planned product | Table 3 will join every intended planet's forecast, status, timing summaries and input features. |

**Order and coverage check.** The order is sample (R1); then the main message
held out and in a post-review longer-horizon comparison (R2–R3); then the uncertainty statements,
H1 and H3 (R4–R5); then the exception and its warning signs (R6–R7); then
the remaining questions and targeting (R8–R10); then the deliverable (R11).
Every item in the section abstract is covered, including the illustrative 3-minute pad in R9
and the dependence on loss scale in R5.

### Paragraph abstracts

**R1.** Of 3,103 intended transits, we accepted 2,185 (70%), for 151 of 156
planets (Table 1).
Among 918 opportunities without accepted timings, 730 lacked qualifying data
at the predicted time.
Of 2,369 coverage-qualified opportunities, 2,181 were accepted (92%);
four further timings were accepted outside that set.
The planned roster table will retain the five planets without accepted timings.
[C043; C046; C052]

**R2.** The pooled median absolute error was 1.1 minutes; with planets
weighted equally it was 1.3 minutes (Fig. 2a). Every accepted timing of 150
planets fell within 26.4 minutes of its prediction (Fig. 2b). HR 858 b, the
one exception, missed by up to 404 minutes. These figures describe accepted
timings, not a catalogue-wide failure rate.
[C063]

**R3.** A post-review comparison of DRC's September 2022 forecasts gives a
longer view on already-inspected outcomes. In selected blocks reaching nearly four years
after issue, every accepted timing of 128 planets fell within 37 minutes
(Fig. 2c). This is descriptive and not a second untouched test.
[C062; D014]

**R4.** Nominal 95% intervals, combined with measurement error, covered 90.8%
of accepted timings per planet.
The conditional 95% host-bootstrap interval was 87.8–93.4%, under the
reconstructed covariance and supplied timing likelihoods (Fig. 3b).
Planned Fig. 3a will use a qualified residual or predictive-PIT diagnostic;
non-Gaussian timings cannot automatically be compared with a normal distribution.
[C043; C063; D076; display-plan diagnostic choice remains open]

**R5.** The correction raised coverage to 97.6% with intervals 1.67 times
wider. Its effect on the planet-balanced score was −0.12, with a 95% interval
of −1.84 to +2.20: inconclusive under the prespecified rule (Table 2). In all,
111 of 151 planets scored worse. Most of the average gain came from HR 858 b,
and the sign changes with the loss scale.
[C043; C046; C052]

**R6.** HR 858 b's 16 accepted timings arrived 5.9–6.7 hours early, outside
every tested model's 95% interval (Fig. 4b).
Two independent programs reproduced b's departure from the same photometry.
A separate check found opposite b/c drift and nearly on-time d,
favouring TTVs over a simple common clock offset (Fig. 4a).
A sector-105 sensitivity also spans zero under conditional fixed-fit
resampling; the frozen primary result is unchanged.
[Bonfanti2025TOI396; C050; C051; C057; C059]

**R7.** HR 858 b first appeared in DRD. Its released input timings ended in
2020 and scattered about the issued line by roughly twice their quoted
errors. TTVs in the system had been published a year before DRD.
These are documented features of one case, not validated predictors.
[Bonfanti2025TOI396; C054]

**R8.** H2 asks whether historical information span predicts performance
beyond nominal precision.
An exploratory development predictor showed an association but did not
transfer reliably across chronological blocks.
The original information-span question therefore remains unresolved.
[C010; C015]

**R9.** Measured-midpoint containment describes one part of H4.
Illustratively, forecast-only 95% midpoint windows padded by three minutes
per side contained 94% of accepted mid-times, averaging equally across planets.
This calculation does not measure full-transit capture or telescope cost.
Those operational outcomes require durations and attempted-observation records.
[C063; D076 §4]

**R10.** The post-review allocation test targeted 10% of intended planets.
Allowed pads were 15, 30, 60, 120 and 240 minutes.
Even hindsight selection could not beat both equal-budget ways of spreading
time evenly.
The result applies to this policy and measured midpoints.
[C061; C064]

**R11.** Planned Table 3 will cover all 156 planets, including five without
accepted timings.
Planet rows will link the full intended-event ledger and summarise issued
forecasts, reconstructed covariance, timing counts, errors and coverage.
Dated input features will retain explicit unknowns and nulls.
The existing portable package replays the saved accepted-event scores exactly.
[C053; C054; add: AAS machine-readable table guidance]

---

## 4. Discussion (8 paragraphs)

### Framework and one-sentence summaries

| ¶ | Key message | One-sentence summary |
|---|---|---|
| D1 | The answer for users | Within this sample, issued forecasts agreed with later measurements to minutes, with one hours-long failure. |
| D2 | What H1 shows | The combined intervals under-cover, but coverage cannot say whether forecast, measurement or covariance is at fault. |
| D3 | Uneven score changes (H3) | The correction's mean gain is concentrated in a few planets while 111 worsen; benefit remains inconclusive. |
| D4 | Against earlier work | Our patterns agree with earlier comparisons, but cohorts and selection differ, so rates are not comparable. |
| D5 | HR 858 b and curators | The one failure had visible antecedents, which suggests a flag that future releases could test. |
| D6 | Limitations | The test is conditional on acceptance, cycle assignment, the covariance reconstruction, one release, shared photons and one failure. |
| D7 | Benchmark reuse | The planned table and scoring package let other methods be compared under explicit observation and selection assumptions. |
| D8 | A possible later data study | Unopened sectors could support a separately authorised gross-failure study with an appropriate forecast origin and qualified recovery. |

**Order and coverage check.** The order is the answer (D1); then the two
uncertainty questions (D2–D3); then context (D4); then the exception's
practical lesson (D5); then the limits (D6); benchmark reuse (D7); and a
possible later data study (D8). Every
item in the section abstract is covered, including all five limitations and
all three next steps.

### Paragraph abstracts

**D1.** For accepted timings, ExoClock's issued forecasts mostly agreed with
later measurements to minutes. One of 151 tested planets missed
by hours. Observers can weigh this as evidence, though it does not guarantee
a safe window, which also depends on durations and scheduling. The table
shows where agreement failed.
[C063; C062]

**D2.** Combined nominal 95% intervals covered about 91% of accepted timings
under the reconstructed covariance and measurement model.
Forecast errors, unmodelled timing variations, measurement error and covariance
assumptions can all contribute.
Testing this combination does not identify which component causes the shortfall.
[C043; C052; C063; Lissauer2020Ephemerides]

**D3.** The correction imposed larger width penalties on most planets but
reduced miss penalties for a few.
HR 858 b dominated the mean gain, and removing it changed the sign.
Overall, 111 of 151 planets scored worse.
None of the tested models contained HR 858 b's timings within its 95% intervals.
[GneitingRaftery2007; C049; C046]

**D4.** Shan et al. found offsets in archival ephemerides of mixed age, and
ExoClock IV's DRD comparison partly reused its own fit data. Our test differs
in three ways: a single issued release, later independent measurements, and
a fixed opportunity list. Cohorts, horizons and selection differ, so we
compare patterns, not failure rates.
[Shan2023TESSTimings; Kokori2026ExoClockIV; IvshinaWinn2022;
Wang2024PeriodVariation]

**D5.** HR 858 b was new to the release, with old, scattered inputs and
previously published TTVs.
Showing these features beside forecasts is a candidate curation strategy,
not a validated warning rule.
We did not establish their predictive value.
Future releases could test them prospectively.
[Bonfanti2025TOI396; C054; C061; Lissauer2024KeplerPeriods]

**D6.** Only accepted timings are scored. Because nearest-cycle assignment
precedes the P/4 gate, displaced transits can be rejected or aliased by whole
cycles. Coverage depends on the reconstructed covariance and measurement
likelihoods. The test covers one release's first year, stars with one
DRD-listed planet (which may host others), re-timings that share photons,
and a single gross failure.
[C043; C045; C046; C050; D080]

**D7.** Fixing forecasts and tests before inspecting outcomes also applies to
other ephemeris catalogues and ecological models.
Interpretation requires explicit observation and selection assumptions.
The planned table and existing scoring package let future methods be
compared against the same outcomes.
[Brook2000PVA; add: Dietze et al. 2018; C053]

**D8.** TESS sectors 74–97 remain unopened by this project.
They could support a separately authorised study of how often forecasts fail grossly.
Such a study needs a fixed cohort, genuinely prior forecasts, and qualified
recovery and cycle identification.
[C055; D073–D076]

---

## Verified reference candidates for later import

The eight DOI-bearing works below have verified identities and supporting
source passages; details and limits are in `13_step3b_reference_checks.md`.
The bibliography remains frozen, so no entry is imported here.

- Gardner et al. 2023, JWST: `10.1088/1538-3873/acd1b5`;
- Tinetti et al. 2018, Ariel: `10.1007/s10686-018-9598-x`;
- Agol et al. 2005, TTV theory: `10.1111/j.1365-2966.2005.08922.x`;
- Holman & Murray 2005, TTV theory: `10.1126/science.1107822`;
- Kovács, Zucker & Mazeh 2002, BLS: `10.1051/0004-6361:20020802`;
- Dietze et al. 2018, ecological forecasting, **PNAS**: `10.1073/pnas.1710231115`;
- Nosek et al. 2018, preregistration: `10.1073/pnas.1708274114`;
- Davison & Hinkley 1997, bootstrap: `10.1017/CBO9780511802843`.

The [AAS Data Guide](https://journals.aas.org/data-guide/) is a dated production
link, with no DOI verified for the page. It is not evidence that Table 3
already exists. The bootstrap source supports dependence-aware resampling in
general; our exact joint host-refit procedure is specified by the protocol.
Mission examples, preregistration context and broad forecasting analogies are
optional; method and mechanism attribution should remain focused.

The proposed comparison with ExoClock II's drift scatter remains unverified
and is omitted from the paragraph claims unless its definition is checked.
