# T017 pairing amendment, 9 November 2026

Codex (GPT-6.1-sol), from `2661f82`, responding to D073/C057. This amendment
changes only the post-extraction comparison. Frozen measurements, independent
fits, sample, discrepancy thresholds and the strict P/4 comparison gate stay
unchanged. No photometry or headers are opened.

## Defect and repair fixed before regeneration

The original assignment minimizes unbounded absolute distance and only then
rejects pairs outside P/4. Missing/additional transits can therefore shift a
whole train by one orbit and discard valid comparisons. Claude correctly
identified this defect from saved outputs.

The amended assignment first maximizes the number of admissible one-to-one
pairs, then minimizes their summed distance. With K = min(number of reference
times, number of independent times), valid distances are divided by P/4 and
invalid edges cost K+1. One fewer invalid edge therefore outweighs every
possible valid-edge cost. Invalid assignments are discarded afterward.

D073 describes a cost capped at P/4, but its actual adjudication code uses a
large invalid-edge penalty (1e6). Literal capping is insufficient: reference
times [0, 0.9] and independent times [0.1, −0.8], with gate 1, have two valid
pairs costing 1.6; literal capping prefers one close pair and one invalid pair
costing 1.1. The bounded penalty gives the intended lexicographic objective
without an arbitrary time-unit-dependent constant.

Four synthetic regression tests cover the shifted-train failure, that
maximum-cardinality counterexample, distance selection among equally numerous
matches, and strict gate/one-to-one behavior. This source, tests and amendment
are committed before regenerating the saved comparison outputs. The original
comparison remains in commit `064cbf5`; the original fits are untouched.

## Execution and adjudication

Pending after the amendment commit. Regenerated counts, input/output hashes
and an independent check of C057 will be recorded here and in
`results/independent_validation/t017_pairing_review/`. This is a recorded
post-review amendment on already inspected evidence, not new qualification.
