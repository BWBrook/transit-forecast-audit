# Step 3c review: full reconstruction draft

Codex (GPT-6.1-sol), 10 November 2026, from `f7a3d60`; T026/D082,
thread 156/message 3180. Clear corrections and cuts are incorporated in `14`.
The structure is worth keeping. Further broad compression would remove useful
explanation rather than solve a material writing problem.

## Cuts and essential restorations

Main text falls from **3,760 to 3,482 words**, a cut of **278 (7.4%)** under
one consistent count: whitespace words after removing headings, claim comments
and citation brackets. The author's approximate count used a different
convention. The abstract grows from 178 to **187 words**, still one paragraph,
because it now gives the primary estimate and interval, not just “inconclusive”.

| Section | Before | After |
|---|---:|---:|
| Introduction | 629 | 617 |
| Data and Methods | 1,209 | 1,173 |
| Results | 1,186 | 1,170 |
| Discussion | 736 | 522 |

Cuts remove the repeated prior-work recital and forecasting explanation in
Discussion, the evaluative coda about the correction, the hypothetical
zero-of-180 binomial aside, and smaller rhetorical repetitions. The concrete
JWST observing-window example earns its space and stays. The future-data
proposal and ecological generalisation remain, briefly.

Three compact restorations matter: the abstract's −0.12 [−1.84,+2.20];
conditional scoring assumptions in Methods; and timing likelihoods conditional
on fitted shape/noise treatment rather than full nuisance marginalisation.
M1/M3, the 399 primary grids and the extension summary were already present.
They need no further main-text expansion. Appendix plans now explicitly retain
all four models' parameters/results, detailed score assumptions, and the
extension's defined/undefined draw accounting.

## Scientific and source corrections

| Finding | Disposition and evidence |
|---|---|
| The “at most 3%” covariance effect is from Track R, not the final cohort | Remove this unnecessary percentage. `results/pilot_v1/independent_review/covariance_review.csv` and C004 govern the earlier benchmark. No replacement final-cohort maximum is claimed. |
| DRB “too narrow at the median” / DRC “calibrated at the median” turn fitted mixture scales into empirical calibration statements | Remove the old parameter recital; retain the development motivation, actual final training cohort and frozen M1/M2 parameters. |
| Accepted-injection coverage is confused with attempted-injection recovery | Failures stay in recovery accounting, while timing calibration is conditional on accepted injections. Original transit windows were masked, not subtracted. C038 and `sprint2_outcomes.inject_run` establish the distinction. |
| Timing posterior/normal approximation and calibration/scoring representations need precision | State fitted shape/noise conditioning, the 95%-endpoint Gaussian check, grid scoring and Gaussian calibration approximations. `acceptance.py`, `sprint2_outcomes.py`, `t015_timing_pipeline.py` and the frozen configuration specify these. |
| The standardised score was presented without its conditional interpretation | Restore the common per-event divisor and outcome-derived likelihood/normaliser qualification. Appendix B retains ancillary-descriptor, observation-model and selection assumptions. These are not established by the numerical replay. |
| The 1.9/2.7 ratios are reported uncertainty scales, not full non-Gaussian SDs | Equal-planet median 1.857997 and pooled median 2.693756 reproduce the two precision CSVs. For non-Gaussian timings the reported scale is a 68% half-width; scoring uses full-grid variance. |
| S105 sensitivity sounds like a new primary analysis | Identify −0.09 [−1.88,+1.12] as fixed-fit conditional resampling; the frozen joint-refit primary remains unchanged (C059). |
| DRC rescoring says DRD is used “only” for cycle labels | The catalogue period also constrains the timing search. State that both search periods and cycle labels retain DRD information; this is retrospective measured-outcome comparison, not a historically executable DRC-era measurement pipeline. |
| M1 “scored worst” is loss-scale dependent | Say worst **standardised IS95**. Its raw-minute score has a different ranking (`final_primary/descriptives.json`). |
| Allocation failure is explained causally by rarity | Restrict the conclusion to the tested 10% policy/padding grid and measured-midpoint endpoint. The finite optimum does not identify the cause (C064). |
| Unrecovered transits “have no error” | Their errors are unknown. Accepted-sample figures do not estimate catalogue-wide failure. |
| Boundaries and covariance availability | Keep numerical near-boundary exclusions distinct from a time conversion. Published covariance would eliminate this reconstruction step, not establish calibration or remove all covariance uncertainty. |
| Agol's check is called “five later timings” without issue chronology | Primary Section II checks five July 2024 timings outside the fit; the preprint posted in September 2024. Name those dates rather than implying they followed verified public issuance. Specify planet h for the tens-of-minutes drift. |
| Brook (2000) “scored” may imply a proper-score method | Use “tested”. First-half fitting/second-half evaluation is supported; that methodological analogy does not establish use of proper scoring rules. |
| Bonfanti's “up to five hours” loses the definition | Use simulated TTV **semi-amplitudes**, about two hours for b and five for c. |
| Manifest and AI provenance are overstated or incomplete | Describe reciprocal construction/review plus separate verification, restore Sonnet 5.5's initial drafting role, and call the correspondence reviewed snapshots rather than a full transcript. Back matter remains a journal-formatting stub. |

The source audit verified the JWST example, ExoClock IV's explicit optimistic
DRD comparison, OSF identifiers/licences and current MAST acknowledgment.
Relevant primary sources: [Agol Section II](https://arxiv.org/html/2409.11620v1#S2)
and [posting date](https://arxiv.org/abs/2409.11620),
[Bonfanti Section 5.2](https://arxiv.org/html/2411.14911v2#S5.SS2),
[Brook author record](https://researchers.mq.edu.au/en/publications/predictive-accuracy-of-population-viability-analysis-in-conservat/),
[Gardner Section 3.1.11](https://ntrs.nasa.gov/api/citations/20250006005/downloads/36_Gardner_2023_PASP_135_068001.pdf),
[ExoClock IV Section 5.1](https://arxiv.org/html/2511.14407v1#S5.SS1)
and [MAST guidance](https://archive.stsci.edu/publishing/mission-acknowledgements).
These are source-specific checks, not a new exhaustive novelty search.

## Verification and unfinished production

Three independent bounded reviews covered numbers, writing/essential coverage,
and sources. Numerical and editorial final rechecks are clean. Parent checked
the source chronology, timing implementation, parameters, ratios and Table 1;
all seven terminal-status counts match the ledger and sum to 3,103.
`results/reconstruction_review/step3c_check.json` records the arithmetic,
word-count convention, draft hash and input hashes. Native freeze verification
has no mismatches; eleven preserved artifact hashes match. No code/environment
changes or local unit-suite rerun is needed for this prose review.

This is still a reconstruction draft, not an assembled release. Figures 1,
2, 3a and 4b, Table 3 and Table 2's percentile cells remain unbuilt; the Fig. 3a
choice remains open. State the percentile weighting convention when those cells
are filled. Appendices A–H are plans requiring assembly from the existing
evidence, not completed appendices. The eight † references remain outside the
frozen bibliography; full contributions and archive metadata remain to finish.

The manuscript, brief, guide, bibliography, scrivmark state and earlier
reconstruction stages are unchanged. No raw photometry, headers, fitting,
displays, new access or release; sectors 74–97 remain closed.

Next: Claude — reconcile the full draft and its cuts before the next reconstruction stage.
