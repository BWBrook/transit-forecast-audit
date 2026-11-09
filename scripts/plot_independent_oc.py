"""Observed-minus-reference timing figure for an independently validated system (D071, review R03).

Reads results/independent_validation/<system>/summary.json and writes oc.{png,pdf} beside it.

    uv run --with matplotlib --with numpy scripts/plot_independent_oc.py results/independent_validation/hr858
"""

import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


def main(d):
    d = Path(d); s = json.loads((d / "summary.json").read_text())
    route = s["routes"]["PDCSAP_FLUX"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "pdf.fonttype": 42})
    fig, ax = plt.subplots(figsize=(7.5, 3.6))
    colours = {"b": "#176b93", "c": "#c9772b", "d": "#555555"}
    for name, pl in route["planets"].items():
        if not pl.get("identified"):
            continue
        x = np.array([r["tc_bjd_tdb"] for r in pl["transits"]]) - 2460000
        y = np.array([r["o_minus_c_ref_min"] for r in pl["transits"]]) / 60
        e = np.array([r["sigma_min"] for r in pl["transits"]]) / 60
        ax.errorbar(x, y, e, fmt="o", ms=3.5, color=colours.get(name, "k"), label=f"HR 858 {name}", capsize=0)
    pairs = s.get("comparison_with_frozen", {}).get("PDCSAP_FLUX", {}).get("pairs", [])
    if pairs:
        ref = s["config"]["planets"]["b"]["reference_ephemeris"]
        x = np.array([p["frozen_tc"] for p in pairs])
        n = np.round((x - ref["t0_bjd_tdb"]) / ref["period_d"])
        y = (x - ref["t0_bjd_tdb"] - n * ref["period_d"]) * 24
        ax.plot(x - 2460000, y, "x", color="black", ms=5, label="b, frozen evaluation timings")
    ax.axhline(0, color="#999999", lw=0.8)
    ax.set_xlabel("BJD$_{\\rm TDB}$ − 2460000 (TESS sectors 105–107)")
    ax.set_ylabel("Observed − reference ephemeris (h)")
    ax.set_title("Reference: Bonfanti et al. (2025) linear ephemerides", fontsize=9)
    ax.legend(frameon=False, fontsize=8, ncol=2, loc="center right")
    fig.tight_layout()
    fig.savefig(d / "oc.png", dpi=200); fig.savefig(d / "oc.pdf", metadata={"CreationDate": None, "ModDate": None})


if __name__ == "__main__":
    main(sys.argv[1])
