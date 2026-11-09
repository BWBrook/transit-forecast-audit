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
