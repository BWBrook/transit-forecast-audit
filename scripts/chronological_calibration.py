"""Observation-cutoff development test: fit DRC calibration on 2022, score 2023.

This is not historically executable Track A: release availability and individual
outcome availability are not reconstructed. All outcomes were previously inspected.
No per-planet posterior updates or late outcomes enter the fitted population rule.
"""

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import forecast_variance_components as f


def train_models(planets, pre, span, weights, order):
    centre = float(np.average(span, weights=weights))
    sd = float(np.sqrt(np.average((span-centre)**2, weights=weights)))
    if sd <= 0:
        raise ValueError("No training-span variation")
    x = (span-centre)/sd
    models = {"issued_gaussian": {"b":1.},
              "scaled_gaussian": f.fit(planets,[],pre=pre,mixture=False,weights=weights,order=order),
              "constant_mixture": f.fit(planets,[],pre=pre,weights=weights,order=order),
              "span_mixture": f.fit(planets,[],pre=pre,x=x,weights=weights,order=order)}
    return models, centre, sd


def score_models(models, pre, span, centre, sd, order):
    data = f.packed(pre)
    scores = {}
    x = (span-centre)/sd
    for name,model in models.items():
        mix = "mixture" in name
        theta = [np.log(model["b"])]
        if mix:
            theta.append(np.log(model["s_log_lambda"]))
        if name == "span_mixture":
            theta.append(model["beta_log_sd"])
        scores[name] = f.objective(theta,data,mix,order,x,np.ones(len(pre)),False)
    return scores


def bootstrap_indices(train_hosts, test_hosts, rng):
    hosts = np.unique(np.concatenate([train_hosts,test_hosts]))
    counts = np.bincount(rng.integers(0,len(hosts),len(hosts)), minlength=len(hosts))
    by_host = dict(zip(hosts,counts))
    return np.array([by_host[h] for h in train_hosts]), np.array([by_host[h] for h in test_hosts])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bootstrap", type=int, default=200)
    ap.add_argument("--a", type=float, default=1.0)
    args = ap.parse_args()
    if args.a <= 0 or args.bootstrap < 0:
        raise ValueError("Invalid scale or replicate count")
    sources = f.source_manifest()
    metadata_path = ROOT/"results/pilot_v1/tranche2_review/metadata_per_planet.csv"
    metadata = {r["planet"]:r for r in csv.DictReader(metadata_path.open())}
    train,c1 = f.visits("DRC",args.a,start="2022-01-01",end="2022-12-31")
    test,c2 = f.visits("DRC",args.a,start="2023-01-01",end="2024-01-03")
    if c1 or c2:
        raise ValueError("This chronological comparison requires no outcome trimming")
    pre_train = f.precompute(train,[p["m"] for p in train])
    pre_test = f.precompute(test,[p["m"] for p in test])
    span_train = np.array([np.log10(float(metadata[p["planet"]]["training_span_days"])) for p in train])
    span_test = np.array([np.log10(float(metadata[p["planet"]]["training_span_days"])) for p in test])
    hosts_train = np.array([p["host"] for p in train])
    hosts_test = np.array([p["host"] for p in test])
    windows = np.array([len(p["m"]) for p in test])
    seen = np.isin(hosts_test,hosts_train)
    models,centre,sd = train_models(train,pre_train,span_train,np.ones(len(train)),384)
    scores = score_models(models,pre_test,span_test,centre,sd,384)
    lower,lo_c,lo_s = train_models(train,pre_train,span_train,np.ones(len(train)),192)
    low_scores = score_models(lower,pre_test,span_test,lo_c,lo_s,192)
    convergence = {name:float(np.max(np.abs(scores[name]-low_scores[name]))) for name in models}
    if max(convergence.values()) > .01:
        raise RuntimeError("Chronological predictions need more accurate integration")
    rows = []
    for name,vals in scores.items():
        for i,p in enumerate(test):
            rows.append({"model":name,"planet":p["planet"],"host":p["host"],"windows":int(windows[i]),
                         "host_seen_in_early_block":bool(seen[i]),"joint_log_density":float(vals[i]),
                         "delta_vs_constant_per_window":float((vals[i]-scores["constant_mixture"][i])/windows[i]),
                         "delta_vs_issued_per_window":float((vals[i]-scores["issued_gaussian"][i])/windows[i])})
    rng = np.random.default_rng(20261107)
    bootstrap = []
    for rep in range(args.bootstrap):
        wt,ws = bootstrap_indices(hosts_train,hosts_test,rng)
        if wt.sum() == 0 or ws.sum() == 0:
            raise RuntimeError("Empty bootstrap block")
        bm,bc,bs = train_models(train,pre_train,span_train,wt,384)
        pred = score_models(bm,pre_test,span_test,bc,bs,384)
        for name in models:
            bootstrap.append({"replicate":rep,"model":name,
                              "delta_vs_constant_per_window":float(np.average((pred[name]-pred["constant_mixture"])/windows,weights=ws)),
                              "delta_vs_issued_per_window":float(np.average((pred[name]-pred["issued_gaussian"])/windows,weights=ws)),
                              "fit_at_bound":bool(bm[name].get("at_bound",False)),
                              "b":bm[name]["b"],"s_log_lambda":bm[name].get("s_log_lambda",0.),
                              "beta_log_sd":bm[name].get("beta_log_sd",0.),
                              "training_centre_log10_span":bc,"training_sd_log10_span":bs,
                              "gradient_max":bm[name].get("gradient_max",0.),
                              "near_zero_heterogeneity":bool(bm[name].get("s_log_lambda",0.) < .001)})
        if (rep+1)%50 == 0:
            print("bootstrap",rep+1,flush=True)
    conditional_rng = np.random.default_rng(20261108)
    test_unique, test_inverse = np.unique(hosts_test,return_inverse=True)
    conditional = {name:[] for name in models}
    for _ in range(2000):
        counts = np.bincount(conditional_rng.integers(0,len(test_unique),len(test_unique)),minlength=len(test_unique))
        for name in models:
            conditional[name].append(float(np.average((scores[name]-scores["constant_mixture"])/windows,weights=counts[test_inverse])))
    comparisons = []
    for name in models:
        delta = (scores[name]-scores["constant_mixture"])/windows
        b = [r for r in bootstrap if r["model"]==name]
        comparisons.append({"model":name,"mean_delta_vs_constant":float(delta.mean()),
                            "median_delta_vs_constant":float(np.median(delta)),
                            "fraction_planets_improved":float(np.mean(delta>0)),
                            "new_host_mean_delta_vs_constant":float(delta[~seen].mean()),
                            "mean_delta_vs_issued":float(np.mean((scores[name]-scores["issued_gaussian"])/windows)),
                            "host_refit_percentile95_vs_constant":list(np.quantile([r["delta_vs_constant_per_window"] for r in b],[.025,.975])) if b else None,
                            "host_refit_percentile95_vs_issued":list(np.quantile([r["delta_vs_issued_per_window"] for r in b],[.025,.975])) if b else None,
                            "conditional_fixed_fit_percentile95_vs_constant":list(np.quantile(conditional[name],[.025,.975])),
                            "bootstrap_fits_at_bound":sum(r["fit_at_bound"] for r in b),
                            "bootstrap_fits_s_below_0_001":sum(r["near_zero_heterogeneity"] for r in b)})
    contributions = []
    for model,reference in (("span_mixture","constant_mixture"),("constant_mixture","issued_gaussian")):
        delta = (scores[model]-scores[reference])/windows
        host_sums = {h:float(delta[hosts_test==h].sum()/len(test)) for h in np.unique(hosts_test)}
        ranked = sorted(host_sums,key=host_sums.get,reverse=True)
        contributions.append({"contrast":model+"_vs_"+reference,
                              "mean_gain":float(delta.mean()),"median_planet_gain":float(np.median(delta)),
                              "fraction_planets_improved":float(np.mean(delta>0)),
                              "largest_positive_host_contributions":[{"host":h,"contribution_to_mean":host_sums[h]} for h in ranked[:5]],
                              "leave_one_host_out_mean_range":[float(min(np.mean(delta[hosts_test!=h]) for h in ranked)),
                                                                 float(max(np.mean(delta[hosts_test!=h]) for h in ranked))]})
    out = ROOT/"results/pilot_v1/chronological_calibration"/f"a_{args.a:g}"
    out.mkdir(parents=True,exist_ok=True)
    f.write_csv(out/"scores.csv",rows)
    f.write_csv(out/"host_refit_bootstrap.csv",bootstrap)
    report = {"development_only":True,"light_curves_opened":0,"track":"observation-cutoff development hindcast",
              "training_dates":["2022-01-01","2022-12-31"],"evaluation_dates":["2023-01-01","2024-01-03"],
              "date_basis":"Explicit TESS record-ID calendar labels; UTC basis and first-public availability unverified",
              "a_fixed":args.a,"primary_a":1.0,"training_planets":len(train),"training_hosts":len(set(hosts_train)),
              "evaluation_planets":len(test),"evaluation_hosts":len(set(hosts_test)),"evaluation_windows":int(windows.sum()),
              "evaluation_planets_on_previously_seen_hosts":int(seen.sum()),"training_centre_log10_span":centre,"training_sd_log10_span":sd,
              "models":models,"comparisons":comparisons,"q192_q384_max_score_change":convergence,
              "score_concentration":contributions,
              "bootstrap_seed":20261107,"bootstrap_replicates":args.bootstrap,
              "conditional_fixed_fit_bootstrap":{"seed":20261108,"replicates":2000,"scope":"Resamples evaluation hosts only, with trained rule fixed; excludes training uncertainty"},
              "source_manifest":sources,"script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "dependencies":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
                              for p in (ROOT/"scripts/forecast_variance_components.py",metadata_path)],
              "command":f"python scripts/chronological_calibration.py --bootstrap {args.bootstrap} --a {args.a}",
              "limitations":["All outcomes previously inspected; predictor nominated after inspecting the full development era",
                             "2022 outcomes precede conservative DRC issue date; first-public availability of timings is unresolved",
                             "Joint per-planet density divided by retained windows, then equal-planet mean; not a pooled event log score",
                             "Population mixture prediction without per-planet posterior updating",
                             "Joint host resampling refits on early outcomes and evaluates on late outcomes; fixed a, family and selected cohort",
                             "Missing issued covariance remains a diagonal-marginal sensitivity; no sealed evaluation or model selection"]}
    (out/"summary.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps({k:report[k] for k in ("training_planets","evaluation_planets","models","comparisons")},indent=2))


if __name__ == "__main__":
    main()
