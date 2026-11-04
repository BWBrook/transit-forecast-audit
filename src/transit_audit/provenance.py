"""Strict core ledger checks. Dates here are documented UTC calendar dates.

Production provenance needs the richer schema in docs/data_contract.md.
These checks establish necessary, not sufficient, independence conditions.
Exposure IDs identify the underlying target-specific photon samples/cadences,
not a whole multi-transit FITS file or a pipeline-dependent reduction name.
The selected ledger must resolve alternative reductions before splitting.
"""
from dataclasses import dataclass
from datetime import date
import math


def parse_date(text):
    value = date.fromisoformat(text)
    if value.isoformat() != text:
        raise ValueError("Use canonical YYYY-MM-DD dates")
    return value


@dataclass(frozen=True)
class Timing:
    measurement_id: str
    planet_id: str
    host_id: str
    event_id: str
    epoch: int
    midtime_bjd_tdb: float
    sigma_days: float
    observed_date: str
    available_date: str
    source_id: str
    exposure_ids: tuple[str, ...]
    time_system: str = "BJD_TDB"

    def __post_init__(self):
        for key in ("measurement_id", "planet_id", "host_id", "event_id", "source_id"):
            if not isinstance(getattr(self, key), str) or not getattr(self, key).strip():
                raise ValueError(f"{key} is required")
        if isinstance(self.epoch, bool) or not isinstance(self.epoch, int):
            raise ValueError("epoch must be a verified integer")
        if not math.isfinite(self.midtime_bjd_tdb) or not math.isfinite(self.sigma_days) or self.sigma_days <= 0:
            raise ValueError("Finite midpoint and positive uncertainty are required")
        if self.time_system != "BJD_TDB":
            raise ValueError("Only explicitly normalised BJD_TDB timings are accepted")
        if parse_date(self.available_date) < parse_date(self.observed_date):
            raise ValueError("A measured event cannot be available before observation")
        if not isinstance(self.exposure_ids, (tuple, list)) or not self.exposure_ids:
            raise ValueError("Exposure IDs must be a nonempty sequence of strings")
        if any(not isinstance(x, str) or not x.strip() for x in self.exposure_ids):
            raise ValueError("Exposure identities are required, not inferred from citations")
        if len(set(self.exposure_ids)) != len(self.exposure_ids):
            raise ValueError("Duplicate exposure identities within a timing")
        object.__setattr__(self, "exposure_ids", tuple(self.exposure_ids))


def chronological_split(timings, cutoff_date):
    """Track B split with documented availability, not event dates alone.

    Historical events released after cutoff are quarantined, not training data
    and not future outcomes. Same-day events are conservatively not future.
    """
    cutoff = parse_date(cutoff_date)
    training, outcomes, quarantined = [], [], []
    seen = set()
    seen_exposures = set()
    for timing in timings:
        if timing.measurement_id in seen:
            raise ValueError("Duplicate measurement ID")
        seen.add(timing.measurement_id)
        if seen_exposures.intersection(timing.exposure_ids):
            raise ValueError(
                "Repeated atomic exposure across timings: resolve alternative "
                "reductions or shared measurements before splitting"
            )
        seen_exposures.update(timing.exposure_ids)
        obs, avail = parse_date(timing.observed_date), parse_date(timing.available_date)
        if obs <= cutoff and avail <= cutoff:
            training.append(timing)
        elif obs > cutoff:
            outcomes.append(timing)
        else:
            quarantined.append(timing)
    assert_disjoint_exposures(training, outcomes)
    return training, outcomes, quarantined


def assert_disjoint_exposures(training, outcomes):
    old = {x for row in training for x in row.exposure_ids}
    new = {x for row in outcomes for x in row.exposure_ids}
    if old & new:
        raise ValueError("Training/outcome exposure overlap: independent evaluation invalid")


def assert_published_forecast_eligible(issued_date, training_cutoff_date, outcome,
                                     training_exposure_ids, lineage_verified):
    """Necessary Track A checks; caller must verify issue-date evidence upstream.

    An empty training-exposure sequence is accepted only with independently
    verified lineage. Its emptiness is not evidence of exposure independence.
    """
    issued = parse_date(issued_date)
    cutoff = parse_date(training_cutoff_date)
    if cutoff > issued:
        raise ValueError("Training cutoff cannot follow forecast issue date")
    if lineage_verified is not True:
        raise ValueError("Unknown exposure lineage cannot pass strict published-forecast audit")
    if not isinstance(training_exposure_ids, (tuple, list)) or any(
        not isinstance(x, str) or not x.strip() for x in training_exposure_ids
    ):
        raise ValueError("Training exposure IDs must be a list or tuple of nonempty strings")
    if parse_date(outcome.observed_date) <= issued:
        raise ValueError("Outcome must be observed after the public issue date")
    if set(training_exposure_ids) & set(outcome.exposure_ids):
        raise ValueError("Forecast and outcome share exposures")
