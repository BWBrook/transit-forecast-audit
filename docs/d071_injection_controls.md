# D071/R01 bounded flux-to-timing control

Codex (GPT-6.1-sol), 9 November 2026. **Design fixed before execution.**
This is a labelled synthetic interpretation check, not power analysis,
qualification, real-data validation or a replacement for the frozen verdict.

## Design submitted before any run

Twelve small runs, each with four intended transits (48 truth events), cross
two latent-error families, two host-like replicates and three flux scenarios.
Each replicate's latent error and white-noise realisation are paired across
the scenarios. Seed: `20261109`.

- Time grid: synthetic days 0–12, 120-second cadence, period 3 days,
  predicted centres 1,4,7,10 days. These are simulated coordinates, not
  astronomical observations or relabelled time standards.
- Physical injection shape: circular batman model through the frozen
  `sprint2_outcomes.model_train`, radius ratio .06, a/R*=10, inclination
  88.5 degrees, q1=.36,q2=.3. White flux noise SD=.003. The supplied
  catalogue period is exactly 3 days, while BLS searches the phase blindly.
- Family A: host-level errors drawn from N(0,60 seconds) using the fixed seed.
- Family B: fixed −50/+50 minute host offsets, a discrete two-point family
  rather than the M2 Gaussian/lognormal scale mixture. These are coherent
  phase offsets, not a physical TTV simulation.
- Scenario 1: complete cadence, white noise and correctly supplied flux errors.
- Scenario 2: the same flux/noise with a recurring 60-minute gap centred
  90 minutes after each *predicted* transit. Gaps do not follow the latent
  transit. This intentionally makes recovery depend on latent phase error.
- Scenario 3: the same gaps plus a shared asymmetric in-transit bump (25% of
  nominal depth, centred +0.2T14, width .12T14), red flux noise with a
  20-minute correlation scale and stationary SD=.001, and flux errors
  supplied at half their white-noise SD. This stresses shared shape and
  estimated-error misspecification; frozen beta/chi-square scaling may
  compensate partially and is not disabled.

The frozen `solution` and `time_windows` helpers execute actual BLS,
planet-level shape fitting, window coverage checks, local-baseline fitting,
profile-grid timing, beta/error estimation and integration flags. The compact
old `inject_run` ledger discards likelihood grids, so the wrapper calls its
same injection/measurement helpers directly and retains actual grids for the
shared `acceptance` support check. No new timing framework or fit is added.
One truth row is retained for every intended transit, including failed runs.
Truth-window matching uses the frozen one-to-one 60-minute rule.

Compare M0 and the frozen-form M2 (s=2.0469590063, median multiplier 1),
with forecast SD=60 seconds, as specified comparators rather than either
assumed truth. Report:

1. latent-truth scores on all intended events;
2. latent-truth scores on the accepted subset (selection alone);
3. measured-time scores without measurement convolution (naive target);
4. measured-time scores with the returned timing distribution convolved;
5. recovery/acceptance, timing error, reported precision, coverage, and within-run
   common timing shifts. All summaries preserve host-like replicate weighting.

The measured-time interval is not an observing window; latent and measured
scores have different targets. No inferential intervals, threshold tuning or
performance decision will be attached to this small simulation. Its job is to
show whether selection or shared-error assumptions change what gets measured
and scored, and to retain a valid negative result if the stress is absorbed.

## Execution status

Awaiting parent review of the concrete design. No synthetic fitting has yet
been run. Only read-only inspection of frozen interfaces has occurred.

## 9 November 2026 execution and results

The parent accepted and committed the design as `03fbf67` before any fitting.
The design-stage status above is preserved as history; the twelve runs are now
complete. `scripts/d071_injection_controls.py` used the retained frozen
measurement environment: Python 3.13.16, numpy 2.3.5, scipy 1.18.1,
astropy 8.0.2 and batman 2.5.3. Control scoring runs in that same environment;
the separate frozen evaluation environment is recorded as Python 3.13.16,
numpy 2.5.4 and scipy 1.18.1. Frozen helpers were imported read-only.

All 48 intended truths remain in `results/d071_controls/truth_ledger.csv`:
45 are accepted, one is rejected at the prior edge and two have unresolved
timing integration. All twelve products identify; there are no exceptions.
Forty actual non-Gaussian grids are retained locally with hashes in the
receipt and ignored in Git (about 8 MB, regenerable from the seeds). Compact
scores, run diagnostics and target comparisons are retained separately.

| Latent family / flux scenario | Accepted / intended | Median timing error, seconds | Median reported sigma, seconds |
|---|---:|---:|---:|
| Gaussian / complete white | 8 / 8 | +33 | 268 |
| Gaussian / phase gaps | 8 / 8 | +479 | 306 |
| Gaussian / gaps + shared shape/red/error stress | 8 / 8 | −268 | 277 |
| Two-point / complete white | 8 / 8 | +24 | 229 |
| Two-point / phase gaps | 6 / 8 | −184 | 272 |
| Two-point / gaps + shared shape/red/error stress | 7 / 8 | −935 | 318 |

These pooled error medians describe accepted event errors; they are not
independent-event uncertainty estimates. The score summaries instead average
events within each host-like replicate and give defined replicates equal
weight, recording how many remain. Both Gaussian latent draws happened to be
positive: +48.625 and +10.070 seconds. This tiny sample is not a balanced
population experiment and no seed was changed after seeing it.

The three core points are visible in the actual extraction:

1. **Targets differ even with complete white-noise flux.** In the Gaussian
   family, M2−M0 raw IS95 is +6.062 score-minutes on known latent truth,
   −50.333 if measured times are naively scored as exact, and −0.716 when
   convolved with the reported timing distribution. This is one finite
   realisation, not an estimate of expected superiority. It demonstrates why
   a measured-time comparison cannot simply be described as a latent-time one.
2. **Cadence and shared fits matter.** The fixed forecast-phase gaps preserve
   all eight Gaussian-family events but shift the median measured timing
   error; the additional shared-shape/red/error stress changes it again. In
   the two-point family the gaps accept six of eight truths. For the late
   replicate the fitted duration shortens from about 144 to 81 minutes,
   despite the unchanged injected shape; two events fail integration. Under
   the combined stress the duration is about 89 minutes. Acceptance and
   precision are therefore outputs of the fit, not independent labels on
   a random sample of timing errors. The accepted-subset latent mean contrast
   happens to remain unchanged here because the ±50-minute latent score
   contrasts are symmetric; this run does not establish selection bias of
   that mean in general.
3. **Score gain is not capture.** In the discrete ±50-minute family, neither
   model covers any latent truth at 95%. The latent M2−M0 raw score is
   nevertheless −115.182 score-minutes: a smaller continuing miss penalty.
   Convolved measured scores also give zero 95% coverage in every scenario.
   These are interval-score units, not allocated observing minutes.

The convolved measured scores use the returned **reported conditional timing
distribution**. It is not called the true measurement distribution, especially
under the deliberate shape/red-noise misspecification. No significance
intervals or improves/worsens decisions are attached to these twelve runs.
They do not establish a rate for real TESS data or qualify a new timing rule.

## Verification and limits

The measured path exercised blind-phase BLS, fitted shared shape, coverage
checks, profiled local baseline, timing grids, beta/chi-square scaling,
integration flags, one-to-one truth matching, the shared acceptance/support
contract and the P/4 cycle check. Three small synthetic unit tests check
phase-dependent coverage, latent-versus-convolved coverage and the analytic
Gaussian convolution's units/width. All pass in the evaluation environment.

The receipt's design-document hash records its original text at execution,
which is available at `03fbf67`; this execution section was appended afterwards.
Runtime source hashes and retained grid hashes are recorded. No raw FITS,
headers, new host sample, network request or S74–S97 outcomes were read.
