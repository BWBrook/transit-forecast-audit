# Can we trust predicted exoplanet transit times?

*Research brief · 7 November 2026 · inspected development evidence. Claim IDs refer to the shared claims ledger.*

## The result so far

Published transit forecasts miss their quoted ranges more often than expected. A population correction improves average coverage, but we have not shown that it improves the main forecast score. Independent review also overturned a reported failure of our timing method: two analysis errors caused that verdict. The corrected test supports conditional calibration of the unadjusted SPOC method. Identification and numerical-support defects still need repair before the final evaluation (C018, C028–C030).

## Why it matters

A planet crosses its star for only a few hours. Astronomers use predicted transit times to book observations. A range that is too narrow risks a miss; one that is too wide uses extra telescope time. ExoClock publishes these predictions and uncertainties in catalogue editions. Its team has already compared old forecasts with later observations. We reproduced the closest published benchmark for two editions (C001).

Our proposed extension combines verified release dates, probabilistic scores, equal weight for each planet, shared uncertainty for planets of one star, and a correction evaluated on a later block that we have kept unopened.

## What the forecast comparison shows

We scored DRC forecasts against 2,324 later catalogue timings of 238 planets. Ranges intended to cover 95% of outcomes covered 88.4%. The correction raised this to 95.6%, widening the average range from 10.1 to 16.4 minutes (C018).

The main score penalises both wide ranges and misses. Its average change favoured the correction, but the uncertainty includes no improvement. Only about one planet in four scored better; two stars supplied most of the average gain. The correction protects against extreme misses at a cost to many ordinary cases (C018).

Remeasuring the outcomes preserved a negative, inconclusive contrast in matched comparisons using Gaussian timing approximations. Agreement on an inconclusive result does not prove that measurement conventions are interchangeable. One wrongly identified timing shifted a comparison substantially, showing why valid identification matters (C026, C030).

\newpage

## What independent review changed

Our brightness-adjusted timing rule still fails its first confirmation. Its unadjusted secondary passed on that sample, so a follow-up replication tested that fixed rule on 120 further selected hosts.

The original replication report said it failed. Review found that the analysis substituted FFI results after the preferred SPOC product failed and reversed the sides of asymmetric uncertainty ranges when checking coverage. Correcting both on the same measurements, with the same pass marks, gives 100 stars with timed injections. Their timing-error RMS is 1.014 times the quoted uncertainty, and coverage is 95.0%; both pass, as do the other frozen criteria (C028).

The earlier suggestion to restrict the study to stars with four or more transits loses its basis. That count also mixed two artificial injection runs rather than counting physical transits. We retain equal weighting of stars and propose no further replication (C028).

The corrected pass is conditional on finding and timing a transit. It does not establish how often identification fails. A separate small likelihood peak can be lost while the main peak looks Gaussian; existing numerical warnings now stop such a timing being accepted. The changed implementation still needs qualification. The replication was also an adaptive follow-up and reused previously measured photometry for many hosts (C028–C029).

## What happens next

Claude counter-reviews these corrections, then the agents reconcile the evidence. Before a freeze, they must resolve identification, likelihood support, complete attempt records and the supported population. The candidate roster contains 184 planets on 175 stars and about 3,400 predicted opportunities; these are not confirmed successful observations. Five events near metadata boundaries remain unresolved (C021, C030).

Only after a protocol freeze may the protected TESS outcomes after 18 November 2025 be opened. The final result will be reported either way.

*Barry W. Brook leads the research and reviews release versions. Claude Opus 5.5 and OpenAI Codex performed the analyses; Claude Sonnet 5.5 drafted the first products and Codex revised them after independent numerical review. Code: MIT. Project text: CC BY-SA 4.0. Claims and reviewed correspondence are in the repository.*
