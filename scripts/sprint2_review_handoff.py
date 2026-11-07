"""Verify review receipts and assemble the corrected scientific handoff."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/sprint2_review"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads((ROOT / path).read_text())


def main():
    corrected = read("results/sprint2_review/statistics/confirm2_corrected_summary.json")
    replication = corrected["groups"]["t015v3|remove|production|all"]
    confirmation = read("results/sprint2_review/statistics/confirm_corrected_summary.json")
    assert replication["verdict"]["pass"]
    assert not confirmation["groups"]["t015v3c|remove|production|all"]["verdict"]["pass"]
    replay = read("results/sprint2_review/interface/summary.json")
    assert replay["source_unchanged_during_run"]
    for path, expected in replay["source_sha256"].items():
        assert digest(ROOT / path) == expected, path
    receipt = read("results/sprint2_review/interface/score_receipt.json")
    assert receipt["source_inputs_unchanged_during_run"]
    for path, expected in receipt["source_config_sha256"].items():
        assert digest(ROOT / path) == expected, path
    archive = read("results/sprint2_review/bulk_archive_receipt.json")
    assert archive["remote_sha256_verified"] and archive["archive_member_sha256_verified"]
    paths = [ROOT / "scripts" / name for name in
             ("sprint1_outcome_adapter.py", "sprint2_analysis.py", "sprint2_outcomes.py",
              "sprint2_forecasts.py", "sprint2_freeze_package.py", "sprint2_figures.py",
              "t015_timing_pipeline.py", "review_sprint2_statistics.py",
              "review_sprint2_timing.py", "review_sprint2_provenance.py",
              "review_sprint2_interface.py", "sprint2_review_handoff.py")]
    paths += [ROOT / name for name in ("configs/candidate_freeze.json", "docs/sprint2_review.md",
                                      "manuscript/paper.md", "docs/brief.md", "docs/brief.pdf", "docs/agent_guide.md")]
    output_hashes = {str(p.relative_to(ROOT)): digest(p) for p in sorted(OUT.rglob("*"))
                     if p.is_file() and p.name != "handoff.json"}
    commands = [
        ".venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm --bootstrap 10000 --output results/sprint2_review/statistics/confirm_corrected_summary.json",
        ".venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm2 --bootstrap 10000 --output results/sprint2_review/statistics/confirm2_corrected_summary.json",
        ".venv/bin/python scripts/review_sprint2_statistics.py --bootstrap 10000 --control-reps 600 --control-bootstrap 600",
        ".venv/bin/python scripts/review_sprint2_timing.py",
        ".venv/bin/python scripts/review_sprint2_provenance.py",
        ".venv/bin/python scripts/review_sprint2_interface.py",
        ".venv/bin/python scripts/sprint2_freeze_package.py roster --output results/sprint2_review/freeze_candidate",
        "pandoc docs/brief.md --pdf-engine=pdflatex -V papersize:a4 -V geometry:margin=20mm -V fontsize=11pt -o docs/brief.pdf",
        ".venv/bin/python -m unittest discover -s tests -v",
        ".venv/bin/python scripts/sprint2_review_handoff.py"]
    result = {
        "date": "2026-11-07", "status": "Codex sprint2 review/fixes complete; Claude counter-review and reconciliation next",
        "reviewed_original_handoff_commit": "d54142e", "frozen_rule_commit": "2c39f0a",
        "replication_design_commit": "9375b3c", "late_receipt_commit": "07b5cf4",
        "history_note": "Concurrent d9c1570 includes initial tracked review fixes; history retained. Corrected numerical analysis source matches that commit; final loader/support changes have new hashes.",
        "protocol_frozen": False, "photometry_opened_by_review": False, "new_samples": 0,
        "primary_replication_verdict": "conditional frozen SPOC criteria pass after two analysis repairs",
        "replication": replication, "brightness_corrected_confirmation_pass": False,
        "end_to_end_freeze_ready": False, "certified_measurement_score_tolerance": None,
        "transit_count_restriction_adopted": False, "host_weighting": "equal-host, unchanged",
        "amended_timing_implementation_qualified": False,
        "replay": {"attempted_events": receipt["attempted_rows"], "timed_events": receipt["timed_production_events"]},
        "open_items": [
            {"owner": "Claude counter-review", "issue": "Validate corrected product selection, asymmetric containment and bounded conditional qualification."},
            {"owner": "reconciliation", "issue": "Full-support likelihood computation and separate qualification of the amended implementation."},
            {"owner": "reconciliation", "issue": "Product-level identification without forecast-residual exclusion; intended real-event denominator independent of recovery."},
            {"owner": "reconciliation", "issue": "FFI/multi-planet supported population, shared shape/lineage and exact time-boundary eligibility."},
            {"owner": "Claude", "issue": "Complete the agreed reciprocal review of sprint1, then reconcile. No further replication or protected access authorised by this handoff."}],
        "commands": commands, "source_and_product_sha256": {str(p.relative_to(ROOT)): digest(p) for p in paths},
        "output_sha256": output_hashes, "claims": ["C028", "C029", "C030"]}
    (OUT / "handoff.json").write_text(json.dumps(result, indent=2) + "\n")
    print("Verified guarded replay and archive; wrote corrected review handoff.")


if __name__ == "__main__":
    main()
