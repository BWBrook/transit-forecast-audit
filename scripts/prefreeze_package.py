"""Bounded prefreeze package (D056): manifests, core-matched candidate refit, joint-refit evaluation path.

Development and synthetic data only; no protected outcome is read.

    .venv/bin/python scripts/prefreeze_package.py manifests
    .venv/bin/python scripts/prefreeze_package.py candidate [--bootstrap 400]
    .venv/bin/python scripts/prefreeze_package.py exercise [--bootstrap 200]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint1_forecast_core as c  # noqa: E402
import sprint2_forecasts as s2  # noqa: E402
from reproduce_table5 import load  # noqa: E402
from transit_audit.exoclock import host_of  # noqa: E402

OUT = ROOT / "results" / "prefreeze"
MANIFEST = ROOT / "results" / "sprint2_review" / "freeze_candidate" / "events_drd.csv"
SHAPE_RCHI_MAX = 10.0
INTEG = {"mass_outside_fine", "coarse_fine_shift"}
RULE = "t015v3a: frozen t015v3 timing, integration fail-closed, SPOC 120-s PDCSAP, product shape reduced chi2 <= 10"


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def write(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with Path(path).open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def manifests(args):
    rows = list(csv.DictReader(MANIFEST.open()))
    OUT.mkdir(parents=True, exist_ok=True)
    keep = [r for r in rows if r["time_boundary_status"] == "metadata_interior_only"]
    excl = [r for r in rows if r["time_boundary_status"] != "metadata_interior_only"]
    core = [r for r in keep if r["cohort"] == "core"]
    ext = [r for r in keep if r["cohort"] == "extension"]
    write(OUT / "manifest_core_primary.csv", core)
    write(OUT / "manifest_extension_exploratory.csv", ext)
    write(OUT / "manifest_boundary_excluded.csv", [{**r, "exclusion": "conservative: within 10 min of an unconverted numeric time boundary (D056 §3)"} for r in excl])
    s = {"source_manifest": str(MANIFEST.relative_to(ROOT)), "source_sha256": sha(MANIFEST),
         "core_events": len(core), "core_planets": len({r["planet"] for r in core}),
         "extension_events": len(ext), "extension_planets": len({r["planet"] for r in ext}),
         "boundary_excluded": len(excl), "boundary_excluded_ids": [r["event_id"] for r in excl],
         "completeness": "conservative subset; not an exhaustive or exact strict-A eligibility claim"}
    (OUT / "manifest_summary.json").write_text(json.dumps(s, indent=1) + "\n")
    print(s)


def gated_rows():
    rows = list(csv.DictReader(gzip.open(ROOT / "results/outcomes/t015v3/outcomes.csv.gz", "rt")))
    pid = {(r["planet"], r["sector"], r["product"]): r for r in
           csv.DictReader((ROOT / "results/outcomes/t015v3/product_identification.csv").open())}
    out, why = [], Counter()
    for r in rows:
        if r["product"] != "SPOC_120":
            why["not_spoc"] += 1
            continue
        p = pid.get((r["planet"], r["sector"], r["product"]))
        if r["status"] == "timed" and p and p.get("shape_rchi2") and float(p["shape_rchi2"]) > SHAPE_RCHI_MAX:
            r = {**r, "status": "product_shape_gate_failed"}
        if r["status"] == "timed" and INTEG & set(r.get("flags", "").split(";")):
            r = {**r, "status": "integration_unresolved"}
        why[r["status"]] += 1
        out.append(r)
    return out, dict(why)


def core_planets(eph):
    from sprint2_remeasure import cohort  # noqa: F401  (documented cohort source)
    drd = eph["DRD"]
    hosts = Counter(host_of(p) for p in drd)
    tm = {}
    for r in csv.DictReader((ROOT / "results/outcomes/t015v3/products.csv").open()):
        if r.get("tmag"):
            for p in r["planets"].split(";"):
                tm[p] = float(r["tmag"])
    return {p for p in drd if hosts[host_of(p)] == 1 and drd[p].period_days <= 12 and tm.get(p, 99) < 13.5}


def joint_draws(train_planets, test_events, B, seed, fit=True):
    """Joint host resampling across calibration and evaluation sets; refit M1-M3 per draw; store multiplicities."""
    hosts = sorted({p["host"] for p in train_planets} | {e["host"] for e in test_events})
    ix = {h: i for i, h in enumerate(hosts)}
    th = np.array([ix[p["host"]] for p in train_planets])
    rng = np.random.default_rng(seed)
    draws = []
    for b in range(B):
        m = np.bincount(rng.integers(0, len(hosts), len(hosts)), minlength=len(hosts))
        models = c.fit_methods(train_planets, weights=m[th]) if fit else None
        draws.append({"draw": b, "multiplicity": m.tolist(),
                      "models": {k: {"b": v["b"], "s_log_lambda": v["s_log_lambda"]} for k, v in models.items()} if models else None})
    return hosts, draws


def candidate(args):
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows, gate_counts = gated_rows()
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    sp = cfg["experiments"]["release_transfer"]["test"]
    core = core_planets(eph)
    res = {"rule": RULE, "gate_counts_all_spoc_rows": gate_counts, "fits": {}}
    for label, sel in (("core_matched", lambda r: r["planet"] in core), ("all_spoc", lambda r: True)):
        ev, rej = s2.our_events(sp["release"], sp["start"], sp["end"], [r for r in rows if sel(r)], eph, flags, cov,
                                convention="t015v3")
        tp_ = c.visit_planets(ev)
        models = c.fit_methods(tp_)
        t0 = time.monotonic()
        hosts, draws = joint_draws(tp_, [], args.bootstrap, cfg["seed"])
        res["fits"][label] = {"training_planets": len(tp_), "training_hosts": len({p["host"] for p in tp_}),
                              "training_events": len(ev), "excluded_rows": len(rej),
                              "models": {k: {"b": v["b"], "s_log_lambda": v["s_log_lambda"], "at_bound": v["at_bound"]}
                                         for k, v in models.items()},
                              "draw_parameter_q025_q975": {m: {p: [float(np.quantile([d["models"][m][p] for d in draws], q))
                                                                   for q in (.025, .975)] for p in ("b", "s_log_lambda")}
                                                           for m in ("M1", "M2", "M3")},
                              "bootstrap_seconds": round(time.monotonic() - t0, 1)}
        with gzip.open(OUT / f"candidate_draws_{label}.json.gz", "wt") as fh:
            json.dump({"hosts": hosts, "draws": draws, "rule": RULE, "convention": "t015v3a"}, fh)
        print(label, res["fits"][label]["training_planets"], {k: (round(v["b"], 3), round(v["s_log_lambda"], 3))
                                                              for k, v in models.items()})
    res["training_window"] = [sp["start"], sp["end"]]
    res["population_transfer"] = ("Primary candidate parameters are fitted on DRC forecasts of core-eligible planets "
                                  "(single DRD planet per host, Tmag < 13.5, P <= 12 d, no DRC origin-TTV flag) and applied "
                                  "to DRD forecasts of the 156-planet core; release transfer DRC->DRD, not an issued correction.")
    c.write_json(OUT / "candidate_parameters.json", {**res, "development_only": True, "frozen": False,
                                                     "outcomes_sha256": sha(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")})


def exercise(args):
    """Run the declared primary inference end to end on synthetic outcomes for the core manifest."""
    cand = json.loads((OUT / "candidate_parameters.json").read_text())
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows, _ = gated_rows()
    cfg = json.loads((ROOT / "configs/sprint1.json").read_text())
    sp = cfg["experiments"]["release_transfer"]["test"]
    core = core_planets(eph)
    tr, _ = s2.our_events(sp["release"], sp["start"], sp["end"], [r for r in rows if r["planet"] in core], eph, flags, cov,
                          convention="t015v3")
    train = c.visit_planets(tr)
    man = list(csv.DictReader((OUT / "manifest_core_primary.csv").open()))
    rng = np.random.default_rng(20261108)
    drd = eph["DRD"]
    test = []
    for m in man:
        if ("DRD", m["planet"]) not in cov or m["planet"] in flags["DRD"]:
            continue
        e = drd[m["planet"]]
        n = int(m["forecast_epoch"])
        rho = c.correlation("DRD", m["planet"], "c2", cov)
        vf = float(c.forecast_variance(e.sigma_t0_days * 86400, e.sigma_period_days * 86400, n, rho))
        sy = 60.0
        lam = np.exp(rng.normal(0, 2.585))
        test.append({"event_id": m["event_id"], "planet": m["planet"], "host": m["host"], "forecast_variance_s2": vf,
                     "sigma_s": sy, "outcome_scale": 1.0,
                     "residual_s": float(np.sqrt(vf * lam) * rng.normal() + sy * rng.normal())})
    models = {k: {"b": v["b"], "s_log_lambda": v["s_log_lambda"]} for k, v in cand["fits"]["core_matched"]["models"].items()}
    point = {m: c.predictive_scores(test, models[m]) for m in c.METHODS}
    agg = c.aggregate(test, point)
    t0 = time.monotonic()
    hosts, draws = joint_draws(train, test, args.bootstrap, cfg["seed"])
    ix = {h: i for i, h in enumerate(hosts)}
    ids, _ = c.planet_aggregate(test, point["M0"]["is95_standardised"])
    phost = {e["planet"]: e["host"] for e in test}
    ws_idx = np.array([ix[phost[p]] for p in ids])
    ref = point["M0"]["is95_standardised"]
    deltas = []
    for d in draws:
        sc = c.predictive_scores(test, d["models"]["M2"])
        _, pm = c.planet_aggregate(test, sc["is95_standardised"] - ref)
        w = np.asarray(d["multiplicity"])[ws_idx]
        deltas.append(float(np.average(pm, weights=w)) if w.sum() else np.nan)
    deltas = np.array(deltas)
    fixed = []
    _, pm0 = c.planet_aggregate(test, point["M2"]["is95_standardised"] - ref)
    for d in draws:
        w = np.asarray(d["multiplicity"])[ws_idx]
        fixed.append(float(np.average(pm0, weights=w)) if w.sum() else np.nan)
    out = {"synthetic": "M2-truth residuals (s=2.585) on DRD core manifest forecasts, sigma_y=60 s; not data",
           "test_events": len(test), "test_planets": len(ids), "train_planets": len(train),
           "primary_delta_M2_M0": agg["M2"]["delta_standardised_vs_M0"],
           "joint_refit_ci95": [float(np.nanquantile(deltas, .025)), float(np.nanquantile(deltas, .975))],
           "fixed_parameter_ci95": [float(np.nanquantile(fixed, .025)), float(np.nanquantile(fixed, .975))],
           "draws": args.bootstrap, "seconds": round(time.monotonic() - t0, 1),
           "multiplicities_and_parameters_stored": True}
    (OUT / "evaluation_path_exercise.json").write_text(json.dumps(out, indent=1) + "\n")
    print(out)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("manifests").set_defaults(func=manifests)
    p = sub.add_parser("candidate")
    p.add_argument("--bootstrap", type=int, default=400)
    p.set_defaults(func=candidate)
    p = sub.add_parser("exercise")
    p.add_argument("--bootstrap", type=int, default=200)
    p.set_defaults(func=exercise)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
