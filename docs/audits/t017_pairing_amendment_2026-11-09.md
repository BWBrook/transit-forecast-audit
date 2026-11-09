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

Amendment/source/tests commit `506ab58` preceded comparison regeneration.
The unchanged independent-fit files now supply **347 flux-route matched
pairs**, formerly 340. Exactly four product/routes gain pairs:

| Product/route | Original | Amended |
|---|---:|---:|
| HR858b S105 SAP | 2 | 4 |
| TOI-157b S98 PDCSAP | 10 | 11 |
| WASP-170b S99 PDCSAP | 4 | 5 |
| WASP-82b S98 PDCSAP | 6 | 9 |

An independent sorted dynamic-programming implementation maximizes valid
pair count before summed distance, without calling the Hungarian solver.
It reproduces every amended pair identity exactly. It also reconstructs all
25 remaining unpaired flux-route rows: each is an
`insufficient_window_coverage` refusal, and every row has a timing from the
other flux route or Claude's C050 checker. None is an independently timed
large disagreement. These are flux-route rows, not 25 distinct events.

The amended summaries contain **zero large discrepancies among the ten
controls**. The unchanged raw diagnostic still flags six control planets
(formerly seven); TOI-157b drops below its unmatched-fraction threshold.
The remaining flags are coverage refusals and WASP-18b's phase ambiguity.
D073's adjudication supplies their interpretation; it does not erase the
raw flags or relax their thresholds. They identify no frozen timing fault
in the evidence examined, so a broader 2026 tranche is not warranted on
this evidence. The HR858b S105 model/shape sensitivity remains separate.

For WASP-18b, the SAP residual signal's phase is 0.50285, depth 451 ppm and
duration 0.081 d (the transit's fitted duration). This is consistent with a
secondary eclipse. The PDCSAP same-period signal is near phase 0.992,
duration 0.24 d versus 0.081 d, and depth 259 ppm versus the transit's
9,931 ppm. A phase curve or detrending residual is plausible. Saved phase,
depth and duration alone do not independently prove astrophysical identity,
and the broad residual should not be declared uniquely astrophysical.

Reproduction (use a runtime containing NumPy/SciPy):

```sh
python -m unittest discover -s tests -p test_t017_pairing.py -v
python scripts/t017_compare.py
python scripts/t017_pairing_audit.py
```

Four targeted tests pass. Input hashes, pre-amendment comparison hash,
pair-count changes, independent pair-set equality and all refusal/alternate
checks are in `results/independent_validation/t017_pairing_review/receipt.json`
and `unpaired_check.json`; comparison output hashes remain in the regenerated
T017 `comparison_receipt.json`. No light curve or header was opened. This is
a recorded post-review amendment on already inspected evidence, not new
qualification or a replacement of the frozen outcomes.
