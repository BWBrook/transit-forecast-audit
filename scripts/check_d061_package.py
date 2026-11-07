"""Focused D061 artifact check; saved development tables/grids, no photometry.

Run prefreeze_evidence.py separately to reproduce the full eight-criterion
calibration result. This command verifies its support inputs and final-path
receipts without repeating the expensive measurement or 200-draw exercise.
"""

from __future__ import annotations

import ast
import csv
import gzip
import hashlib
import json
import sys
import subprocess
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import final_evaluation as final
from sprint1_outcome_adapter import likelihood_grid


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def rows(path):
    with gzip.open(path, "rt") as fh:
        return list(csv.DictReader(fh))


def main():
    base = ROOT / "results/prefreeze"
    replay_path = base / "replay/replay_receipt.json"
    replay = read(replay_path)
    combined = (ROOT / "scripts/sprint2_outcomes.py").read_bytes() + (ROOT / "scripts/t015_timing_pipeline.py").read_bytes()
    assert hashlib.sha256(combined).hexdigest() == replay["timing_source_sha256"]
    assert sha(ROOT / "scripts/acceptance.py") == replay["acceptance_sha256"]
    assert sha(ROOT / "scripts/prefreeze_replay.py") == replay["replay_sha256"]
    evidence_path = base / "injection_evidence_t015v3a.json"
    evidence = read(evidence_path)
    support = {}
    inputs = [replay_path, evidence_path]
    for sample in ("confirm", "confirm2"):
        lp = base / "replay" / sample / "ledger.csv.gz"
        assert sha(lp) == replay["samples"][sample]["ledger_sha256"]
        ledger = rows(lp)
        paths = [r["posterior_grid_path"] for r in ledger if r.get("grid_sha256")]
        assert len(set(paths)) == len(paths)
        counts = Counter()
        for row in ledger:
            if not row.get("grid_sha256"):
                continue
            path = ROOT / row["posterior_grid_path"]
            assert sha(path) == row["grid_sha256"]
            try:
                likelihood_grid(path)
                state = "True"
            except ValueError:
                state = "False"
            assert state == row["support_ok"]
            counts[state] += 1
        assert dict(counts) == replay["samples"][sample]["nonGaussian_support"]
        actual = evidence["samples"][sample]["actual_support"]
        assert actual["verdict"]["pass"] and len(actual["verdict"]["checks"]) == 8
        support[sample] = {"checked_grids": len(paths), "support": dict(counts),
                           "hosts": actual["hosts"], "accepted_injections": actual["events"],
                           "coverage_ci90": actual["cover95_ci90"], "all_eight_pass": True}
        inputs.append(lp)
    run = base / "final_path_dev/run"
    summary_path = run / "evaluation_summary.json"
    summary = read(summary_path)
    guard_repair = {}
    for filename, expected in summary["code_sha256"].items():
        path = ROOT / "scripts" / filename
        if sha(path) == expected:
            continue
        assert filename == "final_evaluation.py", filename
        old = subprocess.check_output(["git", "-C", str(ROOT), "show", "943ec42:scripts/final_evaluation.py"])
        assert hashlib.sha256(old).hexdigest() == expected
        def numerical_body(source):
            tree = ast.parse(source)
            tree.body = [node for node in tree.body if not
                         (isinstance(node, ast.FunctionDef) and node.name == "era_limit") and not
                         (isinstance(node, ast.ImportFrom) and node.module == "datetime")]
            return ast.dump(tree, include_attributes=False)
        assert numerical_body(old) == numerical_body(path.read_bytes())
        guard_repair = {"file": filename, "saved_run_sha256": expected, "current_sha256": sha(path),
                        "numerical_body_ast_unchanged": True}
    assert sha(ROOT / "configs/candidate_freeze.json") == summary["config_sha256"]
    mapping = {"manifest": base / "final_path_dev/manifest.csv", "forecasts": base / "final_path_dev/forecasts.csv",
               "windows": ROOT / "results/outcomes/t015v3/outcomes.csv.gz",
               "products": ROOT / "results/outcomes/t015v3/product_identification.csv",
               "coverage": base / "final_path_dev/coverage.csv", "parameters": base / "candidate_models_core_matched.json"}
    for name, path in mapping.items():
        assert sha(path) == summary["input_sha256"][name], name
    for filename, key in (("joint_draws.json.gz", "joint_draws_sha256"), ("terminal_ledger.csv.gz", "terminal_ledger_sha256"),
                          ("scores.receipt.json", "adapter_receipt_sha256")):
        assert sha(run / filename) == summary[key]
    ledger = rows(run / "terminal_ledger.csv.gz")
    assert len({r["event_id"] for r in ledger}) == len(ledger) == summary["manifest_events"]
    assert dict(Counter(r["status"] for r in ledger)) == summary["terminal_status_counts"]
    with gzip.open(run / "joint_draws.json.gz", "rt") as fh:
        joint = json.load(fh)
    assert len(joint["hosts"]) == summary["joint_hosts_union"] and len(joint["draws"]) == summary["joint_bootstrap"]
    for draw in joint["draws"]:
        assert len(draw["multiplicity"]) == len(joint["hosts"])
        assert sum(draw["multiplicity"]) == len(joint["hosts"])
        assert np.isfinite(draw["paired_delta_M2_M0"])
    assert np.allclose(np.quantile([d["paired_delta_M2_M0"] for d in joint["draws"]], [.025, .975]),
                       summary["joint_refit_ci95"], atol=1e-12, rtol=0)
    chain_path = base / "final_chain_check.json"
    chain = read(chain_path)
    assert sha(ROOT / "scripts/final_measure.py") == chain["measure_receipt"]["measure_sha256"]
    assert not final.ACCESS.exists()
    try:
        final.era_limit("protected")
    except SystemExit:
        pass
    else:
        raise AssertionError("protected era did not refuse")
    inputs += [summary_path, run / "joint_draws.json.gz", run / "terminal_ledger.csv.gz", chain_path,
               ROOT / "configs/candidate_freeze.json", *mapping.values()]
    result = {"photometry_or_headers_opened": False, "protected_data_accessed": False,
              "actual_support": support, "saved_run_inputs_config_and_numerical_source_match": True,
              "post_run_access_guard_repair": guard_repair,
              "private_adapter_receipt_hash_matches": True,
              "manifest_events": len(ledger), "accepted_events": summary["accepted_events"],
              "joint_hosts": len(joint["hosts"]), "joint_draws": len(joint["draws"]), "joint_interval_reproduced": True,
              "chain_measure_source_matches": True, "protected_era_refused": True,
              "limits": "Saved development/synthetic execution only; hindcast scores are not forecast-validation results. Not a freeze or protected-access authorisation.",
              "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs}}
    dest = ROOT / "results/sprint2_review/d061/package_check.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"support": support, "saved_run_verified": True, "protected_era_refused": True}))


if __name__ == "__main__":
    main()
