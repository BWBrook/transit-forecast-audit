# Work queue

Seed preparation is complete. Research tasks below are deliberately ordered by
what they unlock. Agents should claim work by adding owner, branch/worktree and
owned files. Update status with a concrete evidence path rather than a broad
claim of completion.

| ID | Task | Done when | Dependency | Status |
|---|---|---|---|---|
| T001 | Revisit closest literature and novelty | A written prior-art comparison selects one meaningful extension or recommends narrowing | None | Open |
| T002 | Acquire original DRB artifact and version evidence | Exact bytes/table, hash, issue evidence and uncertainty convention recorded | None | Open |
| T003 | Establish one independent later TESS outcome | Full source-to-event chain, time standard, uncertainty and independence verified | T002 for pairing | Open |
| T004 | Build 5–10 planet metadata pilot | Traceable dossiers and all inclusion/exclusion reasons; inspected pilot marked development | T002–T003 | Open |
| T005 | Specify and reproduce Table 5 | Event list/denominators and conventions reconciled; exact match or explained differences | T002–T004 | Open |
| T006 | Decide Track A feasibility and one primary extension | Signed decision entry with novelty, metadata and precision evidence | T001,T004,T005 | Open |
| T007 | Implement minimal real adapters | Tests against small attributed fixtures; raw provenance retained | T006 | Open |
| T008 | Simulate concrete failure modes / design precision | Design report identifies recoverable quantities and adequate cluster counts | T004,T006 | Open |
| T009 | Freeze analysis protocol | Cohort, origins, bins, models, metrics, folds and final-outcome lock recorded in commit | T006–T008 | Open |
| T010 | Fit earlier-only calibration rule | Reproducible development outputs; bound/uncertainty diagnostics | T009 | Open |
| T011 | Execute held-out evaluation | Paired scores, uncertainty, planned sensitivities and complete provenance | T010 | Open |
| T012 | Independent scientific review | Reproduction/criticism with concrete evidence; findings resolved or reported | T011 | Open |
| T013 | Write manuscript and release artifacts | Every result traceable to analysis; scope and citations verified | T012 | Open |

## Suggested first division

- Agent A: T001 and forecast/source side of T002.
- Agent B: T003 and the executable side of T004.
- Both: swap review roles before T006.

Do not run different agents into the same source file concurrently. A shared
filesystem does not provide isolation; use explicit ownership or worktrees.
