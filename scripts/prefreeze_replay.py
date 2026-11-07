# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Replay of the frozen confirmation injections with likelihood grids exported (D060 requirement 1).

Re-executes the same SPOC 120-s removal-mode injection runs of the confirmation
(`confirm`) and replication (`confirm2`) samples: same selected hosts, sectors
and files, same per-host seeds and injected truths, unchanged timing core
(sprint2_outcomes + t015_timing_pipeline; the only source change since 2c39f0a
is the t015v3a integration fail-closed label). The replay adds nothing to the
measurement: it captures each recovered window's chi-square grid, writes the
flat-prior posterior grid in the I1 format for every timed non-Gaussian truth,
and applies the shared support check (`acceptance.support_ok`, the adapter's own
`likelihood_grid`). Grids are regenerable and gitignored; their SHA-256 values
are kept in the ledger.

Identity check: every saved timed row must reproduce err_s, sigma_s and gauss_ok;
rows the frozen code timed with an integration flag must now be labelled
integration_unresolved. Development-era files only (both access guards).

    uv run scripts/prefreeze_replay.py --workers 8
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import sys
from collections import Counter
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import acceptance as A  # noqa: E402
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402

OUT = ROOT / "results" / "prefreeze" / "replay"
so.GRIDS = ROOT / "data" / "derived" / "prefreeze_replay" / "grids"
_CAPTURE: list = []
_time_windows, _inject_run = so.time_windows, so.inject_run


def _capturing_time_windows(*a, **k):
    rows = _time_windows(*a, **k)
    _CAPTURE.append(rows)
    return rows


def _replay_inject_run(t, f, e, exp_s, sol, per_cat, truths, mode, rng, base, cadence):
    _CAPTURE.clear()
    led, run = _inject_run(t, f, e, exp_s, sol, per_cat, truths, mode, rng, base, cadence)
    wins = {w["local_epoch"]: w for rows in _CAPTURE for w in rows}
    for r in led:
        if not r.get("truth_id") or r.get("status") != "timed" or r.get("gauss_ok"):
            continue
        w = wins[r["window_local_epoch"]]
        rel = so.write_grid("replay:" + r["truth_id"], w)
        r.update({"posterior_grid_path": rel, "grid_sha256": tp.sha256(ROOT / rel),
                  "support_ok": A.support_ok(rel)})
    return led, run


so.time_windows, so.inject_run = _capturing_time_windows, _replay_inject_run

SAMPLES = {"confirm": so.OUT / "confirm", "confirm2": so.OUT / "confirm2"}


def replay_host(host):
    h = {**host, "ffi_uri": "", "ffi_t_max_mjd": ""}
    return so.safe_process((h, ("remove",)))


def identity(saved, new):
    key = lambda r: r["truth_id"]  # noqa: E731
    s = {key(r): r for r in saved if r["product"] == A.PRODUCT and r["mode"] == "remove" and r.get("truth_id")}
    n = {key(r): r for r in new if r.get("truth_id")}
    out = Counter()
    worst = 0.0
    for k, a in s.items():
        b = n.get(k)
        if b is None:
            out["missing_in_replay"] += 1
            continue
        if a["status"] in ("timed", "edge") and A.INTEGRATION_FLAGS & set((a.get("flags") or "").split(";")):
            out["integration_relabelled" if b["status"] == "integration_unresolved" else "integration_mismatch"] += 1
            continue
        if a["status"] != b["status"]:
            out["status_mismatch"] += 1
            continue
        if a["status"] == "timed":
            d = max(abs(float(a["err_s"]) - float(b["err_s"])), abs(float(a["sigma_s"]) - float(b["sigma_s"])))
            worst = max(worst, d)
            same = d <= 0.002 and a["gauss_ok"] == str(b["gauss_ok"])
            out["timed_identical" if same else "timed_mismatch"] += 1
        else:
            out["status_identical"] += 1
    out["extra_in_replay"] = len(set(n) - set(s))
    return dict(out), worst


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--only", default="")
    ap.add_argument("--samples", default="confirm,confirm2")
    ap.add_argument("--receipt-only", action="store_true", help="recompute the receipt from saved replay ledgers")
    args = ap.parse_args()
    receipt = {"purpose": "D060 requirement 1: actual support outcomes on the frozen confirmation injections",
               "timing_source_sha256": hashlib.sha256((HERE / "sprint2_outcomes.py").read_bytes()
                                                      + (HERE / "t015_timing_pipeline.py").read_bytes()).hexdigest(),
               "acceptance_sha256": tp.sha256(HERE / "acceptance.py"),
               "replay_sha256": tp.sha256(Path(__file__)), "product": A.PRODUCT, "mode": "remove",
               "max_mjd_guard": tp.MAX_MJD, "max_btjd_guard": tp.MAX_BTJD, "samples": {}}
    for sample in args.samples.split(","):
        d = SAMPLES[sample]
        hosts = [r for r in csv.DictReader((d / "selection.csv").open())
                 if r.get("selection") == "selected" and r.get("spoc_uri")]
        if args.only:
            hosts = [h for h in hosts if h["host"] in args.only.split(",")]
        out = OUT / sample
        if args.receipt_only:
            ledger = list(csv.DictReader(gzip.open(out / "ledger.csv.gz", "rt")))
            for r in ledger:
                r["gauss_ok"] = r.get("gauss_ok") == "True"
                if r.get("support_ok") in ("True", "False"):
                    r["support_ok"] = r["support_ok"] == "True"
        else:
            with Pool(args.workers) as pool:
                res = pool.map(replay_host, hosts, chunksize=1)
            out.mkdir(parents=True, exist_ok=True)
            ledger = [r for x in res for r in x[2]]
            tp.write_csv(out / "products.csv", [r for x in res for r in x[0]])
            tp.write_csv(out / "runs.csv", [r for x in res for r in x[3]])
            keys = list(dict.fromkeys(k for r in ledger for k in r))
            with gzip.open(out / "ledger.csv.gz", "wt", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
                w.writeheader()
                w.writerows(ledger)
        saved = list(csv.DictReader(gzip.open(d / "ledger.csv.gz", "rt")))
        ident, worst = identity(saved, ledger)
        sup = Counter(str(r["support_ok"]) for r in ledger if r.get("support_ok") in (True, False))
        receipt["samples"][sample] = {"hosts": len(hosts), "ledger_rows": len(ledger),
                                      "identity": ident, "max_abs_timing_difference_s": worst,
                                      "nonGaussian_support": dict(sup),
                                      "ledger_sha256": tp.sha256(out / "ledger.csv.gz")}
        print(sample, json.dumps(receipt["samples"][sample]), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "replay_receipt.json").write_text(json.dumps(receipt, indent=1) + "\n")


if __name__ == "__main__":
    main()
