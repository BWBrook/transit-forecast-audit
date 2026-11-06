"""Build the Sprint 1 sealed-era metadata inventory.

This module uses catalogue, schedule, and MAST observation metadata only. It
never requests a FITS file, a target-pixel file, a light curve, or a flux
table. MAST responses are cached as immutable JSON shards under
``data/raw/sprint1_metadata``; rerunning without ``--acquire`` therefore uses
exactly the archived bytes.

The inventory is deliberately an opportunity inventory. A predicted transit
inside a scheduled or product time interval is not a successful timing, a
usable light curve, or a scored outcome. Calendar dates are interpreted
conservatively: one UTC day is removed from each official boundary and no
UTC-to-BJD_TDB correction is applied to the date-only schedule. Product
times are retained as MAST MJD metadata and carry the same explicit timing
limitation.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Iterable

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))
from sealed_era_inventory import coordinates  # noqa: E402
from transit_audit.exoclock import host_of, read_catalogue  # noqa: E402

OUT = ROOT / "results" / "sprint1" / "inventory"
RAW = ROOT / "data" / "raw" / "sprint1_metadata"
DRD = ROOT / "data" / "raw" / "osf" / "wpjtn" / "catalogue_of_ephemerides.txt"
FLAGS = ROOT / "data" / "fixtures" / "exoclock_ttv_flags.csv"
SCHEDULE = ROOT / "results" / "pilot_v1" / "tranche2_review" / "schedule_calendar_review.csv"
AS_OF_DATE = date(2026, 11, 6)
SEAL_START = date(2025, 11, 19)
JOURNAL_STRICT_A_START = date(2026, 2, 12)
# Parent reconciliation D042: the DRD OSF node became public on 2025-11-18;
# the conservative whole-day operational anchor is therefore 2025-11-19.
STRICT_A_START = SEAL_START
BOUNDARY_MARGIN_DAYS = 1.0
MAST_URL = "https://mast.stsci.edu/api/v0/invoke"
SHARD_SIZE = 50
MAST_COLUMNS = (
    "obs_id,target_name,obs_collection,provenance_name,sequence_number,"
    "t_min,t_max,t_obs_release,dataRights,dataproduct_type,dataURL,t_exptime"
)
PRODUCT_TYPES = {"SPOC_120": ("SPOC", 120), "TESS-SPOC_200": ("TESS-SPOC", 200)}


def mjd(day: date) -> float:
    return day.toordinal() - date(1858, 11, 17).toordinal()


def jd_from_mjd(value: float) -> float:
    return float(value) + 2400000.5


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def immutable_write(path: Path, data: bytes) -> None:
    """Write a cache once, refusing to replace an existing cache."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"immutable cache differs: {path}")
        return
    path.write_bytes(data)
    path.chmod(0o444)


def mast_request(target_names: list[str]) -> bytes:
    request = {
        "service": "Mast.Caom.Filtered",
        "format": "json",
        "params": {
            "columns": MAST_COLUMNS,
            "filters": [
                {"paramName": "target_name", "values": target_names},
                {"paramName": "provenance_name", "values": ["SPOC", "TESS-SPOC"]},
            ],
        },
    }
    body = ("request=" + urllib.parse.quote(json.dumps(request, separators=(",", ":")))).encode()
    req = urllib.request.Request(
        MAST_URL,
        data=body,
        headers={"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"},
    )
    with urllib.request.urlopen(req, timeout=180) as response:
        data = response.read()
    parsed = json.loads(data)
    if parsed.get("status") != "COMPLETE":
        raise RuntimeError(f"MAST metadata query failed: {parsed.get('status')}: {parsed.get('msg')}")
    return data


def load_or_acquire_mast(tic_ids: Iterable[str], acquire: bool) -> tuple[list[dict], list[dict]]:
    """Return MAST rows and source receipts, using immutable response shards."""
    names = sorted({str(x).replace("TIC ", "").replace("tic ", "") for x in tic_ids if str(x).strip()})
    shards = [names[i : i + SHARD_SIZE] for i in range(0, len(names), SHARD_SIZE)]
    rows: list[dict] = []
    receipts: list[dict] = []
    for index, shard in enumerate(shards):
        response_path = RAW / f"mast_caom_filtered_{index:03d}.json"
        receipt_path = RAW / f"mast_caom_filtered_{index:03d}.receipt.json"
        if not response_path.exists():
            if not acquire:
                raise FileNotFoundError(f"missing metadata cache {response_path}; rerun with --acquire")
            data = mast_request(shard)
            immutable_write(response_path, data)
            receipt = {
                "url": MAST_URL,
                "service": "Mast.Caom.Filtered",
                "target_names": shard,
                "retrieved_utc": datetime.now(timezone.utc).isoformat(),
                "sha256": sha256_bytes(data),
                "bytes": len(data),
                "metadata_only": True,
                "products_requested": False,
            }
            immutable_write(receipt_path, (json.dumps(receipt, indent=2) + "\n").encode())
        if not receipt_path.exists():
            raise FileNotFoundError(f"missing metadata receipt {receipt_path}")
        receipt = json.loads(receipt_path.read_text())
        if receipt.get("target_names") != shard:
            raise ValueError(f"metadata receipt roster mismatch: {receipt_path}")
        data = response_path.read_bytes()
        if receipt.get("sha256") != sha256_bytes(data) or not receipt.get("metadata_only"):
            raise ValueError(f"metadata provenance mismatch: {response_path}")
        parsed = json.loads(data)
        if parsed.get("status") != "COMPLETE":
            raise ValueError(f"incomplete metadata cache: {response_path}")
        paging = parsed.get("paging", {})
        if paging and (int(paging.get("rows", len(parsed.get("data", [])))) != len(parsed.get("data", []))
                       or int(paging.get("rowsFiltered", len(parsed.get("data", [])))) != len(parsed.get("data", []))
                       or int(paging.get("pagesFiltered", 1)) != 1):
            raise ValueError(f"MAST metadata response is paginated or truncated: {response_path}")
        rows.extend(parsed.get("data", []))
        receipts.append({"path": str(response_path.relative_to(ROOT)), **receipt})
    return rows, receipts


def read_schedule(path: Path = SCHEDULE) -> list[dict]:
    """Read the previously audited official HEASARC calendar extraction."""
    with path.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    out = []
    for row in rows:
        sec = int(row["sector"])
        start = date.fromisoformat(row["start_calendar_day"])
        end = date.fromisoformat(row["end_calendar_day"])
        if end < SEAL_START:
            continue
        interior_start = start + timedelta(days=BOUNDARY_MARGIN_DAYS)
        interior_end = end - timedelta(days=BOUNDARY_MARGIN_DAYS)
        out.append({
            **row,
            "sector": sec,
            "start_date": start,
            "end_date": end,
            "interior_start": interior_start,
            "interior_end": interior_end,
            "scheduled_as_of": (
                "ended" if end < AS_OF_DATE else "in_progress" if start <= AS_OF_DATE <= end else "future"
            ),
        })
    return out


def read_drd_flags(path: Path = FLAGS) -> set[str]:
    """Read the origin-known DRD TTV exclusions used by the historical cohort."""
    with path.open(newline="") as handle:
        return {row["planet"] for row in csv.DictReader(handle) if row["flag_release"] == "DRD"}


def classify_product(row: dict, as_of_mjd: float = mjd(AS_OF_DATE)) -> dict:
    """Classify a MAST observation row without reading its product."""
    provenance = str(row.get("provenance_name", ""))
    exp = row.get("t_exptime")
    exp = float(exp) if exp not in (None, "") else math.nan
    product = ""
    for name, (expected_prov, expected_exp) in PRODUCT_TYPES.items():
        if provenance == expected_prov and math.isfinite(exp) and abs(exp - expected_exp) < 1e-6:
            product = name
    observed = bool(row.get("t_max") not in (None, "") and float(row["t_max"]) <= as_of_mjd)
    released = bool(row.get("t_obs_release") not in (None, "") and float(row["t_obs_release"]) <= as_of_mjd)
    public = str(row.get("dataRights", "")).upper() == "PUBLIC"
    return {
        "product": product,
        "observed_by_as_of": observed,
        "public_by_as_of": released and public,
        "eligible_product_by_as_of": observed and released and public and bool(product),
        "product_status_reason": (
            "eligible_public_observed" if observed and released and public and product else
            "unknown_product_cadence" if not product else
            "not_observed_by_as_of" if not observed else
            "not_public_by_as_of" if not (released and public) else "metadata_incomplete"
        ),
    }


def count_opportunities(t0_bjd_tdb: float, period_days: float, start_jd: float, end_jd: float) -> int:
    """Count predicted integer epochs in a conservative numeric interval."""
    if end_jd <= start_jd or period_days <= 0:
        return 0
    lo = math.ceil((start_jd - t0_bjd_tdb) / period_days)
    hi = math.floor((end_jd - t0_bjd_tdb) / period_days)
    return max(0, hi - lo + 1)


def cohort(planet: str, ephemeris, tmag: float | None, by_host: dict[str, list[str]]) -> tuple[str, str]:
    host = host_of(planet)
    if len(by_host[host]) == 1 and tmag is not None and tmag < 13.5 and ephemeris.period_days <= 12:
        return "core", "single_drd_host_tmag_lt_13.5_period_le_12d"
    if ephemeris.period_days > 12:
        return "extension", "period_gt_12d"
    if len(by_host[host]) > 1:
        return "extension", "multi_drd_planet_host"
    if tmag is None:
        return "unresolved", "missing_tmag"
    if tmag >= 13.5:
        return "unresolved", "tmag_ge_13.5"
    return "unresolved", "other_core_rule_failure"


def _pointing(ra: float, dec: float) -> tuple[dict[int, str], str]:
    try:
        import tess_stars2px as tp
        result = tp.tess_stars2px_function_entry(np.array([0]), np.array([ra]), np.array([dec]), trySector=None)
        by_sector = {}
        for s, cam, ccd in sorted({(int(s), int(cam), int(ccd)) for s, cam, ccd in zip(result[3], result[4], result[5])}):
            by_sector[s] = f"C{cam}:CCD{ccd}"
        return by_sector, "tess-point"
    except Exception:
        return {}, "unavailable"


def build_inventory(*, acquire: bool = False, strict_a_start: date = STRICT_A_START) -> tuple[list[dict], dict]:
    D = read_catalogue(DRD)
    drd_flags = read_drd_flags()
    coords = coordinates(sorted(D))
    by_host: dict[str, list[str]] = defaultdict(list)
    for planet in D:
        by_host[host_of(planet)].append(planet)
    schedule = read_schedule()
    sectors = {r["sector"] for r in schedule}
    tic_ids = [c[2] for c in coords.values() if c is not None and c[2]]
    mast_rows, receipts = load_or_acquire_mast(tic_ids, acquire)
    receipt_times = sorted(r["retrieved_utc"] for r in receipts)
    # Do not use the end of the calendar day as an availability cutoff.  The
    # earliest shard receipt is a conservative common as-of for all shards.
    metadata_as_of_utc = receipt_times[0]
    metadata_as_of_mjd = datetime.fromisoformat(metadata_as_of_utc.replace("Z", "+00:00")).timestamp() / 86400 + 40587
    by_tic_sector: dict[tuple[str, int], list[dict]] = defaultdict(list)
    for row in mast_rows:
        try:
            sec = int(row.get("sequence_number"))
        except (TypeError, ValueError):
            continue
        if sec in sectors:
            by_tic_sector[(str(row.get("target_name", "")), sec)].append(row)

    output: list[dict] = []
    for planet in sorted(D):
        e = D[planet]
        c = coords.get(planet)
        host = host_of(planet)
        drd_ttv_flag = planet in drd_flags
        if c is None:
            output.append({"planet": planet, "host": host, "drd_ttv_flag": drd_ttv_flag, "cohort": "unresolved", "inclusion_basis": "missing_archive_coordinates", "sector": "", "product": "", "status": "unresolved_metadata"})
            continue
        ra, dec, tic, tmag_text, coord_basis = c
        tmag = float(tmag_text) if tmag_text not in (None, "") else None
        label, basis = cohort(planet, e, tmag, by_host)
        tic_num = str(tic).replace("TIC ", "").replace("tic ", "")
        pointing, pointing_basis = _pointing(ra, dec)
        for s in schedule:
            sec = s["sector"]
            scheduled_jd_start = s["interior_start"].toordinal() - date(1858, 11, 17).toordinal() + 2400000.5
            scheduled_jd_end = s["interior_end"].toordinal() - date(1858, 11, 17).toordinal() + 2400000.5
            candidates = by_tic_sector.get((tic_num, sec), [])
            if not candidates:
                n = count_opportunities(e.t0_bjd_tdb, e.period_days, scheduled_jd_start, scheduled_jd_end)
                strict_n = count_opportunities(e.t0_bjd_tdb, e.period_days, max(scheduled_jd_start, strict_a_start.toordinal() - date(1858, 11, 17).toordinal() + 2400000.5), scheduled_jd_end)
                journal_n = count_opportunities(e.t0_bjd_tdb, e.period_days, max(scheduled_jd_start, JOURNAL_STRICT_A_START.toordinal() - date(1858, 11, 17).toordinal() + 2400000.5), scheduled_jd_end)
                output.append({
                    "planet": planet, "host": host, "tic": tic, "tmag": tmag_text,
                    "period_days": e.period_days, "drd_ttv_flag": drd_ttv_flag, "cohort": label, "inclusion_basis": basis,
                    "sector": sec, "product": "", "camera_ccd": pointing.get(sec, ""), "camera_ccd_basis": pointing_basis,
                    "schedule_start_utc": s["start_date"].isoformat(), "schedule_end_utc": s["end_date"].isoformat(),
                    "conservative_start_utc": s["interior_start"].isoformat(), "conservative_end_utc": s["interior_end"].isoformat(),
                    "product_t_min_mjd": "", "product_t_max_mjd": "", "product_release_mjd": "",
                    "scheduled_status_as_of": s["scheduled_as_of"], "observed_by_as_of": False,
                    "public_by_as_of": False, "eligible_product_by_as_of": False,
                    "strict_a_window": s["interior_start"] >= strict_a_start,
                    "opportunity_count": n, "strict_a_opportunity_count": strict_n, "journal_strict_a_opportunity_count": journal_n,
                    "opportunity_basis": "DRD_ephemeris_in_official_calendar_interior",
                    "status": "scheduled_no_target_product_metadata",
                })
                continue
            seen_products = set()
            for raw in candidates:
                info = classify_product(raw, as_of_mjd=metadata_as_of_mjd)
                product = info["product"]
                exp = raw.get("t_exptime")
                exp = float(exp) if exp not in (None, "") else math.nan
                if not product and str(raw.get("provenance_name", "")) == "SPOC" and math.isfinite(exp):
                    product = f"SPOC_{int(exp)}"
                elif not product and str(raw.get("provenance_name", "")) == "TESS-SPOC" and math.isfinite(exp):
                    product = "TESS-SPOC_other"
                if not product or product in seen_products:
                    continue
                seen_products.add(product)
                tmin = float(raw["t_min"]) if raw.get("t_min") not in (None, "") else None
                tmax = float(raw["t_max"]) if raw.get("t_max") not in (None, "") else None
                release = float(raw["t_obs_release"]) if raw.get("t_obs_release") not in (None, "") else None
                start_jd = max(scheduled_jd_start, jd_from_mjd(tmin) if tmin is not None else scheduled_jd_start)
                end_jd = min(scheduled_jd_end, jd_from_mjd(tmax) if tmax is not None else scheduled_jd_end)
                n = count_opportunities(e.t0_bjd_tdb, e.period_days, start_jd, end_jd)
                strict_n = count_opportunities(e.t0_bjd_tdb, e.period_days, max(start_jd, strict_a_start.toordinal() - date(1858, 11, 17).toordinal() + 2400000.5), end_jd)
                journal_n = count_opportunities(e.t0_bjd_tdb, e.period_days, max(start_jd, JOURNAL_STRICT_A_START.toordinal() - date(1858, 11, 17).toordinal() + 2400000.5), end_jd)
                output.append({
                    "planet": planet, "host": host, "tic": tic, "tmag": tmag_text,
                    "period_days": e.period_days, "drd_ttv_flag": drd_ttv_flag, "cohort": label, "inclusion_basis": basis,
                    "sector": sec, "product": product, "product_t_exptime_s": exp if math.isfinite(exp) else "",
                    "camera_ccd": pointing.get(sec, ""), "camera_ccd_basis": pointing_basis,
                    "schedule_start_utc": s["start_date"].isoformat(), "schedule_end_utc": s["end_date"].isoformat(),
                    "conservative_start_utc": s["interior_start"].isoformat(), "conservative_end_utc": s["interior_end"].isoformat(),
                    "product_t_min_mjd": tmin if tmin is not None else "", "product_t_max_mjd": tmax if tmax is not None else "",
                    "product_release_mjd": release if release is not None else "", "product_obs_id": raw.get("obs_id", ""),
                    "product_data_uri": raw.get("dataURL", ""), "scheduled_status_as_of": s["scheduled_as_of"],
                    "observed_by_as_of": info["observed_by_as_of"], "public_by_as_of": info["public_by_as_of"],
                    "eligible_product_by_as_of": info["eligible_product_by_as_of"],
                    "strict_a_window": s["interior_start"] >= strict_a_start,
                    "opportunity_count": n, "strict_a_opportunity_count": strict_n, "journal_strict_a_opportunity_count": journal_n,
                    "opportunity_basis": "DRD_ephemeris_in_MAST_product_intersection",
                    "status": info["product_status_reason"] if info["product"] else "non_target_product_cadence",
                })

    def population_counts(start: date, opportunity_field: str, exclude_flags: bool):
        eligible = {
            r["planet"] for r in output
            if r.get("eligible_product_by_as_of") and r.get(opportunity_field, 0) > 0
            and (not exclude_flags or not r.get("drd_ttv_flag"))
        }
        core_set = {p for p in eligible if any(r.get("planet") == p and r.get("cohort") == "core" for r in output)}
        extension_set = {p for p in eligible if any(r.get("planet") == p and r.get("cohort") == "extension" for r in output)}
        union_set = core_set | extension_set
        return {
            "core": len(core_set),
            "extension": len(extension_set),
            "union": len(union_set),
            "extension_increment_over_core_percent": 100 * len(extension_set) / len(core_set) if core_set else None,
            "extension_increment_over_union_percent": 100 * len(extension_set) / len(union_set) if union_set else None,
            "product_rows": sum(bool(r.get("eligible_product_by_as_of")) and r.get(opportunity_field, 0) > 0
                                 and (not exclude_flags or not r.get("drd_ttv_flag")) for r in output),
            "opportunities": sum(r.get(opportunity_field, 0) for r in output
                                  if r.get("eligible_product_by_as_of") and (not exclude_flags or not r.get("drd_ttv_flag"))),
        }

    primary_counts = population_counts(strict_a_start, "strict_a_opportunity_count", True)
    journal_counts = population_counts(JOURNAL_STRICT_A_START, "journal_strict_a_opportunity_count", True)
    primary_counts_pre_flag = population_counts(strict_a_start, "strict_a_opportunity_count", False)
    journal_counts_pre_flag = population_counts(JOURNAL_STRICT_A_START, "journal_strict_a_opportunity_count", False)
    summary = {
        "metadata_only": True,
        "light_curves_opened": 0,
        "products_requested": False,
        "as_of_utc": metadata_as_of_utc,
        "metadata_query_first_retrieved_utc": receipt_times[0],
        "metadata_query_last_retrieved_utc": receipt_times[-1],
        "sealed_start_utc": "2025-11-19T00:00:00Z",
        "strict_a_start_utc": strict_a_start.isoformat() + "T00:00:00Z",
        "journal_strict_a_sensitivity_utc": JOURNAL_STRICT_A_START.isoformat() + "T00:00:00Z",
        "boundary_margin_days": BOUNDARY_MARGIN_DAYS,
        "boundary_method": "subtract one full UTC day from official date-only sector boundaries; no UTC-to-BJD_TDB conversion",
        "drd_planets": len(D),
        "drd_hosts": len(by_host),
        "drd_origin_ttv_flags": len(drd_flags & set(D)),
        "core_rule": "single DRD planet per host, Tmag < 13.5, P <= 12 d",
        "extension_rule": "P > 12 d OR host has multiple DRD planets; union without double count",
        "core_eligible_planets_with_public_product": primary_counts["core"],
        "extension_eligible_planets_with_public_product": primary_counts["extension"],
        "eligible_union_planets_with_public_product": primary_counts["union"],
        "extension_increment_over_core_percent": primary_counts["extension_increment_over_core_percent"],
        "extension_increment_over_union_percent": primary_counts["extension_increment_over_union_percent"],
        "strict_a_counts": primary_counts,
        "strict_a_counts_pre_flag_sensitivity": primary_counts_pre_flag,
        "journal_strict_a_counts_sensitivity": journal_counts,
        "journal_strict_a_counts_pre_flag_sensitivity": journal_counts_pre_flag,
        "r8_gate": "OR: extension adds >=15% of metadata-eligible sealed-era planets OR projected SE changes >=10%; SE not inferred here",
        "eligible_product_rows_all_metadata": sum(bool(r.get("eligible_product_by_as_of")) for r in output),
        "eligible_product_rows_origin_unflagged": sum(bool(r.get("eligible_product_by_as_of")) and not r.get("drd_ttv_flag") for r in output),
        "opportunity_count_eligible_product_rows_all_metadata": sum(r["opportunity_count"] for r in output if r.get("eligible_product_by_as_of")),
        "opportunity_count_eligible_product_rows_origin_unflagged": sum(r["opportunity_count"] for r in output if r.get("eligible_product_by_as_of") and not r.get("drd_ttv_flag")),
        "scheduled_rows_without_target_product_metadata": sum(r.get("status") == "scheduled_no_target_product_metadata" for r in output),
        "mast_product_rows_by_label": dict(sorted((label, sum(r.get("product") == label for r in output)) for label in sorted({r.get("product", "") for r in output}))),
        "non_target_cadence_rows": sum(r.get("status") == "non_target_product_cadence" for r in output),
        "catalogue_coordinate_matches": sum(c is not None for c in coords.values()),
        "catalogue_coordinate_unmatched": sum(c is None for c in coords.values()),
        "catalogue_tic_matches": sum(c is not None and bool(c[2]) for c in coords.values()),
        "catalogue_tic_unmatched": sum(c is None or not c[2] for c in coords.values()),
        "catalogue_unique_tics": len({str(c[2]).replace("TIC ", "") for c in coords.values() if c is not None and c[2]}),
        "mast_metadata_rows": len(mast_rows),
        "mast_target_tic_matches": len({str(r.get("target_name", "")) for r in mast_rows}),
        "mast_target_tic_unmatched": len({str(c[2]).replace("TIC ", "") for c in coords.values() if c is not None and c[2]} - {str(r.get("target_name", "")) for r in mast_rows}),
        "unknown_planets_count": len(set(D) - {r["planet"] for r in output if r.get("eligible_product_by_as_of") and r["opportunity_count"] > 0}),
        "unknown_planet_examples": sorted(set(D) - {r["planet"] for r in output if r.get("eligible_product_by_as_of") and r["opportunity_count"] > 0})[:10],
        "mast_receipts": receipts,
        "source_files": [str(DRD.relative_to(ROOT)), str(SCHEDULE.relative_to(ROOT))],
        "opportunity_warning": "Counts are ephemeris opportunities, never measured successes or scored outcomes; cadence quality, gaps, full-transit capture, and identification remain unknown.",
    }
    return output, summary


def write_outputs(rows: list[dict], summary: dict, out: Path = OUT) -> None:
    out.mkdir(parents=True, exist_ok=True)
    fields = sorted({key for row in rows for key in row})
    with (out / "planet_sector_product_inventory.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    (out / "inventory_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (out / "inventory_manifest.json").write_text(json.dumps({
        "script": str(Path(__file__).relative_to(ROOT)),
        "script_sha256": sha256_bytes(Path(__file__).read_bytes()),
        "outputs": {name: sha256_bytes((out / name).read_bytes()) for name in ("planet_sector_product_inventory.csv", "inventory_summary.json")},
        "metadata_only": True,
        "light_curves_opened": 0,
    }, indent=2, sort_keys=True) + "\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--acquire", action="store_true", help="query public MAST metadata and cache immutable JSON shards")
    parser.add_argument("--strict-a-start", default=STRICT_A_START.isoformat(), help="strict-A UTC date, default 2025-11-19")
    args = parser.parse_args(argv)
    strict_a = date.fromisoformat(args.strict_a_start)
    rows, summary = build_inventory(acquire=args.acquire, strict_a_start=strict_a)
    write_outputs(rows, summary)
    print(json.dumps({k: v for k, v in summary.items() if k not in {"mast_receipts", "unknown_planets"}}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
