"""Check the bounded contrast of fixed nested interval scores (C049)."""

import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def interval_score(lo, hi, y):
    return hi - lo + 40 * (max(lo - y, 0) + max(y - hi, 0))


def main():
    examples = []
    maximum_error = 0.0
    for d_left, d_right in ((1., 1.), (.25, 2.), (0., 3.)):
        lower, upper = -1., 1.
        width_change = d_left + d_right
        lower_bound = width_change - 40 * max(d_left, d_right)
        for y in (-1e6, -10., -3., -1., 0., 1., 3., 10., 1e6):
            contrast = (interval_score(lower - d_left, upper + d_right, y)
                        - interval_score(lower, upper, y))
            formula = width_change - 40 * (
                min(d_left, max(lower - y, 0))
                + min(d_right, max(y - upper, 0)))
            maximum_error = max(maximum_error, abs(contrast - formula))
            assert lower_bound - 1e-9 <= contrast <= width_change + 1e-9
            examples.append(dict(d_left=d_left, d_right=d_right, y=y,
                                 delta=contrast, bounds=[lower_bound, width_change]))
    assert maximum_error < 1e-9
    score_path = ROOT / "results/final_primary/scores.csv"
    by_event = defaultdict(dict)
    for row in csv.DictReader(score_path.open()):
        if row["method"] in ("M0", "M2"):
            by_event[row["event_id"]][row["method"]] = row
    violations = []
    for event_id, pair in by_event.items():
        m0, m2 = pair["M0"], pair["M2"]
        delta = float(m2["is95_standardised"]) - float(m0["is95_standardised"])
        width_delta = (float(m2["width95_minutes"]) - float(m0["width95_minutes"])) * 60
        width_delta /= float(m0["m0_predictive_sd_s"])
        if delta > width_delta + 1e-9:
            violations.append(event_id)
    assert not violations
    report = {
        "claim": "C049", "alpha": .05,
        "formula": "DeltaIS = dw - 40[min(dL,(l0-y)+) + min(dU,(y-u0)+)]",
        "nested_bounds": "dw - 40 max(dL,dU) <= DeltaIS <= dw",
        "symmetric_bounds": "-19 dw <= DeltaIS <= dw",
        "scope": "Fixed endpoints and positive common standardisation; no bound across varying interval widths.",
        "max_formula_error": maximum_error, "synthetic_examples": examples,
        "saved_events_checked": len(by_event), "penalty_above_added_width": violations,
        "observed_check_limit": "Checks the observed score/width inequality, not interval nesting or new inference.",
        "input_sha256": {str(score_path.relative_to(ROOT)): hashlib.sha256(score_path.read_bytes()).hexdigest()},
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    dest = ROOT / "results/final_review/d068_interval_score.json"
    dest.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"synthetic_cases": len(examples), "events": len(by_event),
                      "max_formula_error": maximum_error, "all_checks_pass": True}))


if __name__ == "__main__":
    main()
