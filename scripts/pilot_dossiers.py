"""Pilot v1: metadata flow, forecast-outcome dossiers and one plot per planet.

Development material. Forecast = DRB as issued (OSF v1 file). Outcomes = TESS
mid-times dated 2022-01-01 onward in DRD `all_mid_time_data.txt`. Each pair
carries explicit eligibility codes; nothing missing is imputed.
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
sys.path.insert(0, str(ROOT / "scripts"))
from covariance_completeness import PREFIX, ZIP, read_sources  # noqa: E402
from reproduce_table5 import ISSUE, load  # noqa: E402
from transit_audit.exoclock import host_of, residuals_without_covariance  # noqa: E402

QUEUE = ["HAT-P-12b", "HAT-P-27b", "HD209458b", "WASP-52b", "WASP-69b", "WASP-74b",
         "WASP-80b", "WASP-43b", "Qatar-1b", "WASP-12b"]
MIN = 1440.0


def jd_to_year(jd):
    return 2000.0 + (np.asarray(jd) - 2451545.0) / 365.25


def date_to_year(d):
    y, m, dd = (int(x) for x in d.split("-"))
    return y + (m - 1) / 12 + (dd - 1) / 365.25


def drb_inputs(planet):
    with zipfile.ZipFile(ZIP) as z:
        return read_sources(io.TextIOWrapper(z.open(f"{PREFIX}{planet}.txt"), encoding="utf-8").read())


def pair_codes(rel, ev, flags):
    codes = []
    if ev.tess_date <= ISSUE[rel]["journal"]:
        codes.append("pre_journal_issue")
    if ev.tess_date <= ISSUE[rel]["arxiv_v1"]:
        codes.append("pre_arxiv_issue")
    if ev.planet in flags[rel]:
        codes.append("flagged_at_origin")
    codes += ["lineage_date_only", "outcome_prior_unverified", "time_standard_release_stated",
              "covariance_missing_wls_sensitivity", "source_date_basis_unverified"]
    return ";".join(codes)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--output", default=str(ROOT / "results" / "pilot_v1"))
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args(argv)
    out = Path(args.output)
    (out / "plots").mkdir(parents=True, exist_ok=True)
    eph, tess, flags = load()
    B, C, D = eph["DRB"], eph["DRC"], eph["DRD"]
    by_planet = {}
    for m in tess:
        by_planet.setdefault(m.planet, []).append(m)

    flow = []
    for p in sorted(B):
        evs = by_planet.get(p, [])
        post = [m for m in evs if m.tess_date > ISSUE["DRB"]["journal"]]
        stage = ("no_tess_2022plus_timing_in_DRD" if not evs else
                 "flagged_at_origin" if p in flags["DRB"] else
                 "only_pre_issue_events" if not post else "eligible_development")
        flow.append({"planet": p, "host": host_of(p), "in_DRC": p in C, "in_DRD": p in D,
                     "drb_flags": ";".join(B[p].flags), "drd_ttv_flag": p in flags["DRD"],
                     "tess_2022plus_events": len(evs), "post_journal_events": len(post),
                     "pilot_queue": p in QUEUE, "stage": stage})
    with (out / "inclusion_flow_drb.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(flow[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(flow)

    pairs, dossiers = [], []
    for p in QUEUE:
        evs = sorted(by_planet.get(p, []), key=lambda m: m.t_bjd_tdb)
        inputs = drb_inputs(p)
        e = B[p]
        d = {"planet": p, "host": host_of(p), "drb_t0_bjd_tdb": e.t0_bjd_tdb,
             "drb_sigma_t0_min": round(e.sigma_t0_days * MIN, 3), "drb_period_days": e.period_days,
             "drb_sigma_period_s": round(e.sigma_period_days * 86400, 4),
             "drb_flags": ";".join(e.flags) or "none", "drc_ttv_flag": p in flags["DRC"],
             "drd_ttv_flag": p in flags["DRD"], "drb_inputs": len(inputs),
             "drb_first_input": min(r[0] for r in inputs), "drb_last_input": max(r[0] for r in inputs),
             "drb_input_sources": ";".join(sorted({r[3] for r in inputs})),
             "tess_2022plus_events": len(evs)}
        if evs:
            n, oc, psd, sig = residuals_without_covariance(B, evs)
            z = oc / sig
            d.update({"first_event": evs[0].tess_date, "last_event": evs[-1].tess_date,
                      "epochs_from_t0": f"{int(n.min())}..{int(n.max())}",
                      "median_oc_min": round(float(np.median(oc)) * MIN, 2),
                      "median_pred_sd_min": round(float(np.median(psd)) * MIN, 2),
                      "median_meas_sd_min": round(float(np.median([m.sigma_days for m in evs])) * MIN, 2),
                      "max_abs_z": round(float(np.max(np.abs(z))), 2),
                      "frac_abs_z_lt_3": round(float(np.mean(np.abs(z) < 3)), 3)})
            for m, ni, o, ps, zi in zip(evs, n, oc, psd, z):
                pairs.append({"planet": p, "forecast": "DRB", "outcome_id": m.record_id,
                              "source_record_date": m.tess_date, "t_bjd_tdb": m.t_bjd_tdb,
                              "epoch_from_t0": int(ni), "oc_min": round(o * MIN, 3),
                              "pred_sd_min": round(ps * MIN, 3), "meas_sd_min": round(m.sigma_days * MIN, 3),
                              "z": round(zi, 3),
                              "source_date_days_after_journal": (np.datetime64(m.tess_date) - np.datetime64(ISSUE["DRB"]["journal"])).astype(int),
                              "source_date_days_after_last_input": (np.datetime64(m.tess_date) - np.datetime64(d["drb_last_input"])).astype(int),
                              "codes": pair_codes("DRB", m, flags)})
        dossiers.append(d)
        if not args.no_plots:
            plot(out / "plots" / f"{p}.png", p, e, C.get(p), D.get(p), inputs, evs, d)

    for name, rows in (("pilot_dossiers.csv", dossiers), ("pilot_pairs_drb.csv", pairs)):
        keys = list(dict.fromkeys(k for r in rows for k in r))
        with (out / name).open("w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=keys, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    from collections import Counter
    print(Counter(r["stage"] for r in flow))
    return 0


def plot(path, planet, e, c, d, inputs, evs, dossier):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(7.2, 4.0), dpi=130)
    t_in = np.array([r[1] for r in inputs])
    s_in = np.array([r[2] for r in inputs])
    n_in = np.round((t_in - e.t0_bjd_tdb) / e.period_days)
    oc_in = (t_in - (e.t0_bjd_tdb + n_in * e.period_days)) * MIN
    t_end = max([t_in.max()] + [m.t_bjd_tdb for m in evs]) + 200
    grid = np.linspace(t_in.min() - 100, t_end, 600)
    ng = (grid - e.t0_bjd_tdb) / e.period_days
    sd = np.sqrt(e.sigma_t0_days**2 + (ng * e.sigma_period_days) ** 2) * MIN
    yr = jd_to_year(grid)
    ax.fill_between(yr, -3 * sd, 3 * sd, color="#9ecae1", alpha=0.45, lw=0, label="DRB forecast ±3σ")
    ax.fill_between(yr, -sd, sd, color="#3182bd", alpha=0.45, lw=0, label="DRB forecast ±1σ")
    for other, lab, col in ((c, "DRC mean", "#e6550d"), (d, "DRD mean (in-sample)", "#756bb1")):
        if other is not None:
            m = (other.t0_bjd_tdb + np.round((grid - other.t0_bjd_tdb) / other.period_days) * other.period_days
                 - (e.t0_bjd_tdb + np.round((grid - e.t0_bjd_tdb) / e.period_days) * e.period_days))
            dt = (other.t0_bjd_tdb - e.t0_bjd_tdb) + (grid - e.t0_bjd_tdb) * (other.period_days - e.period_days) / e.period_days
            ax.plot(yr, (dt - np.round(dt / e.period_days) * e.period_days) * MIN, color=col, lw=1, ls="--", label=lab)
            del m
    ax.errorbar(jd_to_year(t_in), oc_in, s_in * MIN, fmt="o", ms=2.5, color="0.55", elinewidth=0.6,
                label=f"DRB inputs (n={len(inputs)})")
    if evs:
        t = np.array([m.t_bjd_tdb for m in evs])
        n = np.round((t - e.t0_bjd_tdb) / e.period_days)
        oc = (t - (e.t0_bjd_tdb + n * e.period_days)) * MIN
        ax.errorbar(jd_to_year(t), oc, np.array([m.sigma_days for m in evs]) * MIN, fmt="o", ms=3,
                    color="#d62728", elinewidth=0.7, label=f"TESS 2022+ outcomes (n={len(evs)})")
    for key, ls in (("training_end", ":"), ("journal", "-")):
        ax.axvline(date_to_year(ISSUE["DRB"][key]), color="k", lw=0.7, ls=ls)
    ax.axhline(0, color="k", lw=0.4)
    lim = 5 * max(np.max(np.abs(oc_in)) if len(oc_in) else 1, 1)
    if evs:
        lim = max(lim, 1.3 * float(np.max(np.abs(oc) + np.array([m.sigma_days for m in evs]) * MIN)))
    ax.set_ylim(-min(lim, 60), min(lim, 60))
    ax.set_xlabel("Year (from BJD_TDB)")
    ax.set_ylabel("O − C relative to DRB (min)")
    flags = dossier["drb_flags"]
    ax.set_title(f"{planet}: DRB as issued vs later TESS (development; DRB flags: {flags})", fontsize=9)
    ax.legend(fontsize=6.5, loc="upper left", ncol=2, frameon=False)
    ax.text(0.99, 0.02, "dotted: DRB input cutoff · solid: DRB journal issue (2022-02-09)",
            transform=ax.transAxes, ha="right", fontsize=6.5)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    raise SystemExit(main())
