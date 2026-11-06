# Sprint 1 independent audit of D038-D039

**Codex, 6 November 2026. Development evidence only.** The audit reads the
committed D039 event, run, product and selection tables and traces the decisive
code. It does not execute the timing pipeline, open FITS files or access any
post-2025-11-18 product. The reproducible command is:

```bash
.venv/bin/python scripts/review_sprint1_timing.py
```

Machine-readable results are in `results/sprint1/timing_audit/`.

## Decision

D039 establishes **conditional timing recovery** on injections for which the
real product was identified, the injection run recovered, a recovered window
was emitted and timing coverage passed. Its event-weighted pooled z-RMS and
coverage reproduce. It does not yet establish end-to-end recovery or a
host-balanced freeze-ready outcome rule for the stated single-planet population.

The pooled “pass” is not robust to the project's default equal-host weighting.
For TESS-SPOC 200-s PDCSAP, the event-weighted median z is +0.0819, but the
equal-host weighted median is +0.1026 and narrowly fails the prespecified
`|median z| < 0.1` criterion. The paired SPOC 120-s result similarly moves from
+0.0911 to +0.1098. This is not evidence of a scientifically important bias;
it is evidence that the estimand and weights must be fixed before a pass/fail
claim.

The sprint 2 timing repair should retain D039 as development evidence, not
freeze the current rule. It should implement one attempted-event ledger, apply
an explicitly host-balanced estimand, run the no-removal and shape/noise
controls, and replace D041's uncorrected log-mean-square endpoint model.

## Target and data-generating process

The scientific target is calibration of the pipeline's posterior timing error
for a new transit on an eligible host. That target has two distinct components:

1. end-to-end probability that a selected product, injected train and transit
   are identified and timed; and
2. conditional calibration of the timing posterior after all those stages
   succeed.

D039 simulates a transit train using the shape fitted to each real light curve,
removes real-transit windows, reruns blind BLS and a same-family shape fit, then
times the recovered windows. The observation process conditions success on
product-level period identification, run-level BLS/phase recovery and
window-level coverage. PDCSAP and SAP reuse cadences; paired FFI and 120-s
products share observations; phase draws and timing offsets are reused across
products and fluxes within a host. Every transit in one injection run shares
the refitted shape. Host resampling preserves much of this nesting, but it does
not define the point-estimand weights.

The implemented D039 point estimand is event-weighted among timed injected
windows. The alternative reported here gives each host total weight one and
each timed window within a host equal weight. The latter matches the project's
default planet/host-balanced scope more closely. Neither estimand includes
hosts or events that failed before a timing row was written.

## Reproduction and defects

| Finding | Status | Evidence and consequence | Sprint 2 repair |
|---|---|---|---|
| Pooled event-weighted statistics reproduce | Confirmed | FFI validation PDCSAP: 18 hosts, 263 timed windows, z-RMS 0.981105, 95.45% coverage 0.958175 and median z +0.0819. Independent calculations reproduce the decisive pooled and stratum z-RMS, median-z and 95.45%-coverage values in `validation_summary.json`. | Retain these as conditional, event-weighted development estimates. |
| The 7.4% failure rate mixes incompatible denominators | Demonstrated defect | It is `(2 failed real-product identifications + 3 failed injection runs) / (24 products + 44 recorded runs) = 5/68`. Six overlap-dropped runs are in the denominator but not the numerator; 24 coverage-excluded windows are not failures. This rate is neither product, run nor event recovery. | Report separate product-identification, planned-run and attempted-event rates. Never add products and runs into one denominator. |
| End-to-end recovery is not reconstructible | Demonstrated data-contract defect | Of 48 planned primary runs, 4 have no run row after product failure, 3 fail BLS, 6 are dropped for overlap and 35 succeed: planned-run non-success is 13/48 = 27.1%. The 35 successful runs yield 287 recovered-window rows, of which 24 fail coverage and 263 are timed. Truth events for the other 13 runs, and truths that never produced a recovered window, are absent. Only 18/24 selected hosts contribute timed primary injections. | Write one row per intended truth event before fitting, with stable attempt/run/truth IDs and terminal status. Derive recovery from that ledger. |
| Host weighting changes the formal primary verdict | Demonstrated estimand defect | Equal-host z-RMS and coverage remain 0.981 and 0.961, but equal-host median z is +0.1026 rather than +0.0819. For SPOC it is +0.1098 rather than +0.0911. The current cluster bootstrap resamples hosts but concatenates all their rows, so hosts with more timed windows retain more point-estimand weight. | Freeze an equal-host target. Average host MSE and host coverage; compute the median using per-event weights `1/n_host`; resample whole host/shape groups with equal cluster weight. If event weighting is scientifically preferred, state that different target explicitly. |
| The report's total timed-injection count is wrong | Demonstrated reporting defect | `injections.csv` contains 2,103 timed and 257 coverage-excluded rows, not the reported 2,096 timed injections. Primary and per-stratum point estimates still reproduce from the table. | Generate narrative counts directly from the final hashed tables. |
| Per-stratum non-readiness stands, but the recorded failure columns understate selection | Confirmed with qualification | The FFI A stratum has only 3/6 selected hosts with timed injections; B has 4/6 because four short-period runs were dropped, yet its recorded mixed failure rate is 0%. Stratum bootstrap intervals use only 3-6 contributing hosts. The negative verdict remains defensible; the intervals are descriptive, not calibrated population intervals. | Preserve all selected hosts in the attempt ledger and do not infer Tmag calibration from these strata. |
| Recorded matches are close, but one-to-one matching is not independently auditable | No observed bad match; demonstrated provenance defect | Using each product's recorded T14, every timed row has `|error| < 0.123` of the timing-window half-width and local epochs do not duplicate within a run. The code chooses the nearest truth without recording a truth ID, truth time, recovered centre or match distance, and does not apply the report's stated per-row half-width gate. A global phase check is not a one-to-one match assertion. | Record truth and recovered IDs/times, distance, threshold and unmatched/duplicate status; enforce a one-to-one assignment with a hard gate. |
| Real-window removal is a substantial, untested transformation | Demonstrated missing control; direction unresolved | From the recorded number of real windows, T14, exposure and cadence count, the nominal removed-cadence fraction has median 16.8%, IQR 12.3-20.9% and maximum 39.6%. Exact fractions need the timestamps. No committed same-phase no-removal result exists, so its effect on gap topology, BLS recovery, beta or coverage is unidentified. | Run the D041 no-removal control and report paired changes in recovery, white sigma, beta, z and coverage. Retain a separate shape-misspecification control; no-removal alone does not simulate spot crossings. |
| Same-family injected shapes remain conditional | Confirmed limitation | Generation uses the shape fitted from the real product; recovery refits the same transit family. This tests refitting and noise conditional on that family, not shape-family misspecification or full raw-to-PDC processing. | Add controlled duration/impact/limb-darkening perturbations or a realistic independent shape generator, and retain SAP/PDCSAP as paired sensitivities rather than independent replications. |
| Near-zero ICC does not remove the dependence design | Numerical claim reproduced, inference bounded | One-way ANOVA ICC for signed z is -0.014 by FFI host and -0.023 by FFI run (reported as zero); SPOC is 0.026 by host and 0.031 by run. ICCs of z-squared are also at or below zero in this conditional sample. These are point estimates from 39 contributing hosts with no interval. Signed-z ICC tests an additive group effect; it cannot establish absence of shared shape, scale, selection or photon dependence. | Keep host/shape-group clustering regardless of ICC. Report uncertainty or a variance-component/predictive check only if a dependence claim is needed. |

## D041 sizing and criteria

The confirmation-sizing script reproduces its stated counts and approximate
Monte Carlo standard deviations: 39 contributing hosts per product, with about
13.4-13.5 timed injections per host. It resamples only those successful hosts
and concatenates their events, so it sizes an event-weighted conditional
statistic. It does not size end-to-end recovery or the loss of hosts to product,
run and coverage failures.

The continuous Tmag model is not on the same scale as pooled z-RMS. It regresses
`log(mean(z^2)_host)` and exponentiates half the fitted value. This estimates a
geometric typical-host RMS. On D039 FFI data:

- event-pooled z-RMS = 0.951;
- equal-host arithmetic z-RMS = 0.960;
- geometric-mean host z-RMS = 0.918;
- fitted endpoint values are 0.994 at Tmag 9 and 0.841 at Tmag 13.5;
- the slope is -0.074 per magnitude, with a 90% host-bootstrap interval of
  approximately -0.16 to +0.01.

SPOC gives the reported -0.085 slope, but its 90% interval also reaches zero.
The apparent faint-star decline is therefore development evidence, not an
identified Tmag effect.

There is also a finite-event Jensen bias. Even if all z are independent
standard normal, `E[log(mean(z^2))] < 0`; D039 contributing hosts have only 2-31
timed injections. A deterministic negative-control simulation using 120 hosts,
30 per stratum and the observed injection-count distribution gives:

| Quantity | Nominal 90% interval coverage | Mean point estimate under true value 1 |
|---|---:|---:|
| Equal-host pooled z-RMS | 0.896 | 0.999 |
| Uncorrected log-MSE endpoint, Tmag 9 | 0.557 | 0.943 |
| Uncorrected log-MSE endpoint, Tmag 13.5 | 0.676 | 0.943 |
| Chi-square-bias-corrected endpoint, Tmag 9 / 13.5 | 0.881 / 0.880 | 1.001 / 1.001 |

The correction is a diagnostic, not the recommended production model: it
assumes independent zero-mean Gaussian z within each host. The experiment does
show that “30 clusters per stratum” is adequate for the simple pooled RMS in
this negative control but does not validate the proposed log-MSE endpoint
criterion. Sprint 2 should either model event-level squared residuals with
host-cluster uncertainty and a declared arithmetic target, or use a hierarchical
scale model whose posterior/predictive target is explicitly defined. If a log
host-MSE regression is retained, correct finite-event bias and validate endpoint
coverage under bias, heteroscedasticity, shared shapes and failed recovery.

The statement that a per-stratum 0.1-sigma bias criterion is unattainable should
also be narrowed. D041's simulation shows that it is poorly powered with 30
hosts per stratum; it does not show unattainability at every affordable size or
under every true bias. Retiring the point-estimate criterion is reasonable, but
its replacement must test a scientifically defined tolerance rather than only
count clusters.

## Recommendation and residual risk

1. Accept the D039 event-weighted point calculations and the conclusion that no
   extra pooled multiplier was supported on the successful development
   injections.
2. Do not accept “pooled freeze-ready” or 7.4% end-to-end failure. State the
   current evidence as conditional on successful identification, injection-run
   recovery, emitted window and timing coverage.
3. In sprint 2, repair the attempt/truth ledger first; then freeze the
   host-balanced estimand and rerun analysis from the existing development
   products. Add the no-removal, identification-boundary and shape/noise
   controls before any confirmation claim.
4. Replace or formally qualify D041's log-mean-square endpoint model before its
   criteria are used. Preserve D042's separate corrections to R3, R4, I1 and
   R8.

An additional reviewer is unlikely to change the reproduced D039 arithmetic.
Independent scientific review after the sprint 2 repairs would materially
increase confidence in the end-to-end denominator, matching contract and Tmag
criterion. A targeted replay is required to resolve the direction and magnitude
of the real-window-removal effect; table review alone cannot do so.
