# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["numpy<2.4", "scipy", "astropy", "astroquery", "lightkurve==2.5.1", "batman-package",
#                 "setuptools", "tess-point==0.9.5.post1"]
# ///
"""Single replication confirmation of rule t015v3 (no Tmag multiplier); docs/sprint2_replication_design.md.

Uses the frozen timing code (sprint2_outcomes.py and t015_timing_pipeline.py at
2c39f0a) unchanged; this driver only selects hosts and calls it.

    uv run scripts/sprint2_confirm2.py select     # metadata only
    uv run scripts/sprint2_confirm2.py run        # after the replication design commit
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint2_outcomes as so  # noqa: E402
import t015_timing_pipeline as tp  # noqa: E402

OUT = so.OUT / "confirm2"
PER_STRATUM = 30


def select(args):
    rank = lambda s: hashlib.sha256(s.encode()).hexdigest()  # noqa: E731
    used = {r["host"] for r in csv.DictReader((so.OUT / "confirm" / "selection.csv").open()) if r["selection"] != "not_reached"}
    fr = list(csv.DictReader(so.SAMPLES["dev"].open()))
    out = []
    for stratum, _, _ in so.STRATA:
        pool = sorted((r for r in fr if r["frame"] == "in_frame" and r["stratum"] == stratum
                       and r["selection"] == "not_reached" and r["host"] not in used), key=lambda r: r["rank"])
        n = 0
        for r in pool:
            row = {k: r[k] for k in ("host", "planet", "tic", "tmag", "stratum", "period_d", "tess_point_sectors", "rank")}
            if n == PER_STRATUM:
                out.append({**row, "selection": "not_reached"})
                continue
            secs = [int(s) for s in r["tess_point_sectors"].split()]
            spoc = {x["sector"]: x for x in tp.search(r["tic"], secs, "SPOC", 120) if x["guard_ok"]}
            ffi = {x["sector"]: x for x in tp.search(r["tic"], secs, "TESS-SPOC", 200) if x["guard_ok"]}
            if not spoc and not ffi:
                out.append({**row, "selection": "no_qualified_product_passing_guard"})
                continue
            pool_secs = sorted(spoc) if spoc else sorted(ffi)
            sec = min(pool_secs, key=lambda s: rank(f"{so.SALT}:confirm2:{r['tic']}:{s}"))
            n += 1
            out.append({**row, "selection": "selected", "stratum_rank": n, "set": "confirmation2", "sector": sec,
                        "ffi_uri": ffi[sec]["uri"] if sec in ffi else "",
                        "ffi_t_max_mjd": ffi[sec]["t_max_mjd"] if sec in ffi else "",
                        "spoc_uri": spoc[sec]["uri"] if sec in spoc else "",
                        "spoc_t_max_mjd": spoc[sec]["t_max_mjd"] if sec in spoc else ""})
            print(stratum, n, r["host"], "S%d" % sec, flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    tp.write_csv(OUT / "selection.csv", out)


def run(args):
    hosts = [r for r in csv.DictReader((OUT / "selection.csv").open()) if r.get("selection") == "selected"]
    with Pool(args.workers) as pool:
        res = pool.map(so.safe_process, [(h, ("remove", "subtract")) for h in hosts], chunksize=1)
    for i, name in enumerate(("products", "real_transits", "ledger", "runs")):
        tp.write_csv(OUT / f"{name}.csv", [row for r in res for row in r[i]])
    (OUT / "run_receipt.json").write_text(json.dumps({"rule_version": so.rule_version(), "sample": "confirm2",
                                                      "hosts": len(hosts), "modes": ["remove", "subtract"],
                                                      "max_mjd_guard": tp.MAX_MJD, "max_btjd_guard": tp.MAX_BTJD},
                                                     indent=1) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("select").set_defaults(func=select)
    p = sub.add_parser("run")
    p.add_argument("--workers", type=int, default=8)
    p.set_defaults(func=run)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
