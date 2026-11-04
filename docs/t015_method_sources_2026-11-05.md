# D034 method review: red-noise scaling and injection calibration

**Independent bounded review, 5 November 2026.** This review covers only the
uncertainty-calibration method in `scripts/t015_timing_pipeline.py` and the
interpretation proposed in `docs/t015_pipeline_report.md`. It uses the recorded
development outputs, not any protected light curve or sealed outcome.

## Decision

D034 establishes a useful development result: the timing pipeline runs on real
SPOC noise, recovers injected mid-times with little detected bias in this small
sample, and shows that a white-noise analysis is overconfident relative to the
chosen beta-times-chi-square scaling. It does **not** yet establish a calibrated
per-sector uncertainty scale, an outcome-specific scale to carry into the
sealed analysis, or a 1.12 multiplier for ExoClock uncertainties.

The time-averaging beta calculation is a recognisable literature method, but it
is a heuristic variance inflation, not a likelihood for the correlated flux.
The injections provide the more relevant calibration check. Their present
interpretation is conditional on an exactly known fitted shape and on five
bright/moderate 120-second sector-star data sets. Dependence from reused noise,
the small number of independent sector-star units, and unpropagated shape and
scale-estimation uncertainty make the quoted intervals too strong for a freeze.

Accept D034 as **pipeline feasibility and conditional development validation**.
Do not accept the report's unqualified statement that the pipeline is calibrated
on real TESS noise, or its proposal to attach "each outcome's own injection
z-RMS," until the redesign below has been validated.

## What the beta estimator supports

Winn et al. (2008) define the time-averaging method from residuals of a fitted
light curve. For bins containing N points and M non-overlapping bins, the
white-noise expectation is

`sigma_N = sigma_1 / sqrt(N) * sqrt(M / (M - 1))`,

and beta is the observed binned residual RMS divided by that expectation. They
used the median beta over 15--30 minutes, chosen to approximate ingress/egress,
and explicitly described the procedure as lacking full statistical rigour.
The D034 formula and its median over 10, 15, 20 and 30 minutes therefore have a
clear precedent; beta is not an invented statistic.

That precedent does not validate every implementation detail:

- The relevant averaging scale should follow the timing-sensitive part of the
  light curve, usually ingress/egress, rather than a fixed range inherited from
  another target. D034 does not show that 10--30 minutes spans ingress/egress
  for every fitted sector and cadence regime.
- `beta_factor` groups consecutive array entries, not fixed intervals in time.
  Quality masking can make adjacent retained entries non-adjacent cadences.
  Bins should be defined from timestamps or split at cadence gaps.
- Beta is truncated at one and its sampling uncertainty is discarded. The
  subsequent posterior treats `beta * sqrt(max(chi2_nu, 1))` as known.
- The timing fit optimises two baseline coefficients and a mid-time, but the
  script divides its minimum chi-square by `n - 2`; the fixed-shape timing fit
  has `n - 3` residual degrees of freedom. This is numerically minor at the
  present sample sizes but should be corrected before freeze.

Cubillos et al. (2017) show why beta should remain a diagnostic rather than the
calibration claim. They reproduce the same formula, warn that binned-RMS
uncertainty becomes strongly asymmetric when the number of bins is small, and
test time averaging by injection and recovery. In their real-noise experiments,
time averaging improved coverage but did not restore nominal coverage. Carter
and Winn (2009) likewise found that a likelihood modelling correlated noise
gave more reliable mid-time uncertainties than white-noise and time-averaging
approaches when its noise assumptions held. Thus a literature-standard beta
calculation can be useful without being sufficient.

## What the current injections identify

The current experiment injects the sector's fitted transit model into real
out-of-transit flux and recovers it using the identical fixed shape. This is a
valid test of **conditional timing calibration given that shape, baseline model,
eligible phase range and observed noise record**. It usefully tests more than a
synthetic Gaussian-noise experiment.

It does not include:

- uncertainty or bias in radius ratio, scaled semimajor axis, inclination or
  limb darkening;
- mismatch between the batman signal family and a real transit, including spot
  crossings or asymmetric structure;
- uncertainty induced by estimating the shared shape from the same sector;
- the faint-target, 20-second, 200-second, FFI or alternative-pipeline regimes;
  or
- the ExoClock fitting and uncertainty procedure itself.

Consequently, multiplying this pipeline's injection z-RMS by the observed ratio
of its uncertainty to ExoClock's uncertainty does not estimate a uniquely
defined ExoClock scale factor. Agreement of the two mid-times on the same
photons is a useful check, but it does not make their uncertainty estimators
exchangeable.

### Dependence and effective replication

The 261 recoveries are repeated analyses of five sector-star noise records, not
261 independent experiments. Using the recorded rounded phases and the actual
window half-width from the script, 260 of 261 injection windows overlap at
least one other injection window. Their overlap graph contains about 46
connected components: 14, 8, 7, 9 and 8 in the five sector-star data sets. This
is an audit diagnostic, not an exact effective sample size, because phases were
stored to only three decimals and sector-wide correlations can connect
non-overlapping windows.

Clustering the reported interval by the 26 originating real-transit epochs
keeps the most obvious within-epoch overlaps together, but the host epoch is an
administrative label rather than the data-generating unit. It places two
separate injected phase bands in one cluster while treating different epochs
from the same sector-star record as independent. Neither choice addresses
shared sector systematics or the shared fitted shape. More generally, bootstrap
inference for dependent observations requires resampling dependence-preserving
blocks rather than treating reused observations as independent (Kunsch 1989).

There are only five sector-star units. A percentile interval based on 26 host
epochs can describe conditional variation among those phase placements, but it
cannot quantify transfer to new sectors or target regimes. The bootstrap code
that produced the report's intervals is also absent from the committed T015
script and outputs, so those intervals are not presently reproducible from the
documented command.

## Redesign required before a per-sector freeze

### 1. Define the estimand and two calibration tiers

Keep separate:

1. **Conditional noise calibration:** coverage of the mid-time interval when
   the transit shape is fixed and correct for this sector-star light curve.
2. **End-to-end timing calibration:** coverage after estimating the shared
   shape, limb darkening and baseline through the production pipeline.

The first diagnoses the red-noise treatment. The second is the uncertainty
needed for an outcome timing. Do not call the first a full pipeline scale.

### 2. Make independent noise placements the primary injection sample

For each sector-star record, construct eligible out-of-transit intervals from
timestamps and cadence numbers after masking known astrophysical events and
quality gaps. Select a primary set of non-overlapping windows separated by at
least one full fitting-window width, plus a prespecified correlation buffer.
Inject only once into each primary window. Additional overlapping placements
may map phase sensitivity, but label them secondary and cluster them by the
connected cadence-overlap component.

Record the injected window's first and last cadence number. This makes the
dependence structure auditable rather than reconstructing it from rounded
phase. Kepler's large pipeline tests illustrate the useful distinction between
one end-to-end injection per target, which supports population-average pipeline
performance, and multiple flux-level injections on selected targets, which map
within-target behaviour but do not by themselves establish transfer across
targets (Christiansen 2017).

### 3. Break the exact-shape injection/recovery symmetry

Run both tiers:

- fixed-shape injections for conditional noise calibration; and
- end-to-end injections whose shapes are drawn from an earlier-sector or
  leave-sector-out posterior, or from a prespecified grid spanning depth,
  duration, impact parameter and limb darkening. Refit the shared shape exactly
  as the sealed pipeline will.

An injection should not use a posterior informed by the noise window into which
it is injected. Preserve draws and seeds so shape uncertainty can be propagated.

### 4. Calibrate at a supportable level

An individual outcome cannot support its own z-RMS: twelve mostly overlapping
placements produce an unstable scale estimate. Estimate a scale at a
prespecified stratum such as cadence/product x magnitude/SNR x duration, with
sector-star as the independent cluster. If enough sectors exist, use partial
pooling so per-sector estimates shrink toward their stratum mean. If not, retain
the development sensitivities 1.0, 1.09 and 1.2 rather than manufacturing a
precise per-outcome factor.

The calibration set must contain several sector-star records per intended
stratum. Five records cannot validate transfer to the sealed sample whose
cadence, magnitude and product distribution differs from this pilot.

### 5. Freeze metrics before the final validation split

For every stratum report, at minimum:

- median timing bias and a robust spread of recovery error;
- z-RMS and the mean z;
- empirical 68% and 95% interval coverage;
- calibration as a function of depth/SNR, duration, cadence and magnitude; and
- the number of sector-stars and non-overlapping cadence blocks.

Use one earlier subset to choose the beta timescales, scale model and quality
rules, then validate the frozen choices on different sector-star records. Do
not tune beta or a hierarchical scale on the same injections used to declare
coverage. If independent sector-star replication is inadequate, the honest
freeze is a prespecified sensitivity analysis, not a learned per-sector scale.

## Primary sources read

- Winn et al. (2008), *The Transit Light Curve Project IX*, Section III,
  equations 1--2 and the beta discussion. DOI
  [`10.1086/589737`](https://doi.org/10.1086/589737); full text
  [arXiv:0804.4475](https://arxiv.org/html/0804.4475v1).
- Carter & Winn (2009), *Parameter Estimation from Time-Series Data with
  Correlated Errors*, especially the simulated mid-time comparisons. DOI
  [`10.1088/0004-637X/704/1/51`](https://doi.org/10.1088/0004-637X/704/1/51);
  [arXiv:0909.0747](https://arxiv.org/abs/0909.0747).
- Cubillos et al. (2017), *On Correlated-noise Analyses Applied to Exoplanet
  Light Curves*, Sections III.2 and IV. DOI
  [`10.3847/1538-3881/153/1/3`](https://doi.org/10.3847/1538-3881/153/1/3);
  [arXiv:1610.01336](https://arxiv.org/abs/1610.01336).
- Christiansen (2017), *Kepler Planet Detection Metrics: Per-Target Flux-Level
  Transit Injection Tests of TPS for Data Release 25*, KSCI-19109-002,
  [NASA NTRS 20170009551](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20170009551.pdf).
- Kunsch (1989), *The Jackknife and the Bootstrap for General Stationary
  Observations*, *Annals of Statistics* 17:1217--1241. DOI
  [`10.1214/aos/1176347265`](https://doi.org/10.1214/aos/1176347265).

Search date: 2026-11-05. The review was deliberately stopped after these
sources resolved the acceptance question. It is not a broad transit-timing
literature sweep.
