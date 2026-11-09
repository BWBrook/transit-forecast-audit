"""Plot the per-planet M2 - M0 standardised IS95 differences of the frozen primary evaluation (D065).

Sorted planet differences on a symmetric-log axis, with the three current-catalogue TTV-flagged planets
marked. Descriptive; reads the committed planet table only.

    MPLCONFIGDIR=/private/tmp/transit-final-review-mpl .venv/bin/python scripts/plot_final_planet_deltas.py
"""

import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "results/final_secondaries/descriptive/planet_deltas.csv"
OUT = ROOT / "results/final_review/figures/planet_deltas"


def main():
    with SRC.open() as fh:
        rows = [r for r in csv.DictReader(fh) if r["analysis_set"] == "primary" and r["delta"] not in ("", "nan")]
    rows.sort(key=lambda r: float(r["delta"]))
    d = np.array([float(r["delta"]) for r in rows])
    flagged = np.array([r["current_catalogue_ttv_label"] == "current_archive_flagged" for r in rows])
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "font.family": "DejaVu Sans", "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(8.5, 3.8))
    x = np.arange(1, len(d) + 1)
    ax.bar(x, d, width=0.85, color=np.where(d < 0, "#176b93", "#c9772b"))
    ax.scatter(x[flagged], np.full(flagged.sum(), 0.35), marker="v", color="black", s=22, zorder=3,
               label="current NASA catalogue TTV flag (marker above bar)")
    ax.set_yscale("symlog", linthresh=1)
    ax.axhline(0, color="#555555", linewidth=0.8)
    ax.axhline(d.mean(), color="#176b93", linestyle="--", linewidth=1, label=f"mean {d.mean():+.3f}")
    ax.axhline(np.median(d), color="#c9772b", linestyle=":", linewidth=1.2, label=f"median {np.median(d):+.3f}")
    big = [(r["planet"], xi, di) for r, xi, di in zip(rows, x, d) if di < -10]
    for name, xi, di in big[:2]:
        ax.text(xi + 3, di, f"{name} ({di:.0f})", fontsize=8, va="center")
    if len(big) > 2:
        rest = big[2:]
        ax.text(rest[-1][1] + 3, np.mean([b[2] for b in rest]), ", ".join(f"{n} ({v:.0f})" for n, _, v in rest),
                fontsize=8, va="center")
    ax.set_xlim(0, len(d) + 1)
    ax.set_xlabel(f"Planets, sorted ({(d < 0).sum()} of {len(d)} improve under M2)")
    ax.set_ylabel("M2 − M0 standardised IS95\n(planet mean; symlog; lower is better)")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
    fig.tight_layout()
    for ext in ("png", "pdf"):
        fig.savefig(OUT.with_suffix("." + ext), dpi=200)


if __name__ == "__main__":
    main()
