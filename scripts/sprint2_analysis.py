"""Sprint 2 outcome-calibration estimands, criteria and negative controls.

Equal-host target (S1-02): every host has total weight one and the timed
events within a host share it equally.

* z-RMS = sqrt(mean over hosts of the host mean z^2);
* 95% coverage = mean over hosts of the host coverage of exact 2.5/97.5% limits;
* median bias = weighted median of z, weight 1/n_host;
* Tmag model = equal-weight least squares of host mean z^2 on (Tmag - 11), with
  endpoint z-RMS = sqrt(predicted mean z^2) at Tmag 9 and 13.5. The host mean
  z^2 is unbiased for the host mean square at any n, unlike log(mean z^2);
* recovery = mean over hosts of timed / observable intended truths, all
  failures (product, identification, run, coverage, edge, unmatched) included.

Intervals are host-cluster percentile bootstraps.

    .venv/bin/python scripts/sprint2_analysis.py check                 # negative controls
    .venv/bin/python scripts/sprint2_analysis.py analyse --sample dev  # or confirm
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "sprint2"
TMAG_RANGES = {"A_lt10": (8.0, 10.0), "B_10_11": (10.0, 11.0), "C_11_12": (11.0, 12.0), "D_12_13.5": (12.0, 13.5)}
U = 1.10
CRITERIA = {"z_rms_ci90_within": [1 / U, U], "cover95_ci90_lower_ge": 0.93, "mean_z_ci90_within": [-0.15, 0.15],
            "tmag_endpoint_z_rms_ci90_within": [0.80, 1.15], "noise_ratio_median_within": [0.95, 1.05],
            "min_hosts": 60}


def wmedian(x, w):
    o = np.argsort(x)
    x, w = x[o], w[o]
    c = np.cumsum(w)
    return float(x[np.searchsorted(c, 0.5 * c[-1])])


class Hosts:
    """Per-host arrays for fast cluster resampling."""

    def __init__(self, z, cov, host, tmag):
        self.ids = sorted(set(host))
        ix = {h: i for i, h in enumerate(self.ids)}
        self.h = np.array([ix[x] for x in host])
        self.z, self.cov = np.asarray(z, float), np.asarray(cov, float)
        self.n = np.bincount(self.h, minlength=len(self.ids))
        self.mse = np.bincount(self.h, self.z ** 2, len(self.ids)) / self.n
        self.c95 = np.bincount(self.h, self.cov, len(self.ids)) / self.n
        self.zbar = np.bincount(self.h, self.z, len(self.ids)) / self.n
        tm = np.zeros(len(self.ids))
        tm[self.h] = np.asarray(tmag, float)
        self.tmag = tm

    def stats(self, mult):
        """mult: host multiplicities (bootstrap counts); returns the estimand vector."""
        w = mult.astype(float)
        zr = math.sqrt(np.sum(w * self.mse) / w.sum())
        cv = float(np.sum(w * self.c95) / w.sum())
        ew = (w / self.n)[self.h]
        sel = ew > 0
        med = wmedian(self.z[sel], ew[sel])
        x = self.tmag - 11
        X = np.column_stack([np.ones_like(x), x])
        W = np.sqrt(w)
        beta = np.linalg.lstsq(X * W[:, None], self.mse * W, rcond=None)[0]
        e9, e13 = beta[0] - 2 * beta[1], beta[0] + 2.5 * beta[1]
        mz = float(np.sum(w * self.zbar) / w.sum())
        return np.array([zr, cv, med, math.sqrt(max(e9, 0)), math.sqrt(max(e13, 0)), beta[1], mz])

    def boot(self, B, rng):
        H = len(self.ids)
        point = self.stats(np.ones(H, int))
        sims = np.array([self.stats(np.bincount(rng.integers(0, H, H), minlength=H)) for _ in range(B)])
        return point, sims


NAMES = ("z_rms", "cover95", "median_z", "z_rms_tmag9", "z_rms_tmag13.5", "mse_slope_per_mag", "mean_z")


def summarise(hs, B, rng):
    point, sims = hs.boot(B, rng)
    out = {"hosts": len(hs.ids), "events": int(len(hs.z)),
           "host_events_min_median_max": [int(hs.n.min()), float(np.median(hs.n)), int(hs.n.max())]}
    for j, k in enumerate(NAMES):
        out[k] = round(float(point[j]), 4)
        out[k + "_ci90"] = [round(float(v), 4) for v in np.percentile(sims[:, j], [5, 95])]
        out[k + "_ci95"] = [round(float(v), 4) for v in np.percentile(sims[:, j], [2.5, 97.5])]
    out["event_weighted"] = {"z_rms": round(float(np.sqrt(np.mean(hs.z ** 2))), 4),
                             "cover95": round(float(np.mean(hs.cov)), 4), "median_z": round(float(np.median(hs.z)), 4)}
    return out


def verdict(s, noise=None):
    c = CRITERIA
    checks = {
        "min_hosts": s["hosts"] >= c["min_hosts"],
        "z_rms": c["z_rms_ci90_within"][0] <= s["z_rms_ci90"][0] and s["z_rms_ci90"][1] <= c["z_rms_ci90_within"][1],
        "cover95": s["cover95_ci90"][0] >= c["cover95_ci90_lower_ge"],
        "mean_z": c["mean_z_ci90_within"][0] <= s["mean_z_ci90"][0] and s["mean_z_ci90"][1] <= c["mean_z_ci90_within"][1],
        "tmag9": c["tmag_endpoint_z_rms_ci90_within"][0] <= s["z_rms_tmag9_ci90"][0] and s["z_rms_tmag9_ci90"][1] <= c["tmag_endpoint_z_rms_ci90_within"][1],
        "tmag13.5": c["tmag_endpoint_z_rms_ci90_within"][0] <= s["z_rms_tmag13.5_ci90"][0] and s["z_rms_tmag13.5_ci90"][1] <= c["tmag_endpoint_z_rms_ci90_within"][1]}
    if noise is not None:
        for k in ("beta_ratio", "resid_rms_ratio"):
            checks["noise_" + k] = c["noise_ratio_median_within"][0] <= noise[k] <= c["noise_ratio_median_within"][1]
    return {"checks": checks, "pass": all(checks.values())}


# ---------------------------------------------------------------- negative controls

def simulate(scenario, rng, counts, H=120):
    strata = list(TMAG_RANGES)
    tmag = np.concatenate([rng.uniform(*TMAG_RANGES[s], H // 4) for s in strata])
    n = rng.choice(counts, H)
    host, z, cov = [], [], []
    truth = {"z_rms": 1.0, "median_z": 0.0, "mean_z": 0.0, "z_rms_tmag9": 1.0, "z_rms_tmag13.5": 1.0}
    for h in range(H):
        k = 1.0
        if scenario == "heteroscedastic":
            k = math.exp(rng.normal(0, 0.2) - 0.04)
        if scenario == "tmag_trend":
            k = math.sqrt(1 + 0.06 * (tmag[h] - 11))
        if scenario == "heavy_tails":
            e = rng.standard_t(5, n[h]) / math.sqrt(5 / 3)
        elif scenario == "shared_shape":
            g = rng.integers(0, 2, n[h])
            u = rng.normal(0, 0.3, 2)
            e = (u[g] + rng.normal(0, 1, n[h])) / math.sqrt(1.09)
        else:
            e = rng.normal(0, 1, n[h])
        zz = k * e
        host += [h] * n[h]
        z.append(zz)
        cov.append(np.abs(zz) <= 1.959964)
    if scenario == "heteroscedastic":
        truth["z_rms"] = 1.0
    if scenario == "tmag_trend":
        truth["z_rms_tmag9"], truth["z_rms_tmag13.5"] = math.sqrt(1 - 0.12), math.sqrt(1 + 0.15)
        truth["z_rms"] = math.sqrt(float(np.mean(1 + 0.06 * (tmag - 11))))
    return Hosts(np.concatenate(z), np.concatenate(cov), host, np.repeat(tmag, n)), truth


def check(args):
    rng = np.random.default_rng(20261107)
    led = OUT / "dev" / "ledger.csv"
    if led.exists():
        rows = [r for r in csv.DictReader(led.open()) if r["status"] == "timed" and r["mode"] == "remove"]
        per = defaultdict(int)
        for r in rows:
            per[(r["host"], r["product"])] += 1
        counts = np.array(list(per.values()))
        source = "sprint2 dev ledger, timed per host-product"
    else:
        rows = [r for r in csv.DictReader((ROOT / "results/t015_validation/injections.csv").open()) if r["status"] == "timed"]
        per = defaultdict(int)
        for r in rows:
            per[(r["host"], r["product"], r["flux"])] += 1
        counts = np.array(list(per.values()))
        source = "D039 injections, timed per host-product-flux"
    out = {"host_event_counts_source": source, "counts_min_median_max": [int(counts.min()), float(np.median(counts)),
                                                                       int(counts.max())],
           "hosts": 120, "replicates": args.reps, "bootstrap": args.boot, "scenarios": {}}
    idx = {k: NAMES.index(k) for k in ("z_rms", "median_z", "mean_z", "z_rms_tmag9", "z_rms_tmag13.5")}
    for sc in ("gaussian", "heteroscedastic", "shared_shape", "heavy_tails", "tmag_trend"):
        hit = defaultdict(int)
        est = defaultdict(list)
        width = defaultdict(list)
        for _ in range(args.reps):
            hs, truth = simulate(sc, rng, counts)
            point, sims = hs.boot(args.boot, rng)
            for k, j in idx.items():
                lo, hi = np.percentile(sims[:, j], [5, 95])
                hit[k] += lo <= truth[k] <= hi
                est[k].append(point[j])
                width[k].append(hi - lo)
        out["scenarios"][sc] = {k: {"truth": round(truth[k], 4), "ci90_coverage": round(hit[k] / args.reps, 3),
                                    "mean_estimate": round(float(np.mean(est[k])), 4),
                                    "mean_ci90_width": round(float(np.mean(width[k])), 4)} for k in idx}
        print(sc, json.dumps(out["scenarios"][sc]), flush=True)
    (OUT / "estimand_negative_controls.json").write_text(json.dumps(out, indent=1) + "\n")


# ---------------------------------------------------------------- analysis

def load(sample):
    import gzip
    d = OUT / sample

    def rd(n):
        path = d / n
        if not path.exists() and (d / (n + ".gz")).exists():
            return list(csv.DictReader(gzip.open(d / (n + ".gz"), "rt")))
        return list(csv.DictReader(path.open()))
    return rd("ledger.csv"), rd("runs.csv"), rd("products.csv"), rd("real_transits.csv")


def production(rows):
    """Production rule: SPOC_120 where the host has that product, otherwise TESS-SPOC_200."""
    has = {r["host"] for r in rows if r["product"] == "SPOC_120"}
    return [r for r in rows if r["product"] == ("SPOC_120" if r["host"] in has else "TESS-SPOC_200")]


def recovery(ledger, sel, B, rng):
    obs = [r for r in ledger if sel(r) and r.get("truth_id") and r.get("observable") == "True"]
    by = defaultdict(lambda: [0, 0])
    status = defaultdict(int)
    for r in obs:
        by[r["host"]][0] += r["status"] == "timed"
        by[r["host"]][1] += 1
        status[r["status"]] += 1
    if not by:
        return None
    hosts = sorted(by)
    rate = np.array([by[h][0] / by[h][1] for h in hosts])
    sims = [rate[rng.integers(0, len(hosts), len(hosts))].mean() for _ in range(B)]
    return {"hosts": len(hosts), "observable_truths": len(obs), "status_counts": dict(status),
            "equal_host_recovery": round(float(rate.mean()), 4),
            "ci90": [round(float(v), 4) for v in np.percentile(sims, [5, 95])],
            "event_pooled_recovery": round(status["timed"] / len(obs), 4)}


def noise_control(ledger, real, sel):
    by_inj, by_real = defaultdict(list), defaultdict(list)
    for r in ledger:
        if sel(r) and r["status"] == "timed" and r["mode"] == "remove":
            by_inj[(r["host"], r["product"])].append((float(r["beta"]), float(r["resid_rms"])))
    for r in real:
        if sel(r) and r["status"] == "timed" and r.get("resid_rms"):
            by_real[(r["host"], r["product"])].append((float(r["beta"]), float(r["resid_rms"])))
    keys = sorted(set(by_inj) & set(by_real))
    if not keys:
        return None
    rb = [np.median([x[0] for x in by_inj[k]]) / np.median([x[0] for x in by_real[k]]) for k in keys]
    rr = [np.median([x[1] for x in by_inj[k]]) / np.median([x[1] for x in by_real[k]]) for k in keys]
    return {"host_products": len(keys), "beta_ratio": round(float(np.median(rb)), 4),
            "resid_rms_ratio": round(float(np.median(rr)), 4),
            "resid_rms_ratio_iqr": [round(float(v), 4) for v in np.percentile(rr, [25, 75])]}


def paired_modes(ledger, sel, a="remove", b="subtract"):
    def key(r):
        return (r["host"], r["product"], r["phase"], r["truth_id"].split("|")[-1])
    A = {key(r): r for r in ledger if sel(r) and r["mode"] == a and r.get("truth_id")}
    Bm = {key(r): r for r in ledger if sel(r) and r["mode"] == b and r.get("truth_id")}
    both = [k for k in A if k in Bm and A[k]["status"] == "timed" and Bm[k]["status"] == "timed"]
    if not both:
        return None
    za, zb = np.array([float(A[k]["z"]) for k in both]), np.array([float(Bm[k]["z"]) for k in both])
    obs = [k for k in A if k in Bm and A[k]["observable"] == "True" and Bm[k]["observable"] == "True"]
    return {"paired_timed": len(both), "z_rms": [round(float(np.sqrt(np.mean(za ** 2))), 4),
                                                 round(float(np.sqrt(np.mean(zb ** 2))), 4)],
            "median_z": [round(float(np.median(za)), 4), round(float(np.median(zb)), 4)],
            "cover95": [round(float(np.mean([A[k]["cover95"] == "True" for k in both])), 4),
                        round(float(np.mean([Bm[k]["cover95"] == "True" for k in both])), 4)],
            "jointly_observable": len(obs),
            "timed_fraction": [round(float(np.mean([A[k]["status"] == "timed" for k in obs])), 4) if obs else None,
                               round(float(np.mean([Bm[k]["status"] == "timed" for k in obs])), 4) if obs else None],
            "order": [a, b]}


def analyse(args):
    ledger, runs, prods, real = load(args.sample)
    rng = np.random.default_rng(20261107)
    B = args.bootstrap
    timed = [r for r in ledger if r["status"] == "timed" and r.get("truth_id")]
    out = {"sample": args.sample, "estimand": "equal-host; see module docstring", "criteria": CRITERIA,
           "bootstrap": B, "groups": {}}
    sets = [("production", production)] + [(p, lambda rs, p=p: [r for r in rs if r["product"] == p])
                                          for p in ("SPOC_120", "TESS-SPOC_200")]
    subsets = ["all"]
    if args.sample == "dev":
        subsets += ["validation", "calibration"]
    import sprint2_outcomes as so
    for rule in ("t015v3c", "t015v3"):
      for mode in ("remove", "subtract", "shape"):
        for name, fn in sets:
            for sub in subsets:
                rows = [r for r in fn(timed) if r["mode"] == mode and (sub == "all" or r["set"] == sub)]
                if len({r["host"] for r in rows}) < 3:
                    continue
                g = [so.tmag_multiplier(r["tmag"]) if rule == "t015v3c" else 1.0 for r in rows]
                hs = Hosts([float(r["z"]) / k for r, k in zip(rows, g)],
                           [-k * float(r["lo95_s"]) <= float(r["err_s"]) <= k * float(r["hi95_s"]) for r, k in zip(rows, g)],
                           [r["host"] for r in rows], [float(r["tmag"]) for r in rows])
                s = summarise(hs, B if mode == "remove" else min(B, 2000), rng)
                s["stratum"] = {}
                for st in TMAG_RANGES:
                    si = [i for i, r in enumerate(rows) if r["stratum"] == st]
                    if len({rows[i]["host"] for i in si}) >= 3:
                        hh = Hosts(hs.z[[i for i in si]], hs.cov[[i for i in si]],
                                   [rows[i]["host"] for i in si], [float(rows[i]["tmag"]) for i in si])
                        ss = summarise(hh, 2000, rng)
                        s["stratum"][st] = {k: ss[k] for k in ("hosts", "events", "z_rms", "z_rms_ci90", "cover95",
                                                               "cover95_ci90", "mean_z", "mean_z_ci90", "median_z")}
                prodsel = {r["host"] for r in fn(ledger)}
                selp = (lambda r, mode=mode, sub=sub, prodsel=prodsel, name=name:
                        r["mode"] == mode and (sub == "all" or r.get("set") == sub)
                        and (r["product"] in (name,) if name != "production" else True))
                plist = fn([r for r in ledger if r.get("truth_id") or r["status"].startswith("product")])
                pkeys = {(r["host"], r["product"]) for r in plist}
                sel_rec = lambda r, selp=selp, pkeys=pkeys: selp(r) and (r["host"], r["product"]) in pkeys  # noqa: E731
                s["recovery"] = recovery(ledger, sel_rec, 2000, rng)
                s["recovery_by_stratum"] = {st: recovery(ledger, lambda r, st=st, f=sel_rec: f(r) and r["stratum"] == st,
                                                         2000, rng) for st in TMAG_RANGES}
                if mode == "remove":
                    s["noise_control"] = noise_control(ledger, real, lambda r, pk=pkeys: (r["host"], r["product"]) in pk
                                                       and (sub == "all" or r.get("set") == sub))
                    s["verdict"] = verdict(s, s["noise_control"])
                out["groups"][f"{rule}|{mode}|{name}|{sub}"] = s
    out["paired_remove_vs_subtract"] = paired_modes(ledger, lambda r: True)
    out["paired_remove_vs_shape"] = paired_modes(ledger, lambda r: True, "remove", "shape")
    out["runs_by_status"] = dict(sorted(defaultdict(int, {k: sum(1 for r in runs if r["status"].split(":")[0] == k)
                                                          for k in {r["status"].split(":")[0] for r in runs}}).items()))
    out["products_by_status"] = {k: sum(1 for r in prods if r["status"].split(":")[0] == k)
                                 for k in sorted({r["status"].split(":")[0] for r in prods})}
    out["ledger_by_status"] = {k: sum(1 for r in ledger if r["status"] == k) for k in sorted({r["status"] for r in ledger})}
    out["spurious_windows"] = sum(1 for r in ledger if r["status"].startswith("spurious"))
    out["one_to_one"] = {"duplicate_truth_ids": len(timed) - len({r["truth_id"] for r in timed}),
                         "max_match_dist_s": max((float(r["match_dist_s"]) for r in timed), default=None),
                         "gate_s": 3600}
    dest = OUT / args.sample / "summary.json"
    dest.write_text(json.dumps(out, indent=1, default=float) + "\n")
    for k in ("t015v3c|remove|production|all", "t015v3|remove|production|all", "t015v3c|remove|SPOC_120|all",
              "t015v3c|remove|TESS-SPOC_200|all"):
        if k in out["groups"]:
            g = out["groups"][k]
            print(k, {x: g[x] for x in ("hosts", "events", "z_rms", "z_rms_ci90", "cover95", "cover95_ci90", "mean_z",
                                        "mean_z_ci90", "median_z", "z_rms_tmag9_ci90", "z_rms_tmag13.5_ci90")},
                  g["verdict"], g["recovery"], g["noise_control"])


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("check")
    p.add_argument("--reps", type=int, default=400)
    p.add_argument("--boot", type=int, default=1000)
    p.set_defaults(func=check)
    p = sub.add_parser("analyse")
    p.add_argument("--sample", choices=("dev", "confirm"), required=True)
    p.add_argument("--bootstrap", type=int, default=10000)
    p.set_defaults(func=analyse)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
