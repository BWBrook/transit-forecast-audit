"""Read-only D055 checks from saved development ledgers; no photometry access."""
import ast
import csv
import hashlib
import json
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint2_analysis as analysis
import sprint2_outcomes as outcomes
import t015_timing_pipeline as timing

OUT = ROOT / "results/sprint2_review/reconciliation_20261107"
BAD = {"mass_outside_fine", "coarse_fine_shift"}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flagged(row):
    return bool(set(row.get("flags", "").split(";")) & BAD)


def summarise(rows):
    hosts = analysis.Hosts([float(r["z"]) for r in rows],
        [analysis.interval_covers(float(r["err_s"]), float(r["lo95_s"]), float(r["hi95_s"])) for r in rows],
        [r["host"] for r in rows], [float(r["tmag"]) for r in rows])
    result = analysis.summarise(hosts, 10000, np.random.default_rng(7151))
    result["calibration_checks_only"] = analysis.verdict(result)
    result["noise_controls_recomputed"] = False
    return result


def majority_diagnostic(ledger, accepted):
    runs = defaultdict(list)
    for row in ledger:
        if row["product"] == "SPOC_120" and row["mode"] == "remove":
            runs[row["run_id"]].append(row)
    decisions, uncertain, rejected_positive = {}, [], []
    for run, rows in runs.items():
        covered = [r for r in rows if r.get("window_centre_btjd") and
                   r["status"].removeprefix("spurious_window:") in ("timed", "edge", "integration_unresolved")]
        known, unknown = 0, 0
        for row in covered:
            if row["status"].removeprefix("spurious_window:") != "timed":
                continue
            if not row.get("truth_id"):
                unknown += 1
            elif not flagged(row):
                known += 1
        n = len(covered)
        state = "pass" if n and 2*known > n else "fail" if 2*(known+unknown) <= n else "unresolved_spurious_flags"
        decisions[run] = state
        if state == "unresolved_spurious_flags":
            uncertain.append({"run_id":run, "covered_windows":n, "known_timed":known, "unrecorded_spurious_flags":unknown})
        retained = [r for r in accepted if r["run_id"] == run]
        if state == "fail" and retained:
            rejected_positive.append({"run_id":run,"covered_windows":n,"known_timed":known,"matched_timings_removed":len(retained)})
    result = [r for r in accepted if decisions[r["run_id"]] == "pass"]
    return {"definition":"Diagnostic only: strict majority of coverage-qualified recovered windows, per train/run, after integration flags; zero windows fail; spurious flags missing gives bounds.",
            "run_states":dict(Counter(decisions.values())),"positive_yield_rejections":rejected_positive,
            "unresolved_runs":uncertain,"additional_matched_timings_removed":len(accepted)-len(result),
            "retained_calibration":summarise(result),"adopted_as_production_rule":False}


def wrapper_identity():
    source = subprocess.check_output(["git","show","2c39f0a:scripts/sprint2_outcomes.py"], cwd=ROOT, text=True)
    function = next(node for node in ast.parse(source).body if isinstance(node,ast.FunctionDef) and node.name == "time_windows")
    namespace = {"np":np,"tp":timing}
    exec(compile(ast.Module(body=[function],type_ignores=[]),"frozen_time_windows","exec"),namespace)
    t = np.linspace(-.14,.14,29)
    sol = {"wins":[(0,0.)],"half":.15,"t14":.05,"per":3.,"shape":{}}
    checked = 0
    for asymmetric in (False,True):
        q = np.array([-2,-1,0,1,2,-1.959964,1.959964],float)/86400
        if asymmetric:
            q[[0,4,5,6]] *= [1.4,1.5,1.4,1.5]
        r = {"tc":0.,"q":q,"sig":1/86400,"n":len(t),"resid":np.zeros(len(t)),"grid":np.linspace(-10,10,21)/86400,
             "chi":np.linspace(-10,10,21)**2,"edge_mass":0.,"mass_outside_fine":0.,"coarse_shift_sig":0.,"fine_step_s":1.,"mask":np.ones(len(t),bool)}
        for cadences in (None,np.arange(len(t))):
            args = (t,np.ones(len(t)),np.ones(len(t)),sol,120,.01)
            with patch.object(timing,"timed",return_value=(r,r,1.,1.,1.)):
                old = namespace["time_windows"](*args,cad=cadences)[0]
                new = outcomes.time_windows(*args,cad=cadences)[0]
            for key,value in old.items():
                if isinstance(value,np.ndarray):
                    assert value.dtype == new[key].dtype and value.tobytes() == new[key].tobytes(),key
                else:
                    assert value == new[key],key
            checked += 1
    frozen_core = subprocess.check_output(["git","show","2c39f0a:scripts/t015_timing_pipeline.py"],cwd=ROOT)
    assert frozen_core == (ROOT/"scripts/t015_timing_pipeline.py").read_bytes()
    return {"synthetic_unflagged_wrapper_cases":checked,"legacy_fields_identical":True,"timing_core_matches_frozen_bytes":True,
            "scope":"Synthetic Gaussian/asymmetric status-wrapper comparison plus unchanged core source; no replay of real photometry or fresh independent qualification."}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paths = [ROOT/"scripts"/name for name in ("sprint2_analysis.py","sprint2_outcomes.py","t015_timing_pipeline.py","sprint2_white_noise.py","check_d055_evidence.py")]
    result = {"photometry_opened":False,"new_samples":0,"wrapper_identity":wrapper_identity(),"samples":{},
              "bootstrap":10000,"seed":7151,"numpy":np.__version__,"python":sys.version.split()[0]}
    for sample in ("confirm","confirm2"):
        ledger,*_ = analysis.load(sample)
        path = ROOT/f"results/sprint2/{sample}/ledger.csv"
        if not path.exists():
            path = path.with_suffix(".csv.gz")
        paths.append(path)
        timed = [r for r in ledger if r["product"] == "SPOC_120" and r["mode"] == "remove" and r["status"] == "timed" and r.get("truth_id")]
        retained = [r for r in timed if not flagged(r)]
        result["samples"][sample] = {"product":"SPOC_120 only; no FFI fallback","original_timed":len(timed),
            "integration_flags_removed":len(timed)-len(retained),"after_integration_filter":summarise(retained),
            "majority_diagnostic":majority_diagnostic(ledger,retained)}
    noise = json.loads((ROOT/"results/sprint2_review/white_noise.json").read_text())
    paths.append(ROOT/"results/sprint2_review/white_noise.json")
    assert noise["source_sha256"] == digest(ROOT/"scripts/sprint2_white_noise.py")
    result["white_noise"] = {"source_hash_verified":True,"event_naive_mean_z_over_se":{
        k:v["mean_z"]/v["se_mean_z"] for k,v in noise["results"].items()},
        "scope":"A new reproducible synthetic core diagnostic, not recovery of the missing earlier run or proof of absent bias; shared shapes are not accounted for by event-naive SE."}
    result["input_sha256"] = {str(p.relative_to(ROOT)):digest(p) for p in paths}
    (OUT/"evidence_check.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({sample:{"timed":s["after_integration_filter"]["events"],"z_rms":s["after_integration_filter"]["z_rms"],
        "majority_extra_removed":s["majority_diagnostic"]["additional_matched_timings_removed"]} for sample,s in result["samples"].items()}))


if __name__ == "__main__":
    main()
