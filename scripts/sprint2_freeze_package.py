"""Candidate freeze package: metadata roster, DRD event manifest, draft forecasts, access receipt.

Nothing here opens protected photometry. The roster and event manifest come
from the sprint-1 metadata inventory (D045): rows with a public eligible
product, a strict-A opportunity after 2025-11-19 and no DRD origin-TTV flag.
Draft forecasts apply candidate development parameters to the issued DRD
ephemerides; they are not a frozen prediction.

    .venv/bin/python scripts/sprint2_freeze_package.py roster
    .venv/bin/python scripts/sprint2_freeze_package.py forecasts --parameters <json>
    .venv/bin/python scripts/sprint2_freeze_package.py receipt
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
from reproduce_table5 import load  # noqa: E402

OUT = ROOT / "results" / "sprint2" / "freeze_candidate"
INVENTORY = ROOT / "results" / "sprint1" / "inventory" / "planet_sector_product_inventory.csv"
STRICT_A_START_JD = 2460998.5  # 2025-11-19 00:00 UTC, D043
MAX_BTJD = 3313.5 - 0.01


def roster(args):
    eph, _, _ = load()
    drd = eph["DRD"]
    rows = [r for r in csv.DictReader(INVENTORY.open())
            if r["eligible_product_by_as_of"] == "True" and int(r["strict_a_opportunity_count"] or 0) > 0
            and r["drd_ttv_flag"] == "False" and r["cohort"] in ("core", "extension")]
    events, per_planet = [], defaultdict(lambda: {"opps_inventory": 0, "opps_manifest": 0, "sectors": set()})
    for r in rows:
        p = r["planet"]
        e = drd[p]
        jd = lambda d: (datetime.fromisoformat(d).toordinal() - datetime(1858, 11, 17).toordinal()) + 2400000.5  # noqa: E731
        lo = max(float(r["product_t_min_mjd"]) + 2400000.5, jd(r["conservative_start_utc"]), STRICT_A_START_JD)
        hi = min(float(r["product_t_max_mjd"]) + 2400000.5, jd(r["conservative_end_utc"]))
        n0, n1 = int(np.ceil((lo - e.t0_bjd_tdb) / e.period_days)), int(np.floor((hi - e.t0_bjd_tdb) / e.period_days))
        for n in range(n0, n1 + 1):
            events.append({"event_id": f"{p}|S{r['sector']}|DRD{n}", "observation_id": f"{p}|S{r['sector']}|DRD{n}",
                           "planet": p, "host": r["host"], "cohort": r["cohort"], "sector": r["sector"],
                           "product_obs_id": r["product_obs_id"], "forecast_epoch": n,
                           "drd_predicted_bjd_tdb": round(e.t0_bjd_tdb + n * e.period_days, 6),
                           "epoch_basis": "DRD ephemeris inside product interval, sector interior (1-day margins) and strict-A start"})
        d = per_planet[p]
        d.update({"planet": p, "host": r["host"], "tic": r["tic"], "tmag": r["tmag"], "cohort": r["cohort"],
                  "period_d": r["period_days"]})
        d["opps_inventory"] += int(r["strict_a_opportunity_count"])
        d["opps_manifest"] += max(n1 - n0 + 1, 0)
        d["sectors"].add(r["sector"])
    OUT.mkdir(parents=True, exist_ok=True)
    ro = [{**{k: v for k, v in d.items() if k != "sectors"}, "sectors": " ".join(sorted(d["sectors"], key=int))}
          for d in per_planet.values()]
    ro.sort(key=lambda r: r["planet"])
    write(OUT / "roster.csv", ro)
    write(OUT / "events_drd.csv", events)
    summary = {"planets": len(ro), "hosts": len({r["host"] for r in ro}),
               "core": sum(r["cohort"] == "core" for r in ro), "extension": sum(r["cohort"] == "extension" for r in ro),
               "opportunities_inventory": sum(r["opps_inventory"] for r in ro), "events_manifest": len(events),
               "inventory_sha256": sha(INVENTORY), "strict_a_start_jd": STRICT_A_START_JD,
               "note": "Same window as the sprint-1 inventory: product MJD bounds and official sector dates less one day, "
                       "no UTC-BJD conversion (<= ~9 min)."}
    (OUT / "roster_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(summary)


def forecasts(args):
    py = str(ROOT / ".venv/bin/python")
    dest = OUT / "forecasts_drd_draft.csv"
    subprocess.run([py, str(HERE / "sprint1_forecasts.py"), "make_forecasts", "--events", str(OUT / "events_drd.csv"),
                    "--parameters", args.parameters, "--release", "DRD", "--output", str(dest)], check=True)
    print(dest, sha(dest))


def fits_header_cards(path, hdus=2):
    cards, out = {}, []
    with open(path, "rb") as fh:
        for _ in range(hdus):
            hdr = {}
            while True:
                block = fh.read(2880)
                if len(block) < 2880:
                    return out
                for i in range(0, 2880, 80):
                    card = block[i:i + 80].decode("ascii", "replace")
                    key = card[:8].strip()
                    if key == "END":
                        break
                    if card[8:10] == "= ":
                        hdr[key] = card[10:].split("/")[0].strip().strip("'").strip()
                else:
                    continue
                break
            out.append(hdr)
            naxis = int(hdr.get("NAXIS", 0))
            size = 0
            if naxis:
                size = abs(int(hdr.get("BITPIX", 8))) // 8 * int(np.prod([int(hdr[f"NAXIS{k}"]) for k in range(1, naxis + 1)]))
                size *= 1
                size += int(hdr.get("PCOUNT", 0))
            fh.seek(((size + 2879) // 2880) * 2880, 1)
    return out


def receipt(args):
    files = sorted((ROOT / "data" / "raw" / "mast").rglob("*.fits"))
    rows, bad = [], []
    for f in files:
        h = fits_header_cards(f)
        sec = int(h[0].get("SECTOR", -1)) if h else -1
        tstop = float(h[1].get("TSTOP", "nan")) if len(h) > 1 else float("nan")
        m = re.search(r"s00(\d\d)", f.name)
        rows.append({"file": f.name, "sector_header": sec, "sector_name": int(m.group(1)) if m else -1, "tstop_btjd": tstop})
        if not (46 <= sec <= 73) or not tstop <= MAX_BTJD:
            bad.append(f.name)
    out = {"utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "fits_files": len(files),
           "sector_range": [min(r["sector_header"] for r in rows), max(r["sector_header"] for r in rows)] if rows else None,
           "max_tstop_btjd": max(r["tstop_btjd"] for r in rows) if rows else None, "tstop_limit_btjd": MAX_BTJD,
           "files_violating_guard": bad, "protected_outcomes_accessed": bool(bad),
           "method": "Header-only scan of every FITS file under data/raw/mast (primary SECTOR, extension TSTOP); "
                     "no data units read.",
           "listing_sha256": hashlib.sha256("\n".join(f"{r['file']},{r['sector_header']},{r['tstop_btjd']}"
                                                       for r in rows).encode()).hexdigest()}
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "access_receipt.json").write_text(json.dumps(out, indent=1) + "\n")
    print({k: v for k, v in out.items() if k != "files_violating_guard"}, "violations", len(bad))


def write(path, rows):
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=keys, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("roster").set_defaults(func=roster)
    p = sub.add_parser("forecasts")
    p.add_argument("--parameters", required=True)
    p.set_defaults(func=forecasts)
    sub.add_parser("receipt").set_defaults(func=receipt)
    args = ap.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
