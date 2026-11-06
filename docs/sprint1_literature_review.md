# Sprint 1 literature, novelty and release-availability review

**Source freeze:** 6 November 2026. **Protected photometry:** not accessed.

## Decision

**Continue, but narrow the claim.** The defensible candidate contribution is not
the first retrospective test of transit ephemerides, the first use of TESS or
HST timings to update a forecast, the first propagation of epoch-period
covariance, the first heavy-tailed timing model, or the first use of proper
scores. It is the combination of:

1. exact, publicly available issued ephemeris artifacts and explicit forecast
   origins;
2. probabilistic evaluation of measured outcomes with forecast and outcome
   uncertainty kept distinct;
3. a proper interval score as the primary comparison, with log score as a tail
   diagnostic;
4. planet-balanced summaries and host-cluster uncertainty; and
5. a correction trained before, and evaluated without change on, a later
   investigator-unseen block.

No screened paper performed that complete task. This is a bounded search
finding, not proof of absence. OpenAlex returned and this review screened all
80 works it listed as citing ExoClock III and both works it listed as citing
ExoClock IV. Semantic Scholar returned 59 and 1, while Crossref reported 90 and
3 citations respectively. The disagreement proves that no one route is a
complete citation graph. ADS enumeration was unavailable because no API token
was configured.

The strongest immediate restriction is empirical rather than bibliographic:
the existing DRC timing file does not establish a historically available
DRB-error training set before DRC issuance. A release-transfer analysis based
on those rows is a present-day, event-date proxy unless first-public dates are
reconstructed independently.

## Scientific question and estimand

The scientific question is whether a population correction learned from prior
forecast errors improves the predictive reliability of the next issued
ephemeris release. The proposed primary estimand is the paired change in
planet-balanced, issued-SD-standardised 95% interval score between the issued
Gaussian forecast and a correction fitted using information available before
the target release. Secondary estimands are coverage, width, log score and the
fraction of planets improved. Host-cluster resampling is intended to represent
dependence among planets and repeated transits associated with the same host.

The forecast-generating process is a catalogue-level fit of a linear ephemeris
to heterogeneous timings. The observation process is a selected set of usable
transit mid-times, with measurement uncertainty, common light-curve/exposure
lineage, shared fitted shapes and possible timing variation. The experimental
unit for release transfer is a planet forecast; transits are repeated
measurements, not independent forecast replicates. The scale of inference is
the historically defined release cohort or a declared supported subset, not
all transiting planets and not attempted observations that failed to yield a
catalogued timing.

Key uncertainties are missing issued `Cov(T0,P)`, timing measurement error,
between-planet forecast heterogeneity, outcome selection, repeated-exposure and
host dependence, unknown per-row first-public dates, and a small effective
sample for the only currently identifiable post-DRB/pre-DRC TESS proxy.

## Exact release availability

Official OSF API logs resolve an ambiguity in D012-D013. The following dates
are first verified public availability of the exact named files under one
explicit assumption: an OSF `made_public` action plus a file already present,
or a file added to an already-public node, makes that file publicly retrievable
at the later timestamp. The logs establish availability, not discoverability,
and do not establish earlier private sharing.

| Release | Exact artifact | File timestamp | Node-public timestamp | Strict public anchor |
|---|---|---:|---:|---:|
| DRB | `updated_ephemerides.txt` | 2021-10-27 12:03:15.545999 UTC | 2021-10-13 14:33:41.786917 UTC | **2021-10-27 12:03:15.545999 UTC** |
| DRC | `catalogue_of_ephemerides.txt` | 2022-09-27 15:25:16.186146 UTC | 2022-05-30 12:42:23.267781 UTC | **2022-09-27 15:25:16.186146 UTC** |
| DRD | `catalogue_of_ephemerides.txt` | 2025-11-17 23:25:12.850553 UTC | 2025-11-18 09:43:24.090310 UTC | **2025-11-18 09:43:24.090310 UTC** |

DRB and DRC were uploaded to nodes already public. DRD was different: its files
were uploaded while the node was private, so the 17 November upload is not a
public issue date. The public transition on 18 November is nevertheless much
earlier than the 11 February 2026 journal date and supports a sharper strict
Track A anchor. It does not relax the user instruction to leave all post-18
November 2025 light curves unopened until protocol freeze.

The source records and exact API routes are in
`data/raw/sprint1_literature/osf_release_metadata_2026-11-06.json`; the compact
decision table is `results/sprint1/literature/release_availability.csv`.

## Can the DRB to DRC transfer be historical?

Not from the released DRC timing file alone. On the already-public DRC node,
`catalogue_of_ephemerides.txt` was created at 15:25:16.186146 UTC and
`all_mid_time_data.txt` at 15:26:09.374125 UTC: the timing table followed the
forecast by 53.188 seconds. Its schema is:

`planet, Tmid (BJD_TDB), Tmid uncertainty (days), source, ID`.

It contains no observed-at UTC, first-available UTC, retrieval UTC or source
version field. Event time is not availability time.

There is a useful nearest proxy. Restricting the DRC file to DRB planets and to
events after the DRB exact-artifact release but before DRC gives 311 nominal
rows from 63 planets: 203 `space` rows from 16 planets, all with `_TESS` IDs,
and 108 `exoclock` rows from 54 planets. The rows span only 27 October to 31
December 2021 because the DRC input closes at the end of 2021. Six rows are on
the DRB release date. Excluding that civil day conservatively leaves 305 rows:
200 TESS and 105 ExoClock. The exact boundary needs a validated BJD_TDB-to-UTC
comparison with location/barycentric terms rather than the simple Julian-date
mapping used for inventory.

The 108 ExoClock rows collapse to 89 planet-epoch-date units because some
filters or reductions share an event. They cannot be treated as independent.
The TESS subset is observationally more homogeneous but has only 16 planets.

**Recommendation for sprint 1:** use TESS-only as the primary nearest-proxy
release-transfer stress test and the mixed-source set as a sensitivity, unless
MAST product-release and historical ExoClock publication timestamps are
reconstructed. Label both `event_date_proxy`, not availability-aware Track A.
If those 16 planets cannot support stable refitting and host-aware uncertainty,
the release-transfer conclusion should be `not identified`, not extrapolated
from the much larger event count.

## Forward-citation screen

The row-level screen is
`results/sprint1/literature/citation_screen.csv`. It contains 82 records: the
complete OpenAlex results returned on the search date (80 citing ExoClock III,
2 citing ExoClock IV). Fifty-nine were excluded at title level, 21 were checked
at abstract level, and two closest works were read at method level. Exclusion
at title level was reserved for clearly different targets such as atmospheric
spectroscopy, stellar characterization, instruments and non-exoplanet studies.
Timing, orbital-decay and ephemeris papers were screened at least at abstract
level.

The closest newly screened citing study is Ma et al. (2025), ExoEcho I. It fits
64 HST timings for 37 selected systems together with archival timings, fixes
most transit-shape quantities, and compares linear and quadratic ephemerides.
Its timing analysis uses iterative 3- or 5-sigma rejection, BIC, leave-one-out
refits and, for influential points, an enlarged error floor. This is important
prior art for timing-error sensitivity and influential-observation checks. It
does not evaluate a frozen issued forecast distribution, report a proper
forecast score, balance a catalogue by planet or host, or preserve a later
unseen block. See the [full methods](https://arxiv.org/html/2501.05704#S3).

ExoClock IV remains the direct benchmark. Section 5.1 and Table 5 compare DRB,
DRC and DRD predictions with later TESS timings using pooled fractions within
one to four nominal standard deviations. The authors explicitly identify the
DRD comparison as optimistic because those timings contributed to that
release. It does not fit and transfer a recalibration, use a proper score,
balance planets or hosts, or reserve an investigator-unseen evaluation block.
See the [inspected arXiv version](https://arxiv.org/html/2511.14407v1#S5.SS1)
and [version-of-record DOI](https://doi.org/10.3847/1538-4365/ae3238).

Other forward citations refine individual or small sets of systems, search for
TTVs or orbital decay, rescue lost ephemerides, or use ephemerides to schedule
atmospheric observations. Those are scientific uses or refits, not empirical
calibration of an issued catalogue. The most relevant identifiers and screening
depths are retained in `results/sprint1/literature/source_ledger.csv`.

## Closest-method comparison

| Method feature | Closest prior evidence | What remains distinct, if achieved |
|---|---|---|
| Old forecasts against later timings | ExoClock IV Table 5 directly does this | No novelty by itself |
| Frozen archival predictions | Shan et al. (2023) use an August 2021 archive and later TOI timings | Population scoring without selecting only discrepant systems |
| Timing-error checks and extra scatter | Ivshina & Winn (2022); ExoEcho I | Prequalified outcome model carried unchanged into forecast evaluation |
| Joint covariance propagation | Kaye & Aigrain (2025) | Auditing missing issued covariance under explicit C2/C3 sensitivity, not claiming covariance propagation as new |
| Heavy tails or robust residuals | Agol et al. and the 5 November review's cited robust timing literature | Population correction of issued predictive covariance, trained historically |
| Proper interval and log scores | Gneiting & Raftery (2007) establish the general method | Application to issued transit-forecast distributions; the score itself is not novel |
| Planet/host weighting | No equivalent found in the screened forecast studies | Inference matched to planets and host dependence rather than timing-row replication |
| Unseen transfer | No equivalent found in the screened forecast studies | A frozen correction evaluated on a later investigator-unseen block |

The four rightmost claims above are conditional on successful implementation.
The literature cannot make an unstable, weakly identified or availability-
contaminated analysis novel by assertion.

## Availability, sampling and interpretation hazards

- The available outcome catalogue conditions on successful timing extraction
  and quality rules. It cannot estimate missed-transit or failed-observation
  probability without the attempt denominator.
- Multiple timings from a planet and multiple planets from a host are not
  independent replication. Exposure and shared-shape lineage take precedence
  over publication or database row identity.
- A reference epoch is not an issue date. Observation date, first-public date,
  forecast issue, retrieval and source version must remain separate.
- OpenAlex, Crossref and Semantic Scholar disagree materially. The forward
  screen is bounded to returned records and cannot support “no prior work
  exists.”
- ADS and Google Scholar complete exports were not obtained. The unresolved
  gap should remain visible at manuscript submission, although another keyword
  pass is unlikely to change the present sprint decision.
- Exact release availability does not recover missing `Cov(T0,P)` or turn a
  reconstructed C2 distribution into the distribution issued by ExoClock.

## Stop rule and next decision

The literature work has reached diminishing returns for sprint 1. It has found
the direct benchmark, screened a complete enumerated index result, cross-checked
two other indexes, read the decisive methods, and exposed a release-transfer
availability defect. More unstructured keyword searching would not resolve the
main scientific decision.

Proceed only with the narrow study: an availability-labelled, planet-balanced
proper-score audit with explicit covariance and outcome-error sensitivities.
For the DRB to DRC comparison, the next decision is analytical, not literary:
either reconstruct row-level historical availability and retain the historical
deployment interpretation, or accept the 16-planet TESS subset as a labelled
event-date proxy and treat failure to estimate transfer stably as an informative
null. Do not enlarge the claim by pooling the 108 heterogeneous ExoClock rows
as independent evidence.

## Reproducibility map

- Search routes and failures: `results/sprint1/literature/search_routes.csv`
- Full OpenAlex row screen: `results/sprint1/literature/citation_screen.csv`
- Primary-source comparison: `results/sprint1/literature/source_ledger.csv`
- Release chronology: `results/sprint1/literature/release_availability.csv`
- Transfer-proxy counts and assumptions:
  `results/sprint1/literature/release_transfer_proxy_summary.json`
- Immutable normalized API records:
  `data/raw/sprint1_literature/osf_release_metadata_2026-11-06.json` and
  `data/raw/sprint1_literature/citation_index_metadata_2026-11-06.json`
- Plain identifiers only: `references/identifiers_sprint1.txt`
