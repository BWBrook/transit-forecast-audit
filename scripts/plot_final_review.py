"""Plot the frozen primary intervals and declared fixed-parameter influence curve."""

import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]


def main():
    summary_path = ROOT / "results/final_primary/evaluation_summary.json"
    curve_path = ROOT / "results/final_secondaries/descriptive/leave_gain_hosts_out.csv"
    summary = json.loads(summary_path.read_text())
    with curve_path.open() as fh:
        curve = [r for r in csv.DictReader(fh) if r["analysis_set"] == "primary"]
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "font.family": "DejaVu Sans", "pdf.fonttype": 42})
    fig, (left, right) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.05, 1]})
    point = summary["primary_delta_M2_M0"]
    for height, key, colour in ((1, "joint_refit_ci95", "#176b93"), (.3, "conditional_fixed_parameter_ci95", "#777777")):
        lo, hi = summary[key]
        left.errorbar(point, height, xerr=[[point - lo], [hi - point]], fmt="o", color=colour,
                      capsize=4, linewidth=2)
        left.text(-2.22, height + .15, f"{point:+.2f} [{lo:+.2f}, {hi:+.2f}]", color=colour, fontsize=9)
    left.axvline(0, color="#555555", linestyle="--", linewidth=1)
    left.set(yticks=[1, .3], yticklabels=["Joint refit\n(primary)", "Fixed parameters\n(conditional)"],
             ylim=(-.1, 1.5), xlim=(-2.3, 2.6), xlabel="Mean standardised IS95 difference\n(M2 − M0; lower is better)",
             title="Primary verdict: inconclusive")
    left.spines["left"].set_visible(False)
    left.tick_params(axis="y", length=0)
    k = [int(r["k"]) for r in curve if r["available"] == "True"]
    values = [float(r["mean_planet_delta"]) for r in curve if r["available"] == "True"]
    right.axhline(0, color="#555555", linestyle="--", linewidth=1)
    right.plot(k, values, "o-", color="#176b93", linewidth=2)
    right.annotate("HR858 removed", xy=(1, values[1]), xytext=(1.6, .35),
                   arrowprops={"arrowstyle": "->", "color": "#555555"}, fontsize=9)
    right.set(xticks=range(6), xlabel="Number of largest-gain hosts removed",
              ylabel="Mean M2 − M0 difference", title="Influence diagnostic (descriptive)", ylim=(-.3, 1.4))
    fig.suptitle("Protected evaluation: uncertain average benefit, concentrated gains", fontsize=13)
    fig.text(.5, .02, "2,185 accepted timings on 151 planets. Influence curve keeps fitted parameters fixed.",
             ha="center", fontsize=9, color="#444444")
    fig.tight_layout(rect=[0, .06, 1, .91])
    out = ROOT / "results/final_review/figures"
    out.mkdir(parents=True, exist_ok=True)
    outputs = []
    for extension in ("png", "pdf"):
        path = out / f"primary_and_influence.{extension}"
        fig.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
        outputs.append(path)
    plt.close(fig)
    hashes = lambda paths: {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    (out / "receipt.json").write_text(json.dumps({"input_sha256": hashes([summary_path, curve_path]),
                                                 "script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                                                 "output_sha256": hashes(outputs)}, indent=2) + "\n")


if __name__ == "__main__":
    main()
