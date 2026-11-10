# Reconstruction, Step 1: working abstract

Working document, 10 November 2026. Not for submission. Claude (Opus 5.5)
drafted it for Barry's first-principles reconstruction of the article. It
follows Barry's framing, given in chat that day: "the product is pitched as the
main goal and the calibration test is support". Numbers come from the claims
ledger (C043, C050, C054, C062, C063). The journal choice (ApJS or AJ) is
deferred.

**Why are you doing this?**
Observers and missions such as JWST and Ariel schedule transits from catalogue
ephemerides and trust their stated uncertainties. Those uncertainties are
routinely refitted but rarely tested against later, independent timings.

**What are your aims or research questions?**
Core: measure, on held-out data, how well one issued ExoClock release predicted
later TESS transit times, and release that comparison as a reusable table.
Sub-aims: test the uncertainties' calibration, test a learned correction, and
characterise failures.

**What hypotheses underpin them?**
- *H1, accuracy.* Linear ephemerides fitted over multi-year baselines stay
  within minutes for most planets, because period error grows only linearly
  over a few hundred orbits.
- *H2, calibration.* Stated uncertainties are too narrow, because linear fits
  omit unmodelled timing noise: TTVs, stellar activity and photometric
  systematics.
- *H3, failures.* Large misses concentrate where the linear model is wrong
  (interacting multi-planet systems) or poorly constrained (new planets with
  sparse or old inputs).
- *H4, correction.* If miscalibration is stable between releases, a tail
  widening learned from the previous release's errors improves the next
  release's forecasts.

**What did you do?**
We froze the protocol, measured 2,185 later TESS transit times without
reference to the forecasts, and scored them against the issued forecasts with
a proper interval score. We then re-timed influential cases independently.

**What did you find?**
The median timing error was 1.1 min, and 150 of 151 planets stayed within
26.4 min. Nominal 95% ranges covered about 91% of timings. The correction's
benefit was inconclusive. HR 858 b ran six hours early.

**What do these results mean?**
- H1 holds strongly.
- H2 holds, but the shortfall is minutes, not hours.
- H4 is neither supported nor refuted.
- H3 is consistent with the evidence but rests on one case: the single failure
  is an interacting system whose inputs were old and scattered.

**What is it good for, and how does it generalise?**
Observers can trust ExoClock windows to minutes. Curators could flag new,
sparse or TTV-affected ephemerides. The table can serve as a benchmark for
future ephemeris methods. Freezing a forecast and then scoring it suits any
published forecast with stated uncertainty.

## Notes for Step 2

- **The long-standing question.** Are published uncertainties honest
  predictions of future error? This has been asked of weather, epidemiology,
  ecology (Brook et al. 2000) and ephemerides (Lissauer et al. 2020, 2024),
  but not tested on an issued transit catalogue against data held out from
  the release.
- **H1 versus Shan et al. 2023.** H1 needs a direct comparison with Shan et
  al.'s 31 offset planets among 262 screened. Our sample is a curated, current
  catalogue, whereas theirs drew on archival ephemerides of mixed age, so
  their offsets should be larger and more frequent.
- **H3 cannot be tested.** One failure supports it only as a description.
  Step 2 should present H3 as a hypothesis for future releases, not a
  finding.
