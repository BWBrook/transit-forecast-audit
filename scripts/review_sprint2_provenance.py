"""Audit Sprint 2 metadata, hashes and frozen-source identity without reading FITS.

    .venv/bin/python scripts/review_sprint2_provenance.py

Only results/sprint2_review/provenance is written. Download ordering and historical
non-access cannot be proved from undated run logs or a later directory receipt.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import io
import json
import math
import statistics
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/sprint2_review/provenance"
BASELINE = "d54142e"
sys.path.insert(0, str(ROOT / "src"))
from transit_audit.exoclock import read_catalogue  # noqa: E402


def safe_bytes(path):
    path = Path(path)
    if path.suffix.lower() == ".fits" or (ROOT / "data/raw/mast") in path.parents:
        raise ValueError("This audit must not open photometry")
    return path.read_bytes()


def sha(path):
    return hashlib.sha256(safe_bytes(path)).hexdigest()


def rows(path):
    path = ROOT / path
    data = safe_bytes(path)
    if path.suffix == ".gz":
        data = gzip.decompress(data)
    return list(csv.DictReader(io.StringIO(data.decode())))


def obj(path):
    return json.loads(safe_bytes(ROOT / path))


def git(*args):
    return subprocess.run(["git", "-C", str(ROOT), *args], check=True, capture_output=True).stdout


def write_csv(name, records):
    with (OUT / name).open("w", newline="") as handle:
        writer = csv.DictWriter(handle, list(records[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(records)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    handoff = json.loads(git("show", f"{BASELINE}:results/sprint2/handoff.json"))
    checks = []
    for row in handoff["outputs"]:
        path = ROOT / row["path"]
        actual = sha(path) if path.is_file() else "MISSING"
        checks.append({"path": row["path"], "recorded": row["sha256"], "actual": actual,
                       "matches": actual == row["sha256"]})
    write_csv("handoff_hashes.csv", checks)
    source_checks = []
    for row in rows("results/pilot_v1/source_manifest.csv"):
        path = ROOT / row["local_path"]
        actual = sha(path) if path.is_file() else "MISSING"
        source_checks.append({"release": row["release"], "source_id": row["source_id"],
                              "path": row["local_path"], "recorded": row["sha256"],
                              "actual": actual, "matches": actual == row["sha256"]})
    write_csv("source_hashes.csv", source_checks)

    chronology = []
    for rev in ("2c39f0a", "9375b3c", "d54142e"):
        code = b"".join(git("show", f"{rev}:{p}") for p in
                        ("scripts/sprint2_outcomes.py", "scripts/t015_timing_pipeline.py"))
        chronology.append({"commit": rev, "git_dates": git("show", "-s", "--format=%aI|%cI", rev).decode().strip(),
                           "combined_source_sha256": hashlib.sha256(code).hexdigest(),
                           "confirmation_selection_present": bool(git("ls-tree", "-r", "--name-only", rev,
                                                                        "results/sprint2/confirm/selection.csv")),
                           "replication_selection_present": bool(git("ls-tree", "-r", "--name-only", rev,
                                                                       "results/sprint2/confirm2/selection.csv"))})
    rule_receipts = {s: obj(f"results/sprint2/{s}/run_receipt.json") for s in ("dev", "confirm", "confirm2")}
    frozen_source = chronology[0]["combined_source_sha256"]

    inventory = rows("results/sprint1/inventory/planet_sector_product_inventory.csv")
    selected = [r for r in inventory if r["eligible_product_by_as_of"] == "True"
                and int(r["strict_a_opportunity_count"] or 0) > 0 and r["drd_ttv_flag"] == "False"
                and r["cohort"] in ("core", "extension")]
    drd = read_catalogue(ROOT / "data/raw/osf/wpjtn/catalogue_of_ephemerides.txt")
    expected = {}
    expected_count = Counter()
    for row in selected:
        planet = row["planet"]
        eph = drd[planet]
        jd = lambda s: date.fromisoformat(s).toordinal() - date(1858, 11, 17).toordinal() + 2400000.5
        lo = max(float(row["product_t_min_mjd"]) + 2400000.5, jd(row["conservative_start_utc"]), 2460998.5)
        hi = min(float(row["product_t_max_mjd"]) + 2400000.5, jd(row["conservative_end_utc"]))
        for epoch in range(math.ceil((lo - eph.t0_bjd_tdb) / eph.period_days),
                           math.floor((hi - eph.t0_bjd_tdb) / eph.period_days) + 1):
            ident = f"{planet}|S{row['sector']}|DRD{epoch}"
            expected[ident] = (planet, epoch, row["product_obs_id"])
            expected_count[planet] += 1
    events = rows("results/sprint2/freeze_candidate/events_drd.csv")
    roster = rows("results/sprint2/freeze_candidate/roster.csv")
    forecasts = rows("results/sprint2/freeze_candidate/forecasts_drd_draft.csv.gz")
    cov = {(r["release"], r["planet"]): r for r in rows("results/pilot_v1/covariance_completeness.csv")}
    params_path = "results/sprint2/forecasts/candidate_parameters_t015v3.json"
    params = obj(params_path)
    event_lookup = {r["event_id"]: r for r in events}
    failures = []
    for row in events:
        ident, epoch, planet = row["event_id"], int(row["forecast_epoch"]), row["planet"]
        eph = drd[planet]
        if expected.get(ident) != (planet, epoch, row["product_obs_id"]):
            failures.append(f"event source identity: {ident}")
        if abs(float(row["drd_predicted_bjd_tdb"]) - eph.t0_bjd_tdb - epoch * eph.period_days) > 0.000000501:
            failures.append(f"event prediction: {ident}")
    for row in forecasts:
        ident, planet, epoch = row["event_id"], row["planet"], int(row["forecast_epoch"])
        eph, covariance = drd[planet], cov["DRD", planet]
        rho = float(covariance["corr_t0_p_at_published_epoch"])
        vf = (eph.sigma_t0_days * 86400) ** 2 + 2 * epoch * rho * eph.sigma_t0_days * eph.sigma_period_days * 86400**2
        vf += (epoch * eph.sigma_period_days * 86400) ** 2
        if (ident not in event_lookup or epoch != int(event_lookup[ident]["forecast_epoch"])
                or abs(float(row["rho"]) - rho) > 1e-12):
            failures.append(f"forecast source identity: {ident}")
        if abs(float(row["predicted_bjd_tdb"]) - eph.t0_bjd_tdb - epoch * eph.period_days) > 1e-8:
            failures.append(f"forecast prediction: {ident}")
        if not math.isclose(float(row["forecast_variance_s2"]), vf, rel_tol=1e-12):
            failures.append(f"forecast variance: {ident}")
        if row["parameter_version"] != sha(ROOT / params_path):
            failures.append(f"parameter hash: {ident}")
        for model, fit in params["models"].items():
            for field in ("b", "s_log_lambda"):
                if float(row[f"{model}_{field}"]) != fit[field]:
                    failures.append(f"parameter value: {ident} {model} {field}")
    for row in roster:
        if int(row["opps_manifest"]) != expected_count[row["planet"]] or row["opps_manifest"] != row["opps_inventory"]:
            failures.append(f"roster count: {row['planet']}")

    outcomes_data = gzip.decompress(safe_bytes(ROOT / "results/outcomes/t015v3/outcomes.csv.gz"))
    outcomes = list(csv.DictReader(io.StringIO(outcomes_data.decode())))
    matched = [r for r in outcomes if r["status"] == "timed" and r.get("exoclock_delta_s")]
    paired_z2 = [(float(r["exoclock_delta_s"]) / math.hypot(float(r["sigma_s"]), float(r["exoclock_sigma_s"]))) ** 2
                 for r in matched]
    identities = defaultdict(set)
    for sample in ("dev", "confirm", "confirm2"):
        for row in rows(f"results/sprint2/{sample}/products.csv"):
            if row.get("sha256"):
                identities[row["file"]].add(row["sha256"])
    for row in outcomes:
        if row.get("file_sha256"):
            identities[row["file"]].add(row["file_sha256"])
    inconsistent = {name: sorted(values) for name, values in identities.items() if len(values) > 1}
    summary = obj("results/sprint2/freeze_candidate/roster_summary.json")
    access = obj("results/sprint2/freeze_candidate/access_receipt.json")
    interface_dir = ROOT / "data/derived/sprint2/interface"
    interface_receipts = [str(p.relative_to(ROOT)) for p in interface_dir.glob("*receipt*.json")]
    late_receipt_path = ROOT / "results/sprint2/interface/scores.receipt.json"
    late_receipt = None
    if late_receipt_path.is_file():
        receipt = json.loads(git("show", "07b5cf4:results/sprint2/interface/scores.receipt.json"))
        frozen_adapter_sha = hashlib.sha256(git("show", "07b5cf4:scripts/sprint1_outcome_adapter.py")).hexdigest()
        repaired_adapter_sha = hashlib.sha256(git("show", "d9c1570:scripts/sprint1_outcome_adapter.py")).hexdigest()
        late_receipt = {k: v for k, v in receipt.items() if not isinstance(v, (list, dict))}
        late_receipt.update(adapter_sha_at_receipt_commit=frozen_adapter_sha,
                            adapter_sha_at_later_repair_commit=repaired_adapter_sha,
                            recorded_adapter_sha_matches_receipt_commit=receipt["adapter_source_sha256"] == frozen_adapter_sha,
                            recorded_adapter_sha_matches_later_repair=receipt["adapter_source_sha256"] == repaired_adapter_sha,
                            qualification="Receipt hashes adapter file at run end; this does not identify imported code if the source changes during the run.")
    result = {
        "audited_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "head": git("rev-parse", "HEAD").decode().strip(), "baseline": BASELINE,
        "photometry_opened_by_this_audit": False,
        "handoff": {"outputs": len(checks), "hash_failures": [r["path"] for r in checks if not r["matches"]],
                    "script_hash_matches": hashlib.sha256(git("show", f"{BASELINE}:scripts/sprint2_handoff.py")).hexdigest() == handoff["handoff_script_sha256"]},
        "osf_source_files": {"count": len(source_checks), "hash_failures": [r["path"] for r in source_checks if not r["matches"]]},
        "source_chronology": chronology, "recorded_rule_receipts": rule_receipts,
        "frozen_confirmation_source_matches_recorded_prefix": all(frozen_source.startswith(rule_receipts[s]["rule_version"].split("+")[1])
                                                                  for s in ("confirm", "confirm2")),
        "chronology_limits": ["Run receipts lack start/end or download timestamps; logs are undated.",
                              "Dev run records 66a91f709666 at dc5d2b8, but sprint2_outcomes.py was not committed at that revision.",
                              "Replication document discloses prior R5 contact with 82 hosts; never-sampled means injection frame, not untouched photometry."],
        "candidate": {"roster_planets": len(roster), "hosts": len({r['host'] for r in roster}),
                      "cohort_counts": dict(Counter(r["cohort"] for r in roster)), "events": len(events),
                      "forecasts": len(forecasts), "unique_planet_epochs": len({(r['planet'], r['forecast_epoch']) for r in events}),
                      "independent_inventory_events": sum(expected_count.values()), "invariant_failures": failures,
                      "inventory_hash_matches": sha(ROOT / "results/sprint1/inventory/planet_sector_product_inventory.csv") == summary["inventory_sha256"],
                      "covariance_tiers": dict(Counter(r["covariance_tier"] for r in forecasts)),
                      "events_within_10min_of_unconverted_anchor": [r["event_id"] for r in events if abs(float(r["drd_predicted_bjd_tdb"]) - 2460998.5) < 10 / 1440],
                      "covariance_qualification": "WLS reconstruction from assumed release input sets; C2_candidate is not an issued covariance.",
                      "candidate_host_refit_parameter_sets": len(params["host_refit_parameter_sets"])},
        "outcome_table": {"attempts": len(outcomes), "statuses": dict(Counter(r["status"] for r in outcomes)),
                          "uncompressed_sha256": hashlib.sha256(outcomes_data).hexdigest(),
                          "candidate_source_hash_matches": hashlib.sha256(outcomes_data).hexdigest() == params["outcomes_sha256"],
                          "timed_planets": len({r["planet"] for r in outcomes if r["status"] == "timed"}),
                          "same_photon_pairs": len(matched),
                          "median_delta_s": statistics.median(float(r["exoclock_delta_s"]) for r in matched),
                          "same_photon_z_rms": math.sqrt(statistics.mean(paired_z2)),
                          "median_raw_sigma_ratio": statistics.median(float(r["sigma_s"]) / float(r["exoclock_sigma_s"]) for r in matched)},
        "recorded_photometry_identities": {"distinct_files": len(identities), "conflicting_hashes": inconsistent,
                                          "raw_FITS_hashes_independently_recomputed": False},
        "recorded_access_receipt": access,
        "access_conclusion": "Receipt reports no protected files in its scanned directory at its timestamp; historical/global non-access is not proved.",
        "production_interface_receipts_present": interface_receipts,
        "late_production_interface_receipt": late_receipt,
        "brief_render_proof": [str(p.relative_to(ROOT)) for base in ("docs", "manuscript", "results")
                               for p in (ROOT / base).rglob("*brief*") if p.suffix.lower() in (".pdf", ".docx", ".png")],
    }
    (OUT / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"handoff": result["handoff"], "sources": result["osf_source_files"],
                      "candidate_failures": failures, "identity_conflicts": len(inconsistent),
                      "interface_receipts": interface_receipts}, indent=2))


if __name__ == "__main__":
    main()
