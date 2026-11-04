# First session: turn this seed into an evidence-backed pilot

Read `AGENTS.md`, `README.md`, `docs/novelty_gate.md` and the first sections of
`docs/literature_review.md`. Then follow this sequence. Routine research and
local implementation are already the intended work; do not seek confirmation
for every reversible step.

## 1. Both agents establish the same starting point

Run the tests and synthetic example in a fresh output directory. Read the
implementation status; do not infer that a planned component already exists.
Inspect the initial commit and `coordination/decisions.md`. Claim work in the
task board so concurrent agents do not edit the same files unexpectedly.

## 2. Divide the first scientific work

**Agent A: literature and forecast provenance**

- Read ExoClock IV Section 5.1/Table 5 in the version of record.
- Trace the corresponding DRB/DRC files, exact versions, issue evidence and
  uncertainty conventions; verify the publication/version dates in the ledger.
- Read the closest independent studies and challenge every novelty claim.
- Produce a short written decision on which one extension is worth testing.

**Agent B: outcomes and reproduction**

- Acquire the documented release artifacts if accessible; save exact bytes,
  source identifiers and hashes before transformation.
- Inspect actual schemas and exposure-level identifiers. Use 5–10 planets to
  test feasibility, not to estimate population tail coverage.
- Trace later TESS measurements to the underlying independent observations.
- Build a small, fully auditable reproduction table before scaling up.

Swap review roles for the first pilot. Either model can take either role.

## 3. First concrete deliverable

Create `results/pilot_v1/` with:

1. A metadata-only inclusion/exclusion flow and source manifest.
2. Five to ten planet dossiers linking one frozen ephemeris to later events.
3. A report of which ExoClock Table 5 definitions can be reproduced exactly.
4. A covariance and time-system completeness report.
5. One individually inspected prediction plot per planet.
6. A clear **continue / narrow / pivot** recommendation, with its evidence.

Keep the final evaluation block unopened during model development. A pilot whose
outcomes have already been inspected is development material and cannot later
be relabelled untouched validation.

## 4. Decide the first-paper scope

If issued distributions and independent outcomes are recoverable, retain Track
A as primary. If only historical timing observations are recoverable, propose a
clearly labelled Track B study and update the title/estimand. If neither route
has an adequate scientific extension beyond existing work, record the finding
before investing in more automation.

Freeze cohort rules, scoring, chronology, exclusions, calibration folds and one
primary contrast in a protocol commit **after metadata feasibility work and
before inspecting the final evaluation outcomes**. The seed configuration is
deliberately provisional.

## Prompt to paste into either agent

> Read AGENTS.md, START_HERE.md and docs/novelty_gate.md. This is a research seed,
> not a completed study. Begin the role allocated in coordination/task_board.md.
> Revisit the supplied primary sources and distinguish ExoClock's existing
> retrospective benchmark from our proposed extension. Acquire and audit only a
> small sample first. Preserve availability dates and independent exposure
> lineage. Report concrete evidence, uncertainties and decisions in the shared
> coordination files; do not manufacture missing covariance, dates or results.

## Prompt for an independent critic

> Read the protocol and the actual pilot artifacts. Try to explain the result
> using leakage, observation selection, timing conventions, covariance omission,
> outcome-dependent exclusions, correlated events or prior published work.
> Distinguish demonstrated defects from plausible concerns. Supply a reproducer
> or a specific source for each important criticism. Assess whether the remaining
> contribution is scientifically useful and appropriately bounded.
