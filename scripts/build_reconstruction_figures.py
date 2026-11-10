"""Build main-text Figures 1-4 for the reconstruction draft.

Run from the repository root: .venv/bin/python scripts/build_reconstruction_figures.py
Reads saved tables only (no photometry or FITS headers); writes PNGs and a receipt
to results/reconstruction_displays/.
"""
import csv
import datetime as dt
import gzip
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results/reconstruction_displays"
PRIM = ROOT / "data/derived/revision_stage0/benchmark/primary"
IN = {
    "pit_events": OUT / "pit_events.csv",
    "accepted_outcomes": PRIM / "accepted_outcomes.csv",
    "accepted_forecasts": PRIM / "accepted_forecasts.csv",
    "intended_forecasts": PRIM / "intended_forecasts.csv.gz",
    "terminal_ledger": PRIM / "terminal_ledger.csv.gz",
    "c2_events": ROOT / "results/t020_development/longer_horizon/c2_pooled_candidate_events.csv.gz",
    "coverage": ROOT / "results/revision_stage0/interpretability/coverage_vs_nominal.csv",
    "hr858_summary": ROOT / "results/independent_validation/hr858/summary.json",
    "release_planets": ROOT / "results/information_ledger/release_planets.csv",
    "released_timings": ROOT / "data/raw/osf/wpjtn/all_mid_time_data.txt",
}

BLUE, ORANGE, VERM, SKY, GREEN, GREY, DARK = (
    "#0072B2", "#E69F00", "#D55E00", "#56B4E9", "#009E73", "#8a8a8a", "#222222")
plt.rcParams.update({
    "font.size": 8, "axes.labelsize": 8.5, "axes.titlesize": 9, "legend.fontsize": 7.5,
    "xtick.labelsize": 7.5, "ytick.labelsize": 7.5, "axes.spines.top": False,
    "axes.spines.right": False, "axes.linewidth": 0.7, "figure.dpi": 100,
    "savefig.dpi": 200, "axes.grid": False, "figure.facecolor": "white",
})
receipt = {"inputs_sha256": {}, "numbers": {}}
N = receipt["numbers"]


def rows(path):
    op = gzip.open if str(path).endswith(".gz") else open
    with op(path, "rt", newline="") as f:
        return list(csv.DictReader(f))


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def panel(ax, letter, x=-0.02, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=10, fontweight="bold",
            ha="right", va="bottom")


def save(fig, name):
    p = OUT / name
    fig.savefig(p, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    assert p.stat().st_size < 1_000_000, name


def jd_to_date(jd):
    return dt.datetime(1858, 11, 17) + dt.timedelta(days=float(jd) - 2400000.5)


for k, p in IN.items():
    if p.exists():
        receipt["inputs_sha256"][k] = sha(p)
    else:
        receipt["inputs_sha256"][k] = "MISSING"

# ---------------------------------------------------------------- data
pit = rows(IN["pit_events"])
planet = np.array([r["planet"] for r in pit])
abs_err = np.array([float(r["abs_error_min"]) for r in pit])
w = np.array([float(r["planet_weight"]) for r in pit])
pit0 = np.array([float(r["pit_M0"]) for r in pit])
pit2 = np.array([float(r["pit_M2"]) for r in pit])
eid = [r["event_id"] for r in pit]

out = {r["event_id"]: r for r in rows(IN["accepted_outcomes"])}
fc = {r["event_id"]: r for r in rows(IN["accepted_forecasts"])}
chk = np.array([abs(float(out[e]["tc_bjd_tdb"]) - float(fc[e]["predicted_bjd_tdb"])) * 1440 for e in eid])
assert len(eid) == 2185 and np.allclose(chk, abs_err, rtol=1e-6, atol=1e-6)

n_events = len(abs_err)
planets = sorted(set(planet))
cnt = {p: int((planet == p).sum()) for p in planets}
pmax = {p: float(abs_err[planet == p].max()) for p in planets}
assert len(planets) == 151
pooled_med = float(np.median(abs_err))
eq_med = float(np.median([np.median(abs_err[planet == p]) for p in planets]))
# planet-balanced median of events (planet-weighted)
order = np.argsort(abs_err)
cw = np.cumsum(w[order]) / w.sum()
wmed = float(abs_err[order][np.searchsorted(cw, 0.5)])
non_hr = {p: v for p, v in pmax.items() if p != "HR858b"}
n_le = sum(v <= 26.4 for v in pmax.values())
N["fig2"] = {"events": n_events, "planets": len(planets), "pooled_median_min": pooled_med,
             "median_of_planet_medians_min": eq_med, "planet_weighted_event_median_min": wmed,
             "planets_max_le_26.4min": int(n_le), "max_excluding_HR858b_min": max(non_hr.values()),
             "HR858b_max_min": pmax["HR858b"], "HR858b_accepted_events": cnt["HR858b"],
             "accepted_count_range": [min(cnt.values()), max(cnt.values())],
             "min_abs_error_min": float(abs_err.min())}
assert n_le == 150 and abs(pooled_med - 1.1148) < 1e-3

# ================================================================ Fig 1
fig = plt.figure(figsize=(7.2, 5.6))
gs = fig.add_gridspec(2, 1, height_ratios=[1.0, 1.0], hspace=0.38)
ax = fig.add_subplot(gs[0])
fh, mh_, mc, mu = 10.0, 8.0, 4.0, 0.0  # forecast half-width, meas half-width, meas centre
ch = float(np.hypot(fh, mh_) * 1.0)    # illustrative convolution of two Gaussians (95% halves add in quadrature)
win = 150.0
ys = {"win": 3.0, "conv": 2.0, "fc": 1.0, "meas": 0.0}
ax.add_patch(Rectangle((-win, ys["win"] - .16), 2 * win, .32, fc="#d9d9d9", ec=GREY, lw=.6))
ax.add_patch(Rectangle((-ch, ys["conv"] - .16), 2 * ch, .32, fc=SKY, ec=BLUE, lw=.8))
ax.add_patch(Rectangle((-fh, ys["fc"] - .16), 2 * fh, .32, fc=BLUE, ec=BLUE, lw=.8))
ax.errorbar([mc], [ys["meas"]], xerr=[mh_], fmt="o", color=VERM, ms=5, lw=1.4, capsize=3)
ax.plot([0], [ys["fc"]], marker="D", color="white", ms=4, mec=DARK, mew=.8, zorder=5)
ax.axvline(0, color=DARK, lw=.7, ls=":", zorder=0)
lab = [(ys["win"], "Full observing window (transit duration plus baseline)", win + 6),
       (ys["conv"], "Scoring interval: forecast convolved with measurement error (95%)", ch + 6),
       (ys["fc"], "Forecast-only 95% interval", fh + 6),
       (ys["meas"], "Measured mid-time with its own 95% uncertainty", mc + mh_ + 6)]
for y, t, x in lab:
    ax.text(x, y, t, va="center", ha="left", fontsize=7.5)
ax.text(-4, ys["fc"] + .26, "predicted mid-time", ha="right", va="bottom", fontsize=7, color=DARK)
ax.set_xlim(-170, 330)
ax.set_ylim(-.6, 3.6)
ax.set_yticks([])
ax.spines["left"].set_visible(False)
ax.set_xlabel("Time relative to predicted mid-time (min)")
ax.text(1.0, 1.02, "Illustrative, synthetic values; intervals not to scale", transform=ax.transAxes,
        ha="right", va="bottom", fontsize=7, style="italic", color="#555555")
panel(ax, "a", x=0.0, y=1.02)
N["fig1a_synthetic"] = {"forecast_half_width_min": fh, "measurement_half_width_min": mh_,
                        "scoring_half_width_min": ch, "window_half_width_min": win,
                        "measured_offset_min": mc, "note": "illustrative, not data"}

bx = fig.add_subplot(gs[1])
D = lambda y, m, d: mdates.date2num(dt.datetime(y, m, d))
t_drc, t_drd, t_frz = D(2022, 9, 27), D(2025, 11, 18), D(2026, 11, 8)
t_dev0, t_dev1 = D(2022, 9, 28), D(2024, 1, 3)
s74 = D(2024, 1, 3)
last_tc = max(float(out[e]["tc_bjd_tdb"]) for e in eid)
t_end = mdates.date2num(jd_to_date(last_tc + 5))  # end of TESS exposures behind the scored timings (approx.)
N["fig1b"] = {"last_scored_timing_bjd_tdb": last_tc, "later_exposures_bar_end": str(jd_to_date(last_tc + 5).date())}
yo, ya, hb = 1.0, 0.0, .22
bx.add_patch(Rectangle((t_dev0, yo - hb / 2), t_dev1 - t_dev0, hb, fc=BLUE, ec=BLUE))
bx.add_patch(Rectangle((s74, yo - hb / 2), t_drd - s74, hb, fc="white", ec=GREY, hatch="////", lw=.6))
bx.add_patch(Rectangle((t_drd, yo - hb / 2), t_end - t_drd, hb, fc=ORANGE, ec=ORANGE))
bx.add_patch(Rectangle((t_dev0 - 120, ya - hb / 2), t_frz - t_dev0 + 120, hb, fc="none", ec="none"))
bx.add_patch(Rectangle((t_frz, ya - hb / 2), D(2026, 12, 31) - t_frz, hb, fc=VERM, ec=VERM))
bx.plot([t_drc], [yo + .26], "v", color=DARK, ms=6)
bx.plot([t_drd], [yo + .26], "v", color=DARK, ms=6)
bx.plot([t_frz], [ya + .26], "v", color=DARK, ms=6)
bx.plot([t_drd, t_drd], [yo + .26, yo - .5], lw=.5, color=GREY, ls=":", zorder=0)
bx.text(t_drc, yo + .36, "DRC issued\n27 Sep 2022", ha="center", va="bottom", fontsize=7)
bx.text(t_drd, yo + .36, "DRD issued\n18 Nov 2025", ha="center", va="bottom", fontsize=7)
bx.text((t_dev0 + t_dev1) / 2, yo - .2, "final calibration window\n28 Sep 2022 to 3 Jan 2024", ha="center", va="top", fontsize=7, color=BLUE)
bx.text((s74 + t_drd) / 2, yo - .2, "sectors 74-97, Jan 2024 to Nov 2025\nnever opened by this project", ha="center", va="top", fontsize=7, color="#555555")
bx.text(t_drd + 20, yo - .2, "later TESS exposures\n(scored timings)", ha="left", va="top", fontsize=7, color="#9a6700")
bx.text(t_frz - 25, ya + .22, "freeze and authorisation, 8 Nov 2026", ha="right", va="bottom", fontsize=7)
bx.text(t_frz + 12, ya - .2, "first access to the\nlater timings", ha="left", va="top", fontsize=7, color=VERM)
bx.text(D(2021, 12, 15), ya, "no access to the scored timings", ha="left", va="center", fontsize=7, color="#555555", style="italic")
bx.plot([D(2021, 12, 15) + 560, t_frz - 25], [ya, ya], color=GREY, lw=.8, ls=(0, (3, 3)))
bx.set_yticks([yo, ya])
bx.set_yticklabels(["Observations\n(TESS, releases)", "Analyst\naccess"])
bx.set_ylim(-1.05, 2.05)
bx.set_xlim(D(2021, 12, 1), D(2027, 1, 20))
bx.xaxis.set_major_locator(mdates.YearLocator())
bx.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
bx.spines["left"].set_visible(False)
bx.tick_params(axis="y", length=0)
bx.set_xlabel("Calendar date")
panel(bx, "b", x=0.0, y=1.02)
save(fig, "fig1_schematic.png")

# ================================================================ Fig 2
fig = plt.figure(figsize=(7.2, 7.4))
gs = fig.add_gridspec(2, 2, height_ratios=[1, .95], hspace=0.42, wspace=0.32)
a = fig.add_subplot(gs[0, 0])
bins = np.logspace(np.log10(abs_err.min() * .98), np.log10(abs_err.max() * 1.02), 36)
a.hist(abs_err, bins=bins, color=BLUE, ec="white", lw=.4)
a.set_xscale("log")
a.axvline(pooled_med, color=VERM, lw=1.3)
a.text(pooled_med * 1.25, 400, f"pooled median\n{pooled_med:.2f} min", color=VERM, fontsize=7.5, va="top")
a.annotate("HR 858 b\nmax 404 min", xy=(pmax["HR858b"], 2), xytext=(pmax["HR858b"] * .45, 150),
           ha="center", fontsize=7, arrowprops=dict(arrowstyle="->", lw=.7, color=DARK))
a.set_xlabel("Absolute timing error (min, log scale)")
a.set_ylabel("Accepted timings per bin")
a.set_ylim(0, 420)
a.set_title(f"{n_events:,} accepted timings, 151 planets;\nmedian weights each timing equally", fontsize=7, color="#444444", pad=4, loc="left")
a.texts[0].set_position((pooled_med * 1.3, 400))
panel(a, "a", x=-0.16, y=1.16)

b = fig.add_subplot(gs[0, 1])
rk = sorted(planets, key=lambda p: pmax[p])
yv = np.array([pmax[p] for p in rk])
cv = np.array([cnt[p] for p in rk])
sz = 6 + 4.2 * np.sqrt(cv)
col = np.where(np.array(rk) == "HR858b", VERM, BLUE)
b.scatter(np.arange(1, 152), yv, s=sz, c=col, alpha=.8, lw=0)
b.axhline(26.4, color=DARK, lw=.8, ls="--")
b.text(100, 26.4 * 1.12, "26.4 min", fontsize=7.5, va="bottom")
b.set_yscale("log")
b.set_xlabel("Planets ranked by largest error")
b.set_ylabel("Largest accepted error (min, log scale)")
b.annotate("HR 858 b\n404 min", xy=(151, pmax["HR858b"]), xytext=(112, 190), fontsize=7.5, ha="center",
           arrowprops=dict(arrowstyle="->", lw=.7, color=DARK))
b.text(150, 1.0, "150 of 151 planets\nat or below 26.4 min", fontsize=7.5, ha="right", va="center")
b.set_xlim(-3, 156)
hd = [Line2D([], [], marker="o", ls="", color=GREY, ms=np.sqrt(6 + 4.2 * np.sqrt(n)), label=f"{n}") for n in (1, 10, 100)]
b.legend(handles=hd, title="accepted timings", loc="lower right", bbox_to_anchor=(1.0, .02), frameon=False,
         labelspacing=.9, handletextpad=.3, borderpad=0.2, fontsize=7, title_fontsize=7)
panel(b, "b", x=-0.16, y=1.16)
b.get_legend().set_visible(False)
leg = b.legend(handles=hd, title="accepted\ntimings", loc="upper left", frameon=False, labelspacing=.9,
               handletextpad=.3, fontsize=7, title_fontsize=7, bbox_to_anchor=(0.0, 1.0))

# panel c: DRC errors vs years since issue
c2 = [r for r in rows(IN["c2_events"]) if r["status"] == "accepted"]
jd_drc = (dt.datetime(2022, 9, 27, 15, 25, 16) - dt.datetime(1858, 11, 17)).total_seconds() / 86400 + 2400000.5
yrs = np.array([(float(r["drc_prediction_bjd_tdb"]) - jd_drc) / 365.25 for r in c2])
res = np.array([abs(float(r["residual_min"])) for r in c2])
era = np.array([r["era"] for r in c2])
pl2 = {r["planet"] for r in c2}
N["fig2c"] = {"accepted_events": len(c2), "planets": len(pl2), "DRC_issue_jd_utc_approx": jd_drc,
              "convention": "years = (drc_prediction_bjd_tdb - JD of 2022-09-27T15:25:16 UTC)/365.25; BJD_TDB treated as JD (offset under ~1.5 min over the interval, negligible at year scale)",
              "era_counts": {e: int((era == e).sum()) for e in sorted(set(era))},
              "max_years": float(yrs.max())}
gc = gs[1, :].subgridspec(1, 2, width_ratios=[1, 1], wspace=0.06)
eras = [("S56_S73", "2022-2023 development block (S56-S73)"), ("inspected_2026", "2026 (held-out for DRD, inspected after the test)")]
cax = []
for i, (e, ttl) in enumerate(eras):
    m = era == e
    x0, x1 = yrs[m].min(), yrs[m].max()
    ax_ = fig.add_subplot(gc[i], sharey=cax[0] if cax else None)
    ax_.scatter(yrs[m], res[m], s=3, color=BLUE, alpha=.18, lw=0, rasterized=True)
    edges = np.linspace(x0, x1, 9)
    mid, med = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s = m & (yrs >= lo) & (yrs <= hi)
        if s.sum() > 5:
            mid.append(yrs[s].mean()); med.append(np.median(res[s]))
    ax_.plot(mid, med, "-o", color=VERM, lw=1.3, ms=3, label="median per bin")
    ax_.set_xlim(x0 - .03, x1 + .03)
    ax_.set_title(ttl, fontsize=7.5, pad=3)
    ax_.set_yscale("log")
    if i == 1:
        ax_.spines["left"].set_visible(False)
        ax_.tick_params(axis="y", which="both", left=False, labelleft=False)
    else:
        ax_.set_ylabel("DRC forecast absolute error (min, log)")
    cax.append(ax_)
    N["fig2c"][e] = {"years_range": [float(x0), float(x1)], "median_abs_error_min": float(np.median(res[m])),
                     "events": int(m.sum()), "bin_medians_min": [float(v) for v in med]}
cax[0].legend(loc="upper left", frameon=False, fontsize=7)
fig.text(.52, .045, "Years since DRC issue (27 Sep 2022); axis gap between blocks omitted", ha="center", fontsize=8.5)
cax[0].text(0, 1.2, "c", transform=cax[0].transAxes, fontsize=10, fontweight="bold", ha="right", va="bottom")
cax[1].text(.98, .03, f"Both blocks: {len(c2):,} accepted timings, {len(pl2)} planets;\nretrospective comparison on already-inspected timings",
            transform=cax[1].transAxes, ha="right", va="bottom", fontsize=6.8, color="#444444")
save(fig, "fig2_accuracy.png")

# ================================================================ Fig 3
fig, (a, b) = plt.subplots(1, 2, figsize=(7.2, 3.3), gridspec_kw={"wspace": .3})
nb = 20
edges = np.linspace(0, 1, nb + 1)
wn = w / w.sum()
h0 = np.histogram(pit0, edges, weights=wn)[0] * nb
h2 = np.histogram(pit2, edges, weights=wn)[0] * nb
ctr = (edges[:-1] + edges[1:]) / 2
a.axvspan(0, .025, color="#eeeeee", zorder=0)
a.axvspan(.975, 1, color="#eeeeee", zorder=0)
a.bar(ctr - .012, h0, width=.023, color=BLUE, label="M0")
a.bar(ctr + .012, h2, width=.023, color=ORANGE, label="M2")
a.axhline(1, color=DARK, lw=.9, ls="--", label="uniform reference")
inside = {m: float(wn[(p >= .025) & (p <= .975)].sum()) for m, p in (("M0", pit0), ("M2", pit2))}
tails = {m: [float(wn[p < .025].sum()), float(wn[p > .975].sum())] for m, p in (("M0", pit0), ("M2", pit2))}
a.set_xlim(0, 1)
a.set_xlabel("Predictive PIT value (low = transit earlier than forecast)")
a.set_ylabel("Planet-weighted density")
a.legend(loc="upper center", frameon=False, ncol=3, fontsize=7, columnspacing=1, bbox_to_anchor=(.5, 1.16))
a.text(.5, .97, f"inside [0.025, 0.975] (shaded tails outside):\nM0 {inside['M0']:.3f}, M2 {inside['M2']:.3f}",
       transform=a.transAxes, ha="center", va="top", fontsize=7)
panel(a, "a", x=-0.12, y=1.12)
N["fig3a"] = {"inside_0.025_0.975_planet_weighted": inside, "tail_mass_below_0.025_above_0.975": tails,
              "bins": nb, "events": n_events, "planets": 151, "weights": "planet_weight, each planet 1 unit total, normalised",
              "weight_sum": float(w.sum())}
assert abs(inside["M0"] - .908) < .001

cov = [r for r in rows(IN["coverage"]) if r["set"] == "primary" and r["method"] in ("M0", "M2")]
b.plot([0, 1], [0, 1], color=DARK, lw=.9, ls="--", label="1:1")
N["fig3b"] = {}
for m, c_, mk in (("M0", BLUE, "o"), ("M2", ORANGE, "s")):
    rr = sorted([r for r in cov if r["method"] == m], key=lambda r: float(r["nominal"]))
    x = np.array([float(r["nominal"]) for r in rr]); y = np.array([float(r["measured_time_coverage"]) for r in rr])
    lo = np.array([float(r["ci95_lower"]) for r in rr]); hi = np.array([float(r["ci95_upper"]) for r in rr])
    off = -.006 if m == "M0" else .006
    b.errorbar(x + off, y, yerr=[y - lo, hi - y], fmt=mk + "-", color=c_, ms=4, lw=1, capsize=2, label=m)
    N["fig3b"][m] = {"nominal": x.tolist(), "coverage": y.tolist(), "ci95_lower": lo.tolist(), "ci95_upper": hi.tolist()}
b.set_xlabel("Nominal central-interval probability")
b.set_ylabel("Measured-time coverage")
b.set_xlim(.4, 1.0); b.set_ylim(.4, 1.0)
b.set_aspect("equal", adjustable="box")
b.legend(loc="upper left", frameon=False, title="vertical bars: conditional 95% intervals", title_fontsize=6.5)
panel(b, "b", x=-0.15, y=1.12)
save(fig, "fig3_calibration.png")

# ================================================================ Fig 4
S = json.load(open(IN["hr858_summary"]))
pl = S["routes"]["PDCSAP_FLUX"]["planets"]
fig = plt.figure(figsize=(7.2, 6.6))
gs = fig.add_gridspec(2, 1, height_ratios=[1, 1.05], hspace=.42)
a = fig.add_subplot(gs[0])
cols = {"b": BLUE, "c": ORANGE, "d": "#555555"}
frozen = {r["event_id"]: r for r in rows(IN["accepted_outcomes"]) if r["planet"] == "HR858b"}
N["fig4a"] = {}
for k in "bcd":
    t = pl[k]["transits"]
    x = np.array([jd_to_date(r["tc_bjd_tdb"]) for r in t])
    y = np.array([r["o_minus_c_ref_min"] for r in t]) / 60
    e = np.array([r["sigma_min"] for r in t]) / 60
    a.errorbar(mdates.date2num(x), y, yerr=e, fmt="o", color=cols[k], ms=3.5, lw=.8, label=f"HR 858 {k}")
    N["fig4a"][k] = {"n": len(t), "o_minus_c_min_first_last": [t[0]["o_minus_c_ref_min"], t[-1]["o_minus_c_ref_min"]]}
a.axhline(0, color=GREY, lw=.8)
a.set_ylabel("Observed minus published (h)")
a.set_xlabel("Calendar date, 2026 (TESS sectors 105-107)")
a.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
a.legend(loc="center", frameon=False, ncol=3, bbox_to_anchor=(.5, .6))
a.set_title("Published reference ephemerides of Bonfanti et al. (2025); independent PDCSAP re-extraction", fontsize=7.5, loc="left", pad=3)
panel(a, "a", x=-0.07)
N["fig4a"]["reference"] = "Bonfanti et al. 2025 via NASA Exoplanet Archive default row (summary.json config)"
N["fig4a"]["b_pdcsap_independent_minus_drd_min_range"] = S["comparison_with_frozen"]["PDCSAP_FLUX"]["independent_minus_drd_min_range"]

# 4b
rp = [r for r in rows(IN["release_planets"]) if r["release"] == "DRD" and r["planet"] == "HR858b"][0]
T0, P = float(rp["t0_bjd_tdb"]), float(rp["period_days"])
rel = []
for line in open(IN["released_timings"]):
    f = line.split()
    if f and f[0] == "HR858b":
        rel.append((float(f[1]), float(f[2])))
nrel = np.array([round((t - T0) / P) for t, _ in rel])
r_h = np.array([(t - T0 - n * P) * 24 for (t, _), n in zip(rel, nrel)])
r_e = np.array([u * 24 for _, u in rel])
r_d = mdates.date2num([jd_to_date(t) for t, _ in rel])
intended = [r for r in rows(IN["intended_forecasts"]) if r["planet"] == "HR858b"]
term = {r["event_id"]: r["status"] for r in rows(IN["terminal_ledger"]) if r["planet"] == "HR858b"}
intended.sort(key=lambda r: float(r["predicted_bjd_tdb"]))
band_d = mdates.date2num([jd_to_date(r["predicted_bjd_tdb"]) for r in intended])
band_h = np.array([1.96 * np.sqrt(float(r["forecast_variance_s2"])) / 3600 for r in intended])
acc = [(e, r) for e, r in frozen.items()]
acc.sort(key=lambda er: float(er[1]["tc_bjd_tdb"]))
fpred = {e: float(fc[e]["predicted_bjd_tdb"]) for e, _ in acc}
a_d = mdates.date2num([jd_to_date(r["tc_bjd_tdb"]) for _, r in acc])
a_h = np.array([(float(r["tc_bjd_tdb"]) - fpred[e]) * 24 for e, r in acc])
a_e = np.array([float(r["sigma_s"]) / 3600 for _, r in acc])
a_hi = np.array([(float(r["q975_s"])) / 3600 for _, r in acc])
from collections import Counter
stat = Counter(term.values())
N["fig4b"] = {"DRD_T0_bjd_tdb": T0, "DRD_period_d": P, "released_input_rows": len(rel),
              "released_input_resid_rms_min": float(np.sqrt(np.mean((r_h * 60) ** 2))),
              "last_input": str(jd_to_date(rel[-1][0]).date()) if rel[-1][0] == max(t for t, _ in rel) else str(jd_to_date(max(t for t, _ in rel)).date()),
              "intended_events": len(intended), "terminal_status_counts": dict(stat), "accepted_events": len(acc),
              "accepted_resid_hours_min_max": [float(a_h.min()), float(a_h.max())],
              "forecast_only_95_halfwidth_hours_min_max": [float(band_h.min()), float(band_h.max())],
              "accepted_resid_min_range": [float(a_h.min() * 60), float(a_h.max() * 60)]}
assert len(intended) == 24 and len(acc) == 16 and len(rel) == 16

gc = gs[1].subgridspec(1, 2, width_ratios=[1.35, 1], wspace=.05)
l = fig.add_subplot(gc[0]); rt = fig.add_subplot(gc[1], sharey=l)
l.errorbar(r_d, r_h, yerr=r_e, fmt="o", color=DARK, ms=3.5, lw=.8, label=f"released input timings (n = {len(rel)})")
rt.fill_between(band_d, -band_h, band_h, color=SKY, alpha=.55, lw=0, label="forecast-only 95% interval")
rt.errorbar(a_d, a_h, yerr=a_e, fmt="o", color=VERM, ms=3.5, lw=.8, label=f"accepted 2026 timings (n = {len(acc)})")
for ax_ in (l, rt):
    ax_.axhline(0, color=BLUE, lw=1.0)
l.set_xlim(r_d.min() - 60, r_d.max() + 60)
rt.set_xlim(band_d.min() - 8, band_d.max() + 8)
l.xaxis.set_major_locator(mdates.YearLocator()); l.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
rt.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
rt.xaxis.set_major_locator(mdates.MonthLocator())
pass
l.set_ylabel("Observed minus issued DRD line (h)")
rt.spines["left"].set_visible(False); rt.tick_params(axis="y", left=False, labelleft=False)
l.set_ylim(-7.4, 1.2)
l.text(.02, .5, "issued DRD line", color=BLUE, transform=l.get_yaxis_transform(), fontsize=7, va="bottom")
l.set_xlabel("Calendar date (axis gap omitted)")
h1, l1 = l.get_legend_handles_labels(); h2, l2 = rt.get_legend_handles_labels()
l.legend(h1 + h2, l1 + l2, loc="center", frameon=False, fontsize=7, bbox_to_anchor=(.5, .45))
rt.text(.5, .72, "24 intended; 16 accepted\n(6 no cadence at prediction,\n1 edge, 1 integration unresolved)",
        transform=rt.transAxes, ha="center", va="top", fontsize=6.8, color="#444444")
rt.annotate(f"largest miss: 404 min\n(6.7 h)", xy=(a_d[-1], a_h[-1]), xytext=(a_d[-6], -4.2), fontsize=7, ha="center",
            arrowprops=dict(arrowstyle="->", lw=.7, color=DARK))
l.text(0, 1.05, "b", transform=l.transAxes, fontsize=10, fontweight="bold", ha="right", va="bottom")
l.set_title("HR 858 b against the issued DRD line (released inputs end 2020)", fontsize=7.5, loc="left", pad=3)
save(fig, "fig4_hr858.png")

json.dump(receipt, open(OUT / "figures_receipt.json", "w"), indent=1)
print("done")
