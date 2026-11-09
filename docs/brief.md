# Can we trust predicted exoplanet transit times?

*Research brief · 9 November 2026 · held-out result. Claim IDs refer to the shared claims ledger.*

> **Under scientific revision (9 November 2026).** Independent light-curve checks support HR 858 b's large timing departure and find its neighbour late, with remaining shape/identification limits. The new work distinguishes measured-time scores from observing capture. This historical brief and its older PDF will be rewritten after scope reconciliation; start with the D071 counter-review and Stage 0 reports in the repository.

## The answer

Most accepted transit times lie within the published ranges, but fewer than their nominal coverage implies. We tested ExoClock's predictions for 151 planets against 2,185 later TESS transits. Giving every planet equal weight, the quoted 95% ranges contained 90.8% of measured times. A correction learned from earlier data widened the ranges and increased coverage to 97.6%. It did not clearly improve the overall forecast score: the result is inconclusive, with uncertainty spanning substantial benefit and harm (C043). The result applies to transits we could measure, not to missed transits.

The score gains are concentrated. Most planets scored worse after correction; a few gained substantially. HR 858 b's measured transits arrived about six hours early, against a quoted uncertainty scale of 16 minutes. That planet supplies most of the average gain (C046, C048).

## Why it matters

A planet crosses its star for only a few hours. Astronomers use predicted transit times to book telescope time, and space missions use them to plan observations. A range that is too narrow risks missing the transit; one that is too wide wastes telescope time. ExoClock, a project set up to support the European Space Agency's Ariel mission, publishes these predictions with uncertainties in catalogue editions.

## How we tested it

We treated each catalogue edition as an issued forecast and its uncertainties as a claim about future errors.

- **We locked the primary test first.** Its code, inputs, forecasts and decision rule were fingerprinted before protected TESS data were opened, with human authorisation. Declared secondary analyses were implemented afterwards under dated conventions (C042, D065, D067).
- **We measured transit times ourselves.** The search used a catalogue period but searched the transit phase without centring on the forecast time. Thousands of artificial transits in real data checked its timing errors, conditional on recovery (C038).
- **We scored the whole forecast.** The score rewards narrow ranges and heavily penalises misses, with every planet counted equally.
- **We trained the correction only on the past.** It was learned from the previous edition's errors and applied unchanged.

## What the results show

**Coverage is below nominal in the measured sample.** Nominal 95% ranges contained 90.8% of outcomes, and nominal 68% ranges 61.9%, with planets weighted equally. Earlier development comparisons also under-covered (C043, C018).

**Wider ranges do not clearly improve the score.** The correction increases mean width about 1.7-fold, rather than multiplying every range by the same factor. The score changes by −0.12 (negative favours the correction), with a 95% interval from −1.84 to +2.20 (C043). Only 40 of 151 planets score better (C046).

**A few planets decide the average.** Removing HR 858 in a diagnostic turns the average against the correction; it stays in the primary test (C046). Ten alternative settings give point averages on either side of zero. Their intervals hold fitted parameters fixed and do not replace the primary uncertainty interval (C047).

**One large miss had a prior warning.** HR 858 b belongs to a system with timing variations published before the catalogue edition. Its coherent measured sequence supports a large departure from the straight-line forecast, but this internal check cannot rule out every measurement or identification error. It had no flag under the catalogue's own detection rule (C048).

## What it means

Published ranges cover most accepted timings, but large departures matter for scheduling. A wider range costs precision and can reduce the penalty for a miss. Both gains and losses between two fixed ranges are finite; this result does not depend on an unlimited possible score gain (C049).

A targeted rule using known timing variations or neighbouring planets is worth testing. This study has not shown that it beats population-wide correction. The next question is which forecasts we can tell in advance will fail.

## What we can and cannot say

- **It is one test of one edition.** The result covers one catalogue edition and one season of TESS observations.
- **The interval is wide in both directions.** Substantial benefit and harm remain possible; the data do not show that the correction makes no difference.
- **Scoring needs a measured transit.** We measured 70% of predicted opportunities, and 92% of those where TESS was observing at the predicted time (C046). A transit that is far off schedule or poorly observed can go unmeasured.
- **Multi-planet systems remain hard.** A small exploratory set with several catalogued planets per star was too small to inform (C044).
- **One measurement run was repeated.** A file-path fault interrupted data products that needed a detailed, non-bell-shaped timing-error description; this does not diagnose physical timing variations. A complete rerun preserved every previously completed window and grid (C045).

## The record

The code, compact results, audits and reviewed correspondence are in [the public repository](https://github.com/BWBrook/transit-forecast-audit). Bulk inputs and likelihood grids are kept outside Git with recorded hashes. This brief summarises that living research record.

*Sources: C043–C049 in the shared ledger; Bonfanti et al., doi:10.1051/0004-6361/202451300; NASA TESS/MAST observations.*

*Barry W. Brook leads the research, authorised the opening of the protected data and reviews release versions. Claude Opus 5.5 (Anthropic) and Codex GPT-6.1-sol (OpenAI) designed and ran the analyses and reviewed each other's work. Claude drafted this brief; Codex audited the held-out run and computed the secondary analyses. Code: MIT. Project text: CC BY-SA 4.0.*
