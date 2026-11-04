# Heavy-tailed transit-forecast literature audit, 5 November 2026

## Decision on D029

D029 remains worth a prospective test, but its defensible novelty is narrower
than “heavy-tailed transit timing” or “a scale-mixture model.” Robust heavy-tailed
likelihoods, fitted uncertainty scales, outlier mixtures and excess-scatter terms
already occur in transit photometry and transit-timing inference. The candidate
contribution is instead a **historically trained, planet-level calibration of an
issued catalogue's predictive covariance, evaluated with proper scores on a
later untouched block**.

The present search found no published study that performs that complete task.
This is a bounded result, not a final novelty claim: T001's complete ExoClock
III/IV citing-paper screen remains outstanding.

## Three literatures that must remain distinct

| Literature | Existing method | Inferential target | Consequence for D029 |
|---|---|---|---|
| Photometric/light-curve robustness | Heavy-tailed or mixture noise, clipping, Gaussian processes, jitter and robust detrending | Flux-level contamination and uncertainty in a fitted transit | Establishes robust fitting as prior art; it does not calibrate forecast failure between planets |
| Transit-time/TTV robustness | Student-t timing likelihoods, uncertainty-scale parameters, extra scatter and removal/downweighting of timing outliers | Dynamical or linear-ephemeris parameters conditional on observed timings | Establishes heavy-tailed timing residuals and scale inflation as prior art; it usually absorbs measurement error, stellar activity, model misspecification and dynamics together |
| Catalogue forecast calibration | Issued ephemeris distribution scored against later outcomes, with between-planet heterogeneity learned before evaluation | Predictive reliability for a future measured transit | ExoClock IV supplies a Gaussian threshold benchmark, but the searched literature did not supply D029's hierarchical heavy-tailed prospective calibration |

## Closest primary sources

### Student-t transit-time likelihood: Agol et al. (2021)

Agol et al. found many more large normalized residuals than expected under
Gaussian reported timing errors in 447 TRAPPIST-1 transit times. They fitted a
Student-t likelihood with a free width multiplier and degrees of freedom while
inferring an N-body timing model. They explicitly discuss instrumental
systematics, correlated stellar variability, flares and spots as possible causes.

This is close statistical prior art. A Student-t distribution is itself a
Gaussian scale mixture, so neither “heavy tails” nor “mixing over variance” is
new here. The scientific unit and estimand differ: Agol et al. robustify
event-level residuals within one seven-planet system to infer dynamics; D029
models persistent between-planet miscalibration of issued forecast covariance
and proposes an untouched forecast test.

Source read: Sections 2–4 of
[Agol et al. (2021)](https://arxiv.org/html/2010.01074),
*The Planetary Science Journal* 2:1,
[DOI 10.3847/PSJ/abd022](https://doi.org/10.3847/PSJ/abd022).

### Outlier sensitivity in TTV inversion: Jontof-Hutter et al. (2016)

Jontof-Hutter et al. use a Gaussian timing likelihood for their adopted
dynamical inversions, then repeat the analysis with a Student-t likelihood with
two degrees of freedom and with independently measured timing sets. The paper
is an important precursor to Agol et al.'s robust likelihood, but it is a
robustness analysis of parameter inference rather than a calibrated predictive
distribution for an issued ephemeris catalogue.

Source read: methods, likelihood and robustness tests in
[Jontof-Hutter et al. (2016)](https://doi.org/10.3847/0004-637X/820/1/39),
*ApJ* 820:39, DOI `10.3847/0004-637X/820/1/39`.

### TESS timing extra scatter: Ivshina & Winn (2022)

Ivshina & Winn compare TESS-only timing residuals with the nominal chi-square
distribution. In combined TESS-plus-literature fits they impose a 26-second
timing-error floor, assign zero weight to isolated residuals beyond five sigma,
and add a per-system extra-scatter term until chi-square equals its degrees of
freedom. They describe that term as systematic timing error or real TTV
scatter; it does not separate those sources and is not trained as a
transferable forecast distribution.

Source read: Sections V.1–V.2 and the associated timing-residual methods in
[Ivshina & Winn (2022)](https://arxiv.org/html/2202.03401),
DOI [10.3847/1538-4365/ac545b](https://doi.org/10.3847/1538-4365/ac545b).

### Non-Gaussian mixture at the flux-detection layer: Robnik & Seljak (2021)

Robnik & Seljak model isolated non-Gaussian Kepler flux outliers with a mixture
of a Gaussian and a non-central Student-t component, then Gaussianize them while
preserving temporally correlated transit-shaped signals. This is strong prior
art for mixture noise in transit detection. Its observational unit is a flux
sample, and its purpose is detection under non-Gaussian photometric noise. It
does not model the cross-planet distribution of issued ephemeris error.

Source read: likelihood and Gaussianization method in
[Robnik & Seljak (2021)](https://academic.oup.com/mnras/article/504/4/5829/6253227),
*MNRAS* 504:5829–5839,
DOI `10.1093/mnras/stab1178`.

### Existing forecast benchmark: ExoClock IV

ExoClock IV Table 5 pools normalized old-forecast residuals and reports the
fractions inside one to four nominal standard deviations. It therefore exposes
non-Gaussian coverage, but does not fit a hierarchical predictive distribution,
separate typical scale from between-planet heterogeneity, use proper scores, or
evaluate a recalibration learned before the scored era. Its outcome catalogue is
also conditioned by quality and neighbour-agreement filters.

Source read: Sections 2 and 5.1 of
[Kokori et al. (2026)](https://arxiv.org/html/2511.14407v1),
DOI [10.3847/1538-4365/ae3238](https://doi.org/10.3847/1538-4365/ae3238).

## Implications for the proposed lognormal scale mixture

The lognormal mixing distribution is a modelling choice, not an astrophysically
established error law. Agol et al.'s Student-t model corresponds to a different
variance-mixing distribution. With DRC's fitted heterogeneity as large as
`s = 3.13`, tail probabilities and log scores can depend strongly on this choice.
The development analysis should therefore compare, before unsealing:

1. the Gaussian as issued;
2. one common scale multiplier;
3. the proposed lognormal planet-scale mixture; and
4. one prespecified alternative heavy-tail family, preferably Student-t or its
   inverse-gamma variance mixture.

This is a distributional sensitivity analysis, not a license to select whichever
family performs best on the sealed outcomes. The family, parameter estimation,
metadata predictors and scoring rules must be frozen first.

The prospective prediction also needs a precise unit. A development posterior
`lambda_p` inferred from that planet's later residuals cannot be used as if it
were available at forecast issue. For a planet without pre-origin forecast-error
history, the valid prediction is the population mixture conditional only on
issue-time metadata. For a previously evaluated planet, a planet-specific update
is permissible only from outcomes available before the new forecast origin and
answers a different, repeated-system estimand. These two targets should not be
pooled silently.

The threshold `P(lambda_p > 10)` is interpretable as a tail diagnostic for a
tenfold covariance multiplier under this particular model, but it is not
invariant across mixing families. The primary prospective comparison should
remain a proper score and calibration/sharpness display. Tail-event rates can
be secondary, with thresholds defined on directly observable forecast errors
or interval failures where possible.

## Defensible statement and next gate

A supportable provisional claim is:

> Existing transit-timing analyses use robust or heavy-tailed likelihoods to
> protect physical inference from timing outliers. We test a distinct use:
> whether historically estimated between-planet heterogeneity in issued
> ephemeris covariance improves probabilistic forecasts for a later untouched
> block of measured transits.

Before D029 is frozen, demonstrate on development data and simulation that:

- the result is not an artefact of the lognormal mixing family;
- the population mixture generates calibrated predictions for held-out planets,
  rather than merely fitting extreme residuals;
- optional metadata predictors are few, issue-time available and evaluated by
  an earlier chronological or leave-planet-out procedure;
- calibration gains are accompanied by their loss of sharpness; and
- the outcome-selection boundary remains explicit: reliability is conditional
  on a usable timing unless failed or missed events are enumerated.

## Search record and limits

Search date: **2026-11-05**. Sources were primary papers or official article
records; methods were read beyond snippets for the decisive comparisons. No
protected light curve or sealed outcome was opened.

Queries:

- `exoplanet transit timing Student-t likelihood outliers ephemeris`
- `transit timing variations Student t distribution likelihood robust outliers`
- `exoplanet ephemeris Gaussian mixture outlier model transit times`
- `transit ephemeris hierarchical calibration forecast uncertainty mixture model`
- `Jontof-Hutter 2016 ApJ 820 39 Student t transit timing likelihood`
- `exoplanet transit timing Gaussian mixture outlier likelihood ephemeris prediction`
- `exoplanet forecast calibration heavy tailed predictive distribution ephemeris`
- `transit ephemeris reliability Student t predictive forecast calibration`
- `Agol 2021 TRAPPIST-1 Student-t likelihood transit timing residuals width multiplier degrees freedom`
- `Jontof-Hutter 2016 820 39 transit timing non-Gaussian outliers robustness`
- `Robnik Seljak 2021 non-Gaussian Kepler data Gaussian Student t mixture transit`
- `Ivshina Winn 2022 TESS transit timing extra scatter chi square error floor`
- `exoplanet transit ephemeris hierarchical uncertainty calibration forecast prediction mixture model`
- `transit timing catalog probabilistic forecast calibration proper scoring ephemeris uncertainty`
- `transit time likelihood Gaussian mixture outlier exoplanet ephemeris`
- `site:doi.org "Matched filtering with non-Gaussian noise for planet transit detections"`
- `Robnik Seljak MNRAS 504 5829 DOI`

Additional identifiers for the project bibliography, one per line:

```text
10.3847/PSJ/abd022
10.3847/0004-637X/820/1/39
10.1093/mnras/stab1178
```

The search was deliberately bounded after it established the decisive
distinction above. It did not exhaust robust time-series methods outside
astronomy or complete the ExoClock citation graph. A final novelty statement
still requires the T001 citation export and screening already specified in the
4 November update.
