"""Acquire pinned ExoClock release files from OSF with provenance.

Each artifact is identified by OSF node and file GUID/path. The script records
OSF file metadata (creation, modification, version list) alongside the SHA-256
of the downloaded bytes, so a later reader can tell whether the bytes they hold
are the version-1 upload that existed before journal publication.

Raw bytes go under data/raw/osf/ (gitignored). The manifest is written to the
path given by --manifest and is meant to be committed.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ARTIFACTS = [
    ("DRB", "wna5e", "/61794003f14f840031dfb9f4", "updated_ephemerides.txt"),
    ("DRB", "wna5e", "/6179eeb1378953005ea774f8", "4_updated_ecc.txt"),
    ("DRB", "wna5e", "/6179ef8151fbdd004e1420e7", "5_complete_ExoClock_DRB.zip"),
    ("DRC", "p298n", "/633315dc0db48e0023e10f00", "catalogue_of_ephemerides.txt"),
    ("DRC", "p298n", "/6333161131d65300312dc92d", "all_mid_time_data.txt"),
    ("DRD", "wpjtn", "/691baed85f334aadee770a79", "catalogue_of_ephemerides.txt"),
    ("DRD", "wpjtn", "/691baf18c330e7f384957ef8", "all_mid_time_data.txt"),
    ("DRD", "wpjtn", "/691baf0f2f50931303e64e2e", "by_source.zip"),
]

FIELDS = [
    "source_id", "release", "osf_node", "osf_path", "osf_name", "doi",
    "osf_date_created", "osf_date_modified", "osf_current_version",
    "osf_version_count", "osf_v1_created", "download_url", "local_path",
    "sha256", "size_bytes", "retrieved_at_utc", "licence",
]

DOIS = {"wna5e": "10.17605/OSF.IO/WNA5E", "p298n": "10.17605/OSF.IO/P298N",
        "wpjtn": "10.17605/OSF.IO/WPJTN"}


def get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "transit-forecast-audit"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.load(r)


def node_licence(node: str) -> str:
    d = get_json(f"https://api.osf.io/v2/nodes/{node}/?embed=license")["data"]
    return d["embeds"]["license"]["data"]["attributes"]["name"]


def acquire(root: Path, release: str, node: str, path: str, name: str, licence: str) -> dict:
    meta = get_json(f"https://api.osf.io/v2/files{path}/")["data"]
    a = meta["attributes"]
    if a["name"] != name:
        raise SystemExit(f"OSF name mismatch for {path}: {a['name']} != {name}")
    versions = get_json(meta["relationships"]["versions"]["links"]["related"]["href"])["data"]
    v1 = min(versions, key=lambda v: int(v["id"]))
    dest = root / "data" / "raw" / "osf" / node / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    url = meta["links"]["download"]
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if dest.exists():
        data = dest.read_bytes()
        retrieved = "previously_retrieved"
    else:
        req = urllib.request.Request(url, headers={"User-Agent": "transit-forecast-audit"})
        with urllib.request.urlopen(req, timeout=600) as r:
            data = r.read()
        dest.write_bytes(data)
        dest.chmod(0o444)
    if a.get("size") is not None and len(data) != a["size"]:
        raise SystemExit(f"size mismatch for {name}: {len(data)} != {a['size']}")
    return {
        "source_id": f"osf_{node}_{name}",
        "release": release, "osf_node": node, "osf_path": path, "osf_name": name,
        "doi": DOIS[node],
        "osf_date_created": a["date_created"], "osf_date_modified": a["date_modified"],
        "osf_current_version": a["current_version"], "osf_version_count": len(versions),
        "osf_v1_created": v1["attributes"]["date_created"],
        "download_url": url, "local_path": str(dest.relative_to(root)),
        "sha256": hashlib.sha256(data).hexdigest(), "size_bytes": len(data),
        "retrieved_at_utc": retrieved, "licence": licence,
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", default=".")
    p.add_argument("--manifest", required=True)
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    manifest = Path(args.manifest)
    previous = {}
    if manifest.exists():
        with manifest.open() as f:
            previous = {r["source_id"]: r for r in csv.DictReader(f)}
    licences = {n: node_licence(n) for n in {a[1] for a in ARTIFACTS}}
    rows = []
    for release, node, path, name in ARTIFACTS:
        row = acquire(root, release, node, path, name, licences[node])
        old = previous.get(row["source_id"])
        if old:
            if old["sha256"] != row["sha256"]:
                raise SystemExit(f"hash changed for {row['source_id']}")
            row["retrieved_at_utc"] = old["retrieved_at_utc"]
        rows.append(row)
        print(row["source_id"], row["sha256"][:12], row["size_bytes"], file=sys.stderr)
    manifest.parent.mkdir(parents=True, exist_ok=True)
    with manifest.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
