"""Verify D065 receipts, terminal accounting and the complete absolute-path rerun.

Saved metadata/windows/grids only. Does not reopen FITS files or repeat timing.
"""

import csv
import gzip
import hashlib
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import final_evaluation as fe
from reproduce_table5 import load


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rows(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return list(csv.DictReader(fh))


def main():
    fe.era_limit("protected")
    auth = ROOT / "configs/protected_access.json"
    committed = subprocess.check_output(["git", "-C", str(ROOT), "show", "b2f54de:configs/protected_access.json"])
    assert committed == auth.read_bytes()
    drd = load()[0]["DRD"]
    runs, inputs = {}, [auth, ROOT / "results/freeze/freeze_manifest.json"]
    for label, manifest_name in (("primary", "core_primary"), ("extension", "extension_exploratory")):
        base, measured = ROOT / f"results/final_{label}", ROOT / f"data/derived/final_{label}/measured"
        summary = json.loads((base / "evaluation_summary.json").read_text())
        paths = {"manifest": ROOT / f"results/prefreeze/manifest_{manifest_name}.csv",
                 "forecasts": ROOT / f"results/prefreeze/forecasts_{label if label == 'extension' else 'core'}_draft.csv.gz",
                 "windows": measured / "windows.csv.gz", "products": measured / "products.csv",
                 "coverage": measured / "coverage.csv", "parameters": ROOT / "results/prefreeze/candidate_models_core_matched.json"}
        for key, path in paths.items():
            assert sha(path) == summary["input_sha256"][key], (label, key)
        for name, expected in summary["code_sha256"].items():
            assert sha(ROOT / "scripts" / name) == expected, name
        assert sha(ROOT / "configs/candidate_freeze.json") == summary["config_sha256"]
        for name, key in (("joint_draws.json.gz", "joint_draws_sha256"), ("terminal_ledger.csv.gz", "terminal_ledger_sha256")):
            assert sha(base / name) == summary[key]
        portable = json.loads((base / "scores.receipt.portable.json").read_text())
        assert portable["portable_from_receipt_sha256"] == summary["adapter_receipt_sha256"]
        assert sha(base / "scores.csv") == portable["scores_sha256"]
        assert sha(base / "accepted_outcomes.csv") == portable["outcomes_sha256"]
        assert sha(base / "accepted_forecasts.csv") == portable["forecasts_sha256"]
        for name, expected in portable["likelihood_grid_hashes"].items():
            assert sha(ROOT / name) == expected, name
        man, windows, products = rows(paths["manifest"]), rows(paths["windows"]), rows(paths["products"])
        coverage = {r["event_id"]: r for r in rows(paths["coverage"])}
        assert len(coverage) == len(man) and set(coverage) == {r["event_id"] for r in man}
        pd = {(r["planet"], r["sector"]): r for r in products}
        terminal, outside = fe.terminal_ledger(man, windows, pd, coverage, drd)
        saved = rows(base / "terminal_ledger.csv.gz")
        assert len({r["event_id"] for r in saved}) == len(man)
        assert {r["event_id"]: r["status"] for r in saved} == {r["event_id"]: r["status"] for r in terminal}
        assert dict(Counter(r["status"] for r in saved)) == summary["terminal_status_counts"]
        accepted = {r["event_id"] for r in saved if r["status"] == "accepted"}
        for method in ("M0", "M1", "M2", "M3"):
            scored = [r for r in rows(base / "scores.csv") if r["method"] == method]
            assert len(scored) == len(accepted) and {r["event_id"] for r in scored} == accepted
        receipt = json.loads((measured / "measure_receipt.json").read_text())
        assert receipt["manifest_sha256"] == sha(paths["manifest"])
        assert receipt["measure_sha256"] == sha(ROOT / "scripts/final_measure.py")
        runs[label] = {"intended": len(man), "accepted": len(accepted), "windows": len(windows),
                       "outside_manifest_windows": len(outside), "grid_hashes_checked": len(portable["likelihood_grid_hashes"])}
        inputs += list(paths.values()) + [base / "evaluation_summary.json", base / "scores.receipt.portable.json",
                                         measured / "measure_receipt.json", base / "terminal_ledger.csv.gz"]
    first = ROOT / "data/derived/final_primary/measured_attempt1_relpath"
    rerun = ROOT / "data/derived/final_primary/measured"
    key = lambda r: (r["planet"], r["sector"], r["product_obs_id"])
    old = {key(r): r for r in rows(first / "products.csv")}
    new = {key(r): r for r in rows(rerun / "products.csv")}
    assert len(old) == len(new) == 304 and set(old) == set(new)
    complete = [k for k, r in old.items() if r["status"] == "ok" or r["status"].startswith("id_failed")]
    assert all(old[k] == new[k] for k in complete)
    a, b = rows(first / "windows.csv.gz"), rows(rerun / "windows.csv.gz")
    indexed = {r["event_id"]: r for r in b}
    assert all(r == indexed[r["event_id"]] for r in a)
    oldgrids = list((first / "grids").glob("*.json"))
    assert len(oldgrids) == 71
    assert all(sha(p) == sha(rerun / "grids" / p.name) for p in oldgrids)
    for name in ("measure_receipt.json", "products.csv", "windows.csv.gz", "coverage.csv"):
        inputs.append(first / name)
    commit_time = int(subprocess.check_output(["git", "-C", str(ROOT), "show", "-s", "--format=%ct", "b2f54de"]))
    birth = getattr((first / "measure.log").stat(), "st_birthtime", None)
    assert birth is None or birth >= commit_time
    output = {"frozen_package_and_record_verified": True, "protected_runs": runs,
              "retry": {"same_product_keys": len(old), "prior_completed_products_unchanged": len(complete),
                        "prior_windows_unchanged": len(a), "new_windows": len(b) - len(a), "prior_grids_unchanged": len(oldgrids)},
              "chronology": {"access_commit_epoch": commit_time, "first_log_birth_epoch": birth,
                             "limit": "Consistent saved Git/filesystem records, not an immutable invocation audit."},
              "interpretation": "Path failure depended on non-Gaussian likelihood output, not forecast score; full-manifest rerun restored every prior window without selection.",
              "raw_FITS_or_headers_reopened": False,
              "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(inputs))}}
    dest = ROOT / "results/final_review/provenance/audit.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(output, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"runs": runs, "retry": output["retry"]}))


if __name__ == "__main__":
    main()
