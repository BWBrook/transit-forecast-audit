# Predicted planet transits arrived within minutes, with one six-hour miss

*Research brief · 11 November 2026 · aligned with the reconstructed article
([18_final_draft.md](18_final_draft.md)). Codes in brackets are claim IDs in
the project's claims ledger.*

<!--
Reconstruction brief, Claude (Opus 5.5), 11 November 2026. Rewritten from
docs/brief.md (v0.6.1) to match the step 4 article, following the step 4
principles: plain language, repeated main message, no surplus words. Two A4
pages at most. docs/brief.md is unchanged until Barry promotes this draft.
-->

## In one sentence

Published predictions of when planets pass in front of their stars agreed
with later measurements to minutes; one of 151 tested planets missed by
hours.

## Why it matters

Astronomers study many distant planets during a transit, the few hours in
which the planet crosses the face of its star. Starlight passing through the planet's
atmosphere can reveal what it is made of. Telescopes such as JWST, and the coming European Space Agency
mission Ariel, book their observations from a predicted transit time and a
stated uncertainty. If the uncertainty is too small, the transit can be
missed; if too large, scarce telescope time is spent waiting.

ExoClock, a project that supports Ariel, publishes these predictions in
dated catalogue editions. Each edition is a forecast made before the transits
it predicts. ExoClock's own comparison of its 2025 edition was partly
optimistic: some comparison timings had helped build that edition. Among the
studies we checked, none fixed an edition in advance, measured the later
transits independently and scored its stated uncertainties this way.

## What we did

We tested ExoClock's November 2025 edition against transit mid-times—the
centre of each crossing—measured from later observations by NASA's TESS
satellite.

- **We fixed the main test first.** The code, inputs, forecasts and decision rule
  were locked and fingerprinted before any of the later TESS data were opened
  (C042, C045).
- **We measured the transits ourselves**, with a search that did not start
  from the predicted time. For accepted artificial transits planted in real
  data, our ranges contained the true times at about the stated rate, on the
  same samples used to tune the method (C038).
- **We scored whole forecasts**, rewarding narrow ranges and penalising
  misses, with every planet counted equally.
- **We tested a correction learned only from the previous edition's
  errors**, applied unchanged.

We provide a planet-by-planet table and a package that reproduces the saved
scores for every accepted timing, so anyone can test a better
prediction against the same measurements (C053).

## What we found

**Predictions were accurate to minutes.** We accepted 2,185 timings from
151 of the 156 planned planets. The typical prediction was off by about one minute, and for 150
of the 151 planets every measured transit came within 26.4 minutes of its
prediction (C043, C063). Predictions from the 2022 edition still held within
37 minutes nearly four years later, for every planet we could check (C062).
That comparison, the early/late check below and the targeting check were added
after the data were inspected.

**The combined prediction and measurement ranges were a little too narrow.** A range labelled "95%" should
contain 95% of outcomes. Combined with our measurement uncertainty, these
ranges contained about 91%, averaging equally across planets (C063). Transits that fell outside were more often
early than late, for reasons we have not identified (C065).

**A correction did not clearly help.** Widening the ranges about 1.7-fold raised coverage above 95%, but the overall score did not clearly improve:
the result allows substantial benefit or substantial harm (C043). Of 151 planets, 111 scored worse; most of the average gain came from one planet,
and even the widened ranges never contained its transits (C046, C059).

**One planet missed by six hours.** HR 858 b arrived six hours early on all
16 of its measured transits. Two independently written programs reproduce
this. Its neighbour, planet c, ran nine to ten hours late while planet d was
on time: the pattern expected when neighbouring planets tug on each other, and evidence against a shared clock shift (C048, C050, C051).

**The warning signs were visible, but are unproven.** HR 858 b was new to the
edition, its prediction rested on observations that ended in 2020 and fitted
poorly, and its timing variations had been published a year earlier (C048, C054).
These are good reasons for scrutiny. One case, though, cannot validate a
warning rule. On the inspected 2022-edition forecasts, none of the tested
schemes for giving selected planets wider windows captured more measured
midpoints than both even-spending alternatives: equal extra minutes per
window or equal proportional increases, with the same total time budget
(C061, C064).

## What it means

For nearly every planet tested, an ExoClock prediction agreed with the
measured transit to minutes. The rare exception can be large. Information
that might foreshadow it, such as old input data, a poor fit or published
timing variations, could be printed beside each prediction, and future
editions could test whether it works. Publishing how the uncertainties in a
reference transit time and the interval between transits are linked would
also make these tests more exact. We had to estimate that missing link
(C054, C063).

## What we can and cannot say

- **We scored only transits we could measure:** 70% of those predicted, and
  92% of those TESS was watching at the predicted time (C046). A transit far
  off schedule could be lost or assigned to the wrong orbit, so we cannot
  estimate a catalogue-wide failure rate. These are mid-times, not guarantees
  of capturing a whole transit.
- **It is one test** of one edition over its first year, on stars with one
  planet listed in the tested edition, with one large failure.
- **Our cross-checks re-used the same TESS data**; no new telescope
  observations were made.
- **The wider exploratory sample yielded accepted timings for only five
  planets.** Finding transits on multi-planet stars is not yet validated (C044).
- **One measurement run was repeated** after a file-path fault; every result
  from the first attempt was preserved unchanged (C045).

## The record

Code, results, the claims ledger, reviews and the reviewed correspondence
between the authors are in
[the public repository](https://github.com/BWBrook/transit-forecast-audit).
The planet table and scoring package will be archived with a DOI on release.

*Sources: ExoClock catalogue editions on OSF; NASA TESS data via MAST; HR 858
timing variations from Bonfanti et al. 2025, doi:10.1051/0004-6361/202451300.*

*Barry W. Brook set the question, authorised the opening of the protected
data and reviews release versions. Claude Opus 5.5 (Anthropic) and Codex
GPT-6.1-sol (OpenAI) designed and ran the analyses, each built an independent
timing check, and reviewed each other's work. Claude drafted this brief. Code: MIT. Text: CC BY-SA 4.0.*
