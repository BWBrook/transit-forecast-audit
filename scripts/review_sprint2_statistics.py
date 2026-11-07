"""Independent table-only sprint-2 arithmetic and bounded numerical controls.

No timing pipeline, network source, FITS file or likelihood grid is loaded.
Run with .venv/bin/python scripts/review_sprint2_statistics.py.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import NormalDist

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "results/sprint2_review/statistics"
NAMES = ("z_rms", "cover95", "mean_z", "z_rms_tmag9", "z_rms_tmag13.5")


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as f:
        return list(csv.DictReader(f))


def write_json(name, value):
    (DEST / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def choose(rows, available, historical=False):
    reference = rows if historical else available
    has_spoc = {r["host"] for r in reference if r["product"] == "SPOC_120"}
    return [r for r in rows if r["product"] == ("SPOC_120" if r["host"] in has_spoc else "TESS-SPOC_200")]


def hosts(rows, rule, inverted=False):
    grouped = defaultdict(list)
    for r in rows:
        grouped[r["host"]].append(r)
    ids = sorted(grouped)
    values = []
    for host in ids:
        rs = grouped[host]
        tmag = float(rs[0]["tmag"])
        g = math.sqrt(max(0.88566859 - 0.09191112 * (min(max(tmag, 8), 13.5) - 11), 0.25)) if rule == "t015v3c" else 1
        z = np.array([float(r["z"]) / g for r in rs])
        coverage = []
        for r in rs:
            err, lo, hi = (float(r[k]) for k in ("err_s", "lo95_s", "hi95_s"))
            coverage.append(-g * (lo if inverted else hi) <= err <= g * (hi if inverted else lo))
        values.append((np.mean(z**2), np.mean(coverage), np.mean(z), tmag, len(rs)))
    return ids, np.array(values)


def statistics(values, multiplicities):
    w = np.atleast_2d(multiplicities)
    sums = w.sum(axis=1)
    mse, cov, mean, tmag, _ = values.T
    x = tmag - 11
    xbar = (w @ x) / sums
    ybar = (w @ mse) / sums
    denominator = (w @ (x*x)) / sums - xbar*xbar
    slope = ((w @ (x*mse)) / sums - xbar*ybar) / denominator
    intercept = ybar - slope*xbar
    return np.column_stack((np.sqrt(ybar), (w @ cov)/sums, (w @ mean)/sums,
                            np.sqrt(np.maximum(intercept - 2*slope, 0)),
                            np.sqrt(np.maximum(intercept + 2.5*slope, 0))))


def summarise(values, B, seed):
    rng = np.random.default_rng(seed)
    H = len(values)
    indices = rng.integers(0, H, size=(B, H))
    weights = np.zeros((B, H), int)
    np.add.at(weights, (np.repeat(np.arange(B), H), indices.ravel()), 1)
    point = statistics(values, np.ones(H))[0]
    sims = statistics(values, weights)
    ci = np.percentile(sims, [5, 95], axis=0).T
    checks = [H >= 60, 1/1.1 <= ci[0, 0] and ci[0, 1] <= 1.1,
              ci[1, 0] >= .93, -.15 <= ci[2, 0] and ci[2, 1] <= .15,
              .8 <= ci[3, 0] and ci[3, 1] <= 1.15, .8 <= ci[4, 0] and ci[4, 1] <= 1.15]
    return {"hosts": H, "events": int(values[:, 4].sum()),
            "metrics": {key: {"point": float(point[j]), "ci90": ci[j].tolist()} for j, key in enumerate(NAMES)},
            "statistical_criteria_pass": bool(all(checks)), "noise_control_included": False}


def margins():
    normal = NormalDist()
    q = normal.inv_cdf(.975)
    out = []
    for k, delta in ((1.1, 0), (1/1.1, 0), (1, .15), (1.1, .15), (1.15, .15)):
        values = {}
        for r in (1, 2.6, math.inf):
            if math.isinf(r):
                width, sd, mean = q, k, delta
            else:
                nominal = math.sqrt(1 + r*r)
                width, sd, mean = q, math.sqrt(1 + k*k*r*r)/nominal, delta*r/nominal
            coverage = normal.cdf((width-mean)/sd) - normal.cdf((-width-mean)/sd)
            phi = lambda x: math.exp(-x*x/2)/math.sqrt(2*math.pi)
            a, b = (mean-width)/sd, (-width-mean)/sd
            expected_excess = (mean-width)*normal.cdf(a) + sd*phi(a)
            expected_excess += (-mean-width)*normal.cdf(b) + sd*phi(b)
            values[str(r)] = {"coverage": coverage, "standardised_expected_IS95": 2*width + 40*expected_excess}
        out.append({"measurement_scale_k": k, "measurement_mean_shift_sigma_y": delta, "by_sigma_y_over_sigma_f": values})
    return {"assumptions": "Independent Gaussian forecast and outcome errors, additive outcome mean delta*sigma_y; issued SD held fixed.",
            "formula": "Phi((q*sqrt(1+r^2)-delta*r)/sqrt(1+k^2*r^2))-Phi((-q*sqrt(1+r^2)-delta*r)/sqrt(1+k^2*r^2))",
            "scenarios": out}


def controls(values, reps, B):
    rng = np.random.default_rng(1172026)
    H = len(values)
    n = values[:, 4].astype(int)
    mask = np.arange(n.max())[None, :] < n[:, None]
    controls = {}
    for scenario in ("gaussian", "student_t5", "coverage_boundary_0.93", "coverage_below_margin_0.925"):
        hits = np.zeros(5, int)
        estimates = []
        passed = []
        true_coverage = .93 if scenario == "coverage_boundary_0.93" else .925 if scenario == "coverage_below_margin_0.925" else .95
        scale = NormalDist().inv_cdf(.975)/NormalDist().inv_cdf((1+true_coverage)/2)
        truth = np.array([scale, true_coverage, 0, scale, scale])
        if scenario == "student_t5":
            truth[0] = truth[3] = truth[4] = 1
            # t5 = Z/sqrt(chi2_5/5), rescaled to variance one; direct CDF quadrature.
            z0 = NormalDist().inv_cdf(.975)*math.sqrt(5/3)
            theta = math.atan(z0/math.sqrt(5))
            truth[1] = (3*theta/8 + math.sin(2*theta)/4 + math.sin(4*theta)/32)/(3*math.pi/16)
        for _ in range(reps):
            if scenario == "student_t5":
                z = rng.standard_t(5, size=mask.shape)/math.sqrt(5/3)
            else:
                z = rng.normal(0, scale, size=mask.shape)
            mse = np.sum(z*z*mask, axis=1)/n
            c95 = np.sum((np.abs(z) <= NormalDist().inv_cdf(.975))*mask, axis=1)/n
            mean = np.sum(z*mask, axis=1)/n
            vv = np.column_stack((mse, c95, mean, values[:, 3], n))
            ix = rng.integers(0, H, size=(B, H))
            w = np.zeros((B, H), int)
            np.add.at(w, (np.repeat(np.arange(B), H), ix.ravel()), 1)
            ci = np.percentile(statistics(vv, w), [5, 95], axis=0)
            hits += (ci[0] <= truth) & (truth <= ci[1])
            estimates.append(statistics(vv, np.ones(H))[0])
            passed.append(ci[0, 1] >= .93)
        controls[scenario] = {"true_values": dict(zip(NAMES, truth.tolist())),
                              "mean_estimates": dict(zip(NAMES, np.mean(estimates, axis=0).tolist())),
                              "ci90_coverage": dict(zip(NAMES, (hits/reps).tolist())),
                              "coverage_criterion_pass_fraction": float(np.mean(passed))}
    return {"label": "synthetic; conditional on corrected replication successful-host count and Tmag design",
            "replicates": reps, "bootstrap_per_replicate": B, "hosts": H,
            "mc_se_at_90_percent": math.sqrt(.9*.1/reps), "scenarios": controls}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bootstrap", type=int, default=10000)
    ap.add_argument("--control-reps", type=int, default=600)
    ap.add_argument("--control-bootstrap", type=int, default=600)
    args = ap.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    remeasured = read(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    old_hosts = {r["host"] for r in remeasured}
    old_pairs = {(r["host"], r["sector"]) for r in remeasured}
    paths = [ROOT / "results/outcomes/t015v3/outcomes.csv.gz"]
    output, byhost = {}, []
    for sample in ("dev", "confirm", "confirm2"):
        base = ROOT / "results/sprint2" / sample
        available = read(base / "ledger.csv.gz")
        paths.extend(base / name for name in ("ledger.csv.gz", "summary.json", "run_receipt.json"))
        timed = [r for r in available if r["status"] == "timed" and r["truth_id"]]
        chosen_historical = [r for r in choose(timed, available, historical=True) if r["mode"] == "remove"]
        chosen_correct = [r for r in choose(timed, available) if r["mode"] == "remove"]
        archive = json.loads((base / "summary.json").read_text())
        result = {"historical_points_max_rounding_difference": {}, "corrected": {}, "fallback_hosts": []}
        correct_ids = {r["host"] for r in chosen_correct}
        for host in sorted({r["host"] for r in chosen_historical} - correct_ids):
            rs = [r for r in chosen_historical if r["host"] == host]
            result["fallback_hosts"].append({"host": host, "events": len(rs), "z": [float(r["z"]) for r in rs]})
        result["unmultiplied_interval_ledger_disagreements"] = sum(
            ((-float(r["hi95_s"]) <= float(r["err_s"]) <= float(r["lo95_s"])) != (r["cover95"] == "True"))
            for r in timed)
        result["inverted_interval_event_disagreements_remove_spoc"] = sum(
            ((-float(r["lo95_s"]) <= float(r["err_s"]) <= float(r["hi95_s"])) != (r["cover95"] == "True"))
            for r in timed if r["mode"] == "remove" and r["product"] == "SPOC_120")
        for rule in ("t015v3c", "t015v3"):
            ids, vv = hosts(chosen_historical, rule, inverted=True)
            reconstructed = statistics(vv, np.ones(len(vv)))[0]
            archived = archive["groups"][f"{rule}|remove|production|all"]
            differences = [abs(reconstructed[j] - archived[name]) for j, name in enumerate(NAMES)]
            result["historical_points_max_rounding_difference"][rule] = float(max(differences))
            assert max(differences) <= .000051
            ids, vv = hosts(chosen_correct, rule)
            result["corrected"][rule] = summarise(vv, args.bootstrap, 20261107)
            if rule == "t015v3":
                for host, v in zip(ids, vv):
                    byhost.append(dict(zip(("mse", "coverage95", "mean_z", "tmag", "timed_injections"), v.tolist()),
                                       sample=sample, host=host, remeasured=host in old_hosts))
                result["exploratory_count_split"] = {
                    key: summarise(vv[keep], args.bootstrap, 20261107) for key, keep in
                    (("at_most_three_timed_injections", vv[:, 4] <= 3), ("at_least_four_timed_injections", vv[:, 4] >= 4))
                    if np.sum(keep) >= 3}
                if sample == "confirm2":
                    write_json("independent_negative_controls.json", controls(vv, args.control_reps, args.control_bootstrap))
        if (base / "selection.csv").exists():
            selected = [r for r in read(base / "selection.csv") if r["selection"] == "selected"]
            result["remeasurement_contact"] = {"selected_hosts": len(selected),
                "overlap_hosts": sum(r["host"] in old_hosts for r in selected),
                "overlap_host_sector": sum((r["host"], r["sector"]) in old_pairs for r in selected)}
        output[sample] = result
    with (DEST / "corrected_host_statistics.csv").open("w") as f:
        writer = csv.DictWriter(f, fieldnames=list(byhost[0]))
        writer.writeheader()
        writer.writerows(byhost)
    write_json("independent_statistics.json", output)
    write_json("analytic_margins.json", margins())
    paths += [ROOT / p for p in ("docs/sprint2_outcome_design.md", "docs/sprint2_replication_design.md",
                                "scripts/sprint2_analysis.py", "scripts/review_sprint2_statistics.py")]
    write_json("input_hashes.json", {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    print(json.dumps({sample: {rule: entry["statistical_criteria_pass"] for rule, entry in val["corrected"].items()}
                      for sample, val in output.items()}, indent=2))


if __name__ == "__main__":
    main()
