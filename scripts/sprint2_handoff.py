"""Write results/sprint2/handoff.json: decisive commands, values, open defects and output hashes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "sprint2"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def remeasurement():
    import csv
    import gzip
    import numpy as np
    rows = list(csv.DictReader(gzip.open(ROOT / "results/outcomes/t015v3/outcomes.csv.gz", "rt")))
    t = [r for r in rows if r["status"] == "timed"]
    m = [r for r in t if r.get("exoclock_delta_s")]
    d = np.array([float(r["exoclock_delta_s"]) for r in m])
    s1, s2 = np.array([float(r["sigma_s"]) for r in m]), np.array([float(r["exoclock_sigma_s"]) for r in m])
    status = {}
    for r in rows:
        status[r["status"]] = status.get(r["status"], 0) + 1
    return {"attempted": len(rows), "status_counts": status, "timed_planets": len({r["planet"] for r in t}),
            "same_photon_matched": len(m), "median_delta_s": round(float(np.median(d)), 3),
            "z_rms": round(float(np.sqrt(np.mean((d / np.hypot(s1, s2)) ** 2))), 4),
            "median_sigma_ratio_t015v3_over_exoclock": round(float(np.median(s1 / s2)), 4)}


def main():
    j = lambda p: json.loads((ROOT / p).read_text())  # noqa: E731
    c1, c2 = j("results/sprint2/confirm/summary.json"), j("results/sprint2/confirm2/summary.json")
    conv = j("results/sprint2/forecasts/convention_comparison.json")
    cand = j("results/sprint2/forecasts/candidate_parameters_t015v3.json")
    pick = lambda g: {k: g[k] for k in ("hosts", "events", "z_rms", "z_rms_ci90", "cover95", "cover95_ci90", "mean_z",  # noqa: E731
                                        "mean_z_ci90", "z_rms_tmag9_ci90", "z_rms_tmag13.5_ci90")} | {"pass": g["verdict"]["pass"],
                                                                                                    "failed": [k for k, v in g["verdict"]["checks"].items() if not v]}
    files = sorted(p for p in (ROOT / "results" / "sprint2").rglob("*") if p.is_file() and p.name != "handoff.json"
                   and not p.name.endswith("ledger.csv"))
    files += sorted((ROOT / "results" / "outcomes" / "t015v3").glob("*"))
    out = {
        "date": "2026-11-07", "status": "sprint 2 complete; Codex review and fix next",
        "development_only": True, "protocol_frozen": False, "protected_outcomes_accessed": False,
        "rule": {"name": "t015v3", "frozen_at": "2c39f0a", "source_hash": "4b5c9602a29b",
                 "replication_design": "9375b3c"},
        "verdict": "outcome pipeline not ready under prespecified criteria (D049)",
        "confirmation": {"t015v3c_primary": pick(c1["groups"]["t015v3c|remove|production|all"]),
                         "t015v3_secondary": pick(c1["groups"]["t015v3|remove|production|all"])},
        "replication": {"t015v3_primary": pick(c2["groups"]["t015v3|remove|production|all"])},
        "exploratory_transit_count_split": j("results/sprint2/exploratory_transit_count.json"),
        "R5": {exp: conv["experiments"][exp]["transfer"] for exp in conv["experiments"]},
        "remeasurement": remeasurement(),
        "candidate_parameters_t015v3": cand["models"],
        "candidate_training": {k: cand[k] for k in ("training_planets", "training_hosts", "training_events")},
        "freeze_candidate": j("results/sprint2/freeze_candidate/roster_summary.json"),
        "access_receipt": j("results/sprint2/freeze_candidate/access_receipt.json"),
        "open_defects": [
            {"id": "S2-01", "owner": "Codex review", "issue": "Product-level consistency rule against spurious windows (WASP-54b S50 timed at z=55, 12 h from the true transit)"},
            {"id": "S2-02", "owner": "next design", "issue": "Prespecified, metadata-defined test of the >=4-transits-per-sector scope; decide sealed-evaluation restriction"},
            {"id": "S2-03", "owner": "next design", "issue": "Bright-star (Tmag<10) undercoverage 0.915-0.918 and stratum-A recovery"},
            {"id": "S2-04", "owner": "Codex review", "issue": "Equal-host weighting gives few-transit hosts full weight; decide the estimand weighting for the sealed population"},
            {"id": "S2-05", "owner": "Claude", "issue": "Write full-support likelihood grids; 21/404 non-Gaussian grids truncated by the +/-60-min prior are refused by the adapter"},
            {"id": "S1-05", "owner": "both", "issue": "Missing issued covariance, exposure lineage, selection denominator, limited calibration availability"}],
        "commands": [
            "uv run scripts/sprint2_outcomes.py run --sample dev",
            "uv run scripts/sprint2_outcomes.py idtests",
            "uv run scripts/sprint2_outcomes.py run --sample confirm",
            "uv run scripts/sprint2_confirm2.py run",
            ".venv/bin/python scripts/sprint2_analysis.py check",
            ".venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm2",
            "uv run scripts/sprint2_remeasure.py run",
            ".venv/bin/python scripts/sprint2_forecasts.py run --bootstrap 400",
            ".venv/bin/python scripts/sprint2_forecasts.py candidate --convention t015v3 --output candidate_parameters_t015v3.json",
            ".venv/bin/python scripts/sprint2_forecasts.py interface",
            ".venv/bin/python scripts/sprint2_freeze_package.py roster",
            ".venv/bin/python scripts/sprint2_freeze_package.py forecasts --parameters results/sprint2/forecasts/candidate_parameters_t015v3.json",
            ".venv/bin/python scripts/sprint2_freeze_package.py receipt",
            ".venv/bin/python -m unittest discover -s tests"],
        "outputs": [{"path": str(p.relative_to(ROOT)), "sha256": sha(p)} for p in files],
        "handoff_script_sha256": sha(__file__)}
    (OUT / "handoff.json").write_text(json.dumps(out, indent=1, default=float) + "\n")
    print(len(out["outputs"]), "hashed outputs")


if __name__ == "__main__":
    main()
