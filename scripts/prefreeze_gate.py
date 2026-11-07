"""Evaluate the candidate product/train acceptance gate (D056 §2) on saved development evidence.

Gate (candidate, not installed): per recovered train (one product, one run or one
real light curve), count coverage-qualified recovered windows, including
spurious/unmatched windows and edge or integration-unresolved failures. Accept
if timed windows without integration flags are a strict majority; zero covered
windows fails. Where a window's status or flags were not exported, the state is
"unresolved" unless the bound settles it. No forecast residual or injection
truth enters the decision.

    .venv/bin/python scripts/prefreeze_gate.py
"""

from __future__ import annotations

import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "prefreeze"
INTEG = {"mass_outside_fine", "coarse_fine_shift"}


def rows(path):
    p = Path(path)
    with (gzip.open(p, "rt") if p.suffix == ".gz" else p.open()) as fh:
        return list(csv.DictReader(fh))


def flagged(r):
    return bool(INTEG & set((r.get("flags") or "").split(";")))


def gate(known_timed, covered_known, unknown_timed=0, unknown_untimed=0):
    """Three-valued strict-majority decision with bounds over unexported windows."""
    lo_n = covered_known + unknown_timed
    best = (known_timed + unknown_timed) / max(lo_n, 1) if lo_n else 0
    worst_n = covered_known + unknown_timed + unknown_untimed
    worst = known_timed / worst_n if worst_n else 0
    if lo_n == 0 and unknown_untimed == 0:
        return "fail"
    if worst > 0.5:
        return "pass"
    if best <= 0.5 and unknown_timed == 0:
        return "fail"
    return "unresolved"


def injection_ledgers():
    out = {}
    for sample in ("dev", "confirm", "confirm2"):
        led = rows(ROOT / f"results/sprint2/{sample}/ledger.csv.gz")
        runs = defaultdict(list)
        for r in led:
            if r["product"] == "SPOC_120" and r["mode"] == "remove" and r.get("run_id"):
                runs[r["run_id"]].append(r)
        states, wrong, rec_before, rec_after = Counter(), Counter(), defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0])
        for run, rs in runs.items():
            cov = [r for r in rs if r.get("window_centre_btjd") and
                   r["status"].removeprefix("spurious_window:") in ("timed", "edge")]
            known = sum(1 for r in cov if r.get("truth_id") and r["status"] == "timed" and not flagged(r))
            spur_timed = sum(1 for r in cov if not r.get("truth_id") and r["status"].endswith("timed"))
            covered_known = sum(1 for r in cov if r.get("truth_id") or not r["status"].endswith("timed"))
            st = gate(known, covered_known, unknown_timed=spur_timed)
            states[st] += 1
            obs = [r for r in rs if r.get("truth_id") and r.get("observable") == "True"]
            ok = sum(r["status"] == "timed" and not flagged(r) for r in obs)
            is_wrong = bool(obs) and 2 * ok < len(obs) and spur_timed > 0
            if is_wrong:
                wrong[st] += 1
            host = rs[0]["host"]
            rec_before[host][0] += ok
            rec_before[host][1] += len(obs)
            rec_after[host][0] += ok if st == "pass" else 0
            rec_after[host][1] += len(obs)
        eq = lambda d: float(np.mean([a / b for a, b in d.values() if b]))  # noqa: E731
        out[sample] = {"spoc_remove_runs": len(runs), "gate_states": dict(states),
                       "wrong_train_runs_by_gate_state": dict(wrong),
                       "equal_host_recovery_before": round(eq(rec_before), 4),
                       "equal_host_recovery_after_pass_only": round(eq(rec_after), 4)}
    return out


def identification_controls():
    t = [r for r in rows(ROOT / "results/sprint2/dev/identification_tests.csv") if r["kind"]]
    trials = defaultdict(list)
    for r in t:
        trials[(r["host"], r["kind"], r["value"])].append(r)
    out = defaultdict(lambda: Counter())
    for (host, kind, value), rs in trials.items():
        r0 = rs[0]
        key = f"{kind}={value}"
        if r0["status"] != "ok":
            out[key]["id_failed_or_exception"] += 1
            continue
        ev = [r for r in rs if r.get("event_status")]
        matched_cov = [r for r in ev if r["event_status"] in ("timed", "edge")]
        known = sum(r["event_status"] == "timed" for r in matched_cov)
        spur_timed = int(r0.get("spurious_timed_windows") or 0)
        st = gate(known, len(matched_cov), unknown_timed=spur_timed, unknown_untimed=0)
        obs = [r for r in ev if r["observable"] == "True" and (kind != "ttv_offset_min" or r["shifted"] == "False")]
        correct = bool(obs) and 2 * sum(r["event_status"] == "timed" for r in obs) >= len(obs)
        out[key][f"{'correct' if correct else 'wrong'}_train|{st}"] += 1
        if kind == "ttv_offset_min":
            sh = [r for r in ev if r["shifted"] == "True" and r["observable"] == "True"]
            out[key]["shifted_events_timed_when_pass"] += sum(r["event_status"] == "timed" for r in sh) if st == "pass" else 0
            out[key]["shifted_events_observable"] += len(sh)
    return {k: dict(v) for k, v in sorted(out.items())}


def identification_controls_full():
    """Both gates on the full-export identification controls (scripts/prefreeze_idtests.py)."""
    path = OUT / "identification_windows.csv.gz"
    if not path.exists():
        return None
    t = [r for r in rows(path) if r.get("kind")]
    trials = defaultdict(list)
    for r in t:
        trials[(r["host"], r["kind"], r["value"])].append(r)
    out = defaultdict(Counter)
    for (host, kind, value), rs in trials.items():
        key = f"{kind}={value}"
        r0 = rs[0]
        if r0["status"] != "ok":
            out[key]["id_failed_or_exception"] += 1
            continue
        win = [r for r in rs if r.get("record") == "window"]
        cov = [r for r in win if r["window_status"] in ("timed", "edge")]
        timed = sum(1 for r in cov if r["window_status"] == "timed" and not flagged(r))
        maj = gate(timed, len(cov))
        shp = "pass" if r0.get("shape_rchi2") and float(r0["shape_rchi2"]) <= 10 else "fail"
        obs = [r for r in rs if r.get("observable") == "True" and (kind != "ttv_offset_min" or r.get("shifted") == "False")]
        ok = sum(1 for r in obs if r.get("record") == "window" and r["window_status"] == "timed")
        correct = bool(obs) and 2 * ok >= len(obs)
        spurious_timed = sum(1 for r in win if r["truth_index"] == "" and r["window_status"] == "timed")
        tag = "correct" if correct else "wrong"
        out[key][f"{tag}|majority_{maj}"] += 1
        out[key][f"{tag}|shape_{shp}"] += 1
        out[key][f"{tag}|both_pass"] += maj == "pass" and shp == "pass"
        out[key]["spurious_timed_windows_accepted_by_both"] += spurious_timed if (maj == "pass" and shp == "pass") else 0
        bad = [abs(float(r["z"])) for r in win if r.get("z") not in ("", None) and r["window_status"] == "timed"]
        out[key]["matched_timed_abs_z_gt5_accepted_by_both"] += sum(z > 5 for z in bad) if (maj == "pass" and shp == "pass") else 0
    return {k: dict(v) for k, v in sorted(out.items())}


def real_products():
    o = rows(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    by = defaultdict(list)
    for r in o:
        if r["product"] == "SPOC_120":
            by[r["shape_group_id"]].append(r)
    res, rejected = Counter(), []
    for g, rs in by.items():
        cov = [r for r in rs if r["status"] in ("timed", "edge")]
        known = sum(r["status"] == "timed" and not flagged(r) for r in cov)
        if not cov and all(r["status"] == "id_failed" for r in rs):
            res["product_id_failed"] += 1
            continue
        st = gate(known, len(cov))
        res[st] += 1
        if st != "pass":
            timed = [r for r in cov if r["status"] == "timed"]
            ec = [abs(float(r["exoclock_delta_s"])) / np.hypot(float(r["sigma_s"]), float(r["exoclock_sigma_s"]))
                  for r in timed if r.get("exoclock_delta_s")]
            rejected.append({"product": g, "covered_windows": len(cov), "timed_unflagged": known,
                             "timed_rows_lost": len(timed), "exoclock_matched": len(ec),
                             "exoclock_max_abs_z": round(max(ec), 2) if ec else None})
    return {"spoc_products": sum(res.values()), "gate_states": dict(res),
            "timed_events_in_rejected_products": sum(x["timed_rows_lost"] for x in rejected),
            "rejected_products": sorted(rejected, key=lambda x: x["product"])}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    res = {"definition": __doc__.split("\n\n")[1].replace("\n", " "),
           "injection_ledgers": injection_ledgers(), "identification_controls": identification_controls(),
           "identification_controls_full_export": identification_controls_full(),
           "real_development_products": real_products(), "adopted_as_production_rule": False}
    (OUT / "gate_evaluation.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "definition"}, indent=1)[:6000])


if __name__ == "__main__":
    main()
