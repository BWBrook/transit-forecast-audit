"""Readers for the ExoClock DRB/DRC/DRD release files acquired from OSF.

Values are returned as published (rounded text converted to float). No release
publishes Cov(T0, P); callers must treat covariance as missing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class Ephemeris:
    planet: str
    t0_bjd_tdb: float
    sigma_t0_days: float
    period_days: float
    sigma_period_days: float
    flags: tuple[str, ...] = ()


def read_drb_ephemerides(path: str | Path) -> dict[str, Ephemeris]:
    """DRB `updated_ephemerides.txt`: tab-separated, 17 documented columns."""
    out = {}
    for line in Path(path).read_text().splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if len(f) != 17:
            raise ValueError(f"DRB row has {len(f)} columns: {line[:60]}")
        flags = tuple(name for name, v in (("nonlinear", f[14]), ("high_frequency_noise", f[15]))
                      if v.strip() == "True")
        out[f[0].strip()] = Ephemeris(f[0].strip(), float(f[1]), float(f[2]), float(f[3]),
                                      float(f[4]), flags)
    return out


def read_catalogue(path: str | Path) -> dict[str, Ephemeris]:
    """DRC/DRD `catalogue_of_ephemerides.txt`: header row, five columns."""
    lines = Path(path).read_text().splitlines()
    if not lines[0].startswith("Planet"):
        raise ValueError("unexpected catalogue header")
    out = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        f = line.split()
        if len(f) != 5:
            raise ValueError(f"catalogue row has {len(f)} fields: {line[:60]}")
        out[f[0]] = Ephemeris(f[0], *(float(x) for x in f[1:]))
    return out


@dataclass(frozen=True)
class MidTime:
    planet: str
    t_bjd_tdb: float
    sigma_days: float
    source: str
    record_id: str

    @property
    def tess_date(self) -> str | None:
        """UTC calendar date embedded in DRD space-record IDs ending `_TESS`."""
        m = re.search(r"_(\d{4}-\d{2}-\d{2})_TESS$", self.record_id)
        return m.group(1) if m else None


def read_mid_times(path: str | Path) -> list[MidTime]:
    """DRC/DRD `all_mid_time_data.txt`: Planet, Tmid, unc, source, ID.

    The DRC header omits the leading `Planet` label but its rows carry it.
    """
    lines = Path(path).read_text().splitlines()
    if not lines[0].lstrip().startswith(("Planet", "Tmid")):
        raise ValueError("unexpected mid-time header")
    out = []
    for line in lines[1:]:
        f = line.split()
        if not f:
            continue
        if len(f) != 5:
            raise ValueError(f"mid-time row has {len(f)} fields: {line[:60]}")
        out.append(MidTime(f[0], float(f[1]), float(f[2]), f[3], f[4]))
    return out


def host_of(planet: str) -> str:
    """Heuristic host label: strip a trailing planet letter or `.NN` suffix."""
    m = re.match(r"^(.*?)(\.\d+|[b-h])$", planet)
    return m.group(1) if m else planet


def residuals_without_covariance(eph: dict[str, Ephemeris], events: list[MidTime]):
    """Nearest-epoch O-C and the ExoClock IV Table 5 sigma (no covariance term).

    sigma_{O-C}^2 = sigma_Tmid^2 + sigma_T0^2 + (n * sigma_P)^2, reproducing the
    published Table 5 exactly for DRB and DRC (see results/pilot_v1).
    """
    t = np.array([e.t_bjd_tdb for e in events])
    s = np.array([e.sigma_days for e in events])
    t0 = np.array([eph[e.planet].t0_bjd_tdb for e in events])
    st0 = np.array([eph[e.planet].sigma_t0_days for e in events])
    p = np.array([eph[e.planet].period_days for e in events])
    sp = np.array([eph[e.planet].sigma_period_days for e in events])
    n = np.round((t - t0) / p)
    oc = t - (t0 + n * p)
    pred_sd = np.sqrt(st0**2 + (n * sp) ** 2)
    return n, oc, pred_sd, np.sqrt(s**2 + pred_sd**2)
