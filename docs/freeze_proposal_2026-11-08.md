# Hash-bound freeze proposal (D063, verified and corrected by D064)

**Claude (Opus 5.5), 8 November 2026.** This follows Codex's acceptance of
D061 ([review](audits/d061_review_2026-11-08.md), D062).

**Independent check, Codex, 8 November (D064):** the manifest now also binds
two imported local modules, checks the interpreter version, and verifies that
its source commit contains the recorded tracked bytes. All scientific inputs,
forecasts and numerical code are unchanged. The source commit is
`bc853261cd301d5e0b08e7ffd4eab8b5cab98f80`; the verified manifest SHA-256 is
`5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1`.
This supersedes the unapproved D063 fingerprint `eb387f3e…`.
See [the independent review](audits/d063_manifest_review_2026-11-08.md).

This is a proposal. Nothing is frozen until Barry decides, and no protected
outcome has been opened. The package becomes binding only through Barry's
access record, which must cite this manifest's SHA-256. If any bound byte
changes afterwards, the protected run refuses.

```bash
.venv/bin/python scripts/freeze_manifest.py verify     # recompute every hash and binding check
```

**Manifest:** `results/freeze/freeze_manifest.json`. Its SHA-256 at the commit
that adds this document is recorded in D063 and in the board message.
`scripts/freeze_manifest.py build` regenerates it, and `verify` reports any
difference.

## What is bound

**Files** (SHA-256 and size; gzip files also carry a decompressed-content
hash):

| Group | Files | Contents |
|---|---:|---|
| Code | 21 | acceptance, measurement, evaluation, the manifest tool, adapter, forecast core and variance components, forecast maker, candidate package, outcome and timing core, remeasure and inventory helpers, local diagnostic dependency, Table 5 loader, `transit_audit` modules |
| Environment | 4 | `pyproject.toml`; `uv.lock`; uv locks for `final_measure.py` and `prefreeze_replay.py` |
| Config | 2 | `candidate_freeze.json`, `sprint1.json` |
| Event lists | 8 | core primary (3,103), extension exploratory (291), boundary exclusions (5), summary, source DRD event list, roster and roster summary, header-only access receipt |
| Parameters | 3 | frozen M0–M3 parameters, candidate fit record, calibration-only draws |
| Forecasts | 3 | core and extension DRD forecasts, forecast receipt |
| Calibration inputs | 10 | development outcomes, product identification, product table, covariance reconstruction, TTV flags, DRB/DRC/DRD OSF ephemeris and mid-time files |
| Injection evidence | 24 | `prefreeze_evidence.py`, `sprint2_analysis.py`, `prefreeze_replay.py`, the replication driver, frozen selection, ledger, run, product, real-transit tables and receipts for both samples, replay ledgers, runs and products, replay receipt, eight-criterion result |

**Environment details:**
- The uv locks pin what the replay and the development measurement actually
  used: numpy 2.3.5, scipy 1.18.1, astropy 8.0.2, lightkurve 2.5.1.
- The evaluation `.venv` (Python 3.13.16, 17 packages) is recorded and checked
  on verify.
- There are 75 bound files in total. Every tracked record must match its
  recorded source commit as well as the current file; build refuses uncommitted
  bound changes. Interpreter inspection failures also refuse.

**Likelihood grids.** The manifest records 780 grid hashes with an aggregate
hash: 404 development grids, which the acceptance support check reads for
calibration, and 376 replayed injection grids. The grids are regenerable and
stay outside the repository.

**Binding checks** (all true when built; any failure blocks the build):
- original and replayed product and run diagnostics are equal for both samples
  (SPOC, removal), so the evidence cannot silently mix versions;
- every replayed grid matches the hash in its ledger row;
- the decompressed forecast content matches the forecast receipt, and the
  forecasts were made from the bound parameters;
- the core forecasts cover exactly the core manifest.

**Local-only inputs.** Six bound files are not in the repository:
- the five ExoClock OSF files, whose hashes match `results/pilot_v1/source_manifest.csv`;
- the regenerable source DRD event list, whose tracked descendants (the three
  manifests) are bound.

## Access binding

The access guard (`final_evaluation.era_limit`, shared by `final_measure.py`)
keeps Codex's exact affirmative-decision fields and adds one requirement. The
record must cite this manifest's SHA-256, and `verify` must report no
difference. The protected record therefore authorises one concrete,
unchanged package.

```json
{"authorised_by": "Barry W. Brook", "decision": "authorise_protected_access",
 "decision_id": "D0xx", "date": "YYYY-MM-DD",
 "freeze_manifest_sha256": "<sha256 of results/freeze/freeze_manifest.json>"}
```

The tests cover:
- a missing or mismatched hash refuses;
- a changed package refuses;
- a cited hash on a verified package passes;
- Codex's negative-record cases still refuse.
- interpreter drift blocks access even when the package list is unchanged;
- recorded tracked bytes must exist at the named source commit.

No real record exists.

The full suite passes 99 tests. In a restricted tool sandbox, uv's global cache
may be inaccessible; `UV_CACHE_DIR=/private/tmp/transit-freeze-uv-cache` supplies
a writable cache for `verify` without changing the inspected environment.

**Attribution of the development run.** The guard change touches only
`era_limit`. The config and module docstring are unchanged, so Codex's
`check_d061_package.py` still verifies the saved 200-draw run against the
current source (numerical AST identical) and config.

## The protected run, once authorised

The commands are also recorded in the manifest.

1. `uv run scripts/final_measure.py --manifest results/prefreeze/manifest_core_primary.csv --out data/derived/final_primary/measured --era protected`
2. `.venv/bin/python scripts/final_evaluation.py evaluate --manifest results/prefreeze/manifest_core_primary.csv --forecasts results/prefreeze/forecasts_core_draft.csv.gz --windows …/windows.csv.gz --products …/products.csv --coverage …/coverage.csv --out results/final_primary --era protected --bootstrap 2000 --conditional-bootstrap 10000 --workers 8` (about 2 h);
3. `.venv/bin/python scripts/freeze_manifest.py portable-receipt results/final_primary/scores.receipt.json`;
4. the same pair of commands on the 291-event extension, labelled exploratory.

**Interpretation.** The decision is fixed in advance:

| 95% joint-refit interval for planet-balanced standardised IS95, M2 − M0 | Verdict |
|---|---|
| Below zero | The calibration improves |
| Above zero | The calibration worsens |
| Spanning zero | Inconclusive |

The secondary results are reported as declared in the config: the conditional
fixed-parameter interval, the strata, the sensitivities, and recovery against
all intended events and against coverage-qualified events.

## Portable receipt

The adapter's receipt keys grid hashes by absolute path. `portable-receipt`
writes a copy that differs only in having the repository-root prefix removed
and that records the original receipt's SHA-256. For the development run:

- `results/prefreeze/final_path_dev/run/scores.receipt.portable.json` is
  committed;
- its `portable_from_receipt_sha256` equals the `adapter_receipt_sha256` that
  the run summary recorded.

The original stays local.

## Declared open limits (unchanged)

- Full-support likelihood fitting (calibration uses the Gaussian approximation).
- Multi-planet identification (the core is single-DRD-planet hosts).
- Exact and exhaustive boundary eligibility (five conservative exclusions).
- The development-selected χ² ≤ 100 gate.
- The replication's late bias of +0.07, reported and not corrected.
- Conditional injection calibration with narrow coverage margins (lower bounds
  0.934 and 0.938).

## Decision for Barry

Whether to authorise protected access for this package. If yes, the record
above (with a decision ID and date) is written and the four commands run.
Before writing it, either agent can be asked to verify the manifest
independently.
