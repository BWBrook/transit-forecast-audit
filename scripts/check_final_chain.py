"""End-to-end development check of the final chain: final_measure -> final_evaluation evaluate (D060).

Takes a deterministic subset of the development exercise manifest (every k-th
host), measures it from the cached development light curves with the
manifest-driven command, compares the measurement with the saved development
outcomes and attempt-ledger coverage, then runs the frozen evaluate command on
the measured files. Development era only; the hindcast has no inferential content.

    .venv/bin/python scripts/check_final_chain.py [--every 12] [--bootstrap 10]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import final_evaluation as fe  # noqa: E402

DEV = ROOT / "results" / "prefreeze" / "final_path_dev"
WORK = ROOT / "data" / "derived" / "final_chain_dev"
OUT = ROOT / "results" / "prefreeze" / "final_chain_check.json"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--every", type=int, default=12)
    ap.add_argument("--bootstrap", type=int, default=10)
    a = ap.parse_args()
    WORK.mkdir(parents=True, exist_ok=True)
    man = fe.read_csv(DEV / "manifest.csv")
    hosts = sorted({m["host"] for m in man})[::a.every]
    sub = [m for m in man if m["host"] in hosts]
    fe.write_csv(WORK / "manifest.csv", sub)
    ids = {m["event_id"] for m in sub}
    fe.write_csv(WORK / "forecasts.csv", [f for f in fe.read_csv(DEV / "forecasts.csv") if f["event_id"] in ids])
    subprocess.run(["uv", "run", "-q", str(HERE / "final_measure.py"), "--manifest", str(WORK / "manifest.csv"),
                    "--out", str(WORK / "measured"), "--product-meta", str(ROOT / "results/outcomes/t015v3/products.csv"),
                    "--era", "development", "--workers", "4"], check=True)
    meas = fe.read_csv(WORK / "measured" / "windows.csv.gz")
    saved = {(r["planet"], str(int(float(r["sector"]))), r["drd_epoch"]): r
             for r in fe.read_csv(ROOT / "results/outcomes/t015v3/outcomes.csv.gz") if r["product"] == "SPOC_120"}
    same_status, dtc, dsig, statuses = 0, [], [], []
    for r in meas:
        s = saved.get((r["planet"], str(int(float(r["sector"]))), r["drd_epoch"]))
        if s is None:
            statuses.append(("new", r["status"]))
            continue
        same_status += s["status"] == r["status"]
        if s["status"] != r["status"]:
            statuses.append((s["status"], r["status"]))
        if s["status"] == r["status"] == "timed":
            dtc.append(abs(float(s["tc_bjd_tdb"]) - float(r["tc_bjd_tdb"])) * 86400)
            dsig.append(abs(float(s["sigma_s"]) - float(r["sigma_s"])))
    att = {r["event_id"]: r for r in fe.read_csv(ROOT / "results/prefreeze/attempt_ledger_development.csv.gz")}
    cov = fe.read_csv(WORK / "measured" / "coverage.csv")
    dcov = [max(abs(float(c["coverage_window_at_prediction"]) - float(att[c["event_id"]]["coverage_window_at_prediction"])),
                abs(float(c["coverage_in_transit_at_prediction"]) - float(att[c["event_id"]]["coverage_in_transit_at_prediction"])))
            for c in cov if c["coverage_window_at_prediction"] != ""]
    ns = argparse.Namespace(manifest=str(WORK / "manifest.csv"), forecasts=str(WORK / "forecasts.csv"),
                            windows=str(WORK / "measured" / "windows.csv.gz"),
                            products=str(WORK / "measured" / "products.csv"), coverage=str(WORK / "measured" / "coverage.csv"),
                            parameters=str(ROOT / "results/prefreeze/candidate_models_core_matched.json"),
                            out=str(WORK / "evaluate"), era="development", bootstrap=a.bootstrap, conditional_bootstrap=1000,
                            workers=4, label="development chain check (hindcast; no inferential content)")
    summ = fe.evaluate(ns)
    res = {"hosts": len(hosts), "manifest_events": len(sub), "measured_windows": len(meas),
           "measure_receipt": json.loads((WORK / "measured" / "measure_receipt.json").read_text()),
           "vs_saved_development_outcomes": {
               "windows_matched_by_cycle": len(meas) - sum(1 for s in statuses if s[0] == "new"),
               "same_status": same_status, "status_changes": [list(s) for s in statuses],
               "timed_both": len(dtc), "max_abs_tc_diff_s": float(max(dtc, default=0)),
               "median_abs_tc_diff_s": float(np.median(dtc)) if dtc else 0.0,
               "max_abs_sigma_diff_s": float(max(dsig, default=0)),
               "note": "saved development outcomes identified with the earliest release period (DRC first); "
                       "the final command uses the issued DRD period, so small differences are expected"},
           "coverage_vs_attempt_ledger_max_abs_diff": float(max(dcov, default=0)),
           "evaluate": {k: summ[k] for k in ("manifest_events", "terminal_status_counts", "accepted_events",
                                             "nonGaussian_scored", "adapter_reproduction_max_abs_diff",
                                             "calibration_refit_max_abs_diff", "draw_scoring", "joint_refit_ci95",
                                             "decision", "label")}}
    OUT.write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: res[k] for k in ("hosts", "manifest_events", "vs_saved_development_outcomes",
                                          "coverage_vs_attempt_ledger_max_abs_diff")}, indent=1))


if __name__ == "__main__":
    main()
