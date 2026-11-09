# T019: release-input information ledger and historical-source candidates

Codex (GPT-6.1-sol), 9 November 2026. This is a descriptive, outcome-blind
ledger from saved release tables and archive metadata. It does not fit a
triage rule, remeasure a transit or open any photometry/header, including
sectors 74–97. The frozen experiment remains unchanged.

## Deliverables and completion state

- `results/information_ledger/release_planets.csv`: all 180 DRB, 450 DRC and
  620 DRD ephemerides, with released timing counts, first/last observation,
  baseline, issued-line chi-square, correctly distinguished reduced chi-square
  and standardised RMS, origin release flags and missingness.
- `fixed_opportunity_ages.csv.gz`: 7,426 reference-release/planet opportunities
  on the fixed primary/extension event list. Each uses the DRD-predicted
  opportunity, not a measured outcome. Information age and age/baseline use
  released BJD_TDB inputs. Lead time is deliberately a coarse calendar-day
  difference, not a time-system or barycentric conversion.
- `origin_knowledge.csv`: 552 cohort/release rows. Origin release flags are
  source-specific criteria. Current NASA flags and companion candidates are
  dated metadata, never retrospective replacements for origin flags.
- `companion_period_candidates.csv`: release-period ratios where both names
  occur in a release, otherwise explicit unknown values. These are source
  leads, not a verified historical companion inventory.
- `external_metadata/`: a uniform screen of the complete cached NASA name/host
  table across all 184 targets/175 hosts, plus the saved current default-row
  references. It finds 215 cached planets on those hosts, 65 directed
  target/companion candidates affecting 32 targets, and eight current target
  TTV flags. All targets match. The candidate table retains parameter-source
  references/dates where the earlier query saved them; discovery publication
  references, exact historical confirmations and TTV discovery dates remain
  unknown until source curation. There are 46 release-specific period ratios
  among the candidate rows. No unsearched or absent current row becomes a
  historical negative.
- `source_chronology.json`, `summary.json`, `receipt.json`: exact chronology,
  all-source cutoff audit, summary and source/output hashes.

Internal numeric features are complete at the stated source scope. The uniform
external metadata candidate screen is complete; primary-source certification of
historical companion/TTV features is **not complete**. A triage rule must not
silently use the candidate-date fields as verified issue-time predictors.
No verified origin transit durations are present in the exact ephemeris/timing
inputs used here, so duration-normalised features stay unknown. A subsequently
measured or current catalogue duration cannot silently fill an origin feature.

## First forecast availability is not timing-table availability

Availability is the later of the source node's verified public transition and
the immutable-v1 artifact creation time, using the existing recorded source
manifest and OSF history check.

| Release | Timing artifact's lag after first forecast availability | Strict exact-origin timing-derived features |
|---|---:|---|
| DRB | 44,925.965 s (about 12.5 h) | Not verified from the saved ZIP at that instant |
| DRC | 53.188 s | Not available from that released table at that exact instant |
| DRD | 0 s | Both artifacts already existed when the node became public |

The cached first page of DRB logs contains pre-forecast additions for 92
individual data-source files. The later ZIP member hashes are not linked to
those earlier individual versions, so file existence does not certify their
exact bytes at issue. Missing log matches are not evidence of absence: the
unfiltered history page is paginated. `release_bundle_first_public_utc` records
an alternative, explicitly later origin at which the full released input
package was available; adopting it is a design decision, not hidden backdating.

The released input table is also not an independently recovered fitting
inclusion/weighting mask. Counts and chi-square describe the released rows and
rounded issued line, without assuming every row was weighted identically in
the authors' fit. Multiple rows at an orbit can be independent observers or
shared exposures; `same_epoch_extra_rows` does not identify duplicate exposures.

DRB's nonlinear flags are columns of its exact forecast file. DRC/DRD TTV
labels instead come from publication-table transcriptions, not their five-column
ephemeris files. Their availability at the exact first-public forecast timestamp
has not been independently verified here. They remain the frozen experiment's
release-specific labels; a new strict issue-time predictor needs the first-public
date of the flag source, not just the fixture's `flag_release` field.

## HR 858 b check and the proposed untouched block

DRD has sixteen released HR858b timings from nominal TDB calendar dates
2018-10-21 to 2020-11-15, a 756.484-day baseline. The issued-line chi-square is
77.287; nominal N−2 reduced chi-square is **5.521**, while standardised
residual RMS is **2.198**, and raw residual RMS is 10.705 minutes. Saying the
times scatter "5.5 times their stated errors" confuses reduced chi-square
with a scatter ratio. The fixed protected opportunities extrapolate
2,036.442–2,118.903 days after the last released input.

Across **all** 30,344 DRD timing rows and all source types, none is at or after
nominal TDB calendar 2024-01-04 (JD 2460313.5). Maxima are 2024-01-03 for space
timings, 2023-12-31 for ExoClock, 2023-12-13 for literature and 2021-09-01 for
ETD. Therefore this released table does not support a claim that later ground
inputs directly leak sectors 74–97. It also does not make those sectors an
operational post-issue test: they precede DRD's November 2025 public issue.
Calendar labels here are not converted eligibility boundaries or proof that
an unpublished data path did not exist.

## External-source limits and supported next route

The current NASA [column definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html)
distinguish discovery publication dates, parameter-set publication dates and
the TTV flag. These are different facts. Parameter-set dates do not date
when a planet was discovered or when TTVs became known. Even a clearly
pre-origin metadata date is labelled `metadata_pre_origin_source_unverified`.
Partial dates straddling the origin remain ambiguous. The cohort-wide
literature search remains `not_searched`, while the outcome-blind companion
metadata screen is recorded as completed.

Bonfanti's HR858 warning remains a separately verified positive case audit
([DOI](https://doi.org/10.1051/0004-6361/202451300)); it is not a uniform
cohort search and cannot supply negative labels elsewhere. The period-ratio
candidate fields do not establish resonances or physical interactions.

Two public NASA TAP requests failed with upstream HTTP522: the all-host query
and a fixed 35-host first batch. Their exact queries/status are retained in
`external_metadata/provenance.json`. No response data were retrieved. The
saved full names/hosts table and 184 default rows still permit the concrete
uniform candidate screen above. The supported next route is to retry TAP
once reachable for discovery references/dates, then verify cited source
identity, first-public availability and historical host membership under one
predeclared protocol. It is not evidence that the missing sources do not exist.
The cached names table's original receipt used file modification time as its
retrieval timestamp; this is not immutable historical source evidence.

## Rebuild and checks

```bash
.venv/bin/python scripts/t019_external_metadata.py
.venv/bin/python scripts/t019_information_ledger.py
.venv/bin/python -m unittest discover -s tests -p test_t019_information_ledger.py -v
```

The rebuild is offline. Five synthetic tests check the distinction between
reduced chi-square and RMS, observation age versus reference pivot, invalid
uncertainties and undefined degrees of freedom, calendar labels, and partial
metadata dates. Input bytes are hashed before/after the main build; no frozen
file is written. The parent runs the full repository suite at integration.
