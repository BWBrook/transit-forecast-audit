"""Development forecast comparison: common event scores and joint-host fits."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy.interpolate import PchipInterpolator
from scipy.optimize import minimize
from scipy.special import ndtr, ndtri, logsumexp

import forecast_variance_components as f
from reproduce_table5 import RAW, load
from transit_audit.exoclock import host_of, read_mid_times

ROOT = Path(__file__).resolve().parents[1]
METHODS = ("M0", "M1", "M2", "M3")
SETTINGS = ("c2", "zero", "rho_minus1", "rho_plus1")
REFERENCE_A = 1.087
ISSUE_DATES = {"DRB":"2021-10-27", "DRC":"2022-09-27", "DRD":"2025-11-18"}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def write_json(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def covariance_rows():
    with (ROOT/"results/pilot_v1/covariance_completeness.csv").open() as handle:
        return {(r["release"], r["planet"]): r for r in csv.DictReader(handle)}


def correlation(release, planet, setting, rows):
    r = rows.get((release, planet))
    if r is None:
        raise ValueError(f"No covariance reconstruction for {release} {planet}")
    rho = {"zero": 0., "rho_minus1": -1., "rho_plus1": 1.}.get(setting)
    if setting == "c2":
        rho = float(r["corr_t0_p_at_published_epoch"])
    if rho is None or not np.isfinite(rho) or not -1 <= rho <= 1:
        raise ValueError("Invalid covariance setting")
    return rho


def forecast_variance(st0, sp, n, rho):
    st0, sp, n, rho = np.broadcast_arrays(st0, sp, n, rho)
    if np.any(np.abs(rho) > 1) or np.any(st0 < 0) or np.any(sp < 0):
        raise ValueError("Invalid forecast covariance")
    return (st0+rho*sp*n)**2 + (1-rho*rho)*(sp*n)**2


def development_events(release, start, end, setting="c2", a=REFERENCE_A, source_release="DRD"):
    eph, timings, flags = load()
    if source_release == "DRC":
        timings = [m for m in read_mid_times(RAW/"p298n/all_mid_time_data.txt")
                   if m.source == "space" and m.tess_date]
    elif source_release != "DRD":
        raise ValueError("Unsupported development outcome source")
    cov = covariance_rows()
    out, rejected, seen = [], [], set()
    for m in timings:
        if not (start <= m.tess_date <= end and m.planet in eph[release]):
            continue
        if m.tess_date > "2024-01-03":
            raise ValueError("Uninspected outcome outside development boundary")
        if m.planet in flags[release]:
            rejected.append({"planet":m.planet,"record_id":m.record_id,"reason":"origin_TTV_flag"})
            continue
        if (release,m.planet) not in cov:
            rejected.append({"planet":m.planet,"record_id":m.record_id,"reason":"missing_covariance_reconstruction"})
            continue
        identity = m.planet+"|"+m.record_id
        if identity in seen:
            raise ValueError("Duplicate development source record: "+identity)
        seen.add(identity)
        e = eph[release][m.planet]
        n = int(np.rint((m.t_bjd_tdb-e.t0_bjd_tdb)/e.period_days))
        rho = correlation(release,m.planet,setting,cov)
        pred = e.t0_bjd_tdb+n*e.period_days
        cr = cov[release,m.planet]
        discrepancy = abs(float(cr["p_refit_minus_published_s"]))/(e.sigma_period_days*86400)
        out.append({"event_id":identity,"observation_id":identity,
                    "planet":m.planet,"host":host_of(m.planet),"release":release,
                    "record_id":m.record_id,"source_record_date":m.tess_date,
                    "date_basis":source_release+" record label, UTC unverified",
                    "measurement_first_available":"unknown; published in "+source_release,
                    "outcome_source_release":source_release,
                    "tc_bjd_tdb":m.t_bjd_tdb,"sigma_s":m.sigma_days*86400,
                    "outcome_scale":a,"forecast_epoch":n,"epoch_basis":"nearest issued epoch, cycle identity not independently resolved",
                    "predicted_bjd_tdb":pred,"residual_s":(m.t_bjd_tdb-pred)*86400,
                    "sigma_t0_s":e.sigma_t0_days*86400,"sigma_p_s":e.sigma_period_days*86400,
                    "rho":rho,"covariance_setting":setting,
                    "covariance_tier":"C2_candidate" if discrepancy <= 3 else "C3_source_fit_mismatch",
                    "period_fit_discrepancy_sigma":discrepancy,
                    "forecast_variance_s2":float(forecast_variance(e.sigma_t0_days*86400,e.sigma_period_days*86400,n,rho)),
                    "issue_date":ISSUE_DATES[release],
                    "issue_basis":"OSF public node plus exact file availability; day ordering used",
                    "horizon_days":(np.datetime64(m.tess_date)-np.datetime64(ISSUE_DATES[release])).astype(int).item(),
                    "status":"timed","error_convention":"exoclock_reported",
                    "shape_group_id":"unknown","timesys":"TDB","timeref":"SOLARSYSTEM",
                    "lineage_status":"catalogue row identity only; exposure independence unresolved"})
    return sorted(out,key=lambda r:(r["planet"],r["tc_bjd_tdb"])), rejected


def visit_planets(events):
    by = {}
    for r in events:
        by.setdefault(r["planet"], []).append(r)
    out = []
    for name, rows in sorted(by.items()):
        rows.sort(key=lambda r:r["tc_bjd_tdb"])
        chunks = []
        for r in rows:
            if not chunks or r["tc_bjd_tdb"]-chunks[-1][0]["tc_bjd_tdb"] > 20:
                chunks.append([])
            chunks[-1].append(r)
        means, errors, epochs = [], [], []
        for chunk in chunks:
            sigma = np.array([r["sigma_s"]*r["outcome_scale"] for r in chunk])
            weights = 1/sigma**2
            means.append(np.average([r["residual_s"] for r in chunk],weights=weights))
            epochs.append(np.average([r["forecast_epoch"] for r in chunk],weights=weights))
            errors.append(1/np.sqrt(weights.sum()))
        r = rows[0]
        out.append({"planet":name,"host":r["host"],"m":np.asarray(means),"se":np.asarray(errors),
                    "n":np.asarray(epochs),"st0":r["sigma_t0_s"],"sp":r["sigma_p_s"],
                    "rho":r["rho"],"events":len(rows)})
    return out


def fit_methods(planets, weights=None, order=384):
    pre = f.precompute(planets,[p["m"] for p in planets])
    weights = np.ones(len(planets)) if weights is None else np.asarray(weights,dtype=float)
    models = {"M0":{"b":1.,"s_log_lambda":0.,"converged":True,"at_bound":False}}
    models["M1"] = f.fit(planets,[],pre=pre,mixture=False,weights=weights,order=order)
    models["M1"]["s_log_lambda"] = 0.
    models["M3"] = f.fit(planets,[],pre=pre,weights=weights,order=order)
    data, x = f.packed(pre), np.zeros(len(planets))
    def objective(theta):
        v,g = f.objective([0.,theta[0]],data,True,order,x,weights)
        return v,g[1:]
    results = [minimize(objective,[np.log(s)],jac=True,method="L-BFGS-B",
                        bounds=[(-12,np.log(f.S_MAX))],
                        options={"ftol":1e-11,"gtol":1e-6,"maxiter":1000,"maxls":50})
               for s in (.3,1.,3.,4.)]
    good = [r for r in results if r.success and np.isfinite(r.fun)]
    if not good:
        raise RuntimeError("No converged M2 fit")
    best = min(good,key=lambda r:r.fun)
    if min(r.fun for r in results) < best.fun-1e-5:
        raise RuntimeError("Unconverged M2 fit improves likelihood")
    models["M2"] = {"b":1.,"s_log_lambda":float(np.exp(best.x[0])),"nll":float(best.fun),
                    "converged":True,"at_bound":bool(min(abs(best.x[0]+12),abs(best.x[0]-np.log(f.S_MAX))) < 1e-5),
                    "gradient_max":float(abs(best.jac[0])),"order":order}
    return {m:models[m] for m in METHODS}


def mixture_quantiles(ratio, s, probs=(.841344746,.975), order=192):
    ratio = np.asarray(ratio,dtype=float)
    if np.any(ratio < 0) or s < 0:
        raise ValueError("Negative scale")
    if s < 1e-5:
        return np.sqrt(1+ratio[:,None]**2)*ndtri(np.asarray(probs))[None,:]
    z,lw = f.quadrature(order)
    w = np.exp(lw)
    sd = np.sqrt(ratio[:,None]**2+np.exp(s*z)[None,:])
    out = []
    for prob in probs:
        lo = np.zeros(len(ratio))
        hi = np.sqrt(ratio**2+np.exp(.5*s*s))*ndtri(prob)*4
        for _ in range(48):
            mid = (lo+hi)/2
            cdf = ndtr(mid[:,None]/sd)@w
            lo,hi = np.where(cdf < prob,mid,lo),np.where(cdf >= prob,mid,hi)
        out.append((lo+hi)/2)
    return np.asarray(out).T


def predictive_scores(events, model, order=192, interpolate=True):
    vf = np.array([r["forecast_variance_s2"] for r in events])
    sy = np.array([r["sigma_s"]*r["outcome_scale"] for r in events])
    y = np.array([r["residual_s"] for r in events])
    b,s = model["b"],model["s_log_lambda"]
    sf = b*np.sqrt(vf)
    widths = np.empty((len(events),2))
    positive = sf > 0
    widths[~positive] = sy[~positive,None]*ndtri(np.array([.841344746,.975]))
    ratio = sy[positive]/sf[positive]
    if interpolate and s >= 1e-5 and len(ratio)>256 and np.ptp(np.log(ratio)) > 0:
        grid = np.linspace(np.log(ratio.min()),np.log(ratio.max()),384)
        q = mixture_quantiles(np.exp(grid),s,order=order)/np.sqrt(1+np.exp(2*grid))[:,None]
        widths[positive] = PchipInterpolator(grid,q)(np.log(ratio))*np.sqrt(sf[positive]**2+sy[positive]**2)[:,None]
    else:
        widths[positive] = mixture_quantiles(ratio,s,order=order)*sf[positive,None]
    if s < 1e-5:
        sd2 = sy**2+sf**2
        logp = -.5*(np.log(2*np.pi*sd2)+y*y/sd2)
    else:
        z,lw = f.quadrature(order)
        sd2 = sy[:,None]**2+sf[:,None]**2*np.exp(s*z)[None,:]
        logp = logsumexp(-.5*(np.log(2*np.pi*sd2)+y[:,None]**2/sd2)+lw,axis=1)
    is95 = 2*widths[:,1]+40*np.maximum(np.abs(y)-widths[:,1],0)
    denom = np.sqrt(vf+sy**2)
    return {"is95_standardised":is95/denom,"is95_minutes":is95/60,
            "is95_forecast_normalised":np.divide(is95,np.sqrt(vf),out=np.full(len(vf),np.nan),where=vf>0),
            "negative_log_score_seconds":-logp,"covered68":(np.abs(y)<=widths[:,0]).astype(float),
            "covered95":(np.abs(y)<=widths[:,1]).astype(float),"width95_minutes":2*widths[:,1]/60,
            "m0_predictive_sd_s":denom}


def planet_aggregate(events, values):
    ids = sorted({r["planet"] for r in events})
    index = {p:i for i,p in enumerate(ids)}
    inv = np.array([index[r["planet"]] for r in events])
    counts = np.bincount(inv)
    return ids,np.bincount(inv,weights=values)/counts


def aggregate(events, scores):
    out = {}
    for name,vals in scores.items():
        out[name] = {}
        for metric,array in vals.items():
            if metric == "m0_predictive_sd_s":
                continue
            _,pm = planet_aggregate(events,array)
            out[name][metric] = float(np.mean(pm)) if np.all(np.isfinite(pm)) else None
        _,pm = planet_aggregate(events,vals["is95_standardised"]-scores["M0"]["is95_standardised"])
        out[name]["delta_standardised_vs_M0"] = float(pm.mean())
        out[name]["fraction_planets_improved"] = float(np.mean(pm < 0))
        out[name]["median_planet_delta_standardised"] = float(np.median(pm))
    return out


def score_rows(events, scores, parameter_version):
    counts = {}
    for r in events:
        counts[r["planet"]] = counts.get(r["planet"],0)+1
    rows = []
    for method,vals in scores.items():
        for i,r in enumerate(events):
            rows.append({"event_id":r["event_id"],"observation_id":r["observation_id"],
                         "planet":r["planet"],"host":r["host"],"method":method,
                         "release":r["release"],"weight":1/len(counts)/counts[r["planet"]],
                         "resampling_cluster":r["host"],"shape_group_id":r.get("shape_group_id","unknown"),
                         "parameter_version":parameter_version,
                         **{k:float(v[i]) if np.isfinite(v[i]) else "" for k,v in vals.items()}})
    return rows
