"""Run the prespecified inspected-development experiment and I2 commands."""

from __future__ import annotations

import argparse
import csv
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

import sprint1_forecast_core as c
import forecast_variance_components as f
from reproduce_table5 import load

ROOT = c.ROOT
METRICS = ("is95_standardised","is95_minutes","is95_forecast_normalised",
           "negative_log_score_seconds","covered95","width95_minutes")


def forecast_rows(events, models, version):
    rows = []
    for e in events:
        row = dict(e)
        for m,v in models.items():
            row[m+"_b"],row[m+"_s_log_lambda"] = v["b"],v["s_log_lambda"]
        row["parameter_version"] = version
        rows.append(row)
    return rows


def uncertainty(train, test, models, count, seed):
    rng = np.random.default_rng(seed)
    th = np.array([p["host"] for p in train])
    ids = sorted({e["planet"] for e in test})
    byplanet = {e["planet"]:e["host"] for e in test}
    sh = np.array([byplanet[p] for p in ids])
    hosts = np.unique(np.concatenate([th,sh]))
    ix = {h:i for i,h in enumerate(hosts)}
    ti,si = np.array([ix[h] for h in th]),np.array([ix[h] for h in sh])
    reference = c.predictive_scores(test,models["M0"])
    rows = []
    for rep in range(count):
        mult = np.bincount(rng.integers(0,len(hosts),len(hosts)),minlength=len(hosts))
        wt,ws = mult[ti],mult[si]
        if wt.sum() == 0 or ws.sum() == 0:
            raise RuntimeError("Empty bootstrap fitting/scoring sample")
        fitted = c.fit_methods(train,weights=wt)
        for method in c.METHODS[1:]:
            score = c.predictive_scores(test,fitted[method])
            row = {"replicate":rep,"method":method,"b":fitted[method]["b"],
                   "s_log_lambda":fitted[method]["s_log_lambda"],
                   "at_bound":fitted[method]["at_bound"],
                   "gradient_max":fitted[method]["gradient_max"]}
            for metric in METRICS:
                _,pm = c.planet_aggregate(test,score[metric]-reference[metric])
                row["delta_"+metric] = float(np.average(pm,weights=ws)) if np.all(np.isfinite(pm)) else None
            rows.append(row)
    summary = {}
    for method in c.METHODS[1:]:
        sub = [r for r in rows if r["method"]==method]
        summary[method] = {"replicates":count,"fits_at_bound":sum(r["at_bound"] for r in sub),
                           "near_zero_heterogeneity":sum(r["s_log_lambda"]<.001 for r in sub),
                           "parameter_percentile95":{p:list(np.quantile([r[p] for r in sub],[.025,.975]))
                                                     for p in ("b","s_log_lambda")} if sub else None}
        for metric in METRICS:
            vals = [r["delta_"+metric] for r in sub]
            summary[method]["delta_"+metric+"_percentile95"] = list(np.quantile(vals,[.025,.975])) if vals and None not in vals else None
        ci = summary[method]["delta_is95_standardised_percentile95"]
        summary[method]["conditional_decision"] = ("improves" if ci and ci[1]<0 else
                                                     "worsens" if ci and ci[0]>0 else "inconclusive")
    return rows,summary


def influence(events, scores, training_ids):
    out = {}
    hostby = {r["planet"]:r["host"] for r in events}
    for method in c.METHODS[1:]:
        ids,delta = c.planet_aggregate(events,scores[method]["is95_standardised"]-scores["M0"]["is95_standardised"])
        hosts = np.array([hostby[p] for p in ids])
        contrib = {h:float(delta[hosts==h].sum()/len(ids)) for h in np.unique(hosts)}
        top = sorted(contrib,key=lambda h:abs(contrib[h]),reverse=True)[:2]
        keep = ~np.isin(hosts,top)
        common = np.array([p in training_ids for p in ids])
        out[method] = {"top_two_absolute_contribution_hosts":[{"host":h,"contribution":contrib[h]} for h in top],
                       "leave_top_two_out_delta":float(delta[keep].mean()),
                       "common_planets":int(common.sum()),
                       "common_planet_delta":float(delta[common].mean()) if common.any() else None,
                       "new_planets":int((~common).sum()),
                       "new_planet_delta":float(delta[~common].mean()) if (~common).any() else None}
    return out


def numerical_check(events, models, scores):
    result = {}
    for m in c.METHODS:
        high = c.predictive_scores(events,models[m],order=384)
        exact = c.predictive_scores(events,models[m],order=384,interpolate=False)
        result[m] = {
            "max_width95_relative_192_vs384":float(np.max(np.abs(scores[m]["width95_minutes"]-high["width95_minutes"])/high["width95_minutes"])),
            "max_log_density_abs_192_vs384":float(np.max(np.abs(scores[m]["negative_log_score_seconds"]-high["negative_log_score_seconds"]))),
            "max_width95_relative_interpolation":float(np.max(np.abs(high["width95_minutes"]-exact["width95_minutes"])/exact["width95_minutes"]))}
        if result[m]["max_width95_relative_192_vs384"] > .001 or result[m]["max_log_density_abs_192_vs384"] > .01 or result[m]["max_width95_relative_interpolation"] > 1e-4:
            raise RuntimeError("Predictive integration/interpolation requires repair: "+m+" "+str(result[m]))
    return result


def run_one(name, spec, a, setting, reps, output, summary_dir, seed, details=False):
    train_ev,tr_excluded = c.development_events(**spec["train"],a=a,setting=setting)
    test_ev,te_excluded = c.development_events(**spec["test"],a=a,setting=setting)
    trainids = {r["event_id"] for r in train_ev}
    if trainids & {r["event_id"] for r in test_ev}:
        raise ValueError("Training and scoring events overlap")
    train = c.visit_planets(train_ev)
    models = c.fit_methods(train)
    scores = {m:c.predictive_scores(test_ev,models[m]) for m in c.METHODS}
    aggregates = c.aggregate(test_ev,scores)
    numeric = numerical_check(test_ev,models,scores)
    low = c.fit_methods(train,order=192)
    fitcheck = {m:{p:abs(models[m][p]-low[m][p]) for p in ("b","s_log_lambda")} for m in c.METHODS}
    boot,intervals = uncertainty(train,test_ev,models,reps,seed)
    stem = f"{name}/a_{a:g}/{setting}"
    dest = output/stem
    dest.mkdir(parents=True,exist_ok=True)
    c.write_json(dest/"parameters.json",{"models":models,"experiment":name,"a":a,"covariance":setting,
                                        "training_event_ids":sorted(trainids),"training_status":spec["status"]})
    version = c.digest(dest/"parameters.json")
    if details:
        f.write_csv(dest/"events.csv",test_ev)
        f.write_csv(dest/"training_events.csv",train_ev)
        f.write_csv(dest/"forecasts.csv",forecast_rows(test_ev,models,version))
        f.write_csv(dest/"scores.csv",c.score_rows(test_ev,scores,version))
        f.write_csv(dest/"excluded.csv",tr_excluded+te_excluded)
    if boot:
        f.write_csv(dest/"host_refit_bootstrap.csv",boot)
    summary = {"experiment":name,"status":spec["status"],"a":a,"covariance":setting,
               "scored_unit":"catalogue event; equal planet then event weights, one origin",
               "fit_unit":"unclipped span-capped visit means with shared ephemeris covariance",
               "train_events":len(train_ev),"train_planets":len(train),"train_hosts":len({p["host"] for p in train}),
               "test_events":len(test_ev),"test_planets":len({r["planet"] for r in test_ev}),
               "test_hosts":len({r["host"] for r in test_ev}),"unusable_train_rows":len(tr_excluded),
               "unusable_test_rows":len(te_excluded),"C3_test_planets":sorted({r["planet"] for r in test_ev if r["covariance_tier"].startswith("C3")}),
               "test_pre_issue_events":sum(r["horizon_days"]<=0 for r in test_ev),
               "models":models,"metrics":aggregates,"host_refit":intervals,"numeric":numeric,
               "fit_parameter_difference_192_384":fitcheck,
               "influence":influence(test_ev,scores,{p["planet"] for p in train}),
               "parameter_sha256":version,"details_directory":str(dest.relative_to(ROOT)) if dest.is_relative_to(ROOT) else str(dest),
               "protected_outcomes_accessed":False,"actually_issued_correction":False,
               "historical_input_availability_verified":name=="delayed_origin",
               "calibration_origin_utc":spec.get("calibration_origin_utc"),
               "historically_deployable":False}
    c.write_json(summary_dir/(stem.replace("/","__")+".json"),summary)
    return summary


def run(args):
    cfg = json.loads((ROOT/"configs/sprint1.json").read_text())
    sources = f.source_manifest()
    provenance_paths = [ROOT/"configs/sprint1.json",ROOT/"configs/sprint1_delayed_origin.json",
                        ROOT/"scripts/sprint1_forecasts.py",ROOT/"scripts/sprint1_forecast_core.py",
                        ROOT/"scripts/forecast_variance_components.py",ROOT/"scripts/reproduce_table5.py",
                        ROOT/"src/transit_audit/exoclock.py",ROOT/"results/pilot_v1/covariance_completeness.csv",
                        ROOT/"data/fixtures/exoclock_ttv_flags.csv"]
    provenance = {str(p.relative_to(ROOT)):c.digest(p) for p in provenance_paths}
    output = Path(args.output)
    summary_dir = Path(args.summary)
    summaries = []
    names = list(cfg["experiments"]) if args.experiment=="all" else [args.experiment]
    for name in names:
        if name == "delayed_origin":
            spec = json.loads((ROOT/"configs/sprint1_delayed_origin.json").read_text())
        elif name == "late_published_proxy":
            spec = cfg["secondary_release_proxy"]
        else:
            spec = cfg["experiments"][name]
        scenarios = [(c.REFERENCE_A,"c2",args.bootstrap)]
        if args.sensitivities:
            scenarios += [(a,"c2",args.sensitivity_bootstrap) for a in cfg["outcome_scale_grid"] if a != c.REFERENCE_A]
            scenarios += [(c.REFERENCE_A,s,args.sensitivity_bootstrap) for s in c.SETTINGS if s!="c2"]
        for a,setting,reps in scenarios:
            began = time.monotonic()
            summary = run_one(name,spec,a,setting,reps,output,summary_dir,cfg["seed"],details=(a==c.REFERENCE_A and setting=="c2"))
            summaries.append(summary)
            print(name,a,setting,"seconds",round(time.monotonic()-began,1),
                  "M2 delta",summary["metrics"]["M2"]["delta_standardised_vs_M0"],flush=True)
    receipts = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p):c.digest(p)
                for p in sorted(summary_dir.glob("*__*.json"))
                if args.experiment=="all" or p.name.startswith(args.experiment+"__")}
    if any(c.digest(ROOT/path)!=value for path,value in provenance.items()):
        raise RuntimeError("Source/config drift during run; outputs are not qualified by a receipt")
    import scipy
    c.write_json(summary_dir/("receipt_"+args.experiment+".json"),
                 {"config_sha256":c.digest(ROOT/"configs/sprint1.json"),"source_manifest":sources,
                  "source_config_sha256":provenance,"source_unchanged_during_run":True,
                  "environment":{"python":platform.python_version(),"numpy":np.__version__,"scipy":scipy.__version__},
                  "summary_hashes":receipts,"seed":cfg["seed"],"protected_access":False})


def make_forecasts(args):
    with Path(args.events).open() as handle:
        events = list(csv.DictReader(handle))
    params = json.loads(Path(args.parameters).read_text())
    models = params["models"]
    if set(models) != set(c.METHODS):
        raise ValueError("I2 requires exactly M0-M3")
    eph,_,_ = load()
    cov = c.covariance_rows()
    rows = []
    for row in events:
        e = eph[args.release][row["planet"]]
        n = int(row["forecast_epoch"])
        rho = c.correlation(args.release,row["planet"],args.covariance,cov)
        discrepancy=abs(float(cov[args.release,row["planet"]]["p_refit_minus_published_s"]))/(e.sigma_period_days*86400)
        rows.append({"event_id":row["event_id"],"observation_id":row["observation_id"],
                     "planet":row["planet"],"host":row["host"],"release":args.release,
                     "forecast_epoch":n,"predicted_bjd_tdb":e.t0_bjd_tdb+n*e.period_days,
                     "sigma_t0_s":e.sigma_t0_days*86400,"sigma_p_s":e.sigma_period_days*86400,
                     "rho":rho,"rho_source":("released-input WLS reconstruction; not issued covariance" if args.covariance=="c2" else "prespecified sensitivity: "+args.covariance),
                     "covariance_setting":args.covariance,
                     "covariance_tier":"C2_candidate" if discrepancy<=3 else "C3_source_fit_mismatch",
                     "period_fit_discrepancy_sigma":discrepancy,
                     "forecast_variance_s2":float(c.forecast_variance(e.sigma_t0_days*86400,e.sigma_period_days*86400,n,rho)),
                     "issue_date":c.ISSUE_DATES[args.release],"issue_basis":"OSF public node and exact file ledger",
                     "epoch_basis":row.get("epoch_basis","input event manifest")})
    Path(args.output).parent.mkdir(parents=True,exist_ok=True)
    f.write_csv(Path(args.output),forecast_rows(rows,models,c.digest(args.parameters)))


def score(args):
    from sprint1_outcome_adapter import score_outcomes
    score_outcomes(args)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="command",required=True)
    p = sub.add_parser("run")
    p.add_argument("--experiment",choices=("release_transfer","chronological","delayed_origin","late_published_proxy","all"),default="all")
    p.add_argument("--bootstrap",type=int,default=400)
    p.add_argument("--sensitivity-bootstrap",type=int,default=200)
    p.add_argument("--sensitivities",action="store_true")
    p.add_argument("--output",default=str(ROOT/"data/derived/sprint1"))
    p.add_argument("--summary",default=str(ROOT/"results/sprint1/forecasts"))
    p.set_defaults(func=run)
    p = sub.add_parser("make_forecasts")
    p.add_argument("--events",required=True)
    p.add_argument("--parameters",required=True)
    p.add_argument("--release",choices=("DRB","DRC","DRD"),required=True)
    p.add_argument("--covariance",choices=c.SETTINGS,default="c2")
    p.add_argument("--output",required=True)
    p.set_defaults(func=make_forecasts)
    p = sub.add_parser("score")
    p.add_argument("--forecasts",required=True)
    p.add_argument("--outcomes",required=True)
    p.add_argument("--error-convention",required=True)
    p.add_argument("--outcome-scale",type=float,default=1.)
    p.add_argument("--output",required=True)
    p.set_defaults(func=score)
    args = ap.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
