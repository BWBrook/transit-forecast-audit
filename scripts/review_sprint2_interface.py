"""Replay existing development I1 rows, preserving numerical-support failures."""
from pathlib import Path
from argparse import Namespace
from collections import Counter
import csv
import json
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import forecast_variance_components as f
import sprint1_forecast_core as core
import sprint1_forecasts as s1
import sprint1_outcome_adapter as adapter
import sprint2_forecasts as s2


def main():
    source = ROOT / "data/derived/outcomes/t015v3/outcomes.csv"
    dest = ROOT / "data/derived/sprint2_review/interface"
    report = ROOT / "results/sprint2_review/interface"
    dest.mkdir(parents=True, exist_ok=True)
    report.mkdir(parents=True, exist_ok=True)
    paths = [source, ROOT / "scripts/sprint1_forecast_core.py",
             ROOT / "scripts/sprint1_forecasts.py", ROOT / "scripts/sprint1_outcome_adapter.py",
             ROOT / "scripts/sprint2_forecasts.py", Path(__file__)]
    hashes = {str(p.relative_to(ROOT)): core.digest(p) for p in paths}
    eph, _, flags = s2.load()
    covariance = core.covariance_rows()
    rows, failures = [], []
    for original in csv.DictReader(source.open()):
        planet = original["planet"]
        if planet not in eph["DRC"] or planet in flags["DRC"] or ("DRC", planet) not in covariance:
            continue
        reference = float(original.get("tc_bjd_tdb") or original.get("window_centre_bjd_tdb") or original["predicted_bjd_tdb_drd"])
        if not "2022-09-28" <= s2.bjd_date(reference) <= "2024-01-03":
            continue
        row = dict(original)
        ephemeris = eph["DRC"][planet]
        row.update(forecast_epoch=round((reference-ephemeris.t0_bjd_tdb)/ephemeris.period_days),
                   epoch_basis="development nearest DRC epoch; independent scheduled identity unresolved",
                   error_convention="t015v3_beta_chi")
        if row["status"] == "timed":
            bad = set(row.get("flags", "").split(";")) & {"edge", "mass_outside_fine", "coarse_fine_shift"}
            reason = "unresolved timing integration: " + ",".join(sorted(bad)) if bad else ""
            if not reason and row.get("posterior_grid_path"):
                try:
                    adapter.likelihood_grid(ROOT / row["posterior_grid_path"])
                except ValueError as exc:
                    reason = str(exc)
            if reason:
                row.update(status="integration_unresolved", failure_reason=reason)
                failures.append({"event_id": row["event_id"], "reason": reason, "original_status": "timed"})
        rows.append(row)
    outcome_path, forecast_path, score_path = [dest / name for name in ("outcomes.csv", "forecasts.csv", "scores.csv")]
    parameters = ROOT / "results/sprint2/forecasts/parameters_release_transfer_ours_all_raw.json"
    hashes[str(parameters.relative_to(ROOT))] = core.digest(parameters)
    f.write_csv(outcome_path, rows)
    s1.make_forecasts(Namespace(events=str(outcome_path), parameters=str(parameters), release="DRC", covariance="c2", output=str(forecast_path)))
    adapter.score_outcomes(Namespace(forecasts=str(forecast_path), outcomes=str(outcome_path), error_convention="t015v3_beta_chi", outcome_scale=1.0, output=str(score_path)))
    raw_scores = list(csv.DictReader(score_path.open()))
    forecasts = {row["event_id"]: row for row in csv.DictReader(forecast_path.open())}
    selected, _ = adapter.production_rows(rows)
    events = [{**r, "release": "DRC", "outcome_scale": 1.0, "sigma_s": float(r["sigma_s"]),
               "residual_s": (float(r["tc_bjd_tdb"])-float(forecasts[r["event_id"]]["predicted_bjd_tdb"]))*86400,
               "forecast_variance_s2": float(forecasts[r["event_id"]]["forecast_variance_s2"])}
              for r in selected if r["status"] == "timed"]
    scores = {method: {key: np.array([float(r[key]) for r in raw_scores if r["method"] == method])
                       for key in ("is95_standardised", "is95_minutes", "is95_forecast_normalised", "negative_log_score_seconds", "covered68", "covered95", "width95_minutes")}
              for method in core.METHODS}
    models = json.loads(parameters.read_text())["models"]
    gaussian = {method: core.predictive_scores(events, models[method]) for method in core.METHODS}
    assert all(core.digest(ROOT / path) == value for path, value in hashes.items()), "Source drift during replay"
    receipt = json.loads(score_path.with_suffix(".receipt.json").read_text())
    (report / "score_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
    if failures:
        f.write_csv(report / "support_failures.csv", failures)
    result = {"source_sha256": hashes, "source_unchanged_during_run": True,
              "status_counts_all_attempts": dict(Counter(r["status"] for r in rows)),
              "support_failures": len(failures), "timed_events": len(events),
              "exact_likelihood_scores": core.aggregate(events, scores),
              "gaussian_approximation_same_events": core.aggregate(events, gaussian),
              "qualification": "Fixed development parameters; Gaussian visit likelihood used for original fitting; no bootstrap or rule qualification from this replay. Epoch identity remains unresolved.",
              "protected_photometry_accessed": False}
    (report / "summary.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k:result[k] for k in ("timed_events", "support_failures", "status_counts_all_attempts")}), flush=True)


if __name__ == "__main__":
    main()
