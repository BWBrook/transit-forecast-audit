"""Derive release-input information age without opening photometry (T019).

    .venv/bin/python scripts/t019_information_ledger.py

The exact first forecast availability is distinct from the first availability
of its released timing table. Current archive labels are not historical facts.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from transit_audit.exoclock import host_of, read_catalogue, read_drb_ephemerides

OUT = ROOT / "results/information_ledger"
RAW = ROOT / "data/raw/osf"
NODES = {"DRB": "wna5e", "DRC": "p298n", "DRD": "wpjtn"}
DRB_ZIP = RAW / "wna5e/5_complete_ExoClock_DRB.zip"
DRB_PREFIX = "ExoClock_DRB/2_catalogue_of_ExoClock_ephemerides/data_sources/"
SOURCE_MANIFEST = ROOT / "results/pilot_v1/source_manifest.csv"
HISTORY = ROOT / "results/sprint1/literature/osf_history_verification.json"
FLAGS = ROOT / "data/fixtures/exoclock_ttv_flags.csv"
ROSTER = ROOT / "results/sprint2/freeze_candidate/roster.csv"
ARCHIVE_LABELS = ROOT / "results/final_secondaries/ttv/labels.csv"
MANIFESTS = [ROOT / "results/prefreeze/manifest_core_primary.csv",
             ROOT / "results/prefreeze/manifest_extension_exploratory.csv"]


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def utc(value):
    return datetime.fromisoformat(value.rstrip("Z")).replace(tzinfo=timezone.utc)


def calendar_label(jd):
    """Format the named JD scale's Gregorian calendar, without scale conversion.

    JD2451545 is Gregorian 2000-01-01 at noon. Input BJD_TDB is therefore
    labelled as a TDB calendar representation, never relabelled UTC.
    """
    return (datetime(2000, 1, 1, 12) + timedelta(days=float(jd) - 2451545)).date().isoformat()


def timing_statistics(ephemeris, rows):
    valid = [r for r in rows if math.isfinite(r["time"]) and
             math.isfinite(r["sigma"]) and r["sigma"] > 0]
    result = {"released_timing_rows": len(rows), "valid_timing_rows": len(valid),
              "invalid_timing_rows": len(rows) - len(valid)}
    for key in ("first_input_bjd_tdb", "last_input_bjd_tdb", "input_baseline_days",
                "issued_line_chi2", "issued_line_chi2_over_N", "issued_line_reduced_chi2_Nminus2",
                "issued_line_z_rms", "issued_line_residual_rms_minutes"):
        result[key] = None
    result.update(first_input_calendar_tdb=None, last_input_calendar_tdb=None,
                  nominal_dof_Nminus2=None, row_source_counts="{}",
                  unique_nearest_orbit_epochs=None, same_epoch_extra_rows=None)
    if not valid:
        return result
    times = np.array([r["time"] for r in valid])
    sigma = np.array([r["sigma"] for r in valid])
    epochs = np.rint((times - ephemeris.t0_bjd_tdb) / ephemeris.period_days)
    residuals = times - (ephemeris.t0_bjd_tdb + epochs * ephemeris.period_days)
    chi2 = float(np.sum((residuals / sigma)**2))
    n = len(valid)
    result.update(first_input_bjd_tdb=float(times.min()), last_input_bjd_tdb=float(times.max()),
                  first_input_calendar_tdb=calendar_label(times.min()),
                  last_input_calendar_tdb=calendar_label(times.max()),
                  input_baseline_days=float(np.ptp(times)), issued_line_chi2=chi2,
                  issued_line_chi2_over_N=chi2 / n,
                  nominal_dof_Nminus2=n - 2 if n > 2 else None,
                  issued_line_reduced_chi2_Nminus2=chi2 / (n - 2) if n > 2 else None,
                  issued_line_z_rms=float(np.sqrt(chi2 / n)),
                  issued_line_residual_rms_minutes=float(np.sqrt(np.mean(residuals**2)) * 1440),
                  unique_nearest_orbit_epochs=len(set(epochs)),
                  same_epoch_extra_rows=n-len(set(epochs)),
                  row_source_counts=json.dumps(dict(sorted(Counter(r["source"] for r in valid).items()))))
    return result


def read_combined(path):
    rows = defaultdict(list)
    for line in Path(path).read_text().splitlines()[1:]:
        f = line.split()
        if not f:
            continue
        if len(f) != 5:
            raise ValueError("Unexpected released timing row")
        rows[f[0]].append({"time": float(f[1]), "sigma": float(f[2]), "source": f[3]})
    return rows


def read_drb_inputs():
    rows, members = {}, {}
    with ZipFile(DRB_ZIP) as archive:
        for member in archive.namelist():
            if not member.startswith(DRB_PREFIX) or not member.endswith(".txt"):
                continue
            planet = Path(member).stem
            data = archive.read(member)
            parsed = []
            for line in data.decode().splitlines():
                if not line.strip() or line.startswith("#"):
                    continue
                f = line.split("\t")
                if len(f) < 4:
                    raise ValueError("Unexpected DRB source row")
                parsed.append({"time": float(f[1]), "sigma": float(f[2]), "source": f[3].strip().lower()})
            rows[planet] = parsed
            members[planet] = {"member": member, "sha256": hashlib.sha256(data).hexdigest()}
    return rows, members


def chronology():
    sources = list(csv.DictReader(SOURCE_MANIFEST.open()))
    histories = json.loads(HISTORY.read_text())["histories"]
    public = {h["node"]: utc(h["public_at_utc"]) for h in histories}
    result = {}
    for release, node in NODES.items():
        subset = [r for r in sources if r["release"] == release]
        forecast = next(r for r in subset if r["osf_name"] ==
                        ("updated_ephemerides.txt" if release == "DRB" else "catalogue_of_ephemerides.txt"))
        timings = next(r for r in subset if r["osf_name"] ==
                       ("5_complete_ExoClock_DRB.zip" if release == "DRB" else "all_mid_time_data.txt"))
        for r in (forecast, timings):
            if digest(ROOT / r["local_path"]) != r["sha256"]:
                raise ValueError("Released source hash mismatch")
        forecast_at = max(public[node], utc(forecast["osf_date_created"]))
        timing_at = max(public[node], utc(timings["osf_date_created"]))
        result[release] = {
            "forecast_first_public_utc": forecast_at.isoformat(),
            "released_timing_artifact_first_public_utc": timing_at.isoformat(),
            "release_bundle_first_public_utc": max(forecast_at, timing_at).isoformat(),
            "timing_after_forecast_seconds": (timing_at - forecast_at).total_seconds(),
            "timing_features_verified_at_exact_forecast_origin": timing_at <= forecast_at,
            "forecast_path": forecast["local_path"], "timing_path": timings["local_path"],
            "interpretation": "max(node made-public transition, immutable-v1 artifact creation); exact DRB member provenance qualified separately",
        }
    return result


def write_csv(path, rows):
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader(); writer.writerows(rows)
    data = stream.getvalue().encode()
    path.write_bytes(gzip.compress(data, mtime=0) if str(path).endswith(".gz") else data)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    chrono = chronology()
    inputs = [SOURCE_MANIFEST, HISTORY, FLAGS, ROSTER, ARCHIVE_LABELS, *MANIFESTS,
              ROOT / "data/raw/sprint1_osf_logs/wna5e.json", DRB_ZIP,
              *[ROOT / c[key] for c in chrono.values() for key in ("forecast_path", "timing_path")]]
    external_dir = OUT / "external_metadata"
    external = ({r["planet"]:r for r in csv.DictReader((external_dir / "targets.csv").open())}
                if (external_dir / "targets.csv").exists() else {})
    companion_candidates = (list(csv.DictReader((external_dir / "companion_candidates.csv").open()))
                            if (external_dir / "companion_candidates.csv").exists() else [])
    if external:
        inputs += [external_dir / p for p in ("targets.csv", "companion_candidates.csv", "origin_candidate_dates.csv", "provenance.json")]
    input_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(set(inputs))}
    eph = {"DRB": read_drb_ephemerides(RAW / "wna5e/updated_ephemerides.txt"),
           "DRC": read_catalogue(RAW / "p298n/catalogue_of_ephemerides.txt"),
           "DRD": read_catalogue(RAW / "wpjtn/catalogue_of_ephemerides.txt")}
    drb, members = read_drb_inputs()
    timing = {"DRB": drb, "DRC": read_combined(RAW / "p298n/all_mid_time_data.txt"),
              "DRD": read_combined(RAW / "wpjtn/all_mid_time_data.txt")}
    flagged = defaultdict(set)
    for r in csv.DictReader(FLAGS.open()):
        flagged[r["flag_release"]].add(r["planet"])
    flagged["DRB"] = {p for p,e in eph["DRB"].items() if "nonlinear" in e.flags}
    drb_log = json.loads((ROOT / "data/raw/sprint1_osf_logs/wna5e.json").read_text())
    preforecast_paths = {r["attributes"].get("params", {}).get("path", "")
                         for r in drb_log["data"] if
                         r["attributes"]["action"] == "osf_storage_file_added" and
                         utc(r["attributes"]["date"]) <= utc(chrono["DRB"]["forecast_first_public_utc"])}
    planet_rows, lookup = [], {}
    for release, planets in eph.items():
        host_counts = Counter(host_of(p) for p in planets)
        for planet, e in sorted(planets.items()):
            stats = timing_statistics(e, timing[release].get(planet, []))
            row = {"release": release, "planet": planet, "catalogue_host_label": host_of(planet),
                   "catalogued_planets_with_same_host_label": host_counts[host_of(planet)],
                   "host_label_basis": "repository name heuristic; not physical companion inventory",
                   "t0_bjd_tdb": e.t0_bjd_tdb, "period_days": e.period_days,
                   "origin_release_ttv_flag": planet in flagged[release],
                   "origin_flag_basis": "release-specific detection criterion, not exhaustive literature knowledge",
                   "release_flag_source_type": "column_in_exact_forecast_file" if release == "DRB" else "publication_table_transcription_not_forecast_column",
                   "flag_at_exact_forecast_origin_verified": release == "DRB",
                   "flag_source_availability_limit": "exact-v1 forecast columns" if release == "DRB" else "publication first-public timestamp not independently checked against forecast timestamp",
                   **stats,
                   "input_table_status": "released_rows_not_independently_certified_fitting_membership",
                   "strict_origin_timing_features_eligible": chrono[release]["timing_features_verified_at_exact_forecast_origin"],
                   "timing_artifact_delay_seconds": chrono[release]["timing_after_forecast_seconds"],
                   "forecast_first_public_utc": chrono[release]["forecast_first_public_utc"],
                   "release_bundle_first_public_utc": chrono[release]["release_bundle_first_public_utc"],
                   "DRB_individual_source_preforecast_log_found": None,
                   "DRB_zip_member_sha256": None,
                   "origin_transit_duration_minutes": None,
                   "duration_status": "not_present_as_verified_duration_in_exact_ephemeris_timing_inputs"}
            if release == "DRB":
                row["DRB_individual_source_preforecast_log_found"] = (
                    f"/2_catalogue_of_ExoClock_ephemerides/data_sources/{planet}.txt" in preforecast_paths)
                row["DRB_zip_member_sha256"] = members.get(planet, {}).get("sha256")
                row["input_table_status"] += "; later_zip_member_bytes_not_bound_to_earlier_individual_file_version"
            planet_rows.append(row); lookup[release, planet] = row
    write_csv(OUT / "release_planets.csv", planet_rows)

    events = []
    for path in MANIFESTS:
        for event in csv.DictReader(path.open()):
            t = float(event["drd_predicted_bjd_tdb"])
            for release in NODES:
                if (release, event["planet"]) not in lookup:
                    continue
                r = lookup[release, event["planet"]]; e = eph[release][event["planet"]]
                baseline, last = r["input_baseline_days"], r["last_input_bjd_tdb"]
                age = t - last if last is not None else None
                epoch = int(np.rint((t - e.t0_bjd_tdb) / e.period_days))
                marginal_sd_s = math.sqrt(e.sigma_t0_days**2 + (epoch * e.sigma_period_days)**2) * 86400
                lead = (datetime.fromisoformat(calendar_label(t)).date() -
                        utc(chrono[release]["forecast_first_public_utc"]).date()).days
                events.append({"event_id": event["event_id"], "cohort": event["cohort"],
                               "planet": event["planet"], "reference_release": release,
                               "event_time_basis": "fixed DRD predicted opportunity, not observed outcome",
                               "drd_predicted_bjd_tdb": t, "extrapolation_age_days": age,
                               "age_over_input_baseline": age / baseline if age is not None and baseline else None,
                               "operational_lead_coarse_calendar_days": lead,
                               "lead_time_note": "TDB calendar day minus UTC issue calendar day; no barycentric/time-scale conversion; not exact eligibility",
                               "forecast_epoch_in_reference_release": epoch,
                               "forecast_sd_zero_covariance_seconds": marginal_sd_s,
                               "covariance_basis": "marginal-only descriptive sensitivity; not issued joint posterior or final C2",
                               "forecast_sd_over_origin_duration": None,
                               "duration_status": r["duration_status"],
                               "strict_origin_timing_features_eligible": r["strict_origin_timing_features_eligible"]})
    write_csv(OUT / "fixed_opportunity_ages.csv.gz", events)

    roster = list(csv.DictReader(ROSTER.open()))
    current = {r["planet"]: r for r in csv.DictReader(ARCHIVE_LABELS.open())}
    knowledge = []
    for target in roster:
        for release in NODES:
            r = lookup.get((release, target["planet"]))
            warning = target["host"] == "HR858" and release == "DRD"
            knowledge.append({"release": release, "planet": target["planet"], "host": target["host"],
                              "in_release_catalogue": r is not None,
                              "catalogued_planets_same_host_label": r["catalogued_planets_with_same_host_label"] if r else None,
                              "origin_release_ttv_flag": r["origin_release_ttv_flag"] if r else None,
                              "flag_at_exact_forecast_origin_verified": r["flag_at_exact_forecast_origin_verified"] if r else None,
                              "flag_source_availability_limit": r["flag_source_availability_limit"] if r else "target not in release",
                              "uniform_companion_metadata_search_status": "completed_from_saved_archive" if external else "not_searched",
                              "uniform_ttv_primary_literature_search_status": "not_searched",
                              "current_companion_candidates": external.get(target["planet"], {}).get("current_companion_candidates"),
                              "current_parameter_publication_date": external.get(target["planet"], {}).get("current_parameter_publication_date"),
                              "current_parameter_reference": external.get(target["planet"], {}).get("current_parameter_reference"),
                              "historical_companion_inventory_status": "uniform_metadata_candidates_collected; primary_source_verification_pending" if external else "unknown_not_reconstructable_from_saved_current_metadata",
                              "pre_origin_literature_ttv_status": "verified_positive_case_audit_not_uniform" if warning else "not_searched",
                              "warning_source": "https://doi.org/10.1051/0004-6361/202451300" if warning else None,
                              "warning_date_basis": "journal January2025 and November2024 public preprint; both before DRD origin" if warning else None,
                              "eligible_external_predictor_for_uniform_rule": False,
                              "current_archive_ttv_flag": current.get(target["planet"], {}).get("archive_ttv_flag"),
                              "current_label_retrieved_utc": current.get(target["planet"], {}).get("retrieved_at_utc"),
                              "current_label_limit": "dated descriptive metadata; not origin knowledge; unflagged is not physical negative"})
    write_csv(OUT / "origin_knowledge.csv", knowledge)
    ratio_rows = []
    for candidate in companion_candidates:
        for release, planets in eph.items():
            target_e = planets.get(candidate["planet"])
            companion_e = planets.get(candidate["companion_archive_name"].replace(" ", ""))
            ratio_rows.append({"release": release, "planet": candidate["planet"],
                               "companion_archive_name": candidate["companion_archive_name"],
                               "target_in_release": target_e is not None,
                               "companion_in_release_by_whitespace_only_name": companion_e is not None,
                               "released_period_ratio_companion_over_target": companion_e.period_days / target_e.period_days if target_e and companion_e else None,
                               "status": "release_periods_for_current_archive_companion_candidate; historical_confirmation_not_verified" if target_e and companion_e else "period_ratio_unknown; companion_or_target_not_in_release",
                               "historical_knowledge_eligible": False})
    if ratio_rows:
        write_csv(OUT / "companion_period_candidates.csv", ratio_rows)

    cutoff_audit = {}
    for release in ("DRC", "DRD"):
        flat = [(planet, row) for planet, rows in timing[release].items() for row in rows]
        sources = {}
        for source in sorted({r["source"] for _,r in flat}):
            subset = [(p,r) for p,r in flat if r["source"] == source]
            late = [(p,r) for p,r in subset if r["time"] >= 2460313.5]
            sources[source] = {"rows": len(subset), "max_input_bjd_tdb": max(r["time"] for _,r in subset),
                               "max_input_calendar_tdb": calendar_label(max(r["time"] for _,r in subset)),
                               "rows_at_or_after_nominal_2024_01_04_TDB": len(late),
                               "planets_with_such_rows": len({p for p,_ in late})}
        cutoff_audit[release] = sources
    summary = {"release_planets": dict(Counter(r["release"] for r in planet_rows)),
               "strict_origin_timing_feature_eligible_planets": dict(Counter(r["release"] for r in planet_rows if r["strict_origin_timing_features_eligible"])),
               "fixed_opportunity_age_rows": len(events), "origin_knowledge_rows": len(knowledge),
               "external_predictor_complete": False,
               "external_search_status": "uniform_cached_companion_metadata_screen_complete; historical_primary_source_curation_pending" if external else "not_searched uniformly; no false negative labels",
               "external_targets_screened": len(external),
               "current_directed_companion_candidates": len(companion_candidates),
               "companion_reference_release_ratios_available": sum(r["released_period_ratio_companion_over_target"] is not None for r in ratio_rows),
               "duration_complete": False, "DRD_all_source_cutoff_audit": cutoff_audit["DRD"],
               "cutoff_definition": "JD2460313.5 is nominal TDB calendar2024-01-04, not a UTC/barycentric boundary conversion",
               "HR858b_DRD": lookup["DRD", "HR858b"],
               "HR858b_fixed_opportunity_age_range_days": [min(r["extrapolation_age_days"] for r in events if r["planet"] == "HR858b" and r["reference_release"] == "DRD"), max(r["extrapolation_age_days"] for r in events if r["planet"] == "HR858b" and r["reference_release"] == "DRD")],
               "limits": ["Released rows are not an independently certified fit-inclusion mask.",
                          "Nominal N-minus2 reduced chi-square uses published rounded ephemeris without refit; it is not residual scatter in sigma units.",
                          "DRB/DRC timing-derived predictors are not verified available at exact forecast origin.",
                          "DRC/DRD flag lists are publication-table labels, whose exact first-public timestamp has not been checked against forecast availability.",
                          "Current metadata does not reconstruct historical companion inventories or prove negative TTV evidence.",
                          "No raw photometry, headers, new measurements or S74-S97 outcomes read."]}
    (OUT / "source_chronology.json").write_text(json.dumps(chrono, indent=2, allow_nan=False) + "\n")
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, allow_nan=False) + "\n")
    receipt = {"script_sha256": digest(Path(__file__)),
               "input_sha256": input_hashes,
               "output_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sorted(OUT.iterdir()) if p.is_file() and p.name != "receipt.json"},
               "input_unchanged_after": True, "photometry_or_headers_opened": False,
               "external_network_requests": 0, "primary_outputs_changed": False}
    for path, expected in receipt["input_sha256"].items():
        if digest(ROOT / path) != expected:
            raise ValueError("Input changed during ledger build")
    (OUT / "receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("release_planets", "fixed_opportunity_age_rows", "origin_knowledge_rows")}))


if __name__ == "__main__":
    main()
