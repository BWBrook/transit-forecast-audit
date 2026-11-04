#!/usr/bin/env python3
"""Independent numerical audit of the committed T015 injection table.

This reads only committed development outputs. It reconstructs the accepted
phase and offset draws from the recorded RNG seed, quantifies flux-window reuse,
and compares uncertainty summaries at transit-parent, sector-product and host
levels. It does not read FITS flux or protected outcomes.
"""

from __future__ import annotations

import argparse
import copy
import csv
import hashlib
import json
from collections import defaultdict
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
WINDOW_MIN = 60.0
N_INJ = 12
SEED = 20261105


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def key_parent(row: dict[str, str], epoch_name: str) -> tuple[str, str, str]:
    return row["planet"], row["sector"], row[epoch_name]


def reconstruct_rng(
    events: list[dict[str, str]], injections: list[dict[str, str]], seed: int
) -> tuple[list[float], list[float], dict[str, int]]:
    """Replay exact accepted draws; rejected attempts are inferred from row matching."""
    timed = [row for row in events if row["status"] == "timed"]
    rng = np.random.default_rng(seed)
    exact_phase: list[float] = []
    exact_offset_d: list[float] = []
    position = 0
    rejected = 0
    parents_with_acceptance = set()

    for event in timed:
        parent = key_parent(event, "local_epoch")
        for _ in range(N_INJ):
            phase = float(rng.choice([rng.uniform(0.25, 0.40), rng.uniform(0.60, 0.75)]))
            state_after_phase = copy.deepcopy(rng.bit_generator.state)
            matches = (
                position < len(injections)
                and key_parent(injections[position], "host_epoch") == parent
                and round(phase, 3) == float(injections[position]["phase"])
            )
            if not matches:
                rejected += 1
                continue

            offset_d = float(rng.uniform(-15.0, 15.0) / 1440.0)
            if round(offset_d * 86400.0, 2) != float(injections[position]["injected_offset_s"]):
                rng.bit_generator.state = state_after_phase
                raise ValueError(
                    "RNG replay became ambiguous: a rounded phase matched but its offset did not"
                )
            exact_phase.append(phase)
            exact_offset_d.append(offset_d)
            parents_with_acceptance.add(parent)
            position += 1

    if position != len(injections):
        raise ValueError(f"RNG replay matched {position}/{len(injections)} injection rows")
    if len(exact_phase) != len(injections):
        raise AssertionError("accepted RNG draw count does not match injection table")

    all_parents = {key_parent(row, "local_epoch") for row in timed}
    return exact_phase, exact_offset_d, {
        "seed": seed,
        "timed_parent_transits": len(timed),
        "attempted": len(timed) * N_INJ,
        "accepted": len(injections),
        "rejected_by_pipeline_coverage": rejected,
        "parents_with_accepted_injections": len(parents_with_acceptance),
        "parents_with_zero_accepted_injections": len(timed) - len(parents_with_acceptance),
        "zero_acceptance_parent_keys": [
            "|".join(key) for key in sorted(all_parents - parents_with_acceptance)
        ],
    }


def interval_geometry(
    injections: list[dict[str, str]],
    shapes: list[dict[str, str]],
    phases: list[float],
) -> tuple[list[dict[str, object]], dict[str, object], list[bool]]:
    shape_by_product = {(r["planet"], r["sector"]): r for r in shapes}
    by_product: dict[tuple[str, str], list[int]] = defaultdict(list)
    for index, row in enumerate(injections):
        by_product[(row["planet"], row["sector"])].append(index)

    overlap_any = [False] * len(injections)
    product_rows: list[dict[str, object]] = []
    all_pair_fractions: list[float] = []
    total_interval_length = 0.0
    total_union_length = 0.0
    total_components = 0
    min_transit_clearance_min = float("inf")

    for product, indices in sorted(by_product.items()):
        shape = shape_by_product[product]
        period_d = float(shape["bls_period_d"])
        half_phase = (1.5 * float(shape["t14_min"]) + WINDOW_MIN) / (period_d * 1440.0)
        intervals = sorted(
            (
                int(injections[i]["host_epoch"]) + phases[i] - half_phase,
                int(injections[i]["host_epoch"]) + phases[i] + half_phase,
                i,
            )
            for i in indices
        )

        pair_fractions: list[float] = []
        union_length = 0.0
        components = 0
        current: list[float] | None = None
        for left_index, (left, right, row_index) in enumerate(intervals):
            for other_left, other_right, other_index in intervals[left_index + 1 :]:
                if other_left >= right:
                    break
                overlap = min(right, other_right) - max(left, other_left)
                if overlap > 0.0:
                    overlap_any[row_index] = True
                    overlap_any[other_index] = True
                    pair_fractions.append(overlap / (2.0 * half_phase))
            if current is None or left > current[1]:
                if current is not None:
                    union_length += current[1] - current[0]
                current = [left, right]
                components += 1
            else:
                current[1] = max(current[1], right)
        if current is not None:
            union_length += current[1] - current[0]

        nominal_length = len(indices) * 2.0 * half_phase
        clearances_min = [
            (min(phases[i], 1.0 - phases[i]) - half_phase) * period_d * 1440.0
            for i in indices
        ]
        min_transit_clearance_min = min(min_transit_clearance_min, min(clearances_min))
        total_interval_length += nominal_length
        total_union_length += union_length
        total_components += components
        all_pair_fractions.extend(pair_fractions)
        product_rows.append(
            {
                "planet": product[0],
                "sector": product[1],
                "n_injections": len(indices),
                "half_window_phase": half_phase,
                "half_window_min": half_phase * period_d * 1440.0,
                "overlapping_pairs": len(pair_fractions),
                "median_pair_overlap_fraction": float(np.median(pair_fractions)),
                "connected_union_components": components,
                "unique_over_nominal_support": union_length / nominal_length,
                "minimum_clearance_from_nominal_transit_min": min(clearances_min),
            }
        )

    summary = {
        "n_injections": len(injections),
        "n_overlapping_at_least_one_other_window": int(sum(overlap_any)),
        "fraction_overlapping_at_least_one_other_window": float(np.mean(overlap_any)),
        "overlapping_pairs": len(all_pair_fractions),
        "median_pair_overlap_fraction": float(np.median(all_pair_fractions)),
        "pair_overlap_fraction_q10_q90": [
            float(x) for x in np.quantile(all_pair_fractions, [0.10, 0.90])
        ],
        "connected_union_components": total_components,
        "unique_over_nominal_support": total_union_length / total_interval_length,
        "minimum_clearance_from_nominal_transit_min": min_transit_clearance_min,
    }
    return product_rows, summary, overlap_any


def cluster_key(row: dict[str, str], level: str) -> tuple[str, ...]:
    if level == "transit_parent":
        return row["planet"], row["sector"], row["host_epoch"]
    if level == "sector_product":
        return row["planet"], row["sector"]
    if level == "host_planet":
        return (row["planet"],)
    raise ValueError(level)


def bootstrap_level(
    injections: list[dict[str, str]], level: str, replicates: int, seed: int
) -> tuple[dict[str, object], list[dict[str, object]]]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in injections:
        grouped[cluster_key(row, level)].append(row)
    keys = sorted(grouped)
    counts = np.asarray([len(grouped[key]) for key in keys], dtype=float)
    z2 = np.asarray(
        [sum(float(row["z"]) ** 2 for row in grouped[key]) for key in keys], dtype=float
    )
    zw2 = np.asarray(
        [sum(float(row["z_white"]) ** 2 for row in grouped[key]) for key in keys], dtype=float
    )
    cluster_mean_z2 = z2 / counts
    cluster_mean_zw2 = zw2 / counts

    rng = np.random.default_rng(seed)
    sampled = rng.integers(0, len(keys), size=(replicates, len(keys)))
    sampled_n = counts[sampled].sum(axis=1)
    draw_z = np.sqrt(z2[sampled].sum(axis=1) / sampled_n)
    draw_zw = np.sqrt(zw2[sampled].sum(axis=1) / sampled_n)

    summary: dict[str, object] = {
        "n_clusters": len(keys),
        "cluster_size_min_median_max": [
            int(counts.min()),
            float(np.median(counts)),
            int(counts.max()),
        ],
        "row_weighted_rms_z_scaled": float(np.sqrt(z2.sum() / counts.sum())),
        "cluster_balanced_rms_z_scaled": float(np.sqrt(cluster_mean_z2.mean())),
        "row_weighted_rms_z_white": float(np.sqrt(zw2.sum() / counts.sum())),
        "cluster_balanced_rms_z_white": float(np.sqrt(cluster_mean_zw2.mean())),
        "row_weighted_bootstrap_rms_z_scaled_q025_q50_q975": [
            float(x) for x in np.quantile(draw_z, [0.025, 0.5, 0.975])
        ],
        "row_weighted_bootstrap_rms_z_white_q025_q50_q975": [
            float(x) for x in np.quantile(draw_zw, [0.025, 0.5, 0.975])
        ],
    }

    rows: list[dict[str, object]] = []
    for key, n, mean_z2, mean_zw2 in zip(keys, counts, cluster_mean_z2, cluster_mean_zw2):
        values = grouped[key]
        rows.append(
            {
                "level": level,
                "cluster": "|".join(key),
                "n_injections": int(n),
                "rms_z_scaled": float(np.sqrt(mean_z2)),
                "rms_z_white": float(np.sqrt(mean_zw2)),
                "mean_z_scaled": float(np.mean([float(r["z"]) for r in values])),
                "median_bias_s": float(
                    np.median([float(r["recovered_minus_injected_s"]) for r in values])
                ),
            }
        )
    return summary, rows


def parent_bias_bootstrap(
    injections: list[dict[str, str]], replicates: int, seed: int
) -> list[float]:
    grouped: dict[tuple[str, ...], np.ndarray] = defaultdict(list)
    for row in injections:
        grouped[cluster_key(row, "transit_parent")].append(
            float(row["recovered_minus_injected_s"])
        )
    values = [np.asarray(grouped[key], dtype=float) for key in sorted(grouped)]
    rng = np.random.default_rng(seed)
    draws = []
    for _ in range(replicates):
        sampled = rng.integers(0, len(values), size=len(values))
        draws.append(float(np.median(np.concatenate([values[i] for i in sampled]))))
    return [float(x) for x in np.quantile(draws, [0.025, 0.5, 0.975])]


def leave_one_out(injections: list[dict[str, str]], level: str) -> list[dict[str, object]]:
    keys = sorted({cluster_key(row, level) for row in injections})
    rows = []
    for key in keys:
        kept = [row for row in injections if cluster_key(row, level) != key]
        z = np.asarray([float(row["z"]) for row in kept])
        rows.append(
            {
                "level": level,
                "left_out": "|".join(key),
                "n_remaining": len(kept),
                "rms_z_scaled": float(np.sqrt(np.mean(z**2))),
            }
        )
    return rows


def exoclock_scale_bootstrap(
    injections: list[dict[str, str]],
    events_by_parent: dict[tuple[str, str, str], dict[str, str]],
    replicates: int,
    seed: int,
) -> list[float]:
    grouped: dict[tuple[str, ...], list[dict[str, str]]] = defaultdict(list)
    for row in injections:
        grouped[cluster_key(row, "transit_parent")].append(row)
    keys = sorted(grouped)
    counts = np.asarray([len(grouped[key]) for key in keys], dtype=float)
    z2 = np.asarray(
        [sum(float(row["z"]) ** 2 for row in grouped[key]) for key in keys], dtype=float
    )
    ratios = np.asarray(
        [
            float(events_by_parent[key]["sigma_min"])
            / float(events_by_parent[key]["exoclock_sigma_min"])
            for key in keys
        ]
    )
    rng = np.random.default_rng(seed)
    sampled = rng.integers(0, len(keys), size=(replicates, len(keys)))
    rms = np.sqrt(z2[sampled].sum(axis=1) / counts[sampled].sum(axis=1))
    joint = rms * np.median(ratios[sampled], axis=1)
    return [float(x) for x in np.quantile(joint, [0.025, 0.5, 0.975])]


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "results" / "t015")
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "t015_review")
    parser.add_argument("--bootstrap", type=int, default=100_000)
    parser.add_argument("--seed", type=int, default=SEED)
    args = parser.parse_args(argv)

    paths = {
        "events": args.input / "t015_events.csv",
        "injections": args.input / "t015_injections.csv",
        "products": args.input / "t015_products.csv",
        "shapes": args.input / "t015_shapes.csv",
        "summary": args.input / "t015_summary.json",
        "pipeline": ROOT / "scripts" / "t015_timing_pipeline.py",
    }
    events = read_csv(paths["events"])
    injections = read_csv(paths["injections"])
    shapes = read_csv(paths["shapes"])

    exact_phase, exact_offset_d, replay = reconstruct_rng(events, injections, args.seed)
    if any(not (0.25 <= p <= 0.40 or 0.60 <= p <= 0.75) for p in exact_phase):
        raise AssertionError("an accepted injection lies outside the specified phase bands")

    exact_products, exact_geometry, overlap_any = interval_geometry(
        injections, shapes, exact_phase
    )
    _, rounded_geometry, _ = interval_geometry(
        injections, shapes, [float(row["phase"]) for row in injections]
    )

    z = np.asarray([float(row["z"]) for row in injections])
    zw = np.asarray([float(row["z_white"]) for row in injections])
    bias = np.asarray([float(row["recovered_minus_injected_s"]) for row in injections])
    sigma = np.asarray([float(row["sigma_s"]) for row in injections])
    sigma_white = np.asarray([float(row["sigma_white_s"]) for row in injections])
    if np.max(np.abs(z - bias / sigma)) > 5e-3:
        raise AssertionError("recorded scaled z values do not reproduce from rounded columns")
    if np.max(np.abs(zw - bias / sigma_white)) > 5e-3:
        raise AssertionError("recorded white z values do not reproduce from rounded columns")

    cluster_summaries: dict[str, object] = {}
    cluster_rows: list[dict[str, object]] = []
    for index, level in enumerate(("transit_parent", "sector_product", "host_planet")):
        summary, rows = bootstrap_level(
            injections, level, args.bootstrap, args.seed + 1009 * index
        )
        cluster_summaries[level] = summary
        cluster_rows.extend(rows)

    events_by_parent = {
        key_parent(row, "local_epoch"): row for row in events if row["status"] == "timed"
    }
    parent_ratios = []
    for parent in sorted({cluster_key(row, "transit_parent") for row in injections}):
        event = events_by_parent[parent]
        parent_ratios.append(float(event["sigma_min"]) / float(event["exoclock_sigma_min"]))
    median_sigma_ratio = float(np.median(parent_ratios))
    all_event_ratios = [
        float(row["sigma_min"]) / float(row["exoclock_sigma_min"])
        for row in events
        if row["status"] == "timed" and row.get("exoclock_sigma_min")
    ]
    all_event_median_sigma_ratio = float(np.median(all_event_ratios))
    parent_interval = cluster_summaries["transit_parent"][
        "row_weighted_bootstrap_rms_z_scaled_q025_q50_q975"
    ]

    phase_low = z[np.asarray(exact_phase) < 0.5]
    phase_high = z[np.asarray(exact_phase) > 0.5]
    outliers = [
        {
            "planet": row["planet"],
            "sector": row["sector"],
            "host_epoch": row["host_epoch"],
            "phase_exact": exact_phase[i],
            "z": float(row["z"]),
            "overlaps_another_window": overlap_any[i],
        }
        for i, row in enumerate(injections)
        if abs(float(row["z"])) > 3.0
    ]

    result = {
        "review_scope": (
            "Committed development CSVs only; no FITS flux, network acquisition, or protected "
            "post-2025-11-18 outcome was opened"
        ),
        "command": f"python scripts/review_t015_injections.py --bootstrap {args.bootstrap}",
        "source_sha256": {str(path.relative_to(ROOT)): sha256(path) for path in paths.values()},
        "rng_replay": replay,
        "phase_placement": {
            "low_band_count": int(np.sum(np.asarray(exact_phase) < 0.5)),
            "high_band_count": int(np.sum(np.asarray(exact_phase) > 0.5)),
            "minimum_exact_phase": min(exact_phase),
            "maximum_exact_phase": max(exact_phase),
            "low_band_rms_z_scaled": float(np.sqrt(np.mean(phase_low**2))),
            "high_band_rms_z_scaled": float(np.sqrt(np.mean(phase_high**2))),
            "offset_replay_max_rounding_error_s": float(
                np.max(
                    np.abs(
                        np.asarray(exact_offset_d) * 86400.0
                        - np.asarray([float(row["injected_offset_s"]) for row in injections])
                    )
                )
            ),
        },
        "overlap_geometry_exact_rng": exact_geometry,
        "overlap_geometry_rounded_csv_sensitivity": rounded_geometry,
        "point_estimates": {
            "n_injections": len(injections),
            "mean_z_scaled": float(np.mean(z)),
            "rms_z_scaled": float(np.sqrt(np.mean(z**2))),
            "rms_z_white": float(np.sqrt(np.mean(zw**2))),
            "median_bias_s": float(np.median(bias)),
            "coverage_abs_z_lt_1_2_3": [float(np.mean(np.abs(z) < k)) for k in (1, 2, 3)],
            "n_abs_z_gt_3": int(np.sum(np.abs(z) > 3.0)),
        },
        "cluster_comparisons": cluster_summaries,
        "parent_transit_bootstrap_median_bias_q025_q50_q975_s": parent_bias_bootstrap(
            injections, args.bootstrap, args.seed
        ),
        "leave_one_host_out": leave_one_out(injections, "host_planet"),
        "leave_one_product_out": leave_one_out(injections, "sector_product"),
        "exoclock_scale_arithmetic": {
            "median_ours_over_exoclock_sigma_among_injection_parents": median_sigma_ratio,
            "median_ours_over_exoclock_sigma_all_27_events": all_event_median_sigma_ratio,
            "all_event_median_ratio_times_rms_z_scaled": all_event_median_sigma_ratio
            * float(np.sqrt(np.mean(z**2))),
            "fixed_all_event_ratio_times_parent_bootstrap_q025_q50_q975": [
                all_event_median_sigma_ratio * float(value) for value in parent_interval
            ],
            "joint_parent_bootstrap_ratio_and_rms_q025_q50_q975": exoclock_scale_bootstrap(
                injections, events_by_parent, args.bootstrap, args.seed
            ),
            "reported_0.96_1.29_interval_has_no_committed_generator": True,
        },
        "three_abs_z_gt_3_rows": outliers,
        "interpretation_limits": [
            "The 26 clusters are parent transits, not 26 independent host stars; there are four hosts and five sector products.",
            "The row-weighted point estimate targets accepted injection placements and gives more weight to parent transits with more accepted attempts.",
            "The known injected shape is the same fitted shape used for recovery, so the experiment does not propagate shape uncertainty, spot crossings, or model misspecification.",
            "Beta and reduced-chi-square scaling are estimated from the same injected window used for timing; this validates that self-scaled procedure conditionally, not a transferable catalogue-wide multiplier.",
            "Nonparametric bootstrap intervals with four hosts or five products are too discrete for reliable population inference.",
        ],
    }

    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "injection_overlap_by_product.csv", exact_products)
    write_csv(args.output / "injection_cluster_summary.csv", cluster_rows)
    (args.output / "injection_review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["point_estimates"], indent=2))
    print(json.dumps(result["overlap_geometry_exact_rng"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
