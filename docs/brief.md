# Can we trust predicted exoplanet transit times?

*Research brief · 9 November 2026 · held-out result. Claim IDs refer to the shared claims ledger.*

## The answer

Mostly, but not always. We tested ExoClock's published predictions for 151 planets against 2,185 transits that TESS observed after the predictions were issued. The quoted 95% ranges contained 90.8% of the observed transit times, so the ranges are somewhat too narrow. A correction learned from the previous catalogue edition widened them and brought coverage to 97.6%. But the correction did not clearly improve the overall forecast score: the result is inconclusive, with uncertainty spanning both a real gain and a real loss (C043).

The reason is instructive. Most predictions were already good, and the correction cost them a little. A few were wrong by hours, and the correction helped those a lot. One planet, HR 858 b, transited about six hours earlier than predicted, against a quoted uncertainty of 16 minutes. That single planet supplies most of the average gain (C046).

## Why it matters

A planet crosses its star for only a few hours. Astronomers use predicted transit times to book telescope time, and space missions use them to plan observations. A range that is too narrow risks missing the transit; one that is too wide wastes telescope time. ExoClock, a project set up to support the European Space Agency's Ariel mission, publishes these predictions with uncertainties in catalogue editions.

## How we tested it

We treated each catalogue edition as a forecast issued on the day it became public, and we treated its uncertainties as a claim about future errors. We then did four things that together make the test fair.

- **We locked the analysis first.** Every rule, number and line of code was fixed and fingerprinted before we looked at any TESS data from after the latest edition (18 November 2025). Only then did the human lead authorise opening it (C042, D065).
- **We measured transit times ourselves.** A pipeline that never sees the prediction measured each transit, and we checked its own error bars by hiding thousands of artificial transits in real data (C038).
- **We scored the whole forecast.** The score rewards narrow ranges and heavily penalises misses, with every planet counted equally.
- **We trained the correction only on the past.** It was learned from the previous edition's errors and applied unchanged.

## What the results show

**The quoted ranges are a little too narrow.** Nominal 95% ranges contained 90.8% of outcomes, and nominal 68% ranges 61.9%. We saw the same shortfall in earlier editions during development (C043, C018).

**A uniform widening does not clearly pay.** Widening every range by about 1.7 times fixes coverage. Overall, the score changes by −0.12 (negative favours the correction), with a 95% interval from −1.84 to +2.20 (C043). Only 40 of 151 planets score better (C046).

**Rare, large misses decide the average.** A wider range costs each planet a little; a miss costs a lot. Four planets missed badly and gained from the correction. Removing HR 858 alone turns the average against the correction (C046). Across ten alternative settings the average moves either side of zero and is never decisive (C047).

**The large misses are not random.** HR 858 b belongs to a three-planet system in which researchers had already reported transit-timing variations before the latest catalogue edition. It was nonetheless issued a simple straight-line prediction with no timing-variation flag. Its transits arrived on a coherent, drifting schedule, consistent with real timing variations, not a measurement error.

## What it means

For people planning observations, the published ranges are a sound guide for most planets. The main risk is a minority of systems whose transits drift away from a straight-line prediction, often because of gravitational tugs from neighbouring planets. A blanket correction protects against them only by widening every range.

The better route is targeted. Catalogues could flag planets in systems with known timing variations or near-resonant companions, and give those planets wider or non-linear predictions. That is a testable hypothesis for the next catalogue edition: which forecasts can we tell in advance will fail?

## What we can and cannot say

- **It is one test of one edition.** The result covers one catalogue edition and one season of TESS observations.
- **The interval is wide in both directions.** The data cannot exclude a modest benefit or a modest harm from the correction. They do not show that the correction makes no difference.
- **Scoring needs a measured transit.** We measured 70% of predicted opportunities, and 92% of those where TESS was observing at the predicted time (C046). A transit that is far off schedule or poorly observed can go unmeasured.
- **Multi-planet systems remain hard.** A small exploratory set with several catalogued planets per star was too small to inform (C044).
- **One measurement run was repeated.** The first run hit a file-path fault that affected only planets with irregular timing signals. We reran the identical locked command, and an independent check confirmed nothing else changed (C045).

## The record

Everything is public: code, locked package, results, an independent audit by the second AI system, and the reviewed correspondence between the researchers and AI systems (`github.com/BWBrook/transit-forecast-audit`).

*Barry W. Brook leads the research, authorised the opening of the protected data and reviews release versions. Claude Opus 5.5 (Anthropic) and Codex GPT-6.1-sol (OpenAI) designed and ran the analyses and reviewed each other's work. Claude drafted this brief; Codex audited the held-out run and computed the secondary analyses. Code: MIT. Project text: CC BY-SA 4.0.*
