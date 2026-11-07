"""Sprint 2: rerun the closed M0-M3 development comparison under each outcome convention (R5, S1-03).

For the release-transfer and chronological designs of configs/sprint1.json:

* exoclock_matched: catalogue timings x a=1.087, restricted to transits that
  the t015v3 pipeline also timed (same planet, epoch and product window);
* ours_matched: the same transits, t015v3 mid-times and sigma x 1;
* ours_all: every t015v3 timed transit in the window (production convention);
* exoclock_all: the sprint-1 catalogue comparison, recomputed for reference.

R5 acceptance: transfer holds if the matched comparisons agree in the sign of
the primary M2-M0 contrast and in the decision (improves / worsens /
inconclusive). Uses the sprint-1 fitting, scoring and host-refit code unchanged.

    .venv/bin/python scripts/sprint2_forecasts.py run [--bootstrap 400]
    .venv/bin/python scripts/sprint2_forecasts.py interface
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import forecast_variance_components as fvc  # noqa: E402
import sprint1_forecast_core as c  # noqa: E402
import sprint1_forecasts as s1  # noqa: E402
from reproduce_table5 import load  # noqa: E402
from transit_audit.exoclock import host_of  # noqa: E402

RULE = "t015v3"
OUTCOMES = ROOT / "data" / "derived" / "outcomes" / RULE / "outcomes.csv"
OUT = ROOT / "results" / "sprint2" / "forecasts"
DERIVED = ROOT / "data" / "derived" / "sprint2"


def bjd_date(jd):
    return str(np.datetime64("1970-01-01") + np.timedelta64(int(np.floor(jd - 2440587.5)), "D"))


def our_events(release, start, end, rows, eph, flags, cov, setting="c2", a=1.0):
    out, rejected = [], []
    for r in rows:
        if r["status"] != "timed" or r["planet"] not in eph[release]:
            continue
        tc = float(r["tc_bjd_tdb"])
        date = bjd_date(tc)
        if not start <= date <= end:
            continue
        p = r["planet"]
        if p in flags[release]:
            rejected.append({"planet": p, "event_id": r["event_id"], "reason": "origin_TTV_flag"})
            continue
        if (release, p) not in cov:
            rejected.append({"planet": p, "event_id": r["event_id"], "reason": "missing_covariance_reconstruction"})
            continue
        e = eph[release][p]
        n = int(np.rint((tc - e.t0_bjd_tdb) / e.period_days))
        rho = c.correlation(release, p, setting, cov)
        pred = e.t0_bjd_tdb + n * e.period_days
        disc = abs(float(cov[release, p]["p_refit_minus_published_s"])) / (e.sigma_period_days * 86400)
        vf = float(c.forecast_variance(e.sigma_t0_days * 86400, e.sigma_period_days * 86400, n, rho))
        out.append({"event_id": r["event_id"], "observation_id": r["observation_id"], "planet": p, "host": host_of(p),
                    "release": release, "source_record_date": date, "tc_bjd_tdb": tc, "sigma_s": float(r["sigma_s"]),
                    "outcome_scale": a, "forecast_epoch": n, "predicted_bjd_tdb": pred,
                    "residual_s": (tc - pred) * 86400, "sigma_t0_s": e.sigma_t0_days * 86400,
                    "sigma_p_s": e.sigma_period_days * 86400, "rho": rho, "covariance_setting": setting,
                    "covariance_tier": "C2_candidate" if disc <= 3 else "C3_source_fit_mismatch",
                    "period_fit_discrepancy_sigma": disc, "forecast_variance_s2": vf,
                    "issue_date": c.ISSUE_DATES[release],
                    "horizon_days": (np.datetime64(date) - np.datetime64(c.ISSUE_DATES[release])).astype(int).item(),
                    "status": "timed", "error_convention": "t015v3_beta_chi", "shape_group_id": r["shape_group_id"],
                    "gauss_ok": r["gauss_ok"], "product": r["product"],
                    "cycle_margin_sigma": (e.period_days * 86400 / 2) / np.sqrt(vf + float(r["sigma_s"]) ** 2)})
    return sorted(out, key=lambda r: (r["planet"], r["tc_bjd_tdb"])), rejected


def match(ours, cat):
    by = {}
    for r in cat:
        by.setdefault((r["planet"], r["forecast_epoch"]), []).append(r)
    pairs = []
    for r in ours:
        cands = [x for x in by.get((r["planet"], r["forecast_epoch"]), []) if abs(x["tc_bjd_tdb"] - r["tc_bjd_tdb"]) < 0.05]
        if cands:
            pairs.append((r, min(cands, key=lambda x: abs(x["tc_bjd_tdb"] - r["tc_bjd_tdb"]))))
    seen, out = set(), []
    for r, x in pairs:
        if x["event_id"] in seen:
            continue
        seen.add(x["event_id"])
        out.append((r, x))
    return out


def compare(name, train, test, reps, seed):
    if not train or not test:
        return {"experiment": name, "status": "empty", "train_events": len(train), "test_events": len(test)}
    tp_ = c.visit_planets(train)
    models = c.fit_methods(tp_)
    scores = {m: c.predictive_scores(test, models[m]) for m in c.METHODS}
    agg = c.aggregate(test, scores)
    _, intervals = s1.uncertainty(tp_, test, models, reps, seed)
    return {"experiment": name, "train_events": len(train), "train_planets": len(tp_),
            "train_hosts": len({p["host"] for p in tp_}), "test_events": len(test),
            "test_planets": len({r["planet"] for r in test}), "test_hosts": len({r["host"] for r in test}),
            "models": models, "metrics": agg, "host_refit": intervals,
            "influence": s1.influence(test, scores, {p["planet"] for p in tp_})}


def run(args):
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows = list(csv.DictReader(OUTCOMES.open()))
    OUT.mkdir(parents=True, exist_ok=True)
    DERIVED.mkdir(parents=True, exist_ok=True)
    summary = {"outcomes_sha256": c.digest(OUTCOMES), "bootstrap": args.bootstrap, "seed": cfg["seed"],
               "reference_a": c.REFERENCE_A, "experiments": {}}
    for exp in ("release_transfer", "chronological"):
        spec = cfg["experiments"][exp]
        sets = {}
        for part in ("train", "test"):
            sp = spec[part]
            cat, _ = c.development_events(**sp, a=c.REFERENCE_A)
            ours, rej = our_events(sp["release"], sp["start"], sp["end"], rows, eph, flags, cov)
            pairs = match(ours, cat)
            sets[part] = {"exoclock_all": cat, "ours_all": ours,
                          "exoclock_matched": [x for _, x in pairs], "ours_matched": [r for r, _ in pairs],
                          "pairs": pairs, "rejected": rej}
        res = {}
        for variant in ("exoclock_matched", "ours_matched", "ours_all", "exoclock_all"):
            res[variant] = compare(f"{exp}|{variant}", sets["train"][variant], sets["test"][variant],
                                   args.bootstrap, cfg["seed"])
            m = res[variant].get("metrics", {}).get("M2", {})
            print(exp, variant, res[variant].get("train_planets"), res[variant].get("test_events"),
                  "M2 delta", m.get("delta_standardised_vs_M0"),
                  res[variant].get("host_refit", {}).get("M2", {}).get("delta_is95_standardised_percentile95"), flush=True)
        pairs = sets["test"]["pairs"] + sets["train"]["pairs"]
        d = np.array([(r["tc_bjd_tdb"] - x["tc_bjd_tdb"]) * 86400 for r, x in pairs])
        sr = np.array([r["sigma_s"] / x["sigma_s"] for r, x in pairs])
        z = d / np.sqrt([r["sigma_s"] ** 2 + x["sigma_s"] ** 2 for r, x in pairs])
        dec = {v: res[v].get("host_refit", {}).get("M2", {}).get("conditional_decision") for v in res}
        sign = {v: np.sign(res[v]["metrics"]["M2"]["delta_standardised_vs_M0"]) if "metrics" in res[v] else None for v in res}
        res["transfer"] = {
            "matched_pairs": len(pairs), "median_delta_s": round(float(np.median(d)), 2),
            "z_rms_same_photons": round(float(np.sqrt(np.mean(z ** 2))), 3),
            "median_sigma_ratio_ours_over_exoclock": round(float(np.median(sr)), 4),
            "sigma_ratio_iqr": [round(float(v), 4) for v in np.percentile(sr, [25, 75])],
            "decisions": dec, "signs": {k: float(v) if v is not None else None for k, v in sign.items()},
            "R5_transfer_accepted": bool(dec["exoclock_matched"] == dec["ours_matched"]
                                         and sign["exoclock_matched"] == sign["ours_matched"]),
            "cycle_margin_sigma_min_ours_all": round(float(min(r["cycle_margin_sigma"] for r in sets["test"]["ours_all"])), 1)}
        res["coverage_of_catalogue"] = {part: {"catalogue_events": len(sets[part]["exoclock_all"]),
                                               "catalogue_planets": len({r["planet"] for r in sets[part]["exoclock_all"]}),
                                               "matched_events": len(sets[part]["pairs"]),
                                               "ours_events": len(sets[part]["ours_all"]),
                                               "ours_planets": len({r["planet"] for r in sets[part]["ours_all"]}),
                                               "ours_rejected": len(sets[part]["rejected"])}
                                        for part in ("train", "test")}
        summary["experiments"][exp] = res
        for part in ("train", "test"):
            fvc.write_csv(DERIVED / f"{exp}_{part}_ours_all.csv", sets[part]["ours_all"])
    (OUT / "convention_comparison.json").write_text(json.dumps(summary, indent=1, default=float) + "\n")


def interface(args):
    """I1 -> I2 replay on production outcomes: make_forecasts then score, every attempted DRC-era row."""
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    sp = cfg["experiments"]["release_transfer"]["test"]
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows = list(csv.DictReader(OUTCOMES.open()))
    keep = []
    for r in rows:
        p = r["planet"]
        ref = float(r["tc_bjd_tdb"]) if r.get("tc_bjd_tdb") else float(r.get("window_centre_bjd_tdb") or r.get("predicted_bjd_tdb_drd"))
        if p not in eph["DRC"] or p in flags["DRC"] or ("DRC", p) not in cov:
            continue
        if not sp["start"] <= bjd_date(ref) <= sp["end"]:
            continue
        e = eph["DRC"][p]
        keep.append({**r, "forecast_epoch": int(np.rint((ref - e.t0_bjd_tdb) / e.period_days)),
                     "epoch_basis": "t015v3 mid-time or window centre, nearest DRC epoch"})
    d = DERIVED / "interface"
    d.mkdir(parents=True, exist_ok=True)
    fvc.write_csv(d / "outcomes_drc_window.csv", keep)
    params = ROOT / "results/sprint2/forecasts/parameters_release_transfer_ours_all.json"
    py = str(ROOT / ".venv/bin/python")
    subprocess.run([py, str(HERE / "sprint1_forecasts.py"), "make_forecasts", "--events", str(d / "outcomes_drc_window.csv"),
                    "--parameters", str(params), "--release", "DRC", "--output", str(d / "forecasts.csv")], check=True)
    subprocess.run([py, str(HERE / "sprint1_forecasts.py"), "score", "--forecasts", str(d / "forecasts.csv"),
                    "--outcomes", str(d / "outcomes_drc_window.csv"), "--error-convention", "t015v3_beta_chi",
                    "--outcome-scale", "1.0", "--output", str(d / "scores.csv")], check=True)
    print((d / "scores.receipt.json").read_text())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--bootstrap", type=int, default=400)
    p.set_defaults(func=run)
    p = sub.add_parser("interface")
    p.set_defaults(func=interface)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
