# Step 3a review: section abstracts

Codex (GPT-6.1-sol), 10 November 2026, from `f916923`; thread 156,
message 3160; T024/D080. Supports the four-section structure and product-first
message. Clear corrections are incorporated into `09_section_abstracts.md`.
The earlier reconstruction, chosen main message, manuscript, brief, guide,
bibliography and scrivmark round are unchanged. No displays are built.

## Main finding: what P/4 actually bounds

The suggested limitation needs one qualification. In
`scripts/final_evaluation.py:terminal_ledger`, recovered mid-times are assigned
to the nearest DRD cycle with `round((tc − T0) / P)`. Only afterwards does
`scripts/acceptance.py:terminal_status` reject an otherwise acceptable timing
when its distance from that assigned prediction exceeds P/4.

Thus P/4 bounds the **assigned residual**, not necessarily the physical error
for the same transit. A structural example in period units is:

| Displacement from the original cycle | Nearest assigned cycle | Assigned residual | P/4 check |
|---|---|---|---|
| +0.2P | original | +0.2P | passes |
| +0.3P | original | +0.3P | fails |
| +0.9P | next | −0.1P | passes |

The last case could enter the score if the next cycle is in the fixed list
and the other checks pass. It is a counterexample to the unconditional claim
that every physical miss larger than P/4 is excluded. It is **not evidence
that an alias occurred in these observations**. The saved primary ledger has
zero `cycle_ambiguous` terminal rows; this cannot exclude aliases already
inside the assigned gate. Coverage, identification and fit failures
also prevent completeness inside P/4. The revised Methods names nearest-cycle
assignment; Discussion describes possible rejection or whole-cycle aliasing.
No frozen match, timing, score or verdict is changed.

## Hypothesis status and interpretation

- **H1:** conditional undercoverage of the reconstructed,
  measurement-convolved distribution among accepted timings. Neither the
  cause nor a missing number of padding minutes follows from coverage alone.
- **H2:** historical information span at comparable nominal precision is
  not a hypothesis about gross misses alone. The development span predictor's
  unstable transfer does not settle it. Replace “untestable with one gross
  miss” with an unresolved question, without requiring new analysis now.
- **H3:** retain the prespecified primary and inconclusive joint-refit interval.
  The common normaliser includes measured timing uncertainty; propriety is
  conditional on the observation model, ancillary measurement descriptors
  and ignorable selection, which are not established. Methods therefore
  states the conditional interpretation and alternative loss scales.
- **H4:** conditional measured-midpoint containment is available. Operational
  or full-transit capture and telescope cost need durations and attempted
  observing records; those were not measured by this test.

These refer to the original pre-access questions at `bc85326`, not the
withdrawn retrospective H1–H3 from the first reconstruction. Sources:
`docs/project_brief.md`, `docs/third_turn_review_2026-11-05.md`,
`configs/candidate_freeze.json`, D076 and manuscript Section 2.3.

## Numerical and scope checks

Independent bounded reviews checked numbers/hypothesis status and gate/score
semantics; the parent separately recomputed the main saved-table quantities.
Receipt: `results/reconstruction_review/step3a_check.json`, with source hashes.

| Item | Checked value or disposition |
|---|---|
| Intended/accepted | 3,103 / 2,185; 151 of 156 planets |
| Prediction-time coverage subset | 2,181 / 2,369; 92.064% |
| Pooled median absolute error | 1.1148 min; equal-planet-mass median 1.3149 min (C063) |
| Non-HR858 maximum | 26.299 min, hence the stated 26.4-min bound |
| M0/M2 coverage per planet | 0.9079365 / 0.9757620; M0 interval 87.8–93.4% is conditional |
| Ratio of mean widths | 1.66646, rounded 1.67 |
| M2 versus M0 per planet | 40 improve, 111 worsen, no ties |
| Primary difference and joint interval | −0.12131 [−1.83977, +2.19568] |
| HR858b | 16 accepted timings; all remain outside every model's 95% interval |
| Injection evidence | Point coverages 94.7% and 95.0%; the previous 0.93–0.96 range mixed coverage with its 90% uncertainty intervals |
| DRC horizon and input scatter | Earlier review 06 independently checked about 3.94 years and HR858b residual RMS 2.198 |
| Cohort | One **DRD-catalogued** planet per host, not physically single-planet stars |
| Allocation screen | No hindsight choice beat both equal-budget comparators within the tested 10% policy/padding grid; no universal claim about all rules |
| Planned Table 3 | Future metadata join/product, including five planets with no accepted timings; not an already released catalogue |

The withdrawn insurance explanation is removed again. The supported statement
is a larger width penalty for most planets and smaller miss penalties for a
few; HR858b remains missed by every model. ExoClock IV is described by its
fit-data reuse rather than assuming a numerical amount or direction of bias.

The useful message remains plain: accepted timings mostly agreed with issued
predictions to minutes, and the comparison table will show the exceptions and
support future method checks. The P/4 disclosure qualifies recovery and event
identity; it does not demand another data study before Barry's next step.

Only the reconstruction drafts and review/coordination record change. The
word cap is a maximum, not a target to fill. Verification and exact section
counts are recorded with D080. No raw photometry or headers opened; sectors
74–97 remain closed; nothing released.

Next: Claude — reconcile the step 3a corrections with Barry before the next step.
