"""Export or replay the derived scoring benchmark without raw light curves.

Export: python scripts/t018_benchmark.py export --out data/derived/revision_stage0/benchmark
Replay: python replay.py replay --out replayed       (inside an exported package)
"""

from __future__ import annotations

import os
for variable in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ[variable] = "1"

import argparse
import csv
import gzip
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import tarfile
from pathlib import Path

import numpy as np
import scipy

ROOT = Path(__file__).resolve().parent
if ROOT.name == "scripts":
    ROOT = ROOT.parent
SCORING_SCRIPTS = ("sprint1_outcome_adapter.py", "sprint1_forecast_core.py", "forecast_variance_components.py",
                   "reproduce_table5.py", "review_measurement_diagnostic.py")
METRICS = ("weight", "is95_standardised", "is95_minutes", "is95_forecast_normalised",
           "negative_log_score_seconds", "covered68", "covered95", "width95_minutes", "m0_predictive_sd_s")
TOLERANCE = 1e-9


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_csv(path):
    path = Path(path)
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as stream:
        return list(csv.DictReader(stream))


def write_csv(path, rows):
    with Path(path).open("w", newline="") as stream:
        writer = csv.DictWriter(stream, list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def write_json(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def verify(directory):
    manifest = json.loads((directory / "SHA256.json").read_text())
    for name, expected in manifest.items():
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Unsafe package path")
        if sha(directory / relative) != expected:
            raise RuntimeError("Benchmark hash mismatch: " + name)
    return manifest


def compare_scores(expected, actual):
    def indexed(rows):
        result = {(r["event_id"], r["method"]): r for r in rows}
        if len(result) != len(rows):
            raise ValueError("Duplicate event-method score")
        return result
    expected, actual = indexed(expected), indexed(actual)
    if set(expected) != set(actual):
        raise RuntimeError("Replayed score identities differ")
    errors = {key: 0. for key in METRICS}
    for identity, source in expected.items():
        row = actual[identity]
        for key in ("observation_id", "planet", "host", "release", "parameter_version", "shape_group_id"):
            if row[key] != source[key]:
                raise RuntimeError("Replayed score metadata differs: " + key)
        for key in METRICS:
            difference = abs(float(row[key]) - float(source[key]))
            if not np.isfinite(difference):
                raise RuntimeError("Nonfinite score comparison")
            errors[key] = max(errors[key], difference)
    if max(errors.values()) > TOLERANCE:
        raise RuntimeError("Score replay exceeds tolerance: " + str(errors))
    return errors


def replay(directory, output):
    directory = directory.resolve()
    before = verify(directory)
    sys.path[:0] = [str(directory / "scripts"), str(directory / "src")]
    import sprint1_outcome_adapter as adapter
    output.mkdir(parents=True, exist_ok=True)
    reports = {}
    for label in ("primary", "extension"):
        data = directory / label
        destination = output / (label + "_scores.csv")
        adapter.score_outcomes(argparse.Namespace(forecasts=str(data / "accepted_forecasts.csv"),
            outcomes=str(data / "accepted_outcomes.csv"), output=str(destination), outcome_scale=1.,
            error_convention="t015v3_beta_chi", max_tc_bjd=None))
        errors = compare_scores(read_csv(data / "expected_scores.csv"), read_csv(destination))
        raw_receipt = json.loads(destination.with_suffix(".receipt.json").read_text())
        portable_receipt = {
            "timed_events": raw_receipt["timed_production_events"],
            "nonGaussian_events": raw_receipt["nonGaussian_events"],
            "score_sha256": sha(destination), "max_absolute_metric_errors": errors,
            "tolerance": TOLERANCE,
            "scope": "Exact saved accepted outcomes; no fitting, raw data access, or capture claim",
        }
        write_json(destination.with_suffix(".receipt.json"), portable_receipt)
        reports[label] = portable_receipt
    after = verify(directory)
    if before != after:
        raise RuntimeError("Benchmark inputs changed during replay")
    report = {"kind": "complete primary and extension score replay", "all_checks_pass": True,
              "package_files_verified": len(before), "results": reports,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__},
              "raw_photometry_or_headers_opened": False, "network_requests": False}
    write_json(output / "replay_receipt.json", report)
    print(json.dumps({"replay_pass": True, "sets": {label: r["timed_events"] for label, r in reports.items()}}))
    return report


README = """# Derived transit forecast scoring benchmark

This package replays the frozen accepted-event scores for the D065 primary
and exploratory extension. It contains no raw TESS light curves and requires
no download. It does not re-extract transits, fit calibration parameters,
recompute joint-refit uncertainty, estimate missed-transit frequency, or
establish observing-window capture. The pre-registered primary result remains
inconclusive; post-review diagnostics do not replace it.

Use Python 3.13.16 and the pinned `requirements.txt`, then run:

    python replay.py replay --out replayed

The entry point verifies all package hashes, runs the unchanged scoring adapter
on every accepted event, compares every event-method metric with the expected
scores (absolute tolerance 1e-9), and checks inputs again. The replay receipt
contains runtime versions and separate metric errors.

`SHA256.json` binds all package files except itself and generated replay outputs.
`provenance.json` links relocated tables/grids to their original repository hashes.
The full frozen manifest/configuration and fitted parameters are supplied for
identity/context. The minimal scoring import closure is byte-identical to its
source; paths to accepted non-Gaussian grids are relocated, not grid contents.

The package is prepared for a later reviewed archive, not published by this step.
Source/product identifiers and hashes preserve attribution. Code is MIT;
project-derived tables and text are CC BY-SA 4.0. Third-party original photometry
is not redistributed, and its licence is not replaced by project licences.
"""

DICTIONARY = """# Data dictionary and estimands

- `primary/` and `extension/`: primary core versus exploratory extension,
  never pooled for a confirmatory verdict.
- `intended_manifest.csv`: one fixed event opportunity per planet/sector/DRD
  cycle; metadata eligibility is not a recovered transit or exact capture.
- `intended_forecasts.csv.gz`: issued ephemeris predictions and plug-in model
  parameters for intended events. `forecast_variance_s2` includes reconstructed
  T0-period covariance, not outcome error. It is not an issued joint posterior.
- `terminal_ledger.csv.gz`: exactly one status per intended event, including
  failures and prediction-time coverage. Prediction coverage is a diagnostic,
  not an acceptance gate. Unaccepted events have unknown timing truth.
- `accepted_outcomes.csv`: accepted conditional profile-likelihood timing
  distributions. `tc_bjd_tdb` is reported BJD_TDB; `sigma_s` is the timing
  half-width convention in seconds. Gaussian certification uses exact95%
  quantiles. Otherwise `posterior_grid_path` identifies an unmodified saved
  grid in `data/grids/`; its offset coordinate is true mid-time minus reported
  mid-time (seconds), with the file's declared support/prior convention.
  These are conditional on fixed fitted shape/noise treatment, not a marginal
  full-uncertainty posterior. SAP/PDCSAP products are not independent exposures.
- `accepted_forecasts.csv`: rows exactly paired by event/observation/planet/host
  with accepted outcomes. Methods M0 (issued Gaussian reconstruction), M1
  (single scale), M2 (tails only), M3 (both), with stored b and log-variance s.
- `expected_scores.csv`: one row per accepted event and method. IS95 has
  width plus40times the excess beyond its central95% interval. All forecasts
  are convolved with independent supplied measurement error. Raw IS is minutes,
  not telescope time; forecast-normalised IS divides seconds by forecast SD;
  standardised IS divides by M0 predictive SD including outcome error/grid
  variance. The last denominator is measured after issue and may be
  outcome-dependent, so the primary loss is conditional weighted loss.
- `covered68` and `covered95`: coverage of measured time under that convolution,
  not latent true mid-time or whole-transit scheduling capture. `width95_minutes`
  is a predictive measured-time width, not a schedule padded by duration/baselines.
- `weight`: reciprocal of accepted planet count and accepted events within
  planet. Give each planet equal total weight, and resample whole hosts.
- `shape_group_id` and `resampling_cluster`: dependence identities. Bootstrap
  host resampling does not correct a wrong conditional measurement covariance.
- `joint_draws.json.gz`: stored joint host-refit draws from the frozen run,
  supplied as evidence, not a posterior mixture to average into issued forecasts.
  Eleven extension draws contain no evaluation host and have undefined contrast.

No inverse-probability correction or selection-ignorability assumption is made.
The replay evaluates accepted timings only; it cannot recover unseen/missed
events from a successful timing catalogue.
"""


def export(directory):
    directory = directory.resolve()
    directory.mkdir(parents=True, exist_ok=False)
    original = {}
    def copy(source, destination):
        source = ROOT / source
        destination = directory / destination
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
        original[str(source.relative_to(ROOT))] = sha(source)
    for script in SCORING_SCRIPTS:
        copy("scripts/" + script, "scripts/" + script)
    for source in sorted((ROOT / "src/transit_audit").glob("*.py")):
        copy(str(source.relative_to(ROOT)), str(source.relative_to(ROOT)))
    copy("scripts/t018_benchmark.py", "replay.py")
    for source in ("LICENSE", "LICENSE-CONTENT"):
        if (ROOT / source).is_file():
            copy(source, source)
    for source in ("results/freeze/freeze_manifest.json", "configs/candidate_freeze.json", "results/prefreeze/candidate_parameters.json"):
        copy(source, "specification/" + Path(source).name)
    grid_count = 0
    for label, suffix in (("primary", "core"), ("extension", "extension")):
        run = "results/final_" + label + "/"
        for source, target in (("accepted_forecasts.csv", "accepted_forecasts.csv"), ("scores.csv", "expected_scores.csv"),
                               ("terminal_ledger.csv.gz", "terminal_ledger.csv.gz"), ("joint_draws.json.gz", "joint_draws.json.gz")):
            copy(run + source, label + "/" + target)
        copy("results/prefreeze/manifest_" + ("core_primary" if label == "primary" else "extension_exploratory") + ".csv",
             label + "/intended_manifest.csv")
        copy("results/prefreeze/forecasts_" + suffix + "_draft.csv.gz", label + "/intended_forecasts.csv.gz")
        outcome_path = ROOT / run / "accepted_outcomes.csv"
        original[str(outcome_path.relative_to(ROOT))] = sha(outcome_path)
        outcomes = read_csv(outcome_path)
        for row in outcomes:
            if row["posterior_grid_path"]:
                source = Path(row["posterior_grid_path"])
                source = source if source.is_absolute() else ROOT / source
                digest = sha(source)
                target = Path("data/grids") / (digest + ".json")
                if not (directory / target).exists():
                    copy(str(source.relative_to(ROOT)), str(target))
                    grid_count += 1
                row["posterior_grid_path"] = str(target)
        write_csv(directory / label / "accepted_outcomes.csv", outcomes)
    (directory / "README.md").write_text(README)
    (directory / "DATA_DICTIONARY.md").write_text(DICTIONARY)
    environment = json.loads((ROOT / "results/freeze/freeze_manifest.json").read_text())["environment_observed"]
    pins = dict(value.split("==", 1) for value in environment["evaluation_venv_packages"])
    (directory / "requirements.txt").write_text("".join(name + "==" + pins[name] + "\n" for name in ("numpy", "scipy")))
    provenance = {"kind": "derived scoring benchmark, prepared not released", "grid_files": grid_count,
                  "original_repository": "https://github.com/BWBrook/transit-forecast-audit",
                  "checkout_base_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
                  "exporter_status": "Post-review entry point authored in the working checkout; actual bytes are hash-bound, not attributed to the checkout base commit",
                  "original_input_sha256": original,
                  "path_relocation": "Only accepted-outcome grid paths change; grid bytes and forecast/score/ledger bytes preserved",
                  "no_raw_photometry": True, "no_network": True}
    write_json(directory / "provenance.json", provenance)
    manifest = {str(p.relative_to(directory)): sha(p) for p in sorted(directory.rglob("*")) if p.is_file()}
    write_json(directory / "SHA256.json", manifest)
    if any(sha(ROOT / path) != digest for path, digest in original.items()):
        raise RuntimeError("Original inputs changed during export")
    archive = directory.with_suffix(".tar.gz")
    with tarfile.open(archive, "w:gz") as stream:
        stream.add(directory, arcname=directory.name)
    report = {"package_root": str(directory.relative_to(ROOT)), "file_count": len(manifest), "grid_files": grid_count,
              "file_manifest_sha256": sha(directory / "SHA256.json"), "archive": str(archive.relative_to(ROOT)),
              "archive_sha256": sha(archive), "archive_bytes": archive.stat().st_size,
              "original_inputs_unchanged": True, "released": False,
              "runtime": {"python": platform.python_version(), "numpy": np.__version__, "scipy": scipy.__version__}}
    destination = ROOT / "results/revision_stage0"
    destination.mkdir(parents=True, exist_ok=True)
    write_json(destination / "benchmark_export_receipt.json", report)
    print(json.dumps(report))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("export", "replay"))
    parser.add_argument("--package", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.action == "export":
        export(args.out)
    else:
        replay(args.package, args.out.resolve())


if __name__ == "__main__":
    main()
