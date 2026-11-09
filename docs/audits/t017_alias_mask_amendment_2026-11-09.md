# T017 exploratory checker amendment: target-harmonic masking

Codex (GPT-6.1-sol), 9 November 2026. The fixed sample was committed in
`c61c0fc` before any T017 extraction. Its first complete execution processed
all 35 products, both flux routes, in 145 seconds. No file/hash failure,
download or S74–S97 access occurred. The complete first result set, original
engine and tests are preserved in the ignored `attempt1/` archive; the tracked
`attempt1_receipt.json` binds every archived byte and the original run receipt.

## Defect and evidence

The independent checker searches and masks sequential BLS signals. Residual
peaks can be the target itself or a target harmonic; the first implementation
treated every residual peak as a separate companion and masked it during the
shared-shape and timing fits. It could thereby remove the target transit.

WASP-18b/S104 PDCSAP has a duplicate same-period, same-phase peak. Masking it
leaves only 362 folded points and drives the trapezoid fit to its bounds,
whereas SAP has thousands of folded points and a normal target shape.
WASP-126b/S98 PDCSAP has a quarter-period residual harmonic; masking its
overlaps produces weak, shifted profiles. Its SAP route finds the ordinary
target train. These are checker defects/ambiguities, not established defects
in the frozen measurements.

## Repair, fixed before rerun

The original case list, design bytes and discrepancy triggers are unchanged.
Only companion-mask construction changes. A residual signal within 1% of an
integer or reciprocal-integer target period ratio (orders 1–4) is classified
as a harmonic candidate. Its mask cannot remove cadences within 1.2 detected
target durations of the target's own phase-blind BLS train. It still masks its
other phases; a same-period opposite-phase signal remains masked. Nonharmonic
signals, including coincident transits, keep their original masks.

Every harmonic candidate, overlap count and protected target cadence count is
recorded. This classification does not establish whether a separate physical
companion exists; exact commensurabilities/overlapping signals can remain
ambiguous. No issued epoch or frozen outcome enters mask construction.

A synthetic regression proves that duplicate and quarter-period residuals do
not mask away the target, while opposite-phase and nonharmonic companion masks
remain active. The existing six synthetic tests remain in force. The amended
engine and this note are committed before rerunning the same 35 products.
The executable checks both original design and amended source commit bytes.

This is an exploratory implementation repair after inspecting the first
checker outputs. It is not an untouched test, fresh qualification, threshold
relaxation, new sample or replacement of the frozen scientific result. All
first-attempt discrepancies stay inspectable, and any surviving discrepancy
is reported under the original triggers rather than tuned away.
