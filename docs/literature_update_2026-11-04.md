# Focused literature and outcome-measurement audit, 4 November 2026

## Decision

Continue, but narrow the proposed contribution to a **prospective,
component-aware audit of an issued ephemeris release**. Retrospective forecast
testing, tests of transit-time uncertainty, extra-scatter terms and
covariance-aware ephemeris propagation all have clear precedents. The defensible
candidate contribution is their combination under a historical information
freeze: calibrate and validate the outcome-timing pipeline on development data,
then distinguish outcome measurement error from issued-forecast error and test
the frozen rule against genuinely later events.

This search found no paper that performs that complete separation for an issued
transit-forecast catalogue and then tests it on a later untouched TESS block.
That is a bounded search result, **not an exhaustive novelty claim**. The live
ADS/Google Scholar citation graphs were not available through the research
interface, ExoClock IV is recent, and keyword searches do not recover every
citing work.

## Prior-art constraints that now apply

### ExoClock IV already performs the closest forecast benchmark

Kokori et al. (2026), ExoClock IV, Section 5.1 and Table 5, compares post-2022
TESS mid-times with DRB and DRC predictions and reports pooled threshold
coverage. It calls TESS a “calibrator” and interprets the DRC result as evidence
about the reliability of the earlier ephemerides. The project therefore cannot
claim the first retrospective evaluation of transit ephemerides, the first use
of TESS as later outcomes, or novelty from reproducing Table 5.

Primary source: [ExoClock IV arXiv v1 full text](https://arxiv.org/html/2511.14407v1),
especially Sections 2, 4 and 5.1; version-of-record DOI
[10.3847/1538-4365/ae3238](https://doi.org/10.3847/1538-4365/ae3238).
The arXiv HTML and the local arXiv TeX source were read at method level; the
version-of-record PDF identity and Table 5 were checked, but its full text was
not independently line-compared throughout.

### Forecast-free checks of TESS timing uncertainties are not new

Ivshina & Winn (2022) fit constant-period models to TESS transit times alone and
compare the resulting chi-square values with their expected distribution. They
interpret the result as validation of their timing-uncertainty assignment. For
the combined TESS-plus-literature fits they impose a 26-second uncertainty floor,
give isolated greater-than-5-sigma points zero weight, and add a per-system
extra-scatter term until chi-square equals its degrees of freedom when needed.
That term explicitly combines possible systematic timing errors and real TTVs;
it does not identify separate measurement and forecast components.

Their outcome construction is also informative: individual transit shapes are
fixed from a phase-folded fit, while transit time and detrending coefficients
remain free; intervals with less than 75% expected cadence coverage and transits
with unusually high photometric MAD are omitted. This is a direct precedent for
a within-TESS repeatability diagnostic and for extra variance, although not for
the proposed prospective decomposition.

Primary source: [Ivshina & Winn (2022) arXiv full text](https://arxiv.org/html/2202.03401),
Sections 3 and 5; DOI
[10.3847/1538-4365/ac545b](https://doi.org/10.3847/1538-4365/ac545b).
The relevant methods and uncertainty discussion were read in full-text HTML.

### Archival-prediction versus TESS comparisons are established

Shan et al. (2023) compare a frozen August 2021 NASA Exoplanet Archive extract
with TOI timings for 262 hot Jupiters, then re-reduce TESS images for the 31
systems selected for discrepant timings. Their light-curve fit uses uniform
priors except for limb darkening and sets photometric uncertainty from the
initial-fit residual standard deviation, without a time-dependent or jitter
term. They report no population calibration that separates TESS mid-time error
from ephemeris error. Their selected 31-system analysis cannot estimate the
population prevalence of forecast failure.

Primary source: [Shan et al. (2023) arXiv v2 full text](https://arxiv.org/html/2111.06678v2),
Sections 2.1–2.2; DOI
[10.3847/1538-4365/aca65f](https://doi.org/10.3847/1538-4365/aca65f).
The methods, selection and uncertainty paragraphs were read in full-text HTML.

### Covariance-aware propagation and shared-shape timing fits are established

Kaye & Aigrain (2025) jointly analyse Kepler/K2 and TESS light curves for 111
systems. They propagate epoch-period covariance and use the higher-S/N
Kepler/K2 data to inform global transit-shape parameters before fitting TESS
times. Their purpose is ephemeris refinement and TTV discovery, rather than a
chronologically issued forecast audit. This constrains any novelty claim based
on covariance propagation or on using a shared shape to time lower-S/N TESS
events.

Primary source: [Kaye & Aigrain (2025), MNRAS full text](https://academic.oup.com/mnras/article/538/4/2283/8093570),
DOI [10.1093/mnras/staf334](https://doi.org/10.1093/mnras/staf334).
The method overview, covariance discussion and selection limitations were read;
the publisher's paginated full text intermittently redirected to an inaccessible
minimal view, so this was not a page-by-page review.

### Injection recovery is the appropriate precedent for timing-error validation

Mitchell et al. (2026) use end-to-end simulated PLATO images with injected
transits, classify prior-limited and low-significance timing fits, and compare
recovered with injected mid-times. They find that timing-uncertainty calibration
depends on fit class. This is a simulation study for PLATO, not an audit of
historical TESS forecasts, but it establishes that injection recovery and
prior-boundary diagnostics are available methods. This project should not claim
to invent validation of mid-time uncertainties.

Primary source: [Mitchell et al. (2026) full text](https://academic.oup.com/mnras/article/550/1/stag1174/8711987),
Sections 4–5; [arXiv:2606.19685](https://arxiv.org/abs/2606.19685); DOI
[10.1093/mnras/stag1174](https://doi.org/10.1093/mnras/stag1174).
The fitting classification, injection-recovery calibration and cadence
sensitivity were read in full-text HTML.

## Outcome-selection and identifiability findings

ExoClock IV's released mid-time catalogue is not an unselected set of attempted
TESS outcomes. Its pipeline:

1. removes photometric 3-sigma outliers and rescales photometric uncertainties
   from normalized residuals;
2. fits only radius ratio, mid-time and detrending parameters in the final MCMC,
   holding the other transit-shape quantities to ECC values (with some
   duration-related quantities adjusted from TESS data);
3. excludes a light curve unless its residual diagnostics, S/N and radius ratio
   pass quality criteria; and
4. excludes it unless its O-C agrees within 3 sigma with other observations at
   a similar time (approximately one month).

The fourth rule is outcome-dependent selection. It conditions the released
catalogue on agreement among nearby timing measurements and will remove some
genuine short-term deviations as well as bad fits. It therefore prevents Table
5 from identifying unconditional forecast coverage or an attempted-observation
miss rate. The likely direction is optimistic coverage if rejected disagreements
also tend to be large residuals from an old forecast, but that direction is not
mathematically guaranteed because the filter is defined against nearby
observations rather than directly against DRB/DRC. The missing denominator and
rejection reasons must be recovered before quantifying the bias.

The paper says that transit mid-time is a free fit parameter, but does not state
the numerical bounds or prior used for it. The released catalogue description
does not establish that a historical ephemeris could not constrain a weak event
through the extraction window, initialization or sampler bounds. The correct
status remains `outcome_prior_unverified` until the actual fitting configuration
or a source-code execution establishes otherwise.

Within-visit residual scatter is useful but is not, by itself, an identified
measurement-error scale. It contains at least:

- formal mid-time error and event-level detrending error;
- short-timescale TTVs and activity/spot-induced shifts;
- cadence and sector/campaign systematics; and
- errors induced by holding a common transit shape fixed.

Conversely, catalogue agreement filtering, selection for usable transits and
common-mode shape bias can make repeatability scatter smaller than absolute
timing error. Thus the current 7–11% inflation estimate is a diagnostic of
conditional repeatability in accepted events, not yet a clean estimate of a
measurement multiplier `a`.

There is also a model-identifiability issue in

`Var(O-C) = a^2 sigma_Tmid^2 + b^2 sigma_pred(h)^2 + tau^2(h)`.

If `a`, `b` and a flexible `tau(h)` are fitted to the same residuals, forecast
variance and horizon-dependent extra variance may be nearly collinear. The
design should first estimate or strongly constrain `a` using injection recovery
and/or genuinely independent duplicate reductions, then compare a small number
of prespecified forecast models (for example, `b` alone versus one additive
extra-variance term). Simulation must show that the available distribution of
forecast horizons and variances can distinguish them.

## Recommended bounded contribution and next gate

The first-paper contribution worth testing is:

> For planets in a historically frozen ExoClock release and conditional on a
> usable later transit timing, does a component-aware uncertainty model trained
> before the evaluation cutoff improve the calibration and proper score of
> issued forecasts on a later untouched TESS era?

Before freezing that protocol:

1. Validate a forecast-independent mid-time pipeline on the already inspected
   2022–2023 development light curves using injected time shifts across S/N,
   cadence, activity and coverage strata. Record prior-boundary and failed-fit
   outcomes rather than retaining only successful timings.
2. Compare a small sample against another reduction of the same exposures.
   Agreement is a pipeline check, not independent observational replication.
3. Recover ExoClock's event-level acceptance/rejection information if possible;
   otherwise define the estimand explicitly as conditional on catalogue
   acceptance and use the project's own frozen pipeline for the untouched era.
4. Use simulations to test whether `b` and the chosen extra-variance term are
   separately recoverable after `a` is constrained. Narrow the model if they are
   not.

No TESS light curve dated after 2025-11-18 was opened or downloaded in this
review.

## Search record and limits

Search date and source freeze: **2026-11-04**. Routes used were the arXiv full
texts, publisher full text where accessible, DOI landing records, the repository
literature/evidence files and exact-title/DOI web searches. The following query
strings were run (minor search-engine punctuation normalization is immaterial):

- `"ExoClock Project IV" citations ephemeris forecast calibration`
- `"ExoClock Project III" cited by transit timing forecast TESS`
- `TESS transit mid-time uncertainty calibration ephemeris uncertainty forecast residual`
- `transit timing measurement uncertainty calibration TESS midtime residual scatter ephemeris`
- `site:arxiv.org Kaye Aigrain 2025 transit ephemerides timing variations Kepler K2 TESS`
- `site:arxiv.org Ivshina Winn 2022 TESS Transit Timing Hundreds Hot Jupiters`
- `site:ui.adsabs.harvard.edu 2026 ExoClock Project IV citations`
- `site:ui.adsabs.harvard.edu 2023 ExoClock Project III citations`
- `"Transit ephemerides and timing variations from Kepler and K2 to TESS"`
- `"ExoClock Project IV" "variance" timing uncertainty`
- exact DOI searches for `10.3847/1538-4365/ac9da4` and
  `10.3847/1538-4365/ae3238`
- `"Following up the Kepler field with PLATO" timing uncertainty injection recovery`

The searches recovered relevant method precedents but no work that both cites
ExoClock III/IV and performs the proposed prospective variance separation.
Because the research interface did not expose a complete live ADS or Google
Scholar citing list, T001 should be recorded as **substantially advanced but not
closed**. Before a manuscript novelty statement, rerun a complete ADS citation
export for bibcodes `2023ApJS..265....4K` and `2026ApJS..283....5K`, screen every
citing title/abstract, and update this dated record.
