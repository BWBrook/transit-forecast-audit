# Independent review package

Prepared for Barry W. Brook on 9 November 2026.

**Start with `REVIEW.md`.** It contains the scientific judgement, detailed findings, expansion options, revision plan, revised abstract/opening/discussion, reference index and final brief for Claude and Codex.

The reviewed project version is `BWBrook/transit-forecast-audit` at commit
`629f466a2567152047d9cd75be336d865a1d68ad`.
This package is a review of that version. It does not change the project, replace its frozen experiment, or constitute a new confirmation study.

## Contents

| File/directory | Purpose |
|---|---|
| `REVIEW.md` | Complete review and agent brief |
| `checks/recompute_review.py` | Independent saved-result aggregation, stored-draw percentile verification and Gaussian-event scoring |
| `checks/check_saved_measurements.py` | Separate standard-library-only ledger, metadata and HR 858 b sequence checks |
| `checks/make_review_figure.py` | Rebuild the review diagnostic from actual saved measurements and frozen model parameters |
| `checks/check_sensitivities.py` | Independent aggregation of saved sensitivity per-planet differences |
| `checks/requirements.txt` | Dependencies pinned to the review runtime |
| `evidence/review_check_results.json` | Principal verification outputs, exploratory intervals and input SHA-256 hashes |
| `evidence/evidence_measurement_check.json` | Measurement-accounting and trajectory check outputs |
| `evidence/sensitivity_aggregation_check.json` | Independent sensitivity arithmetic |
| `evidence/planet_effects_review.csv` | Per-planet contrasts and coverage/width comparison |
| `evidence/hr858b_review.csv` | Actual saved HR 858 b timings and forecast residuals |
| `evidence/independent_gaussian_scores.csv.gz` | Independently computed M0/M2 scores for 1,786 Gaussian events |
| `evidence/review_diagnostics.png`, `.pdf` | Review figure; actual data, not a synthetic demonstration |
| `evidence/freeze_subset_check.json` | Hash check of the downloaded subset of frozen inputs; explicitly not a full verifier rerun |
| `evidence/source_snapshot_manifest.json` | Pin, file-level Git blob verification and download scope |
| `SHA256SUMS.txt` | Checksums of package contents |

## Run the checks

Use a local checkout at the exact commit above. If the working project has moved on, create a separate detached worktree or checkout. The scripts need the project's tracked data files; they do not acquire raw TESS data or require a network connection.

The main calculations were run with Python 3.12.14, NumPy 2.3.5, pandas 2.2.3, SciPy 1.17.0 and matplotlib 3.10.8. A separate environment is preferable to changing the frozen project's environment.

From this review package directory:

```bash
python3 -m pip install -r checks/requirements.txt
python3 checks/recompute_review.py --repo /path/to/pinned-project --out /path/to/new-review-output
python3 checks/check_saved_measurements.py --source /path/to/pinned-project --output /path/to/new-review-output/evidence_measurement_check.json
python3 checks/check_sensitivities.py --repo /path/to/pinned-project --out /path/to/new-review-output/sensitivity_aggregation_check.json
python3 checks/make_review_figure.py --repo /path/to/pinned-project --evidence /path/to/new-review-output
```

Keep output outside the audited checkout. The first script enforces this. The measurement-accounting script uses only Python's standard library and can run without installing any dependencies. The sensitivity script additionally needs pandas/NumPy. The plot script runs after the main script.

The main quadrature calculation can take a few minutes on one CPU. `--skip-gaussian` performs only the fast saved-output aggregation; its output explicitly records that the independent convolution was skipped. Do not describe that shorter run as a full numerical reproduction.

### Expected key outputs

- Status `passed` from the main script.
- Accepted primary counts: 2,185 events, 151 planets/hosts; 399 non-Gaussian events.
- Primary M2 − M0: approximately −0.121307804524.
- Stored joint-refit percentile interval: approximately [−1.839772910799, +2.195684963454].
- Independent Gaussian scoring: 1,786 events; 109 planets with entirely Gaussian accepted sets. Maximum differences in those complete per-planet summaries below 10⁻⁶ standardised units; observed here about 2.05 × 10⁻¹¹.
- HR 858 b: 16 accepted events; zero 95% coverage under each of M0–M3.
- Saved sensitivity differences reproduce their scenario summaries.

Floating-point round-trip CSV reading matters for large BJD values. The script uses it to avoid parser rounding differences being amplified by the interval-score miss penalty. Rebuilt image metadata and compressed-file headers need not be byte-identical; compare numerical outputs and recorded input hashes.

## What these checks do not establish

The main scorer does not import the project's implementation. Its M0 calculation is analytic; its M2 calculation integrates the lognormal variance mixture with independent adaptive quadrature and solves for the predictive interval endpoints. It checks complete saved per-planet scores only where all accepted timings are Gaussian. It does not recreate the missing non-Gaussian likelihood grids.

The stored-draw check recomputes percentiles of saved draws. It does not rerun the 2,000 calibration refits. The measurement script checks saved measurements and metadata; it does not independently identify transits or extract light curves. The sensitivity check verifies aggregation, not scenario refits or all event convolutions.

New coverage intervals, influence calculations and figures are **exploratory review diagnostics on inspected outcomes**, conditional on frozen point parameters where stated. The main review explains why they cannot replace the original primary inference. No synthetic event outcomes are presented as observations; the figure's right-hand bands are explicitly model-implied latent intervals.

## Attribution

Source data and analysis products are from Barry W. Brook's transit-forecast-audit project at the pinned commit, building on ExoClock, TESS and MAST. Original project code is MIT-licensed; project text/figures/derived data are stated as CC BY-SA 4.0. Review-derived tables/figures retain attribution and are offered under CC BY-SA 4.0. New check scripts are offered under MIT; see `LICENSE-CHECKS.txt`. No third-party journal article or raw photometric file is redistributed in this package.
