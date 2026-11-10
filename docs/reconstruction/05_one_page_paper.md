# Reconstruction, Step 2: the one-page paper

Working draft, 10 November 2026. Claude (Opus 5.5) wrote the first draft and
Codex reviewed it (commit `b035e05`). Claude then reconciled the two, keeping
Codex's corrections to numbers and scope and restoring plain language and
statements of use. The hypotheses are now the ones recorded before held-out
access (`bc85326`). Numbers come from C010, C015, C043, C046, C050, C054,
C062 and C063. This is not a manuscript revision.

---

## Published transit predictions agreed with later measurements to minutes, with one hours-long miss

**Why.** Many exoplanet observations, including most studies of planetary
atmospheres, are made during transit, the few hours when a planet crosses its
star. Telescope time, including for JWST and ESA's Ariel mission, is booked
from catalogues that predict each transit's mid-time with an uncertainty. A
window too narrow misses the transit; one too wide wastes the telescope.
Catalogues are refitted regularly, but refitting does not test how earlier
predictions, or their stated uncertainties, performed later.

**Aims.** We test how well one published release of ExoClock, a catalogue
built for Ariel, predicted transit times later measured by NASA's TESS
satellite. We provide the comparison as a reusable per-planet table. Before
seeing the outcomes we recorded four questions. Do measured times follow the
stated uncertainty once measurement error is included (H1)? Do planets with
short or patchy histories do worse (H2)? Does a correction learned from the
previous release improve the next (H3, the prespecified primary test)? Do
uncertainty-based windows contain the intended share of transits (H4)?

**Methods.** Before opening any TESS data recorded after ExoClock's DRD
release on 18 November 2025, we froze and fingerprinted the protocol: the cohort,
forecasts, measurement and acceptance rules, correction and scoring. The cohort comprised 156 stars with one catalogued planet
each, offering 3,103 predicted transits.

We searched TESS light curves at the catalogue period without centring on
the predicted time, checked timing errors on artificial transits, and accepted
a timing only within a quarter of an orbital period of its prediction.

The 95% interval score, which rewards narrow intervals and penalises misses,
weighted planets equally; its uncertainty came from resampling stars and
refitting the correction. The
correction widened the forecasts' tails by an amount learned from the errors
of the previous release, DRC (public in 2022). Two independently written
programs re-timed the influential cases.

**Results.** We accepted 2,185 timings for 151 planets: 70% of the intended
transits, and 92% of those with enough TESS data around the predicted time.
The median absolute error was 1.1 minutes. For 150 planets, every accepted
timing fell within 26.4 minutes of its prediction. DRC forecasts, checked on
data used to design the test, stayed within 37 minutes for all 128 planets,
up to nearly four years after issue.

Nominal 95% intervals, combined with measurement uncertainty, covered 90.8%
of timings per planet (95% interval 87.8–93.4%). The correction raised
coverage to 97.6%, with intervals 1.7 times wider. Its effect on the interval
score was inconclusive: −0.12, with a 95% interval of −1.84 to +2.20.

The one large failure was HR 858 b, whose 16 transits arrived 5.9–6.7 hours
early. Independent re-timing of the same TESS data reproduced the offset.
Against published ephemerides, its neighbour HR 858 c ran 9–10 hours late and
HR 858 d was on time, which favours timing variations over a shared clock
error. HR 858 b was new to DRD. Its input timings ended in 2020 and scattered
about the forecast line by roughly twice their quoted errors, and the
system's timing variations had already been published.

**Interpretation.** H1: coverage fell short of 95%, by minutes; the cause is
unidentified. H2 could not be tested: development associations were weak and
unstable, and HR 858 b is one case. H3: the correction gave no clear gain. H4
needs transit durations and attempted-observation records, which we lack. A search
for a rule to target wider windows found no advantage.

**Use.** For the planets tested, predictions were good to minutes, and the
table shows where they were not. Ephemerides like HR 858 b's are candidates for a
flag that future releases could test. The table and a portable scoring package let
others benchmark ephemeris methods on the same outcomes. Freezing a published
forecast and scoring it later suits any prediction that states its
uncertainty.
