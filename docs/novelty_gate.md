# Novelty and feasibility decision

**Current decision: proceed to a small reproduction/feasibility pilot; do not yet
commit to a journal claim or a large data-ingestion programme.**

## What is already established

ExoClock IV, Section 5.1/Table 5, evaluates older DRB/DRC ephemerides against later
TESS observations. Other studies compare archival predictions with new timings,
model ephemeris deterioration, or refine predictions. The literature review
identifies the closest examples. Neither retrospective testing, uncertainty
inflation nor correct covariance propagation can be advertised as novel alone.

## Candidate extension and the evidence needed

| Candidate | Why it might matter | What would defeat or narrow the claim? |
|---|---|---|
| Issued-artifact audit with explicit availability dates | Tests predictions that could have been used at the decision date | Existing work already provides the same benchmark; historical artifacts/lineage cannot be established |
| Lead-time-specific calibration and precision with planet-balanced weighting | Resolves performance hidden by pooled, unevenly replicated observations | Adequately studied already; too few independent systems within horizons |
| Earlier-error calibration evaluated in a later untouched era | Tests whether a practical uncertainty correction transfers | Correction already tested equivalently; no independent final era; weakly identifiable forecast/measurement errors |
| Auditable selection and covariance sensitivity | Establishes the scope and robustness of a population conclusion | Merely restates known caveats without changing an inference or providing a useful resource |

## Decision record to complete after the pilot

1. Exact nearest result, citation, table/figure and code location.
2. Exact empirical quantity we propose to estimate differently.
3. One paragraph explaining the astronomical consequence of that difference.
4. Available inputs, dates, lineage and uncertainty information supporting it.
5. The new outcome era, if any, and why it is independent.
6. Precision attainable with the actual number of planets/hosts.
7. Specific prior-art searches completed, including citing papers.
8. Decision: **continue**, **narrow to a benchmark/reproduction**, or **change the
   question**. Record rationale in `coordination/decisions.md`.

Negative findings from this gate are useful. Do not compensate for an unproven
scientific contribution by adding complex machine learning, many model classes
or an enormous scraped dataset.

## Suggested search questions

- Has an exoplanet study published coverage conditional on both lead time and
  historical training span, using independent future events?
- Has the same literature used proper distributional scores and equal-planet
  aggregation, or tested an empirically calibrated rule on a later era?
- Does the existing benchmark include measurements that postdate the data cutoff
  but predate the issued artifact, and is that distinction already analysed?
- How are unsuccessful or unmeasurable transits represented?
- Which later studies have already extended ExoClock IV Table 5?

Do not interpret a failed keyword search as proof of absence. Read the relevant
methods, appendices, release scripts and citing studies.
