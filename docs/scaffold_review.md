# Independent review of the executable scaffold

**Review date:** 4 November 2026. **Scope:** the small Python scaffold in `src/transit_audit/` and `tests/test_core.py`. This review checks the implemented numerical demonstration and core guards against the proposed methods; it does not validate an astronomical dataset, a historical release reconstruction or a completed forecast audit.

## Outcome

The baseline Gaussian calculations are consistent with the methodological specification. The existing 24 tests passed before review. Three safeguards were strengthened and eight focused tests were added, including an integration follow-up. The final suite has **32 passing tests**, including an end-to-end synthetic run.

Validation command, from the repository root:

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## Confirmed behaviour

- Weighted linear fitting centres both epoch and time coordinates and uses the supplied timing errors without silently inflating them from residuals.
- Future timing variance includes the epoch–period covariance term. Re-pivoting transforms both parameters and covariance, preserving predictions.
- Independent evaluation measurement variance is added to forecast variance before coverage, PIT and proper scoring. The optional scale affects forecast uncertainty only.
- The logarithmic score uses seconds consistently. Interval scores penalise both width and misses, with positive timing error meaning an observed transit occurred later than predicted.
- Planet balancing prevents a densely observed planet from automatically dominating the point summary. The bootstrap resamples host groups while retaining all planet means in each group; it therefore preserves the intended planet-weighted ratio, rather than silently changing to equal host weighting.
- The synthetic demonstration is deterministic for a fixed seed in the same software environment, labels its outputs as synthetic and refuses to overwrite its existing result files.

## Defects and safeguards addressed

### 1. Reused measurements within the same chronological partition

The original split checked duplicate measurement IDs and training/test exposure overlap, but different measurement IDs could reuse the same exposures entirely inside training, evaluation or the quarantine set. That could duplicate information and produce false precision.

The selected-ledger splitter now rejects repeated atomic exposure IDs anywhere among its timing records. Alternative reductions must be reconciled upstream. Tests exercise repetition within all three partitions and across the cutoff.

**Identity convention:** an exposure ID must refer to target-specific underlying photon samples/cadences. A whole FITS file may contain several distinct transit events and is not a suitable atomic token. Different reductions of the same samples must retain the same lineage tokens. Distinct cadences from the same product are allowed; this is explicitly tested. Shared detector frame names across different targets should be namespaced by the extracted target/sample identity.

### 2. Ambiguous input types for provenance assertions

A bare string supplied as `exposure_ids` could be interpreted as a sequence of character IDs. Non-string members also lacked a clear rejection. The constructor now requires a nonempty list/tuple of nonempty strings and stores an immutable tuple.

The published-forecast guard now requires an explicit Boolean `True` for verified lineage, preventing an imported string such as `"false"` from passing because it is truthy. This checks the representation, not the underlying evidence: a caller remains responsible for establishing lineage.

The integration review also found that the guard's separate `training_exposure_ids` argument needed the same type discipline: a bare string could otherwise be split into characters and hide actual overlap. That argument now requires a list/tuple of nonempty strings. A focused test covers malformed inputs and overlap rejection for correctly typed sequences. Empty sequences remain accepted only alongside an explicit verified-lineage assertion; an empty list is not evidence that the forecast and outcome are independent.

### 3. Positive-semidefinite validation at very different variance scales

An eigenvalue tolerance relative only to the largest covariance entry could accept a correlation outside `[-1, 1]` when epoch and period variances differed greatly. The two-parameter covariance now uses the equivalent scale-aware condition `|cov(T0,P)| <= sigma(T0)*sigma(P)` with a small roundoff tolerance, after symmetry and diagonal checks. A regression test rejects an invalid correlation of 2 and accepts a correlation of 0.5 at the same strongly unequal scales.

## Important limits of the implementation

These are declared scope limits, not completed features:

1. Provenance checks are **necessary, not sufficient**, for independent evaluation. The code cannot determine whether a source date, time standard, cycle label, exposure lineage or Boolean assertion is true.
2. The core uses conservative UTC calendar-date boundaries. It does not convert BJD_TDB, HJD, UTC, observatory timestamps or publication timestamps. A production importer must establish their relationship and handle uncertain boundaries.
3. Duplicate reductions sharing exposure tokens are rejected; independent measurements of the same physical event still require event-level grouping or a declared joint measurement model upstream.
4. The simple planet-mean helper averages its supplied rows. For multiple forecast origins per planet, perform the protocol's equal-origin aggregation first; the demonstration has one origin per planet. Likewise, the bootstrap expects one input mean per planet in the relevant stratum.
5. The demo has 24 synthetic planets and one planet per host. The separate bootstrap test checks a multi-planet host. These are implementation checks, not evidence of empirical calibration or sufficient power for rare misses.
6. No historical archive adapter, actual ExoClock Table 5 reproduction, calibration-parameter estimator, general correlated-error fit, full light-curve model or telescope scheduling simulation is implemented by this scaffold.

The seed is therefore suitable as a tested starting point for the stated linear/Gaussian calculations and data-ledger discipline. Scientific conclusions must wait for the source audit, benchmark reproduction, cohort freeze and independent real-data evaluation.
