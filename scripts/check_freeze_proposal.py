"""Independent D063/D064 package check using hashes, metadata and import closure.

Does not import the supplied manifest verifier, measure photometry or authorise
protected access. Run with the evaluation .venv interpreter.
"""

import ast
import csv
import gzip
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def rows(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as fh:
        return list(csv.DictReader(fh))


def main():
    path = ROOT / "results/freeze/freeze_manifest.json"
    doc = json.loads(path.read_text())
    files = {p: r for group in doc["files"].values() for p, r in group.items()}
    assert len(files) == sum(map(len, doc["files"].values()))
    for rel, record in files.items():
        data = (ROOT / rel).read_bytes()
        assert sha(data) == record["sha256"] and len(data) == record["bytes"], rel
        if rel.endswith(".gz"):
            assert sha(gzip.decompress(data)) == record["content_sha256"], rel
        if record["in_repository"]:
            committed = subprocess.check_output(["git", "-C", str(ROOT), "show", doc["built_from_commit"] + ":" + rel])
            assert committed == data, rel
    grids = doc["likelihood_grids"]["sha256"]
    for rel, expected in grids.items():
        assert sha((ROOT / rel).read_bytes()) == expected, rel
    assert len(grids) == doc["likelihood_grids"]["count"]
    assert sha("\n".join(f"{p} {h}" for p, h in grids.items()).encode()) == doc["likelihood_grids"]["aggregate_sha256"]

    modules = {p.stem: p for p in (ROOT / "scripts").glob("*.py")}
    for p in (ROOT / "src").rglob("*.py"):
        key = str(p.relative_to(ROOT / "src")).removesuffix(".py").replace("/", ".").removesuffix(".__init__")
        modules[key] = p
    pending = [ROOT / "scripts" / p for p in ("final_measure.py", "final_evaluation.py", "prefreeze_evidence.py", "prefreeze_replay.py")]
    seen = set()
    while pending:
        p = pending.pop()
        if p in seen:
            continue
        seen.add(p)
        for node in ast.walk(ast.parse(p.read_text())):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom):
                assert node.level == 0, "resolve new relative imports explicitly"
                names = [node.module] + [node.module + "." + a.name for a in node.names]
            pending += [modules[n] for n in names if n in modules and modules[n] not in seen]
    assert all(str(p.relative_to(ROOT)) in files for p in seen)

    observed = doc["environment_observed"]
    assert observed["evaluation_python"] == "Python " + platform.python_version()
    installed = {d.metadata["Name"].lower().replace("_", "-") + "==" + d.version
                 for d in importlib.metadata.distributions()
                 if d.metadata["Name"] != "transit-forecast-audit"}
    assert installed == set(observed["evaluation_venv_packages"])
    locks = []
    for name in ("scripts/final_measure.py.lock", "scripts/prefreeze_replay.py.lock"):
        packages = tomllib.loads((ROOT / name).read_text())["package"]
        locks.append({(p["name"], p["version"]) for p in packages})
    assert locks[0] == locks[1]
    pins = dict(locks[0])
    assert {k: pins[k] for k in ("numpy", "scipy", "astropy", "lightkurve")} == {
        "numpy": "2.3.5", "scipy": "1.18.1", "astropy": "8.0.2", "lightkurve": "2.5.1"}

    provenance = rows(ROOT / "results/pilot_v1/source_manifest.csv")
    external = [p for p, r in files.items() if not r["in_repository"]]
    for p in external:
        if p.startswith("data/raw/osf/"):
            assert any(r["local_path"] == p and r["sha256"] == files[p]["sha256"] for r in provenance)
    primary = rows(ROOT / "results/prefreeze/manifest_core_primary.csv")
    extension = rows(ROOT / "results/prefreeze/manifest_extension_exploratory.csv")
    excluded = rows(ROOT / "results/prefreeze/manifest_boundary_excluded.csv")
    source = rows(ROOT / "results/sprint2_review/freeze_candidate/events_drd.csv")
    ids = lambda data: [r["event_id"] for r in data]
    assert [len(primary), len(extension), len(excluded), len(source)] == [3103, 291, 5, 3399]
    assert len(set(ids(primary + extension + excluded))) == 3399
    assert set(ids(primary + extension + excluded)) == set(ids(source))
    for label, data in (("core", primary), ("extension", extension)):
        forecast = rows(ROOT / f"results/prefreeze/forecasts_{label}_draft.csv.gz")
        assert len(forecast) == len(data) and set(ids(forecast)) == set(ids(data))
    base = ROOT / "results/prefreeze/final_path_dev/run"
    original = (base / "scores.receipt.json").read_bytes()
    portable = json.loads((base / "scores.receipt.portable.json").read_text())
    assert portable.pop("portable_from_receipt_sha256") == sha(original)
    portable.pop("portable_transform")
    def relative(value):
        if isinstance(value, dict):
            return {k.replace(str(ROOT) + "/", ""): relative(v) for k, v in value.items()}
        if isinstance(value, list):
            return [relative(v) for v in value]
        return value.replace(str(ROOT) + "/", "") if isinstance(value, str) else value
    assert portable == relative(json.loads(original))
    assert sha(original) == json.loads((base / "evaluation_summary.json").read_text())["adapter_receipt_sha256"]
    assert not (ROOT / "configs/protected_access.json").exists()
    result = {"manifest_sha256": sha(path.read_bytes()), "source_commit": doc["built_from_commit"],
              "files": len(files), "grids": len(grids), "local_import_modules": len(seen),
              "file_size_hash_gzip_and_source_checks": True, "all_grid_hashes_and_aggregate_match": True,
              "import_closure_bound": True, "interpreter_and_installed_packages_match": True,
              "measurement_replay_locks_match": True, "five_OSF_inputs_match_download_provenance": True,
              "portable_receipt_transformation_and_linkage_match": True, "local_only_inputs": external,
              "event_partition_and_both_forecast_manifests_match": True,
              "protected_access_record_exists": False, "photometry_or_headers_opened": False,
              "status": "Independently verified proposal; no freeze or protected access authorised."}
    dest = ROOT / "results/sprint2_review/d063/independent_manifest_check.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
