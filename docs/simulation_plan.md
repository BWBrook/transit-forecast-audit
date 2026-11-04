# Simulation and design-precision plan

**Status:** proposed, apart from the small executable synthetic demonstration.

The purpose is to discover what the evaluation can identify and what mistakes
can produce its apparent findings. Simulated parameter ranges become physically
grounded only after the metadata pilot; do not present artificial rates or
amplitudes as astrophysical estimates.

## Stage 1: numerical correctness (already exercised in tests)

- Exact linear data recover the analytic weighted solution and covariance.
- Recentring parameters and covariance leaves all forecasts invariant.
- Independent outcome measurement error is convolved with forecast error.
- Unknown covariance is not silently treated as zero.
- Chronological availability and atomic-exposure overlap checks reject leakage.
- Equal-planet summaries are not dominated by duplicated identical events.

The demo adds a deliberate late drift to half of 24 artificial systems. It is a
worked pipeline example only; it is too small and too stylised for study design.

## Stage 2: emulate the pilot's observation process

Use empirical training epochs, later observation windows, precision ranges and
release delays from the metadata pilot, while generating artificial physical
times and measurements. Keep a table of true event times separate from the
noisy observed estimates and the dates on which the latter become public.

| Scenario | Question answered |
|---|---|
| Constant-period truth with correctly known errors | Does the full evaluator attain nominal calibration? |
| Misreported training timing errors | Can earlier-error recalibration repair later forecast distributions? |
| Misreported evaluation measurement errors | Can the design distinguish measurement miscalibration from forecast miscalibration? |
| Omitted T0–P covariance / shifted pivot | How sensitive is a conclusion to incomplete published uncertainty? |
| Low-amplitude sinusoidal timing variations at varied phases | Can a short baseline hide coherent behaviour that becomes important later? |
| Small quadratic drift of either sign | How does unmodelled secular change affect different horizons? |
| Instrument/campaign offsets and correlated timing noise | Is host-only resampling adequate for the selected data? |
| Duplicate reductions of shared exposures | Does provenance handling prevent artificial precision? |
| Availability delays and later reprocessed historical data | Does a date-only split produce optimistic results? |
| Observing windows centred on old predictions | How strongly can successful-only selection mask forecast failure? |

Introduce complications separately before combining them. Include a completely
well-specified control in every run. A method should not be judged only on
scenarios designed to make its comparator fail.

## Stage 3: calibrator transfer

Generate an earlier calibration cohort and a later evaluation cohort with
controlled similarity or change. Fit only a scalar forecast-error multiplier
initially. Check its boundary behaviour, uncertainty and effect on proper scores.
Do not scale the known evaluation measurement errors merely to increase coverage.

Compare no correction versus the earlier-trained correction on the same held-out
pairs. Use host-level resampling and, if calibration uncertainty is material,
repeat fitting inside the outer resampling procedure. Add a different model only
when a prespecified failure mode motivates it.

## Stage 4: precision and cohort size

Simulate the actual nested structure: host, planet, forecast origin, campaign,
transit. Explore the recoverable number of independent systems and their uneven
event counts. For illustration, a design grid might contain 30, 60, 120 and 240
hosts, but actual sample availability determines relevant scenarios.

Report Monte Carlo uncertainty, interval width for the key coverage estimates,
and precision for the paired proper-score contrast. Choose the simplest lead-time
stratification that supports useful estimates. A small pilot cannot establish
precise three-sigma tail rates, irrespective of how many correlated timings it
contains.

## Deliverables and stopping condition

Each simulation run records a configuration hash, RNG seeds, code commit,
environment, truth parameters, observation process and evaluation outputs.
Write a short design report stating which inferences are recoverable, which
remain weak, and how this changes the final protocol. Stop expanding the matrix
once the concrete risks in the selected first-paper design are resolved.
