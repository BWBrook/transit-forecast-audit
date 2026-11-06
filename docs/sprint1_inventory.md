# Sprint 1 metadata inventory

Status: metadata-only development evidence; no protected light curve, FITS
header, target-pixel file, or flux value was requested or opened.

The executable is `scripts/sprint1_inventory.py`. It reads the frozen DRD
ephemeris catalogue, the already audited official HEASARC sector-calendar
extraction, NASA Exoplanet Archive coordinates/TIC/Tmag metadata, and public
MAST CAOM observation metadata. MAST responses are stored as twelve immutable
JSON shards under `data/raw/sprint1_metadata/`, each with a receipt and SHA-256
hash. The query is restricted to the DRD TIC roster and SPOC/TESS-SPOC
provenance rows. It does not call the MAST product-download service.

## Time and availability conventions

The common metadata cutoff is the earliest shard receipt,
`2026-11-06T12:19:25.987078+00:00` (the latest shard was received at
`2026-11-06T12:21:46.594258+00:00`), rather than the end of the calendar day.
`t_max`, `t_obs_release`, and `dataRights` are therefore evaluated at that
explicit cutoff. The official calendar is date-only and is retained as such.
One full UTC day is removed from both calendar boundaries before counting an
opportunity; no UTC-to-BJD_TDB conversion is claimed. MAST `t_min`/`t_max`
remain MJD metadata and are intersected numerically with that conservative
calendar interior. This is a boundary margin, not an exact transit-window
conversion.

The primary strict-A anchor is 2025-11-19 UTC (the first whole day after the
DRD OSF node's recorded `made_public` transition at
`2025-11-18T09:43:24.090310Z`; source bytes are cached at
`data/raw/sprint1_osf_logs/wpjtn_made_public.json`). The journal-publication
sensitivity starts 2026-02-12 UTC.
Both counts are emitted. If the OSF source-log evidence changes, rerun with
`--strict-a-start YYYY-MM-DD`; the cache and output receipts preserve the
chosen value.

MAST product labels are assigned only when both provenance and exposure time
match the requested cadence: `SPOC_120` (SPOC, 120 s) and `TESS-SPOC_200`
(TESS-SPOC, 200 s). The sealed-era roster currently contains 424 public,
observed `SPOC_120` rows and no `TESS-SPOC_200` rows in sectors S98--S110. The
immutable query cache does contain 1,132 `TESS-SPOC_200` rows overall, but
they are confined to sectors S56--S85 and S1751, with MAST metadata limits
spanning MJD 59824.7500--61062.4866; none is a sealed-era product. A further
420 SPOC 20-s rows are retained as `SPOC_20` non-target cadence evidence. No
inference is made that absent sealed-era TESS-SPOC rows imply absent
photometry: the target-roster query returned no matching 200-s metadata row
for those sectors at the common cutoff.

## Cohort and counts

The DRD catalogue has 620 planets on 584 hosts. Coordinates/TIC metadata are
matched for 619 planet rows (583 unique TICs); one planet row remains
unmatched. MAST metadata matched 577 of those unique TICs, leaving six TICs
without a returned row in the restricted public query. The core rule is one
DRD planet per host, Tmag < 13.5, and P <= 12 d. The extension is the union of
P > 12 d and hosts with multiple DRD planets, with no duplicate planet count.
The 42 origin-known DRD TTV flags in `data/fixtures/exoclock_ttv_flags.csv`
are excluded from the primary counts; pre-flag values are retained as a
sensitivity.

| strict-A basis | core planets | extension planets | union | extension/core | extension/union | product rows | all eligible opportunities | qualified-union opportunities |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| OSF-public anchor, origin flags excluded | 156 | 28 | 184 | 17.95% | 15.22% | 393 | 3,533 | 3,399 |
| same anchor, flags retained (sensitivity) | 159 | 40 | 199 | 25.16% | 20.10% | 415 | 3,695 | 3,399 |
| journal anchor 2026-02-12, flags excluded | 127 | 25 | 152 | 19.69% | 16.45% | 298 | 2,664 | 2,609 |
| journal anchor 2026-02-12, flags retained (sensitivity) | 128 | 28 | 156 | 21.88% | 17.95% | 305 | 2,741 | 2,609 |

The R8 interpretation is the revised plan's OR rule: the extension clears the
15% metadata-eligible-planet gate under both denominators shown here. This is
not a scored-sample claim and does not estimate a standard error; Sprint 1
precision simulations must use the qualified-union opportunities in the last
column. The difference between all eligible and qualified-union opportunities
is unresolved metadata cohort material: four planets contribute 134 strict-A
opportunities (55 journal-anchor opportunities). They remain in the CSV and
all-eligible totals but are not silently assigned to core or extension.

Counts are opportunities predicted by the DRD ephemeris inside conservative
metadata windows. They are not measured successes, usable complete transits,
timed outcomes, or an estimate of recovery. Cadence gaps, quality selection,
full-transit capture, target identification, and physical single-planet status
remain unresolved. The product table preserves one row per planet-sector-
product evidence record and includes TIC, host, Tmag, period, schedule dates,
MJD product limits, release date, product URI, predicted camera/CCD where
`tess-point` supplies it, availability evidence, and the covariance-independent
inclusion basis.

## Reproduction

```bash
uv run --locked python scripts/sprint1_inventory.py --acquire
uv run --locked python scripts/sprint1_inventory.py
uv run --locked python -m unittest tests.test_sprint1_inventory -v
```

`--acquire` is only needed when a cache shard is absent. Existing shards are
immutable: changed bytes, changed TIC rosters, incomplete MAST paging, or a
receipt hash mismatch stop the run. The generated files are:

- `results/sprint1/inventory/planet_sector_product_inventory.csv`
- `results/sprint1/inventory/inventory_summary.json`
- `results/sprint1/inventory/inventory_manifest.json`

The archived HEASARC schedule audit remains the exact source for calendar
windows. It records S98's extended duration, the S99 interruption, S100's
boundary straddle, and S110's in-progress status; calendar status does not
prove target-level product availability.
