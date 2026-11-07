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
import sprint2_outcomes as so  # noqa: E402
from reproduce_table5 import load  # noqa: E402
from transit_audit.exoclock import host_of  # noqa: E402

RULE = "t015v3"
OUTCOMES = ROOT / "data" / "derived" / "outcomes" / RULE / "outcomes.csv"
OUT = ROOT / "results" / "sprint2" / "forecasts"
DERIVED = ROOT / "data" / "derived" / "sprint2"


def bjd_date(jd):
    return str(np.datetime64("1970-01-01") + np.timedelta64(int(np.floor(jd - 2440587.5)), "D"))


def our_events(release, start, end, rows, eph, flags, cov, setting="c2", a=1.0, convention="t015v3c"):
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
                    "release": release, "source_record_date": date, "tc_bjd_tdb": tc,
                    "sigma_s": float(r["sigma_s"]) * (so.tmag_multiplier(r["tmag"]) if convention == "t015v3c" else 1.0),
                    "outcome_scale": a, "forecast_epoch": n, "predicted_bjd_tdb": pred,
                    "residual_s": (tc - pred) * 86400, "sigma_t0_s": e.sigma_t0_days * 86400,
                    "sigma_p_s": e.sigma_period_days * 86400, "rho": rho, "covariance_setting": setting,
                    "covariance_tier": "C2_candidate" if disc <= 3 else "C3_source_fit_mismatch",
                    "period_fit_discrepancy_sigma": disc, "forecast_variance_s2": vf,
                    "issue_date": c.ISSUE_DATES[release],
                    "horizon_days": (np.datetime64(date) - np.datetime64(c.ISSUE_DATES[release])).astype(int).item(),
                    "status": "timed", "error_convention": convention, "shape_group_id": r["shape_group_id"],
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
            raw, _ = our_events(sp["release"], sp["start"], sp["end"], rows, eph, flags, cov, convention="t015v3")
            pairs = match(ours, cat)
            ids = {r["event_id"] for r, _ in pairs}
            sets[part] = {"exoclock_all": cat, "ours_all": ours, "ours_all_raw": raw,
                          "exoclock_matched": [x for _, x in pairs], "ours_matched": [r for r, _ in pairs],
                          "ours_matched_raw": [r for r in raw if r["event_id"] in ids],
                          "pairs": pairs, "rejected": rej}
        res = {}
        for variant in ("exoclock_matched", "ours_matched", "ours_matched_raw", "ours_all", "ours_all_raw", "exoclock_all"):
            res[variant] = compare(f"{exp}|{variant}", sets["train"][variant], sets["test"][variant],
                                   args.bootstrap, cfg["seed"])
            if "models" in res[variant]:
                c.write_json(OUT / f"parameters_{exp}_{variant}.json",
                             {"models": res[variant]["models"], "experiment": exp, "variant": variant,
                              "outcomes_sha256": c.digest(OUTCOMES), "development_only": True})
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
            "R5_transfer_accepted_raw_t015v3": bool(dec["exoclock_matched"] == dec["ours_matched_raw"]
                                                    and sign["exoclock_matched"] == sign["ours_matched_raw"]),
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


def candidate(args):
    """Candidate DRD-era parameters: release transfer on DRC forecasts vs all development outcomes after DRC issue."""
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows = list(csv.DictReader(OUTCOMES.open()))
    sp = cfg["experiments"]["release_transfer"]["test"]
    events, _ = our_events(sp["release"], sp["start"], sp["end"], rows, eph, flags, cov, convention=args.convention)
    cand = c.visit_planets(events)
    models = c.fit_methods(cand)
    rng = np.random.default_rng(cfg["seed"])
    hosts = sorted({p["host"] for p in cand})
    hix = np.array([hosts.index(p["host"]) for p in cand])
    boot = []
    for _ in range(args.bootstrap):
        mult = np.bincount(rng.integers(0, len(hosts), len(hosts)), minlength=len(hosts))[hix]
        fm = c.fit_methods(cand, weights=mult)
        boot.append({m: {"b": fm[m]["b"], "s_log_lambda": fm[m]["s_log_lambda"]} for m in c.METHODS[1:]})
    c.write_json(OUT / args.output, {
        "models": models, "convention": args.convention,
        "rule": f"release transfer: DRC forecasts vs {args.convention} outcomes 2022-09-28..2024-01-03",
        "training_planets": len(cand), "training_hosts": len(hosts), "training_events": len(events),
        "outcomes_sha256": c.digest(OUTCOMES), "host_refit_parameter_sets": boot,
        "development_only": True, "frozen": False})
    print({m: (round(v["b"], 4), round(v["s_log_lambda"], 4)) for m, v in models.items()})


def grid_resolved(path):
    g = json.loads(Path(path).read_text())
    o, lg = np.asarray(g["offset_s"]), np.asarray(g["log_density"])
    d = np.exp(lg - lg.max())
    w = np.r_[np.diff(o)[0] / 2, (o[2:] - o[:-2]) / 2, np.diff(o)[-1] / 2]
    m = d * w / np.sum(d * w)
    return m[0] + m[-1] <= 0.001 and max(d[0], d[-1]) <= 0.001


def interface(args):
    """I1 -> I2 replay on production outcomes: make_forecasts then score, every attempted DRC-era row."""
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    sp = cfg["experiments"]["release_transfer"]["test"]
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows = list(csv.DictReader(OUTCOMES.open()))
    keep = []
    conv_name = "t015v3c_beta_chi_tmag" if args.convention == "t015v3c" else "t015v3_beta_chi"
    for r in rows:
        p = r["planet"]
        ref = float(r["tc_bjd_tdb"]) if r.get("tc_bjd_tdb") else float(r.get("window_centre_bjd_tdb") or r.get("predicted_bjd_tdb_drd"))
        if p not in eph["DRC"] or p in flags["DRC"] or ("DRC", p) not in cov:
            continue
        if not sp["start"] <= bjd_date(ref) <= sp["end"]:
            continue
        e = eph["DRC"][p]
        g = so.tmag_multiplier(r["tmag"]) if args.convention == "t015v3c" else 1.0
        row = {**r, "forecast_epoch": int(np.rint((ref - e.t0_bjd_tdb) / e.period_days)),
               "epoch_basis": "t015v3 mid-time or window centre, nearest DRC epoch",
               "error_convention": conv_name, "tmag_multiplier": round(g, 6)}
        if r["status"] == "timed" and r["posterior_grid_path"] and not grid_resolved(ROOT / r["posterior_grid_path"]):
            row.update({"status": "likelihood_support_truncated",
                        "failure_reason": "posterior grid has >0.1% mass or density at the +/-60-min prior support (S2-05)"})
        if row["status"] == "timed":
            for k in ("sigma_s", "q025_s", "q1587_s", "q8413_s", "q975_s", "q0228_s", "q9772_s"):
                row[k] = round(float(r[k]) * g, 4)
            if r["posterior_grid_path"] and args.convention == "t015v3c":
                src = json.loads((ROOT / r["posterior_grid_path"]).read_text())
                src["offset_s"] = [round(v * g, 4) for v in src["offset_s"]]
                src["support_s"] = [v * g for v in src["support_s"]]
                src["tmag_multiplier"] = g
                gp = DERIVED / "interface" / "grids_t015v3c" / Path(r["posterior_grid_path"]).name
                gp.parent.mkdir(parents=True, exist_ok=True)
                gp.write_text(json.dumps(src) + "\n")
                row["posterior_grid_path"] = str(gp.relative_to(ROOT))
        keep.append(row)
    d = DERIVED / "interface"
    d.mkdir(parents=True, exist_ok=True)
    fvc.write_csv(d / "outcomes_drc_window.csv", keep)
    params = OUT / ("parameters_release_transfer_ours_all.json" if args.convention == "t015v3c"
                    else "parameters_release_transfer_ours_all_raw.json")
    py = str(ROOT / ".venv/bin/python")
    subprocess.run([py, str(HERE / "sprint1_forecasts.py"), "make_forecasts", "--events", str(d / "outcomes_drc_window.csv"),
                    "--parameters", str(params), "--release", "DRC", "--output", str(d / "forecasts.csv")], check=True)
    subprocess.run([py, str(HERE / "sprint1_forecasts.py"), "score", "--forecasts", str(d / "forecasts.csv"),
                    "--outcomes", str(d / "outcomes_drc_window.csv"), "--error-convention", conv_name,
                    "--outcome-scale", "1.0", "--output", str(d / "scores.csv")], check=True)
    print((d / "scores.receipt.json").read_text())


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run")
    p.add_argument("--bootstrap", type=int, default=400)
    p.set_defaults(func=run)
    p = sub.add_parser("candidate")
    p.add_argument("--convention", choices=("t015v3", "t015v3c"), required=True)
    p.add_argument("--bootstrap", type=int, default=400)
    p.add_argument("--output", default="candidate_parameters.json")
    p.set_defaults(func=candidate)
    p = sub.add_parser("interface")
    p.add_argument("--convention", choices=("t015v3", "t015v3c"), default="t015v3")
    p.set_defaults(func=interface)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
