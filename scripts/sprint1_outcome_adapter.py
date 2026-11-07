"""I1 to I2 adapter; never substitute an informative posterior for a likelihood."""

from __future__ import annotations

import csv
import json
import re
from pathlib import Path

import numpy as np
from scipy.special import ndtr, logsumexp
from scipy.optimize import brentq

import sprint1_forecast_core as c
import forecast_variance_components as f


def validate_i1(rows):
    required = {"event_id","observation_id","planet","host","tic","sector","camera","ccd",
                "product","flux","file","file_sha256","data_rel","cadenceno_first","cadenceno_last",
                "timesys","timeref","bjdrefi","bjdreff","tc_bjd_tdb","sigma_s","gauss_ok",
                "q025_s","q1587_s","q8413_s","q975_s","posterior_grid_path",
                "shape_group_id","loo_shift_s","id_method","id_period_d","id_period_source",
                "id_period_source_date","coverage_window","coverage_in_transit","status",
                "failure_reason","error_convention","rule_version"}
    for row in rows:
        missing = required-set(row)
        if missing:
            raise ValueError("Incomplete I1 columns: "+", ".join(sorted(missing)))
        for key in ("event_id","observation_id","planet","host","tic","product","flux",
                    "file","data_rel","id_period_source","id_period_source_date","rule_version"):
            if not row[key]:
                raise ValueError("Missing I1 provenance: "+key)
        if not re.fullmatch(r"[0-9a-f]{64}",row["file_sha256"]):
            raise ValueError("Invalid file SHA-256")
        if row["status"]!="timed":
            if not row["failure_reason"]:
                raise ValueError("Every failed attempt needs a reason")
            continue
        if not row["shape_group_id"]:
            raise ValueError("Timed outcomes need a dependence group")
        if any(flag in row.get("flags", "").split(";")
               for flag in ("edge", "mass_outside_fine", "coarse_fine_shift")):
            raise ValueError("Unresolved timing support must remain a failed attempt")
        if row["id_method"] not in ("blind","catalogue_period"):
            raise ValueError("Unrecognised identification method")
        for key in ("sector","camera","ccd"):
            if int(row[key])<1:
                raise ValueError("Invalid detector/sector identity")
        if row["loo_shift_s"]!="not_estimable" and not np.isfinite(float(row["loo_shift_s"])):
            raise ValueError("LOO shift needs a finite value or explicit not_estimable status")
        for key in ("coverage_window","coverage_in_transit"):
            value=float(row[key])
            if not np.isfinite(value) or not 0<=value<=1:
                raise ValueError("Invalid coverage metadata")
        if not np.all(np.isfinite([float(row[k]) for k in ("bjdrefi","bjdreff","id_period_d")])) or float(row["id_period_d"])<=0:
            raise ValueError("Invalid time/identification metadata")
        if int(row["cadenceno_last"])<int(row["cadenceno_first"]):
            raise ValueError("Reversed cadence bounds")


def likelihood_grid(path):
    raw = json.loads(Path(path).read_text())
    if raw.get("units") != "seconds" or raw.get("coordinate") != "true_midtime_minus_reported_midtime":
        raise ValueError("Grid must declare seconds and true-midtime offsets")
    if raw.get("kind") == "posterior":
        if raw.get("prior") != "uniform" or raw.get("prior_constant_over_support") is not True:
            raise ValueError("Informative posterior cannot substitute for measurement likelihood")
    elif raw.get("kind") != "likelihood":
        raise ValueError("Grid kind must be likelihood or a declared flat-prior posterior")
    x,logd = np.asarray(raw["offset_s"],dtype=float),np.asarray(raw["log_density"],dtype=float)
    if x.ndim!=1 or x.shape!=logd.shape or len(x)<5 or np.any(np.diff(x)<=0) or not np.all(np.isfinite(x)):
        raise ValueError("Invalid likelihood grid")
    if np.any(np.isnan(logd)) or np.any(np.isposinf(logd)) or not np.any(np.isfinite(logd)):
        raise ValueError("Invalid log density")
    density = np.exp(logd-np.max(logd))
    widths = np.r_[np.diff(x)[0]/2,(x[2:]-x[:-2])/2,np.diff(x)[-1]/2]
    mass = density*widths
    mass /= mass.sum()
    if mass[0]+mass[-1]>.001 or max(density[0],density[-1])>.001:
        raise ValueError("Likelihood grid has unresolved boundary mass")
    return x,mass


def grid_score(residual, vf, model, grid, denominator, order=384):
    x,w = grid
    b,s = model["b"],model["s_log_lambda"]
    if vf <= 0:
        raise ValueError("NonGaussian likelihood convolution requires positive forecast variance")
    z,lw = f.quadrature(order) if s>=1e-5 else (np.zeros(1),np.zeros(1))
    sd = b*np.sqrt(vf)*np.exp(.5*s*z)
    mixture_weights = np.exp(lw)
    keep_mixture = mixture_weights > 1e-15/len(mixture_weights)
    keep_error = w > 1e-15/len(w)
    cdf_x, cdf_sd = x[keep_error], sd[keep_mixture]
    cdf_w, cdf_mix = w[keep_error], mixture_weights[keep_mixture]
    def cdf(value):
        # Removed terms bound the absolute CDF error by 2e-15; density uses all nodes.
        return float(cdf_w @ (ndtr((value+cdf_x[:,None])/cdf_sd[None,:]) @ cdf_mix))
    bound = max(abs(x))+20*b*np.sqrt(vf)*np.exp(.25*s*s)
    lo,hi = -bound,bound
    quantiles = [brentq(lambda value: cdf(value)-p, lo, hi, xtol=1e-7, rtol=1e-12)
                 for p in (.158655254,.841344746,.025,.975)]
    a68,b68,lower,upper=quantiles
    logp = logsumexp(np.log(np.maximum(w,np.finfo(float).tiny))[:,None]+lw[None,:]
                    -.5*np.log(2*np.pi)-np.log(sd)[None,:]
                    -.5*((residual+x[:,None])/sd[None,:])**2)
    is95 = upper-lower+40*(max(lower-residual,0)+max(residual-upper,0))
    return {"is95_standardised":is95/denominator,"is95_minutes":is95/60,
            "is95_forecast_normalised":is95/np.sqrt(vf),"negative_log_score_seconds":-float(logp),
            "covered68":float(a68<=residual<=b68),"covered95":float(lower<=residual<=upper),
            "width95_minutes":(upper-lower)/60,"m0_predictive_sd_s":denominator}


def production_rows(rows, catalogue=False):
    grouped={}
    for r in rows:
        if not r.get("event_id") or not r.get("observation_id"):
            raise ValueError("Every attempted event needs event_id and observation_id")
        grouped.setdefault(r["observation_id"],[]).append(r)
    selected,omitted=[],[]
    for obs,group in grouped.items():
        if not catalogue and any(not r.get("flux") or not r.get("product") for r in group):
            raise ValueError("I1 requires explicit product and flux metadata")
        pdcsap=[r for r in group if r.get("flux","") in ("PDCSAP","pdcsap") or catalogue]
        if not pdcsap:
            raise ValueError("No declared production flux for "+obs)
        preferred=[r for r in pdcsap if r.get("product")=="SPOC_120"]
        chosen=preferred or [r for r in pdcsap if r.get("product")=="TESS-SPOC_200"] or pdcsap
        if len(chosen)!=1:
            raise ValueError("Ambiguous duplicate production observation: "+obs)
        selected.append(chosen[0])
        for r in group:
            if r is not chosen[0]:
                omitted.append({"event_id":r["event_id"],"observation_id":obs,"reason":"paired_nonproduction_product_or_flux"})
    return selected,omitted


def score_outcomes(args):
    forecast_path,outcome_path=Path(args.forecasts),Path(args.outcomes)
    source_paths = (Path(__file__), Path(c.__file__), Path(f.__file__))
    source_hashes = {str(p): c.digest(p) for p in source_paths}
    input_hashes = {str(p): c.digest(p) for p in (forecast_path, outcome_path)}
    with forecast_path.open() as handle:
        forecast_list=list(csv.DictReader(handle))
    forecasts={r["event_id"]:r for r in forecast_list}
    if len(forecasts)!=len(forecast_list):
        raise ValueError("Duplicate forecasts")
    with outcome_path.open() as handle:
        raw=list(csv.DictReader(handle))
    if len({r["event_id"] for r in raw}) != len(raw):
        raise ValueError("Duplicate outcome event ID")
    if set(forecasts)!={r["event_id"] for r in raw}:
        raise ValueError("Forecast and attempted-outcome sets must match; retain explicit failure rows")
    if args.outcome_scale<=0 or not np.isfinite(args.outcome_scale):
        raise ValueError("Outcome scale must be positive")
    if any(r.get("error_convention")!=args.error_convention for r in raw):
        raise ValueError("Mixed or incorrect outcome-error conventions")
    if args.error_convention!="exoclock_reported":
        validate_i1(raw)
    selected,omitted=production_rows(raw,catalogue=args.error_convention=="exoclock_reported")
    events,model_rows,grids,grid_hashes=[],[],[],{}
    for r in selected:
        if r["event_id"] not in forecasts:
            raise ValueError("Missing forecast for attempted event "+r["event_id"])
        fc=forecasts[r["event_id"]]
        if fc["planet"]!=r["planet"] or fc["host"]!=r["host"] or fc["observation_id"]!=r["observation_id"]:
            raise ValueError("Forecast/outcome identity mismatch")
        if r["status"]!="timed":
            omitted.append({"event_id":r["event_id"],"observation_id":r["observation_id"],"reason":r["status"]+":"+r.get("failure_reason","")})
            continue
        if r["timesys"]!="TDB" or r["timeref"]!="SOLARSYSTEM":
            raise ValueError("Unverified time standard")
        tc=float(r["tc_bjd_tdb"])
        if tc>2460313.49:
            raise ValueError("This adapter run is development-only; no protected-era scoring")
        sigma=float(r["sigma_s"])
        if not np.isfinite(sigma) or sigma<=0 or not np.isfinite(tc):
            raise ValueError("Invalid timing or uncertainty")
        models={m:{"b":float(fc[m+"_b"]),"s_log_lambda":float(fc[m+"_s_log_lambda"])} for m in c.METHODS}
        if any(v["b"]<=0 or v["s_log_lambda"]<0 or not np.all(np.isfinite(list(v.values()))) for v in models.values()):
            raise ValueError("Invalid predictive model")
        if models["M0"]!={"b":1.,"s_log_lambda":0.}:
            raise ValueError("M0 baseline changed")
        e={**r,"release":fc["release"],"sigma_s":sigma,"outcome_scale":args.outcome_scale,
           "residual_s":(tc-float(fc["predicted_bjd_tdb"]))*86400,
           "forecast_variance_s2":float(fc["forecast_variance_s2"])}
        if not np.isfinite(e["forecast_variance_s2"]) or e["forecast_variance_s2"]<0 or not np.isfinite(e["residual_s"]):
            raise ValueError("Invalid forecast mean or variance")
        gaussian=r.get("gauss_ok","").lower() in ("true","1","yes") or args.error_convention=="exoclock_reported"
        if gaussian:
            grid=None
            if args.error_convention!="exoclock_reported":
                q=[float(r[k]) for k in ("q025_s","q975_s")]
                if q[0]>=0 or q[1]<=0 or any(abs(abs(t)/(1.95996398454*sigma)-1)>.10 for t in q):
                    raise ValueError("gauss_ok contradicts exact 95% quantiles")
        else:
            path=Path(r["posterior_grid_path"])
            path=path if path.is_absolute() else c.ROOT/path
            x,w=likelihood_grid(path)
            grid_hashes[str(path)]=c.digest(path)
            grid=(x*args.outcome_scale,w)
        events.append(e);model_rows.append(models);grids.append(grid)
    counts={p:sum(r["planet"]==p for r in events) for p in {r["planet"] for r in events}}
    output=[]
    for i,(e,models,grid) in enumerate(zip(events,model_rows,grids)):
        denom=np.sqrt(e["forecast_variance_s2"]+(e["sigma_s"]*e["outcome_scale"])**2)
        if grid is not None:
            x,w=grid
            noisevar=float(w@(x*x)-(w@x)**2)
            denom=np.sqrt(e["forecast_variance_s2"]+noisevar)
        for m,model in models.items():
            vals=grid_score(e["residual_s"],e["forecast_variance_s2"],model,grid,denom) if grid is not None else {
                k:float(v[0]) for k,v in c.predictive_scores([e],model,order=384,interpolate=False).items()}
            output.append({"event_id":e["event_id"],"observation_id":e["observation_id"],"planet":e["planet"],
                           "host":e["host"],"method":m,"release":e["release"],
                           "weight":1/len(counts)/counts[e["planet"]],"resampling_cluster":e["host"],
                           "shape_group_id":e.get("shape_group_id","unknown"),
                           "parameter_version":forecasts[e["event_id"]]["parameter_version"],
                           **{k:v if np.isfinite(v) else "" for k,v in vals.items()}})
    if any(c.digest(Path(path)) != expected for path, expected in
           {**source_hashes, **input_hashes, **grid_hashes}.items()):
        raise RuntimeError("Source/input drift during scoring; no receipt issued")
    dest=Path(args.output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if output:
        f.write_csv(dest,output)
    else:
        dest.write_text("event_id,observation_id,planet,host,method,release,weight,resampling_cluster,shape_group_id,parameter_version,is95_standardised,is95_minutes,is95_forecast_normalised,negative_log_score_seconds,covered68,covered95,width95_minutes,m0_predictive_sd_s\n")
    if omitted:
        f.write_csv(dest.with_suffix(".omitted.csv"),omitted)
    c.write_json(dest.with_suffix(".receipt.json"),
                 {"forecasts_sha256":c.digest(forecast_path),"outcomes_sha256":c.digest(outcome_path),
                  "scores_sha256":c.digest(dest),"attempted_rows":len(raw),"selected_production_attempts":len(selected),
                  "adapter_source_sha256":source_hashes[str(Path(__file__))],
                  "predictive_core_sha256":source_hashes[str(Path(c.__file__))],
                  "source_config_sha256":{str(Path(k).relative_to(c.ROOT)):v for k,v in source_hashes.items()},
                  "source_inputs_unchanged_during_run":True,
                  "timed_production_events":len(events),"omitted_rows":len(omitted),
                  "error_convention":args.error_convention,"outcome_scale":args.outcome_scale,
                  "likelihood_grid_hashes":grid_hashes,
                  "nonGaussian_events":sum(g is not None for g in grids),
                  "I1_schema_checked":args.error_convention!="exoclock_reported",
                  "timed_rows_without_estimable_loo_shift":sum(e.get("loo_shift_s")=="not_estimable" for e in events),
                  "photometry_or_file_hashes_reopened_for_verification":False,
                  "development_only":True,"units":"seconds in log density; minutes in interval score",
                  "proper_score_scope":"conditional on supplied measurement likelihood; normaliser may be outcome-dependent"})
