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
| C005 | Local TESS excess scatter scales with σ_Tmid: a = 1.087 [1.043, 1.117], white jitter τ ≤ 11 s, over 4173 events and 336 planets (span-capped groups, DRD flags excluded) | Development diagnostic; physical σ-proportional variance and selection not excluded | `results/pilot_v1/local_noise/` | `uv run --extra analysis python scripts/local_noise_structure.py` |
| C006 | Planet-level scale mixture on visit means: DRB b = 2.25 [1.87, 2.72], s = 1.09; DRC b = 0.98 [0.71, 1.28], s = 3.13 [2.78, 3.74], with 15 of 316 planets λ > 10 (origin flags, TESS 2022–23) | Development estimate, fixed a = 1.087; recovery verified by simulation on the real design | `results/pilot_v1/variance_components/` | `uv run --extra analysis python scripts/forecast_variance_components.py` |
| C007 | 224 DRD planets on 206 hosts fall in TESS sectors S98–S110, already observed, with about 5071 DRD-predicted transits; 171 planets fall in windows starting after the DRD journal date | Metadata only (FFI pointing coverage, approximate sector windows) | `results/sealed_inventory/` | `uv run --extra analysis python scripts/sealed_era_inventory.py` |

Interpretation, primary-source evidence and limits are in
`docs/independent_review.md` and `docs/literature_update_2026-11-04.md`, both at
`16b5799`. The new-model and novelty propositions remain proposals under D024.
Do not promote a source-record date to verified availability/UTC, catalogue
lineage to cadence independence, or synthetic demonstrations to astronomical
results. Published rounded aggregates support a numerical reconstruction, not
unique recovery of the authors' original event list.
