# Claims ledger

Shared evidence index for future article, public brief and agent guide. No
held-out empirical claim exists. Commands run from the repository root in its
Python environment; raw artifacts must match `results/pilot_v1/source_manifest.csv`.
Evidence commit `16b5799` contains both source scripts and the outputs below.

| ID | Claim and scope | Status | Evidence at commit | Reproduce |
|---|---|---|---|---|
| C001 | Independent base-R calculation matches all DRB/DRC Table 5 counts and percentages; DRD differs by one 1-sigma count; Initial not reproduced | Verified numerical reproduction, Track R | `16b5799:results/pilot_v1/independent_review/table5_independent_summary.csv`; raw hashes and line trace in adjacent `table5_*` files | `Rscript scripts/independent_table5.R` |
| C002 | The original consecutive-gap grouping yields 333/425 nonflagged groups spanning over 20 days; maximum 378.575 days | Verified development diagnostic defect | `16b5799:results/pilot_v1/independent_review/measurement_groups.csv` and `measurement_sensitivity.csv` | `python scripts/review_measurement_diagnostic.py` |
| C003 | Capped-span local-linear residuals have RMS 1.0968 for 4173 retained timings/336 planets; this does not identify pure measurement-error inflation | Verified conditional dispersion; causal attribution unresolved | `16b5799:results/pilot_v1/independent_review/measurement_sensitivity.csv`; `synthetic_identifiability.csv` contains explicitly synthetic counterexamples | `python scripts/review_measurement_diagnostic.py` |
| C004 | Under reconstructed WLS correlations plus published marginals, the largest absolute Track R total-variance cross terms are about 0.27%, 0.98%, 2.94% for DRB/C/D | Verified conditional sensitivity; not recovered posterior covariance | `16b5799:results/pilot_v1/independent_review/covariance_review.csv`; input receipt alongside | `python scripts/review_measurement_diagnostic.py` |

Interpretation, primary-source evidence and limits are in
`docs/independent_review.md` and `docs/literature_update_2026-11-04.md`, both at
`16b5799`. The new-model and novelty propositions remain proposals under D024.
Do not promote a source-record date to verified availability/UTC, catalogue
lineage to cadence independence, or synthetic demonstrations to astronomical
results. Published rounded aggregates support a numerical reconstruction, not
unique recovery of the authors' original event list.
