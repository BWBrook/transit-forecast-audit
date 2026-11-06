"""Actual-design precision and stress simulations for sprint 1.

The simulations use only inspected development tables and metadata-only future
opportunities.  Fitted calibration parameters are held fixed: parameter-refit
uncertainty is reported by the forecast workflow, not duplicated here.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
import sprint1_forecast_core as core  # noqa: E402


OUT = ROOT / "results" / "sprint1" / "precision"
DERIVED = ROOT / "data" / "derived" / "sprint1"
INVENTORY = ROOT / "results" / "sprint1" / "inventory"
REFERENCE_TIMINGS = ROOT / "results" / "t015_validation" / "real_transits.csv"
SEED = 20261106
METHODS = core.METHODS
COMPARATORS = ("M1", "M2", "M3")


@dataclass
class Design:
    name: str
    events: list[dict]
    models: dict[str, dict]
    planet_names: list[str]
    host_names: list[str]
    planet_index: np.ndarray
    host_index: np.ndarray
    epoch: np.ndarray
    sigma_t0: np.ndarray
    sigma_p: np.ndarray
    rho: np.ndarray
    forecast_variance: np.ndarray
    sigma_y: np.ndarray
    weights: np.ndarray
    host_weights: np.ndarray
    half_widths: dict[str, np.ndarray]
    denominator: np.ndarray


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    keys = list(dict.fromkeys(key for row in rows for key in row))
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=keys, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def stable_seed(label: str) -> int:
    return SEED + int.from_bytes(hashlib.sha256(label.encode()).digest()[:4], "big")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def event_weights(planets: list[str]) -> np.ndarray:
    labels, inverse, counts = np.unique(np.asarray(planets), return_inverse=True, return_counts=True)
    return 1.0 / (len(labels) * counts[inverse])


def make_design(name: str, events: list[dict], models: dict[str, dict]) -> Design:
    events = sorted(events, key=lambda row: (row["planet"], float(row["forecast_epoch"]), row["event_id"]))
    planet_names = sorted({row["planet"] for row in events})
    host_names = sorted({row["host"] for row in events})
    planet_lookup = {name: index for index, name in enumerate(planet_names)}
    host_lookup = {name: index for index, name in enumerate(host_names)}
    planet_index = np.asarray([planet_lookup[row["planet"]] for row in events])
    host_index = np.asarray([host_lookup[row["host"]] for row in events])
    epoch = np.asarray([float(row["forecast_epoch"]) for row in events])
    sigma_t0 = np.asarray([float(row["sigma_t0_s"]) for row in events])
    sigma_p = np.asarray([float(row["sigma_p_s"]) for row in events])
    rho = np.asarray([float(row["rho"]) for row in events])
    forecast_variance = np.asarray([float(row["forecast_variance_s2"]) for row in events])
    sigma_y = np.asarray([float(row["sigma_s"]) * float(row.get("outcome_scale", 1.0)) for row in events])
    weights = event_weights([row["planet"] for row in events])
    host_weights = np.bincount(host_index, weights=weights, minlength=len(host_names))
    score_events = [
        {
            "forecast_variance_s2": forecast_variance[index],
            "sigma_s": sigma_y[index],
            "outcome_scale": 1.0,
            "residual_s": 0.0,
        }
        for index in range(len(events))
    ]
    half_widths = {}
    denominator = None
    for method in METHODS:
        scores = core.predictive_scores(score_events, models[method])
        half_widths[method] = np.asarray(scores["width95_minutes"]) * 30.0
        if method == "M0":
            denominator = np.asarray(scores["m0_predictive_sd_s"])
    assert denominator is not None
    if not np.isclose(weights.sum(), 1.0):
        raise ValueError("Planet-balanced event weights do not sum to one")
    for field in (sigma_t0, sigma_p, rho, forecast_variance, sigma_y, denominator):
        if not np.all(np.isfinite(field)):
            raise ValueError(f"Non-finite design field in {name}")
    return Design(
        name,
        events,
        models,
        planet_names,
        host_names,
        planet_index,
        host_index,
        epoch,
        sigma_t0,
        sigma_p,
        rho,
        forecast_variance,
        sigma_y,
        weights,
        host_weights,
        half_widths,
        denominator,
    )


def load_development_design(experiment: str) -> Design:
    directory = DERIVED / experiment / "a_1.087" / "c2"
    parameters = json.loads((directory / "parameters.json").read_text())
    rows = read_csv(directory / "events.csv")
    events = []
    numeric = (
        "forecast_epoch",
        "sigma_t0_s",
        "sigma_p_s",
        "rho",
        "forecast_variance_s2",
        "sigma_s",
        "outcome_scale",
    )
    for row in rows:
        event = dict(row)
        for key in numeric:
            event[key] = float(row[key])
        events.append(event)
    return make_design(experiment, events, parameters["models"])


def timing_sigma_references() -> tuple[list[dict], dict]:
    rows = [
        row
        for row in read_csv(REFERENCE_TIMINGS)
        if row["status"] == "timed" and row["product"] == "SPOC_120" and row["flux"] == "pdcsap"
    ]
    by_host: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        by_host[row["host"]].append(row)
    references = [
        {
            "host": host,
            "tmag": float(values[0]["tmag"]),
            "sigma_s": float(np.median([float(row["sigma_s"]) for row in values])),
            "transits": len(values),
        }
        for host, values in by_host.items()
    ]
    references.sort(key=lambda row: (row["tmag"], row["host"]))
    return references, {
        "reference_hosts": len(references),
        "reference_transits": len(rows),
        "tmag_min": min(row["tmag"] for row in references),
        "tmag_max": max(row["tmag"] for row in references),
        "baseline_reference_host_median_sigma_s": float(np.median([row["sigma_s"] for row in references])),
    }


def matched_sigma(tmag: float | None, references: list[dict], neighbours: int = 5) -> tuple[float, str]:
    if tmag is None or not math.isfinite(tmag):
        return float(np.median([row["sigma_s"] for row in references])), "global_median_missing_tmag"
    selected = sorted(references, key=lambda row: (abs(row["tmag"] - tmag), row["host"]))[:neighbours]
    status = f"nearest_{len(selected)}_tmag_median"
    if tmag < references[0]["tmag"] or tmag > references[-1]["tmag"]:
        status += "_extrapolated"
    return float(np.median([row["sigma_s"] for row in selected])), status


def _date_jd(value: str) -> float:
    return date.fromisoformat(value).toordinal() - date(1858, 11, 17).toordinal() + 2_400_000.5


def load_future_events(cohorts: set[str], sigma_multiplier: float = 1.0) -> tuple[list[dict], dict]:
    inventory = read_csv(INVENTORY / "planet_sector_product_inventory.csv")
    ephemerides, _, flags = core.load()
    drd = ephemerides["DRD"]
    covariance = core.covariance_rows()
    references, reference_summary = timing_sigma_references()
    strict_start = _date_jd("2025-11-19")
    events = []
    match_status = defaultdict(int)
    selected_planets = set()
    selected_hosts = set()
    selected_by_cohort: dict[str, set[str]] = defaultdict(set)
    for row in inventory:
        count = int(row.get("strict_a_opportunity_count") or 0)
        if (
            row.get("eligible_product_by_as_of") != "True"
            or count <= 0
            or row.get("cohort") not in cohorts
            or row["planet"] in flags["DRD"]
        ):
            continue
        if row["product"] not in ("SPOC_120", "TESS-SPOC_200"):
            raise ValueError(f"Unsupported eligible product {row['product']}")
        ephemeris = drd[row["planet"]]
        start_jd = max(_date_jd(row["conservative_start_utc"]), float(row["product_t_min_mjd"]) + 2_400_000.5, strict_start)
        end_jd = min(_date_jd(row["conservative_end_utc"]), float(row["product_t_max_mjd"]) + 2_400_000.5)
        first_epoch = math.ceil((start_jd - ephemeris.t0_bjd_tdb) / ephemeris.period_days)
        last_epoch = math.floor((end_jd - ephemeris.t0_bjd_tdb) / ephemeris.period_days)
        epochs = list(range(first_epoch, last_epoch + 1)) if last_epoch >= first_epoch else []
        if len(epochs) != count:
            raise ValueError(f"Opportunity count mismatch for {row['planet']} sector {row['sector']}")
        tmag = float(row["tmag"]) if row.get("tmag") not in (None, "") else None
        sigma, status = matched_sigma(tmag, references)
        sigma *= sigma_multiplier
        match_status[status] += len(epochs)
        rho = core.correlation("DRD", row["planet"], "c2", covariance)
        sigma_t0 = ephemeris.sigma_t0_days * 86400
        sigma_p = ephemeris.sigma_period_days * 86400
        for epoch in epochs:
            event_id = f"{row['planet']}|S{row['sector']}|{row['product']}|{epoch}"
            variance = float(core.forecast_variance(sigma_t0, sigma_p, epoch, rho))
            events.append(
                {
                    "event_id": event_id,
                    "planet": row["planet"],
                    "host": row["host"],
                    "forecast_epoch": epoch,
                    "sigma_t0_s": sigma_t0,
                    "sigma_p_s": sigma_p,
                    "rho": rho,
                    "forecast_variance_s2": variance,
                    "sigma_s": sigma,
                    "outcome_scale": 1.0,
                    "cohort": row["cohort"],
                    "sector": row["sector"],
                    "product": row["product"],
                    "tmag": tmag if tmag is not None else "",
                    "sigma_match_status": status,
                }
            )
        selected_planets.add(row["planet"])
        selected_hosts.add(row["host"])
        selected_by_cohort[row["cohort"]].add(row["planet"])
    identities = [event["event_id"] for event in events]
    if len(identities) != len(set(identities)):
        raise ValueError("Duplicate future opportunity event")
    summary = {
        "cohorts": sorted(cohorts),
        "planets": len(selected_planets),
        "hosts": len(selected_hosts),
        "opportunities": len(events),
        "planets_by_cohort": {cohort: len(selected_by_cohort[cohort]) for cohort in sorted(cohorts)},
        "sigma_multiplier": sigma_multiplier,
        "sigma_match_status_events": dict(sorted(match_status.items())),
        "assigned_sigma_s_min": float(min(event["sigma_s"] for event in events)),
        "assigned_sigma_s_median": float(np.median([event["sigma_s"] for event in events])),
        "assigned_sigma_s_max": float(max(event["sigma_s"] for event in events)),
        **reference_summary,
    }
    return events, summary


def selected_weights(mask: np.ndarray, planet_index: np.ndarray, n_planets: int) -> tuple[np.ndarray, np.ndarray]:
    rows, events = mask.shape
    weights = np.zeros((rows, events))
    active_planets = np.zeros(rows, int)
    for index in range(rows):
        counts = np.bincount(planet_index, weights=mask[index].astype(float), minlength=n_planets)
        active = counts > 0
        active_planets[index] = int(active.sum())
        if active_planets[index]:
            denominator = active_planets[index] * counts[planet_index]
            np.divide(1.0, denominator, out=weights[index], where=mask[index])
    return weights, active_planets


def draw_chunk(
    design: Design,
    rng: np.random.Generator,
    size: int,
    *,
    true_b: float,
    true_s: float,
    true_rho: str,
    outcome_sigma_ratio: float,
    shared_outcome_rho: float,
    influential_hosts: int,
    failure_selection: bool,
) -> tuple[np.ndarray, np.ndarray, dict]:
    planets = len(design.planet_names)
    hosts = len(design.host_names)
    z0 = rng.standard_normal((size, planets))
    zp = rng.standard_normal((size, planets))
    zlambda = rng.standard_normal((size, planets))
    scale = true_b * np.exp(0.5 * true_s * zlambda)
    sigma_t0 = np.zeros(planets)
    sigma_p = np.zeros(planets)
    rho = np.zeros(planets)
    for planet in range(planets):
        event = int(np.flatnonzero(design.planet_index == planet)[0])
        sigma_t0[planet] = design.sigma_t0[event]
        sigma_p[planet] = design.sigma_p[event]
        rho[planet] = design.rho[event]
    if true_rho == "minus1":
        rho.fill(-1.0)
    elif true_rho == "plus1":
        rho.fill(1.0)
    elif true_rho == "zero":
        rho.fill(0.0)
    elif true_rho != "assumed":
        raise ValueError(f"Unknown true-rho setting {true_rho}")
    epoch_error = scale * sigma_t0 * z0
    period_error = scale * sigma_p * (rho * z0 + np.sqrt(np.maximum(0.0, 1 - rho**2)) * zp)
    forecast_error = epoch_error[:, design.planet_index] + period_error[:, design.planet_index] * design.epoch

    independent = rng.standard_normal((size, len(design.events)))
    if shared_outcome_rho:
        shared = rng.standard_normal((size, hosts))
        measurement_z = (
            math.sqrt(1 - shared_outcome_rho) * independent
            + math.sqrt(shared_outcome_rho) * shared[:, design.host_index]
        )
    else:
        measurement_z = independent
    residual = forecast_error + outcome_sigma_ratio * design.sigma_y * measurement_z

    influential_names = []
    if influential_hosts:
        order = np.argsort(-design.host_weights, kind="stable")[:influential_hosts]
        shocks = rng.standard_normal((size, len(order)))
        for column, host in enumerate(order):
            selected = design.host_index == host
            residual[:, selected] += 6.0 * shocks[:, column, None] * design.denominator[selected]
            influential_names.append(design.host_names[host])

    if failure_selection:
        latent_z = np.divide(
            np.abs(forecast_error),
            np.sqrt(design.forecast_variance),
            out=np.zeros_like(forecast_error),
            where=design.forecast_variance > 0,
        )
        probability = np.where(latent_z <= 2.0, 0.95, 0.35)
        selected = rng.random(residual.shape) < probability
    else:
        selected = np.ones(residual.shape, bool)
    return residual, selected, {"influential_host_names": influential_names}


def summarise(values: np.ndarray) -> dict[str, float]:
    replicates = len(values)
    mean = float(np.mean(values))
    sd = float(np.std(values, ddof=1))
    return {
        "mean": mean,
        "sd": sd,
        "q025": float(np.percentile(values, 2.5)),
        "q975": float(np.percentile(values, 97.5)),
        "mean_mcse": sd / math.sqrt(replicates),
        "sd_mcse": sd / math.sqrt(2 * (replicates - 1)),
    }


def simulate(
    design: Design,
    scenario: dict,
    *,
    replicates: int,
    chunk_size: int,
) -> tuple[list[dict], dict]:
    rng = np.random.default_rng(stable_seed(f"{design.name}:{scenario['name']}"))
    delta_standardised = {method: [] for method in COMPARATORS}
    delta_minutes = {method: [] for method in COMPARATORS}
    coverage = {method: [] for method in METHODS}
    retained_events = []
    retained_planets = []
    retained_hosts = []
    effective_hosts = []
    detail = {}
    completed = 0
    while completed < replicates:
        size = min(chunk_size, replicates - completed)
        residual, selected, detail = draw_chunk(
            design,
            rng,
            size,
            true_b=scenario["true_b"],
            true_s=scenario["true_s"],
            true_rho=scenario.get("true_rho", "assumed"),
            outcome_sigma_ratio=scenario.get("outcome_sigma_ratio", 1.0),
            shared_outcome_rho=scenario.get("shared_outcome_rho", 0.0),
            influential_hosts=scenario.get("influential_hosts", 0),
            failure_selection=scenario.get("failure_selection", False),
        )
        if scenario.get("failure_selection", False):
            weights, active_planets = selected_weights(selected, design.planet_index, len(design.planet_names))
            active_hosts = np.zeros(size, int)
            kish = np.zeros(size)
            for index in range(size):
                host_weight = np.bincount(design.host_index, weights=weights[index], minlength=len(design.host_names))
                active_hosts[index] = int(np.sum(host_weight > 0))
                kish[index] = 1.0 / np.sum(host_weight**2) if np.sum(host_weight**2) else 0.0
        else:
            weights = np.broadcast_to(design.weights, residual.shape)
            active_planets = np.full(size, len(design.planet_names))
            active_hosts = np.full(size, len(design.host_names))
            kish = np.full(size, 1.0 / np.sum(design.host_weights**2))
        retained_events.extend(np.mean(selected, axis=1))
        retained_planets.extend(active_planets / len(design.planet_names))
        retained_hosts.extend(active_hosts)
        effective_hosts.extend(kish)

        scores = {}
        for method in METHODS:
            half = design.half_widths[method]
            interval_score = 2 * half + 40 * np.maximum(np.abs(residual) - half, 0)
            scores[method] = interval_score
            covered = np.abs(residual) <= half
            coverage[method].extend(np.sum(weights * covered, axis=1))
        for method in COMPARATORS:
            difference = scores[method] - scores["M0"]
            delta_standardised[method].extend(np.sum(weights * difference / design.denominator, axis=1))
            delta_minutes[method].extend(np.sum(weights * difference / 60.0, axis=1))
        completed += size

    rows = []
    for method in COMPARATORS:
        standardised = np.asarray(delta_standardised[method])
        minutes = np.asarray(delta_minutes[method])
        improved = standardised < 0
        standardised_summary = summarise(standardised)
        minute_summary = summarise(minutes)
        probability = float(np.mean(improved))
        rows.append(
            {
                "design": design.name,
                "scenario": scenario["name"],
                "method": method,
                "replicates": replicates,
                "events": len(design.events),
                "planets": len(design.planet_names),
                "hosts": len(design.host_names),
                "kish_effective_hosts": float(np.mean(effective_hosts)),
                "mean_retained_event_fraction": float(np.mean(retained_events)),
                "mean_retained_planet_fraction": float(np.mean(retained_planets)),
                "mean_retained_hosts": float(np.mean(retained_hosts)),
                "delta_standardised_mean": standardised_summary["mean"],
                "delta_standardised_sd": standardised_summary["sd"],
                "delta_standardised_q025": standardised_summary["q025"],
                "delta_standardised_q975": standardised_summary["q975"],
                "delta_standardised_mean_mcse": standardised_summary["mean_mcse"],
                "delta_standardised_sd_mcse": standardised_summary["sd_mcse"],
                "probability_delta_lt_zero": probability,
                "probability_mcse": math.sqrt(probability * (1 - probability) / replicates),
                "delta_minutes_mean": minute_summary["mean"],
                "delta_minutes_sd": minute_summary["sd"],
                "coverage95_m0_mean": float(np.mean(coverage["M0"])),
                "coverage95_method_mean": float(np.mean(coverage[method])),
            }
        )
    return rows, detail


def scenarios(models: dict[str, dict]) -> list[dict]:
    m1, m2, m3 = models["M1"], models["M2"], models["M3"]
    base = {"true_rho": "assumed", "outcome_sigma_ratio": 1.0, "shared_outcome_rho": 0.0, "influential_hosts": 0, "failure_selection": False}
    return [
        {**base, "name": "null_m0", "true_b": 1.0, "true_s": 0.0},
        {**base, "name": "scale_m1", "true_b": m1["b"], "true_s": 0.0},
        {**base, "name": "broad_m2", "true_b": 1.0, "true_s": m2["s_log_lambda"]},
        {**base, "name": "full_m3", "true_b": m3["b"], "true_s": m3["s_log_lambda"]},
        {**base, "name": "outcome_sigma_0.85", "true_b": 1.0, "true_s": m2["s_log_lambda"], "outcome_sigma_ratio": 0.85},
        {**base, "name": "outcome_sigma_1.25", "true_b": 1.0, "true_s": m2["s_log_lambda"], "outcome_sigma_ratio": 1.25},
        {**base, "name": "two_influential_hosts", "true_b": 1.0, "true_s": m2["s_log_lambda"], "influential_hosts": 2},
        {**base, "name": "shared_outcome_rho_0.30", "true_b": 1.0, "true_s": m2["s_log_lambda"], "shared_outcome_rho": 0.30},
        {**base, "name": "rho_true_zero", "true_b": 1.0, "true_s": 0.0, "true_rho": "zero"},
        {**base, "name": "rho_true_minus1", "true_b": 1.0, "true_s": 0.0, "true_rho": "minus1"},
        {**base, "name": "rho_true_plus1", "true_b": 1.0, "true_s": 0.0, "true_rho": "plus1"},
        {**base, "name": "failure_selected_m2", "true_b": 1.0, "true_s": m2["s_log_lambda"], "failure_selection": True},
    ]


def run_development(replicates: int, chunk_size: int) -> tuple[list[dict], dict]:
    rows = []
    details = {}
    for experiment in ("release_transfer", "chronological"):
        design = load_development_design(experiment)
        details[experiment] = {
            "events": len(design.events),
            "planets": len(design.planet_names),
            "hosts": len(design.host_names),
            "kish_effective_hosts": float(1.0 / np.sum(design.host_weights**2)),
            "models": design.models,
        }
        for scenario in scenarios(design.models):
            result, detail = simulate(design, scenario, replicates=replicates, chunk_size=chunk_size)
            rows.extend(result)
            if detail.get("influential_host_names"):
                details[experiment]["influential_host_names"] = detail["influential_host_names"]
    return rows, details


def run_future(replicates: int, chunk_size: int) -> tuple[list[dict], dict]:
    parameters = json.loads((DERIVED / "release_transfer" / "a_1.087" / "c2" / "parameters.json").read_text())
    rows = []
    design_summaries = {}
    future_scenarios = scenarios(parameters["models"])
    for sigma_multiplier in (0.5, 1.0, 2.0):
        for label, cohorts in (("core", {"core"}), ("union", {"core", "extension"})):
            events, summary = load_future_events(cohorts, sigma_multiplier)
            design_name = f"future_{label}_sigma_x{sigma_multiplier:g}"
            design = make_design(design_name, events, parameters["models"])
            opportunities_by_planet = np.bincount(design.planet_index)
            planet_hosts = {
                row["planet"]: row["host"]
                for row in events
            }
            planets_by_host = np.asarray(
                [sum(planet_hosts[planet] == host for planet in design.planet_names) for host in design.host_names]
            )
            design_summaries[design_name] = {
                **summary,
                "kish_effective_hosts": float(1.0 / np.sum(design.host_weights**2)),
                "opportunities_per_planet_min": int(opportunities_by_planet.min()),
                "opportunities_per_planet_median": float(np.median(opportunities_by_planet)),
                "opportunities_per_planet_max": int(opportunities_by_planet.max()),
                "multi_planet_hosts": int(np.sum(planets_by_host > 1)),
                "max_planets_per_host": int(planets_by_host.max()),
                "sigma_assumption": "median of five nearest D039 SPOC-120 PDCSAP host medians by Tmag, multiplied as labelled; no protected sigma used",
                "candidate_parameters": "release-transfer a=1.087 C2 fixed fit; transfer to pipeline-sigma convention is provisional",
            }
            for scenario in future_scenarios:
                if sigma_multiplier != 1.0 and scenario["name"] != "broad_m2":
                    continue
                result, detail = simulate(design, scenario, replicates=replicates, chunk_size=chunk_size)
                rows.extend(result)
                if detail.get("influential_host_names"):
                    design_summaries[design_name]["influential_host_names"] = detail["influential_host_names"]
    return rows, design_summaries


def r8_projection(future_rows: list[dict], inventory_summary: dict) -> dict:
    comparisons = []
    scenario_names = sorted(
        {
            row["scenario"]
            for row in future_rows
            if row["design"] in ("future_core_sigma_x1", "future_union_sigma_x1")
        }
    )
    for scenario in scenario_names:
        for method in COMPARATORS:
            core_row = next(
                row
                for row in future_rows
                if row["design"] == "future_core_sigma_x1" and row["scenario"] == scenario and row["method"] == method
            )
            union_row = next(
                row
                for row in future_rows
                if row["design"] == "future_union_sigma_x1" and row["scenario"] == scenario and row["method"] == method
            )
            ratio = union_row["delta_standardised_sd"] / core_row["delta_standardised_sd"]
            replicates = core_row["replicates"]
            comparisons.append(
                {
                    "scenario": scenario,
                    "method": method,
                    "core_sd": core_row["delta_standardised_sd"],
                    "union_sd": union_row["delta_standardised_sd"],
                    "se_reduction_percent": 100 * (1 - ratio),
                    "absolute_se_change_percent": 100 * abs(1 - ratio),
                    "se_reduction_ge_10_percent": 100 * (1 - ratio) >= 10,
                    "absolute_change_ge_10_percent": 100 * abs(1 - ratio) >= 10,
                    "ratio_mcse_approx": ratio / math.sqrt(replicates),
                }
            )
    core_planets = inventory_summary["core_eligible_planets_with_public_product"]
    extension_planets = inventory_summary["extension_eligible_planets_with_public_product"]
    increment = 100 * extension_planets / core_planets
    return {
        "gate_logic": "OR",
        "metadata_eligible_core_planets": core_planets,
        "metadata_eligible_extension_planets": extension_planets,
        "metadata_increment_over_core_percent": increment,
        "metadata_gate_ge_15_percent": increment >= 15,
        "projected_se_gate_ge_10_percent_by_scenario_method": comparisons,
        "decision": "extension clears the metadata-count arm; SE projections are conditional sensitivities, not required to rescue the gate",
        "qualification": "long-period and multi-planet extension systems remain unsupported until sprint 2 identification tests pass; core-versus-union SE compares different target populations",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replicates", type=int, default=4000)
    parser.add_argument("--chunk-size", type=int, default=100)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    if args.replicates < 1000 or args.chunk_size < 1:
        raise ValueError("Use at least 1000 replicates and a positive chunk size")
    args.output.mkdir(parents=True, exist_ok=True)

    development, development_designs = run_development(args.replicates, args.chunk_size)
    future, future_designs = run_future(args.replicates, args.chunk_size)
    inventory_summary = json.loads((INVENTORY / "inventory_summary.json").read_text())
    r8 = r8_projection(future, inventory_summary)
    scenario_records = scenarios(load_development_design("release_transfer").models)
    summary = {
        "replicates": args.replicates,
        "seed": SEED,
        "protected_outcomes_accessed": False,
        "light_curves_opened": False,
        "parameter_uncertainty": "not included; fixed fitted rules by design; parent host-refit analysis handles fit uncertainty",
        "development_designs": development_designs,
        "future_designs": future_designs,
        "r8": r8,
        "scenario_definitions": scenario_records,
        "interpretation": "Monte Carlo sampling distributions conditional on the recorded designs and stated truths; not astrophysical population probabilities",
        "future_union_scope": "core plus extension only; four inventory rows labelled unresolved (134 opportunities) are excluded",
    }
    write_csv(args.output / "development_precision.csv", development)
    write_csv(args.output / "future_design_precision.csv", future)
    (args.output / "precision_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    (args.output / "r8_projection.json").write_text(json.dumps(r8, indent=2, sort_keys=True) + "\n")

    sources = [
        Path(__file__).resolve(),
        ROOT / "tests" / "test_sprint1_precision.py",
        ROOT / "scripts" / "sprint1_forecast_core.py",
        ROOT / "scripts" / "forecast_variance_components.py",
        DERIVED / "release_transfer" / "a_1.087" / "c2" / "events.csv",
        DERIVED / "release_transfer" / "a_1.087" / "c2" / "parameters.json",
        DERIVED / "chronological" / "a_1.087" / "c2" / "events.csv",
        DERIVED / "chronological" / "a_1.087" / "c2" / "parameters.json",
        INVENTORY / "planet_sector_product_inventory.csv",
        INVENTORY / "inventory_summary.json",
        REFERENCE_TIMINGS,
    ]
    write_csv(
        args.output / "source_hashes.csv",
        [{"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in sources],
    )
    outputs = (
        "development_precision.csv",
        "future_design_precision.csv",
        "precision_summary.json",
        "r8_projection.json",
        "source_hashes.csv",
    )
    receipt = {
        "command": f".venv/bin/python scripts/sprint1_precision.py --replicates {args.replicates} --chunk-size {args.chunk_size}",
        "seed": SEED,
        "replicates": args.replicates,
        "chunk_size": args.chunk_size,
        "python": sys.version.split()[0],
        "numpy": np.__version__,
        "outputs": [
            {"path": f"results/sprint1/precision/{name}", "sha256": sha256(args.output / name)}
            for name in outputs
        ],
    }
    (args.output / "run_receipt.json").write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"development_rows": len(development), "future_rows": len(future), "r8": r8["decision"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
