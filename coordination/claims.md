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
| C005 | Original conditional REML estimate a=1.087 and planet-bootstrap interval; see C008 for independent host-bootstrap verification and qualified jitter interpretation | Conditional development result; not physical attribution or universal tau bound | `7a9f1a6:results/pilot_v1/local_noise/` | `uv run --extra analysis python scripts/local_noise_structure.py` |
| C006 | Original mixture point estimates and profile intervals; coarse-node posterior tail counts superseded by C009 | Point estimates supported; original tail labels superseded; intervals not independently host-qualified | `7a9f1a6:results/pilot_v1/variance_components/` | `uv run --extra analysis python scripts/forecast_variance_components.py` |
| C007 | Original approximate geometric inventory: 224 planets/206 hosts, 5071 predicted transits and 171 planets in nominal post-issue windows | Already-observed and strict-A interpretations rejected by C011; counts not corrected | `7a9f1a6:results/sealed_inventory/` | `uv run --extra analysis python scripts/sealed_era_inventory.py` |
| C008 | Independent error-contrast REML reproduces a=1.086576, tau=5.005 s and LR 27.39/1.48; 400 host resamples give a=1.04984–1.12091 | Verified conditional development result; measurement-error attribution unresolved | `a3f70fd:results/pilot_v1/tranche2_review/noise_review.json` and adjacent `noise_*` | `python scripts/review_tranche2_noise.py --bootstrap 400` |
| C009 | Stable mixture integration gives DRB b=2.24949,s=1.09314; DRC b=0.97626,s=3.14868. DRC posterior median lambda>10 count is 29, posterior expected count 61.21 and model population probability 0.2323 | Verified numerical correction; distinct conditional estimands, not observed failures; host uncertainty open | `a3f70fd:results/pilot_v1/tranche2_review/mixture_*`; `docs/tranche2_mixture_review.md` | `python scripts/review_tranche2_mixture.py` |
| C010 | Released training span improves conditional host-held-out log score versus constant mixture by 0.02709 nats/window [0.00673,0.05399]; epoch count and TESS inclusion lack clear gains | Exploratory development only: one split, three predictors, global fixed a includes held-out hosts, no chronological or sealed validation | `a3f70fd:results/pilot_v1/tranche2_review/predictor_*` and `metadata_*` | `python scripts/review_tranche2_predictors.py --order 192`; repeat with `--order 384`, then `--verify` |
| C011 | Official calendar metadata reveals extended S98, interrupted S99, S100 crossing issue date and ongoing S110; old day-after-publication constant is one UTC day early | Verified metadata correction; exact barycentric exposure windows and revised inventory counts open | `a3f70fd:results/pilot_v1/tranche2_review/schedule_review.json` and `schedule_calendar_review.csv` | `python scripts/review_tranche2_schedule.py --acquire` |
| C012 | A forecast-independent SPOC 120-s pipeline reproduces 27/27 ExoClock DRD mid-times (median −2.7 s), and its scaled σ are calibrated on 261 real-noise injections (z-RMS 1.03 [0.90, 1.17]); implied ExoClock σ scale 1.12 [0.96, 1.29] | Development validation, 4 planets; same photons, not independent replication | `results/t015/` | `uv run scripts/t015_timing_pipeline.py` |

Interpretation, primary-source evidence and limits are in
`docs/independent_review.md` and `docs/literature_update_2026-11-04.md`, both at
`16b5799`. The new-model and novelty propositions remain proposals under D024.
Do not promote a source-record date to verified availability/UTC, catalogue
lineage to cadence independence, or synthetic demonstrations to astronomical
results. Published rounded aggregates support a numerical reconstruction, not
unique recovery of the authors' original event list.
