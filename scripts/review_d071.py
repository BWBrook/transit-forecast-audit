"""Audit saved C050 outputs and candidate-block metadata without opening flux."""

import csv
import gzip
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
from sealed_era_inventory import coordinates
from transit_audit.exoclock import host_of, read_catalogue

OUT = ROOT / "results/d071_review"
INPUTS = {}


def record(path):
    path = ROOT / path
    INPUTS[str(path.relative_to(ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return path


def rows(path):
    p = record(path)
    with (gzip.open(p, "rt") if p.suffix == ".gz" else p.open()) as stream:
        return list(csv.DictReader(stream))


def write_json(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def c050_check():
    source = json.loads(record("results/independent_validation/hr858/summary.json").read_text())
    reference_table = {"b": (2458409.1900, 3.585287), "c": (2458415.63344, 5.973865),
                       "d": (2458409.7324, 11.230511)}
    references_match = all(
        abs(source["config"]["planets"][name]["reference_ephemeris"]["t0_bjd_tdb"] - values[0]) < 1e-9
        and abs(source["config"]["planets"][name]["reference_ephemeris"]["period_d"] - values[1]) < 1e-12
        for name, values in reference_table.items())
    assert references_match, "C050 reference configuration differs from the checked Table 2 transcription"
    frozen = [r for r in rows("results/final_primary/accepted_outcomes.csv") if r["planet"] == "HR858b"]
    forecast = {r["event_id"]: r for r in rows("results/final_primary/accepted_forecasts.csv")}
    terminal = [r for r in rows("results/final_primary/terminal_ledger.csv.gz") if r["planet"] == "HR858b"]
    routes = {}
    for column, route in source["routes"].items():
        planets = {}
        for name, data in route["planets"].items():
            ref = source["config"]["planets"][name]["reference_ephemeris"]
            times = np.array([r["tc_bjd_tdb"] for r in data["transits"]])
            epochs = np.rint((times - ref["t0_bjd_tdb"]) / ref["period_d"])
            residual = (times - ref["t0_bjd_tdb"] - epochs * ref["period_d"]) * 1440
            # Centering avoids loss of precision from fitting large Julian dates.
            n = epochs - epochs.mean()
            local_period = float(np.dot(n, times - times.mean()) / np.dot(n, n))
            planets[name] = {"events": len(times), "reference_residual_min_range": [float(residual.min()), float(residual.max())],
                             "unweighted_local_period_d": local_period,
                             "reference_period_d": ref["period_d"],
                             "local_minus_reference_period_min": (local_period - ref["period_d"]) * 1440}
        independent = source["routes"][column]["planets"]["b"]["transits"]
        matched = []
        used = set()
        for f in frozen:
            j = min(range(len(independent)), key=lambda k: abs(independent[k]["tc_bjd_tdb"] - float(f["tc_bjd_tdb"])))
            assert j not in used
            used.add(j)
            delta = (independent[j]["tc_bjd_tdb"] - float(f["tc_bjd_tdb"])) * 1440
            assert abs(delta) < 60
            matched.append(delta)
        extras = []
        for j, event in enumerate(independent):
            if j in used:
                continue
            nearest = min(terminal, key=lambda r: abs(float(r["drd_predicted_bjd_tdb"]) - event["tc_bjd_tdb"]))
            extras.append({"tc_bjd": event["tc_bjd_tdb"], "terminal_event_id": nearest["event_id"],
                           "terminal_status": nearest["status"], "coverage_at_prediction": nearest["coverage_ok_at_prediction"]})
        routes[column] = {"planets": planets, "frozen_matches": len(matched),
                          "signed_median_difference_min": float(np.median(matched)),
                          "median_absolute_difference_min": float(np.median(np.abs(matched))),
                          "maximum_absolute_difference_min": float(np.max(np.abs(matched))),
                          "extra_independent_events": extras}
    metadata = [{key: r.get(key) for key in ("sector", "file", "file_sha256", "timesys", "timeref", "bjdrefi", "bjdreff")}
                for r in {r["file"]: r for r in frozen}.values()]
    return {"routes": routes, "saved_SPOC_header_metadata": metadata,
            "reference_values_match_Bonfanti_table2": references_match,
            "reference_source": "https://arxiv.org/pdf/2411.14911#page=6",
            "reference_time_standard_limit": "Table labels BJD, not an explicitly verified TDB standard; no conversion made. Numerical hours-scale departures are descriptive, not a new time-system validation.",
            "interpretation": "Different implementations on shared SPOC photons support a coherent departure. Opposite signs/slopes and an approximately on-time d disfavor a simple common additive shift; they are not a unique dynamical explanation or a pixel/blend exclusion.",
            "comparison_uncertainty_limit": "The two timing estimates share photons; quadrature-combined errors do not calibrate independent residuals."}


def single_sector_spoc120(row):
    sector = row.get("sequence_number")
    if not sector or not 74 <= int(sector) <= 97:
        return False
    if row.get("provenance_name") != "SPOC" or float(row.get("t_exptime") or 0) != 120:
        return False
    if str(row.get("dataRights", "")).upper() != "PUBLIC" or row.get("t_min") is None or row.get("t_max") is None:
        return False
    single = re.search(r"-s(\d{4})-\d{16}-\d+-s_lc\.fits$", str(row.get("dataURL", "")))
    return row.get("dataproduct_type") == "timeseries" and single is not None and int(single[1]) == int(sector)


def raw_filename_identity(name):
    spoc = re.search(r"-s(\d{4})-(\d{16})-", name)
    if spoc:
        return int(spoc[1]), str(int(spoc[2]))
    ffi = re.search(r"tess_phot_(\d+)-s(\d{4})_", name)
    return (int(ffi[2]), str(int(ffi[1]))) if ffi else None


def candidate_inventory():
    drd = read_catalogue(record("data/raw/osf/wpjtn/catalogue_of_ephemerides.txt"))
    drc = read_catalogue(record("data/raw/osf/p298n/catalogue_of_ephemerides.txt"))
    for name in ("pscomppars.csv", "toi.csv"):
        record(f"data/raw/exoplanet_archive/{name}")
    coords = coordinates(sorted(drd))
    metadata = []
    for p in sorted((ROOT / "data/raw/sprint1_metadata").glob("mast_caom_filtered_*.json")):
        if p.name.endswith(".receipt.json"):
            continue
        metadata.extend(json.loads(record(p.relative_to(ROOT)).read_text())["data"])
    products = (rows("data/derived/final_primary/measured/products.csv")
                + rows("data/derived/final_extension/measured/products.csv"))
    manifests = rows("results/prefreeze/manifest_core_primary.csv") + rows("results/prefreeze/manifest_extension_exploratory.csv")
    manifest_planets = {r["planet"] for r in manifests}
    manifest_hosts = {r.get("host") or host_of(r["planet"]) for r in manifests}
    evaluated_hosts = {r["host"] for r in products}
    evaluated_tics = {str(r["tic"]).removeprefix("TIC ").strip() for r in products}
    raw_names = sorted(str(p.relative_to(ROOT)) for p in (ROOT / "data/raw").rglob("*.fits"))
    raw_tics, sector_counts, unparsed = set(), Counter(), []
    for name in raw_names:
        identity = raw_filename_identity(name)
        if identity:
            sector, tic = identity
            sector_counts[sector] += 1
            raw_tics.add(tic)
        else:
            unparsed.append(name)
    by_tic = defaultdict(dict)
    for r in metadata:
        if not single_sector_spoc120(r):
            continue
        by_tic[str(r["target_name"])][str(r["obs_id"])] = r
    flags = rows("data/fixtures/exoclock_ttv_flags.csv")
    flagged = {release: {r["planet"] for r in flags if r["flag_release"] == release} for release in ("DRC", "DRD")}
    by_host = {release: Counter(host_of(p) for p in cat) for release, cat in (("DRC", drc), ("DRD", drd))}
    inventory = []
    for planet, e in sorted(drd.items()):
        c = coords.get(planet)
        if c is None or not c[2]:
            continue
        tic = c[2].removeprefix("TIC ").strip()
        host = host_of(planet)
        tmag = float(c[3]) if c[3] else None
        for obs in sorted(by_tic.get(tic, {}).values(), key=lambda r: (int(r["sequence_number"]), str(r["obs_id"]))):
            # Coarse interior counts only; MAST UTC metadata is not converted to BJD_TDB.
            lo, hi = float(obs["t_min"]) + 2400000.5 + 1, float(obs["t_max"]) + 2400000.5 - 1
            n0, n1 = int(np.ceil((lo - e.t0_bjd_tdb) / e.period_days)), int(np.floor((hi - e.t0_bjd_tdb) / e.period_days))
            inventory.append({"planet": planet, "host": host, "tic": tic, "sector": int(obs["sequence_number"]),
                              "obs_id": obs["obs_id"], "metadata_start_mjd_utc": obs["t_min"], "metadata_end_mjd_utc": obs["t_max"],
                              "DRD_coarse_interior_opportunities": max(n1 - n0 + 1, 0),
                              "attempted_2026_host_or_tic": host in evaluated_hosts or tic in evaluated_tics,
                              "local_raw_TIC_present_before_T017": tic in raw_tics,
                              "DRC_forecast_exists": planet in drc,
                              "DRD_core_metadata": tmag is not None and tmag < 13.5 and e.period_days <= 12 and by_host["DRD"][host] == 1 and planet not in flagged["DRD"],
                              "DRC_core_metadata": planet in drc and tmag is not None and tmag < 13.5 and drc[planet].period_days <= 12 and by_host["DRC"][host] == 1 and planet not in flagged["DRC"],
                              "coordinate_basis": c[4]})
    if inventory:
        with (OUT / "s74_s97_metadata_candidates.csv").open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(inventory[0])); writer.writeheader(); writer.writerows(inventory)
    def counts(predicate):
        selected = [r for r in inventory if predicate(r)]
        return {"planets": len({r["planet"] for r in selected}), "hosts": len({r["host"] for r in selected}),
                "planet_products": len(selected), "coarse_opportunities": sum(r["DRD_coarse_interior_opportunities"] for r in selected)}
    return {"recorded_2026_attempted_planets": len({r["planet"] for r in products}), "recorded_2026_attempted_hosts": len(evaluated_hosts),
            "current_roster_never_attempted_2026_hosts": len(manifest_hosts - evaluated_hosts),
            "current_roster_unattempted_host_names": sorted(manifest_hosts - evaluated_hosts),
            "current_roster_unattempted_planet_names": sorted(manifest_planets - {r["planet"] for r in products}),
            "project_raw_filename_sector_counts": dict(sorted(sector_counts.items())), "unparsed_raw_filenames": unparsed,
            "raw_filenames_in_candidate_sectors": sum(n for s, n in sector_counts.items() if 74 <= s <= 97),
            "all_saved_SPOC120_metadata_candidates": counts(lambda r: True),
            "not_2026_attempted": counts(lambda r: not r["attempted_2026_host_or_tic"]),
            "not_local_raw_cached": counts(lambda r: not r["local_raw_TIC_present_before_T017"]),
            "DRC_core_not_2026_attempted": counts(lambda r: r["DRC_core_metadata"] and not r["attempted_2026_host_or_tic"]),
            "DRC_core_not_raw_cached": counts(lambda r: r["DRC_core_metadata"] and not r["local_raw_TIC_present_before_T017"]),
            "single_sector_light_curve_filter": "SPOC120 timeseries with single-sector -sNNNN-ID-processing-s_lc.fits URL; combined-sector validation products excluded",
            "limits": ["Saved MAST product metadata only: no flux, headers or downloads requested.",
                       "No local filename does not prove that no agent ever opened a now-absent file.",
                       "New metadata candidates are not a qualified cohort, power calculation or access authority.",
                       "Coarse DRD event counts use one-day interiors without time-system conversion or cadence/gap checks; DRC needs its own exact manifest.",
                       "No-cache classification is a conservative lead, not a complete audit of past development/injection/scoring host reuse."]}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {"C050": c050_check(), "candidate_block": candidate_inventory(), "new_photometry_or_headers_opened": False,
              "new_downloads": False, "protected_sector_access_authorised": False}
    report["input_sha256"] = INPUTS
    report["script_sha256"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    write_json("audit.json", report)
    print(json.dumps({k: v for k, v in report["candidate_block"].items() if k not in ("project_raw_filename_sector_counts", "unparsed_raw_filenames", "limits")}))


if __name__ == "__main__":
    main()
