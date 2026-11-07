# Can we trust predicted exoplanet transit times?

*Repository draft, 7 November 2026. Development evidence only. Bracketed claim IDs point to `coordination/claims.md`, shared with the article and agent guide.*

## The short version

Astronomers predict when a planet will cross its star, then book telescope time for that window. We checked those predictions, with their stated error bars, against what the TESS space telescope later saw. The error bars are too small: about one outcome in nine falls outside a range that should miss one in twenty (C018). A correction learned from the previous catalogue edition fixes that on average, but it does not help most individual planets, and our main test of whether it is worth using is inconclusive (C018). Separately, our own method for measuring transit times is accurate for most planets but failed its pre-agreed replication, so the final test waits (C025).

## What we asked

The ExoClock project publishes planets' predicted transit times, orbital periods and uncertainties, in editions called DRB, DRC and DRD. Each edition is a forecast. Do its stated uncertainties describe how wrong it turns out to be? Can a correction learned from the previous edition's errors make the next edition's uncertainties more honest?

ExoClock's team has already checked old predictions, and we reproduced their table exactly for two of three editions (C001). Our contribution, if the work succeeds, is a combination: exact edition files with known release times, independently measured outcomes, a score that penalises ranges both too wide and too narrow, planets of one star treated as related, and a correction tested on unseen data.

## Why it matters

A transit lasts a few hours. A forecast that misses the window wastes a night of telescope time. A range too narrow causes missed transits; one too wide costs observing time.

## What we found about the forecasts (development data)

We scored the DRC edition against 2,324 later timings of 238 planets (C018).

- **The error bars were too small.** Ranges meant to hold 95% of outcomes held 88.4%. A second test, splitting timings by date, gave 89.8% (C018).
- **A correction restored coverage.** Allowing for rare large errors raised coverage to about 95.5% and widened the average range from 10.1 to 16.4 minutes (C018).
- **It is not a clear win.** Our main score combines width and misses. The correction scored better on average, but the plausible improvement runs from large to slightly negative. We call that inconclusive and claim no improvement (C018).
- **Most planets do not benefit.** Only about one planet in four scored better (one in five in the date test). Two stars, TOI-1130 and TOI-125, supplied about 69% and 86% of the average gain in the two tests (C018).
- **The result survives a change of measurements.** We re-measured transit times ourselves for 294 planets and repeated the comparison. With catalogue timings or ours, the correction scored better on average and the answer stayed inconclusive (C026). One falsely timed transit among 3,946 shifted one version of the calculation a lot, which shows how fragile the correction is (C026).

## Measuring outcomes ourselves: not ready

The final test needs transit times measured the same way for every planet. We tested our pipeline by hiding artificial transits in real light curves and checking that it recovered them with honest error bars.

Before each test we wrote down pass marks. Our first version, with a brightness adjustment fitted on 45 inspected stars, failed a test on 120 new stars: its adjustment over-corrected (C025). The unadjusted version passed on the same stars, but only as a side check that could not count. We then ran one pre-agreed replication on 120 further stars. It failed: about one outcome in fourteen fell outside ranges meant to miss one in twenty, and the plausible range for the true hit rate (0.908 to 0.947) fell short of the pre-agreed floor of 0.93 (C025). We changed no pass mark and dropped no star.

Looking afterwards, the method works well for stars where it timed at least four transits, in both tests. The failures come from stars with one to three transits, mostly long-period planets (C025). That is an observation, not yet a rule: it needs its own pre-agreed test on new stars.

## What we do not know

- **Whether the correction helps on new data.** Everything above uses data we inspected while designing the work (C018).
- **Whether the transit-count scope holds up.** We defined it after the replication (C025).
- **How often observations miss.** A catalogue of successful timings cannot count failed attempts (C021).
- **The catalogue's error links.** ExoClock does not publish how its epoch and period errors correlate; we reconstruct this, as a labelled approximation (C004).
- **Bright stars and crowded or long-period systems.** Bright stars were slightly under-covered in both tests, and the rule cannot time transits that arrive more than about an hour off schedule (C024, C025).

## What happens next

1. Codex and Claude review each other's work.
2. We pre-agree and run a test of the narrower scope on new stars, or repair the method.
3. If a measurement rule passes, we freeze the protocol, fingerprinting planets, forecasts, correction, score and code together.
4. Only then do we open TESS data after 18 November 2025: 184 planets on 175 stars and about 3,400 predicted transit chances, scored against DRD (C021, C027).
5. We report the result either way.

## How the work was done

Barry W. Brook leads and reviews every final version. The analysis was done by AI systems, Claude (Anthropic) and Codex (OpenAI); Claude Sonnet 5.5 drafted this brief. Roles are in the article; the correspondence is in `docs/correspondence/`. Code is MIT, text and data CC BY-SA 4.0.
