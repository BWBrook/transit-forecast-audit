"""Hash-bound freeze manifest for the DRD core evaluation (D062 handoff).

build   writes results/freeze/freeze_manifest.json: SHA-256 of every file the
        protected run and its qualification depend on (code, environment
        locks, config, event lists, parameters, forecasts, calibration and
        ephemeris inputs, the full injection evidence chain with grid hashes),
        plus binding checks that must hold (original and replay diagnostics
        equal, grid hashes match their ledger records, decompressed forecast
        content matches the forecast receipt).
verify  recomputes everything and reports mismatches; exits nonzero on any.
portable-receipt PATH  writes PATH with '.portable.json': adapter receipt with
        repository-relative paths and the original receipt's SHA-256.

final_evaluation.era_limit('protected') calls check_for_access(), which
requires the access record's freeze_manifest_sha256 to equal this manifest's
hash and verify() to pass, so an authorisation binds this exact package.

    .venv/bin/python scripts/freeze_manifest.py build|verify
    .venv/bin/python scripts/freeze_manifest.py portable-receipt results/.../scores.receipt.json
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
MANIFEST = ROOT / "results" / "freeze" / "freeze_manifest.json"

CODE = ["scripts/acceptance.py", "scripts/final_measure.py", "scripts/final_evaluation.py",
        "scripts/freeze_manifest.py", "scripts/sprint1_outcome_adapter.py", "scripts/sprint1_forecast_core.py",
        "scripts/forecast_variance_components.py", "scripts/sprint1_forecasts.py", "scripts/prefreeze_package.py",
        "scripts/review_measurement_diagnostic.py", "scripts/sealed_era_inventory.py",
        "scripts/sprint2_forecasts.py", "scripts/sprint2_outcomes.py", "scripts/sprint2_remeasure.py",
        "scripts/t015_timing_pipeline.py", "scripts/reproduce_table5.py", "src/transit_audit/__init__.py",
        "src/transit_audit/ephemeris.py", "src/transit_audit/exoclock.py", "src/transit_audit/provenance.py",
        "src/transit_audit/scoring.py"]
ENVIRONMENT = ["pyproject.toml", "uv.lock", "scripts/final_measure.py.lock", "scripts/prefreeze_replay.py.lock"]
CONFIG = ["configs/candidate_freeze.json", "configs/sprint1.json"]
LISTS = ["results/prefreeze/manifest_core_primary.csv", "results/prefreeze/manifest_extension_exploratory.csv",
         "results/prefreeze/manifest_boundary_excluded.csv", "results/prefreeze/manifest_summary.json",
         "results/sprint2_review/freeze_candidate/events_drd.csv", "results/sprint2/freeze_candidate/roster.csv",
         "results/sprint2/freeze_candidate/roster_summary.json", "results/sprint2/freeze_candidate/access_receipt.json"]
PARAMETERS = ["results/prefreeze/candidate_models_core_matched.json", "results/prefreeze/candidate_parameters.json",
              "results/prefreeze/candidate_calibration_draws_core_matched.json.gz"]
FORECASTS = ["results/prefreeze/forecasts_core_draft.csv.gz", "results/prefreeze/forecasts_extension_draft.csv.gz",
             "results/prefreeze/forecasts_draft_receipt.json"]
CALIBRATION_INPUTS = ["results/outcomes/t015v3/outcomes.csv.gz", "results/outcomes/t015v3/product_identification.csv",
                      "results/outcomes/t015v3/products.csv", "results/pilot_v1/covariance_completeness.csv",
                      "data/fixtures/exoclock_ttv_flags.csv", "data/raw/osf/wna5e/updated_ephemerides.txt",
                      "data/raw/osf/p298n/catalogue_of_ephemerides.txt", "data/raw/osf/p298n/all_mid_time_data.txt",
                      "data/raw/osf/wpjtn/catalogue_of_ephemerides.txt", "data/raw/osf/wpjtn/all_mid_time_data.txt"]
EVIDENCE = ["scripts/prefreeze_evidence.py", "scripts/sprint2_analysis.py", "scripts/prefreeze_replay.py",
            "scripts/sprint2_confirm2.py", "results/prefreeze/injection_evidence_t015v3a.json",
            "results/prefreeze/replay/replay_receipt.json"]
for _s in ("confirm", "confirm2"):
    EVIDENCE += [f"results/sprint2/{_s}/{f}" for f in ("selection.csv", "ledger.csv.gz", "runs.csv", "products.csv",
                                                       "real_transits.csv", "run_receipt.json")]
    EVIDENCE += [f"results/prefreeze/replay/{_s}/{f}" for f in ("ledger.csv.gz", "runs.csv", "products.csv")]
GROUPS = {"code": CODE, "environment": ENVIRONMENT, "config": CONFIG, "event_lists": LISTS, "parameters": PARAMETERS,
          "forecasts": FORECASTS, "calibration_inputs": CALIBRATION_INPUTS, "injection_evidence": EVIDENCE}
DIAG = {"products": ("host", "product", "status", "shape_rchi2", "sha256", "t14_min"),
        "runs": ("run_id", "status", "shape_rchi2", "refit_t14_min", "id_period_d")}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tracked(rel):
    return subprocess.run(["git", "-C", str(ROOT), "ls-files", "--error-unmatch", rel],
                          capture_output=True).returncode == 0


def gz_content(p):
    with gzip.open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rows(p):
    p = Path(p)
    with (gzip.open(p, "rt") if p.suffix == ".gz" else p.open()) as fh:
        return list(csv.DictReader(fh))


def file_records():
    out = {}
    for group, paths in GROUPS.items():
        out[group] = {}
        for rel in paths:
            p = ROOT / rel
            rec = {"sha256": sha(p), "bytes": p.stat().st_size, "in_repository": tracked(rel)}
            if rel.endswith(".gz"):
                rec["content_sha256"] = gz_content(p)
            out[group][rel] = rec
    return out


def grid_records():
    """Every likelihood grid that acceptance reads: development calibration rows and replayed injections."""
    grids = {}
    for r in rows(ROOT / "results/outcomes/t015v3/outcomes.csv.gz"):
        if r.get("posterior_grid_path") and r["status"] == "timed":
            grids[r["posterior_grid_path"]] = None
    recorded = {}
    for s in ("confirm", "confirm2"):
        for r in rows(ROOT / f"results/prefreeze/replay/{s}/ledger.csv.gz"):
            if r.get("grid_sha256"):
                grids[r["posterior_grid_path"]] = None
                recorded[r["posterior_grid_path"]] = r["grid_sha256"]
    out = {k: sha(ROOT / k) for k in sorted(grids)}
    agg = hashlib.sha256("\n".join(f"{k} {v}" for k, v in out.items()).encode()).hexdigest()
    return out, agg, recorded


def checks(grids, recorded):
    res = {}
    for s in ("confirm", "confirm2"):
        for name, keys in DIAG.items():
            key = keys[0] if name == "runs" else None

            def pick(path):
                rs = [r for r in rows(path) if r.get("product") == "SPOC_120" and r.get("mode", "remove") == "remove"]
                if name == "products":
                    return sorted(tuple(r.get(k, "") for k in keys) for r in rs)
                return sorted(tuple(r.get(k, "") for k in keys) for r in rs if r.get(key))
            orig = pick(ROOT / f"results/sprint2/{s}/{name}.csv")
            rep = pick(ROOT / f"results/prefreeze/replay/{s}/{name}.csv")
            res[f"{s}_{name}_original_equals_replay"] = orig == rep and len(orig) > 0
    res["replay_grid_hashes_match_ledger"] = all(grids.get(k) == v for k, v in recorded.items())
    rec = json.loads((ROOT / "results/prefreeze/forecasts_draft_receipt.json").read_text())
    res["forecast_content_matches_receipt"] = all(
        gz_content(ROOT / f"results/prefreeze/forecasts_{n.split('_')[1]}_draft.csv.gz") == rec[n]["sha256_csv"]
        for n in ("manifest_core_primary", "manifest_extension_exploratory"))
    res["forecast_parameters_match_receipt"] = sha(ROOT / "results/prefreeze/candidate_models_core_matched.json") == \
        rec["parameters_sha256"]
    core = {r["event_id"] for r in rows(ROOT / "results/prefreeze/manifest_core_primary.csv")}
    res["core_forecasts_cover_core_manifest"] = core == {
        r["event_id"] for r in rows(ROOT / "results/prefreeze/forecasts_core_draft.csv.gz")}
    return res


def environment_observed():
    venv = subprocess.run(["uv", "pip", "freeze", "--python", str(ROOT / ".venv/bin/python")],
                          capture_output=True, text=True, check=True).stdout.splitlines()
    py = subprocess.run([str(ROOT / ".venv/bin/python"), "--version"],
                        capture_output=True, text=True, check=True).stdout.strip()
    return {"evaluation_python": py, "evaluation_venv_packages": [x for x in venv if not x.startswith("-e ")],
            "measurement_environment": "uv run with scripts/final_measure.py.lock"}


def compute():
    grids, agg, recorded = grid_records()
    return {"files": file_records(), "likelihood_grids": {"count": len(grids), "aggregate_sha256": agg,
                                                          "sha256": grids},
            "binding_checks": checks(grids, recorded), "environment_observed": environment_observed()}


def build(_args):
    body = compute()
    if not all(body["binding_checks"].values()):
        raise SystemExit(f"binding checks fail: {body['binding_checks']}")
    head = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    bad = source_commit_mismatches(body["files"], head)
    if bad:
        raise SystemExit(f"commit bound files before building the manifest: {bad}")
    doc = {"kind": "hash-bound freeze manifest (proposal; binding only once Barry's access record cites its SHA-256)",
           "question": json.loads((ROOT / "configs/candidate_freeze.json").read_text())["question"],
           "built_from_commit": head, "protected_outcomes_accessed": False,
           "commands": {"measure": "uv run scripts/final_measure.py --manifest results/prefreeze/manifest_core_primary.csv "
                                   "--out data/derived/final_primary/measured --era protected",
                        "evaluate": ".venv/bin/python scripts/final_evaluation.py evaluate "
                                    "--manifest results/prefreeze/manifest_core_primary.csv "
                                    "--forecasts results/prefreeze/forecasts_core_draft.csv.gz "
                                    "--windows data/derived/final_primary/measured/windows.csv.gz "
                                    "--products data/derived/final_primary/measured/products.csv "
                                    "--coverage data/derived/final_primary/measured/coverage.csv "
                                    "--out results/final_primary --era protected --bootstrap 2000 "
                                    "--conditional-bootstrap 10000 --workers 8",
                        "exploratory_extension": "same two commands with manifest_extension_exploratory.csv and "
                                                 "forecasts_extension_draft.csv.gz, label exploratory",
                        "publish_receipt": ".venv/bin/python scripts/freeze_manifest.py portable-receipt "
                                           "results/final_primary/scores.receipt.json"},
           **body}
    MANIFEST.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(doc, indent=1, sort_keys=False) + "\n")
    print("freeze manifest", sha(MANIFEST), "grids", body["likelihood_grids"]["count"])


def source_commit_mismatches(groups, revision):
    bad = []
    for records in groups.values():
        for rel, record in records.items():
            if not record["in_repository"]:
                continue
            blob = subprocess.run(["git", "-C", str(ROOT), "show", f"{revision}:{rel}"], capture_output=True)
            if blob.returncode or hashlib.sha256(blob.stdout).hexdigest() != record["sha256"]:
                bad.append(rel)
    return bad


def verify(_args=None, quiet=False):
    doc = json.loads(MANIFEST.read_text())
    bad = []
    for group, recs in doc["files"].items():
        for rel, rec in recs.items():
            p = ROOT / rel
            if not p.exists():
                bad.append(f"missing {rel}")
            elif sha(p) != rec["sha256"]:
                bad.append(f"changed {rel}")
    grids, agg, recorded = grid_records()
    if agg != doc["likelihood_grids"]["aggregate_sha256"]:
        bad.append("likelihood grids changed")
    chk = checks(grids, recorded)
    bad += [f"binding check failed: {k}" for k, v in chk.items() if not v]
    bad += [f"source commit differs: {p}" for p in source_commit_mismatches(doc["files"], doc["built_from_commit"])]
    env = environment_observed()
    if env["evaluation_python"] != doc["environment_observed"]["evaluation_python"]:
        bad.append("evaluation Python differs from the frozen version")
    if env["evaluation_venv_packages"] != doc["environment_observed"]["evaluation_venv_packages"]:
        bad.append("evaluation .venv packages differ from the frozen list")
    if not quiet:
        print(json.dumps({"manifest_sha256": sha(MANIFEST), "mismatches": bad}, indent=1))
    if _args is not None and bad:
        raise SystemExit(1)
    return bad


def check_for_access(record):
    """Called by final_evaluation.era_limit('protected'): the decision must cite this exact verified package."""
    if not MANIFEST.exists() or record.get("freeze_manifest_sha256") != sha(MANIFEST):
        raise SystemExit("access record does not cite the current freeze manifest SHA-256")
    bad = verify(quiet=True)
    if bad:
        raise SystemExit(f"frozen package changed since the manifest: {bad[:5]}")


def portable_receipt(args):
    p = Path(args.path)
    root = str(ROOT) + "/"
    text = p.read_text()
    rec = json.loads(text)

    def rel(x):
        return x.replace(root, "") if isinstance(x, str) else x

    def walk(o):
        if isinstance(o, dict):
            return {rel(k): walk(v) for k, v in o.items()}
        if isinstance(o, list):
            return [walk(v) for v in o]
        return rel(o)
    out = {**walk(rec), "portable_from_receipt_sha256": hashlib.sha256(text.encode()).hexdigest(),
           "portable_transform": "repository-root prefix removed from paths; values otherwise unchanged"}
    dest = p.with_name(p.name.removesuffix(".json") + ".portable.json")
    s = json.dumps(out, indent=1) + "\n"
    if str(Path.home()) in s:
        raise SystemExit("home path remains after transform")
    dest.write_text(s)
    print(dest)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(func=build)
    sub.add_parser("verify").set_defaults(func=verify)
    p = sub.add_parser("portable-receipt")
    p.add_argument("path")
    p.set_defaults(func=portable_receipt)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
