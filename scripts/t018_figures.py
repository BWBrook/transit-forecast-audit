"""Plot conditional loss-scale and measured-time coverage diagnostics."""

import csv
import gzip
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results/revision_stage0/interpretability"


def rows(name):
    return list(csv.DictReader((DATA / name).open()))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "font.family": "DejaVu Sans"})
    contrasts = [r for r in rows("loss_scales.csv") if r["set"] == "primary"]
    figure, axes = plt.subplots(1, 3, figsize=(11, 3.3))
    names = [("is95_standardised", "M0 predictive-SD scale"),
             ("is95_forecast_normalised", "Forecast-SD scale"), ("is95_minutes", "Raw minutes")]
    for axis, (metric, title) in zip(axes, names):
        axis.axvline(0, color="#777777", linestyle="--", linewidth=.8)
        for height, selection, colour in ((1, "all", "#176b93"), (0, "without_HR858", "#a75a1d")):
            row = next(r for r in contrasts if r["metric"] == metric and r["selection"] == selection)
            value, lo, hi = (float(row[k]) for k in ("point", "ci95_lower", "ci95_upper"))
            axis.errorbar(value, height, xerr=[[value-lo], [hi-value]], fmt="o", color=colour, capsize=4)
        axis.set(title=title, yticks=[0, 1], yticklabels=["Without HR858", "All planets"], ylim=(-.6, 1.6),
                 xlabel="M2 − M0 (lower is better)")
    figure.suptitle("Primary set: loss scales with conditional 95% host intervals", y=1.03)
    figure.tight_layout()
    p1 = DATA / "loss_scales.png"
    figure.savefig(p1, dpi=170, bbox_inches="tight")
    plt.close(figure)
    curve = [r for r in rows("coverage_vs_nominal.csv") if r["set"] == "primary"]
    figure, (axis, hist) = plt.subplots(1, 2, figsize=(10, 3.6))
    axis.plot([.45, 1], [.45, 1], color="#999999", linestyle="--", linewidth=1)
    for method, colour in (("M0", "#555555"), ("M2", "#176b93")):
        selected = sorted([r for r in curve if r["method"] == method], key=lambda r: float(r["nominal"]))
        x = np.array([float(r["nominal"]) for r in selected])
        y, lo, hi = [np.array([float(r[key]) for r in selected]) for key in
                     ("measured_time_coverage", "ci95_lower", "ci95_upper")]
        axis.errorbar(x, y, yerr=[y-lo, hi-y], marker="o", color=colour, capsize=3, label=method)
    axis.set(xlim=(.45, 1.01), ylim=(.4, 1.01), xlabel="Nominal central interval probability",
             ylabel="Planet-balanced measured-time coverage", title="Conditional on accepted timings")
    axis.legend(frameon=False)
    source = ROOT / "results/final_primary/joint_draws.json.gz"
    with gzip.open(source, "rt") as stream:
        draws = json.load(stream)["draws"]
    s = np.array([row["models"]["M2"]["s_log_lambda"] for row in draws])
    hist.hist(s, bins=35, color="#176b93", alpha=.75)
    for q in (.025, .975):
        hist.axvline(np.quantile(s, q), color="#555555", linestyle=":")
    hist.set(xlabel="M2 s (log-variance spread)", ylabel="Stored joint refit draws",
             title="Parameter uncertainty, not a forecast mixture")
    hist.text(.98, .95, f"95%: [{np.quantile(s,.025):.2f}, {np.quantile(s,.975):.2f}]",
              ha="right", va="top", transform=hist.transAxes, fontsize=9)
    figure.tight_layout()
    p2 = DATA / "coverage_and_s.png"
    figure.savefig(p2, dpi=170)
    plt.close(figure)
    flow_path = DATA / "population_flow.csv"
    with flow_path.open() as stream:
        flow = list(csv.DictReader(stream))
    planet_path = ROOT / "results/revision_stage0/selection/per_planet_recovery.csv"
    with planet_path.open() as stream:
        planet_rows = list(csv.DictReader(stream))
    boundary_path = ROOT / "results/prefreeze/manifest_summary.json"
    excluded = json.loads(boundary_path.read_text())["boundary_excluded"]
    population = {(r["set"], r["status"]): r for r in flow if r["level"] == "population"}
    intended = sum(int(population[label, "intended"]["events"]) for label in ("primary", "extension"))
    figure, axis = plt.subplots(figsize=(11.5, 6.3))
    axis.set(xlim=(0, 10), ylim=(-.2, 6))
    axis.axis("off")
    def box(x, y, text, colour="#f1f1f1"):
        axis.text(x, y, text, ha="center", va="center", fontsize=10,
                  bbox={"boxstyle": "round,pad=.5", "facecolor": colour, "edgecolor": "#777777"})
    def arrow(start, end):
        axis.annotate("", xy=end, xytext=start,
                      arrowprops={"arrowstyle": "->", "color": "#555555", "linewidth": 1.2})
    box(5, 5.5, f"Frozen roster: {len(planet_rows)} planets / {len({r['host'] for r in planet_rows})} hosts")
    box(5, 4.6, f"{intended + excluded:,} metadata opportunities")
    arrow((5, 5.2), (5, 4.9))
    box(1.45, 4.6, f"{excluded} near-boundary\nevents excluded")
    arrow((3.4, 4.6), (2.45, 4.6))
    for label, x in (("primary", 2.5), ("extension", 7.5)):
        total = population[label, "intended"]
        accepted = population[label, "accepted"]
        n, a = int(total["events"]), int(accepted["events"])
        title = "Core primary" if label == "primary" else "Exploratory extension"
        box(x, 3.4, f"{title}\n{n:,} opportunities / {total['planets']} planets")
        arrow((5, 4.25), (x, 3.8))
        box(x-1, 2.05, f"{a:,} accepted timings\n{accepted['planets']} planets", "#e1f0f7")
        box(x+1, 2.05, f"{n-a:,} not accepted")
        arrow((x, 3), (x-1, 2.45))
        arrow((x, 3), (x+1, 2.45))
        missing = int(total["planets"]) - int(accepted["planets"])
        axis.text(x, 1.15, f"{missing} intended planets have no accepted timing", ha="center", fontsize=9)
    status = {r["status"]: int(r["events"]) for r in flow if r["set"] == "primary" and r["level"] == "terminal_event"}
    axis.text(5, .55, f"Core not accepted: no cadence at prediction {status['no_cadence_coverage_at_prediction']}; "
              f"window coverage {status['excluded_coverage']};\n"
              f"integration {status['integration_unresolved']}; prior edge {status['edge']}; "
              f"product identification {status['product_id_failed']}; likelihood support {status['likelihood_support_unresolved']}.",
              ha="center", fontsize=9)
    axis.text(5, -.05, "Opportunities are metadata counts. Not accepted does not imply an ephemeris miss or failed observing capture.",
              ha="center", fontsize=8, color="#555555")
    figure.tight_layout()
    p3 = DATA / "population_flow.png"
    figure.savefig(p3, dpi=170)
    plt.close(figure)
    inputs = [DATA / "loss_scales.csv", DATA / "coverage_vs_nominal.csv", source, flow_path, planet_path, boundary_path]
    receipt = {"script_sha256": sha(Path(__file__)),
               "input_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
               "output_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (p1, p2, p3)},
               "matplotlib": matplotlib.__version__, "scope": "Descriptive; conditional intervals are not primary decisions"}
    (DATA / "figures_receipt.json").write_text(json.dumps(receipt, indent=2, allow_nan=False) + "\n")


if __name__ == "__main__":
    main()
