# Statistical models and scoring specification

**Status:** design specification, 4 November 2026. The small executable scaffold demonstrates only a subset of this specification on synthetic data. Check the README and code for implemented functionality. No astrophysical estimates or empirical validation results are claimed here.

## 1. Notation and the forecast target

For planet `i`, historical forecast origin `o` and transit cycle `E`, write the true physical mid-time as `theta_iE` and an independently measured timing as `y_iE`. Let `s_iE` be the measurement standard deviation. Every cycle label is tied to an explicit reference convention; it is an integer identifier, not a rounded calendar time.

The usual linear ephemeris is

\[
\mu(E)=T_0+P E,
\]

with epoch `T0` and period `P` expressed in days. BJD_TDB is the internal time coordinate. Reference epochs chosen for fitting need not be dates at which anyone issued a forecast. Keep issue date, last input observation and numerical reference epoch separate.

Three quantities must not be conflated:

1. A point prediction `mu(E)` for a physical transit mid-time.
2. Uncertainty in that physical prediction, including whatever parameter and model uncertainty the forecast actually states.
3. Uncertainty in an independently measured evaluation mid-time.

A published linear fit may quantify parameter uncertainty while treating the constant-period model as exact. The audit tests the resulting forecast's empirical behaviour; it does not silently augment that original model using later discoveries.

## 2. Propagate the complete epoch–period covariance

For a bivariate approximately Gaussian parameter estimate,

\[
\Sigma=\begin{pmatrix}
\sigma_{T_0}^2 & c_{T_0,P}\\
c_{T_0,P} & \sigma_P^2
\end{pmatrix},
\qquad
v_f(E)=[1,E]\Sigma[1,E]^\top
=\sigma_{T_0}^2+2E c_{T_0,P}+E^2\sigma_P^2.
\]

Require finite values, nonnegative diagonal variances, symmetry and positive semidefiniteness within a scale-aware numerical tolerance. A genuinely negative propagated variance is a data/model error. Only roundoff-sized negatives may be truncated to zero with an explicit check.

For two future epochs, forecast errors remain correlated:

\[
\operatorname{Cov}\{\mu(E_a),\mu(E_b)\}
=[1,E_a]\Sigma[1,E_b]^\top.
\]

This is one reason that thousands of future transits of a few planets do not provide thousands of independent tests of ephemeris calibration.

### Changing the pivot must not change the prediction

Let `Tq = T0 + q P`, `Eq = E - q` and

\[
A_q=\begin{pmatrix}1&q\\0&1\end{pmatrix},
\qquad \Sigma_q=A_q\Sigma A_q^\top.
\]

Then both `Tq + P Eq` and the propagated variance must equal the original values, apart from floating-point tolerance. Re-epoching the point estimate while leaving its uncertainty unchanged is incorrect. A fractional weighted pivot is a convenient regression coordinate; physical transit cycle IDs remain integers, and exported ephemerides must specify whether their pivot is an actual transit.

Deeg (2015) discusses the importance of central reference epochs and prediction errors. Full covariance propagation is established practice, not a novelty claim for this project. [Primary reference](https://doi.org/10.1051/0004-6361/201425368).

### When covariance is absent

An omitted table entry does not establish zero covariance. Given only marginal errors, write

\[
v_f(E;\rho)=\sigma_{T_0}^2+E^2\sigma_P^2
+2E\rho\sigma_{T_0}\sigma_P,\qquad -1\le\rho\le1.
\]

The mathematical bounds are

\[
(\sigma_{T_0}-|E|\sigma_P)^2\le v_f(E)\le
(\sigma_{T_0}+|E|\sigma_P)^2.
\]

Use these as a sensitivity range, not as a posterior distribution for `rho`. Near a cancelling covariance configuration, the lower bound can be uninformative. Point errors remain evaluable, but full probabilistic rankings may remain unresolved. A stated weighted-centre fitting procedure can justify an approximation only after checking the actual pivot, likelihood, weights and posterior behaviour. Rounding the pivot to a transit and using nonlinear or robust likelihoods can leave residual correlation.

## 3. A stable standardised refit for Track B

Let `w_j=1/s_j^2` for training timing observations available at the cutoff. Set `Ebar=sum(w_j E_j)/sum(w_j)` and use centred predictors `x_j=E_j-Ebar`. Subtract a time offset close to the observations before fitting, so a Julian date around 2.4 million days is not multiplied through an ill-conditioned normal equation.

With `X_j=[1,x_j]`, a weighted linear least-squares model has

\[
\hat\beta=(X^\top W X)^{-1}X^\top W y,
\qquad C_\beta=(X^\top W X)^{-1},
\]

when the supplied independent measurement variances are taken as known and correctly calibrated. In implementation, use centred closed-form sums, QR or a stable solve; do not form a numerical matrix inverse merely to solve coefficients. Convert the full covariance when exporting another reference epoch. Guard against too few distinct epochs, effectively zero baseline and singular designs.

For general correlated measurement errors `V`, replace `W` by `V^{-1}` and perform generalised least squares. Shared-exposure alternatives cannot be made independent by giving them separate rows.

Do not automatically multiply this covariance by reduced chi-square and still call it the original known-error model. A residual-scale model is a distinct model; its variance estimate, degrees of freedom and uncertainty need documenting. The published ExoClock fitting procedure already includes an excess-noise rescaling step, so applying another scale to that product has to be justified and evaluated out of sample. See [ExoClock IV, Section III.1](https://arxiv.org/html/2511.14407v1).

For a small reconstructed training sample with unknown residual scale, Student-t prediction or posterior simulation is preferable to pretending the estimated scale is known. That refinement is optional after the basic benchmark is reproduced; it is not necessary for the initial synthetic demonstration.

## 4. Evaluate the distribution of the measurement correctly

Assume temporarily

\[
\theta_E\mid\mathcal{H}_o\sim\mathcal N(\mu_E,v_{f,E}),
\qquad y_E\mid\theta_E\sim\mathcal N(\theta_E,s_E^2),
\]

where `H_o` is the information actually available at the origin and the measurement is independent of the forecast inputs. Then

\[
y_E\mid\mathcal{H}_o\sim\mathcal N(\mu_E,v_{f,E}+s_E^2),
\quad e_E=y_E-\mu_E,
\quad z_E=\frac{e_E}{\sqrt{v_{f,E}+s_E^2}}.
\]

The general case is the convolution

\[
p(y_E\mid\mathcal H_o)=\int p(y_E\mid\theta_E)\,
p_f(\theta_E\mid\mathcal H_o)\,d\theta_E.
\]

A bootstrap sample or posterior sample can approximate this when either distribution is asymmetric. Use a proper likelihood for the measurement, not an arbitrary combination of upper and lower errors.

If a timing product shares exposures or a constraining ephemeris prior with the forecast, the residual variance includes `-2 Cov(y_E, mu_E)`. Primary evaluation avoids such overlaps. Merely adding two marginal variances does not fix dependence introduced by a joint fit.

### What can be called calibrated?

Observed residual coverage evaluates the convolved measurement distribution under the assumed measurement-error model. It does not directly reveal the coverage of a latent true-time interval. A useful diagnostic subset has evaluation measurements much more precise than the forecast, with its selection rule fixed in advance; even there, report the approximation and sensitivity. If measurement errors are poorly known, forecast error and measurement error can be weakly identifiable.

Keep `sqrt(v_f)` and `s_E` as separate outputs. Otherwise a very uncertain evaluation measurement can make a poor forecast appear operationally safe.

## 5. Minimal model ladder

| Label | Description | Role |
|---|---|---|
| **P0** | Frozen published point ephemeris and explicitly documented uncertainty convention | Track A baseline; reproduce the issued product |
| **P1** | P0 with a scalar calibration of the forecast variance learned from earlier completed pairs | Main optional extension; test on later outcomes |
| **R0** | Chronological weighted linear refit with complete covariance and specified measurement errors | Track B reference model |
| **R1** | R0 with a separately defined residual-noise model or historical recalibration | Secondary, only if identifiable and needed |
| **D1** | Quadratic or periodic timing model selected/fitted solely on past data | Later exploratory comparison, not required for paper one |

Do not compare a published product with a refit that uses observations unavailable when that product was issued without identifying the information difference. For a fair method comparison, use identical eligible events, information cutoffs and outcome products.

### A single forecast-scale parameter

For historical calibration pairs `k`, let

\[
V_k(\lambda)=\lambda^2 v_{f,k}+s_k^2,\qquad\lambda>0.
\]

Fit `lambda` by minimising a planet/system-balanced mean negative log predictive density on an earlier calibration block. A deterministic one-dimensional optimisation of `log(lambda)` is sufficient. Freeze the fitted value before later evaluation. Numerical search bounds must be disclosed, and a boundary solution must be flagged and investigated rather than silently accepted as a scientific estimate.

Do not use `lambda^2(v_f+s^2)` for this forecast-only correction: that would change the evaluation measurement model as well. Nor should `lambda` be estimated from the same held-out errors on which its success is scored.

An additive timing floor gives `V=lambda^2 v_f+q^2+s^2`, but `lambda` and `q` can trade off when forecast variances have little range. Horizon-dependent inflation, heavy tails and system-specific scales add further flexibility. Add them only in response to a prespecified, identifiable question and evaluate them on an independent later block. They are not defaults for the first pilot.

Because the scale estimate itself is uncertain, a later full analysis should assess whether plug-in predictions are adequate using outer resampling or a predictive mixture over calibration uncertainty. Store calibration-cohort IDs so that uncertainty propagation can reproduce the entire fitting step.

## 6. Scores, signs and units

Use one time unit consistently within each calculation. Fit in days if convenient, but compute reported residuals, widths and scores in seconds or minutes with an explicit conversion. One day is 86,400 seconds by the units used here. Converting a time *scale* is a separate astronomical operation; BJD_TDB is not obtained by applying a constant offset to arbitrary UTC/HJD data. See [Eastman et al. 2010](https://doi.org/10.1086/655938).

Define `e=y-mu`, so **positive means the observed transit is later than predicted**. Do not wrap residuals modulo the period to reduce them. If cycle assignment is ambiguous, represent the mixture or exclude that pair from the unambiguous primary scope with a recorded reason.

For total predictive variance `V` in seconds squared, the negative logarithmic score is

\[
\operatorname{NLL}=\tfrac12\log(2\pi V)+\frac{e^2}{2V}.
\]

Lower is better. The numerical value depends on time units, so scores from different units cannot be mixed; paired differences with the same units remain interpretable. Very small variances and large residuals may dominate this score, which is why physical provenance and a complementary interval score matter.

For a central `(1-alpha)` predictive interval `[l,u]`,

\[
\operatorname{IS}_{\alpha}(l,u;y)
=(u-l)+\frac{2}{\alpha}(l-y)\mathbf1(y<l)
+\frac{2}{\alpha}(y-u)\mathbf1(y>u).
\]

Lower is better. It rewards narrow useful intervals and penalises misses; arbitrary widening cannot improve it without cost. The 95% interval score is a suitable primary proper score. These scoring definitions follow [Gneiting & Raftery 2007](https://doi.org/10.1198/016214506000001437).

For the Gaussian case use quantiles from `N(mu,V)`: a central 95% interval uses approximately `1.959964 sqrt(V)`, whereas one standard deviation corresponds to approximately 68.2689%. Do not label a one-sigma interval as an exact 68% interval or compare a 95% empirical rate to a three-sigma nominal target. Include boundary points in coverage consistently.

Coverage, signed error, absolute error, interval width and interval score are complementary outputs. A pooled mean of `z^2` does not establish conditional calibration; well-calibrated aggregate coverage can conceal opposite problems in different lead-time groups.

## 7. Aggregation and comparison

For an event score `S_ioj` in a fixed horizon band, a proposed planet-balanced aggregate is

\[
\bar S=\frac1{N}\sum_{i=1}^{N}
\frac1{O_i}\sum_{o=1}^{O_i}
\frac1{n_{io}}\sum_{j=1}^{n_{io}}S_{ioj}.
\]

Apply the same weights to coverage indicators and widths. Define how zero-event cells are handled: they are absent with their counts reported, not scored as successes. For comparing two models, use their common eligible pairs and then calculate the weighted paired score difference. Record both the common-pair cohort and all-model-specific exclusions.

Resample systems (or planets where system IDs are unavailable) and keep their entire history intact. Each bootstrap replicate should preserve model pairing; if uncertainty about a learned calibration is included, repeat calibration on the resampled earlier block. A more complex campaign bootstrap is a sensitivity analysis when shared instrument effects may span multiple systems. Do not claim that a basic planet bootstrap captures all such dependence.

## 8. Scheduling calculations are a separate target

For a symmetric observing window of half-width `W` centred on the prediction, a point estimate with fixed duration `D` is wholly inside the window when

\[
|\theta-\mu|+D/2\le W.
\]

Operational predictions concern the latent physical `theta` and duration, not the noisy measured timing used to score a forecast. Integrate over both uncertainties when they matter. Required pre/post-transit baselines further enlarge the window. A BJD_TDB event time must also be converted appropriately for the observatory's scheduling clock and light-travel geometry.

Replaying this inequality on a sample of successfully observed transits is conditional evidence. It does not include previously missed transits, weather or telescope visibility. A comparison of suggested windows can be a useful secondary figure, but a claim of total telescope time saved requires additional observation-policy evidence.

## 9. Simulation matrix and verification targets

Construct simulated planets with varied period, training baseline, timing precision, pivot and number of observations. Generate the physical timing process first, then noisy measurements, publication delays and a selection process. Preserve the distinction between a true event, an exposure, a reduction and a public timing estimate.

The initial matrix should include:

| Scenario | Purpose |
|---|---|
| Exact linear process, known errors | Check covariance, convolved coverage and scoring under the model |
| Same model at several pivots | Verify invariance of means and variances |
| Misstated forecast errors only | Test forecast-scale recovery and later predictive performance |
| Misstated outcome errors only | Demonstrate possible misattribution to the forecast |
| Long-period sinusoidal deviation | Test extrapolation failure that may look linear on a short training span |
| Quadratic timing drift | Stress a misspecified constant-period model without claiming orbital decay |
| Campaign offsets and duplicate reductions | Check false precision and grouping safeguards |
| Publication delay and old observations published late | Verify historical availability filters |
| Window-truncated observations | Show why success-conditioned timing samples can overstate reliability |

Use physically motivated amplitudes only after checking source-class literature; otherwise label scenarios as mathematical stress tests and express their scale directly in timing units. For a quadratic illustration `theta(E)=T0+P E+Q E^2`, a physical identification `Q≈P dot(P)/2` assumes a small approximately constant period derivative with consistent units. A fitted nonzero `Q` alone does not identify its physical cause.

Meaningful verification targets include analytic covariance results, pivot invariance, duplicate/exposure leakage rejection, correct date-boundary handling, known interval-score values, extreme residual behaviour and uncertainty recovery over repeated simulated datasets. A demo with dozens of synthetic planets is an illustration of the pipeline, not a power analysis or an astronomical result.

## 10. Decisions deliberately left for feasibility review

- Whether enough issued forecasts with verified dates exist for Track A to be the main analysis.
- Whether source covariance and the exact published scoring convention are recoverable.
- Whether timing-product uncertainties are adequate without a dedicated photometric reanalysis.
- Which historical cohort and lead-time bands provide enough independent systems.
- Whether an honest earlier-calibration/later-evaluation split supports P1.
- Whether the most useful new contribution is calibration, lead-time dependence, operational issuance, or a documented limitation of available forecast products.

These are scientific decisions to resolve and record. They are not grounds to conceal a weak denominator, infer missing metadata, or expand the first paper automatically into a full orbital-dynamics programme.
