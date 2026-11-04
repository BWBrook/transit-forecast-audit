# T015 provenance and access-guard review

**Codex, 5 November 2026. Read-only audit of the existing development
artifacts.** No network request or new light-curve acquisition was made. The
five FITS products named in `results/t015/t015_products.csv` were checked in
place; their exact hashes and time headers are retained in
`results/t015_review/provenance_check.json`.

## Findings

All five named files hash exactly to the existing T015 product receipt. Their
headers state `TIMESYS=TDB`, `TIMEREF=SOLARSYSTEM`, `TIMEUNIT=d`,
`BJDREFI=2457000`, and `BJDREFF=0.0`. The latest product TSTOP is BTJD
2853.143281567599, and all five products are from 2022 in their source
identities. These are barycentric TDB coordinates; no spacecraft UTC
observation instant is inferred from them. None approaches the protected
post-2025-11-18 interval or the development-era boundary.

The pipeline sets `MAX_BTJD = 3313.5` in
`scripts/t015_timing_pipeline.py:43`. With the stated BTJD/TDB convention this
is 2024-01-04 00:00:00 TDB. The comment says 2024-01-03 00:00 UTC, so the
numeric boundary and its comment disagree by about one day. A TDB-to-UTC-scale
conversion of a barycentric timestamp does not establish the spacecraft UTC
instant or undo target/observer light-time correction; no valid replacement
BTJD cutoff is asserted here. A corrected guard needs target and observer
metadata or a conservative boundary exclusion. The discrepancy did not affect
the five existing 2022 products.

The source-level access ordering is weaker than the pipeline documentation
states. `fetch()` restricts the MAST search to sectors S46--S73, then calls
`res[i].download()` (`scripts/t015_timing_pipeline.py:53-69`). `clean()` checks
the FITS TSTOP before the pipeline explicitly accesses `lc.time` and flux
columns (`scripts/t015_timing_pipeline.py:72-90`). However, Lightkurve 2.5.1's
`SearchResult._download_one()` returns `read(path, ...)` after download/cache
resolution (`lightkurve/search.py:336-360`), and its TESS reader calls
`read_generic_lightcurve()` (`lightkurve/io/tess.py:33-51`). That reader runs
`fits.open()` and `Table.read(hdulist[ext], format="fits")`
(`lightkurve/io/generic.py:42-55`) before returning the LightCurve. Thus the
TSTOP guard is post-download and post-table-read; the effective pre-request
boundary in this run is the sector restriction, not the TSTOP check.

The evidence supports saying that the five observed products were all within
the intended development era and that no protected product was requested. It
does not support saying that the TSTOP guard refuses a file before Lightkurve
reads its flux table.

Reproduce the header/hash-only audit (no network and exactly the five named
existing inputs):

```bash
uv run --offline --extra analysis python scripts/review_t015_provenance.py
```

Reproducible receipt: `results/t015_review/provenance_check.json`.
