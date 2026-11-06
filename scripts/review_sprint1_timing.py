"""Independent table audit of D038-D039 and the linked D041 sizing claims.

This script reads only committed development-era CSV/JSON products.  It does
not import or execute the timing pipeline and does not open FITS files.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
from scipy.special import digamma


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "results" / "t015_validation"
DEFAULT_OUT = ROOT / "results" / "sprint1" / "timing_audit"
PRODUCTS = ("TESS-SPOC_200", "SPOC_120")
STRATA = ("all", "A_lt10", "B_10_11", "C_11_12", "D_12_13.5")
PHASES_PER_PRODUCT = 2
SEED = 20261106


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def as_bool(value: str | bool) -> bool:
    return value is True or value == "True"


def stable_seed(label: str) -> int:
    digest = hashlib.sha256(label.encode()).digest()
    return SEED + int.from_bytes(digest[:4], "big")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def weighted_median(values: list[float], weights: list[float]) -> float:
    order = np.argsort(np.asarray(values), kind="mergesort")
    x = np.asarray(values, float)[order]
    w = np.asarray(weights, float)[order]
    cutoff = 0.5 * float(w.sum())
    return float(x[np.searchsorted(np.cumsum(w), cutoff, side="left")])


def point_metrics(rows: list[dict], host_equal: bool) -> dict[str, float | int]:
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_host[row["host"]].append(row)
    if not rows:
        return {"hosts": 0, "n": 0}
    if host_equal:
        host_mse = [np.mean([float(row["z"]) ** 2 for row in values]) for values in by_host.values()]
        host_coverage = [np.mean([as_bool(row["cover95"]) for row in values]) for values in by_host.values()]
        values = [float(row["z"]) for row in rows]
        weights = [1.0 / len(by_host[row["host"]]) for row in rows]
        return {
            "hosts": len(by_host),
            "n": len(rows),
            "z_rms": float(math.sqrt(np.mean(host_mse))),
            "median_bias_sigma": weighted_median(values, weights),
            "cover95": float(np.mean(host_coverage)),
        }
    z = np.asarray([float(row["z"]) for row in rows])
    return {
        "hosts": len(by_host),
        "n": len(rows),
        "z_rms": float(np.sqrt(np.mean(z**2))),
        "median_bias_sigma": float(np.median(z)),
        "cover95": float(np.mean([as_bool(row["cover95"]) for row in rows])),
    }


def cluster_bootstrap(rows: list[dict], host_equal: bool, draws: int, seed: int) -> dict[str, list[float]]:
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_host[row["host"]].append(row)
    hosts = sorted(by_host)
    rng = np.random.default_rng(seed)
    sims = []
    for _ in range(draws):
        picked = rng.integers(0, len(hosts), len(hosts))
        sample = []
        if host_equal:
            for occurrence, index in enumerate(picked):
                for row in by_host[hosts[index]]:
                    sample.append({**row, "host": f"{occurrence}:{row['host']}"})
        else:
            for index in picked:
                sample.extend(by_host[hosts[index]])
        metrics = point_metrics(sample, host_equal)
        sims.append([metrics["z_rms"], metrics["median_bias_sigma"], metrics["cover95"]])
    sims_array = np.asarray(sims)
    return {
        "z_rms": [float(x) for x in np.percentile(sims_array[:, 0], [2.5, 97.5])],
        "median_bias_sigma": [float(x) for x in np.percentile(sims_array[:, 1], [2.5, 97.5])],
        "cover95": [float(x) for x in np.percentile(sims_array[:, 2], [2.5, 97.5])],
    }


def selected_frame(frame: list[dict], product: str, sample_set: str) -> list[dict]:
    rows = [row for row in frame if row.get("selection") == "selected" and row["set"] == sample_set]
    if product == "SPOC_120":
        rows = [row for row in rows if row.get("spoc_uri")]
    return rows


def attempt_denominator(
    frame: list[dict], products: list[dict], runs: list[dict], injections: list[dict], product: str, stratum: str
) -> dict:
    def in_group(row: dict) -> bool:
        return (
            row.get("product") == product
            and row.get("flux") == "pdcsap"
            and row.get("set") == "validation"
            and (stratum == "all" or row.get("stratum") == stratum)
        )

    selected = [
        row
        for row in selected_frame(frame, product, "validation")
        if stratum == "all" or row["stratum"] == stratum
    ]
    product_rows = [row for row in products if in_group(row)]
    run_rows = [row for row in runs if in_group(row)]
    injection_rows = [row for row in injections if in_group(row)]
    timed = [row for row in injection_rows if row["status"] == "timed"]
    product_failed = sum(row["status"] != "ok" for row in product_rows)
    run_ok = sum(row["status"] == "ok" for row in run_rows)
    run_bls_failed = sum(row["status"] == "bls_injected_not_recovered" for row in run_rows)
    run_dropped = sum(row["status"] == "dropped_window_overlap" for row in run_rows)
    edge = sum("edge" in row.get("flags", "").split(";") for row in timed)
    coverage_excluded = sum(row["status"] == "excluded_coverage" for row in injection_rows)
    planned_runs = PHASES_PER_PRODUCT * len(selected)
    absent_after_product_failure = planned_runs - len(run_rows)
    mixed_denominator = len(product_rows) + len(run_rows)
    return {
        "product": product,
        "stratum": stratum,
        "selected_product_attempts": len(selected),
        "product_records": len(product_rows),
        "product_identification_failed": product_failed,
        "planned_injection_runs": planned_runs,
        "runs_absent_after_product_failure": absent_after_product_failure,
        "runs_recorded": len(run_rows),
        "runs_ok": run_ok,
        "runs_bls_failed": run_bls_failed,
        "runs_dropped_window_overlap": run_dropped,
        "recovered_window_records": len(injection_rows),
        "timed_windows": len(timed),
        "coverage_excluded_windows": coverage_excluded,
        "edge_flagged_timed_windows": edge,
        "hosts_with_timed_windows": len({row["host"] for row in timed}),
        "reported_mixed_failure_rate": (product_failed + run_bls_failed + edge) / mixed_denominator
        if mixed_denominator
        else float("nan"),
        "product_identification_failure_rate": product_failed / len(selected) if selected else float("nan"),
        "conditional_run_bls_failure_rate": run_bls_failed / (run_ok + run_bls_failed)
        if run_ok + run_bls_failed
        else float("nan"),
        "planned_run_non_success_rate": (planned_runs - run_ok) / planned_runs if planned_runs else float("nan"),
        "conditional_window_coverage_exclusion_rate": coverage_excluded / len(injection_rows)
        if injection_rows
        else float("nan"),
        "selected_host_timed_fraction": len({row["host"] for row in timed}) / len(selected)
        if selected
        else float("nan"),
        "event_level_end_to_end_denominator_available": False,
    }


def one_way_icc(rows: list[dict], group_key, value_key) -> dict[str, float | int]:
    groups: dict[object, list[float]] = defaultdict(list)
    for row in rows:
        groups[group_key(row)].append(float(value_key(row)))
    k = len(groups)
    n = sum(len(values) for values in groups.values())
    grand = sum(sum(values) for values in groups.values()) / n
    ss_between = sum(len(values) * (float(np.mean(values)) - grand) ** 2 for values in groups.values())
    ss_within = sum(sum((value - float(np.mean(values))) ** 2 for value in values) for values in groups.values())
    ms_between = ss_between / (k - 1)
    ms_within = ss_within / (n - k)
    n0 = (n - sum(len(values) ** 2 for values in groups.values()) / n) / (k - 1)
    raw = (ms_between - ms_within) / (ms_between + (n0 - 1) * ms_within)
    return {"groups": k, "n": n, "icc_raw": raw, "icc_truncated_at_zero": max(0.0, raw)}


def dependence_audit(injections: list[dict]) -> list[dict]:
    timed = [row for row in injections if row["status"] == "timed" and row["flux"] == "pdcsap"]
    out = []
    for product in PRODUCTS:
        rows = [row for row in timed if row["product"] == product]
        for level, key in (
            ("host", lambda row: row["host"]),
            ("run", lambda row: (row["host"], row["phase"])),
        ):
            for metric, value in (
                ("z", lambda row: row["z"]),
                ("z_squared", lambda row: float(row["z"]) ** 2),
            ):
                out.append({"product": product, "level": level, "metric": metric, **one_way_icc(rows, key, value)})
    return out


def matching_and_removal_audit(products: list[dict], real: list[dict], injections: list[dict]) -> dict:
    product_map = {
        (row["host"], row["product"], row["flux"]): row for row in products if row["status"] == "ok"
    }
    timed = [row for row in injections if row["status"] == "timed"]
    ratios = []
    for row in timed:
        product = product_map[(row["host"], row["product"], row["flux"])]
        half_s = 1.5 * float(product["t14_min"]) * 60 + 3600
        ratios.append(abs(float(row["err_s"])) / half_s)
    duplicate_local_epochs = 0
    by_run: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in injections:
        by_run[(row["host"], row["product"], row["flux"], row["phase"])].append(row)
    for rows in by_run.values():
        epochs = [row["local_epoch"] for row in rows]
        duplicate_local_epochs += len(epochs) - len(set(epochs))

    real_by_product: dict[tuple[str, ...], list[dict]] = defaultdict(list)
    for row in real:
        real_by_product[(row["host"], row["product"], row["flux"])].append(row)
    nominal_removed = []
    for key, rows in real_by_product.items():
        product = product_map.get(key)
        if product is None:
            continue
        half_s = 1.5 * float(product["t14_min"]) * 60 + 3600
        expected_cadences = len(rows) * 2 * half_s / float(product["exp_s"])
        nominal_removed.append(expected_cadences / int(product["n_cadences"]))
    return {
        "timed_matches": len(timed),
        "max_abs_error_over_window_half_width": max(ratios),
        "matches_beyond_one_window_half_width": sum(value > 1 for value in ratios),
        "duplicate_recovered_local_epochs_within_run": duplicate_local_epochs,
        "truth_identifier_recorded": False,
        "truth_time_recorded": False,
        "match_distance_recorded_directly": False,
        "one_to_one_truth_matching_verifiable": False,
        "nominal_real_window_cadence_fraction_quantiles": {
            label: float(value)
            for label, value in zip(
                ("min", "q25", "median", "q75", "max"), np.percentile(nominal_removed, [0, 25, 50, 75, 100])
            )
        },
        "no_removal_control_in_committed_tables": True,
    }


def fit_log_mse_model(by_host: dict[str, list[dict]], bias_correct: bool = False) -> dict:
    hosts = sorted(by_host)
    x = np.asarray([float(by_host[host][0]["tmag"]) - 11 for host in hosts])
    n = np.asarray([len(by_host[host]) for host in hosts])
    mse = np.asarray([np.mean([float(row["z"]) ** 2 for row in by_host[host]]) for host in hosts])
    y = np.log(mse)
    if bias_correct:
        y = y - (digamma(n / 2) + np.log(2) - np.log(n))
    slope, intercept = np.polyfit(x, y, 1)
    endpoints = np.exp((intercept + slope * np.asarray([-2.0, 2.5])) / 2)
    return {
        "hosts": len(hosts),
        "min_injections_per_host": int(n.min()),
        "max_injections_per_host": int(n.max()),
        "slope_log_mean_z2_per_mag": float(slope),
        "predicted_typical_host_z_rms_tmag9": float(endpoints[0]),
        "predicted_typical_host_z_rms_tmag13_5": float(endpoints[1]),
        "event_pooled_z_rms": float(np.sqrt(np.mean([float(row["z"]) ** 2 for rows in by_host.values() for row in rows]))),
        "equal_host_z_rms": float(np.sqrt(np.mean(mse))),
        "geometric_mean_host_z_rms": float(np.exp(np.mean(np.log(mse)) / 2)),
    }


def tmag_model_audit(injections: list[dict], draws: int = 10_000) -> list[dict]:
    timed = [
        row
        for row in injections
        if row["status"] == "timed" and row["flux"] == "pdcsap"
    ]
    out = []
    for product in PRODUCTS:
        by_host: dict[str, list[dict]] = defaultdict(list)
        for row in timed:
            if row["product"] == product:
                by_host[row["host"]].append(row)
        base = fit_log_mse_model(by_host, False)
        corrected = fit_log_mse_model(by_host, True)
        hosts = sorted(by_host)
        x = np.asarray([float(by_host[host][0]["tmag"]) - 11 for host in hosts])
        n = np.asarray([len(by_host[host]) for host in hosts])
        mse = np.asarray([np.mean([float(row["z"]) ** 2 for row in by_host[host]]) for host in hosts])
        y = np.log(mse)
        correction = digamma(n / 2) + np.log(2) - np.log(n)
        rng = np.random.default_rng(stable_seed(f"tmag:{product}"))
        slopes = []
        endpoints = []
        corrected_endpoints = []
        for _ in range(draws):
            index = rng.integers(0, len(hosts), len(hosts))
            slope, intercept = np.polyfit(x[index], y[index], 1)
            slopes.append(slope)
            endpoints.append(np.exp((intercept + slope * np.asarray([-2.0, 2.5])) / 2))
            slope_c, intercept_c = np.polyfit(x[index], (y - correction)[index], 1)
            corrected_endpoints.append(np.exp((intercept_c + slope_c * np.asarray([-2.0, 2.5])) / 2))
        endpoints_array = np.asarray(endpoints)
        corrected_array = np.asarray(corrected_endpoints)
        out.append(
            {
                "product": product,
                **base,
                "slope_ci90_low": float(np.percentile(slopes, 5)),
                "slope_ci90_high": float(np.percentile(slopes, 95)),
                "tmag9_ci90_low": float(np.percentile(endpoints_array[:, 0], 5)),
                "tmag9_ci90_high": float(np.percentile(endpoints_array[:, 0], 95)),
                "tmag13_5_ci90_low": float(np.percentile(endpoints_array[:, 1], 5)),
                "tmag13_5_ci90_high": float(np.percentile(endpoints_array[:, 1], 95)),
                "chi_square_bias_corrected_tmag9": corrected["predicted_typical_host_z_rms_tmag9"],
                "chi_square_bias_corrected_tmag13_5": corrected["predicted_typical_host_z_rms_tmag13_5"],
                "chi_square_bias_corrected_tmag9_ci90_low": float(np.percentile(corrected_array[:, 0], 5)),
                "chi_square_bias_corrected_tmag9_ci90_high": float(np.percentile(corrected_array[:, 0], 95)),
                "chi_square_bias_corrected_tmag13_5_ci90_low": float(np.percentile(corrected_array[:, 1], 5)),
                "chi_square_bias_corrected_tmag13_5_ci90_high": float(np.percentile(corrected_array[:, 1], 95)),
            }
        )
    return out


def sizing_negative_control(injections: list[dict], outer: int = 1000, inner: int = 499) -> dict:
    rows = [
        row
        for row in injections
        if row["status"] == "timed" and row["flux"] == "pdcsap" and row["product"] == "TESS-SPOC_200"
    ]
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_host[row["host"]].append(row)
    empirical_n = np.asarray([len(values) for values in by_host.values()])
    rng = np.random.default_rng(stable_seed("a2-negative-control"))
    hosts = 120
    x = np.concatenate(
        [
            rng.uniform(-2.5, -1.0, 30),
            rng.uniform(-1.0, 0.0, 30),
            rng.uniform(0.0, 1.0, 30),
            rng.uniform(1.0, 2.5, 30),
        ]
    )
    pooled_cover = 0
    low_cover = 0
    high_cover = 0
    corrected_low_cover = 0
    corrected_high_cover = 0
    pooled_points = []
    endpoint_points = []
    corrected_points = []
    for _ in range(outer):
        n = rng.choice(empirical_n, hosts)
        mse = np.asarray([np.mean(rng.normal(size=int(count)) ** 2) for count in n])
        y = np.log(mse)
        correction = digamma(n / 2) + np.log(2) - np.log(n)
        slope, intercept = np.polyfit(x, y, 1)
        slope_c, intercept_c = np.polyfit(x, y - correction, 1)
        endpoint = np.exp((intercept + slope * np.asarray([-2.0, 2.5])) / 2)
        endpoint_c = np.exp((intercept_c + slope_c * np.asarray([-2.0, 2.5])) / 2)
        pooled_points.append(math.sqrt(float(np.mean(mse))))
        endpoint_points.append(endpoint)
        corrected_points.append(endpoint_c)

        index = rng.integers(0, hosts, (inner, hosts))
        mse_boot = mse[index]
        pooled_boot = np.sqrt(np.mean(mse_boot, axis=1))
        x_boot = x[index]
        for values, counter in ((y, "raw"), (y - correction, "corrected")):
            y_boot = values[index]
            x_mean = np.mean(x_boot, axis=1)
            y_mean = np.mean(y_boot, axis=1)
            boot_slope = np.sum((x_boot - x_mean[:, None]) * (y_boot - y_mean[:, None]), axis=1) / np.sum(
                (x_boot - x_mean[:, None]) ** 2, axis=1
            )
            boot_intercept = y_mean - boot_slope * x_mean
            low_endpoint = np.exp((boot_intercept - 2 * boot_slope) / 2)
            high_endpoint = np.exp((boot_intercept + 2.5 * boot_slope) / 2)
            low_interval = np.percentile(low_endpoint, [5, 95])
            high_interval = np.percentile(high_endpoint, [5, 95])
            if counter == "raw":
                low_cover += low_interval[0] <= 1 <= low_interval[1]
                high_cover += high_interval[0] <= 1 <= high_interval[1]
            else:
                corrected_low_cover += low_interval[0] <= 1 <= low_interval[1]
                corrected_high_cover += high_interval[0] <= 1 <= high_interval[1]
        pooled_interval = np.percentile(pooled_boot, [5, 95])
        pooled_cover += pooled_interval[0] <= 1 <= pooled_interval[1]
    endpoint_array = np.asarray(endpoint_points)
    corrected_array = np.asarray(corrected_points)
    return {
        "scenario": "iid standard-normal z; 120 hosts, 30 per Tmag stratum; injections-per-host sampled from D039 FFI",
        "outer_simulations": outer,
        "bootstrap_draws_per_simulation": inner,
        "nominal_interval": 0.90,
        "pooled_equal_host_z_rms_mean": float(np.mean(pooled_points)),
        "pooled_equal_host_z_rms_interval_coverage": pooled_cover / outer,
        "uncorrected_log_mse_tmag9_mean": float(np.mean(endpoint_array[:, 0])),
        "uncorrected_log_mse_tmag13_5_mean": float(np.mean(endpoint_array[:, 1])),
        "uncorrected_log_mse_tmag9_interval_coverage": low_cover / outer,
        "uncorrected_log_mse_tmag13_5_interval_coverage": high_cover / outer,
        "chi_square_bias_corrected_tmag9_mean": float(np.mean(corrected_array[:, 0])),
        "chi_square_bias_corrected_tmag13_5_mean": float(np.mean(corrected_array[:, 1])),
        "chi_square_bias_corrected_tmag9_interval_coverage": corrected_low_cover / outer,
        "chi_square_bias_corrected_tmag13_5_interval_coverage": corrected_high_cover / outer,
        "correction_scope": "diagnostic only; assumes independent zero-mean Gaussian z within host",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--bootstrap", type=int, default=10_000)
    args = parser.parse_args(argv)
    args.output.mkdir(parents=True, exist_ok=True)

    frame = read_csv(SOURCE / "frame_and_selection.csv")
    products = read_csv(SOURCE / "products.csv")
    runs = read_csv(SOURCE / "injection_runs.csv")
    injections = read_csv(SOURCE / "injections.csv")
    real = read_csv(SOURCE / "real_transits.csv")
    recorded = json.loads((SOURCE / "validation_summary.json").read_text())

    timed = [row for row in injections if row["status"] == "timed"]
    metric_rows = []
    comparisons = []
    for product in PRODUCTS:
        for stratum in STRATA:
            rows = [
                row
                for row in timed
                if row["product"] == product
                and row["flux"] == "pdcsap"
                and row["set"] == "validation"
                and (stratum == "all" or row["stratum"] == stratum)
            ]
            if not rows:
                continue
            event = point_metrics(rows, False)
            host = point_metrics(rows, True)
            event_ci = cluster_bootstrap(rows, False, args.bootstrap, stable_seed(f"event:{product}:{stratum}"))
            host_ci = cluster_bootstrap(rows, True, args.bootstrap, stable_seed(f"host:{product}:{stratum}"))
            row = {"product": product, "stratum": stratum}
            for prefix, values, intervals in (("event", event, event_ci), ("equal_host", host, host_ci)):
                row.update({f"{prefix}_{key}": value for key, value in values.items()})
                for key, interval in intervals.items():
                    row[f"{prefix}_{key}_ci95_low"] = interval[0]
                    row[f"{prefix}_{key}_ci95_high"] = interval[1]
            metric_rows.append(row)
            recorded_key = f"{product}|pdcsap|validation|{stratum}"
            if recorded_key in recorded["groups"]:
                original = recorded["groups"][recorded_key]
                comparisons.append(
                    {
                        "product": product,
                        "stratum": stratum,
                        "z_rms_difference": event["z_rms"] - original["z_rms"],
                        "median_bias_sigma_difference": event["median_bias_sigma"] - original["median_bias_sigma"],
                        "cover95_difference": event["cover95"] - original["cover95"],
                    }
                )

    attempts = [attempt_denominator(frame, products, runs, injections, product, stratum) for product in PRODUCTS for stratum in STRATA]
    dependence = dependence_audit(injections)
    match_removal = matching_and_removal_audit(products, real, injections)
    tmag = tmag_model_audit(injections)
    negative_control = sizing_negative_control(injections)

    report_total_timed = 2096
    actual_total_timed = sum(row["status"] == "timed" for row in injections)
    primary_event = next(row for row in metric_rows if row["product"] == "TESS-SPOC_200" and row["stratum"] == "all")
    primary_attempt = next(row for row in attempts if row["product"] == "TESS-SPOC_200" and row["stratum"] == "all")
    summary = {
        "scope": "committed D038-D039 development tables only; no FITS opened; no protected product accessed",
        "inputs_commit": "6931eb8",
        "decisive_results": {
            "reported_event_weighted_primary_reproduced": max(
                abs(row[key])
                for row in comparisons
                for key in ("z_rms_difference", "median_bias_sigma_difference", "cover95_difference")
            )
            < 1e-12,
            "primary_event_weighted_median_bias_sigma": primary_event["event_median_bias_sigma"],
            "primary_equal_host_median_bias_sigma": primary_event["equal_host_median_bias_sigma"],
            "primary_equal_host_bias_criterion_passes": abs(primary_event["equal_host_median_bias_sigma"]) < 0.1,
            "primary_reported_mixed_failure_rate": primary_attempt["reported_mixed_failure_rate"],
            "primary_planned_run_non_success_rate": primary_attempt["planned_run_non_success_rate"],
            "primary_selected_host_timed_fraction": primary_attempt["selected_host_timed_fraction"],
            "report_timed_injections": report_total_timed,
            "csv_timed_injections": actual_total_timed,
            "timed_injection_count_discrepancy": actual_total_timed - report_total_timed,
        },
        "matching_and_window_removal": match_removal,
        "dependence_icc": dependence,
        "a2_sizing_negative_control": negative_control,
        "limitations": [
            "Event-level end-to-end recovery cannot be reconstructed because truth attempts for failed, dropped, and product-failed runs are absent.",
            "Nearest matching lacks recorded truth identifiers/times, so one-to-one matching is not independently auditable from the table.",
            "The committed experiment has no same-phase no-removal control; the real-window removal effect is not identified.",
            "Signed-z ICC tests an additive group effect and cannot by itself establish absence of shared shape, scale, or photon dependence.",
            "The log host-mean-z-squared regression targets a geometric typical-host scale and has finite-event Jensen bias; it is not pooled RMS.",
        ],
    }

    write_csv(args.output / "pooled_and_stratum_metrics.csv", metric_rows)
    write_csv(args.output / "reported_point_comparison.csv", comparisons)
    write_csv(args.output / "attempt_denominators.csv", attempts)
    write_csv(args.output / "dependence_icc.csv", dependence)
    write_csv(args.output / "tmag_model_audit.csv", tmag)
    (args.output / "audit_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")

    source_paths = [
        SOURCE / name
        for name in (
            "frame_and_selection.csv",
            "products.csv",
            "injection_runs.csv",
            "injections.csv",
            "real_transits.csv",
            "validation_summary.json",
        )
    ] + [
        ROOT / "scripts" / "t015_stratified_validation.py",
        ROOT / "scripts" / "t015_confirmation_sizing.py",
        ROOT / "docs" / "t015_validation_design.md",
        ROOT / "docs" / "t015_validation_report.md",
        Path(__file__).resolve(),
    ]
    write_csv(
        args.output / "source_hashes.csv",
        [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in source_paths],
    )
    print(json.dumps(summary["decisive_results"], indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
