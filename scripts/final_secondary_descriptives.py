"""Post-unblinding implementation of declared descriptive secondaries (9 November 2026).

Uses saved protected scores and terminal ledgers only. All score summaries give
equal weight to planets within each reported subset. The gain-host curve holds
parameters fixed and never changes the primary analysis or its decision.

    .venv/bin/python scripts/final_secondary_descriptives.py
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import fmean, median


ROOT = Path(__file__).resolve().parents[1]
METHODS = ("M0", "M1", "M2", "M3")
METRICS = ("is95_standardised", "is95_minutes", "is95_forecast_normalised",
           "negative_log_score_seconds", "covered68", "covered95", "width95_minutes")
LEAD_BANDS = ("(0,1] years", "(1,3] years", "(3,5] years", ">5 years", "nonpositive", "unknown")
TMAG_BANDS = ("<10", "[10,11)", "[11,12)", "[12,13.5)", ">=13.5", "unknown")
TTV_LABELS = ("current_archive_flagged", "current_archive_unflagged_physical_status_unknown", "unknown")
SETS = {
    "primary": {"directory": "final_primary", "cohort": "core", "forecast": "forecasts_core_draft.csv.gz"},
    "exploratory_extension": {"directory": "final_extension", "cohort": "extension",
                              "forecast": "forecasts_extension_draft.csv.gz"},
}


def read_csv(path):
    path = Path(path)
    with (gzip.open(path, "rt", newline="") if path.suffix == ".gz" else path.open(newline="")) as handle:
        return list(csv.DictReader(handle))


def finite_or_none(value):
    try:
        number = float(value)
    except (ValueError, TypeError):
        return None
    return number if math.isfinite(number) else None


def numeric_anchor_jd(anchor):
    stamp = datetime.fromisoformat(anchor.replace("Z", "+00:00"))
    if stamp.tzinfo is None:
        raise ValueError("availability anchor must have a time zone")
    return stamp.timestamp() / 86400 + 2440587.5


def lead_band(years):
    if years is None:
        return "unknown"
    if years <= 0:
        return "nonpositive"
    for bound, label in zip((1, 3, 5), LEAD_BANDS):
        if years <= bound:
            return label
    return ">5 years"


def tmag_band(tmag):
    if tmag is None:
        return "unknown"
    for bound, label in zip((10, 11, 12, 13.5), TMAG_BANDS):
        if tmag < bound:
            return label
    return ">=13.5"


def coverage_state(value):
    if value in (True, "True", "true", "1"):
        return True
    if value in (False, "False", "false", "0"):
        return False
    if value in (None, ""):
        return None
    raise ValueError(f"unrecognised coverage state: {value!r}")


def unique_rows(rows, key, label):
    result = {}
    for row in rows:
        identity = row[key]
        if identity in result:
            raise ValueError(f"duplicate {label}: {identity}")
        result[identity] = row
    return result


def validate_scores(rows, events):
    expected = {r["event_id"] for r in events if r["status"] == "accepted"}
    metadata = {r["event_id"]: r for r in events}
    scores = defaultdict(dict)
    for row in rows:
        identity, method = row["event_id"], row["method"]
        if identity not in expected or method not in METHODS:
            raise ValueError(f"score outside accepted event/method contract: {identity}, {method}")
        if method in scores[identity]:
            raise ValueError(f"duplicate event-method score: {identity}, {method}")
        if any(row[k] != metadata[identity][k] for k in ("planet", "host")):
            raise ValueError(f"score identity mismatch: {identity}")
        metrics = {key: finite_or_none(row[key]) for key in METRICS}
        if any(value is None for value in metrics.values()):
            raise ValueError(f"nonfinite score metric: {identity}, {method}")
        if any(metrics[key] not in (0.0, 1.0) for key in ("covered68", "covered95")):
            raise ValueError(f"invalid coverage indicator: {identity}, {method}")
        scores[identity][method] = metrics
    if set(scores) != expected or any(set(scores[e]) != set(METHODS) for e in expected):
        raise ValueError("scores do not exactly cover every accepted event for M0-M3")
    return dict(scores)


def per_planet_scores(events, scores):
    grouped = defaultdict(list)
    for event in events:
        if event["status"] == "accepted":
            grouped[event["planet"]].append(event)
    result = {}
    for planet, rows in sorted(grouped.items()):
        result[planet] = {method: {key: fmean(scores[r["event_id"]][method][key] for r in rows)
                                  for key in METRICS} for method in METHODS}
    return result


def summarize(events, scores):
    planets = defaultdict(list)
    for row in events:
        planets[row["planet"]].append(row)
    accepted = [r for r in events if r["status"] == "accepted"]
    qualified = [r for r in events if r["coverage_qualified"] is True]
    qualified_accepted = [r for r in qualified if r["status"] == "accepted"]
    pmeans = per_planet_scores(events, scores)
    deltas = [p["M2"]["is95_standardised"] - p["M0"]["is95_standardised"] for p in pmeans.values()]
    planet_recovery = [sum(r["status"] == "accepted" for r in rs) / len(rs) for rs in planets.values()]
    planet_qualified_recovery = []
    for rows in planets.values():
        qs = [r for r in rows if r["coverage_qualified"] is True]
        if qs:
            planet_qualified_recovery.append(sum(r["status"] == "accepted" for r in qs) / len(qs))
    counts = {
        "intended_events": len(events), "intended_planets": len(planets),
        "intended_hosts": len({r["host"] for r in events}), "accepted_events": len(accepted),
        "accepted_planets": len(pmeans), "accepted_hosts": len({r["host"] for r in accepted}),
        "coverage_qualified_events": len(qualified),
        "coverage_qualified_planets": len(planet_qualified_recovery),
        "coverage_unqualified_events": sum(r["coverage_qualified"] is False for r in events),
        "coverage_unknown_events": sum(r["coverage_qualified"] is None for r in events),
        "accepted_coverage_qualified_events": len(qualified_accepted),
        "accepted_coverage_unqualified_events": sum(r["coverage_qualified"] is False for r in accepted),
        "accepted_coverage_unknown_events": sum(r["coverage_qualified"] is None for r in accepted),
        "event_recovery_all_intended": len(accepted) / len(events) if events else None,
        "planet_balanced_recovery_all_intended": fmean(planet_recovery) if planet_recovery else None,
        "event_recovery_coverage_qualified": len(qualified_accepted) / len(qualified) if qualified else None,
        "planet_balanced_recovery_coverage_qualified": fmean(planet_qualified_recovery) if planet_qualified_recovery else None,
        "M2_minus_M0_mean_planet_delta": fmean(deltas) if deltas else None,
        "M2_minus_M0_median_planet_delta": median(deltas) if deltas else None,
        "fraction_planets_improved": fmean(d < 0 for d in deltas) if deltas else None,
        "terminal_status_counts": json.dumps(dict(sorted(Counter(r["status"] for r in events).items())),
                                             separators=(",", ":")),
    }
    model_metrics = {method: {key: fmean(p[method][key] for p in pmeans.values()) if pmeans else None
                              for key in METRICS} for method in METHODS}
    return counts, model_metrics


def gain_host_influence(planets, max_k=5):
    """Rank negative host sums/N, keep hosts whole, and reweight remaining planets."""
    by_host = defaultdict(list)
    for row in planets:
        if row["delta"] is not None:
            by_host[row["host"]].append(row)
    number = sum(map(len, by_host.values()))
    ranking = []
    for host, rows in by_host.items():
        total = math.fsum(r["delta"] for r in rows)
        ranking.append({"host": host, "planets": ";".join(sorted(r["planet"] for r in rows)),
                        "accepted_planets": len(rows), "sum_planet_deltas": total,
                        "contribution_to_original_mean": total / number,
                        "gain_host": total < 0})
    ranking.sort(key=lambda r: (r["contribution_to_original_mean"], r["host"]))
    gain_hosts = [r["host"] for r in ranking if r["gain_host"]]
    for rank, row in enumerate(ranking, 1):
        row["rank_all_hosts"] = rank
        row["rank_gain_hosts"] = gain_hosts.index(row["host"]) + 1 if row["gain_host"] else None
    curve = []
    for k in range(max_k + 1):
        available = k <= len(gain_hosts)
        removed = gain_hosts[:k] if available else []
        remaining = [r for rows in by_host.values() for r in rows if r["host"] not in removed] if available else []
        ds = [r["delta"] for r in remaining]
        curve.append({"k": k, "available": available, "gain_hosts_available": len(gain_hosts),
                      "removed_hosts": ";".join(removed),
                      "removed_planets": number - len(remaining) if available else None,
                      "remaining_planets": len(remaining) if available else None,
                      "remaining_hosts": len({r["host"] for r in remaining}) if available else None,
                      "mean_planet_delta": fmean(ds) if ds else None,
                      "median_planet_delta": median(ds) if ds else None,
                      "fraction_planets_improved": fmean(d < 0 for d in ds) if ds else None,
                      "reason": "" if ds else "fewer than k gain hosts" if not available else "no remaining accepted planets"})
    return ranking, curve


def load_inputs(root):
    config_path = root / "configs/candidate_freeze.json"
    config = json.loads(config_path.read_text())
    roster_path = root / config["roster"]
    roster = unique_rows(read_csv(roster_path), "planet", "roster planet")
    anchor_jd = numeric_anchor_jd(config["availability_anchor_utc"])
    paths, events_by_set, scores_by_set = [config_path, roster_path], {}, {}
    for label, spec in SETS.items():
        base = root / "results" / spec["directory"]
        ledger_path, score_path = base / "terminal_ledger.csv.gz", base / "scores.csv"
        forecast_path = root / "results/prefreeze" / spec["forecast"]
        forecasts = unique_rows(read_csv(forecast_path), "event_id", "forecast event")
        ledger = unique_rows(read_csv(ledger_path), "event_id", "terminal event")
        if set(forecasts) != set(ledger):
            raise ValueError(f"forecast/terminal event sets differ: {label}")
        events = []
        for identity, row in sorted(ledger.items()):
            fc, rr = forecasts[identity], roster[row["planet"]]
            if any(row[k] != fc[k] or row[k] != rr[k] for k in ("planet", "host")):
                raise ValueError(f"forecast/ledger/roster identity mismatch: {identity}")
            if rr["cohort"] != spec["cohort"]:
                raise ValueError(f"wrong roster cohort: {identity}")
            predicted = finite_or_none(fc["predicted_bjd_tdb"])
            lead = (predicted - anchor_jd) / 365.25 if predicted is not None else None
            tmag = finite_or_none(rr["tmag"])
            events.append({**row, "analysis_set": label, "cohort": rr["cohort"], "tmag": tmag,
                           "tmag_band": tmag_band(tmag), "lead_years_proxy": lead,
                           "lead_band": lead_band(lead), "covariance_tier": fc.get("covariance_tier") or "unknown",
                           "product": "SPOC_120", "coverage_qualified": coverage_state(row["coverage_ok_at_prediction"])})
        events_by_set[label] = events
        scores_by_set[label] = validate_scores(read_csv(score_path), events)
        paths.extend((ledger_path, score_path, forecast_path))
    if set(scores_by_set["primary"]) & set(scores_by_set["exploratory_extension"]):
        raise ValueError("primary and extension accepted event IDs overlap")
    if {r["planet"] for rs in events_by_set.values() for r in rs} != set(roster):
        raise ValueError("manifest planets do not exactly cover the frozen roster")
    return config, paths, events_by_set, scores_by_set


def join_ttv_labels(event_sets, label_rows):
    """Join independently selected current labels; uncertainty never removes an event."""
    by_planet = defaultdict(list)
    for row in label_rows:
        by_planet[row["planet"]].append(row)
    targets = {}
    for events in event_sets.values():
        for event in events:
            targets[event["planet"]] = event
    joined = {}
    for planet, target in sorted(targets.items()):
        candidates = by_planet.get(planet, [])
        label, status = "unknown", "missing_label_row"
        if len(candidates) > 1:
            status = "ambiguous_label_rows"
        elif candidates:
            row = candidates[0]
            if any(row.get(key) != target[key] for key in ("host", "cohort")):
                status = "identity_mismatch"
            else:
                expected = {"0": TTV_LABELS[1], "1": TTV_LABELS[0]}.get(row.get("archive_ttv_flag"))
                supplied = row.get("current_catalogue_ttv_label")
                if expected is not None and supplied == expected:
                    label, status = supplied, "matched"
                else:
                    status = "unknown_or_inconsistent_catalogue_label"
        joined[planet] = {"current_catalogue_ttv_label": label, "ttv_label_match_status": status,
                          "ttv_discovery_date": "unknown", "new_since_origin": "unknown"}
    for events in event_sets.values():
        for event in events:
            event.update(joined[event["planet"]])
    return {"target_planets": len(targets),
            "metadata_planets_not_in_analysis": sorted(set(by_planet) - set(targets)),
            "current_label_counts": dict(sorted(Counter(r["current_catalogue_ttv_label"] for r in joined.values()).items())),
            "match_status_counts": dict(sorted(Counter(r["ttv_label_match_status"] for r in joined.values()).items()))}


def write_csv(path, rows):
    if not rows:
        raise ValueError(f"no output schema for {path}")
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def build(root, out, implementation_date="2026-11-09"):
    config, inputs, event_sets, score_sets = load_inputs(root)
    ttv_directory = root / "results/final_secondaries/ttv"
    ttv_labels_path, ttv_provenance_path = ttv_directory / "labels.csv", ttv_directory / "provenance.json"
    ttv_note_path = ttv_directory / "SOURCE_NOTE.md"
    ttv_provenance = json.loads(ttv_provenance_path.read_text())
    if hashlib.sha256(ttv_labels_path.read_bytes()).hexdigest() != ttv_provenance["labels_sha256"]:
        raise ValueError("current TTV labels differ from the independently recorded provenance")
    if hashlib.sha256(ttv_note_path.read_bytes()).hexdigest() != ttv_provenance["source_note_sha256"]:
        raise ValueError("current TTV source note differs from the independently recorded provenance")
    ttv_join = join_ttv_labels(event_sets, read_csv(ttv_labels_path))
    inputs.extend((ttv_labels_path, ttv_provenance_path, ttv_note_path))
    ttv_source = {"ttv_source": ttv_provenance["source"],
                  "ttv_source_url": "https://doi.org/" + ttv_provenance["source_dataset_doi"],
                  "ttv_retrieval_date_hobart": ttv_provenance["retrieval_date_hobart"]}
    combined = [row for rows in event_sets.values() for row in rows]
    combined_scores = {key: value for scores in score_sets.values() for key, value in scores.items()}
    event_sets["combined_descriptive"] = combined
    score_sets["combined_descriptive"] = combined_scores
    covariance_tiers = tuple(config["forecasts"]["covariance_tiers"]) + ("unknown",)
    if any(r["covariance_tier"] not in covariance_tiers for r in combined):
        raise ValueError("unrecognised covariance tier")
    axes = {"overall": ("all",), "lead_band": LEAD_BANDS, "tmag_band": TMAG_BANDS,
            "covariance_tier": covariance_tiers, "cohort": ("core", "extension"), "product": ("SPOC_120",),
            "current_catalogue_ttv_label": TTV_LABELS}
    recovery, summaries, planet_metrics, planet_deltas, rankings, curves = [], [], [], [], [], []
    for label, events in event_sets.items():
        scores = score_sets[label]
        for axis, cells in axes.items():
            for cell in cells:
                subset = events if axis == "overall" else [r for r in events if r[axis] == cell]
                identity = {"analysis_set": label, "stratum": axis, "cell": cell}
                if axis == "current_catalogue_ttv_label":
                    identity.update(ttv_source)
                counts, models = summarize(subset, scores)
                recovery.append({**identity, **counts})
                for method in METHODS:
                    summaries.append({**identity, "method": method, "accepted_events": counts["accepted_events"],
                                      "accepted_planets": counts["accepted_planets"],
                                      "accepted_hosts": counts["accepted_hosts"], **models[method]})
        grouped = defaultdict(list)
        for row in events:
            grouped[row["planet"]].append(row)
        deltas = []
        for planet, rows in sorted(grouped.items()):
            counts, models = summarize(rows, scores)
            meta = rows[0]
            identity = {"analysis_set": label, "planet": planet, "host": meta["host"],
                        "cohort": meta["cohort"], "tmag": meta["tmag"], "tmag_band": meta["tmag_band"],
                        "covariance_tier": meta["covariance_tier"],
                        **{key: meta[key] for key in ("current_catalogue_ttv_label", "ttv_label_match_status",
                                                     "ttv_discovery_date", "new_since_origin")}}
            pd = {**identity, **counts, "delta": counts["M2_minus_M0_mean_planet_delta"]}
            planet_deltas.append(pd)
            deltas.append(pd)
            for method in METHODS:
                planet_metrics.append({**identity, "method": method, "intended_events": len(rows),
                                       "accepted_events": counts["accepted_events"], **models[method]})
        ranking, curve = gain_host_influence(deltas)
        rankings.extend({"analysis_set": label, **r} for r in ranking)
        curves.extend({"analysis_set": label, **r} for r in curve)
    out.mkdir(parents=True, exist_ok=True)
    outputs = {"recovery_by_stratum.csv": recovery, "scores_by_stratum.csv": summaries,
               "planet_metrics.csv": planet_metrics, "planet_deltas.csv": planet_deltas,
               "gain_host_ranking.csv": rankings, "leave_gain_hosts_out.csv": curves}
    for filename, rows in outputs.items():
        write_csv(out / filename, rows)
    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()
    receipt = {
        "kind": "declared descriptive protected secondaries; post-unblinding implementation",
        "implementation_date": implementation_date, "generated_utc": datetime.now(timezone.utc).isoformat(),
        "script_sha256": sha(Path(__file__)),
        "frozen_manifest_sha256": sha(root / "results/freeze/freeze_manifest.json"),
        "inputs_sha256": {str(p.relative_to(root)): sha(p) for p in inputs},
        "outputs_sha256": {name: sha(out / name) for name in outputs},
        "conventions": {
            "score_weighting": "equal planets within every subset; equal accepted events within each planet; saved full-cohort weight column ignored",
            "metrics": list(METRICS), "score_scope": "conditional on accepted timings; no imputation",
            "lead_time": {"anchor_utc": config["availability_anchor_utc"],
                          "numeric_anchor_jd": numeric_anchor_jd(config["availability_anchor_utc"]),
                          "formula": "(frozen predicted_bjd_tdb - numeric UTC JD anchor) / 365.25",
                          "qualification": "coarse metadata proxy; UTC and BJD_TDB have not been converted to a common scale or reference; not an exact UTC-to-BJD conversion",
                          "bands": list(LEAD_BANDS)},
            "tmag": {"source": config["roster"], "bands": list(TMAG_BANDS),
                     "status": f"existing development bin boundaries adopted for protected descriptive reporting on {implementation_date}, after unblinding; not fixed original protected bins",
                     "continuous_table": "planet_metrics.csv and planet_deltas.csv retain continuous Tmag"},
            "covariance_tier": "from frozen forecasts, including C3; not inferred from protected outcomes",
            "product": "SPOC_120 only, from the frozen SPOC 120-s PDCSAP scope; no other product comparison is available",
            "recovery": "accepted/all intended and accepted among coverage-qualified/coverage-qualified; qualification requires both saved prediction window and in-transit coverage >=0.75 (terminal ledger boolean); unknown stays separate; planet-balanced recovery averages planet-specific fractions over planets with a denominator",
            "coverage_at_prediction_role": "recovery denominator diagnostic, not a timing acceptance gate; accepted timings with unqualified prediction coverage remain accepted and scored",
            "current_catalogue_ttv": {**ttv_source, **ttv_join,
                                      "scope": "current catalogue flag diagnostic retrieved after unblinding; source selected independently without reading scores; descriptive only",
                                      "labels": list(TTV_LABELS),
                                      "limits": "raw flag 0 means catalogue-unflagged with physical TTV status unknown, never no-TTV; missing, ambiguous or mismatched joins remain unknown; retrieval and parameter dates are not TTV discovery dates; new-since-origin status remains unknown; no cohort exclusions or primary changes"},
            "influence": "fixed per-planet M2-M0 standardized IS95; host contribution=sum(planet deltas)/original N; rank negative contributions ascending, alphabetical host ties; remove whole hosts and give remaining planets equal weight; k=0..5; k beyond available gain hosts is explicitly unavailable",
            "combined_descriptive": "core and extension pooled only for description, with equal planets; does not change either frozen analysis",
            "empty_cells": "zero counts and blank metrics; planets without accepted timings remain in recovery and continuous tables, with blank scores/deltas",
            "inference": "descriptive only; no subgroup significance rule, bootstrap/refit, primary exclusion or revised primary decision",
        },
        "rows": {name: len(rows) for name, rows in outputs.items()},
    }
    (out / "receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--out", type=Path, default=ROOT / "results/final_secondaries/descriptive")
    parser.add_argument("--implementation-date", default="2026-11-09")
    args = parser.parse_args()
    receipt = build(args.root.resolve(), args.out.resolve(), args.implementation_date)
    print(json.dumps({"output": str(args.out), "rows": receipt["rows"]}))


if __name__ == "__main__":
    main()
