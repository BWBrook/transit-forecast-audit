"""Uniform outcome-blind source-candidate screen from hash-bound archive caches.

    .venv/bin/python scripts/t019_external_metadata.py

Two public TAP attempts returned HTTP522. The saved complete names/hosts table
and 184 default parameter rows still supply a uniform, reproducible candidate
screen. Metadata dates are curation leads, not certified historical knowledge.
"""

import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/information_ledger/external_metadata"
TARGETS = ROOT / "results/final_secondaries/ttv/ps_default_ttv.json"
LABELS = ROOT / "results/final_secondaries/ttv/labels.csv"
NAMES = ROOT / "data/raw/exoplanet_archive/pscomppars.csv"
NAMES_RECEIPT = ROOT / "results/sealed_inventory/sealed_inventory_summary.json"
ORIGINS = {"DRB": "2021-10-27", "DRC": "2022-09-27", "DRD": "2025-11-18"}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def date_candidate(value, origin):
    if not value or not re.fullmatch(r"\d{4}(?:-\d{2})?(?:-\d{2})?", str(value)):
        return "unknown"
    parts = [int(p) for p in str(value).split("-")]
    if len(parts) == 1:
        first, after = date(parts[0], 1, 1), date(parts[0] + 1, 1, 1)
    elif len(parts) == 2:
        first = date(*parts, 1)
        after = date(parts[0] + (parts[1] == 12), parts[1] % 12 + 1, 1)
    else:
        return "metadata_pre_origin_source_unverified" if date(*parts) < date.fromisoformat(origin) else "metadata_on_or_after_origin"
    cut = date.fromisoformat(origin)
    if after <= cut:
        return "metadata_pre_origin_source_unverified"
    if first >= cut:
        return "metadata_on_or_after_origin"
    return "boundary_or_unknown"


def write_csv(path, rows):
    with path.open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader(); writer.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    targets = json.loads(TARGETS.read_text())
    labels = list(csv.DictReader(LABELS.open()))
    names = list(csv.DictReader(NAMES.open()))
    by_host = defaultdict(list)
    by_name = {}
    for row in names:
        by_host[row["hostname"]].append(row)
        if row["pl_name"] in by_name:
            raise ValueError("Duplicate cached archive planet")
        by_name[row["pl_name"]] = row
    default_rows = {row["pl_name"]: row for row in targets}
    hostnames = {row["hostname"] for row in targets}
    input_receipt = json.loads(NAMES_RECEIPT.read_text())
    candidates = []
    def walk(value):
        if isinstance(value, dict):
            if value.get("file") == str(NAMES.relative_to(ROOT)):
                candidates.append(value)
            for v in value.values(): walk(v)
        elif isinstance(value, list):
            for v in value: walk(v)
    walk(input_receipt)
    if len(candidates) != 1 or candidates[0]["sha256"] != sha(NAMES):
        raise ValueError("Name-cache hash does not match original receipt")
    target_rows, companion_rows, origin_rows = [], [], []
    for label in labels:
        name = label["archive_pl_name"]
        target = default_rows[name]
        if name not in by_name or by_name[name]["hostname"] != target["hostname"]:
            raise ValueError("Target identity/host mismatch in saved source tables")
        companions = [r for r in by_host[target["hostname"]] if r["pl_name"] != name]
        target_rows.append({"planet": label["planet"], "archive_pl_name": name,
                            "archive_host": target["hostname"],
                            "cached_confirmed_planets_same_host": len(by_host[target["hostname"]]),
                            "current_companion_candidates": len(companions),
                            "current_parameter_publication_date": target["pl_pubdate"],
                            "current_parameter_reference": target["pl_refname"],
                            "current_parameter_archive_release_date": target["releasedate"],
                            "current_ttv_flag": target["ttv_flag"], "ttv_source_date": None,
                            "ttv_source_status": "flag_not_source_specific; discovery_timing_unknown",
                            "discovery_reference_status": "not_in_saved_name_or_default_row_query",
                            "screen_status": "uniform_cached_archive_screen_complete; historical_source_curation_pending"})
        for companion in companions:
            cached_default = default_rows.get(companion["pl_name"], {})
            base = {"planet": label["planet"], "target_archive_name": name,
                    "archive_host": target["hostname"], "companion_archive_name": companion["pl_name"],
                    "companion_current_parameter_publication_date": cached_default.get("pl_pubdate"),
                    "companion_current_parameter_reference": cached_default.get("pl_refname"),
                    "discovery_year": None, "discovery_publication_date": None, "discovery_reference": None,
                    "missingness": "complete cached names/hosts query; companion parameter reference only if also in frozen-target default-row query"}
            companion_rows.append(base)
            for release, origin in ORIGINS.items():
                origin_rows.append({"release": release, "origin_utc_calendar_date": origin, **base,
                                    "companion_parameter_date_candidate_state": date_candidate(cached_default.get("pl_pubdate"), origin),
                                    "historical_identity_availability_verified": False,
                                    "eligible_historical_companion_predictor": False,
                                    "next_source_check": "obtain discovery reference/first-public date and period source; parameter publication does not establish discovery or TTV date"})
    write_csv(OUT / "targets.csv", target_rows)
    write_csv(OUT / "companion_candidates.csv", companion_rows)
    write_csv(OUT / "origin_candidate_dates.csv", origin_rows)
    summary = {"targets": len(target_rows), "frozen_hosts": len(hostnames),
               "cached_planets_on_frozen_hosts": sum(len(by_host[h]) for h in hostnames),
               "targets_with_current_companion_candidates": sum(r["current_companion_candidates"] > 0 for r in target_rows),
               "directed_target_companion_pairs": len(companion_rows),
               "companion_parameter_date_candidate_states": dict(Counter(r["companion_parameter_date_candidate_state"] for r in origin_rows)),
               "target_current_ttv_flags": sum(r["current_ttv_flag"] == 1 for r in target_rows),
               "historically_verified_companion_inventories": 0, "missing_target_matches": 0,
               "name_cache_recorded_retrieval_utc": candidates[0]["retrieved_utc"],
               "name_cache_retrieval_time_limit": "original acquisition script recorded file modification time; not immutable source-availability evidence",
               "method": "same saved complete name/host table screened for all 175 hosts, independent of outcomes; source dates are leads only",
               "ttv_limit": "Default parameter reference does not date the TTV flag; no physical negatives inferred.",
               "failed_public_route": "NASA TAP HTTP522 for 175-host query and 35-host first batch; no response data; retry after source becomes reachable"}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    prov = {"script_sha256": sha(Path(__file__)),
            "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (TARGETS, LABELS, NAMES, NAMES_RECEIPT)},
            "output_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (OUT / "targets.csv", OUT / "companion_candidates.csv", OUT / "origin_candidate_dates.csv", OUT / "summary.json")},
            "source_documentation": "https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html",
            "source_doi": "10.26133/NEA12", "licence": "not established; do not impute repository licence",
            "no_photometry_or_headers_requested": True, "network_requests_in_offline_rebuild": 0}
    columns = ("pl_name,hostname,pl_orbper,pl_trandur,disc_year,disc_pubdate,disc_refname,"
               "pl_refname,pl_pubdate,releasedate,rowupdate,ttv_flag,sy_pnum")
    prov["failed_live_requests"] = []
    for count, timeout in ((175, 60), (35, 45)):
        quoted = ",".join("'" + n.replace("'", "''") + "'" for n in sorted(hostnames)[:count])
        query = f"select {columns} from ps where default_flag=1 and hostname in ({quoted}) order by hostname,pl_name"
        prov["failed_live_requests"].append({"endpoint": "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
                                              "method": "GET", "format": "json", "query": query,
                                              "timeout_seconds": timeout, "http_status": 522,
                                              "attempt_date_utc": "2026-11-09", "exact_clock_time": "not retained",
                                              "response_data_retrieved": False})
    (OUT / "provenance.json").write_text(json.dumps(prov, indent=2) + "\n")
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
