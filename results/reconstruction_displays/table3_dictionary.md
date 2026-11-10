# Table 3 data dictionary

Files: `table3_planets.csv` (156 core planets, one row each, including the five with no accepted timing), `table3_extension.csv` (28 exploratory extension planets, same schema, `cohort = extension`; never pool with core for a confirmatory statement), `table3_excerpt.md` (10-row printed excerpt), `table3_receipt.json` (input SHA-256s, checks). Built by `scripts/build_table3.py` from saved files only; no TESS photometry or headers were opened.

Conventions. An empty cell means unknown or not applicable, never zero or "no"; the per-column entries say which. Counts are always filled (0 is a real zero). The "accepted" population is the registered accepted-timing set; planets with none have empty accuracy and coverage fields. Sources: `B/` = `data/derived/revision_stage0/benchmark/{primary|extension}/`; `IL/` = `results/information_ledger/`.

| Column | Unit | Source | Definition; empty means |
|---|---|---|---|
| planet | text | `B/terminal_ledger.csv.gz` | Planet label as in the benchmark (ExoClock-style, no space, e.g. HR858b). Join key to every source. |
| host | text | terminal ledger | Host label. |
| cohort | core / extension | directory | `core` is the primary 156; `extension` is exploratory. |
| tic | text | `results/sprint2/freeze_candidate/roster.csv` | TIC identifier of the host. |
| drd_t0_bjd_tdb | BJD_TDB | `IL/release_planets.csv`, release = DRD | Published DRD reference mid-time T0. Not the integer `forecast_epoch`. |
| drd_period_d | days | same | Published DRD period P. |
| sigma_t0_s, sigma_p_s | seconds | `B/intended_forecasts.csv.gz` | Marginal 1-sigma uncertainties on T0 and P as used in the forecasts (sigma_p_s is the period uncertainty expressed in seconds). Reconstructed from released inputs, not issued by ExoClock as a joint posterior. |
| rho | dimensionless | intended forecasts | Reconstructed T0-P correlation (weighted-least-squares reconstruction from released inputs; not an issued covariance). |
| covariance_tier | text | intended forecasts | Reconstruction tier of the covariance (`C2_candidate` for all rows). |
| n_intended | count | terminal ledger | Fixed intended event opportunities (planet x sector x DRD cycle), selection fixed before outcomes. Metadata eligibility, not a recovered transit. |
| n_coverage_qualified_at_prediction | count | terminal ledger `coverage_ok_at_prediction` | Intended events whose predicted window had qualifying cadence coverage at prediction time. A diagnostic, not an acceptance gate, and not proof a transit was observed. |
| n_accepted | count | terminal ledger | Events with an accepted timing. |
| n_no_cadence_coverage_at_prediction, n_excluded_coverage, n_integration_unresolved, n_edge, n_product_id_failed, n_likelihood_support_unresolved | count | terminal ledger `status` | Terminal status counts. With `n_accepted` they sum to `n_intended` (with `n_unmatched_expected_event` for the extension). Unaccepted events have unknown timing truth. |
| n_unmatched_expected_event | count | terminal ledger | Extension-only terminal status (4 events: expected event with no matching measurement record); 0 for core. |
| median_abs_error_min, max_abs_error_min | minutes | `B/accepted_outcomes.csv` joined to `accepted_forecasts.csv` on `event_id` | Median and maximum over accepted events of absolute (measured TESS mid-time `tc_bjd_tdb` minus DRD forecast `predicted_bjd_tdb`), x1440. Empty when n_accepted = 0. |
| m0_coverage95, m2_coverage95 | proportion | `B/expected_scores.csv` `covered95` | Mean within planet over accepted events of 95% coverage of the measured time under M0 (issued Gaussian reconstruction) and M2 (tails-only widened). Convolved with measurement error: coverage of measured time, not of the latent mid-time or of observing capture. Empty when n_accepted = 0. With few accepted events the values are coarse (e.g. 0, 0.5, 1). |
| mean_std_is95_diff_m2_minus_m0 | standardised IS95 | expected scores `is95_standardised` | Within planet mean over accepted events of (M2 minus M0) standardised 95% interval score. Negative favours M2. The standardising denominator is measured after issue and may depend on the outcome. Empty when n_accepted = 0. |
| input_baseline_days | days | `IL/release_planets.csv` DRD row `input_baseline_days` | Span from first to last timing input of the DRD release ledger. |
| last_input_bjd_tdb | BJD_TDB | same | Time of the last release timing input. |
| issued_line_z_rms | dimensionless | same | RMS of standardised residuals of the release inputs about the issued line. |
| issued_line_reduced_chi2_nminus2 | dimensionless | same | Chi-squared of the issued line over N-2 degrees of freedom. Numeric descriptors only; no pass/fail flag is defined. |
| n_release_inputs | count | same, `valid_timing_rows` | Valid timing rows in the release ledger. Released rows were not independently certified as the actual fitting set. |
| new_in_drd_by_name | true / false | `IL/release_planets.csv` | `true` when no DRB or DRC row exists under the same planet label. Limitation: name matching only. A renamed or aliased planet may appear new, and absence under a matched name is not proof that no earlier forecast or knowledge existed. Core: 27 true, 129 false; extension: 12 true, 16 false. |
| drd_origin_ttv_flag | true / false | `IL/origin_knowledge.csv` DRD row `origin_release_ttv_flag` | The catalogue's own release-specific TTV flag at the DRD origin. Not literature knowledge: it is `false` for all 184 planets, including HR858b, which has a verified pre-origin TTV warning. Read `false` as "not flagged in this release", never "no TTVs". The flag's timing relative to the forecast was not verified. |
| pre_origin_ttv_literature_status | text | `IL/origin_knowledge.csv` `pre_origin_literature_ttv_status` | `verified_positive_case_audit_not_uniform` (HR858b only, a case audit rather than a uniform search) or `not_searched`. `not_searched` means unknown: no uniform primary-literature search was done. No planet is labelled negative. |
| ttv_warning_source | DOI/URL | same `warning_source` | Source of the positive pre-origin warning (HR858b: doi.org/10.1051/0004-6361/202451300; journal January 2025 and November 2024 preprint, both before the DRD origin of 18 Nov 2025). Empty when no positive source is held. |
| current_archive_ttv_flag | 0 / 1 | same | Current archive descriptive metadata flag, retrieved on the date in the next column. Not origin knowledge, and 0 does not mean physically negative. Keep separate from the release flag. |
| current_archive_flag_retrieved_utc | UTC timestamp | same `current_label_retrieved_utc` | Retrieval time of the archive flag. |

## Left out, and why

- Transit duration: the release ledger does not hold a verified origin duration (`duration_status` is not present), so it is omitted rather than approximated.
- A uniform literature TTV flag for every planet: needs curation not yet done.
- Per-event rows: they live in the benchmark package (`B/`); this table is per planet.
