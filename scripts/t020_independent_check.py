"""Independent arithmetic check of saved T020 development outputs (stdlib only)."""

import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist, mean, median

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/t020_development"
FEATURES = ("forecast_sd_min", "age_over_baseline", "issued_line_z_rms",
            "negative_timing_count", "last_input_age_days", "space_fraction")
PADS = (0., 15., 30., 60., 120., 240.)
POLICIES = ("baseline", "triage", "proportional", "additive")
Z95 = NormalDist().inv_cdf(.975)


def read(path):
    with path.open() as handle:
        return list(csv.DictReader(handle))


def close(a, b, tolerance=1e-12):
    if not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance):
        raise AssertionError((a, b))


def comparison(rows, feature, pad):
    planets = defaultdict(list)
    for row in rows:
        planets[row["planet"]].append(row)
    values = {p: median(float(r[feature]) for r in rs) for p, rs in planets.items()}
    if not all(math.isfinite(v) for v in values.values()):
        raise AssertionError("Nonfinite ranking feature")
    flags = set(sorted(values, key=lambda p: (-values[p], p))[:math.ceil(.1*len(values))])
    base = [Z95*float(r["forecast_sd_min"]) for r in rows]
    triage = [b+pad*(r["planet"] in flags) for b, r in zip(base, rows)]
    extra = sum(t-b for t, b in zip(triage, base))
    widths = {"baseline": base, "triage": triage,
              "proportional": [b*(1+extra/sum(base)) for b in base],
              "additive": [b+extra/len(rows) for b in base]}
    budgets = {k: 2*sum(v) for k, v in widths.items()}
    for k in ("proportional", "additive"):
        close(budgets[k], budgets["triage"])
    captures = {k: [int(abs(float(r["residual_min"])) <= w) if r["residual_min"] != "" else None
                    for r, w in zip(rows, v)] for k, v in widths.items()}
    gains = {}
    for k in ("proportional", "additive"):
        by_planet = defaultdict(list)
        for r, a, b in zip(rows, captures["triage"], captures[k]):
            if a is not None:
                by_planet[r["planet"]].append(a-b)
        gains[k] = mean(mean(v) for v in by_planet.values())
    return {"feature": feature, "pad_min": pad, "minimum_gain": min(gains.values()),
            "gain_proportional": gains["proportional"], "gain_additive": gains["additive"],
            "flags": flags, "widths": widths, "captures": captures, "budgets": budgets}


def search(rows):
    candidates = [comparison(rows, f, pad) for f in FEATURES for pad in PADS]
    return min(candidates, key=lambda r: (-r["minimum_gain"], r["pad_min"], FEATURES.index(r["feature"]))), candidates


def compare_event_table(rows, result):
    for i, row in enumerate(rows):
        assert (row["flagged"] == "True") == (row["planet"] in result["flags"])
        for k in POLICIES:
            close(float(row[k+"_half_width_min"]), result["widths"][k][i])
            saved = int(row[k+"_capture"]) if row[k+"_capture"] != "" else None
            assert saved == result["captures"][k][i]


def main():
    paths = [OUT/"summary.json", OUT/"candidate_search.csv"]
    paths += [OUT/f"{setting}_{kind}_events.csv" for setting in ("c2", "zero")
              for kind in ("candidate", "crossfit")]
    summary = json.loads(paths[0].read_text())
    candidates = read(paths[1])
    expected = {(s, f, p) for s in ("c2", "zero") for f in FEATURES for p in PADS}
    keys = [(r["covariance"], r["feature"], float(r["pad_min"])) for r in candidates]
    assert len(keys) == len(set(keys)) == 72 and set(keys) == expected
    max_error, fold_checks, evidence = 0., 0, {}
    for setting in ("c2", "zero"):
        full = read(OUT/f"{setting}_candidate_events.csv")
        cross = read(OUT/f"{setting}_crossfit_events.csv")
        assert len({r["event_id"] for r in full}) == len(full)
        assert {r["event_id"] for r in full} == {r["event_id"] for r in cross}
        assert len(cross) == len(full)
        best, computed = search(full)
        saved = summary[setting]["selected_full_development_rule"]
        assert (best["feature"], best["pad_min"]) == (saved["feature"], saved["pad_min"])
        compare_event_table(full, best)
        for actual, row in zip(computed, [r for r in candidates if r["covariance"] == setting]):
            assert (actual["feature"], actual["pad_min"]) == (row["feature"], float(row["pad_min"]))
            for key in ("gain_proportional", "gain_additive", "minimum_gain"):
                error = abs(actual[key]-float(row[key]))
                max_error = max(max_error, error)
                close(actual[key], float(row[key]))
        host_folds = defaultdict(set)
        for row in cross:
            host_folds[row["host"]].add(int(row["fold"]))
        assert all(len(folds) == 1 for folds in host_folds.values())
        assert {int(r["fold"]) for r in cross} == set(range(5))
        fold_choices = []
        for choice in summary[setting]["fold_choices"]:
            fold = choice["fold"]
            train = [r for r in cross if int(r["fold"]) != fold]
            test = [r for r in cross if int(r["fold"]) == fold]
            selected, _ = search(train)
            assert (selected["feature"], selected["pad_min"]) == (choice["feature"], choice["pad_min"])
            compare_event_table(test, comparison(test, selected["feature"], selected["pad_min"]))
            fold_choices.append({"fold": fold, "feature": selected["feature"], "pad_min": selected["pad_min"]})
            fold_checks += 1
        for table, label in ((full, "resubstitution"), (cross, "host_crossfit")):
            assert all(float(r["pad_min"]) == 0 for r in table), "Current no-pad finding changed"
            for r in table:
                assert len({float(r[k+"_half_width_min"]) for k in POLICIES}) == 1
                assert len({r[k+"_capture"] for k in POLICIES}) == 1
            for k in ("proportional", "additive"):
                close(summary[setting][label]["gain"][k]["point"], 0.)
        positive = min((r for r in computed if r["pad_min"] > 0),
                       key=lambda r: (-r["minimum_gain"], r["pad_min"], FEATURES.index(r["feature"])))
        evidence[setting] = {"intended_events": len(full), "intended_planets": len({r["planet"] for r in full}),
            "accepted_events": sum(r["residual_min"] != "" for r in full),
            "selected_feature": best["feature"], "selected_pad_min": best["pad_min"],
            "fold_choices": fold_choices, "host_fold_groups_preserved": True,
            "all_selected_policy_windows_and_captures_identical": True,
            "best_positive_pad": {k: positive[k] for k in ("feature", "pad_min", "gain_proportional", "gain_additive", "minimum_gain")},
            "best_positive_pad_flagged_planets": len(positive["flags"]),
            "best_positive_pad_all_intended_minutes": positive["budgets"]}
    receipt = {"development_only": True, "uses_t020_implementation_helpers": False,
        "candidate_rows_checked": len(candidates), "fold_selections_checked": fold_checks,
        "maximum_candidate_contrast_error": max_error, "settings": evidence,
        "interpretation": "No-pad policies are identical by construction. Zero contrasts/intervals are not equivalence or power evidence.",
        "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}
    (OUT/"independent_check.json").write_text(json.dumps(receipt, indent=2, allow_nan=False)+"\n")
    print(json.dumps({k: receipt[k] for k in ("candidate_rows_checked", "fold_selections_checked", "maximum_candidate_contrast_error")}))


if __name__ == "__main__":
    main()
