"""Online figure set: per-planet accepted-timing residuals against the issued DRD forecast.

Run from the repository root: .venv/bin/python scripts/build_online_figure_set.py
Reads saved tables only; writes results/reconstruction_displays/online_figure_set_oc.pdf and
adds an entry to figures_receipt.json.
"""
import csv, datetime as dt, hashlib, json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_pdf import PdfPages

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "results/reconstruction_displays"
PRIM = ROOT / "data/derived/revision_stage0/benchmark/primary"
srcs = {"accepted_outcomes": PRIM / "accepted_outcomes.csv", "accepted_forecasts": PRIM / "accepted_forecasts.csv"}
rd = lambda p: list(csv.DictReader(open(p, newline="")))
fc = {r["event_id"]: r for r in rd(srcs["accepted_forecasts"])}
by = {}
for r in rd(srcs["accepted_outcomes"]):
    f = fc[r["event_id"]]
    t = float(r["tc_bjd_tdb"])
    by.setdefault(r["planet"], []).append((t, (t - float(f["predicted_bjd_tdb"])) * 1440,
                                           float(r["sigma_s"]) / 60, 1.96 * np.sqrt(float(f["forecast_variance_s2"])) / 60))
planets = sorted(by)
assert len(planets) == 151 and sum(len(v) for v in by.values()) == 2185
date = lambda jd: mdates.date2num(dt.datetime(1858, 11, 17) + dt.timedelta(days=jd - 2400000.5))
plt.rcParams.update({"font.size": 6.5, "axes.spines.top": False, "axes.spines.right": False, "axes.linewidth": .5})
BLUE, VERM, SKY = "#0072B2", "#D55E00", "#56B4E9"
R, C = 5, 4
per = R * C
npages = -(-len(planets) // per)
with PdfPages(OUT / "online_figure_set_oc.pdf") as pdf:
    for pg in range(npages):
        fig, axs = plt.subplots(R, C, figsize=(8.27, 11.69))
        for ax in axs.flat:
            ax.set_visible(False)
        for ax, p in zip(axs.flat, planets[pg * per:(pg + 1) * per]):
            ax.set_visible(True)
            v = sorted(by[p])
            d = np.array([date(x[0]) for x in v]); y = np.array([x[1] for x in v])
            e = np.array([x[2] for x in v]); b = np.array([x[3] for x in v])
            ax.fill_between(d, -b, b, color=SKY, alpha=.45, lw=0, step=None)
            ax.axhline(0, color="#555555", lw=.5)
            ax.errorbar(d, y, yerr=e, fmt="o", ms=2, lw=.5, color=VERM if p == "HR858b" else BLUE)
            ax.set_title(f"{p}  (n = {len(v)})", fontsize=7, loc="left", pad=2)
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=2, maxticks=3))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
            ax.tick_params(length=2, pad=1)
            ax.set_ylabel("min", fontsize=6, labelpad=1)
            for t in ax.get_xticklabels():
                t.set_rotation(20); t.set_ha("right")
        fig.suptitle("Accepted timings minus issued DRD forecast; light band = forecast-only 95% interval; bars = timing 1-sigma"
                     f"   (page {pg + 1}/{npages})", fontsize=7, y=.995)
        fig.tight_layout(rect=(0, 0, 1, .985))
        pdf.savefig(fig); plt.close(fig)
pdf_path = OUT / "online_figure_set_oc.pdf"
rec_p = OUT / "figures_receipt.json"
rec = json.load(open(rec_p))
rec["online_figure_set_oc"] = {"file": "online_figure_set_oc.pdf", "sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
    "bytes": pdf_path.stat().st_size, "planets": len(planets), "events": 2185, "pages": npages, "panels_per_page": per,
    "hr858b_page": planets.index("HR858b") // per + 1, "band": "+/-1.96*sqrt(forecast_variance_s2)/60 min per event",
    "inputs_sha256": {k: hashlib.sha256(p.read_bytes()).hexdigest() for k, p in srcs.items()}}
json.dump(rec, open(rec_p, "w"), indent=1)
print(pdf_path.stat().st_size, npages, rec["online_figure_set_oc"]["hr858b_page"])
