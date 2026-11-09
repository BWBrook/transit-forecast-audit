"""D073 adjudication of the T017 review triggers.

Reads saved T017 products, the frozen accepted outcomes and the separate
C050/T017-adjudication checker runs; opens no photometry. Writes
results/independent_validation/t017_adjudication/.

1. Re-pairs frozen and independent timings with a gated assignment (cost
   capped at P/4 before the Hungarian step). The saved T017 comparison pairs
   on raw absolute distance, which has tied optima that shift whole trains by
   one cycle and then discard every shifted pair at the P/4 gate.
2. For each frozen timing still unpaired, records the independent window
   status and whether the other flux route timed it.
3. Classifies same-period residual signals by phase offset (secondary eclipse
   at phase 0.5 versus a duplicate train).
4. Tabulates HR858b three ways: frozen, C050 checker, T017 checker (gated).
"""
import csv
import gzip
import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT = Path(__file__).resolve().parents[1]
T017 = ROOT / "results/independent_validation/t017"
OUT = ROOT / "results/independent_validation/t017_adjudication"
FLUXES = ("PDCSAP_FLUX", "SAP_FLUX")


def read(path):
    with (gzip.open(path, "rt") if path.suffix == ".gz" else path.open()) as handle:
        return list(csv.DictReader(handle))


def pair(ref_tc, ind_tc, period, gated):
    if len(ref_tc) == 0 or len(ind_tc) == 0:
        return []
    distance = np.abs(np.asarray(ref_tc)[:, None] - np.asarray(ind_tc)[None, :])
    cost = np.where(distance < period / 4, distance, 1e6) if gated else distance
    rows, cols = linear_sum_assignment(cost)
    return [(int(i), int(j)) for i, j in zip(rows, cols) if distance[i, j] < period / 4]


def checker_pairs(summary_path):
    summary = json.loads(summary_path.read_text())
    return {column: {round(p["frozen_tc"], 6): p["diff_min"] for p in block["pairs"]}
            for column, block in summary["comparison_with_frozen"].items()}


def main():
    design = json.loads((ROOT / "configs/independent_validation/t017_design.json").read_text())
    primary = read(ROOT / "results/final_primary/accepted_outcomes.csv")
    development = read(ROOT / "results/outcomes/t015v3/outcomes.csv.gz")
    accepted = {r["window_event_id"] for r in read(ROOT / "results/prefreeze/attempt_ledger_development.csv.gz")
                if r["status"] == "accepted"}
    references = defaultdict(list)
    for row in primary + [r for r in development if r["event_id"] in accepted]:
        references[row["planet"], int(row["sector"])].append(row)
    hints = {c["planet"]: c["period_hint_d"] for c in design["cases"]}
    categories = defaultdict(list)
    for case in design["cases"]:
        for product in case["products"]:
            categories[case["planet"], product["sector"]].append(case["category"])

    products, unpaired, residual_signals, gated_diff = [], [], [], {}
    for (planet, sector), cats in sorted(categories.items()):
        result = json.loads((T017 / f"{planet}_S{sector}.json").read_text())
        ref = references[planet, sector]
        period = hints[planet]
        timed_by_route = {}
        for column in FLUXES:
            flux = result.get("fluxes", {}).get(column, {})
            windows = flux.get("transits", [])
            timed = [w for w in windows if w.get("status") == "timed"]
            timed_by_route[column] = timed
            ref_tc = [float(r["tc_bjd_tdb"]) for r in ref]
            ind_tc = [w["tc_bjd_tdb"] for w in timed]
            saved = pair(ref_tc, ind_tc, period, gated=False)
            gated = pair(ref_tc, ind_tc, period, gated=True)
            diffs = [(ind_tc[j] - ref_tc[i]) * 1440 for i, j in gated]
            gated_diff.update({(ref[i]["event_id"], column): d for d, (i, _) in zip(diffs, gated)})
            large = sum(abs(d) > max(10.0, 3 * float(ref[i]["sigma_s"]) / 60) for d, (i, _) in zip(diffs, gated))
            if ref:
                products.append({
                    "planet": planet, "sector": sector, "categories": ";".join(cats), "flux": column,
                    "frozen_timings": len(ref), "independent_timed": len(timed),
                    "paired_saved_rule": len(saved), "paired_gated": len(gated),
                    "median_abs_diff_min": round(float(np.median(np.abs(diffs))), 3) if diffs else "",
                    "max_abs_diff_min": round(float(np.max(np.abs(diffs))), 3) if diffs else "",
                    "large_discrepancies": int(large),
                    "unpaired_fraction_gated": round(1 - len(gated) / len(ref), 4)})
            for i, r in enumerate(ref):
                if i in {p[0] for p in gated}:
                    continue
                tc = float(r["tc_bjd_tdb"])
                near = [w for w in windows if abs(w["window_centre_btjd"] + 2457000 - tc) < period / 4]
                unpaired.append({"planet": planet, "sector": sector, "flux": column, "event_id": r["event_id"],
                                 "frozen_sigma_min": round(float(r["sigma_s"]) / 60, 3),
                                 "independent_window_status": near[0]["status"] if near else "no_window"})
            selected = flux.get("selected_signal")
            signals = flux.get("signals", [])
            if selected is None or not signals:
                continue
            target = signals[selected]
            for k, s in enumerate(signals):
                if k == selected:
                    continue
                ratio = s["period_d"] / target["period_d"]
                if abs(ratio - round(ratio)) > 0.01 or round(ratio) != 1:
                    continue
                phase = ((s["epoch_btjd"] - target["epoch_btjd"]) / target["period_d"]) % 1.0
                residual_signals.append({
                    "planet": planet, "sector": sector, "flux": column, "signal": k,
                    "period_ratio": round(ratio, 5), "phase_offset": round(phase, 4),
                    "depth_ppm": round(s["depth"] * 1e6, 1), "target_depth_ppm": round(target["depth"] * 1e6, 1),
                    "duration_d": s["duration_d"], "target_duration_d": target["duration_d"],
                    "class": ("secondary_eclipse_phase" if abs(phase - 0.5) < 0.02 else
                              "same_phase_residual" if min(phase, 1 - phase) < 0.02 else "other_phase")})
        for u in unpaired:
            if u["planet"] == planet and u["sector"] == sector and "other_route_timed" not in u:
                other = timed_by_route["SAP_FLUX" if u["flux"] == "PDCSAP_FLUX" else "PDCSAP_FLUX"]
                tc = next(float(r["tc_bjd_tdb"]) for r in ref if r["event_id"] == u["event_id"])
                hit = [w for w in other if abs(w["tc_bjd_tdb"] - tc) < period / 4]
                u["other_route_timed"] = bool(hit)
                u["other_route_diff_min"] = round((hit[0]["tc_bjd_tdb"] - tc) * 1440, 3) if hit else ""

    third = {}
    for planet, path in (("HR858b", ROOT / "results/independent_validation/hr858/summary.json"),
                         ("TOI-157b", ROOT / "results/independent_validation/toi157_s98/summary.json")):
        third[planet] = checker_pairs(path)
    for u in unpaired:
        tc = next(float(r["tc_bjd_tdb"]) for r in references[u["planet"], u["sector"]] if r["event_id"] == u["event_id"])
        route = third.get(u["planet"], {}).get(u["flux"], {})
        u["c050_checker_diff_min"] = round(route[round(tc, 6)], 3) if round(tc, 6) in route else ""

    t017 = gated_diff
    hr858 = []
    for r in [r for r in primary if r["planet"] == "HR858b"]:
        tc = round(float(r["tc_bjd_tdb"]), 6)
        row = {"event_id": r["event_id"], "frozen_sigma_min": round(float(r["sigma_s"]) / 60, 2)}
        for column in FLUXES:
            short = column.split("_")[0]
            row[f"c050_{short}_diff_min"] = round(third["HR858b"][column][tc], 2) if tc in third["HR858b"][column] else ""
            row[f"t017_{short}_diff_min"] = round(t017[r["event_id"], column], 2) if (r["event_id"], column) in t017 else ""
        hr858.append(row)

    OUT.mkdir(parents=True, exist_ok=True)
    for name, rows in (("gated_pairs.csv", products), ("unpaired_frozen_timings.csv", unpaired),
                       ("same_period_residual_signals.csv", residual_signals), ("hr858b_three_way.csv", hr858)):
        with (OUT / name).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    controls = sorted({p["planet"] for p in products if "seeded_control" in p["categories"]})
    summary = {
        "products_with_more_pairs_under_gating": [f'{p["planet"]}|S{p["sector"]}|{p["flux"]}: {p["paired_saved_rule"]}->{p["paired_gated"]}'
                                                   for p in products if p["paired_gated"] != p["paired_saved_rule"]],
        "unpaired_frozen_timings": len(unpaired),
        "unpaired_with_independent_window_timed": sum(u["independent_window_status"] == "timed" for u in unpaired),
        "unpaired_timed_by_other_route_or_c050_checker": sum(bool(u["other_route_timed"]) or u["c050_checker_diff_min"] != "" for u in unpaired),
        "control_unpaired": [u for u in unpaired if u["planet"] in controls],
        "control_large_discrepancies_gated": sum(p["large_discrepancies"] for p in products if p["planet"] in controls),
        "same_period_residual_signals": residual_signals,
        "opens_photometry": False,
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "same_period_residual_signals"}, indent=1))
    print(json.dumps(residual_signals, indent=1))


if __name__ == "__main__":
    main()
