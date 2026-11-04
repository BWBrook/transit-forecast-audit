"""Covariance completeness for the DRB, DRC and DRD issued ephemerides.

Purpose: covariance completeness. DRB publishes T0, P and their marginal
uncertainties but not Cov(T0, P). If a weighted least-squares refit of the
released `data_sources` timings, with each planet's published uncertainty
scaling factor, reproduces the published T0/P/sigmas, then the implied
correlation at the published reference epoch is a reconstructed (tier-2)
covariance for the issued forecast, not a published one.

DRC and DRD publish neither scaling factors nor per-planet input lists, but
the correlation at the published epoch is invariant to a per-planet error
scale, so it is computed from each release's `all_mid_time_data.txt`. That
file is treated as the release's fitted input set (an assumption checked by
how closely the refit reproduces the published period).
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from transit_audit.ephemeris import fit_linear  # noqa: E402
from transit_audit.exoclock import read_catalogue, read_drb_ephemerides, read_mid_times  # noqa: E402

ZIP = ROOT / "data" / "raw" / "osf" / "wna5e" / "5_complete_ExoClock_DRB.zip"
PREFIX = "ExoClock_DRB/2_catalogue_of_ExoClock_ephemerides/data_sources/"


def read_sources(text: str):
    rows = []
    for line in text.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        rows.append((f[0].strip(), float(f[1]), float(f[2]), f[3].strip(), f[4].strip()))
    return rows


def scale_factors():
    out = {}
    for line in (ROOT / "data/raw/osf/wna5e/updated_ephemerides.txt").read_text().splitlines():
        if line.strip() and not line.startswith("#"):
            f = line.split("\t")
            out[f[0].strip()] = float(f[5])
    return out


def summarise_fit(release, planet, e, t, s, days, scale):
    n = np.round((t - e.t0_bjd_tdb) / e.period_days)
    fit = fit_linear(n, t, s)
    eph = fit.ephemeris
    sa, sp = np.sqrt(np.diag(eph.covariance_days2))
    delta = 0.0 - eph.reference_epoch
    t0_refit = eph.t_ref_bjd_tdb + delta * eph.period_days
    var_t0 = sa**2 + delta**2 * sp**2
    cov = delta * sp**2
    return {
        "release": release, "planet": planet, "n_timings": len(t),
        "same_day_duplicates": len(days) - len(set(days)) if days else "",
        "last_training_day": max(days) if days else "",
        "scale_factor": scale if scale is not None else "",
        "pivot_minus_published_epoch": round(eph.reference_epoch, 3),
        "t0_refit_minus_published_s": round((t0_refit - e.t0_bjd_tdb) * 86400, 2),
        "p_refit_minus_published_s": round((eph.period_days - e.period_days) * 86400, 5),
        "sigma_t0_refit_over_published": round(np.sqrt(var_t0) / e.sigma_t0_days, 3) if scale else "",
        "sigma_p_refit_over_published": round(sp / e.sigma_period_days, 3) if scale else "",
        "corr_t0_p_at_published_epoch": round(cov / np.sqrt(var_t0) / sp, 4),
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "pilot_v1" / "covariance_completeness.csv"))
    args = ap.parse_args(argv)
    pub = read_drb_ephemerides(ROOT / "data/raw/osf/wna5e/updated_ephemerides.txt")
    scale = scale_factors()
    out = []
    with zipfile.ZipFile(ZIP) as z:
        for name in sorted(z.namelist()):
            if not (name.startswith(PREFIX) and name.endswith(".txt")):
                continue
            planet = Path(name).stem
            e = pub[planet]
            rows = read_sources(io.TextIOWrapper(z.open(name), encoding="utf-8").read())
            t = np.array([r[1] for r in rows])
            s = np.array([r[2] for r in rows]) * scale[planet]
            out.append(summarise_fit("DRB", planet, e, t, s, [r[0] for r in rows], scale[planet]))
    for rel, node in (("DRC", "p298n"), ("DRD", "wpjtn")):
        cat = read_catalogue(ROOT / "data/raw/osf" / node / "catalogue_of_ephemerides.txt")
        mids = read_mid_times(ROOT / "data/raw/osf" / node / "all_mid_time_data.txt")
        by = {}
        for m in mids:
            by.setdefault(m.planet, []).append(m)
        for planet, e in sorted(cat.items()):
            ms = by.get(planet, [])
            if len(ms) < 3:
                continue
            t = np.array([m.t_bjd_tdb for m in ms])
            s = np.array([m.sigma_days for m in ms])
            out.append(summarise_fit(rel, planet, e, t, s, None, None))
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(out[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(out)
    for rel in ("DRB", "DRC", "DRD"):
        sub = [r for r in out if r["release"] == rel]
        print(f"{rel}: planets {len(sub)}  (quantiles 0, 5, 50, 95, 100%)")
        for k in ("t0_refit_minus_published_s", "p_refit_minus_published_s", "sigma_t0_refit_over_published",
                  "sigma_p_refit_over_published", "corr_t0_p_at_published_epoch", "pivot_minus_published_epoch"):
            vals = np.array([float(r[k]) for r in sub if r[k] != ""])
            if vals.size:
                q = np.quantile(vals, [0, 0.05, 0.5, 0.95, 1])
                print(f"  {k:34s}", " ".join(f"{x:10.4g}" for x in q))
        if rel == "DRB":
            print("  max last training day", max(r["last_training_day"] for r in sub))
            print("  planets with same-day duplicate timings", sum(r["same_day_duplicates"] > 0 for r in sub))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
