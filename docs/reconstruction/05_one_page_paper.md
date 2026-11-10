# Reconstruction, Step 2: the one-page paper

Working draft, 10 November 2026, by Claude (Opus 5.5), built from Step 1
(1a–1d). Numbers come from C043, C046, C050, C054, C062 and C063. About 600
words in the body below.

---

## Published exoplanet transit forecasts are accurate to minutes, with rare hour-scale failures

**Why.** Many exoplanet observations, including most studies of their atmospheres,
are made during transit, the few hours when a planet crosses its
star. Telescope time, including for JWST and ESA's Ariel mission, is booked
from catalogues that predict each transit's mid-time with an uncertainty. A
window too narrow misses the transit; one too wide wastes the telescope.
Catalogues are refitted often, but their predictions are seldom tested against
later, independent observations, and their stated uncertainties almost never.

**Aims and expectations.** We test how well one published release of ExoClock,
a catalogue built for Ariel, predicted transit times later measured by NASA's
TESS satellite, and we release the comparison as a per-planet table. We also
ask whether its uncertainties are calibrated, whether a correction learned
from the previous release improves them, and what marks the failures. Our expectations:

- **H1.** Forecasts would stay within minutes over a few years, because
  period error in a linear ephemeris grows only in proportion to the number
  of orbits.
- **H2.** Stated uncertainties would be too narrow, because linear fits omit
  transit-timing variations (TTVs) and instrumental noise.
- **H3.** Large misses would concentrate in interacting multi-planet systems
  and in planets with sparse or old data.

**Methods.** Before opening any TESS data recorded after ExoClock's DRD
release (18 November 2025), we froze and fingerprinted the protocol: cohort,
forecasts, measurement rule, correction and scoring. The cohort comprised 156 stars with one catalogued
planet each, offering 3,103 predicted transits. We measured each transit time
from TESS light curves without centring the search on the prediction. Artificial
transits qualified the method; timings were accepted only within a quarter
of the orbital period of their prediction.

We scored forecasts with the 95% interval score, which rewards narrow
intervals and penalises misses. Each planet counted equally, and uncertainty
came from resampling stars. The correction widened each forecast's tails by
an amount learned from the errors of the previous release, DRC (public 2022).
Two independently written timing programs re-measured the influential cases.

**Results.** We accepted 2,185 transit times for 151 planets: 70% of all
predicted transits, and 92% of those TESS observed. The median error was 1.1
minutes. For 150 planets, every transit fell within 26.4 minutes of its
prediction. The earlier DRC forecasts, checked on data used to design the
test, stayed within 37 minutes for all 128 planets, up to four
years after issue.

Nominal 95% intervals, combined with the measurement uncertainty, covered
90.8% of timings per planet (95% interval 87.8–93.4%). The correction raised
coverage to 97.6% with intervals 1.7 times wider. Its effect on the interval
score was inconclusive: −0.12, with a 95% interval of −1.84 to +2.20.

The one large failure was HR 858 b, whose 16 transits arrived 5.9–6.7 hours
early. Independent re-timing reproduced the offset. Against published
ephemerides, its neighbour HR 858 c ran 9–10 hours late and HR 858 d was on
time, the signature of TTVs, not of measurement error. HR 858 b was new
to DRD; its input timings ended in 2020 and scattered twice as widely as their
errors allowed, and the system's TTVs were already published.

**Interpretation.** H1 is strongly supported. H2 is supported, but the
shortfall is minutes, and the correction did not clearly help. H3 fits the one failure but cannot be tested
on one case. A search for a warning rule in the earlier data found too few
failures to learn from.

**Use.** Observers can trust ExoClock's windows to within minutes. Curators could flag new, sparse or TTV-affected ephemerides for
review. The per-planet table and a portable scoring package let others test
future ephemeris methods against the same outcomes. Freezing an issued
forecast and scoring it on later data suits any published prediction that
states its uncertainty.
