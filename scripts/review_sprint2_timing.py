"""Audit existing development tables and synthetic timing profiles without opening photometry."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint2_outcomes as so
import t015_timing_pipeline as tp
from transit_audit.exoclock import read_catalogue


def read_rows(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt") as handle:
        return list(csv.DictReader(handle))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def secondary_mode_control():
    """Synthetic chi profile, exercising the production integration algorithm."""
    class ProfileModel:
        def __init__(self, t, *args):
            self.n = len(t)

        def __call__(self, centre):
            x = centre * 86400
            chi = -2 * np.logaddexp(np.log(0.97) - 0.5 * (x / 20) ** 2,
                                   np.log(0.03) - 0.5 * ((x - 1800) / 20) ** 2)
            return np.full(self.n, np.sqrt(max(chi, 0) / self.n))

    t = np.linspace(-0.14, 0.14, 29)
    with patch.object(tp, "Model", ProfileModel), patch.object(
            np.linalg, "lstsq", return_value=(np.array([1.0, 0.0]), None, None, None)):
        profile = tp.time_transit(t, np.zeros(len(t)), np.ones(len(t)), 0.0, 3.0, {}, 0.15, 120)
    sol = {"wins": [(0, 0.0)], "half": 0.15, "t14": 0.05, "per": 3.0, "shape": {}}
    with patch.object(tp, "timed", return_value=(profile, profile, 1.0, 1.0, 1.0)):
        row = so.time_windows(t, np.zeros(len(t)), np.ones(len(t)), sol, 120, 0.01)[0]
    q, sig = profile["q"], profile["sig"]
    endpoints = np.exp(-0.5 * (profile["chi"][[0, -1]] - profile["chi"].min()))
    return {
        "synthetic": True, "specified_profile": "0.97*N(0,20^2)+0.03*N(1800,20^2), seconds",
        "mass_outside_fine": profile["mass_outside_fine"], "edge_mass": profile["edge_mass"],
        "fine_support_s": (profile["grid"][[0, -1]] * 86400).tolist(),
        "endpoint_relative_density": endpoints.tolist(),
        "quantile_gaussian_check_alone": bool(abs((q[2] - q[5]) / (1.959964 * sig) - 1) <= 0.1
                                              and abs((q[6] - q[2]) / (1.959964 * sig) - 1) <= 0.1),
        "flags": tp.flags(profile), "current_status": row["status"], "current_gauss_ok": row["gauss_ok"],
    }


def i1_audit(rows, products):
    timed = [r for r in rows if r["status"] == "timed"]
    groups = defaultdict(list)
    for row in rows:
        groups[row["shape_group_id"]].append(row)
    minority = []
    for group, rr in groups.items():
        covered = [r for r in rr if r["status"] in ("timed", "edge")]
        nt = sum(r["status"] == "timed" for r in covered)
        if nt and 2 * nt <= len(covered):
            minority.append({"shape_group_id": group, "timed": nt, "covered_windows": len(covered)})
    ratios = [abs(float(r["loo_shift_s"])) / float(r["sigma_s"]) for r in timed
              if r["loo_shift_s"] != "not_estimable"]
    numerical = [r for r in timed if set(r["flags"].split(";")) & {"mass_outside_fine", "coarse_fine_shift"}]
    grids = []
    for row in timed:
        if not row["posterior_grid_path"]:
            continue
        raw = json.loads((ROOT / row["posterior_grid_path"]).read_text())
        x, lg = np.asarray(raw["offset_s"]), np.asarray(raw["log_density"])
        q, _ = tp._quantiles(x, -2 * lg)
        density = np.exp(lg - lg.max())
        widths = np.r_[np.diff(x)[0] / 2, (x[2:] - x[:-2]) / 2, np.diff(x)[-1] / 2]
        mass = density * widths / np.sum(density * widths)
        grids.append({"event_id": row["event_id"], "sigma_difference_s": float((q[3] - q[1]) / 2 - float(row["sigma_s"])),
                      "endpoint_unresolved": bool(mass[0] + mass[-1] > 0.001 or max(density[0], density[-1]) > 0.001),
                      "integration_flag": bool(row["flags"]), "source_sha256": digest(ROOT / row["posterior_grid_path"])})
    drd = read_catalogue(so.DRD_CAT)["WASP-54b"]
    wasp = []
    for row in rows:
        if row["planet"] != "WASP-54b" or row["sector"] != "50":
            continue
        record = {k: row[k] for k in ("event_id", "status", "coverage_window", "coverage_in_transit", "sigma_s",
                                      "sigma_white_s", "beta", "rchi2", "gauss_ok", "loo_shift_s")}
        centre = float(row["window_centre_bjd_tdb"])
        predicted = drd.t0_bjd_tdb + int(row["drd_epoch"]) * drd.period_days
        record["window_minus_drd_prediction_hours"] = (centre - predicted) * 24
        wasp.append(record)
    return {
        "rows": len(rows), "status_counts": dict(Counter(r["status"] for r in rows)),
        "max_timed_bjd_tdb": max(float(r["tc_bjd_tdb"]) for r in timed),
        "duplicate_event_ids": len(rows) - len({r["event_id"] for r in rows}),
        "timed_with_integration_flags": len(numerical),
        "gaussian_with_integration_flags": [r["event_id"] for r in numerical if r["gauss_ok"] == "True"],
        "timed_without_loo": sum(r["loo_shift_s"] == "not_estimable" for r in timed),
        "absolute_loo_over_sigma_quantiles_50_90_95_99_100": np.quantile(ratios, [0.5, 0.9, 0.95, 0.99, 1.0]).tolist(),
        "absolute_loo_over_sigma_gt1": sum(v > 1 for v in ratios),
        "strict_majority_rule_diagnostic_only": minority,
        "wasp54_s50": wasp,
        "wasp54_product_identification": [r for r in products if r["planet"] == "WASP-54b"],
        "grid_count": len(grids), "endpoint_unresolved_grids": sum(g["endpoint_unresolved"] for g in grids),
        "integration_flagged_grids_passing_endpoint_gate": sum(g["integration_flag"] and not g["endpoint_unresolved"] for g in grids),
        "integration_flagged_grids_already_rejected_by_endpoint_gate": sum(g["integration_flag"] and g["endpoint_unresolved"] for g in grids),
        "max_grid_sigma_difference_s": max(abs(g["sigma_difference_s"]) for g in grids),
        "grid_audit": grids,
    }


def ledger_audit(sample):
    directory = ROOT / "results/sprint2" / sample
    ledger, runs = read_rows(directory / "ledger.csv.gz"), read_rows(directory / "runs.csv")
    byrun = defaultdict(list)
    for row in ledger:
        byrun[row["run_id"]].append(row)
    ids = [r["truth_id"] for r in ledger if r["truth_id"]]
    mismatches = []
    for run in runs:
        if not run.get("n_truths"):
            continue
        observed = sum(bool(r["truth_id"]) for r in byrun[run["run_id"]])
        if observed != int(run["n_truths"]):
            mismatches.append({"run_id": run["run_id"], "n_truths": int(run["n_truths"]), "ledger_truths": observed})
    return {"rows": len(ledger), "truths": len(ids), "duplicate_truth_ids": len(ids) - len(set(ids)),
            "status_counts": dict(Counter(r["status"] for r in ledger)), "run_n_truth_mismatches": mismatches,
            "matched_outside_gate": sum(bool(r.get("match_dist_s")) and float(r["match_dist_s"]) > float(r["gate_s"]) + 0.01 for r in ledger),
            "timed_but_truth_not_observable": sum(r["status"] == "timed" and r["observable"] != "True" for r in ledger)}


def main():
    paths = [ROOT / "data/derived/outcomes/t015v3/outcomes.csv",
             ROOT / "data/derived/outcomes/t015v3/product_identification.csv"]
    paths += [ROOT / f"results/sprint2/{s}/{f}" for s in ("dev", "confirm", "confirm2")
              for f in ("ledger.csv.gz", "runs.csv")]
    rows, products = read_rows(paths[0]), read_rows(paths[1])
    if max(float(r["tc_bjd_tdb"]) for r in rows if r.get("tc_bjd_tdb")) > tp.MAX_BTJD + 2457000:
        raise ValueError("Existing timing table extends beyond the development boundary")
    result = {"development_only": True, "photometry_opened": False, "new_data_acquired": False,
              "inputs": {str(p.relative_to(ROOT)): digest(p) for p in paths},
              "source_sha256": {name: digest(ROOT / "scripts" / name) for name in
                                ("sprint2_outcomes.py", "t015_timing_pipeline.py", "review_sprint2_timing.py")},
              "i1": i1_audit(rows, products), "ledgers": {s: ledger_audit(s) for s in ("dev", "confirm", "confirm2")},
              "secondary_mode_control": secondary_mode_control()}
    out = ROOT / "results/sprint2_review/timing"
    out.mkdir(parents=True, exist_ok=True)
    (out / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(out.relative_to(ROOT) / "audit.json"),
                      "timed_integration_flags": result["i1"]["timed_with_integration_flags"],
                      "secondary_mode_control": result["secondary_mode_control"]}, indent=2))


if __name__ == "__main__":
    main()
