# Evaluation protocol: retrospective reliability of transit forecasts

**Status:** proposed protocol v0.1, 4 November 2026; not frozen. The development
pilot independently reproduces the DRB/DRC benchmark columns (D020), but this is
not a registration or held-out result. D021–D024 qualify the covariance and
variance-components proposals. **Do not open TESS light curves dated after
2025-11-18 until the protocol is frozen.** Resolve cohort, exact public
availability, outcome lineage and model identifiability first. The sealed
interval is not automatically eligible for strict Track A: absent earlier
verified availability, DRD's conservative issue anchor is 2026-02-11.

The 5 November development review (D030–D033) nominates a stable population
scale mixture and training-span predictor for further testing; neither is frozen.
Resolve numerical posterior summaries, host-aware uncertainty, chronological
validation and exact target coverage first. S100 straddles the availability
boundary; S110 was still in progress at the metadata audit. See
[the review](tranche2_independent_review.md).

## 1. Scientific question and contribution boundary

**Central question:** For a historically defined cohort of transiting planets, how well do previously available ephemerides predict later independent transit mid-times, and how do calibration and precision vary with forecast lead time?

The first paper should assess a clearly specified forecast product. Its purpose is to determine whether uncertainty statements support their intended interpretation and whether a small, prospectively applied correction improves them. Discovering new orbital decay or transit-timing variations (TTVs) is outside the primary scope.

The broad idea already has direct precedents. ExoClock IV, Section V.1 and Table 5, evaluates earlier releases against subsequent TESS timings and explicitly labels the comparison using the newest fitted release as optimistic. **Reproducing that benchmark and identifying a material extension is a mandatory scientific gate.** Do not claim the first retrospective validation of transit ephemerides. See [literature_review.md](literature_review.md) and [ExoClock IV](https://arxiv.org/html/2511.14407v1).

Potential extensions to evaluate, rather than presumed novelties, are:

1. An operational audit using the date a forecast actually became available, separately from the end of its input observations.
2. Lead-time-specific, planet-balanced calibration and sharpness, with uncertainty that respects repeated observations of the same system.
3. A simple recalibration learned entirely from earlier completed forecast–observation pairs and evaluated on later pairs.

Retain only the extensions that survive the literature and data audits. An exact reproduction is an excellent first milestone but does not, by itself, establish a new journal contribution.

## 2. Keep three analyses separate

| Analysis | Forecast and evaluation rule | What it can establish |
|---|---|---|
| **R: published-benchmark reproduction** | Follow the original paper's release, exclusions, dates, weighting and uncertainty convention exactly, documenting unresolved details | Whether this implementation reproduces the reported benchmark |
| **A: audit of issued forecasts** | Freeze a verifiable published/versioned ephemeris; evaluate only events after that forecast became publicly available and after all of its input events | Reliability of predictions that a user could actually have used |
| **B: reconstructed forecasting experiment** | Refit a standard model using inputs demonstrably available by a historical cutoff; evaluate subsequent independent observations | Performance of that specified reconstruction and update policy |

A model fitted to pre-cutoff observations can be evaluated on later observations even if its publication came later still. That is a legitimate temporal validation, but the early test events were not forecasts available to users at the time. Label this distinction rather than treating it as misconduct or automatically invalid analysis.

If individual historical data availability cannot be reconstructed, Track B may instead use observation-date cutoffs. Call it an **observation-cutoff hindcast**, make its information advantage explicit, and keep it separate from the availability-aware analysis. Never silently substitute the current catalogue for a historical snapshot.

## 3. Cohort definition and the unit of analysis

Start with a versioned ExoClock release and an independently recorded set of later TESS observations, subject to the access and provenance findings in [data_sources.md](data_sources.md). A provisional bounded subset is short-period, relatively deep-transit systems; any period, radius or depth threshold must be fixed using historical metadata before examining forecast errors. A hard size cut is optional and should not require reconstructing unnecessary historical parameters.

Define the population in the manuscript as precisely as the available evidence allows: for example, eligible planets from a particular release that have usable independent later TESS timing measurements. This is not automatically representative of all known transiting planets, future Ariel targets or all attempted ground-based observations.

The elementary record is a **forecast–event pair**: one frozen forecast for one physical transit event. The same transit appearing in multiple catalogues or reductions is one event, not several independent outcomes. For each event, choose a timing product by a predeclared provenance/quality hierarchy. Retain alternatives for sensitivity analysis. Combine independent simultaneous measurements only using a defensible shared-event model; do not count a joint timing and its component observations separately.

The primary summary gives each planet equal weight, each eligible forecast origin within a planet equal weight, and each eligible event within an origin/horizon cell equal weight. A transit-weighted summary is secondary and useful for reproducing existing work. For multiplanet systems, uncertainty resampling should cluster at the host-system level when identifiers are available.

### Eligibility rules

- A source version, immutable file hash and identifiable parameter set exist for the forecast.
- Time convention and units are resolved, with BJD_TDB as the internal time coordinate.
- Period, reference epoch and their uncertainties are from the same fit/product.
- The test event is beyond the forecast's training observations and, for Track A, beyond public issuance.
- The outcome uses different exposures from the training data; shared reduction, shape priors or timing priors are recorded.
- Epoch identification is unambiguous without choosing the cycle number to make the residual small.
- Outcome quality can be established independently of the size or sign of the forecast error.

For the primary constant-period scope, known-at-origin TTV status may define an explicit stratum or exclusion. A planet whose TTVs become apparent later remains in its original cohort: that discovery is part of the difficulty faced by a historical prediction. Present-day TTV labels can be shown descriptively but cannot be used to erase forecast failures.

## 4. Reconstruct four dates, not one

Every forecast record needs the following distinct fields, plus evidence for each:

| Field | Meaning |
|---|---|
| `training_end` | End of the latest observation used in producing the ephemeris; record the time convention |
| `available_from_utc` | First verified public availability of these exact parameters: a versioned preprint, release or other documented product |
| `forecast_origin_utc` | Time at which this audit's decision maker issues/uses the frozen forecast; cannot precede availability |
| `retrieved_at_utc` | When this project retrieved the source; this establishes provenance, not historical availability |

An evaluation timing likewise needs event/exposure dates, first availability of the timing or underlying photometry, its present processing version, and contributing exposure identifiers. A 2025 paper reporting a 2019 transit is not an input available in 2019 merely because the transit occurred then. Conversely, a public photometric product might have been available before a later paper reported a timing: that supports a raw-photometry reconstruction only if the reconstruction explicitly performs the measurement.

Report both **operational lead time** (event minus forecast origin) and **extrapolation age** (event minus last training observation). Also retain baseline-normalised age, using the historical training baseline. Do not define lead time from the numerical reference epoch: that epoch is often deliberately placed near the centre of the training data.

Civil availability dates and BJD_TDB event times are different coordinates. Convert them through an explicitly documented timing routine for precise eligibility checks, or exclude events near an uncertain day-level boundary conservatively. Never subtract their numeric representations as though they were identical. Unknown first-public dates are an uncertainty category; journal publication can serve as a conservative verified bound, with the interpretation recorded.

## 5. Freeze source provenance and exclusions

For every included or excluded planet and event, retain source URL/DOI, release/version, file checksum, exact table/row or exposure identifier, retrieval date, parser version and reason codes. Keep raw source fields alongside normalised values. Missing covariance and an ambiguous time standard are explicit states, not zero-valued quantities.

Do not repair an as-issued forecast using later information and then score it as the original. If a unit, transcription or timing error is independently established, retain both the original operational record and the corrected sensitivity analysis. The evidence for the correction must be visible. Residual size alone is not evidence of a bad observation.

Modern software may measure independent post-origin photometry as an evaluation outcome. Its timing parameter must be free to move: an informative prior centred tightly on the old ephemeris would bias the outcome towards the forecast being tested. Shared full-dataset transit-shape estimates and detrending choices require a sensitivity check or separate outcome product. A newly fitted ephemeris using all observations is not a substitute for independently measured future transit times.

## 6. Forecast uncertainties and covariance tiers

For a linear ephemeris, propagate the full covariance of epoch and period; see [statistical_models.md](statistical_models.md). Retain asymmetric errors or posterior samples when needed rather than silently replacing them with an arbitrary Gaussian standard deviation.

Use explicit evidence tiers:

- **C1:** covariance or joint posterior available and its convention verified.
- **C2:** a specific source method establishes approximate decorrelation at the supplied pivot; justify and test the approximation. This is not equivalent to a table merely omitting covariance.
- **C3:** only marginal uncertainties available; report point errors and covariance-sensitivity results, keeping them separate from the primary full-distribution comparison.
- **C4:** uncertainty/time provenance unresolved; exclude from primary probabilistic scoring and count the exclusion.

Track B can generate a covariance through a declared refit. That does not retroactively recover the covariance of a different published fit. For Track A, also distinguish reproducing a publisher's explicitly stated uncertainty convention from auditing a reconstructed full probabilistic model.

## 7. Outcomes and scoring

The observed evaluation time has measurement error. For independent approximately Gaussian uncertainties, compare the observed residual with the square root of **forecast variance plus outcome measurement variance**. Report the source forecast width separately so uncertain outcomes do not masquerade as useful forecasts. Other distributions require numerical convolution or posterior simulation.

Proposed primary audit outputs are:

1. Planet-balanced 68.27% and 95% empirical coverage of the distribution for a measured future timing, overall and by lead-time band.
2. Planet-balanced mean 95% interval score, alongside interval width. The score penalises both excessive width and misses.
3. Signed timing error, median absolute error and selected error quantiles in minutes.

Use the negative logarithmic score as a secondary full-density diagnostic when the adopted density is defensible. Report predicted latent timing uncertainty separately from the uncertainty of the noisy evaluation measurement. Coverage of measured outcomes is not direct proof that nominal intervals contain the unobserved true mid-time at the stated rate.

For reproduction R, the absolute-residual rule with the reported forecast and
measurement variances and 42 DRD flags removed reproduces both DRB/DRC columns
independently. The source does not fully specify that algorithm: retain the
distinction between numerical reproduction and verified author code/event list.
DRD differs by one count and Initial is still open. See D020. These outcomes are
development material; their agreement does not validate the proposed new model.

## 8. Lead-time and covariate analyses

Provisional operational lead-time bands are `(0, 1]`, `(1, 3]`, `(3, 5]` and `>5` years. Change these only using the distribution of eligible metadata, before inspecting outcomes; sparse cells should be displayed as sparse or merged by a recorded rule. Use the same events when comparing methods within a band.

A small secondary analysis can assess whether forecast failure relates to historical training span, extrapolation age divided by that span, or forecast uncertainty relative to transit duration. These covariates must be available at the origin. Do not fit a large post-hoc predictor search to a small number of independent planets. Current-catalogue values and classifications acquired after the origin are explanatory follow-up information, not historical decision features.

Different releases often contain different planets and different eligible outcomes. Compare releases on their intersection before interpreting a change in aggregate performance as an improvement due to the release. Also report each release's own target population so restriction to the intersection is transparent.

## 9. Dependence and uncertainty

Many test transits share the same ephemeris error. Randomly splitting rows or using the number of transits as a binomial sample size would exaggerate independent information. Use paired host-system/planet-cluster resampling for method differences, preserving each system's origins and outcomes together. When there are enough independent observing campaigns, assess sensitivity to shared campaign effects as well.

Report the numbers of systems, planets, origins, unique physical transits, observing campaigns and forecasts in every comparison. Bootstrap uncertainty is conditional on the sampling and target-population assumptions; it does not make an observational convenience sample representative.

For planning intuition only, independent Bernoulli outcomes with 95% coverage give an approximate 95% margin `1.96 sqrt(0.95*0.05/N)`: about 6.0 percentage points at N=50, 4.3 at N=100 and 3.0 at N=200. Repeated correlated transits cannot simply be inserted as N. Use the real cluster structure in simulation to plan the eventual analysis. A 5–10-planet pilot establishes feasibility, not precise tail calibration.

## 10. Recalibration is a separate prospective prediction

The minimum extension is one scale parameter applied to the forecast component of uncertainty, leaving the reported outcome measurement error unchanged. Learn it on completed historical forecast–observation pairs whose outcomes were available by a calibration cutoff. Then freeze it and evaluate only later pairs. Its fitted value and the set of eligible training pairs are part of the forecast record.

Use a chronological outer evaluation block. If selecting between calibration rules or tuning a horizon effect, use earlier chronological inner blocks. All decisions about hyperparameters, quality thresholds and outcome exclusions belong inside that training process. Overlapping origins remain clustered in uncertainty estimates.

A secondary leave-system-out experiment asks whether the correction transfers to previously unseen systems. It estimates a different generalisation target from updating forecasts for already monitored planets; label both. If the available historical span cannot support an honest calibration/evaluation split, retain the audit and defer improvement claims.

The primary improvement contrast should be the paired difference in planet-balanced 95% interval score on the untouched later block, with coverage and width explaining its behaviour. A wider interval alone is not an improvement, and a correction to uncertainty alone does not change point-prediction accuracy.

## 11. Observation selection and scheduling

Successful timing measurements may be selected by the old prediction: a transit outside a narrow observing window can be missed entirely. Even near-continuous space observations have coverage gaps and detection thresholds. Record usable exposures/attempts and non-detections whenever recoverable. Do not code an unobserved event as zero error or as an ordinary missing value with no scientific consequence.

Without the denominator of unsuccessful attempts, the primary estimand is **forecast reliability conditional on a usable later timing being available**. It cannot directly estimate a mission-wide missed-transit rate. If attempting population correction, specify and validate an observation model; inverse-probability weighting needs defensible probabilities and positivity, not just an available covariate table.

Scheduling is ancillary. On held-out observed events, one can calculate whether a hypothetical window would contain the fitted transit, with uncertainty in duration and timing propagated. This is a conditional window-replay exercise. A claim about telescope time saved additionally requires attempted-observation coverage, weather, detectability, duration uncertainty and the allocation policy. Defer those ingredients unless they can be supported without enlarging the first paper substantially.

## 12. Simulation and failure checks

Before a real-data result is interpreted, run simulations with:

- Correct linear ephemerides, full covariance and known observation noise.
- Strong epoch–period covariance and re-pivoted equivalent parameterisations.
- Misstated forecast and/or outcome uncertainties, treated separately.
- Weak curvature and periodic timing deviations, with amplitudes expressed in timing units.
- Campaign-level timing offsets, duplicates and shared-exposure reductions.
- Release delays, late publication of old observations and ambiguous cycle numbering.
- Observing windows that preferentially miss large errors.

Check whether the proposed pipeline recovers the known target metric, whether confidence intervals reflect between-system replication, and when recalibration fails. Synthetic scenarios are methodological stress tests, not evidence that the corresponding astrophysical process exists in the real sample.

## 13. Decision gates and minimum paper

1. **Provenance:** recover immutable forecasts, dates, independent outcomes and uncertainty conventions for a small pilot. If only observation-date cutoffs are possible, narrow the claim to a hindcast.
2. **Reproduction:** recreate the closest existing benchmark or document a precise unresolved obstacle. Resolve definitional differences before comparing numbers.
3. **Novelty:** identify a scientifically consequential extension beyond that benchmark. If none survives, redirect scope rather than claiming novelty from a changed implementation.
4. **Identifiability:** show through simulation that measurement error, covariance and sampling do not make the proposed interpretation untenable.
5. **Freeze:** record cohort, models, scores, folds, exclusions and the analysis commit before unmasking the final evaluation block.
6. **Report:** publish code, provenance, inclusion flow, conditional scope and results for all prespecified primary comparisons, including useful null findings.

The minimum paper can be an operational forecast audit with one bounded, out-of-sample recalibration experiment. It does not need a new dynamical model, a full light-curve reduction framework or a telescope scheduling optimiser.

## 14. Methods references

- Deeg, H. J. (2015). *Period, epoch, and prediction errors of ephemerides from continuous sets of timing measurements.* A&A 578, A17. [DOI](https://doi.org/10.1051/0004-6361/201425368); [author preprint](https://arxiv.org/abs/1503.05368). Motivates careful epoch placement and propagated timing errors; this protocol derives its general covariance formulas directly.
- Eastman, J., Siverd, R., & Gaudi, B. S. (2010). *Achieving Better Than 1 Minute Accuracy in the Heliocentric and Barycentric Julian Dates.* PASP 122, 935. [DOI](https://doi.org/10.1086/655938); [author preprint](https://arxiv.org/abs/1005.4415). Timing standards and barycentric conventions.
- Gneiting, T., & Raftery, A. E. (2007). *Strictly Proper Scoring Rules, Prediction, and Estimation.* JASA 102, 359–378. [DOI](https://doi.org/10.1198/016214506000001437); [author-hosted text](https://sites.stat.washington.edu/people/raftery/Research/PDF/Gneiting2007jasa.pdf). Proper scoring and interval-score definitions.
- Kokori et al. (2026; preprint 2025). *ExoClock Project IV: A Homogeneous Catalog of 620 Updated Exoplanet Ephemerides.* [DOI](https://doi.org/10.3847/1538-4365/ae3238); [version inspected](https://arxiv.org/html/2511.14407v1). Direct precedent to reproduce, especially Section V.1/Table 5.

The equations, cohort choices, dates policy and proposed comparison design above are project proposals. Citations do not imply that these specific decisions are endorsed by the cited authors.
