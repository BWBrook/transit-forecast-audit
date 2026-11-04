"""T016: metadata-only inventory of the sealed TESS era for DRD planets.

Lists, for every DRD planet, the TESS sectors whose pointing covers it and whose
window ends after the sealing boundary (2025-11-18), and the number of transits
the DRD ephemeris *predicts* inside each window. No light curve, target-pixel
file, mid-time or other photometric product is requested or opened (D023).

Coordinates: NASA Exoplanet Archive (pscomppars, toi), fetched once into
data/raw/exoplanet_archive/ with SHA-256 recorded. Pointings: tess-point.
Sector windows are approximated as pointing midtime +/- 13.7 d because the
official orbit-times table (tess.mit.edu) failed TLS verification on this host;
every row carries `window_basis = midtime_pm_13.7d_approx`. FFI coverage only:
whether a planet also has 2-min/20-s cadence needs the per-sector target lists.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from transit_audit.exoclock import host_of, read_catalogue  # noqa: E402

RAW = ROOT / "data" / "raw" / "exoplanet_archive"
TAP = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
QUERIES = {
    "pscomppars.csv": "select pl_name,hostname,ra,dec,sy_tmag,tic_id from pscomppars",
    "toi.csv": "select toi,tid,ra,dec,st_tmag from toi",
}
JD_SEAL = 2460998.5          # 2025-11-19 00:00 UTC: first day of the sealed era
JD_STRICT_A = 2461083.5      # 2026-02-12 00:00 UTC: day after DRD journal publication (D023, D033)
HALF = 13.7


def jd_to_date(jd):
    return datetime.fromtimestamp((jd - 2440587.5) * 86400, tz=timezone.utc).strftime("%Y-%m-%d")


def fetch(today_jd):
    RAW.mkdir(parents=True, exist_ok=True)
    receipt = []
    for name, q in QUERIES.items():
        path = RAW / name
        if not path.exists():
            url = TAP + "?" + urllib.parse.urlencode({"query": q, "format": "csv"})
            path.write_bytes(urllib.request.urlopen(url, timeout=120).read())
            path.chmod(0o444)
        receipt.append({"file": str(path.relative_to(ROOT)), "query": q,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                        "retrieved_utc": datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).isoformat()})
    return receipt


def coordinates(planets):
    ps = list(csv.DictReader((RAW / "pscomppars.csv").open()))
    by_name = {r["pl_name"].replace(" ", ""): r for r in ps}
    by_host = {}
    for r in ps:
        by_host.setdefault(r["hostname"].replace(" ", ""), r)
    toi = {"TOI-" + r["toi"]: r for r in csv.DictReader((RAW / "toi.csv").open())}
    out = {}
    for p in planets:
        if p in by_name:
            r, basis = by_name[p], "pscomppars_name"
        elif p in toi:
            r, basis = toi[p], "toi_table"
        elif host_of(p) in by_host:
            r, basis = by_host[host_of(p)], "pscomppars_host"
        else:
            out[p] = None
            continue
        tic = r.get("tic_id") or ("TIC " + r["tid"] if r.get("tid") else "")
        out[p] = (float(r["ra"]), float(r["dec"]), tic, r.get("sy_tmag") or r.get("st_tmag") or "", basis)
    return out


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "sealed_inventory"))
    ap.add_argument("--today", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    args = ap.parse_args(argv)
    import tess_stars2px as tp

    today_jd = datetime.strptime(args.today, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp() / 86400 + 2440587.5
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    receipt = fetch(today_jd)
    D = read_catalogue(ROOT / "data" / "raw" / "osf" / "wpjtn" / "catalogue_of_ephemerides.txt")
    coords = coordinates(sorted(D))
    pointing = tp.TESS_Spacecraft_Pointing_Data()
    mid = {int(s): float(m) for s, m in zip(pointing.sectors, pointing.midtimes) if s < 1000}
    rows, unmatched = [], []
    for p in sorted(D):
        c = coords[p]
        if c is None:
            unmatched.append(p)
            continue
        ra, dec, tic, tmag, basis = c
        res = tp.tess_stars2px_function_entry(np.array([0]), np.array([ra]), np.array([dec]), trySector=None)
        e = D[p]
        for sec, cam, ccd in sorted({(int(s), int(cm), int(cd)) for s, cm, cd in zip(res[3], res[4], res[5]) if s in mid}):
            lo, hi = mid[sec] - HALF, mid[sec] + HALF
            if hi < JD_SEAL:
                continue
            n = np.arange(np.ceil((max(lo, JD_SEAL) - e.t0_bjd_tdb) / e.period_days),
                          np.floor((hi - e.t0_bjd_tdb) / e.period_days) + 1)
            status = "future" if lo > today_jd else ("in_progress" if hi > today_jd else "observed")
            rows.append({"planet": p, "host": host_of(p), "tic_id": tic, "tmag": tmag, "coord_basis": basis,
                         "sector": sec, "camera": cam, "ccd": ccd,
                         "window_start": jd_to_date(lo), "window_end": jd_to_date(hi),
                         "window_basis": "midtime_pm_13.7d_approx", "status_on_" + args.today: status,
                         "strict_track_a_window": lo >= JD_STRICT_A,
                         "predicted_transits_DRD": len(n),
                         "max_epochs_from_DRD_t0": int(np.max(np.abs(n))) if len(n) else "",
                         "DRD_pred_sd_min_at_window": round(float(np.sqrt(e.sigma_t0_days**2 + (np.max(np.abs(n)) * e.sigma_period_days)**2)) * 1440, 3) if len(n) else ""})
    with (out / "sealed_sector_inventory.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    status_key = "status_on_" + args.today
    obs = [r for r in rows if r[status_key] in ("observed", "in_progress")]
    summary = {
        "development_only_metadata": True, "light_curves_opened": 0,
        "today": args.today, "seal_start": jd_to_date(JD_SEAL), "strict_track_a_start": jd_to_date(JD_STRICT_A),
        "drd_planets": len(D), "unmatched_coordinates": unmatched,
        "sectors_considered": sorted({r["sector"] for r in rows}),
        "planet_sectors_total": len(rows),
        "planets_any_sealed_sector": len({r["planet"] for r in rows}),
        "planets_observed_by_today": len({r["planet"] for r in obs}),
        "hosts_observed_by_today": len({r["host"] for r in obs}),
        "predicted_transits_observed_by_today": int(sum(r["predicted_transits_DRD"] for r in obs)),
        "planets_observed_strict_A_window": len({r["planet"] for r in obs if r["strict_track_a_window"]}),
        "predicted_transits_strict_A_observed": int(sum(r["predicted_transits_DRD"] for r in obs if r["strict_track_a_window"])),
        "by_sector": {s: {"planets": sum(1 for r in rows if r["sector"] == s),
                          "window": [next(r["window_start"] for r in rows if r["sector"] == s),
                                     next(r["window_end"] for r in rows if r["sector"] == s)],
                          "status": next(r[status_key] for r in rows if r["sector"] == s)}
                      for s in sorted({r["sector"] for r in rows})},
        "sources": receipt,
        "tess_point_version": getattr(tp, "__version__", "0.9.5.post1"),
        "caveats": ["FFI pointing coverage only; cadence and data-gap losses not applied",
                    "sector windows approximate (midtime +/- 13.7 d)",
                    "predicted transit counts use DRD ephemeris; real usable counts will be lower"],
        "command": "uv run --extra analysis python scripts/sealed_era_inventory.py",
    }
    (out / "sealed_inventory_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k not in ("by_sector", "sources")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
