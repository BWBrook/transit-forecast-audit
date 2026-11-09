"""Acquire current NASA Archive TTV metadata for the frozen 184-planet roster.

Run with --acquire once, then without it to reproduce labels from saved bytes.
This script reads metadata only, never timings, scores or host rankings.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/final_secondaries/ttv"
ROSTER = ROOT / "results/sprint2/freeze_candidate/roster.csv"
CACHED_NAMES = ROOT / "data/raw/exoplanet_archive/pscomppars.csv"
ORIGIN_FLAGS = ROOT / "data/fixtures/exoclock_ttv_flags.csv"
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
ALIAS = "https://exoplanetarchive.ipac.caltech.edu/cgi-bin/Lookup/nph-aliaslookup.py"
SCHEMA_QUERY = (
    "select table_name,column_name,datatype,description from TAP_SCHEMA.columns "
    "where table_name in ('ps','pscomppars') and column_name in "
    "('pl_name','hostname','ttv_flag','pl_ttvflag','default_flag','rowupdate',"
    "'pl_pubdate','releasedate','pl_refname','pl_tranmid_reflink')"
)
PS_COLUMNS = ("pl_name", "hostname", "ttv_flag", "rowupdate", "pl_pubdate", "releasedate", "pl_refname")
DOCS = {
    "columns": "https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html",
    "tap": "https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html",
    "aliases": "https://exoplanetarchive.ipac.caltech.edu/docs/sysaliases.html",
    "acknowledgement": "https://exoplanetarchive.ipac.caltech.edu/docs/acknowledge.html",
    "doi": "https://exoplanetarchive.ipac.caltech.edu/docs/doi.html",
}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")


def read_csv(path):
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def compact(name):
    return "".join(name.split())


def saved_json(stem, url, acquire, query=None):
    path, receipt_path = OUT / f"{stem}.json", OUT / f"{stem}.request.json"
    if path.exists():
        receipt = json.loads(receipt_path.read_text())
        if receipt["url"] != url or receipt.get("sha256") != sha(path):
            raise ValueError(f"Saved source or request mismatch: {stem}")
        return json.loads(path.read_bytes()), receipt
    if not acquire:
        raise ValueError(f"Missing saved metadata: {path}; use --acquire to retrieve")
    with urllib.request.urlopen(url, timeout=60) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("Metadata response unexpectedly exceeds 1 MB")
    parsed = json.loads(raw)
    path.write_bytes(raw)
    receipt = {"url": url, "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
               "sha256": sha(path), "bytes": len(raw)}
    if query is not None:
        receipt["query"] = query
    write_json(receipt_path, receipt)
    return parsed, receipt


def resolve_names(targets, acquire):
    by_name = defaultdict(list)
    for row in read_csv(CACHED_NAMES):
        by_name[compact(row["pl_name"])].append(row["pl_name"])
    mapping = {}
    for target in targets:
        planet = target["planet"]
        names = sorted(set(by_name[compact(planet)]))
        if len(names) == 1:
            mapping[planet] = (names[0], "cached_name_whitespace_only", "")
            continue
        if names:
            mapping[planet] = ("", "ambiguous_cached_name", "")
            continue
        stem = f"alias_{planet}"
        url = ALIAS + "?" + urllib.parse.urlencode({"objname": planet})
        aliases, _ = saved_json(stem, url, acquire)
        hits = []
        if aliases.get("manifest", {}).get("lookup_status") == "OK":
            objects = aliases.get("system", {}).get("objects", {}).get("planet_set", {}).get("planets", {})
            for obj in objects.values():
                alias_set = obj.get("alias_set", {})
                if compact(planet) in {compact(n) for n in alias_set.get("aliases", [])}:
                    hits.append(alias_set["default_name"])
        names = sorted(set(hits))
        mapping[planet] = (names[0] if len(names) == 1 else "",
                           "official_planet_alias" if len(names) == 1 else "alias_unknown_or_ambiguous",
                           str((OUT / f"{stem}.json").relative_to(ROOT)))
    resolved = [value[0] for value in mapping.values() if value[0]]
    if len(resolved) != len(set(resolved)):
        raise ValueError("Two frozen planets mapped to one archive planet")
    return mapping


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true")
    args = parser.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    targets = sorted(read_csv(ROSTER), key=lambda r: r["planet"])
    if len(targets) != 184 or len({r["planet"] for r in targets}) != 184:
        raise ValueError("Expected exactly the frozen 184 unique target planets")
    schema_url = TAP + "?" + urllib.parse.urlencode({"query": SCHEMA_QUERY, "format": "json"})
    schema, _ = saved_json("schema", schema_url, args.acquire, SCHEMA_QUERY)
    fields = {(r["table_name"], r["column_name"]) for r in schema}
    if not all(("ps", key) in fields for key in (*PS_COLUMNS, "default_flag")):
        raise ValueError("Live/saved PS schema does not support the declared query")
    mapping = resolve_names(targets, args.acquire)
    names = sorted({v[0] for v in mapping.values() if v[0]})
    literals = ",".join("'" + name.replace("'", "''") + "'" for name in names)
    query = f"select {','.join(PS_COLUMNS)} from ps where default_flag=1 and pl_name in ({literals}) order by pl_name"
    url = TAP + "?" + urllib.parse.urlencode({"query": query, "format": "json"})
    raw, receipt = saved_json("ps_default_ttv", url, args.acquire, query)
    rows = {}
    for row in raw:
        if set(row) != set(PS_COLUMNS) or row["pl_name"] not in names or row["pl_name"] in rows:
            raise ValueError("Unexpected or duplicate archive default row")
        if row["ttv_flag"] not in (None, 0, 1):
            raise ValueError("Unknown archive TTV flag encoding")
        rows[row["pl_name"]] = row
    origin = {r["planet"] for r in read_csv(ORIGIN_FLAGS) if r["flag_release"] == "DRD"}
    labels = []
    for target in targets:
        planet = target["planet"]
        name, method, alias_path = mapping[planet]
        row = rows.get(name, {})
        flag = row.get("ttv_flag")
        label = "current_archive_flagged" if flag == 1 else (
            "current_archive_unflagged_physical_status_unknown" if flag == 0 else "unknown")
        labels.append({"planet": planet, "host": target["host"], "cohort": target["cohort"],
                       "origin_drd_ttv_flag": planet in origin, "archive_pl_name": name,
                       "match_method": method, "match_source_alias": alias_path,
                       "archive_row_present": bool(row), "archive_ttv_flag": "" if flag is None else flag,
                       "current_catalogue_ttv_label": label,
                       "physical_ttv_status": "positive_archive_flag" if flag == 1 else "unknown",
                       "archive_rowupdate": row.get("rowupdate") or "",
                       "archive_parameter_publication_date": row.get("pl_pubdate") or "",
                       "archive_parameter_release_date": row.get("releasedate") or "",
                       "archive_parameter_reference": row.get("pl_refname") or "",
                       "ttv_discovery_date": "unknown", "new_since_origin": "unknown",
                       "retrieved_at_utc": receipt["retrieved_at_utc"],
                       "source_response_sha256": receipt["sha256"]})
    dest = OUT / "labels.csv"
    with dest.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(labels[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(labels)
    provenance = {
        "label": "Current catalogue flag retrieved after unblinding; descriptive only",
        "retrieval_date_hobart": datetime.fromisoformat(receipt["retrieved_at_utc"]).astimezone(ZoneInfo("Australia/Hobart")).date().isoformat(),
        "source": "NASA Exoplanet Archive Planetary Systems table, current default rows",
        "source_dataset_doi": "10.26133/NEA12", "documentation": DOCS,
        "licence": "No explicit dataset licence established from the inspected archive documentation; do not infer CC BY-SA from this repository",
        "limits": ["Flag 0 is an unflagged catalogue row, not proof of no TTV", "The flag concerns variations attributed to another planet and is not a complete timing-anomaly classification", "Parameter dates/reference describe the current default parameter set, not TTV discovery or first-public dates", "No current label establishes that TTV knowledge arose after the DRD origin", "Aliases were matched at planet level; host-only matching is forbidden", "No outcome, score, ranking or photometry was read"],
        "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (ROSTER, CACHED_NAMES, ORIGIN_FLAGS)},
        "script_sha256": sha(Path(__file__)), "source_note_sha256": sha(OUT / "SOURCE_NOTE.md"),
        "target_planets": len(targets),
        "archive_rows": len(rows), "label_counts": dict(Counter(r["current_catalogue_ttv_label"] for r in labels)),
        "match_counts": dict(Counter(r["match_method"] for r in labels)),
        "files_sha256": {p.name: sha(p) for p in sorted(OUT.glob("*.json")) if p.name != "provenance.json"},
        "labels_sha256": sha(dest), "reproduce": ".venv/bin/python scripts/final_ttv_labels.py",
        "acquire": ".venv/bin/python scripts/final_ttv_labels.py --acquire",
    }
    write_json(OUT / "provenance.json", provenance)
    print(json.dumps({k: provenance[k] for k in ("target_planets", "archive_rows", "label_counts", "match_counts")}, indent=2))


if __name__ == "__main__":
    main()
