# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "batman-package", "setuptools"]
# ///
"""Synthetic white-noise calibration of the t015 timing core (C022 reproducer).

120-s cadence over 27 d with a 1.2-d gap; P ~ U(2.5, 3.5) d; rp 0.1, a/R* 9,
i 88.5 deg; per-transit offsets U(+/-2 min). Gaussian noise of the stated
per-cadence SD; blind BLS, shape fit and timing as in t015_timing_pipeline.

    uv run scripts/sprint2_white_noise.py
"""

from __future__ import annotations

import json
import sys
from multiprocessing import Pool
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts")]
import t015_timing_pipeline as tp  # noqa: E402

SIGMAS = (1.5e-3, 4e-3, 8e-3)
TRIALS = 120


def trial(arg):
    sig, seed = arg
    rng = np.random.default_rng([20261107, seed, int(sig * 1e6)])
    cad = 120 / 86400
    t = np.arange(0, 27, cad)
    t = t[(t < 13) | (t > 14.2)]
    per = 3.0 + rng.uniform(-0.5, 0.5)
    shape = {"rp": 0.1, "a": 9.0, "inc": 88.5, "q1": 0.4, "q2": 0.3}
    t0 = rng.uniform(0, per)
    offs = rng.uniform(-2, 2, 40) / 1440
    truths = np.array([t0 + k * per + offs[k] for k in range(int(27 / per) + 1)])
    f = np.ones_like(t)
    for c in truths:
        m = np.abs(t - c) < 0.3
        if m.any():
            f[m] *= tp.Model(t[m], per, shape, 120)(c)
    f = f + rng.normal(0, sig, len(t))
    e = np.full_like(t, sig)
    sol = tp.sector_solution(t, f, e, 120.0)
    out = []
    for _, c in sol["wins"]:
        if tp.coverage(t, c, sol["half"], cad) < .75 or tp.coverage(t, c, sol["t14"] / 2, cad) < .75:
            continue
        r, rs, *_ = tp.timed(t, f, e, c, sol["per"], sol["shape"], sol["half"], 120.0, cad)
        tru = truths[np.argmin(np.abs(truths - rs["tc"]))]
        out.append(((rs["tc"] - tru) / rs["sig"], (r["tc"] - tru) / r["sig"], rs["sig"] * 86400))
    return out


def main():
    res = {}
    with Pool(8) as pool:
        for sig in SIGMAS:
            a = np.array([x for r in pool.map(trial, [(sig, s) for s in range(TRIALS)]) for x in r])
            res[f"{sig:g}"] = {"transits": len(a), "median_sigma_s": round(float(np.median(a[:, 2])), 1),
                               "mean_z": round(float(a[:, 0].mean()), 4),
                               "se_mean_z": round(float(a[:, 0].std() / np.sqrt(len(a))), 4),
                               "median_z": round(float(np.median(a[:, 0])), 4),
                               "z_rms_scaled": round(float(np.sqrt(np.mean(a[:, 0] ** 2))), 4),
                               "z_rms_white": round(float(np.sqrt(np.mean(a[:, 1] ** 2))), 4)}
            print(sig, res[f"{sig:g}"], flush=True)
    dest = ROOT / "results" / "sprint2_review" / "white_noise.json"
    dest.write_text(json.dumps({"trials_per_sigma": TRIALS, "results": res,
                                "source_sha256": __import__("hashlib").sha256(Path(__file__).read_bytes()).hexdigest()},
                               indent=1) + "\n")


if __name__ == "__main__":
    main()
