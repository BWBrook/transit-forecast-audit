# Sprint 1 actual-design precision and stress simulations

**Codex, 6 November 2026. Development and metadata evidence only.** The
reproducible command is:

```bash
.venv/bin/python scripts/sprint1_precision.py --replicates 4000 --chunk-size 100
```

Outputs and a run receipt are in `results/sprint1/precision/`. No protected
outcome or light-curve file was opened.

## Decision

The metadata-defined experiment is large enough to distinguish a substantial,
transfer-stable correction from the unadjusted forecast **conditional on the
fitted rule, the assumed outcome-error model and successful scoring**. It does
not establish that such a correction is real or historically transferable.
Parameter-refit uncertainty is deliberately excluded here and is handled by
the forecast workflow's host-refit analysis.

The R8 extension clears its metadata arm: 28 planets add 17.95% to the 156
core planets. It should not be justified as a precision gain. The declared
union has 184 planets but only 175 hosts and 164.35 Kish-effective hosts. In
these conditional simulations its standard error never decreases relative to
the core design; signed changes range from a 6.49% to 34.46% increase across
the model/scenario grid. Core and union target different populations, so this
is a sensitivity, not a controlled estimate of the extension's causal value.

## Target, design and assumptions

The estimand is the equal-planet mean paired change in standardised 95%
interval score for M1, M2 or M3 versus M0. Events are weighted equally within
planet; host weights follow from those planet weights. Its Monte Carlo standard
deviation is the conditional study-design SE. The simulation does not estimate
transit occurrence, end-to-end recovery, or an astrophysical population
probability.

The generator preserves one joint T0-period error per planet across all of its
opportunities. The lognormal scale mixture is drawn once per planet. Stress
scenarios add host-shared outcome offsets, two host-shared six-SD shocks,
informative event loss based on latent forecast error, outcome-error scale
misspecification, and true covariance at zero and both feasible endpoints.
Every candidate is scored with the recorded C2 rule; the covariance stresses
therefore test misspecification, while the parent workflow supplies matched
rho-setting analyses.

The future design contains 3,107 core opportunities and 3,399 core-plus-
extension opportunities. Four inventory planets labelled unresolved, with 134
opportunities, are not members of that union. Opportunity counts are metadata
predictions, not successful timings. Assumed measurement errors come from 42
D039 SPOC-120 PDCSAP hosts (325 timed transits): each target receives the
median host error among its five nearest neighbours in Tmag. At the reference
scale the union's assigned median is 77.82 s (range 36.07-180.61 s); 154
opportunities lie outside the reference Tmag range and use the nearest boundary
neighbours. Half-scale and double-scale sensitivities are retained.

## Results

M2 illustrates the decision; the output tables contain all M1-M3 comparisons.
`Delta IS95 < 0` favours the correction. Intervals below are the 2.5th and
97.5th percentiles across 4,000 simulated studies, not confidence intervals for
the Monte Carlo mean.

| Design / known truth | Mean Delta IS95 | Conditional SE | 95% simulation interval | Pr(Delta < 0) |
|---|---:|---:|---:|---:|
| DRB-to-DRC, M0 truth | +1.487 | 0.134 | [1.186, 1.710] | 0.000 |
| DRB-to-DRC, M2 truth | -1.434 | 0.810 | [-3.125, -0.003] | 0.975 |
| chronological, M0 truth | +1.909 | 0.150 | [1.570, 2.162] | 0.000 |
| chronological, M2 truth | -1.876 | 1.075 | [-4.134, +0.027] | 0.971 |
| future union, M0 truth | +2.828 | 0.201 | [2.346, 3.128] | 0.000 |
| future union, M2 truth | -2.953 | 1.572 | [-6.211, -0.131] | 0.981 |
| future union, M2 truth with host rho = 0.30 | -2.947 | 1.587 | [-6.187, -0.011] | 0.976 |
| future union, informative failure | -2.390 | 1.506 | [-5.515, +0.321] | 0.952 |

Under informative failure, 83.69% of opportunities and 98.72% of planets are
retained on average; the effective host count falls to 163.19. Selection both
attenuates the expected improvement and lets the study-level interval cross
zero. Host-shared outcome correlation of 0.30 changes the M2 SE only from
1.572 to 1.587 in the declared union, but this one-factor offset is not a full
shared-shape or photon-dependence model.

Measurement precision materially changes the margin. Under M2 truth, union
SEs are 1.948, 1.572 and 1.273 for assumed outcome errors at 0.5x, 1x and 2x;
the corresponding probabilities of a negative contrast are 0.989, 0.981 and
0.952. Larger outcome error reduces both the standardised signal and its
sampling variance, so probability and mean contrast must be read together.

The Gaussian-truth covariance stresses retain harmful widening. When true rho
is forced to zero, -1 or +1 while scoring retains C2, M2's mean union contrasts
are +2.832, +3.216 and +2.128: the correction is harmful in every simulated
study. These scenarios also set the true heterogeneity to zero (`true_s = 0`),
whereas the broad-M2 scenario has `true_s > 0`. They therefore cannot isolate
the effect of covariance or support a covariance-caused reversal relative to
broad M2. The matched-rho main analysis, not this factorially incomplete stress,
must determine covariance sensitivity.

Monte Carlo error is small relative to the scientific variation. For the
future-union M2-truth result, the MCSE is 0.025 for the mean, 0.018 for the SE,
and 0.0022 for `Pr(Delta < 0)`.

## Recommendation and residual risk

Use these results as a conditional design stress test, not as predicted sealed
performance. Continue the core experiment and allow the extension under R8's
already-passed metadata arm, subject to sprint 2's long-period and multi-planet
identification tests. Do not claim that the extension improves precision.
Preserve the no-correction comparator: under M0 truth every fitted correction
is detectably worse.

The main residual risks are fixed fitted parameters; model-generated known
truths; assumed rather than observed future measurement errors; treating every
metadata opportunity as scorable outside the explicit failure stress; an
arbitrary selection curve; and incomplete representations of shared shape,
product and photon dependence. Host-refit uncertainty, outcome-pipeline
qualification and matched covariance analyses remain necessary before a freeze
recommendation.

An independent numerical scoring audit is being performed elsewhere in sprint
1. A further scientific review after integration would materially increase
confidence in the scenario interpretation and the core-versus-union comparison,
but is unlikely to change the simulation arithmetic if the stated generator is
accepted.
