# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Identification controls with full window export, to judge product acceptance gates (D056 §2).

Same trials, seeds and frozen timing code as `sprint2_outcomes.py idtests`
(development hosts, real transits subtracted), but every recovered window is
written with its status, integration flags and match, and each trial records
the product shape-fit reduced chi-square. Development data only.

    uv run scripts/prefreeze_idtests.py
"""

from __future__ import annotations

import csv
import math
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402

OUT = ROOT / "results" / "prefreeze"


def host_trials(host):
    cat = so.drd_catalogue()
    pc = cat[host["planet"]].period_days
    rng = np.random.default_rng([so.SEED, 7, int(host["tic"].split()[-1])])
    key = "spoc" if host.get("spoc_uri") else "ffi"
    path = tp.download({"tic": host["tic"], "uri": host[f"{key}_uri"], "t_max_mjd": float(host[f"{key}_t_max_mjd"]),
                        "guard_ok": float(host[f"{key}_t_max_mjd"]) <= tp.MAX_MJD})
    t, f, e, cad, meta = tp.read(path, "pdcsap")
    exp_s, cadence = meta["exp_s"], float(np.median(np.diff(t)))
    sol = so.solution(t, f, e, exp_s, pc)
    if sol["id_fail"]:
        return [{"host": host["host"], "kind": "", "status": "real_id_failed"}]
    real_c = [sol["tref"] + k * sol["per"] for k in range(
        math.floor((t.min() - sol["tref"]) / sol["per"]) - 1, math.ceil((t.max() - sol["tref"]) / sol["per"]) + 2)]
    fb = f / so.model_train(t, real_c, sol["per"], sol["shape"], sol["half"], exp_s)
    trials = [("period_offset", d) for d in (-0.006, -0.004, -0.002, 0.0, 0.002, 0.004, 0.006)]
    trials += [("alias", a) for a in (0.5, 2.0, 3.0)] + [("ttv_offset_min", m) for m in (30, 50, 70, 90, 120)]
    out = []
    for kind, val in trials:
        ptrue = pc * (1 + val) if kind == "period_offset" else pc * val if kind == "alias" else sol["per"]
        for _ in range(50):
            ph = rng.uniform(0, 1)
            t0 = sol["tref"] + ph * sol["per"]
            if min(ph, 1 - ph) * sol["per"] > 2 * sol["half"] + 0.05:
                break
        ks = range(math.floor((t.min() - t0) / ptrue) - 1, math.ceil((t.max() - t0) / ptrue) + 2)
        truths = [t0 + k * ptrue for k in ks]
        shifted = [i % 3 == 1 for i in range(len(truths))] if kind == "ttv_offset_min" else [False] * len(truths)
        truths = [x + (val / 1440 if s else 0) for x, s in zip(truths, shifted)]
        keep = [t.min() - sol["half"] < x < t.max() + sol["half"] for x in truths]
        truths = [x for x, k in zip(truths, keep) if k]
        shifted = [s for s, k in zip(shifted, keep) if k]
        fi = fb * so.model_train(t, truths, ptrue, sol["shape"], sol["half"], exp_s)
        base = {"host": host["host"], "tmag": host["tmag"], "kind": kind, "value": val, "phase": round(ph, 4)}
        try:
            si = so.solution(t, fi, e, exp_s, pc)
        except Exception as exc:  # noqa: BLE001
            out.append({**base, "status": f"exception {exc!r}"[:150]})
            continue
        base.update({"id_fail": si["id_fail"], "id_snr": round(si["id"]["snr"], 2),
                     "shape_rchi2": round(si.get("rchi_shape", float("nan")), 3),
                     "shape_at_bound": ";".join(si.get("at_bound", []))})
        if si["id_fail"]:
            out.append({**base, "status": "id_failed"})
            continue
        rows = so.time_windows(t, fi, e, si, exp_s, cadence)
        match = so.assign(truths, si["wins"])
        inv = {j: i for i, (j, _) in match.items()}
        for i, x in enumerate(truths):
            obs = tp.coverage(t, x, si["half"], cadence) >= .75 and tp.coverage(t, x, si["t14"] / 2, cadence) >= .75
            if i not in match:
                out.append({**base, "status": "ok", "record": "truth", "truth_index": i, "shifted": shifted[i],
                            "observable": obs, "window_status": "not_recovered"})
        for j, w in enumerate(rows):
            i = inv.get(j)
            z = (w["tc"] - truths[i]) / w["sig"] if i is not None and "tc" in w else None
            out.append({**base, "status": "ok", "record": "window", "window_index": j,
                        "truth_index": "" if i is None else i, "shifted": "" if i is None else shifted[i],
                        "observable": "" if i is None else (tp.coverage(t, truths[i], si["half"], cadence) >= .75 and
                                                            tp.coverage(t, truths[i], si["t14"] / 2, cadence) >= .75),
                        "window_status": w["status"], "flags": w.get("flags", ""),
                        "z": "" if z is None else round(z, 4)})
    print(host["host"], "done", flush=True)
    return out


def main():
    hosts = [r for r in csv.DictReader(so.SAMPLES["dev"].open()) if r.get("selection") == "selected"]
    with Pool(8) as pool:
        res = pool.map(host_trials, hosts, chunksize=1)
    OUT.mkdir(parents=True, exist_ok=True)
    tp.write_csv(OUT / "identification_windows.csv", [r for x in res for r in x])
    import gzip, shutil
    with open(OUT / "identification_windows.csv", "rb") as a, gzip.open(OUT / "identification_windows.csv.gz", "wb") as b:
        shutil.copyfileobj(a, b)
    (OUT / "identification_windows.csv").unlink()


if __name__ == "__main__":
    main()
