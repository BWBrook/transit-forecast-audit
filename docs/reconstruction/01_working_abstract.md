# Reconstruction, Step 1a: working abstract

Working document, 10 November 2026. Not for submission. Claude (Opus 5.5)
drafted it for Barry's first-principles reconstruction of the article. It
follows Barry's framing, given in chat that day: "the product is pitched as the
main goal and the calibration test is support". Numbers come from the claims
ledger (C043, C050, C054, C062, C063). The journal choice (ApJS or AJ) is
deferred. Codex's 10 November review edits below are proposals for discussion,
not changes to the manuscript. Historical and numerical checks are in
`06_hypotheses_numbers_review.md`.

**Why are you doing this?**
Observers schedule transits from catalogue predictions and their uncertainties.
Refitting those predictions does not itself test how an earlier forecast
performed against later observations.

**What are your aims or research questions?**
Core: measure, on held-out data, how well one issued ExoClock release predicted
later TESS transit times, and release that comparison as a reusable table.
Sub-aims: test the uncertainties' calibration, test a learned correction, and
characterise failures.

**What hypotheses underpin them?**
The following H1–H3 are retrospective organising expectations, not the recorded
pre-access H1–H3. H4 restates the original transferable-calibration question
(then H3); the specific correction comparison was frozen before access.

- *H1, accuracy.* Linear ephemerides fitted over multi-year baselines stay
  useful when periods remain stable. Linear propagation motivates the question
  but does not predict minute-scale errors without the input uncertainty and horizon.
- *H2, calibration.* Unmodelled timing variations or other errors could cause
  undercoverage. Combined forecast-and-measurement coverage tests calibration,
  but cannot identify the cause of a departure.
- *H3, failures; future hypothesis.* Large misses may concentrate where the linear model is wrong
  (interacting multi-planet systems) or poorly constrained (new planets with
  sparse or old inputs).
- *H4, correction.* If miscalibration is stable between releases, a tail
  widening learned from the previous release's errors improves the next
  release's forecasts.

**What did you do?**
We froze measurement, acceptance and the primary correction test before protected
access. Catalogue-period searches yielded 2,185 accepted timings; acceptance
required a quarter-period forecast match. Influential cases were independently re-timed.

**What did you find?**
The pooled median absolute error was 1.1 min; every accepted timing on 150 of
151 planets was within 26.4 min. Combined nominal 95% ranges covered about 91%
per planet. The correction's
benefit was inconclusive. HR 858 b ran six hours early.

**What do these results mean?**
- Minute-scale agreement describes the selected accepted timings.
- Conditional combined coverage is below nominal; its cause is unidentified.
- The prespecified correction comparison is inconclusive.
- One gross-miss case motivates H3 but cannot test a concentration or warning rule.

**What is it good for, and how does it generalise?**
The planned table will let readers inspect forecast errors and compare methods.
The exceptional case suggests features for future investigation, rather than
a validated scheduling or warning rule.

## Notes for the next steps

- **The long-standing question.** Are published uncertainties honest
  predictions of future error? This has been asked of weather, epidemiology,
  ecology (Brook et al. 2000) and ephemerides (Lissauer et al. 2020, 2024).
  Position our fixed issued-release benchmark against ExoClock IV, Shan and
  Agol's later-timing/calibration work; do not claim that this question is untested.
- **H1 versus Shan et al. 2023.** H1 needs a direct comparison with Shan et
  al.'s 31 offset planets among 262 screened. Our sample is a curated, current
  catalogue, whereas theirs drew on archival ephemerides of mixed age. Different
  cohorts, horizons and selection prevent a direct comparison of failure rates.
- **H3 cannot be tested here.** One failure illustrates a possible mechanism.
  Step 2 should present H3 as a hypothesis for future releases, not a
  finding.
