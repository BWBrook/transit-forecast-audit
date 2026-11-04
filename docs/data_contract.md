# Data contract and historical information boundaries

This is the **proposed production contract**. The executable `Timing` dataclass
implements only a strict, normalised subset. Do not describe the full contract
as an implemented archive adapter.

## 1. Preserve the original evidence

Each downloaded artifact gets a stable local source ID, exact URL/DOI, repository
file/version identifier, retrieval timestamp in UTC, byte size, SHA-256 hash and
licence/attribution information. Keep the original bytes unchanged. A hash proves
which bytes we used; it does not prove when those bytes became public.

Use one source-manifest record per file/version. A repository-level DOI can point
to evolving files; record file-level history where available. For a transcription
from a published table, record the exact article version, table/page, original
printed values/precision and two independent transcription checks.

## 2. Distinguish five times and the reference epoch

| Field | Meaning | Evidence required |
|---|---|---|
| `observed_at_utc` | When the outcome observation occurred | Exposure headers or source event record |
| `measurement_first_available_at_utc` | When this measurement or reproducible input product could be accessed | Publication/archive history, with timestamp precision |
| `forecast_issued_at_utc` | When this exact forecast artifact was public | Artifact release, publication or verified announcement |
| `training_last_observed_at_utc` | Latest observation contributing to the forecast | Input list, with uncertainty if incomplete |
| `retrieved_at_utc` | When our project obtained the artifact | Download log |
| `reference_epoch_number`, `t_ref_bjd_tdb` | Coordinate pivot used to express the ephemeris | The ephemeris itself; **not** evidence of issuance |

Also record the training **availability cutoff** for chronological refits. A
measurement observed in 2020 but first published in 2023 is unavailable for a
2021 refit unless an earlier public input product and the declared reduction
procedure make that route legitimate. Label a later reduction of historical
photometry as a reconstructed analysis, not the original published prediction.

Every date needs `evidence_source_id`, `date_kind`, `precision` (instant/day/month)
and a status such as verified, conservative bound or unknown. Do not replace a
missing first-public date with the date our script downloaded the file.
Same-day ordering is ambiguous if only dates are known; exclude that boundary
from strict Track A or use a verified timestamp. The core checker conservatively
requires the outcome to fall on a later UTC calendar date.

## 3. Forecast table

One row identifies one forecast product for one planet and origin.

| Field group | Required contents |
|---|---|
| Identity | `forecast_id`, canonical `planet_id`, `host_id`, source aliases, `track` R/A/B, `release_id` |
| Artifact | `source_id`, version, table/row locator, exact original parameters and units |
| Timing | `time_system`, reference location/frame, `reference_epoch_number`, `t_ref_bjd_tdb`, `period_days` |
| Uncertainty | Marginal errors, asymmetry, full covariance or posterior sample locator, `covariance_status`, `uncertainty_convention` |
| Historical boundary | Issue evidence, training observation range, input availability cutoff, input record/exposure IDs |
| Scope | TTV/decay flag and evidence **as known at origin**, model form, original quality flags |
| Audit | `lineage_verified`, `normalisation_verified`, `eligible_for_point_score`, `eligible_for_distribution_score`, reason codes |

Do not join a period from one reference to T0 from another. Do not use a current
composite archive row as though it were a historical joint fit. Preserve the
source rounding; rounding may matter for long-baseline extrapolation.

Covariance uses day-squared units for the parameter vector `(T_ref, P)` when
epoch number is dimensionless. Both the matrix and its pivot must be preserved.
When covariance is absent, retain null and the declared sensitivity tier. A
printed weighted-centre epoch does not itself prove a covariance is exactly zero
under every fitting model or posterior.

## 4. Timing, event and exposure tables

These identities are different:

- **Event:** one physical transit of a particular planet.
- **Exposure:** target-specific underlying photon/cadence samples used to measure
  part of that event.
- **Reduction:** a pipeline's processing of those samples.
- **Timing estimate:** a fitted midpoint and measurement likelihood from one or
  more exposures/reductions.
- **Publication/catalogue record:** a location where that estimate is reported.

Two papers may contain one timing estimate. Two reductions may contain the same
photons. Two observatories may produce genuinely separate measurements of one
event, with a common physical midpoint and potentially different systematic
errors. Never resolve these distinctions using only row names.

**Atomic exposure IDs in the code** mean target-specific original cadence sets
or their explicitly recorded time windows, e.g. an immutable TESS product ID plus
the cadence indices used. A whole multi-transit FITS file is too coarse: disjoint
events can legitimately use disjoint segments of it. Different reduction IDs
are too fine: they can hide reuse of the same samples. Upstream reconciliation
must map overlapping selections to a shared identity (or compare intervals)
before the simple set-based core checks can detect them.

Each normalised timing requires measurement/event/planet/host IDs, verified epoch
assignment relative to a declared mapping, BJD_TDB midpoint, uncertainty or
measurement likelihood, source, underlying sample identities, observation and
availability evidence, reduction version, fitted priors and quality metadata.

For multiple estimates of the same event, select one by a prespecified,
outcome-blind rule or fit an appropriate joint measurement model. The simple
weighted fit assumes independent measurement errors. It must not receive
unresolved repeated reductions or arbitrarily duplicated measurements.

## 5. Time and epoch normalisation

Retain the source time value, numerical offset (such as BTJD), time scale, light-
travel reference and conversion provenance. BJD and HJD identify different
reference locations; UTC and TDB identify different time scales. Neither the
letters `JD` nor a number close to 2.45 million establishes all of this.

If conversion is necessary, use validated astronomical software with the target
coordinates, observer location/trajectory, exposure timestamp convention and
appropriate ephemeris. Record software/data versions. Never apply a universal
offset to HJD and call it BJD. [Eastman et al. 2010](https://doi.org/10.1086/655938).

Keep integer epoch mappings explicit between historical releases. Do not wrap
large errors modulo the period or search for the cycle assignment that produces
the most favourable score. If the cycle is ambiguous, the first-paper simple
scope excludes that pair with a reason; a later analysis can use a mixture.

## 6. Forecast–outcome pairs

One pair record carries:

`pair_id`, `forecast_id`, `measurement_id`, `event_id`, `planet_id`, `host_id`,
verified forecast-relative epoch, `origin_id`, operational lead days, days since
last training observation, baseline-normalised age, uncertainty tier, quality
status, inclusion/exclusion reason, and the exact rule/version that created it.

An eligible Track A pair requires:

1. A recoverable and identifiable issued artifact.
2. Outcome observation strictly after the documented issue boundary.
3. Outcome exposures absent from all forecast inputs.
4. No constraining use of the tested forecast as an outcome timing prior.
5. A validated time/epoch convention.
6. Sufficient uncertainty information for the selected score.
7. Eligibility decided independently of the realised residual.

Store unavailable lineage as unknown, not as an empty list meaning verified
disjointness. The executable checker has a separate verified-lineage flag, but
the human/source audit must justify it.

## 7. Observation opportunities and missingness

A production opportunity table would record eligible future events, space-camera
coverage or ground-based attempts, usable baselines, gaps, weather/quality where
known, detection status and why a midpoint could not be measured. This separates
no observation, unsuccessful capture and observed but unmeasurable transit.

Until such denominators are recoverable, label estimates **conditional on a
usable independent later timing being available**. Do not fill missing outcomes
with zero errors, and do not infer telescope-time savings from successful events
alone.

## 8. Templates and machine checks

Header-only CSV templates under `data/templates/` define initial exchange files.
They contain no real records. List-valued fields use JSON arrays in CSV cells;
timestamps use ISO 8601 UTC. Boolean statuses remain strings/enums until an
adapter validates and converts them. Unknown values stay empty/null, never zero.

The current Python tests cover a normalised subset and several failure modes.
They do not validate the full CSV contract or resolve archive aliases. Adapter
tests must be added against small, attributed real fixtures after artifacts are
actually inspected.
