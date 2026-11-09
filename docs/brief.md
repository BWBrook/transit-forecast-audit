# Can we trust predicted exoplanet transit times?

*Research brief · 9 November 2026 · repository draft v0.6. Claim IDs refer to the shared claims ledger.*

## The answer

Mostly, and to within minutes. We tested ExoClock's published predictions for 151 planets against 2,185 transits that NASA's TESS satellite later observed and that we measured ourselves. For 150 of the 151 planets, every measured transit fell within 26.4 minutes of its prediction. The typical difference was about one minute (C063).

The quoted uncertainty ranges were slightly too narrow. Counting each planet equally, the "95%" ranges contained 90.8% of measured times (C063). A correction learned from an earlier catalogue edition widened the ranges and brought coverage close to 95%. It did not clearly improve the overall forecast score: the result is inconclusive (C043).

One planet, HR 858 b, was six hours early. Its timings are real, and its neighbour in the same system was hours late (C050). Hints of trouble existed before the prediction was issued. One case, however, cannot show that such hints reliably flag failures in advance.

## Why it matters

A planet crosses its star for only a few hours. Astronomers use predicted transit times to book telescope time, and space missions use them to plan observations. A range that is too narrow risks missing the transit; one that is too wide wastes telescope time. ExoClock, a project set up to support the European Space Agency's Ariel mission, publishes these predictions with uncertainties in catalogue editions.

## How we tested it

We treated each catalogue edition as an issued forecast, and its uncertainties as a claim about future errors.

- **We locked the main test first.** Its code, inputs, forecasts and decision rule were fingerprinted before any TESS data from after the edition's release were opened, with human authorisation (C042, D065).
- **We measured transit times ourselves.** The search used each planet's catalogue period but did not centre on the predicted time. Thousands of artificial transits checked the timing errors (C038).
- **We scored the whole forecast.** The score rewards narrow ranges and penalises misses, with every planet counted equally.
- **We trained the correction only on the past.** It was learned from the previous edition's errors and applied unchanged.
- **We then invited criticism.** An external AI review of the previous draft prompted further checks. They are reported separately from the locked test and did not change its verdict (D071–D076).

## What the results show

**Predictions are accurate to minutes.** Forecasts from the earlier edition, issued in 2022, also stayed within 37 minutes for all 128 planets we could check, up to four years later (C062). These figures cover the transits we could measure. They are not a guaranteed failure rate for the whole catalogue.

**The ranges are a little too narrow.** The shortfall from 95% to about 91% partly reflects our own measurement uncertainty, which is often larger than the forecast's. We cannot say how much of the shortfall belongs to the catalogue alone (C052, C063).

**Widening the ranges does not clearly help.** The correction widened the ranges about 1.7-fold. The score change was −0.12, where negative favours the correction, with a 95% interval from −1.84 to +2.20. That interval allows substantial benefit or harm (C043). Only 40 of 151 planets scored better. Most of the average gain came from HR 858 b, and even the corrected forecasts never contained its transits (C046, C052).

**The one big miss is physical.** Two separate timing programs, sharing no code with the main pipeline, reproduce HR 858 b's six-hour early arrival from the same TESS data (C050, C051). Its sister planet c ran 9–10 hours late, and a third planet, d, was on time. That is the signature of planets tugging on each other. It argues against a clock or software error.

**The warning signs were there, but unproven.** HR 858 b was new to the catalogue edition. Its forecast rested on observations that ended in 2020, which fit the forecast line poorly. Astronomers had published its timing variations a year before the edition appeared (C054). Those are reasonable grounds for scrutiny, but one example does not make a tested warning rule.

**Failures were too rare to target.** We asked whether giving a tenth of planets wider observing windows could capture more transits than spreading the same extra time evenly. In earlier data with no hour-scale misses, no choice of planets did so, even one made with hindsight (C061, C064). So we did not use the untouched TESS data from 2024–2025 to test a warning rule.

## What it means

Observers can rely on these predictions to within minutes for planets like those tested. Whether a few minutes matters depends on the observation, so we do not prescribe a fixed safety margin. Rare large failures do happen. The information that might foreshadow them, such as old input data, a poor fit or published timing variations, could usefully be shown alongside each prediction. Whether it actually predicts failure remains to be tested.

## What we can and cannot say

- **It is one locked test of one edition.** It covers one catalogue edition and one season of TESS observations, with one large failure.
- **Scoring needs a measured transit.** We measured 70% of predicted opportunities, and 92% of those where TESS was observing at the predicted time (C046). A transit that is far off schedule or poorly observed can go unmeasured.
- **The extra checks used the same light.** Independent programs re-analysed the same TESS data; no new telescope observations or pixel-level checks were made.
- **Multi-planet systems remain hard.** An exploratory set with several catalogued planets per star was too small to inform (C044).
- **One measurement run was repeated.** A file-path fault was fixed and the run repeated in full. The repeat preserved every previously completed result (C045).

## The record

The code, compact results, the external review, audits and reviewed correspondence are in [the public repository](https://github.com/BWBrook/transit-forecast-audit). A portable package re-scores every measured transit exactly (C053). Bulk inputs are kept outside Git with recorded hashes.

*Sources: ledger claims C042–C064; Bonfanti et al. 2025, doi:10.1051/0004-6361/202451300; NASA TESS observations via MAST.*

*Barry W. Brook leads the research, authorised the opening of the protected data, commissioned the external review (GPT-6 Pro, OpenAI) and reviews release versions. Claude Opus 5.5 (Anthropic) and Codex GPT-6.1-sol (OpenAI) designed and ran the analyses, each built an independent timing check, and reviewed each other's work. Claude drafted this brief. Code: MIT. Project text: CC BY-SA 4.0.*
