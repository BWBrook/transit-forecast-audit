# Independent verification of the freeze proposal

Codex (GPT-6.1-sol), 8 November 2026. A GPT-5.6-sol specialist independently
checked the verifier/access binding and the subsequent bounded repairs.
Codex recomputed file/grid hashes through a separate implementation, checked
local imports, environment metadata/locks, input provenance, event partitions
and the portable receipt. No photometry, FITS headers or protected data were
opened, and no actual access record was created.

**Decision: the corrected proposal is verified and ready for Barry's access
decision.** Nothing is frozen or authorised by this review.

```text
Manifest: results/freeze/freeze_manifest.json
SHA-256: 5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1
Source commit: bc853261cd301d5e0b08e7ffd4eab8b5cab98f80
```

## Findings and repairs

The original D063 proposal, SHA-256 `eb387f3e…`, had matching file/grid hashes
and a sound access binding. Three bookkeeping defects required correction
before approval:

| Finding | Repair and check |
|---|---|
| Two reachable local imports were unbound | Added `review_measurement_diagnostic.py` and `sealed_era_inventory.py`; the conservative local import closure of measurement, evaluation and evidence/replay now has no unbound modules |
| Interpreter version was recorded but not compared | Verification now compares Python separately from packages; a synthetic Python drift with identical packages blocks access |
| `built_from_commit` predates some recorded bytes | Bound code was committed before rebuilding; build and verify now check all tracked records against the named source commit |

Environment subprocess failures now propagate rather than appearing as an
empty package inventory. Independent review accepted these corrections.
The original fingerprint was never authorised and is superseded by the exact
fingerprint above. Numerical code, calibration, event lists, forecasts,
likelihood grids and scientific choices are unchanged.

## Independent results

- All **75 file records** match current SHA-256, byte count and, where
  applicable, decompressed-content hash. Every tracked record also matches its
  blob at the source commit above. The six local-only records remain byte-hash
  bound rather than Git-commit bound.
- All **780 likelihood grids** and their aggregate hash match. Their content
  is unchanged from the D063 proposal: 404 development and 376 replay grids.
- The local import closure of the four measurement/evaluation/evidence entry
  points contains **21 modules**; every one is bound. This includes lazy imports
  conservatively, without asserting they all execute in the primary run.
- The evaluation interpreter is **Python 3.13.16**; an independent installed-
  metadata inventory matches all **17 packages**. The measurement and replay
  locks have identical package/version sets, including NumPy 2.3.5, SciPy
  1.18.1, Astropy 8.0.2 and Lightkurve 2.5.1.
- Each of the five OSF local-input hashes matches its original download
  provenance. The sixth local input is the regenerable source event list.
- Core 3,103, extension 291 and five exclusions form an exact, unique partition
  of the source list's 3,399 events. Both forecast files cover their respective
  manifests exactly, including row counts.
- The portable receipt equals the original after the documented root-prefix
  transformation. Its original-receipt hash matches the saved run summary.
  No home-directory path was copied into this review.
- The supplied verifier reports **zero mismatches** and all eight detailed
  binding booleans are true. The full suite passes **99 tests**.

The first sandboxed verifier invocation could not read uv's global cache and
therefore safely refused. Using a temporary writable cache yielded a clean
verification; the independent installed-metadata check also confirmed that
no environment drift occurred. This was an access limitation of the tool
runtime, not a package change.

## Access and stopping point

The shared guard retains the exact affirmative Barry decision, decision ID and
canonical date requirements. It also requires this exact manifest SHA-256 and
a clean package verification. Changed source, files, grids, interpreter or
packages therefore refuse protected mode. No actual record exists.

The scientific readiness decision D062 stands. Previously declared limits
remain: conditional injection calibration, development-selected gross-fit QC,
late bias, Gaussian calibration fitting, exploratory multi-planet extension
and conservative boundary exclusions. This check does not claim new held-out
forecast performance.

Barry can now approve or decline freezing this exact package and opening the
protected data for the recorded primary and exploratory commands. Neither
agent should write the access record or run those commands before that decision.
No further agent research or qualification tranche is requested.

```bash
.venv/bin/python scripts/check_freeze_proposal.py
UV_CACHE_DIR=/private/tmp/transit-freeze-uv-cache .venv/bin/python scripts/freeze_manifest.py verify
.venv/bin/python -m unittest discover -s tests -v
```

The independent check writes
`results/sprint2_review/d063/independent_manifest_check.json` and does not
import the supplied verifier or access protected data.
