#!/usr/bin/env python3
"""Build a provenance-preserving metadata tranche for the DRC origin cohort.

This reads the frozen DRC release text files and uses only explicit TESS record
IDs from the already acquired DRD outcome index to identify the 316-planet
origin-only cohort. No outcome timing or uncertainty values from DRD are parsed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRC_MID = ROOT / "data/raw/osf/p298n/all_mid_time_data.txt"
DRC_EPH = ROOT / "data/raw/osf/p298n/catalogue_of_ephemerides.txt"
DRD_INDEX = ROOT / "data/raw/osf/wpjtn/all_mid_time_data.txt"
FLAGS = ROOT / "data/fixtures/exoclock_ttv_flags.csv"
OUT = ROOT / "results/pilot_v1/tranche2_review"
MANIFEST = ROOT / "results/pilot_v1/source_manifest.csv"

DATE_RE = re.compile(r"(?<!\d)(20\d{2}-\d{2}-\d{2})(?!\d)")
DEV_START = date(2022, 1, 1)
DEV_END = date(2024, 1, 3)
SOURCES = ("etd", "exoclock", "literature", "space")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def verify_manifest() -> list[dict[str, str]]:
    """Verify source bytes before parsing or creating any output directory."""
    with MANIFEST.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    relevant = [r for r in rows if r["release"] in {"DRC", "DRD"}]
    if len(relevant) != 5:
        raise ValueError(f"expected five DRC/DRD manifest rows, found {len(relevant)}")
    for row in relevant:
        path = ROOT / row["local_path"]
        if not path.is_file():
            raise FileNotFoundError(path)
        observed = sha256(path)
        if observed != row["sha256"]:
            raise ValueError(f"source hash mismatch before parsing: {path}")
        row["sha256_observed"] = observed
        row["hash_match"] = "true"
    return relevant


def parse_drc_mid(path: Path) -> dict[str, list[dict[str, object]]]:
    rows: dict[str, list[dict[str, object]]] = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            if not raw.strip() or raw.startswith("Tmid") or raw.startswith("Planet"):
                continue
            fields = raw.rstrip("\n").split("\t")
            first = fields[0].split()
            if len(first) < 2 or len(fields) != 4:
                raise ValueError(f"unexpected DRC mid-time schema at line {line_no}")
            vals = [first[0], first[1], *(x.strip() for x in fields[1:])]
            planet, tmid, unc, source, record_id = vals
            if source not in SOURCES:
                raise ValueError(f"unknown DRC source value {source!r} at line {line_no}")
            if not math.isfinite(float(tmid)) or not math.isfinite(float(unc)) or float(unc) <= 0:
                raise ValueError(f"invalid DRC timing value at line {line_no}")
            if not record_id:
                raise ValueError(f"empty DRC record ID at line {line_no}")
            row = {
                "planet": planet,
                "tmid": float(tmid),
                "unc": float(unc),
                "source": source,
                "record_id": record_id,
                "raw": raw,
                "line_no": line_no,
            }
            rows[planet].append(row)
    return rows


def parse_drc_catalogue(path: Path) -> dict[str, dict[str, float]]:
    result: dict[str, dict[str, float]] = {}
    with path.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            if not raw.strip() or raw.startswith("Planet"):
                continue
            fields = [x.strip() for x in raw.rstrip("\n").split("\t")]
            if len(fields) != 5:
                raise ValueError(f"unexpected DRC catalogue schema at line {line_no}")
            planet, t0, t0_unc, period, period_unc = fields
            if planet in result:
                raise ValueError(f"duplicate DRC forecast planet {planet}")
            vals = {"t0": float(t0), "t0_unc": float(t0_unc),
                    "period": float(period), "period_unc": float(period_unc)}
            if (not all(math.isfinite(v) for v in vals.values()) or vals["t0_unc"] <= 0 or
                    vals["period"] <= 0 or vals["period_unc"] <= 0):
                raise ValueError(f"invalid DRC forecast values for {planet}")
            result[planet] = vals
    return result


def parse_tess_index(path: Path) -> dict[str, list[dict[str, object]]]:
    """Index explicit TESS IDs/dates only; deliberately ignores numeric outcomes."""
    result: dict[str, list[dict[str, object]]] = defaultdict(list)
    with path.open(encoding="utf-8") as f:
        for line_no, raw in enumerate(f, 1):
            if not raw.strip() or raw.startswith("Tmid") or raw.startswith("Planet"):
                continue
            fields = raw.rstrip("\n").split("\t")
            first = fields[0].split()
            if len(first) < 2 or len(fields) != 4:
                raise ValueError(f"unexpected DRD index schema at line {line_no}")
            planet = first[0]
            source = fields[2].strip()
            record_id = fields[3].strip()
            if source != "space" or not record_id.endswith("_TESS"):
                continue
            match = DATE_RE.search(record_id)
            if not match:
                continue
            event_date = date.fromisoformat(match.group(1))
            if DEV_START <= event_date <= DEV_END:
                result[planet].append({"record_id": record_id, "date": event_date.isoformat(),
                                       "line_no": line_no})
    return result


def load_drc_flags(path: Path) -> set[str]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = [r for r in csv.DictReader(f) if r["flag_release"] == "DRC"]
    planets = {r["planet"] for r in rows}
    if len(planets) != 19:
        raise ValueError(f"expected 19 DRC origin flags, found {len(planets)}")
    return planets


def one_planet(planet: str, rows: list[dict[str, object]], eph: dict[str, float],
               tess_index: dict[str, list[dict[str, object]]], flags: set[str]) -> dict[str, object]:
    tmids = [float(r["tmid"]) for r in rows]
    raw_lines = [str(r["raw"]) for r in rows]
    ids = [str(r["record_id"]) for r in rows]
    sources = [str(r["source"]) for r in rows]
    epochs_raw = [(t - eph["t0"]) / eph["period"] for t in tmids]
    epochs = [math.floor(x + 0.5) for x in epochs_raw]
    dates = [m.group(1) for rid in ids if (m := DATE_RE.search(rid))]
    exact_rows = Counter((str(r["tmid"]), str(r["unc"]), str(r["source"]), str(r["record_id"]))
                         for r in rows)
    source_counts = Counter(sources)
    tess_ids = [rid for rid in ids if rid.endswith("_TESS")]
    tess_membership = planet in tess_index
    out: dict[str, object] = {
        "planet": planet,
        "analysis_cohort_origin_only": tess_membership and planet not in flags,
        "post_2021_tess_metadata_present": tess_membership,
        "drc_ttv_flag_known_at_issue": planet in flags,
        "n_timing_rows": len(rows),
        "n_unique_record_ids": len(set(ids)),
        "n_duplicate_record_id_rows": len(ids) - len(set(ids)),
        "n_exact_duplicate_rows": sum(max(n - 1, 0) for n in exact_rows.values()),
        "n_unique_epochs": len(set(epochs)),
        "n_duplicate_epoch_rows": len(epochs) - len(set(epochs)),
        "max_abs_nearest_epoch_phase": max(abs(x - e) for x, e in zip(epochs_raw, epochs)),
        "n_unique_record_dates": len(set(dates)),
        "n_rows_with_parseable_record_date": len(dates),
        "n_tess_ids": len(tess_ids),
        "literature_only": not tess_ids and all(s == "literature" for s in sources),
        "training_first_observed_bjd_tdb": min(tmids),
        "training_last_observed_bjd_tdb": max(tmids),
        "training_span_days": max(tmids) - min(tmids),
        "raw_first_line_no": min(int(r["line_no"]) for r in rows),
        "raw_last_line_no": max(int(r["line_no"]) for r in rows),
        "raw_row_sha256": hashlib.sha256("".join(raw_lines).encode()).hexdigest(),
        "period_mismatch_status": "not_identifiable_from_single_issued_period",
    }
    for source in SOURCES:
        out[f"n_source_{source}"] = source_counts[source]
        out[f"frac_source_{source}"] = source_counts[source] / len(rows)
        source_ids = [str(r["record_id"]) for r in rows if str(r["source"]) == source]
        out[f"n_duplicate_record_id_rows_{source}"] = len(source_ids) - len(set(source_ids))
    return out


def main() -> None:
    manifest_rows = verify_manifest()
    OUT.mkdir(parents=True, exist_ok=True)
    mid_rows = parse_drc_mid(DRC_MID)
    eph = parse_drc_catalogue(DRC_EPH)
    tess_index = parse_tess_index(DRD_INDEX)
    flags = load_drc_flags(FLAGS)
    candidate = set(eph) & set(tess_index)
    cohort = candidate - flags
    if len(candidate) != 330 or len(cohort) != 316:
        raise AssertionError(f"unexpected cohort counts: candidate={len(candidate)}, cohort={len(cohort)}")

    features = [one_planet(p, mid_rows[p], eph[p], tess_index, flags)
                for p in sorted(eph)]
    fieldnames = list(features[0])
    with (OUT / "metadata_per_planet.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(features)

    source_info = {
        "drc_mid_times": {"path": str(DRC_MID.relative_to(ROOT)), "sha256": sha256(DRC_MID),
                          "role": "all DRC released timing rows, treated as the release's fitted-input collection for metadata; completeness of the fitted set is not independently verified"},
        "drc_catalogue": {"path": str(DRC_EPH.relative_to(ROOT)), "sha256": sha256(DRC_EPH),
                          "role": "issued DRC T0/P and marginal uncertainties"},
        "drd_tess_index": {"path": str(DRD_INDEX.relative_to(ROOT)), "sha256": sha256(DRD_INDEX),
                           "role": "metadata-only cohort membership index; IDs/dates/source parsed, Tmid and uncertainty ignored"},
        "drc_origin_flags": {"path": str(FLAGS.relative_to(ROOT)), "sha256": sha256(FLAGS),
                             "role": "19 DRC TTV flags, sourced in fixture from ExoClock III arXiv v1 Table tab:ttvs"},
    }
    source_counts = Counter(str(r["source"]) for rows in mid_rows.values() for r in rows)
    summary = {
        "status": "metadata tranche only; no regressions or outcome scores",
        "release": "DRC / ExoClock III",
        "release_readme_detail": {
            "all_mid_time_data_schema": ["Planet", "Tmid (BJD_TDB)", "Tmid unc.", "source", "ID"],
            "catalogue_schema": ["Planet", "T0 (BJD_TDB)", "T0 unc.", "P (days)", "P unc. (days)"],
            "source_values_observed": sorted(source_counts),
            "record_date_rule": "Dates are counted only when an explicit YYYY-MM-DD occurs in the record ID; no date is inferred from an ADS-style literature identifier.",
        },
        "cohort_rule": {
            "candidate": "DRC catalogue planets with at least one DRD metadata-only space record whose explicit ID ends _TESS and date is 2022-01-01 through 2024-01-03",
            "candidate_planets": len(candidate), "origin_flags_removed": len(candidate & flags),
            "origin_only_planets": len(cohort), "flagged_planets_in_drc_catalogue": len(flags & set(eph)),
            "flag_source": "data/fixtures/exoclock_ttv_flags.csv; article locator arXiv:2209.09673v1 Table tab:ttvs",
        },
        "date_semantics": "training_first/last_observed_bjd_tdb are dates in the DRC release; they do not establish first-public availability of each observation",
        "availability": {
            "drc_training_end_anchor": "2021-12-31",
            "drc_issue_anchors": {"osf_upload": "2022-09-27", "arxiv_v1": "2022-09-20", "journal": "2023-02-14"},
            "event_level_first_public_dates": "unresolved",
        },
        "historical_multiplicity": "unavailable from these release tables; n_unique_epochs/dates describe rows in the released DRC input, not independent exposures",
        "input_row_diagnostics": {
            "drc_planets": len(eph), "drc_timing_rows": sum(len(v) for v in mid_rows.values()),
            "source_counts": dict(sorted(source_counts.items())),
            "duplicate_record_id_rows": sum(int(x["n_duplicate_record_id_rows"]) for x in features),
            "exact_duplicate_rows": sum(int(x["n_exact_duplicate_rows"]) for x in features),
            "max_abs_nearest_epoch_phase": max(float(x["max_abs_nearest_epoch_phase"]) for x in features),
            "period_mismatch": "No independent period is supplied. The nearest-epoch phase residual is descriptive only and is not a cycle-validation test.",
            "duplicate_record_id_rows_by_source": {
                source: sum(int(x[f"n_duplicate_record_id_rows_{source}"]) for x in features)
                for source in SOURCES
            },
        },
        "source_provenance": source_info,
        "manifest_gate": {
            "path": str(MANIFEST.relative_to(ROOT)),
            "verified_before_parsing": True,
            "rows": [{"source_id": r["source_id"], "sha256": r["sha256"],
                      "sha256_observed": r["sha256_observed"], "hash_match": r["hash_match"]}
                     for r in manifest_rows],
        },
        "no_protected_outcomes_opened": True,
        "no_tess_light_curves_opened": True,
        "output_schema": "metadata_per_planet.csv; raw line ranges and per-planet raw-row SHA-256 retain traceability",
    }
    script_hash = sha256(Path(__file__))
    summary["run_provenance"] = {
        "command": "python3 scripts/review_tranche2_metadata.py",
        "script_sha256": script_hash,
        "source_commit": __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    }
    (OUT / "metadata_summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"drc_planets": len(eph), "candidate": len(candidate), "origin_only": len(cohort),
                      "rows": sum(len(v) for v in mid_rows.values())}, indent=2))


if __name__ == "__main__":
    main()
