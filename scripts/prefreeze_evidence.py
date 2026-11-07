"""Eight-criterion injection evidence for t015v3a under the shared acceptance contract (D058).

For each frozen confirmation sample, SPOC 120-s PDCSAP, removal mode:
the product gate uses the real product's shape fit and each injection run's
refit shape (a run is its own recovered train); event acceptance uses
scripts/acceptance.py. Injection ledgers did not export likelihood grids, so
non-Gaussian timings are bracketed: upper bound treats them as passing the
support check, lower bound excludes every one of them. All amended-A2
criteria (minimum hosts, z-RMS, coverage, mean z, both Tmag endpoints and
both noise ratios) are evaluated at B = 10,000 with the analysis seed.

    .venv/bin/python scripts/prefreeze_evidence.py
"""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import acceptance as A  # noqa: E402
import sprint2_analysis as sa  # noqa: E402

OUT = ROOT / "results" / "prefreeze"
SEED = 20261107


def run():
    res = {"rule": "t015v3a (scripts/acceptance.py)", "shape_rchi_max": A.SHAPE_RCHI_MAX, "bootstrap": 10000,
           "seed": SEED, "acceptance_source_sha256": hashlib.sha256((HERE / "acceptance.py").read_bytes()).hexdigest(),
           "samples": {}}
    for sample in ("confirm", "confirm2"):
        d = ROOT / "results" / "sprint2" / sample
        led = list(csv.DictReader(gzip.open(d / "ledger.csv.gz", "rt")))
        runs = {r["run_id"]: r for r in csv.DictReader((d / "runs.csv").open()) if r.get("run_id")}
        prods = {(r["host"], r.get("product")): r for r in csv.DictReader((d / "products.csv").open())}
        real = [r for r in csv.DictReader((d / "real_transits.csv").open())]
        states = Counter()
        upper, lower = [], []
        for r in led:
            if r["product"] != A.PRODUCT or r["mode"] != "remove" or not r.get("truth_id"):
                continue
            ps = A.product_state(prods.get((r["host"], r["product"])))
            if ps == "ok":
                rr = runs.get(r["run_id"], {})
                if rr.get("status", "").split(":")[0] != "ok":
                    ps = "run_" + (rr.get("status", "missing").split(":")[0] or "missing")
                else:
                    ps = A.product_state({"status": "ok", "shape_rchi2": rr.get("shape_rchi2")})
                    ps = "run_" + ps if ps != "ok" else ps
            st = ps if ps != "ok" else A.event_state(r, check_support=False)
            states[st] += 1
            if st == A.ACCEPTED:
                upper.append(r)
                lower.append(r)
            elif st == "likelihood_support_not_exported":
                upper.append(r)
        out = {"injection_states": dict(states.most_common())}
        for label, rows in (("upper_nonGaussian_pass", upper), ("lower_nonGaussian_fail", lower)):
            hs = sa.Hosts([float(r["z"]) for r in rows], [r["cover95"] == "True" for r in rows],
                          [r["host"] for r in rows], [float(r["tmag"]) for r in rows])
            s = sa.summarise(hs, 10000, np.random.default_rng(SEED))
            keys = {(r["host"], r["product"]) for r in rows}
            noise = sa.noise_control(rows, real, lambda r, k=keys: (r["host"], r.get("product")) in k)
            s["noise_control"] = noise
            s["verdict"] = sa.verdict(s, noise)
            out[label] = {k: s[k] for k in ("hosts", "events", "z_rms", "z_rms_ci90", "cover95", "cover95_ci90",
                                            "mean_z", "mean_z_ci90", "z_rms_tmag9_ci90", "z_rms_tmag13.5_ci90",
                                            "noise_control", "verdict")}
            print(sample, label, out[label]["hosts"], out[label]["events"], out[label]["z_rms_ci90"],
                  out[label]["cover95_ci90"], out[label]["verdict"]["pass"], flush=True)
        res["samples"][sample] = out
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "injection_evidence_t015v3a.json").write_text(json.dumps(res, indent=1, default=float) + "\n")


if __name__ == "__main__":
    run()
