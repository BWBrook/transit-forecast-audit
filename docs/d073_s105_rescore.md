# D073: HR858b S105 measurement sensitivity

Codex, 9 November 2026. This definition is written before the sensitivity is
executed. It is a post-unblinding robustness diagnostic, not a replacement for
the frozen outcomes, an uncertainty calibration or a new primary test.

Only `HR858b|S105|DRD645`, `DRD647` and `DRD649` change. For each event, take
the unweighted median of the four exact saved point timings from the C050
and T017 checkers on PDCSAP and SAP. These share photons: the median is an
explicit sensitivity centre, not four independent observations or a more
precise estimate. Match these already-fitted timings uniquely within P/4;
do not reopen any light curve.

The four cases are the unchanged baseline, shift to that consensus only,
double width only, and shift plus double width. The reported centre moves by
the consensus minus frozen reported timing. Doubling width maps every offset,
support endpoint and reported quantile offset to twice its value about the
reported centre; it doubles the reported sigma and subtracts log(2) from the
grid log density. The Jacobian preserves integrated mass. It does not centre
an asymmetric likelihood by its median or change its original shape. All
three affected outcomes are non-Gaussian; Gaussian handling is implemented
and tested consistently but does not affect these data.

The unchanged scoring adapter scores the three events under all four saved
models. The baseline must reproduce every saved numeric metric to 1e-9.
The adapter's subset-only weights are replaced with the original full-cohort
weights, then these twelve event/model rows are merged into the saved full
score table. Every other score row and outcome remains unchanged. No model
is refitted, event admitted/rejected, or primary interval recomputed.

Report equal-planet means on the primary cohort and HR858b separately, for
standardised IS95, forecast-SD-normalised IS95 and raw IS95 minutes. Report
M2−M0 contrasts and conditional fixed-fit host-bootstrap intervals using the
same 10,000 draws and seed 20261109 as T018. Those intervals are descriptive,
not the frozen joint-refit primary interval. HR858b-only intervals are omitted
because one host supplies no host-level sampling information. Coverage95 is
also checked; raw score minutes are not telescope allocation.

The script hashes its sources and affected grids before/after. Regenerable
full score tables and transformed grids stay in the ignored `working/`
directory; compact summaries and a receipt carry the evidence.

Reproduce: `.venv/bin/python scripts/d073_s105_rescore.py`, in the restored
exact frozen evaluation runtime. No candidate-sector photometry or headers
are accessed.

## Execution result

The unchanged baseline adapter reproduces all nine saved numeric metrics for
the three events exactly (maximum absolute error zero). The consensus shifts
are +7.9389, −10.7249 and −12.5396 minutes for DRD645, 647 and 649. All 2,182
other outcomes and 8,728 other event/model score rows remain identical.

| M2−M0 scale, primary cohort | Frozen baseline | Shift only | Width ×2 only | Shift and width ×2 |
|---|---:|---:|---:|---:|
| Standardised IS95 | −0.121308 | −0.121308 | −0.089004 | −0.089004 |
| Forecast-SD-normalised IS95 | +0.081505 | +0.081505 | +0.096204 | +0.096204 |
| Raw IS95 minutes | −8.460441 | −8.460441 | −8.225570 | −8.225570 |

For the combined sensitivity, the conditional 95% intervals are respectively
[−1.880, +1.124], [−2.030, +1.678] and [−33.521, +5.678]. These descriptive
fixed-fit intervals all include zero. The frozen joint-refit primary interval
and its verdict remain unchanged.

On HR858b alone, the standardised contrast changes from −108.646 to −103.768;
raw IS95 contrast changes from −1,824.697 to −1,789.231 score-minutes. Every
one of HR858b's 16 events remains outside the convolved 95% intervals under
all four models, in every sensitivity.

The shifts change individual absolute scores but cancel from the interval-score
contrast: these events remain beyond both models' lower interval endpoints,
where each loss has the same linear residual slope. Doubling width changes
both the convolved interval endpoints and the standardisation denominator.
This supports robustness of the qualitative comparison to this particular
measurement perturbation; it does not validate the conditional measurement
likelihood, exclude other measurement errors or establish observing capture.

`results/d073_s105_rescore/summary.csv` reports all four model means and
M2−M0 contrasts on the full primary cohort and on HR858b. `consensus.json`
keeps the unrounded checker inputs, `coverage.csv` the zero-capture checks,
and `receipt.json` hashes the source tables, grid transformations and outputs.
