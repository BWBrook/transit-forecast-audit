# Predicted planet transits arrived within minutes, with one six-hour miss

*Research brief · 12 November 2026 · aligned with the reconstructed article
([18_final_draft.md](18_final_draft.md)). Codes in brackets are claim IDs in
the project's claims ledger.*

<!--
Reconstruction brief, Claude (Opus 5.5), 11–12 November 2026. Rewritten from
docs/brief.md (v0.6.1) to match the step 4 article, cross-checked by Codex
(23_brief_review.md), then trimmed to 1.5 pages around a half-page graphical
abstract (scripts/build_graphical_abstract.py). Two A4 pages at most.
Build: see results/reconstruction_review/brief_check.json, adding
--resource-path=docs/reconstruction. docs/brief.md is unchanged until Barry
promotes this draft.
-->

![](../../results/reconstruction_displays/graphical_abstract.pdf){width=100%}

**In one sentence:** Published predictions of when planets pass in front of their stars agreed
with later measurements to minutes; one of 151 tested planets missed by
hours.

## Why it matters

During a transit, a planet crosses its star. Starlight passing through the
planet's atmosphere can reveal its composition. JWST and the coming Ariel
mission schedule observations from predicted times and uncertainties: too
small, and the transit can be missed; too large, and telescope time is wasted.

ExoClock publishes dated predictions for Ariel. Its own check of the 2025
edition was partly optimistic: some comparison timings had helped build it.
Among the studies we checked, none fixed an edition in advance, measured
later transits independently and scored its uncertainties this way.

## What we did

We measured mid-times, the centre of each crossing, from later NASA TESS data,
locking the main test before access (C042, C045). Accepted artificial transits
fell within our ranges at about the stated rate, on the samples used to tune
the method (C038). We tested a correction learned from the previous edition's
errors. The table and scoring package let anyone test new forecasts against
these accepted timings (C053).

## What we found

**Accurate to minutes.** We accepted 2,185 timings of 151 of the 156 planned
planets. The typical miss was about a minute, and for 150 planets every
accepted timing came within 26.4 minutes of its prediction (C043, C063). The 2022
edition still held within 37 minutes nearly four years on, for every planet
we could check (C062).

**Ranges a little too narrow.** Ranges labelled "95%", combined with our
measurement uncertainty, contained about 91% of accepted timings, averaging equally across
planets (C063). Misses were more often early than late, for reasons we have not
identified (C065).

**A correction did not clearly help.** Widening the ranges 1.7-fold raised
coverage above 95%, but the overall score could have improved or worsened
substantially (C043). Of 151 planets, 111 scored worse; most of the average
gain came from one planet, whose transits even the widened ranges never
contained (C046, C059).

**One six-hour miss.** HR 858 b arrived about six hours early on all 16
accepted timings, as two independently written programs confirm. Against
separate published timetables, its neighbour c ran nine to ten hours late
while d was on time:
the pattern expected when planets tug on each other, and evidence against a
shared clock shift (C048, C050, C051).

**Warning signs, unproven.** HR 858 b was new to the edition, its prediction
rested on poorly fitting observations that ended in 2020, and its timing
variations had been published a year earlier (C048, C054). But one case
cannot validate a warning rule, and on the 2022 edition no tested scheme for
giving selected planets wider windows captured more measured midpoints than
both ways of spreading the same extra time evenly (C061, C064). This test, the four-year comparison and the
early/late check were added after the data had been inspected.

## What it means

For nearly every planet tested, an ExoClock prediction agreed with the
measured transit to minutes, but the rare exception can be large. Warning
information such as old inputs, a poor fit or published timing variations
could be printed beside each prediction and tested in future editions.
Publishing how the uncertainties of a reference transit time and the interval
between transits are linked would make such tests more exact; we had to estimate that link
(C054, C063).

## What we can and cannot say

- **Only accepted timings count:** 70% of those predicted, and 92% of those
  TESS was watching at the predicted time (C046). A transit far off schedule
  could be lost or assigned to the wrong orbit, so no catalogue-wide failure
  rate follows, and a mid-time does not guarantee capturing a whole transit.
- **One test:** one edition over its first year, on stars with one planet
  listed in that edition. The wider sample yielded timings for only five
  planets, and identification on multi-planet stars remains unvalidated (C044). Our
  cross-checks re-used the same TESS data, and one measurement run was
  repeated after a file-path fault, preserving every earlier result (C045).

## The record

Code, results, claims ledger, reviews and author correspondence are in
[the public repository](https://github.com/BWBrook/transit-forecast-audit);
the table and scoring package will get a DOI on release.

*Sources: ExoClock catalogue editions on OSF; NASA TESS data via MAST; HR 858
timing variations from Bonfanti et al. 2025, doi:10.1051/0004-6361/202451300.*

*Barry W. Brook set the question, authorised the opening of the protected
data and reviews release versions. Claude Opus 5.5 (Anthropic) and Codex
GPT-6.1-sol (OpenAI) designed and ran the analyses, each built an independent
timing check, and reviewed each other's work. Claude drafted this brief and
its graphical abstract; Codex cross-checked both. Code: MIT. Text:
CC BY-SA 4.0.*
