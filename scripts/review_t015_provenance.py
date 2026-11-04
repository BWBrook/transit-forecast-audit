#!/usr/bin/env python3
"""Verify the five existing T015 FITS receipts and time headers locally.

This is deliberately a header/hash-only audit. It reads no MAST search result,
does not download anything, and refuses any input set other than the five
products already named by ``results/t015/t015_products.csv``.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

from astropy.io import fits

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = ROOT / "results/t015/t015_products.csv"
DEFAULT_OUTPUT = ROOT / "results/t015_review/provenance_check.json"
EXPECTED_COUNT = 5
EXPECTED_MANIFEST_SHA256 = "9584f2fe40e8ffb760879e8849a4b5056f0ecd5a11fdc68bd58d358d49b7eef2"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def audit() -> dict:
    if sha256(PRODUCTS) != EXPECTED_MANIFEST_SHA256:
        raise ValueError("This audit is restricted to the original five-product manifest")
    rows = list(csv.DictReader(PRODUCTS.open(newline="", encoding="utf-8")))
    if len(rows) != EXPECTED_COUNT:
        raise ValueError(f"expected exactly {EXPECTED_COUNT} named products, found {len(rows)}")
    products = []
    for row in rows:
        path = ROOT / row["local_path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        observed = sha256(path)
        if observed != row["sha256"]:
            raise ValueError(f"hash mismatch: {path}")
        with fits.open(path, memmap=False) as hdul:
            primary, table = hdul[0].header, hdul[1].header
            keys = ("TIMESYS", "TIMEREF", "TIMEUNIT", "BJDREFI", "BJDREFF", "TSTART", "TSTOP")
            headers = {key: table.get(key, primary.get(key)) for key in keys}
        if headers["TIMESYS"] != "TDB" or headers["BJDREFI"] != 2457000:
            raise ValueError(f"unexpected time convention: {path}")
        products.append({
            "planet": row["planet"],
            "sector": int(row["sector"]),
            "local_path": row["local_path"],
            "expected_sha256": row["sha256"],
            "observed_sha256": observed,
            "hash_match": True,
            "time_headers": headers,
        })
    return {
        "development_only": True,
        "network_access": False,
        "source": str(PRODUCTS.relative_to(ROOT)),
        "manifest_sha256":EXPECTED_MANIFEST_SHA256,
        "pipeline_sha256":sha256(ROOT/"scripts/t015_timing_pipeline.py"),
        "command":"python scripts/review_t015_provenance.py",
        "files_checked": len(products),
        "hashes_all_match": True,
        "boundary": {
            "pipeline_constant": "MAX_BTJD = 3313.5",
            "pipeline_source": "scripts/t015_timing_pipeline.py:43",
            "constant_scale": "BTJD = JD - 2457000; SPOC TIMESYS=TDB",
            "constant_tdb_calendar": "2024-01-04 00:00:00 TDB",
            "commented_intent": "2024-01-03 00:00 UTC",
            "interpretation": "Calendar labels disagree by about one day. No replacement BTJD cutoff is asserted because barycentric TDB to UTC-scale conversion does not establish spacecraft UTC or undo target/observer light-time correction.",
        },
        "products": products,
        "guard_order": {
            "pipeline_fetch": "scripts/t015_timing_pipeline.py:53-69; sector search is restricted to S46-S73, then res[i].download() is called",
            "pipeline_check": "scripts/t015_timing_pipeline.py:72-90; TSTOP is checked before the pipeline explicitly accesses LightCurve columns",
            "lightkurve_download": "lightkurve/search.py:_download_one:336-360; returns read(path, ...) after download/cache resolution",
            "lightkurve_tess_reader": "lightkurve/io/tess.py:33-51; calls read_generic_lightcurve",
            "lightkurve_table_read": "lightkurve/io/generic.py:42-55; Table.read loads the light-curve table before clean()",
        },
        "script_sha256": sha256(Path(__file__).resolve()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", default=str(DEFAULT_OUTPUT))
    args = parser.parse_args()
    report = audit()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"files_checked": report["files_checked"], "hashes_all_match": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
