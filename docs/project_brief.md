# Research brief

**Working title:** *How reliable are exoplanet transit forecasts? A retrospective
evaluation of calibration, forecast horizon and practical precision.*

**Status:** proposed research design; no real-data findings. Prepared 2026-11-04.

## Rationale and the connection to population viability analysis

Brook et al. (2000) estimated population-model parameters from an earlier part
of each of 21 ecological time series and compared predictions with the later
part. The transferable principle is replicated temporal evaluation with a
separation between information used to predict and information used to judge
the prediction. The present project brings that principle to transit timings.
[Brook et al., Nature 404:385–387](https://doi.org/10.1038/35006050).

The astronomical setting offers a simple baseline: a linear ephemeris expresses
the predicted midpoint of transit number E as T0 + P E. The apparent simplicity
is useful. It lets the study concentrate on whether forecast uncertainties and
their operational interpretation are justified. Departures from strict
periodicity, uncertain measurements and the way observations are collected
still make validation a substantive problem.

The analogy to PVA does not transfer every design choice. Astronomical records
have multiple clocks: observation, data publication, model issuance and a
mathematical reference epoch. A halfway split of a modern cleaned catalogue
does not establish that the resulting forecast could have been made at that
historical point. Conversely, a legitimate frozen-data hindcast remains useful
if described accurately.

## What the initial review changed

The broad idea already has direct precedents. Most importantly, ExoClock IV
Section 5.1/Table 5 compares older ephemerides with later TESS timings. The study
also already discusses uncertainty scaling and the need for continued monitoring.
Our project begins with that evidence, rather than claiming those problems have
not been investigated. [Kokori et al. 2026](https://doi.org/10.3847/1538-4365/ae3238).

The potential additional contribution is an auditable benchmark that makes the
forecast origin, population, horizon, weighting, uncertainty target and
information boundary explicit, then tests one practical correction on an
independent later block. Whether that constitutes sufficient new knowledge is
the first decision, not an assumption built into the manuscript.

## Central and ancillary questions

| Question | Proposed output | Role in first paper |
|---|---|---|
| Q1. How do calibration and useful precision of issued forecasts vary with lead time? | Coverage curves, interval widths and proper scores by historical release and horizon | Primary |
| Q2. Which historically available information predicts poor performance? | A small prespecified analysis of training baseline, temporal gaps and reported uncertainty; TTV status as known then | Secondary |
| Q3. Can a simple correction learned from earlier forecast errors improve later predictions? | Paired held-out interval-score comparison with coverage/width trade-off | Primary extension if feasible |
| Q4. What timing margins would these predictions require for a specified observing-window rule? | Conditional window replay with explicit duration/selection assumptions | Ancillary; defer if scope expands |

The first paper should not attempt all possible covariates or all nonlinear
ephemeris models. Its strongest form is one defined forecast product, a
defensible outcome cohort, and one new empirical comparison.

## Proposed hypotheses, before seeing the final outcomes

**H1: conditional calibration.** Under a correctly specified linear timing model
and reliable input errors, measured future midpoints should follow the issued
forecast distribution convolved with their measurement-error distribution.
Evaluate departure across lead times without assuming a preferred direction.
Formal uncertainty already grows with extrapolation; increasing absolute error
alone is not evidence of worsening calibration.

**H2: information span matters beyond nominal precision.** Forecast performance
may differ for systems with short or patchy historical coverage even at similar
reported forecast uncertainty. Use only information available at the origin.
This is an association to test, not a claim to identify a causal mechanism.

**H3: earlier forecast errors contain transferable calibration information.** A
single multiplicative correction to forecast standard deviation, estimated on
earlier outcomes, may improve a proper score on a later block. The null outcome
is valuable: no transferable improvement, or improvement too uncertain to
justify a more complex rule. Coverage gains accompanied by excessive width
are not automatically useful.

**H4: apparent precision may have a practical cost.** A fixed observing-window
rule based on formal uncertainty may have different conditional containment
than intended. A real missed-transit rate requires attempted-observation
denominators and observing conditions. Do not equate the two quantities.

## The bounded first study

Recommended first route: historical ExoClock DRB/DRC forecast artifacts and later
TESS measurements, with a metadata-first pilot of 5–10 planets. Use TESS because
its observing windows and public products can make independent evaluation more
tractable; the sample remains conditioned on available, measurable transits.
Public release documentation is summarised in `data_sources.md`.

For a deliberately narrow main cohort, consider short-period, well-established
transiting giants whose historical ephemerides are linear. A provisional screen
is P <= 10 days and radius >= 0.6 Jupiter radii, applied only to measurements
available at the forecast origin. These numbers are **design placeholders**, not
an approved definition or a result. Metadata feasibility and the literature
gate may justify using a different transparent cohort or the complete release.
Do not choose the cohort by the size or sign of its later errors.

Report the full baseline cohort and the subset with suitable later data. Known
TTV systems can form a separate, historically defined stratum. Later-discovered
TTV behaviour must remain visible in the original forecast cohort.

## Three tracks and their legitimate claims

**R — reproduction.** Match the earlier paper's sample, date convention,
uncertainty calculation and weighting. Reproduce it before changing the design.
Comparisons against its rounded published values are a necessary check, not a
substitute for matching the event list and denominators.

**A — issued forecasts.** Use a recoverable artifact that was public before the
outcome occurred. Its issue date may be a journal publication date, a verified
repository release or an independently verified preprint announcement. Retain
artifact identity: a later revised file is not the original forecast.

**B — chronological refits.** Fit a declared common procedure to timing
measurements demonstrably available by each cutoff. This estimates performance
of that procedure. It does not assess exactly what original observers issued.

Choose A as the primary target if its inputs are sufficiently complete. B is a
transparent secondary or fallback study, with a revised question when needed.

## Statistical foundation

The basic forecast variance at epoch E is

\[
v_f(E)=\sigma_{T_0}^2+E^2\sigma_P^2+2E\,\mathrm{Cov}(T_0,P).
\]

When the parameters use a pivot epoch E_ref, replace E with E-E_ref. A different
pivot changes the parameter covariance but must not change the forecast. This
is established ephemeris theory; see [Deeg 2015](https://doi.org/10.1051/0004-6361/201425368).

For an independent measured midpoint y with error variance s_y^2, the simple
Gaussian predictive variance for the **measurement** is v_f+s_y^2. Scoring the
measurement against only v_f unfairly attributes all measurement error to the
forecast. Conversely, uncertainty in y should not be added to a telescope
schedule as though it were physical uncertainty in the true transit time.

Use coverage together with width and a proper score. The proposed primary
improvement metric is a paired, planet-balanced 95% interval-score difference
on an untouched later block. Signed errors, absolute errors, PIT diagnostics and
log scores provide complementary evidence. Full details and dependence rules
are in `statistical_models.md` and `evaluation_protocol.md`.

## What would count as a useful outcome?

- A demonstrated, reproducible lead-time dependence that matters to use of
  historical forecast intervals and was not adequately characterised before.
- A simple correction with a defensible improvement in an independent era,
  along with its limits and uncertainty.
- Evidence that an apparently useful correction fails to generalise, narrowing
  what can be inferred from retrospective residuals.
- A reusable forecast–outcome benchmark with transparent provenance and a clear
  scientific lesson beyond repackaging existing tables.

These are candidate outcomes, not promised publications. If the result is only
an exact reproduction, assess it as a reproduction resource or note rather than
forcing a claim of new astronomical discovery.

## A realistic sequence

1. **Source and novelty check:** revisit the closest papers and identify one
   empirical extension with a reason to matter.
2. **Metadata pilot:** recover 5–10 fully traceable forecast–outcome dossiers.
3. **Reproduction:** establish the existing benchmark's exact conventions.
4. **Simulation:** test calibration, selection and leakage failure modes with
   the actual pilot's cadence and precision ranges.
5. **Protocol freeze:** select the cohort, lead-time bands and final untouched
   evaluation period; register the decision in a versioned protocol commit.
6. **Main analysis:** run the frozen comparisons and targeted sensitivity tests.
7. **Interpretation:** seek domain criticism using concrete figures and source
   records; write the result at the scope its evidence supports.

The first feasibility gate determines the practical scale. Compute is unlikely
to be the first bottleneck; trustworthy historical information is the key input.
