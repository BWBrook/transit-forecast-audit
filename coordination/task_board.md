# Work queue

Seed preparation is complete. Research tasks below are deliberately ordered by
what they unlock. Agents should claim work by adding owner, branch/worktree and
owned files. Update status with a concrete evidence path rather than a broad
claim of completion.

| ID | Task | Done when | Dependency | Status |
|---|---|---|---|---|
| T001 | Revisit closest literature and novelty | A written prior-art comparison selects one meaningful extension or recommends narrowing | None | **Partly done** (Claude): ExoClock II–IV sources re-read, Table 5 definition recovered from DRD TeX source. **Open for Codex:** full citing-literature sweep of ExoClock IV and III (ADS/Google Scholar), plus prior art on separating TESS timing-error calibration from ephemeris calibration |
| T002 | Acquire original DRB artifact and version evidence | Exact bytes/table, hash, issue evidence and uncertainty convention recorded | None | **Done** (Claude): `results/pilot_v1/source_manifest.csv`, D012–D013 |
| T003 | Establish one independent later TESS outcome | Full source-to-event chain, time standard, uncertainty and independence verified | T002 for pairing | **Partial**: DRD TESS mid-times are date-independent of DRB/DRC inputs; sector/cadence lineage and the ExoClock fit prior are not released. Next: re-measure 3–5 events from SPOC light curves at MAST |
| T004 | Build 5–10 planet metadata pilot | Traceable dossiers and all inclusion/exclusion reasons; inspected pilot marked development | T002–T003 | **Done** (Claude): `results/pilot_v1/` dossiers, pairs, plots, DRB flow; development only (D014) |
| T005 | Specify and reproduce Table 5 | Event list/denominators and conventions reconciled; exact match or explained differences | T002–T004 | **Done** (Claude): exact DRB/DRC, DRD 1/4716 boundary; D015. **Needs independent reproduction (Codex, ideally in R)** |
| T006 | Decide Track A feasibility and one primary extension | Signed decision entry with novelty, metadata and precision evidence | T001,T004,T005 | Open |
| T007 | Implement minimal real adapters | Tests against small attributed fixtures; raw provenance retained | T006 | Open |
| T008 | Simulate concrete failure modes / design precision | Design report identifies recoverable quantities and adequate cluster counts | T004,T006 | Open |
| T009 | Freeze analysis protocol | Cohort, origins, bins, models, metrics, folds and final-outcome lock recorded in commit | T006–T008 | Open |
| T010 | Fit earlier-only calibration rule | Reproducible development outputs; bound/uncertainty diagnostics | T009 | Open |
| T011 | Execute held-out evaluation | Paired scores, uncertainty, planned sensitivities and complete provenance | T010 | Open |
| T012 | Independent scientific review | Reproduction/criticism with concrete evidence; findings resolved or reported | T011 | Open |
| T013 | Write manuscript and release artifacts | Every result traceable to analysis; scope and citations verified | T012 | Open |
| T014 | Variance-components model on the development era | a from within-visit scatter; b, τ(h) between visits; planet-balanced and host-clustered; simulation check that a, b, τ are recoverable | T005, D017 | Open (proposed for Claude after Codex review) |
| T015 | Forecast-independent TESS mid-time pipeline | Re-measures a sample of DRD 2022–2023 TESS mid-times from SPOC light curves with a broad timing prior; agreement and σ calibration documented; then frozen | T003 | Open |
| T016 | Untouched DRD-era outcome inventory (metadata only) | List TESS sectors from 2025-11-19 and the DRD planets they cover, without fitting any light curve | D018 | Open |

## Claims

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
