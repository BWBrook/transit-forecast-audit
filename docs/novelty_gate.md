# Novelty and feasibility decision

**Latest development decision (5 November, third turn):** continue the forecast
audit and outcome validation, without selecting the training-span rule or
per-outcome injection scale. Independent chronological resampling revealed
tail collapse and severe extrapolation failures. The known-shape timing pilot
is feasible but does not validate the complete outcome model. These adverse
findings strengthen the need for an untouched prospective test; they do not
establish improvement or novelty. See [the review](third_turn_review_2026-11-05.md).

**Review update, 2026-11-05:** continue the proposed prospective calibration
experiment under D029, without freezing it. Independent REML and stable
scale-mixture integration support the conditional development findings, while
tail labels, uncertainty qualification and the schedule inventory need revision.
Training span warrants chronological predictor validation. Heavy-tailed timing
likelihoods and scale mixtures are prior art; the candidate contribution remains
historically trained calibration of issued forecasts tested on an untouched block.
See [tranche-2 review](tranche2_independent_review.md),
[literature update](literature_update_2026-11-05.md) and D030–D033. Full citation
screening, outcome validation and protocol freeze remain open.

**Current decision (2026-11-04, after independent review): continue the development
pilot, with narrower claims. DRB/DRC Table 5 columns reproduce independently in
R; DRD differs by one count and Initial remains unreproduced. The candidate
contribution is an availability-aware forecast audit with validated outcome
uncertainty and a later untouched test. Variance separation is not yet identified,
the citation sweep remains incomplete, and the protocol is not frozen.**

See [independent review](independent_review.md),
[dated literature update](literature_update_2026-11-04.md) and D020–D024.
TESS-only uncertainty diagnostics and extra-scatter terms have prior art.
The original grouping chained across up to 379 days; a corrected local-linear
diagnostic still shows excess scatter but cannot attribute it uniquely to
measurement error. Covariance reconstruction is a conditional WLS sensitivity,
not recovery of the issued posterior. **Keep all post-2025-11-18 light curves
unopened until the protocol is frozen.**

### Decision record, pilot v1 (Claude)

Historical first-turn interpretation below; D020–D024 and the independent review
qualify items 1 and 3–5. In particular, 5.06% is a planet-balanced event failure
fraction, not the fraction of planets with any failure.

1. **Nearest result:** Kokori et al. 2026 (ExoClock IV) §5.1, Table 5. The
   definition was recovered from the arXiv v1 TeX source. It is reproduced
   exactly by `scripts/reproduce_table5.py` (DRB, DRC) and differs by one
   boundary measurement for DRD.
2. **Quantity we would estimate differently:** forecast calibration as a
   function of horizon, separated from measurement-error calibration. It would
   be planet-balanced and use only flags known at origin.
3. **Astronomical consequence:** for DRC, Table 5's 62% at 1σ and 1.7% 3σ
   misses are mostly the behaviour of TESS σ_Tmid, which are about 7–11% too
   small. Once flags are restricted to those known at origin and planets are
   balanced, about 5% of planets miss at 3σ. Ariel scheduling margins depend
   on the forecast term, which the published statistic barely isolates.
4. **Inputs:** OSF v1 artifacts with hashes; release-stated BJD_TDB;
   covariance is reconstructed and negligible (D016); outcome lineage is by
   date only.
5. **New outcome era:** TESS from 2025-11-19, after DRD's issue (D018). It is
   independent because it postdates every ExoClock release, but it requires
   our own frozen timing pipeline (T015).
6. **Precision:** the development era has 316 DRC planets under S2, giving a
   host-cluster CI for the planet-balanced 3σ miss of about ±2.5 pp. The size
   of the untouched era is not yet known (T016).
7. **Searches completed:** two quick web searches found no extension of
   Table 5. A systematic sweep of works citing ExoClock III/IV is outstanding.
8. **Decision:** continue. Revisit after T001 and Codex's independent
   reproduction.

Earlier seed decision: proceed to a small reproduction/feasibility pilot; do not yet
commit to a journal claim or a large data-ingestion programme.

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
