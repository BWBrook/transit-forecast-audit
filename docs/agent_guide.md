# Agent guide: using the transit-forecast-audit work

**Audience:** a new AI agent (Claude, Codex or another) that must use, extend, review or reproduce this work. **Status at this draft (7 November 2026):** development evidence only, protocol not frozen, protected outcomes unopened, and the outcome-measurement pipeline **not ready** under its prespecified criteria (C025). Companion products from the same ledger: `manuscript/paper.md` (article) and `docs/brief.md` (public brief). All three cite claim IDs in `coordination/claims.md`; if a number differs between them, the ledger wins and the product is out of date.

Authoritative integrated sprint-2 account: `docs/sprint2_report.md`.

## 1. The question and the boundary

**Question.** How well do issued ExoClock ephemerides (releases DRB, DRC, DRD) predict later, independently measured TESS transit mid-times, and does a population calibration (models M0-M3) learned from the previous release improve the predictive distribution?

**Primary contrast.** Planet-balanced standardised 95% interval score (IS95), M2 minus M0. Negative favours M2. Decision is "improves", "worsens" or "inconclusive" from a 95% host-cluster percentile interval.

**What exists.** A complete development forecast experiment (sprint 1); an outcome-measurement rule with calibration, identification tests, a 120-host confirmation and a 120-host replication, both of which failed (sprint 2, C025); a remeasured-outcome convention comparison (C026); a candidate freeze package that is not freeze-ready (C027); and these drafts.

**What does not exist.** A final evaluation. Every empirical result so far is inspected development material (D014). Never describe a development result as validation, an untouched test or a held-out result.

**Protected-data boundary.** TESS outcomes dated after 2025-11-18 stay unopened until a protocol freeze is recorded and reciprocal review has finished (Barry's instruction, paraphrased in D023, 2026-11-04). The inspected development era is 2022-01-01 to 2024-01-03. Do not request, open or fit photometry outside it, and do not open anything under `data/raw/` unless your task is development-era acquisition through the guarded scripts.

## 2. Repository map

| Path | Contents |
|---|---|
| `AGENTS.md`, `CLAUDE.md`, `START_HERE.md` | Shared rules (scientific invariants, collaboration, reporting). Read first. `CLAUDE.md` points to `AGENTS.md`. |
| `README.md`, `VALIDATION.md` | Overview. `README.md` carries the sprint-1 status; `VALIDATION.md` records the seed suite only. |
| `coordination/claims.md` | **Claims ledger.** IDs, status, evidence at commit, reproduce command. Single source of evidence. |
| `coordination/decisions.md` | Dated decisions D001-D045 with responsible agent and status. |
| `coordination/message_board.md`, `task_board.md`, `decision_queue.md` | Progress notes, task claims, queue. |
| `docs/evaluation_protocol.md` | Estimands, tracks R/A/B, covariance tiers, scoring, dependence. Status header lists amendments. |
| `docs/statistical_models.md` | Notation, covariance propagation, model ladder, scores. |
| `docs/two_sprint_plan_2026-11-05.md` | The plan. The revision section (R1-R9, I1-I3, A1-A2) governs where it conflicts with the draft. |
| `docs/sprint1_report.md` and `sprint1_*.md` | Sprint-1 synthesis, timing audit, inventory, precision, scoring review, literature review. |
| `docs/sprint2_outcome_design.md` | Outcome rule `t015v3`/`t015v3c`, criteria, confirmation design, identification tests. Frozen at commit `2c39f0a`. |
| `docs/sprint2_replication_design.md` | The single prespecified replication of fixed `t015v3` (committed at `9375b3c` before any replication photometry). |
| `docs/sprint2_report.md` | Integrated sprint-2 report (decisions D046-D050, claims C022-C027, open items S2-01 to S2-05). Authoritative for sprint-2 numbers. |
| `docs/t015_*.md`, `docs/third_turn_review_2026-11-05.md` | Earlier timing-pipeline reports and reviews. |
| `docs/novelty_gate.md`, `docs/literature_review.md`, `docs/literature_update_*.md` | Prior art and the bounded novelty statement. |
| `docs/correspondence/` | Published snapshots of the human-AI correspondence (redacted, with flagged messages withheld). |
| `docs/brief.md`, `docs/agent_guide.md`, `manuscript/paper.md` | The three linked products. |
| `configs/` | `sprint1.json` (development comparisons), `sprint1_delayed_origin.json`, `candidate_freeze.json` (candidate final protocol, not frozen), `pilot_provisional.json` (superseded). |
| `scripts/` | Analysis (`sprint1_*`, `sprint2_*`, `t015_*`, `review_*`), acquisition (`acquire_osf.py`), independent R check (`independent_table5.R`). |
| `src/transit_audit/` | Small NumPy core: ephemeris, covariance, scoring, provenance, ExoClock parsing. |
| `tests/` | Unit tests for scientific failure modes. |
| `results/sprint1/`, `results/sprint2/`, `results/outcomes/`, `results/t015_*` | Compact committed outputs. `results/sprint1/handoff.json` is the machine-readable sprint-1 entry point. |
| `results/pilot_v1/`, `results/sealed_inventory/` | Earlier pilot (claims C001-C007 and similar) and the superseded geometric inventory. |
| `references/` | `references.bib`, `references.csl.json`, `literature_evidence.json`, identifier lists. |
| `data/raw/` | Immutable downloaded bytes. Gitignored. Do not open without need. |
| `data/derived/` | Regenerable intermediate tables. Gitignored. |

**Version control of outputs.** `.gitignore` excludes `results/*` by default and re-includes named directories. `results/sprint2/*/ledger.csv` is ignored; the committed form is `ledger.csv.gz`. `data/derived/` is ignored, so any command that reads `data/derived/...` needs that directory restored from the sprint-1 bulk archive (`results/sprint1/bulk_archive_receipt.json`, manifest `results/sprint1/bulk_manifest.csv`) or regenerated.

## 3. Data flow, from sources to scores

1. **Release files** (OSF): DRB `wna5e`, DRC `p298n`, DRD `wpjtn` (DOIs `10.17605/OSF.IO/WNA5E`, `P298N`, `WPJTN`; CC BY 4.0). `scripts/acquire_osf.py` re-fetches, hashes and records the OSF file metadata. Manifest: `results/pilot_v1/source_manifest.csv`. Availability anchors (C019): DRB 2021-10-27 12:03:15 UTC, DRC 2022-09-27 15:25:16 UTC, DRD 2025-11-18 09:43:24 UTC.
2. **Parsing and reproduction** (`src/transit_audit/exoclock.py`, `scripts/reproduce_table5.py`, `scripts/independent_table5.R`): release ephemerides, planet flags and covariance reconstruction (C1-C4 tiers; the cohort is C2 with no C3 planets in development).
3. **Catalogue timings** (`all_mid_time_data.txt` of each release): event-level mid-times and published uncertainties. These are the development outcomes of sprint 1, scaled by a = 1.087 (C005, C008). Their first-availability dates are unknown (C019).
4. **Forecast comparison** (`scripts/sprint1_forecasts.py`, `sprint1_forecast_core.py`): fit M1-M3 on a training window, score M0-M3 on a test window, resample hosts jointly with refitting. Output: `results/sprint1/forecasts/*.json`, `results/sprint1/comparison.csv`, `results/sprint1/handoff.json`.
5. **Independent outcomes** (`scripts/sprint2_outcomes.py`, `t015_timing_pipeline.py`): identify the transit by BLS inside the catalogue period ±0.5%, fit shape, time each transit, write I1 rows. Output tables under `results/outcomes/<rule_version>/` (`t015v3`) and calibration tables under `results/sprint2/`.
6. **Outcome calibration** (`scripts/sprint2_analysis.py`): equal-host z-RMS, coverage, bias, Tmag trend, recovery from injected transits, with host-cluster bootstrap.
7. **Convention comparison** (`scripts/sprint2_forecasts.py`): refit M1-M3 on four outcome conventions (exoclock_all, exoclock_matched, ours_matched, ours_all) and write `results/sprint2/forecasts/convention_comparison.json`.
8. **Candidate freeze package** (`scripts/sprint2_freeze_package.py`): metadata roster (`roster.csv`), DRD event manifest (`events_drd.csv`), draft forecasts, access receipt. Metadata only; no photometry opened.
9. **Figures** (`scripts/sprint2_figures.py`).

## 4. Environments

- **Locked Python:** `.venv` built from `uv.lock`. Run analysis, scoring and tests with `.venv/bin/python`.
- **Photometry scripts:** PEP 723 inline-metadata files run with `uv run scripts/<name>.py`. They declare their own dependencies and a pinned Python range. Dependencies include `lightkurve==2.5.1`, `batman-package`, `astroquery`, `astropy`, `scipy` and `tess-point==0.9.5.post1`.
- **R:** `scripts/independent_table5.R` is an independent base-R reproduction of the benchmark.
- **Tests:** 70 pass at sprint 1; 75 with the sprint-2 tests.
- **Seed:** sprint-1 comparisons use 20261106; sprint-2 injections use 20261107, with the TIC identifier as a second seed element.

## 5. Decisive commands

Run from the repository root. Do not change a flag when reproducing a claim.

### 5.1 Sprint 1, exactly as in `results/sprint1/handoff.json` "commands"

```bash
.venv/bin/python scripts/sprint1_forecasts.py run --experiment release_transfer --bootstrap 400 --sensitivity-bootstrap 200 --sensitivities
.venv/bin/python scripts/sprint1_forecasts.py run --experiment chronological --bootstrap 400 --sensitivity-bootstrap 200 --sensitivities
.venv/bin/python scripts/sprint1_forecasts.py run --experiment delayed_origin --bootstrap 400
.venv/bin/python scripts/sprint1_forecasts.py run --experiment late_published_proxy --bootstrap 200
.venv/bin/python scripts/sprint1_forecasts.py make_forecasts --events data/derived/sprint1/release_transfer/a_1.087/c2/events.csv --parameters data/derived/sprint1/release_transfer/a_1.087/c2/parameters.json --release DRC --output data/derived/sprint1/interface/forecasts.csv
.venv/bin/python scripts/sprint1_forecasts.py score --forecasts data/derived/sprint1/interface/forecasts.csv --outcomes data/derived/sprint1/release_transfer/a_1.087/c2/events.csv --error-convention exoclock_reported --outcome-scale 1.087 --output data/derived/sprint1/interface/scores.csv
.venv/bin/python scripts/review_sprint1_scores.py
.venv/bin/python scripts/sprint1_precision.py --replicates 4000 --chunk-size 100
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/sprint1_handoff.py
```

### 5.2 Sprint 2, from `docs/sprint2_outcome_design.md`, `docs/sprint2_replication_design.md` and `docs/sprint2_report.md`

```bash
uv run scripts/sprint2_outcomes.py run --sample dev
.venv/bin/python scripts/sprint2_analysis.py analyse --sample dev
.venv/bin/python scripts/sprint2_analysis.py check
uv run scripts/sprint2_outcomes.py idtests
uv run scripts/sprint2_remeasure.py select
uv run scripts/sprint2_remeasure.py run
```

Confirmation, replication and idsummary (script docstrings, design documents and the report's Reproduce block):

```bash
uv run scripts/sprint2_outcomes.py select-confirm
uv run scripts/sprint2_outcomes.py run --sample confirm
.venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm
uv run scripts/sprint2_confirm2.py select
uv run scripts/sprint2_confirm2.py run
.venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm2
.venv/bin/python scripts/sprint2_analysis.py idsummary
```

The first confirmation and the replication are done. Neither is to be repeated or extended: the replication design states there will be no further replication, and a changed rule is a new rule version needing new evidence. Any new photometry request must pass the access guards of section 6.

### 5.3 Sprint-2 forecast, freeze and figure commands

```bash
.venv/bin/python scripts/sprint2_forecasts.py run
.venv/bin/python scripts/sprint2_forecasts.py run --bootstrap 400
.venv/bin/python scripts/sprint2_forecasts.py candidate --convention t015v3 --output candidate_parameters_t015v3.json
.venv/bin/python scripts/sprint2_forecasts.py interface
.venv/bin/python scripts/sprint2_freeze_package.py roster
.venv/bin/python scripts/sprint2_freeze_package.py forecasts --parameters results/sprint2/forecasts/candidate_parameters_t015v3.json
.venv/bin/python scripts/sprint2_freeze_package.py receipt
.venv/bin/python scripts/sprint2_figures.py
```

- `sprint2_forecasts.py run` accepts `--bootstrap` (default 400, so the first two lines are equivalent). `interface` replays I1 to I2 on production outcomes: `make_forecasts` then `score` over every attempted DRC-era row.
- `candidate` writes the release-transfer fit of M1-M3 on DRC forecasts against all development outcomes of the named convention. Output at `results/sprint2/forecasts/candidate_parameters_t015v3.json` (217 planets, 2,328 events; M1 b = 10.02, M2 s = 2.585, M3 b = 0.996, s = 2.591). The `t015v3c` version is kept for comparison.
- `sprint2_figures.py` writes `fig_timing_calibration.png` (development and first confirmation, both rules) and `fig_convention_contrasts.png` (chronological M1 and all-timed intervals run off scale and are drawn as arrows).

### 5.4 Reproduction commands for ledger claims (copied from `coordination/claims.md`)

```bash
Rscript scripts/independent_table5.R                                                     # C001
python scripts/review_measurement_diagnostic.py                                          # C002, C003, C004
uv run --extra analysis python scripts/local_noise_structure.py                          # C005
uv run --extra analysis python scripts/forecast_variance_components.py                   # C006
uv run --extra analysis python scripts/sealed_era_inventory.py                           # C007
python scripts/review_tranche2_noise.py --bootstrap 400                                  # C008
python scripts/review_tranche2_mixture.py                                                # C009
python scripts/review_tranche2_predictors.py --order 192                                 # C010 (repeat with --order 384, then --verify)
python scripts/review_tranche2_schedule.py --acquire                                     # C011
uv run scripts/t015_timing_pipeline.py                                                   # C012, C016
python scripts/review_t015_injections.py --bootstrap 100000                              # C013
python scripts/review_t015_grid.py                                                       # C013
python scripts/review_t015_provenance.py                                                 # C013
python scripts/forecast_variance_components.py --reps 20 --bootstrap 400                 # C014
python scripts/chronological_calibration.py --bootstrap 400 --a 1.0                      # C015
python scripts/review_chronological_extremes.py                                          # C015
uv run scripts/t015_stratified_validation.py select                                      # C017 (then run, then analyse)
.venv/bin/python scripts/review_sprint1_availability.py                                  # C019
.venv/bin/python scripts/review_sprint1_timing.py                                        # C020
.venv/bin/python scripts/sprint1_inventory.py                                            # C021
.venv/bin/python scripts/sprint1_precision.py --replicates 4000                          # C021
```

C018's reproduce commands are the first two lines of section 5.1 (`--experiment release_transfer --sensitivities` and `--experiment chronological --sensitivities`; the claims ledger abbreviates the bootstrap flags).

### 5.5 Other

```bash
python -m unittest discover -s tests -v                 # AGENTS.md form
uv run --project ~/work/correspondence correspondence-export docs/correspondence/publication.toml   # refresh the correspondence snapshot on the board host
GIT_CONFIG_GLOBAL=/dev/null gitleaks protect --staged   # before pushing to this public repository
```

## 6. Access guards and the protected-data boundary

- **Guard 1, before the request.** The MAST product's `t_max` must be within the development era. `sprint2_outcomes.py` and `t015_timing_pipeline.py` check it before any download.
- **Guard 2, before flux is read.** The FITS header `TSTOP` must be at most BTJD 3313.49 (the end of 2024-01-03 less a light-time margin; `MAX_BTJD = 3313.5` in the pipeline denotes 4 January 2024 00:00 TDB, see `docs/t015_provenance_review.md`).
- **Receipt.** `sprint2_freeze_package.py receipt` scans every FITS file under `data/raw/mast` by header only and records the maximum TSTOP, files violating the guard, and a listing hash. The current receipt (2026-11-07 06:26:59 UTC, after the confirmation and replication downloads) scanned 996 files, all in sectors 46-73, with maximum TSTOP BTJD 3312.655 and no violations; listing hash `de08107d...`. Re-run it before any freeze.
- **Eligibility anchor for the final era.** 2025-11-19 00:00 UTC (the first whole day after DRD's public time). The journal-date sensitivity (2026-02-11 plus one day) is a secondary anchor.
- **What may not be done without Barry's explicit instruction.** Open any TESS product dated after 2025-11-18, fit anything to it, or use it to select a model. An agent that must deviate records the reason in `coordination/decisions.md` first.
- **The metadata roster** (`results/sprint2/freeze_candidate/roster.csv`, `events_drd.csv`) uses only pointing predictions and calendars. It is not an outcome table. Its epochs come from the issued ephemeris, not from data.

## 7. Interface schemas

These are the sprint-1/2 contracts (plan sections I1-I3). Source of truth is the plan's revision section and the code; if they disagree, the code that produced the committed outputs is the reference.

### I1: outcome table `results/outcomes/<rule_version>/outcomes.csv`

One row per attempted event, whether it succeeded or failed. Owner: Claude.

| Group | Fields |
|---|---|
| Identity | `event_id` (planet\|sector\|product\|local_epoch), `planet`, `host`, `tic`, `sector`, `camera`, `ccd` |
| Product | `product` (SPOC_120 or TESS-SPOC_200), `flux`, `file`, `file_sha256`, `data_rel`, `cadenceno_first`, `cadenceno_last` |
| Time standard | `timesys`, `timeref`, `bjdrefi`, `bjdreff` |
| Mid-time | `tc_bjd_tdb` (posterior median) |
| Posterior | offsets in seconds from the median: `q025_s`, `q975_s` (required for IS95 and Gaussian 95% checks), and separately named `q0228_s`, `q1587_s`, `q8413_s`, `q9772_s`; `sigma_s` (68% half-width); `gauss_ok` (both one-sided 95% half-widths within 10% of 1.96σ); otherwise `posterior_grid_path`. A grid must declare whether it is a likelihood or a posterior, its prior, units, offset sign and support. |
| Dependence | `shape_group_id` (planet\|sector\|product), `loo_shift_s` (`not_estimable` is counted, not dropped) |
| Identification | `id_method` (blind or catalogue_period), `id_period_d`, `id_period_source`, plus the source date and availability basis |
| Quality | `coverage_window`, `coverage_in_transit`, `status`, `failure_reason` |
| Version | `error_convention`, `rule_version` (git commit plus script SHA-256) |

Paired products of one observation share an `observation_id` and are never both scored. Status values in the ledgers: timed, excluded_coverage, product_id_failed, run_id_failed, id_failed, edge, not_recovered.

### I2: forecasts and scores (owner: Codex)

- `forecasts.csv`: planet, host, release, issue and availability date with basis, covariance tier, epoch n, predicted BJD_TDB, σ_T0, σ_P, ρ and its source, and for each of M0-M3 the latent predictive parameters with the fitted-parameter version.
- `scores.csv`: `event_id` by method; standardised and minute IS95, log score, covered68 and covered95, interval width, the weights used and the resampling cluster.
- Commands: `make_forecasts`, then `score --outcomes <I1 path> --error-convention <name>` (section 5.1). Deterministic seed and an output receipt with hashes.

Error-convention names in use: `exoclock_reported` (catalogue timings, with `--outcome-scale a`), `t015v3_beta_chi`, `t015v3c_beta_chi_tmag`.

### I3: `results/sprint1/handoff.json`

Keys: `date`, `status`, `development_only`, `protocol_frozen`, `protected_outcomes_accessed`, `commands`, `parameters` (M1-M3 fits for each design, with parameter-file paths and hashes), `outcome_scale_tolerance` (reference a, same-decision grid range, `certified_measurement_tolerance: null`), `R8` (156 core, 28 extension, 184 union planets, 175 hosts, extension +17.95%, gate passed, identification not yet qualified), `open_defects`, `output_sha256`, `detailed_output_sha256`, `handoff_script_sha256`, `qualification`. Treat every parameter set as a development fit, not an adopted protected-era rule.

## 8. Concepts an agent must keep straight

- **Tracks R, A, B (D003).** R reproduces a published benchmark. A audits issued forecasts available at the time. B reconstructs a forecasting experiment. Label every output with its track. The current forecast comparisons are proxies: release transfer is an event-date proxy, chronological is an observation-date proxy, delayed origin is a reconstruction built after inspection.
- **Four dates.** training end, first public availability, forecast origin, retrieval. A reference epoch is not an issue date.
- **Covariance tiers C1-C4.** ExoClock gives no issued covariance (D021). M0 is a reconstruction. Never set missing covariance to zero without a label.
- **Models.** M0 issued Gaussian; M1 one fitted scale b; M2 b = 1 with a lognormal multiplier of log-scale SD s (median 1); M3 both. The comparator set is closed; nothing outside it competes (D041).
- **Outcome error.** `exoclock_reported` timings are multiplied by a = 1.087; `t015v3c` multiplies its own σ by g(Tmag) = √max(0.8857 − 0.0919(T − 11), 0.25) with T clamped to [8, 13.5]; that multiplier failed confirmation (C025). `t015v3` is the same pipeline without it. Neither is qualified.
- **Standardised IS95.** Each event's interval score divided by the M0 predictive SD including outcome error. It is a conditional weighted loss (D042), not an issue-time proper score. Always report raw minute IS95 and the forecast-only normalisation beside it.
- **Equal-host estimand.** For outcome calibration, each host has weight one and its timed events share it equally. Pooled event-weighted numbers are reproduction-only (C020).
- **Failure denominators.** Product failures, run failures, event failures and end-to-end recovery are separate. Never add them into one rate. Recovery is reported, never imputed.
- **Host-cluster resampling.** Planets of one host and repeated transits of one planet are dependent. Counts of events, planets and hosts accompany every comparison.
- **Observed coverage is not latent coverage.** Intervals describe measured mid-times (forecast convolved with outcome error), not the unobserved true time.

## 9. Where every claim's evidence lives

Evidence commits are as recorded in the ledger. Use `git show <commit>:<path>` for committed files.

| ID | Claim (short) | Evidence | Notes |
|---|---|---|---|
| C001 | Independent base-R reproduction of Table 5 (DRB/DRC exact, DRD one count) | `16b5799:results/pilot_v1/independent_review/table5_*` | numerical reproduction, not publisher code |
| C002 | Original consecutive-gap grouping chains 333/425 groups over 20 days | `.../measurement_groups.csv`, `measurement_sensitivity.csv` | diagnostic defect |
| C003 | Capped-span residual RMS 1.0968 (4,173 timings, 336 planets) | `.../measurement_sensitivity.csv`; `synthetic_identifiability.csv` is synthetic | attribution unresolved |
| C004 | Covariance cross terms at most about 0.27%, 0.98%, 2.94% (DRB/C/D) | `.../covariance_review.csv` | sensitivity only |
| C005 | Conditional REML a = 1.087 | `7a9f1a6:results/pilot_v1/local_noise/` | not physical attribution |
| C006 | Original mixture estimates | `7a9f1a6:results/pilot_v1/variance_components/` | tail labels superseded by C009 |
| C007 | Original geometric inventory (224 planets, 5,071 transits) | `7a9f1a6:results/sealed_inventory/` | interpretations rejected by C011 |
| C008 | Independent REML a = 1.086576; host bootstrap 1.04984-1.12091 | `a3f70fd:results/pilot_v1/tranche2_review/noise_review.json` | |
| C009 | Stable mixture DRB b = 2.24949, s = 1.09314; DRC b = 0.97626, s = 3.14868 | `a3f70fd:results/pilot_v1/tranche2_review/mixture_*` | |
| C010 | Training-span predictor gain 0.02709 nats per window | `a3f70fd:.../predictor_*`, `metadata_*` | exploratory |
| C011 | Calendar metadata corrections (S98-S110) | `a3f70fd:.../schedule_review.json` | |
| C012 | 27/27 DRD mid-times reproduced; injection z-RMS 1.03 | `490ef7b:results/t015/` | qualified by C013 |
| C013 | Corrected conventions; 260/261 fitting intervals overlap | `4c369df:results/t015_review/` | |
| C014 | Repaired mixture; DRC host-bootstrap b 0.712-1.357, s 1.576-4.211 | `4c369df:results/pilot_v1/variance_components_v2/` | |
| C015 | Chronological span gain unstable under refitting | `4c369df:results/pilot_v1/chronological_calibration/`; `docs/chronological_instability_audit.md` | adverse |
| C016 | Corrected T015 shifts the 27 D034 mid-times by +1.0 s | `results/t015_corrected/` | |
| C017 | 18-host validation: coverage 0.958, z-RMS 0.981 | `results/t015_validation/`, design `26590c3` | readiness superseded by C020; per-stratum failure retained |
| C018 | M2-M0 standardised IS95: release transfer −2.445 [−5.756, 0.187]; chronological −2.628 [−6.351, 0.067] | `6d69f0e:results/sprint1/forecasts/`, `results/sprint1/handoff.json` | inconclusive |
| C019 | DRD public by 2025-11-18 09:43:24 UTC; DRC timing file 53 s after its forecast | `6d69f0e:results/sprint1/literature/release_availability.csv` | |
| C020 | 13/48 planned primary runs not successful; log-MSE endpoints fail a control | `6d69f0e:results/sprint1/timing_audit/` | |
| C021 | 156 core + 28 extension planets, 184 planets on 175 hosts, 3,399 opportunities | `6d69f0e:results/sprint1/inventory/`, `results/sprint1/precision/` | metadata only |
| C022 | `t015v3`/`t015v3c` development calibration (45 hosts, 682 injections), ledger counts, shape stress test, window-removal control, white-noise tests | `results/sprint2/dev/summary.json`, `runs.csv`, `ledger.csv.gz`, `run_receipt.json` | in-sample multiplier |
| C023 | Estimand negative controls: estimators unbiased (within 0.007), 90% intervals cover 0.853-0.927 | `results/sprint2/estimand_negative_controls.json` | |
| C024 | Identification boundary tests | `results/sprint2/dev/identification_summary.json`, `identification_tests.csv` | |
| C025 | Confirmation (`t015v3c` fails; `t015v3` secondary passes), replication (`t015v3` fails), exploratory transit-count split | `results/sprint2/confirm/summary.json`, `confirm2/summary.json`, `results/sprint2/exploratory_transit_count.json`; designs `docs/sprint2_outcome_design.md`, `docs/sprint2_replication_design.md` | exploratory split defined after the replication |
| C026 | Remeasurement (4,615 attempted, 3,946 timed), convention transfer accepted, WASP-54b S50 diagnostic | `results/sprint2/forecasts/convention_comparison.json`, `diagnostic_wasp54_s50.json`; I1 table `results/outcomes/t015v3/` | all M2-M0 contrasts inconclusive |
| C027 | Candidate freeze package, candidate parameters, access receipt | `results/sprint2/freeze_candidate/`, `results/sprint2/forecasts/candidate_parameters_t015v3.json`, `configs/candidate_freeze.json` | candidate, not freeze-ready |

Claims C022-C027 are cited in the sprint-2 report; check that `coordination/claims.md` carries matching rows before relying on them (at this draft its last row was C021).

## 10. Known limitations and open defects

Open defects (from `results/sprint1/handoff.json`, with sprint-2 status as of this draft):

| ID | Defect | Status |
|---|---|---|
| S1-01 | Complete intended-event ledger and one-to-one match, distinct denominators | Addressed by `sprint2_outcomes.py` (ledger, Hungarian match with 60-min gate); needs reciprocal review |
| S1-02 | Host-balanced outcome estimand; replace biased log-MSE endpoints | Addressed in `sprint2_analysis.py`; negative controls at `estimand_negative_controls.json` (intervals slightly anti-conservative) |
| S1-03 | Remeasure development outcomes; refit M1-M3 under each convention | Done (C026): R5 transfer accepted, all contrasts inconclusive |
| S1-04 | Independent epoch mapping, no-removal and shape controls, short periods, identification boundary, extension qualification | Controls and identification tests run; the remeasured development designs and `interface` still use nearest-epoch mapping; extension qualification rests on identification tests and same-photon agreement, not on confirmation |
| S1-05 | Missing issued covariance, incomplete exposure lineage, selection denominator, limited calibration availability | Open; reciprocal review pending |
| S1-06 | Confirm eligible 120-host frame and actual product availability | Done: first confirmation 106 of 120 hosts timed; replication 102 of 120 |
| S2-01 | Product-level consistency rule against spurious windows (WASP-54b S50) | Open |
| S2-02 | Prespecified test of the at-least-four-transit, metadata-defined scope; decide whether the final evaluation is restricted to it | Open, next design |
| S2-03 | Bright-star (Tmag below 10) undercoverage 0.915-0.918 and low stratum-A recovery | Open |
| S2-04 | Equal-host weighting gives single-transit hosts full weight; consider weighting by expected final-evaluation transits | Open, Codex review |
| S2-05 | 21 of 404 non-Gaussian grids truncated by the ±60-min prior; the adapter refuses them and they count as failed attempts | Stated in the sprint-2 hand-off; no committed receipt seen at this draft |

Limitations to state in any derivative work:

1. All results are development material (D014); several designs were chosen after inspection.
2. Covariance is reconstructed; C2 is an approximation (C004, D021).
3. Release-transfer and chronological comparisons are proxies; the DRC timing file followed its forecast by 53 s (C019).
4. The `t015v3c` multiplier was fitted in-sample on 45 hosts and failed confirmation. `t015v3` failed its single replication (z-RMS 1.095 [1.002, 1.214], coverage 0.929 [0.908, 0.947], both Tmag endpoints). The at-least-four-transit scope that calibrates in both samples was defined after the replication and is exploratory.
5. The estimator bootstrap is slightly anti-conservative (0.853-0.927 coverage of nominal 90% intervals).
6. Identification excludes period errors beyond 0.5% and per-transit displacements beyond about an hour (the injection tests time 93/93 at 30 min, 85/93 at 50, 13/96 at 70, 1/95 at 90, 0/91 at 120).
7. Faint-star conservatism is real in the light curves and unexplained; stratum B (Tmag 10-11) shows positive bias (mean z +0.215 [+0.049, +0.391]).
8. D039's per-stratum failure stands (C017); the pooled "pass" is conditional (C020). The 0.1σ per-stratum bias margin was retired as poorly powered at 30 hosts per stratum, not as proven unattainable.
9. Covariance sensitivity and outcome-scale grids do not certify a measurement tolerance (`certified_measurement_tolerance: null`).
10. Missed-transit frequency is not estimable from successful timings (D010).
11. Inconsistencies between the sprint-2 report and the JSON files, to reconcile rather than silently fix (found when drafting; check each before citing):
    - The report says M1's b "rises to about 10" in the chronological all-timed fit; `convention_comparison.json` gives b = 191.3 (`ours_all`) and 190.4 (`ours_all_raw`). b = 10.02 belongs to the release-transfer candidate fit.
    - The report quotes 3,748 matched transits, a median difference of −0.1 s and a raw `t015v3` σ ratio of 1.055. The JSON gives 3,416 (chronological) and 2,230 (release transfer) matched pairs, median differences −0.18 s and −0.33 s, and a median σ ratio 0.986 and 0.985 (the convention of that ratio is not stated there).
    - The report says `t015v3` passes every criterion in the first confirmation. That holds for the production set; by product type, SPOC 120 s misses the coverage bound (0.9291 against 0.93).
    - `summary.json` records 28 spurious windows (confirmation) and 16 (replication); the report says only that no duplicate truth assignments occurred.
    - The report cites `results/sprint2/handoff.json`, which did not exist, and a scoring receipt `data/derived/sprint2/interface/scores.receipt.json`, which did not exist, at this draft.
    - Older notes: the DRD one-count benchmark mismatch (C001); the design document's 45 hosts and 682 timed injections against the recovery table's 678 timed truths come from different denominators; the dev-era `paired_remove_vs_subtract` fields carry no rule label.

## 11. How to add a claim, and conventions

1. Run the analysis with a deterministic seed and write a receipt with the command, rule or code commit, input hashes and output hashes.
2. Commit code and compact outputs together. Large regenerable data stays out of Git (over about 1 MB belongs on `nectar:/data/share/<project>/` or Zenodo) and is hashed in a manifest.
3. Append a row to `coordination/claims.md`: next free ID, a scoped claim statement (population, rule, convention), status wording that includes what is not established, evidence path with commit, and the exact reproduce command. Do not promote a source-record date to verified availability, catalogue lineage to cadence independence, or a synthetic demonstration to an astronomical result.
4. Record a decision with rationale in `coordination/decisions.md` (template at its foot); add a short progress note to `coordination/message_board.md`.
5. Cite the ID wherever the number appears in the article, brief or this guide, and run a search for the number to catch drift.
6. For an independent check, prefer a separate implementation, a numerical invariant or a primary-source reading over model agreement. Keep disagreements visible.
7. Amendments after a freeze are dated and justified in `decisions.md`; the frozen analysis is reported first and in full.
8. References: give Barry a plain-text identifier list (one DOI, ISSN, ISBN or arXiv ID per line) for Zotero. Do not hand-write bibliography entries. Mark a missing citation `[CITATION NEEDED: description]`.
9. Before pushing, scan staged files with `GIT_CONFIG_GLOBAL=/dev/null gitleaks protect --staged`. This repository is public: no credentials, no third-party copyrighted text or transcripts quoting papers, no regenerable data over about 1 MB.
10. Style for any text: lead with the result, active voice, precise statements, no hedging pile-ups, negative evidence kept prominent. End a turn on the board with `Next: Claude`, `Next: Codex` or `Next: Barry`, with a short reason.

## 12. Placeholders still open at this draft

The production-I1 interface receipt is `results/sprint2/interface/scores.receipt.json`: all 2,777 attempted DRC-window rows pass the full I1 schema check; 2,310 timed events are scored (309 through flat-prior likelihood grids), and 467 attempts remain explicit failures (313 coverage, 93 identification, 43 prior edge, 18 likelihood support truncated by the ±60-min prior, S2-05).

All draft slots are filled: confirmation and replication (C025), convention transfer (C026), candidate parameters (C027), tests (75), claim IDs C022-C027.

## 13. Suggested first moves for a new agent

1. Read `AGENTS.md`, this guide, `docs/sprint1_report.md`, `docs/sprint2_outcome_design.md` and the claims ledger.
2. Run the unit tests and `.venv/bin/python scripts/sprint1_handoff.py` to confirm the environment reproduces the sprint-1 receipts.
3. If asked to review, start from the independence argument: check that the calibration inputs do not overlap the scored observations (S1-05), and that no development-era result is labelled as validation.
4. If asked to extend, check the I1/I2/I3 contracts and the access guards before touching photometry, and confirm in `coordination/decisions.md` that the freeze state allows what you intend.
