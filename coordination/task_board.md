# Work queue

Seed preparation is complete. Research tasks below are deliberately ordered by
what they unlock. Agents should claim work by adding owner, branch/worktree and
owned files. Update status with a concrete evidence path rather than a broad
claim of completion.

| ID | Task | Done when | Dependency | Status |
|---|---|---|---|---|
| T001 | Revisit closest literature and novelty | A written prior-art comparison selects one meaningful extension or recommends narrowing | None | **Bounded sprint-1 screen complete (D043):** all 82 returned OpenAlex citing records screened, primary-method comparison in `docs/sprint1_literature_review.md`; index disagreement/ADS access limits retained, no exhaustive-absence claim |
| T002 | Acquire original DRB artifact and version evidence | Exact bytes/table, hash, issue evidence and uncertainty convention recorded | None | **Done** (Claude): `results/pilot_v1/source_manifest.csv`, D012–D013 |
| T003 | Establish one independent later TESS outcome | Full source-to-event chain, time standard, uncertainty and independence verified | T002 for pairing | **Done for 27 development events** (Claude, D034): SPOC file + SHA-256 + CADENCENO range + TDB keywords per event in `results/t015/`; forecast-independent timing. BJD_TDB is SPOC-stated, not reconverted |
| T004 | Build 5–10 planet metadata pilot | Traceable dossiers and all inclusion/exclusion reasons; inspected pilot marked development | T002–T003 | **Done** (Claude): `results/pilot_v1/` dossiers, pairs, plots, DRB flow; development only (D014) |
| T005 | Specify and reproduce Table 5 | Event list/denominators and conventions reconciled; exact match or explained differences | T002–T004 | **DRB/DRC independently reproduced** (Codex, base R): `results/pilot_v1/independent_review/table5_*`, D020. DRD boundary unresolved; Initial unreproduced; reconstructed rule not verified publisher code |
| T006 | Decide Track A feasibility and one primary extension | Signed decision entry with novelty, metadata and precision evidence | T001,T004,T005 | Open |
| T007 | Implement minimal real adapters | Tests against small attributed fixtures; raw provenance retained | T006 | Open |
| T008 | Simulate concrete failure modes / design precision | Design report identifies recoverable quantities and adequate cluster counts | T004,T006 | Open |
| T009 | Freeze analysis protocol | Cohort, origins, bins, models, metrics, folds and final-outcome lock recorded in commit | T006–T008 | **Candidate package only (D050, C027):** `configs/candidate_freeze.json`, roster, 3,399-event manifest, draft DRD forecasts, access receipt; not freeze-ready until the outcome rule is qualified and reviews reconcile |
| T010 | Fit earlier-only calibration rule | Reproducible development outputs; bound/uncertainty diagnostics | T009 | Open |
| T011 | Execute held-out evaluation | Paired scores, uncertainty, planned sensitivities and complete provenance | T010 | Open |
| T012 | Independent scientific review | Reproduction/criticism with concrete evidence; findings resolved or reported | T011 | Open |
| T013 | Write manuscript and release artifacts | Every result traceable to analysis; scope and citations verified | T012 | Open |
| T014 | Identifiable variance-components model on the development era | Outcome scale independently constrained or declared a sensitivity; shared ephemeris covariance specified; simulation checks separation of b and any extra variance before fitting | T005, D021–D024 | **Development model in place** (Claude, D026–D027): outcome scale a=1.09 as fixed sensitivity; two-stage planet-level scale mixture (b, s) with recovery simulation on the real DRC design, `results/pilot_v1/variance_components/`. **Production repaired (D036):** continuous posterior summaries and 400 host resamples retained in `variance_components_v2/`. Chronological refit instability prevents selecting the span correction (D037) |
| T015 | Forecast-independent TESS mid-time pipeline | Re-measures a sample of DRD 2022–2023 TESS mid-times from SPOC light curves with a broad timing prior; agreement and σ calibration documented; then frozen | T003 | **Not ready (D049):** t015v3c failed its 120-host confirmation; fixed t015v3 failed its prespecified 120-host replication. Exploratory: ≥4-transit hosts calibrated in both (C025). Remeasurement and R5 transfer done (C026). Open: S2-01 spurious-window rule, S2-02 prespecified narrower-scope test, S2-03 bright stars, S2-05 grid support |
| T016 | Untouched DRD-era outcome inventory (metadata only) | List TESS sectors from 2025-11-19 and the DRD planets they cover, without fitting any light curve | D018 | **Metadata correction complete (D043/D045):** public product/date inventory in `results/sprint1/inventory/`; 184 core+extension planets, 3399 opportunities after origin flags, no protected FITS opened. Actual cadence capture and outcome recovery remain unverified |

## Claims

- 2026-11-07 Claude: **sprint 2 complete** (D046–D050, C022–C027). Report `docs/sprint2_report.md`, handoff `results/sprint2/handoff.json`. Outcome pipeline not ready under prespecified criteria; R5 transfer accepted; candidate freeze package not freeze-ready. Drafts: `manuscript/paper.md`, `docs/brief.md`, `docs/agent_guide.md`. Next in Barry's order: Codex reviews and fixes sprint 2. Protected outcomes remain closed.

- 2026-11-06 Codex: **sprint 1 complete** from `33884de`, D042–D045.
  Owns the forecast/scoring interface and experiment, covariance integration,
  precision/tolerance assessment, and synthesis/handoff. Independent delegates
  own only `review_sprint1_timing.py`/timing audit outputs,
  `sprint1_inventory.py`/inventory outputs, and the sprint literature ledger.
  Claude retains production timing implementation and sprint 2. See the plan's
  execution reconciliation for qualifications to D041. All protected outcomes
  remain closed. Handoff is `docs/sprint1_report.md` and `results/sprint1/handoff.json`: full
  A1/I2/I3 development package, null certified outcome tolerance, 70 tests pass.
  Claude checks the interface and executes sprint 2; protected data stay closed.

- 2026-11-05 Codex: drafted the two-sprint programme requested by Barry in
  chat, `docs/two_sprint_plan_2026-11-05.md` (D040). **Proposed, awaiting
  Claude's critique/revision; implementation has not started.** Codex's sprint
  covers the forecast experiment, inventory, precision/novelty and D038–D039
  audit. Claude's sprint covers outcome qualification, integrated analysis,
  candidate freeze package and article/brief/agent-guide drafts. Execution is
  sequential, then Codex reviews/fixes Claude's work, Claude reviews/fixes
  Codex's, and both reconcile. Protected outcomes stay closed throughout.
  **Revised by Claude (D041):** the revision section of the plan (R1–R9,
  I1–I3, A1–A2) governs. Awaiting Codex's acceptance, then sprint 1.

- 2026-11-05 Claude (Opus 5.5): D035 corrections to T015 and the
  prespecified stratified validation, on `main`. Owns
  `scripts/t015_timing_pipeline.py`, `scripts/t015_stratified_validation.py`,
  `tests/test_t015_numerics.py`, `results/t015_corrected/`,
  `results/t015_validation/`, `docs/t015_validation_design.md` and
  `docs/t015_validation_report.md`. New development-era photometry (S56–S73,
  ending by 2024-01-03) is downloaded to `data/raw/mast/`, which is gitignored.
  **Completed:** design `26590c3`, then results (D038–D039, C016–C017).

- 2026-11-05 Codex: claims D034 audit and completion of the stable development
  mixture/chronological predictor check from `490ef7b` on `main`. Owns
  `scripts/review_t015_*.py`, `results/t015_review/`, `docs/t015_*review.md`,
  `docs/t015_method_sources_2026-11-05.md`, production
  `scripts/forecast_variance_components.py`, new chronological-development
  script/results and related tests/coordination. Delegates audit injection
  geometry, provenance and primary methods separately. Claude retains the
  original timing pipeline and future stratified sample. No new photometry
  acquisition or protected light-curve access; existing five development FITS
  may be checked only against their named manifest. Handoff: accepted versus
  unsupported D034 claims, checked production mixture and bounded chronological
  result, without protocol freeze. Exact sealed target-window inventory remains
  a separate metadata task after this outcome-method gate.
  **Completed:** evidence commit `4c369df`, D035–D037, C013–C015; 51 tests pass.
  Injection claims narrowed; production mixture repaired; span rule fails
  chronological refit stability. No new photometry or protected outcomes opened.

- 2026-11-05 Claude (Opus 5.5): T015 development validation and the D031/D033
  repairs (rank-2 likelihood algebra, strict Track A JD), on `main`. Owns
  `scripts/t015_timing_pipeline.py`, `results/t015/`,
  `docs/t015_pipeline_report.md`. No post-2025-11-18 data requested.

- 2026-11-05 Codex: claims independent review of D026–D029, a bounded
  issue-time metadata test and the heavy-tail portion of T001, on `main` from
  `7a9f1a6`. Owns new `scripts/review_tranche2_*.py`,
  `results/pilot_v1/tranche2_review/`, `docs/tranche2_independent_review.md`,
  `docs/literature_update_2026-11-05.md`; integrates coordination changes.
  Handoff: numerical/identifiability review, source-supported metadata analysis
  with development-only interpretation, and a concrete response to Claude.
  Claude retains T015. No light curves or protected outcomes will be opened;
  this review neither freezes nor releases the protocol.
  **Completed:** `docs/tranche2_independent_review.md`, D030–D033. Independent
  REML and stable mixture point estimates reproduce; posterior tail counts and
  schedule claims are corrected. Training span is promising in a conditional
  host-held-out development comparison, pending chronological validation.
  Full citation screening remains open. Claude retains T015 and the next
  production numerical/inventory repair, with this review as reference evidence.

- 2026-11-05 Claude (Opus 5.5): T014 development model, T016 metadata
  inventory, on `main`. Owns `scripts/local_noise_structure.py`,
  `scripts/forecast_variance_components.py`, `scripts/sealed_era_inventory.py`,
  `results/pilot_v1/local_noise/`, `results/pilot_v1/variance_components/`,
  `results/sealed_inventory/`, `tests/test_variance_components.py`,
  `docs/development_tranche2.md`. No light curves opened. Next proposed:
  T015 on 3–5 development events (Claude) while Codex reviews D026–D029.

- 2026-11-04 Codex: claims the bounded first-turn review of T005 and D015–D018,
  plus a focused T001 source/citation sweep, on `main`. Owns new
  `scripts/independent_table5.R`, `scripts/review_measurement_diagnostic.py`,
  `results/pilot_v1/independent_review/`, `docs/independent_review.md`, and
  `docs/literature_update_2026-11-04.md`; integrates coordination and status
  corrections. Handoff: independent raw-byte reproduction, explicit covariance
  and measurement-error limitations, source-backed novelty assessment, and
  next feasibility gate. No post-2025-11-18 TESS light curves may be opened;
  this turn does not freeze the protocol or unseal evaluation data.
  **Completed:** independent R reproduction, diagnostic/covariance review and
  bounded primary-source sweep. T001 remains open for a complete citing list;
  `docs/literature_update_2026-11-04.md` records the routes and limits. Corrected
  source-date/covariance labels in the dossier generator and regenerated pair
  metadata without changing scores. Next handoff: T003/T015 development events,
  T014 identifiability design and T016 metadata only, under D023's lock.

- 2026-11-04 Claude (Opus 5.5): T002, T004, T005 done on `main`; owns `scripts/acquire_osf.py`,
  `scripts/reproduce_table5.py`, `scripts/covariance_completeness.py`,
  `scripts/tess_measurement_calibration.py`, `scripts/pilot_dossiers.py`,
  `src/transit_audit/exoclock.py`, `results/pilot_v1/`. Handoff: Codex reviews
  and independently reproduces T005 and the D015–D017 claims, and takes T001.

## Suggested first division

- Agent A: T001 and forecast/source side of T002.
- Agent B: T003 and the executable side of T004.
- Both: swap review roles before T006.

Do not run different agents into the same source file concurrently. A shared
filesystem does not provide isolation; use explicit ownership or worktrees.
