"""Check D059 artifacts and the claim that all/none support scenarios are bounds.

Saved development tables and synthetic checks only; no photometry or headers.
The selective-support scenario is a diagnostic counterexample, never a proposed
acceptance rule or an assertion about the unknown actual support outcomes.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import acceptance as A
import prefreeze_package as pp
import sprint2_analysis as sa


def read_rows(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return list(csv.DictReader(fh))


def main():
    seed, bootstrap = 20261107, 10000
    paths = [ROOT / p for p in ("scripts/acceptance.py", "scripts/prefreeze_evidence.py",
             "scripts/prefreeze_attempts.py", "scripts/prefreeze_package.py", "configs/candidate_freeze.json")]
    results = {}
    for sample in ("confirm", "confirm2"):
        directory = ROOT / "results/sprint2" / sample
        lp, rp, pp_, np_ = [directory / p for p in ("ledger.csv.gz", "runs.csv", "products.csv", "real_transits.csv")]
        paths += [lp, rp, pp_, np_]
        runs = {r["run_id"]: r for r in read_rows(rp) if r.get("run_id")}
        products = {(r["host"], r.get("product")): r for r in read_rows(pp_)}
        certain, optional = [], []
        for row in read_rows(lp):
            if row["product"] != A.PRODUCT or row["mode"] != "remove" or not row.get("truth_id"):
                continue
            state = A.product_state(products.get((row["host"], row["product"])))
            if state == "ok":
                run = runs.get(row["run_id"], {})
                state = (A.product_state({"status": "ok", "shape_rchi2": run.get("shape_rchi2")})
                         if run.get("status", "").split(":")[0] == "ok" else "run_failed")
            state = A.event_state(row, check_support=False) if state == "ok" else state
            if state == A.ACCEPTED:
                certain.append(row)
            elif state == "likelihood_support_not_exported":
                optional.append(row)
        real = read_rows(np_)
        cases = {}
        selectors = {"all_missing_support_fail": [], "all_missing_support_pass": optional,
                     "diagnostic_partial_subset": [r for r in optional if r["cover95"] != "True"]}
        for name, selected in selectors.items():
            rows = certain + selected
            hosts = sa.Hosts([float(r["z"]) for r in rows], [r["cover95"] == "True" for r in rows],
                             [r["host"] for r in rows], [float(r["tmag"]) for r in rows])
            stats = sa.summarise(hosts, bootstrap, np.random.default_rng(seed))
            keys = {(r["host"], r["product"]) for r in rows}
            noise = sa.noise_control(rows, real, lambda r: (r["host"], r.get("product")) in keys)
            cases[name] = {k: stats[k] for k in ("hosts", "events", "z_rms", "z_rms_ci90",
                                                "cover95", "cover95_ci90", "mean_z", "mean_z_ci90")}
            cases[name]["verdict"] = sa.verdict(stats, noise)
            cases[name]["optional_accepted"] = len(selected)
        assert cases["all_missing_support_fail"]["verdict"]["pass"]
        assert cases["all_missing_support_pass"]["verdict"]["pass"]
        assert not cases["diagnostic_partial_subset"]["verdict"]["pass"]
        results[sample] = {"certain_events": len(certain), "unknown_support_events": len(optional), "cases": cases}

    outdir = ROOT / "results/prefreeze"
    ledger = read_rows(outdir / "attempt_ledger_development.csv.gz")
    summary = json.loads((outdir / "attempt_ledger_development.json").read_text())
    assert len({r["event_id"] for r in ledger}) == len(ledger) == 5425
    assert dict(Counter(r["status"] for r in ledger)) == summary["terminal_status_counts"]
    with gzip.open(outdir / "exercise_joint_draws.json.gz", "rt") as fh:
        joint = json.load(fh)
    exercise = json.loads((outdir / "evaluation_path_exercise.json").read_text())
    assert len(joint["hosts"]) == 270 and len(joint["draws"]) == 200
    for draw in joint["draws"]:
        assert len(draw["multiplicity"]) == 270 and sum(draw["multiplicity"]) == 270
        assert np.isfinite(draw["paired_delta_M2_M0"]) and np.isfinite(draw["fixed_parameter_delta"])
    for column, target in (("paired_delta_M2_M0", "joint_refit_ci95"), ("fixed_parameter_delta", "fixed_parameter_ci95")):
        assert np.allclose(np.quantile([r[column] for r in joint["draws"]], [.025, .975]), exercise[target], atol=1e-12, rtol=0)
    receipt = json.loads((outdir / "forecasts_draft_receipt.json").read_text())
    for name, label in (("manifest_core_primary", "core"), ("manifest_extension_exploratory", "extension")):
        with gzip.open(outdir / f"forecasts_{label}_draft.csv.gz", "rb") as fh:
            assert hashlib.sha256(fh.read()).hexdigest() == receipt[name]["sha256_csv"]
    rows, acceptance_counts = pp.gated_rows()
    assert acceptance_counts[A.ACCEPTED] == 3897 and acceptance_counts["likelihood_support_unresolved"] == 8
    missing_cert = A.accept({"status": "timed", "sigma_s": "60", "tc_bjd_tdb": "2460000",
                             "gauss_ok": "True"}, {"status": "ok", "shape_rchi2": "1"})
    assert missing_cert == A.ACCEPTED
    paths += [outdir / p for p in ("attempt_ledger_development.csv.gz", "attempt_ledger_development.json",
              "exercise_joint_draws.json.gz", "evaluation_path_exercise.json", "forecasts_draft_receipt.json")]
    result = {
        "protected_data_accessed": False, "photometry_or_headers_opened": False,
        "bootstrap": bootstrap, "seed": seed,
        "support_selection_cases": results,
        "interpretation": "All/none are sensitivity scenarios, not mathematical bounds over arbitrary unknown support subsets. Diagnostic subset uses coverage truth only to disprove the bound; actual support remains unknown.",
        "verified_repairs": {"acceptance_counts": acceptance_counts, "unique_attempt_events": len(ledger),
                             "joint_hosts": len(joint["hosts"]), "joint_draws": len(joint["draws"]),
                             "draw_intervals_match": True, "draft_forecast_hashes_match": True},
        "missing_gaussian_quantiles_counterexample_state": missing_cert,
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
    }
    dest = ROOT / "results/sprint2_review/d059/evidence_check.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    for sample, data in results.items():
        print(sample, {k: (v["events"], v["cover95_ci90"], v["verdict"]["pass"]) for k, v in data["cases"].items()})
    print("Saved ledger, joint draws and forecast hashes verify; missing Gaussian certification passes.")


if __name__ == "__main__":
    main()
