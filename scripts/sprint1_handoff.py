"""Assemble the sprint handoff from completed, source-verified comparisons."""
from pathlib import Path
import csv
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "results/sprint1"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def main():
    experiments = ("release_transfer", "chronological", "delayed_origin", "late_published_proxy")
    for name in experiments:
        receipt = read(BASE / f"forecasts/receipt_{name}.json")
        assert receipt["source_unchanged_during_run"]
        for section in ("source_config_sha256", "summary_hashes"):
            for path, expected in receipt[section].items():
                assert digest(ROOT / path) == expected, path
        for source in receipt["source_manifest"]:
            assert digest(ROOT / source["path"]) == source["sha256"]
    rows, parameters, tolerances = [], {}, {}
    for name in experiments:
        reference = read(BASE / f"forecasts/{name}__a_1.087__c2.json")
        parameters[name] = {"models": reference["models"], "parameters_path": reference["details_directory"] + "/parameters.json", "sha256": reference["parameter_sha256"], "status": reference["status"]}
        for path in sorted((BASE / "forecasts").glob(name + "__*.json")):
            data = read(path)
            for method in ("M1", "M2", "M3"):
                low, high = data["host_refit"][method]["delta_is95_standardised_percentile95"]
                rows.append({"experiment": name, "a": data["a"], "covariance": data["covariance"], "method": method, "delta_is95": data["metrics"][method]["delta_standardised_vs_M0"], "lower95": low, "upper95": high, "decision": data["host_refit"][method]["conditional_decision"], "bootstrap_replicates": data["host_refit"][method]["replicates"]})
        grid = sorted([r for r in rows if r["experiment"] == name and r["covariance"] == "c2" and r["method"] == "M2"], key=lambda r: r["a"])
        index = next(i for i,r in enumerate(grid) if r["a"] == 1.087)
        decision = grid[index]["decision"]
        start = end = index
        while start > 0 and grid[start-1]["decision"] == decision:
            start -= 1
        while end+1 < len(grid) and grid[end+1]["decision"] == decision:
            end += 1
        tolerances[name] = {"tested_grid_only": True, "reference_a": 1.087, "reference_decision": decision, "contiguous_same_decision_grid_range": [grid[start]["a"], grid[end]["a"]], "negative_point_delta_entire_grid": all(r["delta_is95"] < 0 for r in grid), "certified_measurement_tolerance": None, "reason": "Inspected development comparisons are inconclusive at reference; sign or null stability does not qualify an outcome-error convention."}
    with (BASE / "comparison.csv").open("w") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    (BASE / "outcome_scale_tolerance.json").write_text(json.dumps(tolerances, indent=2) + "\n")
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8), sharey=True, layout="constrained")
    for ax, name, label in zip(axes, experiments[:2], ("Release-transfer proxy", "Chronological proxy")):
        points = sorted([r for r in rows if r["experiment"] == name and r["covariance"] == "c2" and r["method"] == "M2"], key=lambda r: r["a"])
        ax.fill_between([r["a"] for r in points], [r["lower95"] for r in points], [r["upper95"] for r in points], color="#367DA2", alpha=.18)
        ax.plot([r["a"] for r in points], [r["delta_is95"] for r in points], "o-", color="#245E7B", markersize=3)
        ax.axhline(0, color="black", lw=.8); ax.axvline(1.087, color="#A85D2A", ls="--", lw=1)
        ax.set(title=label, xlabel="Outcome SD multiplier a")
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].set_ylabel("M2 − M0 standardised IS95\nNegative favours M2")
    fig.suptitle("Development evidence: mean gain, uncertain primary contrast", fontsize=12)
    fig.savefig(BASE / "outcome_scale_sensitivity.png", dpi=180)
    plt.close(fig)
    commands = [
        ".venv/bin/python scripts/sprint1_forecasts.py run --experiment release_transfer --bootstrap 400 --sensitivity-bootstrap 200 --sensitivities",
        ".venv/bin/python scripts/sprint1_forecasts.py run --experiment chronological --bootstrap 400 --sensitivity-bootstrap 200 --sensitivities",
        ".venv/bin/python scripts/sprint1_forecasts.py run --experiment delayed_origin --bootstrap 400",
        ".venv/bin/python scripts/sprint1_forecasts.py run --experiment late_published_proxy --bootstrap 200",
        ".venv/bin/python scripts/sprint1_forecasts.py make_forecasts --events data/derived/sprint1/release_transfer/a_1.087/c2/events.csv --parameters data/derived/sprint1/release_transfer/a_1.087/c2/parameters.json --release DRC --output data/derived/sprint1/interface/forecasts.csv",
        ".venv/bin/python scripts/sprint1_forecasts.py score --forecasts data/derived/sprint1/interface/forecasts.csv --outcomes data/derived/sprint1/release_transfer/a_1.087/c2/events.csv --error-convention exoclock_reported --outcome-scale 1.087 --output data/derived/sprint1/interface/scores.csv",
        ".venv/bin/python scripts/review_sprint1_scores.py",
        ".venv/bin/python scripts/sprint1_precision.py --replicates 4000 --chunk-size 100",
        ".venv/bin/python -m unittest discover -s tests -v",
        ".venv/bin/python scripts/sprint1_handoff.py"]
    defects = [
        {"id": "S1-01", "owner": "Claude sprint 2", "issue": "Complete intended-event truth/attempt ledger and one-to-one match, with distinct product/run/event failure denominators."},
        {"id": "S1-02", "owner": "Claude sprint 2", "issue": "Freeze host-balanced outcome-calibration estimand; replace or bias-correct and validate log host-MSE endpoints. No certified A2 tolerance supplied."},
        {"id": "S1-03", "owner": "Claude sprint 2", "issue": "Remeasure development outcomes and refit M1-M3 under each error convention; do not transplant catalogue parameters to the pipeline."},
        {"id": "S1-04", "owner": "Claude sprint 2", "issue": "Independent forecast-cycle mapping, no-removal and shape controls, short-period geometry, identification boundary controls and R8 extension qualification."},
        {"id": "S1-05", "owner": "Claude and Codex reciprocal review", "issue": "Missing issued covariance, incomplete exposure lineage, selection denominator and limited historical calibration availability qualify all claims."},
        {"id": "S1-06", "owner": "Claude sprint 2", "issue": "Confirm eligible 120-host development frame and actual product availability; metadata opportunities do not establish timing recovery."}]
    output_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(BASE.rglob("*")) if p.is_file() and p.name != "handoff.json"}
    detail_hashes = {str(p.relative_to(ROOT)): digest(p) for name in experiments for p in sorted((ROOT / parameters[name]["parameters_path"]).parent.glob("*")) if p.is_file()}
    handoff = {"date": "2026-11-06", "status": "sprint1 complete; sprint2 interface acceptance and execution next", "development_only": True, "protocol_frozen": False, "protected_outcomes_accessed": False, "commands": commands, "parameters": parameters, "outcome_scale_tolerance": tolerances, "R8": {"core_planets": 156, "extension_planets": 28, "union_planets": 184, "union_hosts": 175, "metadata_increment_percent": 28/156*100, "gate_logic": "OR", "extension_gate_passed": True, "identification_qualified": False}, "open_defects": defects, "output_sha256": output_hashes, "detailed_output_sha256": detail_hashes, "handoff_script_sha256": digest(Path(__file__)), "qualification": "All parameter sets are labelled development fits, not adopted protected-era rules. Raw IS95 and forecast-only normalisation accompany outcome-dependent standardisation."}
    (BASE / "handoff.json").write_text(json.dumps(handoff, indent=2) + "\n")
    print("Verified four experiment receipts; wrote comparison, figure, tolerance and handoff.")


if __name__ == "__main__":
    main()
