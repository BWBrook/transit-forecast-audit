"""Review D057 using saved development tables/grids and a synthetic gap example.

No photometry, FITS headers, network access or protected outcomes are used.
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import math
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import prefreeze_attempts as attempts
import prefreeze_package as package
import sprint2_forecasts as forecasts
import t015_timing_pipeline as timing


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    rows, _ = package.gated_rows()
    retained = [r for r in rows if r["status"] == "timed"]
    grid_rows = [r for r in retained if r.get("posterior_grid_path")]
    rejected, missing, grid_hashes = [], [], {}
    for row in grid_rows:
        path = ROOT / row["posterior_grid_path"]
        if not path.exists():
            missing.append(row["event_id"])
            continue
        grid_hashes[row["posterior_grid_path"]] = digest(path)
        if not forecasts.grid_resolved(path):
            rejected.append(row["event_id"])
    eph, _, flags = package.load()
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    spec = cfg["experiments"]["release_transfer"]["test"]
    core = package.core_planets(eph)
    train, _ = forecasts.our_events(
        spec["release"], spec["start"], spec["end"],
        [r for r in rows if r["planet"] in core], eph, flags,
        package.c.covariance_rows(), convention="t015v3",
    )
    t0 = 2459000.0
    cadences = np.array([t0 - .1, t0, t0 + .1])
    recovered = timing.windows(cadences, 2.0, t0 + 1.0, .2)
    manifest = [{"planet": "synthetic", "sector": "1", "epoch": 0}]
    ledger, _ = attempts.build_ledger(
        manifest, [], {("synthetic", "1"): "ok"},
        {"synthetic": SimpleNamespace(t0_bjd_tdb=t0, period_days=2.0)},
    )
    assert not recovered
    assert np.any(np.abs(cadences - t0) < .2)
    assert ledger[0]["status"] == "no_cadence_in_window"
    manifests = {}
    for label in ("core_primary", "extension_exploratory", "boundary_excluded"):
        data = list(csv.DictReader((ROOT / f"results/prefreeze/manifest_{label}.csv").open()))
        manifests[label] = {"events": len(data), "planets": len({r["planet"] for r in data}),
                            "unique_event_ids": len({r["event_id"] for r in data})}
    paths = ["scripts/prefreeze_attempts.py", "scripts/prefreeze_package.py",
             "scripts/sprint2_forecasts.py", "configs/candidate_freeze.json",
             "results/prefreeze/candidate_parameters.json",
             "results/outcomes/t015v3/outcomes.csv.gz",
             "results/outcomes/t015v3/product_identification.csv",
             "results/prefreeze/identification_windows.csv.gz"]
    with gzip.open(ROOT / paths[-1], "rt") as fh:
        controls = [r for r in csv.DictReader(fh) if r["record"] == "window"
                    and r["window_status"] == "timed"
                    and not (attempts.INTEG & set(r["flags"].split(";")))]
    threshold_counts = {}
    for threshold in (10., 100.):
        keep = [r for r in controls if math.isfinite(float(r["shape_rchi2"]))
                and float(r["shape_rchi2"]) <= threshold]
        threshold_counts[str(int(threshold))] = {
            "accepted_control_timings": len(keep), "lost_control_timings": len(controls) - len(keep),
            "spurious_control_timings": sum(not r["truth_index"] for r in keep),
            "matched_abs_z_gt5": sum(bool(r["z"]) and abs(float(r["z"])) > 5 for r in keep),
        }
    out = {
        "protected_data_accessed": False, "photometry_or_headers_opened": False,
        "support_check": {
            "retained_timed": len(retained), "grid_rows": len(grid_rows),
            "missing_grids": missing, "adapter_rejected_but_candidate_retained": rejected,
            "core_training_events": len(train),
            "core_training_support_rejections": [r["event_id"] for r in train if r["event_id"] in rejected],
            "grid_hash_map_sha256": hashlib.sha256(json.dumps(grid_hashes, sort_keys=True).encode()).hexdigest(),
        },
        "synthetic_gap_counterexample": {
            "synthetic": True, "cadence_offsets_days": [-.1, 0., .1], "period_days": 2.,
            "recovered_epoch_offset_days": 1., "half_window_days": .2,
            "recovered_windows": recovered, "cadence_present_at_intended_event": True,
            "ledger_status": ledger[0]["status"],
            "conclusion": "No recovered window does not establish a cadence gap at the intended event.",
        },
        "manifests": manifests,
        "shape_threshold_controls": {"ungated_timed": len(controls), "thresholds": threshold_counts},
        "input_sha256": {p: digest(ROOT / p) for p in paths},
    }
    dest = ROOT / "results/sprint2_review/d057/package_check.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"support_check": out["support_check"],
                      "synthetic_gap_counterexample": out["synthetic_gap_counterexample"],
                      "manifests": manifests}, indent=2))


if __name__ == "__main__":
    main()
