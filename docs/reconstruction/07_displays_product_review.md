# Reviewer draft: display and product feasibility

Codex, 10 November 2026. Review of reconstruction steps 1d and 2, from
`0f390f3`. This is a working review, not a replacement display plan or an
instruction to begin step 3. Barry's provisional four figures/three tables
are preserved. No display, production table, new fit, raw photometry or FITS
header was generated or opened. The manuscript, brief, bibliography and
scrivmark state are unchanged.

## Recommendation

The proposed displays are feasible from saved tables, with the qualifications
below. The reusable per-planet product is a sensible deliverable, but it is
**not yet the same thing as the prepared C053 scoring package**. It requires
an explicit metadata/roster join, a data dictionary and an archive release.
Neither a new figure nor the new machine-readable table has been built here.

## Source and interpretation map

| Planned item | Saved source and join | Feasibility and required meaning |
|---|---|---|
| Fig. 1a, forecast/window/measured event | `results/final_primary/accepted_forecasts.csv`: `predicted_bjd_tdb`, `forecast_variance_s2`; join `accepted_outcomes.csv` on `event_id` for `tc_bjd_tdb`, `sigma_s`, `q025_s`, `q975_s`; `scores.csv` carries convolved interval width/coverage | Feasible. Distinguish the **forecast-only** range from the later **measurement-convolved** predictive interval. A measured midpoint is not a full transit and a predictive interval is not a duration/baseline-complete observing schedule. For a non-Gaussian likelihood the convolved interval need not be symmetric, so `width95_minutes / 2` is not enough to recover both endpoints. A labelled schematic may be synthetic rather than an actual event. |
| Fig. 1b, observation/access timeline | Availability anchors in `results/information_ledger/source_chronology.json`; frozen access record/configuration and D065; sector/product/event metadata in the fixed manifests | Feasible, but show **observation dates and analyst access as separate lanes**. The freeze was 8 November 2026, after the held-out 2025–2026 exposures had been recorded but before project access. DRD issue → freeze → held-out observations would imply a prospective observation design that did not occur. Label S74–S97 as uninspected and note sector 74 straddles the cutoff day. |
| Fig. 2a, absolute-error distribution | Exact join of `results/final_primary/accepted_outcomes.csv` and `accepted_forecasts.csv` on `event_id`; absolute `tc_bjd_tdb − predicted_bjd_tdb`, converted to minutes | Feasible for all 2,185 accepted events. All current absolute errors are finite and positive; the smallest is 0.00131093 min, so an ordinary log axis requires no arbitrary offset for this dataset. Define zero handling rather than silently adding epsilon if the product is generalised. An unweighted event distribution has median 1.115 min; equal planet mass gives 1.315 min. State which weighting the display and median use. |
| Fig. 2b, ranked maximum per planet | The same paired rows, grouped by `planet`; retain accepted count per planet | Feasible for 151 accepted planets. The non-HR858b maximum is 26.29898 min, consistent with a 26.4-min bound. Counts range from 1 to 155 accepted events per planet: the maximum is an observed extreme under unequal sampling, not a comparable estimate of intrinsic risk. Report counts in the product/caption and identify the five zero-accepted primary planets outside this plotted set. |
| Fig. 2c, DRC error versus lead time | `results/t020_development/longer_horizon/c2_pooled_candidate_events.csv.gz`: `event_id`, `planet`, `era`, `status`, `drc_prediction_bjd_tdb`, `drc_forecast_epoch`, `residual_min`; filter `status=accepted` | Feasible for 3,052 accepted events on 128 DRC-core development planets. The `era` field separates S56–S73 and inspected 2026 blocks. Plot these gaps honestly; do not connect them as continuous surveillance through four years. The issued origin is 27 September 2022; use a clearly labelled year-scale lead convention, not an unexplained UTC↔BJD relabelling. This is retrospective inspected-development evidence, not another held-out test. |
| Fig. 3a, residuals scaled by combined SD versus N(0,1) | Paired outcomes/forecasts plus M0 rows of `scores.csv`: `m0_predictive_sd_s`, `weight`; outcome `gauss_ok` and `posterior_grid_path` distinguish the 399 non-Gaussian events | Feasible **as a qualified diagnostic**, not automatically an exact calibration test. Dividing by a combined SD does not make a non-Gaussian convolved distribution normal. Using `sqrt(forecast variance + sigma_s²)` also differs from the actual grid-variance denominator on those rows. Options within this panel: explicitly label a Gaussian-surrogate comparison, show the Gaussian-certified subset with its denominator, or later compute normalised PIT values from the exact M0 predictive CDF. The adapter's saved-grid convolution provides the calculation; no refitting or photometry is required, but PIT is not a saved CSV column. Retain planet weights, host dependence and accepted-sample/measurement-model qualifications. |
| Fig. 3b, coverage against nominal | Existing `results/revision_stage0/interpretability/coverage_vs_nominal.csv`: `set`, `method`, `nominal`, `measured_time_coverage`, `ci95_lower`, `ci95_upper` | Directly feasible. Use `set=primary`, M0/M2 and the existing conditional intervals. It describes convolved measured-time coverage conditional on acceptance and C2 reconstruction. “Narrow by minutes” needs a width in minutes; the coverage fraction alone does not give one. |
| Fig. 4a, b/c/d timing pattern | Existing `results/independent_validation/hr858/oc.png`; underlying `summary.json`, `routes.PDCSAP_FLUX.planets.*.transits`: `tc_bjd_tdb`, `o_minus_c_ref_min`, `sigma_min`; published reference coefficients are in `config` | Directly feasible and already drawn. It compares with the published reference ephemerides, whereas Fig. 4b compares with **DRD**. Name the distinction in each panel. The implementations share photons; opposite residuals and nearly on-time d support an astrophysical interpretation, not unique dynamics or exclusion of every extraction/identity error. |
| Fig. 4b, released inputs versus DRD and 2026 timings | Released timing rows `data/raw/osf/wpjtn/all_mid_time_data.txt` (`Planet`, `Tmid (BJD_TDB)`, uncertainty, source, ID), filtered to HR858b; DRD `T0`/period in `results/information_ledger/release_planets.csv`; paired primary outcomes/forecasts; all 24 HR858b intended opportunities in `results/prefreeze/forecasts_core_draft.csv.gz` and `terminal_ledger.csv.gz` | Feasible without opening any light curve. The release ledger supplies the old input epoch/baseline/scatter; individual error bars require the released timing rows, not the aggregate ledger alone. Show residuals around the issued line or a sufficiently explicit inset so the few-minute old scatter and six-hour future departure remain visible. Use the frozen reconstructed C2 variance for a forecast-only band, with measurement intervals separate. Released rows are not independently certified as the exact fitting-membership mask. Of HR858b's 24 intended events, 16 are accepted, six have no prediction-time cadence, one is edge and one integration-unresolved; do not depict all 24 as observed timings. |

## Tables and reference product

**Tables 1 and 2 are feasible from saved results.** Table 1 should say
prediction-time qualifying cadence coverage rather than simply “observed”.
`results/final_primary/terminal_ledger.csv.gz` has every intended identity,
terminal status and `coverage_ok_at_prediction`; the manifest has all 3,103
opportunities. Cadence at a prediction is not proof that an actual displaced
transit was observed.

For Table 2, error quantiles can be derived from the exact paired rows;
method scores/coverage/widths come from `scores.csv` and `descriptives.json`;
the primary joint interval is in `evaluation_summary.json`. Event and
planet weighting must be defined separately. The global maximum does not
change with weighting, and there is no need to manufacture an event-weighted
counterpart to the registered planet-balanced joint decision interval.

**Table 3 needs a new derived join, not new observations.** The core fields map
as follows:

- Intended planet/host/TIC/cohort and opportunities: fixed manifest, terminal
  ledger and `results/sprint2/freeze_candidate/roster.csv`.
- Published DRD reference epoch `T0` and period `P`: the DRD rows of
  `results/information_ledger/release_planets.csv`; their marginal uncertainties
  are `sigma_t0_s`, `sigma_p_s` in intended/accepted forecasts. Keep the
  reconstructed `rho`/covariance convention if the product supports propagation.
  Do not confuse published reference `T0` with integer `forecast_epoch`.
- Accepted timing counts and median/maximum errors: joined outcome/forecast
  rows. Per-planet M0/M2 coverage: group method rows of the saved score table.
  Coverage is convolved measured-time coverage, not observing capture.
- Input span, last input time and issued-line scatter: the DRD release ledger
  fields `input_baseline_days`, `last_input_bjd_tdb`, `issued_line_z_rms` and
  `issued_line_reduced_chi2_Nminus2`. Store numeric descriptors with definitions,
  not newly chosen pass/fail flags.
- “New in DRD”: compare the matched catalogue entries across releases and label
  the name/alias limitation; absence under a matched name is not proof that no
  prior forecast or knowledge existed.
- TTV literature: `results/information_ledger/origin_knowledge.csv` retains
  explicit unknowns. All 552 release-target rows say uniform literature search
  was `not_searched`, and none is eligible as a certified external predictor.
  HR858b has a positive case audit; a generic zero/no-TTV label for everyone
  else would be false. A complete origin-dated literature flag column requires
  curation; otherwise use positive/unknown states and source dates. Current
  archive flags and release flags must remain separate and dated.

Recommend at least **156 primary planet rows**, preserving the five
zero-accepted planets with counts/statuses and null accuracy/coverage values.
If the full product includes the 28-planet extension, mark it exploratory and
separate it from primary summaries. A 151-row accepted-only table can also
be supplied, but must be labelled and linked to the complete intended roster.
The printed excerpt should be identified as such, with a declared selection
rather than being read as the full population.

C053 is a prepared, hash-bound **event-scoring replay package**, containing both
intended and accepted tables, grids and source-code closure. Its export receipt
says `released: false`. It is not yet a published per-planet reference catalogue
with a DOI, uniform historical TTV inventory or origin duration fields (the
release ledger's durations are unknown). The proposed product needs its own
schema, definitions of null/status fields, source/version hashes and reviewed
archive metadata. These are later production tasks after Barry's next step,
not reasons to open more photometry or enlarge the present display count.

## Scope to retain in the reconstruction

The planned package can make “minute-scale agreement among accepted timings”
checkable and reusable. It cannot turn the accepted sample into a catalogue-wide
failure rate, measured-time coverage into full-transit capture, or one HR858b
case into a prospectively validated warning rule. Keep those distinctions in
captions and product metadata rather than returning to eight process figures.

Next: parent integrates this review in thread 156; no display production yet.
