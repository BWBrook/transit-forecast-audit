# Reconstruction, Step 2: the one-page paper

Working draft, 10 November 2026, by Claude (Opus 5.5), built from Step 1
(1a–1d). Numbers come from C043, C046, C050, C054, C062 and C063. About 600
words in the body below. Codex revised the draft on 10 November after checking
historical status and numerical wording; this is not a manuscript revision.

---

## Testing published transit predictions: minute-scale agreement and one hours-long miss

**Why.** Many exoplanet observations, including most studies of their atmospheres,
are made during transit, the few hours when a planet crosses its
star. Telescope time, including for JWST and ESA's Ariel mission, is booked
from catalogues that predict each transit's mid-time with an uncertainty. A
window too narrow misses the transit; one too wide wastes the telescope.
Refitting a catalogue does not itself test how its earlier predictions
performed against later, independent observations.

**Aims and expectations.** We test how well one published release of ExoClock,
a catalogue built for Ariel, predicted transit times later measured by NASA's
TESS satellite, and plan a reusable per-planet comparison table. We also
ask whether its uncertainties are calibrated, whether a correction learned
from the previous release improves them, and what marks the failures. The
calibration and transfer questions preceded access; the accuracy summary and
case explanations organise the findings retrospectively. Stable periods motivate
linear prediction, but do not guarantee minute-scale accuracy. Unmodelled
transit-timing variations (TTVs) could impair calibration; one exceptional case
cannot establish where failures concentrate.

**Methods.** Before opening any TESS data recorded after ExoClock's DRD
release (18 November 2025), we froze and fingerprinted the protocol: cohort,
forecasts, measurement rule, correction and scoring. The cohort comprised 156 stars with one catalogued
planet each, offering 3,103 predicted transits. We measured each transit time
from TESS light curves without centring the search on the prediction. Artificial
transits qualified its conditional timing calibration; timings were accepted only within a quarter
of the orbital period of their prediction.

We scored forecasts with the 95% interval score, which rewards narrow
intervals and penalises misses. Each planet counted equally, and uncertainty
came from jointly resampling calibration and evaluation stars and refitting
the correction. The correction widened each forecast's tails by
an amount learned from the errors of the previous release, DRC (public 2022).
Two independently written timing programs re-measured the influential cases.

**Results.** We accepted 2,185 transit times for 151 planets: 70% of all
intended opportunities, and 92% of those with sufficient data around the
predicted time. The pooled median absolute error was 1.1
minutes. For 150 planets, every accepted timing fell within 26.4 minutes of its
prediction. The earlier DRC forecasts, checked on data used to design the
test, stayed within 37 minutes for all 128 selected planets, in inspected
blocks reaching about four years after issue.

Nominal 95% intervals, combined with the measurement uncertainty, covered
90.8% per planet (conditional 95% interval 87.8–93.4%). This depends on
reconstructed covariance and the supplied measurement likelihoods. The correction raised
coverage to 97.6% with intervals 1.7 times wider. Its effect on the interval
score was inconclusive: −0.12, with a 95% interval of −1.84 to +2.20.

The one large failure was HR 858 b, whose 16 transits arrived 5.9–6.7 hours
early. Independent re-timing reproduced the offset. Against published
ephemerides, its neighbour HR 858 c ran 9–10 hours late and HR 858 d was on
time, supporting TTVs over a simple common clock offset. The independent
programs share the same photometry. HR 858 b was new to DRD; its released
input timings ended in 2020 and scattered about the issued line by roughly
twice their quoted errors. The system's TTVs were already published.

**Interpretation.** The selected accepted timings mostly agree to minutes.
Combined coverage is below nominal, without identifying why. The frozen primary
correction test is inconclusive. HR 858 b suggests features worth investigating,
not a validated warning rule. A bounded allocation screen found no advantage
from targeting wider windows under the tested policy.

**Use.** The planned per-planet table will expose the errors, selection and
provenance. It and the portable scoring package will let others test
future ephemeris methods against the same outcomes. Freezing an issued
forecast and scoring it on later data suits any published prediction that
states its uncertainty. These measurements do not establish a catalogue-wide
failure rate or a safe observing window.
