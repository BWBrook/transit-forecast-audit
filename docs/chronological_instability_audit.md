# Chronological calibration instability audit

## Conclusion

The large negative tail in the joint-host refit bootstrap is real model
instability, not failed quadrature or an optimiser artefact. The inspected
training-span rule has a point gain of `0.01276` nats per retained window over
the constant mixture, but its 400-replicate host-bootstrap interval is
`[-9.07197, 0.04295]`. It therefore provides no stable evidence of prospective
improvement and should not be selected for a frozen analysis in its present
form.

## Exact replay

`scripts/review_chronological_extremes.py` replays bootstrap replicates 6, 61,
273 and 325 using the original seed `20261107`, fixed outcome scale `a=1`, the
2022 observation-date training block and the 2023-01-01 to 2024-01-03
evaluation block. No light curves are read. Each replay refits both population
models and checks the later score by three routes:

- 384-node Gauss-Hermite quadrature used by the calibration script;
- 768-node Gauss-Hermite quadrature;
- independent adaptive integration after a posterior-mode search over
  `z = [-100, 100]`.

The 384-node scores for replicates 6, 61, 273 and 325 are respectively
`-33.33379`, `-90.63339`, `-61.81921` and `-55.50882` nats per retained window
relative to the constant mixture. The 768-node results differ by at most
`0.00154`; wide adaptive integration agrees with the 384-node per-planet log
densities to numerical precision. The extreme losses are therefore not an
integration-resolution failure.

## Mechanism

All four resampled early blocks drive the fitted span model's population
heterogeneity scale close to zero (`s = 2.6e-5` to `7.3e-5`) while estimating a
positive training-span coefficient (`beta = 0.229` to `0.407`). This is a
scientifically near-boundary fit even though it is not literally at the
optimiser bound. The rule then extrapolates to unusually short training spans
with a narrow predictive distribution.

The clearest case is replicate 61. Its span fit is `b = 1.87979`,
`s = 2.62e-5`, `beta = 0.40672`. TOI-1130 lies about 3.84 training-bootstrap
standard deviations below the predictor centre, receives a median forecast-SD
scale of about 0.39, and contributes `-85.90` nats per window-equivalent to the
resampled mean contrast. The same host is the largest adverse contributor in
all four audited replicates; WASP-161 is secondary in three. This is genuine
extrapolation and tail-collapse sensitivity in the fitted rule.

## Interpretation and limits

The audit is a conditional development diagnostic. The training-span predictor
was nominated after the complete development era had been inspected, 2022
outcomes precede the conservative DRC issue date, and individual timing
availability is unresolved. The exercise is therefore an observation-cutoff
hindcast, not availability-correct Track A or sealed validation. It also fixes
the outcome scale, model family and selected cohort, while issued
`Cov(T0, P)` remains unavailable.

A future candidate could impose a pre-specified tail or shrinkage rule and
validate that choice entirely within development data. The present result does
not justify choosing such a repair post hoc. The retained evidence is
`results/pilot_v1/chronological_calibration/extreme_audit.json`.

Reproduce with:

```sh
python scripts/review_chronological_extremes.py
```
