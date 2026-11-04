# Independent numerical and methodological review of D027

**Codex, 5 November 2026. Development material only.** This review used only
the already inspected 2022–2024 timing catalogue. It opened no light curves or
protected outcomes. The reference implementation and receipts are in
`scripts/review_tranche2_mixture.py` and
`results/pilot_v1/tranche2_review/mixture_*`.

## Decision

The fitted population-level shape survives numerical repair: DRB has a typical
forecast-SD inflation near 2.25 with moderate heterogeneity; DRC has a median
near one and very large between-planet heterogeneity. D027 remains useful as a
development model, but its likelihood implementation, hard planet labels and
uncertainty statements do not survive unchanged.

The production Woodbury calculation evaluates the quadratic as a large norm
minus a projection. At large scale factors those terms cancel. For the real
TOI-1130c design at `c=1e32`, the old calculation returns a log likelihood of
+35190.6; the stable SVD calculation and dense Cholesky both return -38.0619.
At sufficiently high Gauss–Hermite nodes this creates impossible likelihoods
and sends the optimiser to its parameter bounds. The existing test checks only
`c <= 50`, outside the failure region.

The independent implementation whitens each planet, uses an SVD to separate
the forecast subspace from its orthogonal residual, and evaluates

`q_perp + sum(alpha_j^2 / (1 + c * eigenvalue_j))`.

This is algebraically equivalent without subtracting nearly equal quantities.
It matches dense Cholesky on real gross-failure planets where Cholesky remains
well conditioned.

## Converged fit

Robust Gauss–Hermite orders 192, 256 and 384 agree, and adaptive integration
over the standard-normal mixing variable confirms the order-384 optimum.

| Release | Adaptive b | Adaptive s | Adaptive NLL | Stable profile 95% CI b | Stable profile 95% CI s |
|---|---:|---:|---:|---:|---:|
| DRB | 2.24949 | 1.09314 | 493.21582 | 1.828–2.723 | 0.708–1.568 |
| DRC | 0.97626 | 3.14868 | 1378.64978 | 0.699–1.301 | 2.690–3.724 |

For DRC, GH48 gives `b=0.97694`, `s=3.13289` and an NLL spuriously 0.137
lower. The point estimates therefore survive, but GH48 is not converged at the
reported tail width. Orders 192 and 384 should agree before fitting extensions;
adaptive integration should check the adopted optimum and difficult planets.

The profile intervals above are conditional model-based intervals. They treat
planets as independent, fix the outcome scale, omit model-selection uncertainty
and do not preserve dependence between planets in one host. They are not the
project's final host-cluster uncertainty intervals.

## Three different tail quantities

The earlier report counted planets whose quadrature-node posterior median
exceeded a threshold. GH48 made these medians visibly quantised. Continuous
posterior integration changes DRC's median-label count above 10 from 15 to 29
(and above 100 from 10 to 9). DRB changes from zero to two above 10. The labels
are therefore unsuitable as a response for predictor selection.

Three estimands must remain separate:

| Release | Model population P(lambda>10) | Sum of posterior P(lambda_p>10) | Planets with posterior median lambda>10 |
|---|---:|---:|---:|
| DRB | 0.0176 | 2.68 of 134 | 2 |
| DRC | 0.2323 | 61.21 of 316 | 29 |

For DRC, the corresponding quantities above 100 are 0.0718, 16.23 planets and
9 median labels. The fitted population tail is determined by `s`; the posterior
expected count also uses each planet's data; a count of posterior medians is a
classification rule. None can substitute silently for another. Halving the
posterior integration grid changes no log median by more than 3.3e-6, so the
continuous values are numerically stable.

## Scientific interpretation

The model estimates an effective discrepancy scale relative to the issued
diagonal `T0,P` covariance. A large lambda can arise from underestimated
parameter uncertainty, a biased epoch or period, TTVs, a source/input mismatch,
or an unmodelled outcome offset. With one issued forecast per planet, these are
not separately identified. Calling lambda a latent, intrinsic planet property
would overstate the evidence.

The visit-mean standard errors assume independent event errors after applying
the common outcome scale. The local analysis cannot detect sector-common or
reduction-common offsets, so such errors can enter lambda. The missing issued
`Cov(T0,P)` remains a C2/C3 sensitivity under D021, not recovered covariance.
Gross tail cases should receive row-level source, cycle and availability checks
before being used to motivate an astrophysical or pipeline explanation.

The recovery simulations establish identifiability under the fitted model and
real design. They do not test the numerical tail at higher quadrature order,
source mismatch, common outcome offsets, host dependence, mean bias, or an
alternative discrepancy shape. Twenty simulations per truth are a diagnostic,
not interval validation.

## Recommendation

Replace the production rank-two likelihood with the stable whitened-SVD form
and require order-192/order-384 convergence plus an adaptive check. Fit
issue-time predictors through the marginal likelihood, with folds grouped by
host; do not regress hard posterior lambda labels. Report the fitted
population tail and posterior expected tail count separately. Treat the
current profile intervals as conditional until host-cluster uncertainty and
outcome-scale sensitivity are incorporated.

The heavy-tail model is worth carrying forward to prospective comparison, but
it should compete against simpler robust alternatives and the issued Gaussian
using proper scores. A symmetric scale mixture may rescue large mean biases by
becoming very wide; that is not automatically useful forecast improvement.
