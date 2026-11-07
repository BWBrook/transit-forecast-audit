"""Sprint 2 development figures (PNG, 200 dpi) for the article draft.

    .venv/bin/python scripts/sprint2_figures.py
"""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path[:0] = [str(HERE), str(ROOT / "src")]
import sprint2_analysis as sa  # noqa: E402
import sprint2_outcomes as so  # noqa: E402

OUT = ROOT / "results" / "sprint2" / "figures"
INK, GRID = "#222222", "#d9d9d9"
C1, C2, C3 = "#2b6cb0", "#c05621", "#6b7280"


def ledger(sample):
    d = ROOT / "results" / "sprint2" / sample
    p = d / "ledger.csv"
    fh = p.open() if p.exists() else gzip.open(d / "ledger.csv.gz", "rt")
    return list(csv.DictReader(fh))


def host_points(rows, rule):
    by = defaultdict(list)
    tm = {}
    for r in rows:
        g = so.tmag_multiplier(r["tmag"]) if rule == "t015v3c" else 1.0
        by[r["host"]].append((float(r["z"]) / g) ** 2)
        tm[r["host"]] = float(r["tmag"])
    h = sorted(by)
    return np.array([tm[x] for x in h]), np.array([np.mean(by[x]) for x in h]), np.array([len(by[x]) for x in h])


def calibration_figure(samples):
    fig, axes = plt.subplots(1, len(samples), figsize=(5.2 * len(samples), 4.0), sharey=True, squeeze=False)
    for ax, (sample, title) in zip(axes[0], samples):
        rows = sa.production([r for r in ledger(sample) if r["status"] == "timed" and r["mode"] == "remove"
                              and r.get("truth_id")])
        for rule, col, lab in (("t015v3", C3, "t015v3 (no multiplier)"), ("t015v3c", C1, "t015v3c (Tmag multiplier)")):
            t, m, n = host_points(rows, rule)
            ax.scatter(t, np.sqrt(m), s=8 + 2 * np.sqrt(n), color=col, alpha=0.55, lw=0, label=lab)
            X = np.column_stack([np.ones_like(t), t - 11])
            b = np.linalg.lstsq(X, m, rcond=None)[0]
            xs = np.linspace(8, 13.5, 50)
            ax.plot(xs, np.sqrt(np.maximum(b[0] + b[1] * (xs - 11), 0)), color=col, lw=2)
        ax.axhspan(0.80, 1.15, color="#2f855a", alpha=0.07, lw=0)
        ax.axhline(1, color=INK, lw=0.8, ls=":")
        ax.set_xlim(4.8, 13.7)
        ax.set_ylim(0, 2.2)
        ax.set_xlabel("TESS magnitude of host")
        ax.set_title(title, fontsize=10, color=INK)
        ax.grid(color=GRID, lw=0.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0][0].set_ylabel("Host timing z-RMS (injected transits)")
    axes[0][0].legend(frameon=False, fontsize=8, loc="upper left")
    fig.text(0.01, 0.01, "Points: hosts (size ~ timed injections). Lines: equal-host linear model of mean z\u00b2.\n"
             "Band: endpoint criterion [0.80, 1.15].", fontsize=7, color=C3)
    fig.tight_layout(rect=(0, 0.07, 1, 1))
    fig.savefig(OUT / "fig_timing_calibration.png", dpi=200)
    plt.close(fig)


def contrast_figure():
    p = ROOT / "results" / "sprint2" / "forecasts" / "convention_comparison.json"
    if not p.exists():
        return
    d = json.loads(p.read_text())
    variants = [("exoclock_all", "ExoClock timings, all (sprint 1)"), ("exoclock_matched", "ExoClock timings, matched"),
                ("ours_matched_raw", "t015v3, matched"), ("ours_matched", "t015v3c, matched"),
                ("ours_all_raw", "t015v3, all timed"), ("ours_all", "t015v3c, all timed")]
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.4), sharey=True)
    for ax, exp in zip(axes, ("release_transfer", "chronological")):
        res = d["experiments"][exp]
        for i, (v, lab) in enumerate(variants):
            r = res.get(v, {})
            if "metrics" not in r:
                continue
            for j, (m, col) in enumerate((("M1", C3), ("M2", C1), ("M3", C2))):
                pt = r["metrics"][m]["delta_standardised_vs_M0"]
                ci = r["host_refit"][m]["delta_is95_standardised_percentile95"]
                y = i + (j - 1) * 0.22
                ax.plot(np.clip(ci, -8, 8), [y, y], color=col, lw=1.6)
                if ci[1] > 8:
                    ax.annotate("", (8.4, y), (7.6, y), arrowprops=dict(arrowstyle="->", color=col, lw=1))
                ax.plot(pt, y, "o", color=col, ms=4, label=m if i == 0 else None)
        ax.axvline(0, color=INK, lw=0.8)
        ax.set_xlim(-8, 8.6)
        ax.set_yticks(range(len(variants)))
        ax.set_yticklabels([lab for _, lab in variants], fontsize=8)
        ax.set_title(exp.replace("_", " "), fontsize=10)
        ax.set_xlabel("Planet-balanced standardised IS95, method − M0\n(negative favours method; 95% host-refit interval)",
                      fontsize=8)
        ax.grid(axis="x", color=GRID, lw=0.5)
        ax.spines[["top", "right"]].set_visible(False)
    axes[0].legend(frameon=False, fontsize=8, loc="lower left")
    fig.tight_layout()
    fig.savefig(OUT / "fig_convention_contrasts.png", dpi=200)
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    samples = [("dev", "Development: 45 inspected hosts")]
    if (ROOT / "results/sprint2/confirm/ledger.csv").exists() or (ROOT / "results/sprint2/confirm/ledger.csv.gz").exists():
        samples.append(("confirm", "Confirmation: prespecified new hosts"))
    calibration_figure(samples)
    contrast_figure()
    print(sorted(p.name for p in OUT.glob("*.png")))


if __name__ == "__main__":
    main()
