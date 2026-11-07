"""Frozen final-evaluation path for the DRD core question (D060 requirement 2).

One command from the fixed event manifest to the decision:

1. terminal ledger: exactly one row per manifest event. Product state from the
   measurement's product diagnostics (absent product -> product_unavailable,
   read failure -> product_read_failed; no readable header is needed), recovered
   windows mapped to DRD cycles, then scripts/acceptance.py terminal_status with
   directly measured coverage at the prediction (missing -> observability unknown);
2. scoring: the accepted rows, relabelled to their manifest identities, go
   through the I1 adapter (score_outcomes), the declared representation:
   Gaussian when certified, otherwise the accepted likelihood grid;
3. inference: B joint host resamples spanning calibration and evaluation hosts,
   M1-M3 refitted on each draw's calibration weights, M2 rescored with the same
   event representation as the adapter (checked to reproduce the adapter's
   scores for M0-M3 before any draw; every draw exact), planet-balanced M2-M0 weighted by host
   multiplicity; decision from the 95% percentile interval. The fixed-parameter
   host bootstrap is a separately labelled conditional result.

Inputs are files; nothing is measured here. The era limit is the development
limit unless --era protected names an access record written after Barry's
decision (configs/protected_access.json); without it the command refuses.

    .venv/bin/python scripts/final_evaluation.py evaluate --manifest M --forecasts F --windows W \\
        --products P --coverage C --out DIR [--era development|protected] [--bootstrap 2000]
    .venv/bin/python scripts/final_evaluation.py dev-exercise [--bootstrap 50]
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import acceptance as A  # noqa: E402
import sprint1_forecast_core as c  # noqa: E402
import sprint1_outcome_adapter as ad  # noqa: E402

CONFIG = ROOT / "configs" / "candidate_freeze.json"
ACCESS = ROOT / "configs" / "protected_access.json"
CONVENTION = "t015v3_beta_chi"
REPRO_TOL = 1e-9


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def read_csv(p):
    p = Path(p)
    with (gzip.open(p, "rt") if p.suffix == ".gz" else p.open()) as fh:
        return list(csv.DictReader(fh))


def write_csv(p, rows):
    p = Path(p)
    keys = list(dict.fromkeys(k for r in rows for k in r)) or ["event_id"]
    with (gzip.open(p, "wt", newline="") if p.suffix == ".gz" else p.open("w", newline="")) as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def era_limit(era):
    if era == "development":
        return ad.DEVELOPMENT_MAX_TC
    rec = json.loads(ACCESS.read_text()) if ACCESS.exists() else {}
    if not (rec.get("authorised_by") and rec.get("decision") and rec.get("date")):
        raise SystemExit("protected era requires configs/protected_access.json recording Barry's decision")
    return None


# ---------------------------------------------------------------- 1. terminal ledger

def terminal_ledger(manifest, windows, products, coverage, drd):
    """manifest rows; windows: I1 rows; products: diagnostics keyed (planet, sector); coverage: event_id -> row."""
    by_cycle = defaultdict(list)
    for w in windows:
        if w.get("product") != A.PRODUCT or w["planet"] not in drd:
            continue
        e = drd[w["planet"]]
        ref = A._finite(w.get("tc_bjd_tdb")) or A._finite(w.get("window_centre_bjd_tdb")) \
            or A._finite(w.get("predicted_bjd_tdb_drd"))
        if ref is None:
            continue
        by_cycle[(w["planet"], str(int(float(w["sector"]))), round((ref - e.t0_bjd_tdb) / e.period_days))].append(w)
    ledger, used = [], set()
    for m in manifest:
        e = drd[m["planet"]]
        n, sector = int(m["forecast_epoch"]), str(int(float(m["sector"])))
        pred = e.t0_bjd_tdb + n * e.period_days
        key = (m["planet"], sector, n)
        used.add(key)
        diag = products.get((m["planet"], sector))
        ps = A.product_state(diag)
        cv = coverage.get(m["event_id"])
        cov_ok = None
        if cv is not None:
            cw, ci = A._finite(cv.get("coverage_window_at_prediction")), A._finite(cv.get("coverage_in_transit_at_prediction"))
            cov_ok = None if cw is None or ci is None else (cw >= .75 and ci >= .75)
        ws = by_cycle.get(key, [])
        st = A.terminal_status(ps, ws, diag, pred, e.period_days, cov_ok)
        ledger.append({"event_id": m["event_id"], "observation_id": m["observation_id"], "planet": m["planet"],
                       "host": m["host"], "sector": sector, "forecast_epoch": n, "drd_predicted_bjd_tdb": round(pred, 7),
                       "product_state": ps, "windows": len(ws),
                       "window_event_id": ";".join(w["event_id"] for w in ws),
                       "coverage_ok_at_prediction": "" if cov_ok is None else cov_ok, "status": st})
    planets = {m["planet"] for m in manifest}
    outside = [w for k, ws in by_cycle.items() if k[0] in planets and k not in used for w in ws]
    return ledger, outside


# ---------------------------------------------------------------- 2. adapter scoring

def scoring_inputs(ledger, windows, forecasts):
    wid = {w["event_id"]: w for w in windows}
    fid = {f["event_id"]: f for f in forecasts}
    outs, fcs = [], []
    for r in ledger:
        if r["status"] != A.ACCEPTED:
            continue
        w = wid[r["window_event_id"]]
        outs.append({**w, "event_id": r["event_id"], "observation_id": r["observation_id"], "status": "timed",
                     "measurement_event_id": w["event_id"]})
        fcs.append(fid[r["event_id"]])
    return outs, fcs


def event_representation(outs, forecasts, scale=1.0):
    """The adapter's per-event representation, rebuilt for per-draw rescoring."""
    fid = {f["event_id"]: f for f in forecasts}
    ev = []
    for r in outs:
        fc = fid[r["event_id"]]
        sigma = float(r["sigma_s"])
        e = {"event_id": r["event_id"], "planet": r["planet"], "host": r["host"], "sigma_s": sigma,
             "outcome_scale": scale, "residual_s": (float(r["tc_bjd_tdb"]) - float(fc["predicted_bjd_tdb"])) * 86400,
             "forecast_variance_s2": float(fc["forecast_variance_s2"]), "grid": None}
        if str(r.get("gauss_ok", "")).lower() not in ("true", "1", "yes"):
            p = Path(r["posterior_grid_path"])
            x, w = ad.likelihood_grid(p if p.is_absolute() else ROOT / p)
            e["grid"] = (x * scale, w)
            e["denom"] = float(np.sqrt(e["forecast_variance_s2"] + float(w @ (x * x * scale * scale) - (w @ (x * scale)) ** 2)))
        ev.append(e)
    return ev


def grid_is95(e, model):
    """Standardised IS95 of a grid event: the adapter's grid_score formula on its own 2.5/97.5% quantile roots."""
    lower, upper = ad.grid_quantiles(e["forecast_variance_s2"], model, e["grid"], (.025, .975))
    y = e["residual_s"]
    return (upper - lower + 40 * (max(lower - y, 0) + max(y - upper, 0))) / e["denom"]


def score_events(ev, model):
    """is95_standardised per event under one model, computed exactly as the adapter computes it."""
    out = np.empty(len(ev))
    gi = [i for i, e in enumerate(ev) if e["grid"] is None]
    if gi:
        out[gi] = c.predictive_scores([ev[i] for i in gi], model, order=384, interpolate=False)["is95_standardised"]
    for i, e in enumerate(ev):
        if e["grid"] is not None:
            out[i] = grid_is95(e, model)
    return out


_W = {}


def _init_worker(ev):
    _W["ev"] = ev


def _score_draw(model):
    return score_events(_W["ev"], model)


# ---------------------------------------------------------------- 3. inference

def calibration_planets():
    """Frozen calibration set: core-matched DRC training events under the shared acceptance rule."""
    import prefreeze_package as pp
    import sprint2_forecasts as s2
    from reproduce_table5 import load
    eph, _, flags = load()
    cov = c.covariance_rows()
    rows, _ = pp.gated_rows()
    sp = json.loads((ROOT / "configs/sprint1.json").read_text())["experiments"]["release_transfer"]["test"]
    core = pp.core_planets(eph)
    ev, _ = s2.our_events(sp["release"], sp["start"], sp["end"], [r for r in rows if r["planet"] in core],
                          eph, flags, cov, convention="t015v3")
    return c.visit_planets(ev)


def planet_delta(ev, values, host_index, mult=None):
    ids, pm = c.planet_aggregate(ev, values)
    if mult is None:
        return float(pm.mean())
    ph = {e["planet"]: e["host"] for e in ev}
    w = np.asarray(mult)[[host_index[ph[p]] for p in ids]]
    return float(np.average(pm, weights=w)) if w.sum() else float("nan")


def evaluate(args):
    cfg = json.loads(CONFIG.read_text())
    seeds = cfg["seeds"]
    max_tc = era_limit(args.era)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    from reproduce_table5 import load
    drd = load()[0]["DRD"]
    manifest, forecasts, windows = read_csv(args.manifest), read_csv(args.forecasts), read_csv(args.windows)
    if {m["event_id"] for m in manifest} != {f["event_id"] for f in forecasts} or len(manifest) != len(forecasts):
        raise ValueError("forecasts must cover exactly the manifest events")
    products = {}
    for p in read_csv(args.products):
        if p.get("planet") and p.get("product") == A.PRODUCT:
            k = (p["planet"], str(int(float(p["sector"]))))
            if k in products:
                raise ValueError(f"duplicate product diagnostics {k}")
            products[k] = p
    coverage = {r["event_id"]: r for r in read_csv(args.coverage)}

    ledger, outside = terminal_ledger(manifest, windows, products, coverage, drd)
    write_csv(out / "terminal_ledger.csv.gz", ledger)
    counts = Counter(r["status"] for r in ledger)

    outs, fcs = scoring_inputs(ledger, windows, forecasts)
    write_csv(out / "accepted_outcomes.csv", outs)
    write_csv(out / "accepted_forecasts.csv", fcs)
    scores_path = out / "scores.csv"
    ad.score_outcomes(argparse.Namespace(forecasts=str(out / "accepted_forecasts.csv"),
                                         outcomes=str(out / "accepted_outcomes.csv"), error_convention=CONVENTION,
                                         outcome_scale=1.0, output=str(scores_path), max_tc_bjd=max_tc))
    adapter = defaultdict(dict)
    for r in read_csv(scores_path):
        adapter[r["method"]][r["event_id"]] = float(r["is95_standardised"])

    ev = event_representation(outs, fcs)
    frozen = json.loads(Path(args.parameters).read_text())["models"]
    fixed = {m: score_events(ev, frozen[m]) for m in c.METHODS}
    worst = max(abs(fixed[m][i] - adapter[m][e["event_id"]]) for m in c.METHODS for i, e in enumerate(ev))
    if worst > REPRO_TOL * max(1.0, max(abs(v) for d in adapter.values() for v in d.values())):
        raise RuntimeError(f"draw scorer does not reproduce the adapter (max |diff| {worst:.3g})")

    train = calibration_planets()
    refit = c.fit_methods(train)
    drift = max(abs(refit[m][k] - frozen[m][k]) for m in ("M1", "M2", "M3") for k in ("b", "s_log_lambda"))
    if drift > 1e-6:
        raise RuntimeError(f"calibration input does not reproduce the frozen parameters (max |diff| {drift:.3g})")

    import prefreeze_package as pp
    from multiprocessing import Pool
    t0 = time.monotonic()
    hosts, draws = pp.joint_draws(train, ev, args.bootstrap, seeds["evaluation_joint_bootstrap"])
    with Pool(args.workers, initializer=_init_worker, initargs=(ev,)) as pool:
        draw_scores = pool.map(_score_draw, [d["models"]["M2"] for d in draws], chunksize=1)
    ix = {h: i for i, h in enumerate(hosts)}
    point = planet_delta(ev, fixed["M2"] - fixed["M0"], ix)
    joint, cond = [], []
    for d, sc in zip(draws, draw_scores):
        d["paired_delta_M2_M0"] = planet_delta(ev, sc - fixed["M0"], ix, d["multiplicity"])
        d["fixed_parameter_delta"] = planet_delta(ev, fixed["M2"] - fixed["M0"], ix, d["multiplicity"])
        joint.append(d["paired_delta_M2_M0"])
    rng = np.random.default_rng(seeds["conditional_fixed_parameter_bootstrap"])
    ehosts = sorted({e["host"] for e in ev})
    eix = {h: i for i, h in enumerate(ehosts)}
    for _ in range(args.conditional_bootstrap):
        m = np.bincount(rng.integers(0, len(ehosts), len(ehosts)), minlength=len(ehosts))
        cond.append(planet_delta(ev, fixed["M2"] - fixed["M0"], eix, m))
    ci = [float(np.nanquantile(joint, .025)), float(np.nanquantile(joint, .975))]
    decision = "improves" if ci[1] < 0 else "worsens" if ci[0] > 0 else "inconclusive"
    with gzip.open(out / "joint_draws.json.gz", "wt") as fh:
        json.dump({"kind": "joint host-refit draws spanning calibration and evaluation hosts", "hosts": hosts,
                   "calibration_hosts": sorted({p["host"] for p in train}), "evaluation_hosts": ehosts,
                   "seed": seeds["evaluation_joint_bootstrap"], "draws": draws}, fh, default=lambda o: o.item())
    inputs = {k: sha(getattr(args, k)) for k in ("manifest", "forecasts", "windows", "products", "coverage", "parameters")}
    code = {p: sha(HERE / p) for p in ("final_evaluation.py", "acceptance.py", "sprint1_outcome_adapter.py",
                                        "sprint1_forecast_core.py", "forecast_variance_components.py",
                                        "prefreeze_package.py", "sprint2_forecasts.py")}
    summary = {"era": args.era, "max_tc_bjd": max_tc, "label": args.label,
               "manifest_events": len(ledger), "terminal_status_counts": dict(counts.most_common()),
               "accepted_events": counts[A.ACCEPTED], "accepted_planets": len({e["planet"] for e in ev}),
               "evaluation_hosts": len(ehosts), "windows_outside_manifest": len(outside),
               "nonGaussian_scored": sum(e["grid"] is not None for e in ev),
               "adapter_reproduction_max_abs_diff": worst, "calibration_refit_max_abs_diff": drift,
               "draw_scoring": "exact per draw: Gaussian events by the adapter's predictive_scores (order 384, no interpolation); grid events by the adapter's grid_quantiles roots",
               "draw_M2_s_q025_q975": [float(np.quantile([d["models"]["M2"]["s_log_lambda"] for d in draws], q))
                                       for q in (.025, .975)],
               "calibration_planets": len(train), "joint_hosts_union": len(hosts),
               "primary_delta_M2_M0": point, "joint_refit_ci95": ci, "decision": decision,
               "conditional_fixed_parameter_ci95": [float(np.nanquantile(cond, .025)), float(np.nanquantile(cond, .975))],
               "joint_bootstrap": args.bootstrap, "conditional_bootstrap": args.conditional_bootstrap,
               "seeds": {k: seeds[k] for k in ("evaluation_joint_bootstrap", "conditional_fixed_parameter_bootstrap")},
               "seconds_joint": round(time.monotonic() - t0, 1),
               "input_sha256": inputs, "code_sha256": code, "config_sha256": sha(CONFIG),
               "adapter_receipt_sha256": sha(scores_path.with_suffix(".receipt.json")),
               "joint_draws_sha256": sha(out / "joint_draws.json.gz"),
               "terminal_ledger_sha256": sha(out / "terminal_ledger.csv.gz")}
    (out / "evaluation_summary.json").write_text(json.dumps(summary, indent=1, default=lambda o: o.item()) + "\n")
    print(json.dumps({k: summary[k] for k in ("manifest_events", "accepted_events", "primary_delta_M2_M0",
                                              "joint_refit_ci95", "decision")}))
    return summary


# ---------------------------------------------------------------- development exercise

def dev_exercise(args):
    """Run the final command on saved development measurements (core planets, DRD cycles, hindcast; path only)."""
    import prefreeze_package as pp
    from reproduce_table5 import load
    d = ROOT / "results" / "prefreeze" / "final_path_dev"
    d.mkdir(parents=True, exist_ok=True)
    core = pp.core_planets(load()[0])
    att = [r for r in read_csv(ROOT / "results/prefreeze/attempt_ledger_development.csv.gz") if r["planet"] in core]
    from transit_audit.exoclock import host_of
    obs = {}
    for p in read_csv(ROOT / "results/outcomes/t015v3/products.csv"):
        if p["status"] == "selected" and p["product"] == A.PRODUCT:
            for pl in p["planets"].split(";"):
                obs[(pl, p["sector"])] = p["uri"].split("/")[-1].removesuffix("_lc.fits")
    man = [{"event_id": r["event_id"], "observation_id": r["event_id"], "planet": r["planet"], "host": host_of(r["planet"]),
            "sector": r["sector"], "product_obs_id": obs[(r["planet"], r["sector"])], "forecast_epoch": r["epoch"],
            "epoch_basis": "development DRD cycle (hindcast exercise)"} for r in att]
    write_csv(d / "manifest.csv", man)
    write_csv(d / "coverage.csv", [{"event_id": r["event_id"], **{k: r[k] for k in (
        "coverage_window_at_prediction", "coverage_in_transit_at_prediction")}} for r in att])
    import subprocess
    subprocess.run([str(ROOT / ".venv/bin/python"), str(HERE / "sprint1_forecasts.py"), "make_forecasts",
                    "--events", str(d / "manifest.csv"), "--parameters", str(ROOT / "results/prefreeze/candidate_models_core_matched.json"),
                    "--release", "DRD", "--output", str(d / "forecasts.csv")], check=True)
    ns = argparse.Namespace(manifest=str(d / "manifest.csv"), forecasts=str(d / "forecasts.csv"),
                            windows=str(ROOT / "results/outcomes/t015v3/outcomes.csv.gz"),
                            products=str(ROOT / "results/outcomes/t015v3/product_identification.csv"),
                            coverage=str(d / "coverage.csv"),
                            parameters=str(ROOT / "results/prefreeze/candidate_models_core_matched.json"),
                            out=str(d / "run"), era="development", bootstrap=args.bootstrap,
                            conditional_bootstrap=args.conditional_bootstrap, workers=args.workers,
                            label="development path exercise: DRD hindcast of development outcomes; no inferential content")
    evaluate(ns)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("evaluate")
    for k in ("manifest", "forecasts", "windows", "products", "coverage", "out"):
        p.add_argument("--" + k, required=True)
    p.add_argument("--parameters", default=str(ROOT / "results/prefreeze/candidate_models_core_matched.json"))
    p.add_argument("--era", choices=("development", "protected"), default="development")
    p.add_argument("--bootstrap", type=int, default=2000)
    p.add_argument("--conditional-bootstrap", type=int, default=10000)
    p.add_argument("--label", default="primary")
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(func=evaluate)
    p = sub.add_parser("dev-exercise")
    p.add_argument("--bootstrap", type=int, default=50)
    p.add_argument("--conditional-bootstrap", type=int, default=1000)
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(func=dev_exercise)
    a = ap.parse_args(argv)
    a.func(a)


if __name__ == "__main__":
    main()
