# Pilot feasibility: establish ten traceable forecast–outcome histories

**Status: proposed pilot, not completed analysis.** The goal is to determine whether a bounded, historically valid forecast audit can be assembled. The ten names below are a screening queue, not an eligible scientific sample, and no real-data performance numbers are reported.

## 1. Start with an issued-forecast audit

The most economical starting point is one historical ExoClock release and genuinely later TESS transits. Prefer DRB first because its publication predates DRC and therefore offers a longer potential follow-up interval. Use the exact historical ephemeris as issued; refitting and recalibration are separate comparisons.

The release dates and acquisition routes are documented in [data_sources.md](data_sources.md). For the conservative journal-version implementation, DRB's issuance date is 2022-02-09 and DRC's is 2023-02-14. Outcome events must be later than the chosen version's issuance, not merely later than the observations used to estimate it. Apply a conservative next-day rule where within-day publication timing is unknown.

A preprint-based analysis could start earlier, but it must use the exact preprint table and verified public-availability evidence. Do not automatically use arXiv submission time as the moment the numerical forecast became public.

## 2. The immediate scientific precedent

ExoClock IV already evaluates DRB/DRC forecasts against TESS transits acquired after 2022-01-01. Its Table 5 reports coverage by timing-error threshold; the authors explicitly mark the DRD comparison as optimistic because those measurements contributed to DRD. This is a direct predecessor to the project, not merely an ephemeris-update paper. [Kokori et al. 2026, §5.1 and Table 5](https://doi.org/10.3847/1538-4365/ae3238); [readable full text](https://arxiv.org/html/2511.14407v1).

The pilot should support an extension involving one or more of:

- Strict separation between forecast issuance and later events.
- Dependence of accuracy and calibration on actual forecast horizon.
- Planet-balanced estimates and uncertainty that respect repeated transits.
- Proper scoring of predictive distributions, not coverage alone.
- A bounded connection between uncertainty and the length of an observing window.
- Explicit treatment of missing covariance and measurement uncertainty.

The aim is to find a useful increment to this existing programme. A change of statistical terminology alone would not establish novelty.

## 3. Define two clocks for every prediction

Retain both of the following:

- **Operational horizon:** time from the adopted public issuance of that numerical forecast to the outcome event.
- **Extrapolation gap:** time from the last observation used to construct that forecast to the outcome event.

Also retain **reference-epoch distance**, the number of cycles from T0. It is needed for uncertainty propagation, but a centred T0 can fall years before publication. It is not interchangeable with either horizon above.

This distinction should become a diagnostic figure: a timeline showing the last input, reference epoch, issuance and subsequent outcomes for each pilot planet.

## 4. Ten provisional screening targets

Every planet below occurs in the published 180-planet DRB ephemeris table. Presence was checked in [the version-specific Appendix B](https://arxiv.org/html/2110.13863v1). Their exact values have **not** been reconciled against the journal table or OSF file. Post-issuance TESS products, exposure independence, historical flags and complete covariance have **not** been verified for any row.

| Queue | Planet | Proposed pilot role | Specific question before admission | Eligibility now |
| --- | --- | --- | --- | --- |
| 1 | HAT-P-12 b | Ordinary short-period candidate | Can the source-version ephemeris be linked to complete later TESS transits? | Not yet eligible |
| 2 | HAT-P-27 b / WASP-40 b | Candidate plus alias-resolution check | Confirm the catalogue aliases refer to the same system and preserve the exact source label. | Not yet eligible |
| 3 | HD 209458 b | Candidate with heterogeneous published observations | Identify independent later exposures and account for duplicate timing publications. | Not yet eligible |
| 4 | WASP-52 b | Ordinary candidate | Establish the historical quality and timing flags rather than assigning current ones. | Not yet eligible |
| 5 | WASP-69 b | Ordinary candidate | Verify available TESS sectors and whether a useful complete-transit outcome exists. | Not yet eligible |
| 6 | WASP-74 b | Ordinary candidate | Confirm the model version, time standard and availability of outcome metadata. | Not yet eligible |
| 7 | WASP-80 b | Ordinary candidate | Check whether independent observations span more than one forecast-horizon bin. | Not yet eligible |
| 8 | WASP-43 b | Pre-flagged noise challenge | DRB flags unusual residual behaviour; assess the published warning before scoring a simple linear forecast. | Challenge only; not yet eligible |
| 9 | Qatar-1 b | Flag-history challenge | Reconstruct the information available at each issue date; later classifications differ across ExoClock releases. | Challenge only; not yet eligible |
| 10 | WASP-12 b | Known-nonlinearity positive control | DRB explicitly discusses its nonlinear ephemeris; use to test exception handling, not to inflate failures in an ostensibly unflagged cohort. | Challenge only; not yet eligible |

DRB's warnings for WASP-43 b and WASP-12 b are in its §4.2. ExoClock IV discusses the change in Qatar-1 b's flag in §5.4.1 [DRB full text](https://arxiv.org/html/2110.13863v1), [DRD full text](https://arxiv.org/html/2511.14407v1).

The HAT-P-27/WASP-40 alias is a provisional cross-match to verify against catalogue identifiers, not permission to merge records automatically. No candidate is assumed dynamically stable because it appears in the ordinary queue.

These familiar objects are appropriate for debugging provenance, not a representative sample. The eventual study cohort should come from the complete historical release and predeclared criteria. Do not select the final sample based on small or large observed forecast errors.

## 5. Six pilot work products

### A. One immutable forecast artifact

Acquire DRB's original files or a verified journal/preprint table. Record URL, DOI, exact version, hash, original precision, the documented release date and the source of that date. Preserve originals read-only.

Compare at least three transcribed records independently with their source. Confirm whether the paper and machine-readable product give identical numerical values. If they differ, retain separate forecast IDs and explain the version choice.

**Acceptance:** a reviewer can reconstruct every forecast parameter without relying on the current live catalogue.

### B. One documented TESS product per admitted target

Query MAST using verified target identifiers. Save the observation and product metadata before downloading. Start with existing light curves. Inspect timestamps, finite integration time, gaps, quality flags and actual coverage of ingress, mid-transit, egress and baseline.

A single TESS sector may contain several transits. Preserve event-level identities, but treat the planet as a cluster in population inference. Distinct photometric pipelines applied to the same cadence are repeated reductions, not additional independent transits.

**Acceptance:** every measured outcome has an exposure lineage and is later than its forecast's issue date.

### C. A prediction-independent outcome measurement

Initially use one reproducible light-curve-fitting approach and predeclared quality rules. Inspect a modest subset visually. Use a timing search region broad enough that a displaced transit is not excluded by the forecast being tested.

Permit contemporary calibration of outcome observations, but record it. Avoid a narrow timing prior centred on the historical forecast. Avoid fitting an ephemeris jointly to training and test events and then calling the resulting test-event mid-times independent measurements.

Later-release catalogue timings can be a convenient first comparison. They are not automatically unbiased outcomes: shared transit-shape parameters, clipping, acceptance against neighbouring timing measurements and reprocessing should be documented.

**Acceptance:** changing the tested forecast within a reasonable range does not mechanically pull the measured transit midpoint along with it.

### D. A pairwise eligibility ledger

For each proposed forecast–outcome pair, complete:

| Check | Required status |
| --- | --- |
| Exact forecast version and date basis recorded | Pass |
| Event occurred after forecast issuance and training boundary | Pass |
| Forecast and observation time standards harmonised or explicitly excluded | Pass |
| Planet identity and cycle count unambiguous | Pass |
| No overlapping input exposure or reused timing measurement | Pass |
| Outcome quality selected without looking at forecast error | Pass |
| Covariance and uncertainty convention known, or comparison routed to a declared sensitivity-only analysis | Pass or labelled sensitivity |
| Historical timing flags and current retrospective knowledge kept separate | Pass |
| Missing/failed outcomes retained in the screening denominator | Pass |

Use explicit failure codes such as unknown_issue_date, overlap_unresolved, unknown_time_scale, partial_transit, epoch_ambiguous, covariance_missing and no_public_followup. Missing fields should cause an ineligible or limited-use state rather than being silently imputed.

### E. A small end-to-end diagnostic report

Before population conclusions, produce:

1. The four-date timeline described above.
2. A source-version ephemeris projected to each later event.
3. O–C residuals in minutes, with both forecast and outcome measurement uncertainties visible.
4. Standardised residuals using the appropriate convolved observation-prediction distribution.
5. Coverage and a proper score with planet identities visible.
6. A count of all candidate pairs, exclusions and unresolved cases.

Ten planets can validate the workflow. They cannot establish precise population coverage of extreme prediction intervals. Do not turn a few unusual cases into a claim about all exoplanet ephemerides.

### F. A feasibility decision and next cohort

Proceed to a larger fixed cohort only if the source version, dates, timing conventions and independence are tractable for several ordinary candidates. A practical next step is a 30–50-planet development cohort, followed by a separately frozen evaluation cohort or later time block. The exact size should follow a precision/power calculation and source availability.

If most candidates fail because historic covariance or lineage is unavailable, change the estimand transparently:

- A point-prediction audit can still be possible when interval calibration is not.
- A restricted full-covariance subset can test distributional calibration.
- A reconstruction experiment can compare modelling strategies, with a different claim from evaluating issued forecasts.
- A data-provenance methods product may be useful if it establishes a concrete limitation that affects existing conclusions.

Do not manufacture missing dates or a zero covariance to preserve a preferred study design.

## 6. Sampling and missing-follow-up considerations

The population to which results apply should initially be the defined historical-release cohort with documented eligible follow-up. It is not automatically all confirmed transiting planets.

Track the whole screening frame: targets without TESS coverage, targets observed but without a usable transit, and sources whose provenance cannot be resolved. Report how the included sample differs in period, magnitude, transit depth, prior observing baseline, forecast uncertainty and historical warnings.

Ground-based follow-up is often scheduled around an existing forecast. A large forecast error can therefore cause incomplete or missed transits. Successful-timing catalogues alone cannot estimate that operational failure rate without information about attempted observing windows. TESS long-baseline observations help investigate this issue, but their target selection and temporal coverage still need description.

A missing record is not a measured failure. A fully observed window with a detectable transit absent under a predeclared search procedure can be informative; it requires separate modelling of coverage and detectability.

## 7. Decisions to settle after the pilot

- Which exact historical artifact defines the primary issuance?
- Which short-period giant-planet criteria are scientifically appropriate and available at that date?
- Are historically flagged systems excluded from the primary cohort or included as a separate prespecified stratum?
- Which covariance conditions permit primary calibration scoring?
- Which measurement-reduction and quality rules are fixed before the final evaluation?
- Which single endpoint will be primary, and how many horizon bins can the sample support?
- Can an observing-window analysis use actual attempted windows, or should it remain a clearly labelled model-based utility calculation?

These are decisions the pilot is intended to inform. The repository's main protocol should record the eventual answers before inspecting the final cohort's results.

## 8. What is established now, and what remains untested?

**Established from primary sources:** historical ExoClock ephemeris tables exist; their journal dates can be distinguished from input cutoffs; OSF deposits are identified; MAST exposes relevant provenance metadata; the live ExoClock endpoint is documented; ETD now has a current VarAstro route; and ExoClock IV contains directly relevant prior validation.

**Not yet established:** successful bulk retrieval of OSF products; exact historical file schemas or licence terms; complete covariance availability; ten targets with eligible subsequent events; a clean training–test exposure map; or any evidence that the proposed recalibration improves a forecast.

This is enough to start disciplined research. The next agents should resolve those empirical uncertainties rather than interpreting the seed as a finished feasibility demonstration.

