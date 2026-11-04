"""Synthetic numerical audit of T015's timing-grid CDF convention; no photometry."""

import hashlib
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def quantiles(grid, density, trapezoid):
    if trapezoid:
        mass = .5*(density[1:]+density[:-1])*np.diff(grid)
        cdf = np.r_[0.,np.cumsum(mass)]
    else:
        cdf = np.cumsum(density)
    cdf /= cdf[-1]
    return np.interp([.15865,.5,.84135],cdf,grid)


def main():
    rows = []
    grid = np.arange(-3600,3600+2,2.)
    for sigma in (5.,10.,30.,60.):
        density = np.exp(-.5*(grid/sigma)**2)
        original = quantiles(grid,density,False)
        continuous = quantiles(grid,density,True)
        rows.append({"synthetic_only":True,"true_median_s":0.,"true_sigma_s":sigma,
                     "original_grid_median_s":float(original[1]),"trapezoid_grid_median_s":float(continuous[1]),
                     "original_sigma_s":float((original[2]-original[0])/2),
                     "trapezoid_sigma_s":float((continuous[2]-continuous[0])/2)})
    if any(abs(r["original_grid_median_s"]+1)>1e-9 or abs(r["trapezoid_grid_median_s"])>1e-9 for r in rows):
        raise AssertionError("Grid diagnostic did not reproduce the expected half-step displacement")
    report = {"synthetic_only":True,"light_curves_opened":0,"grid_seconds":2.,"rows":rows,
              "finding":"Cumulative point masses interpolated at node centers shift symmetric posteriors earlier by half a grid step",
              "scope":"Numerical quantile bias only; does not establish corrected real-data timing or physical bias",
              "pipeline_sha256":hashlib.sha256((ROOT/"scripts/t015_timing_pipeline.py").read_bytes()).hexdigest(),
              "script_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "command":"python scripts/review_t015_grid.py"}
    out = ROOT/"results/t015_review"
    out.mkdir(parents=True,exist_ok=True)
    (out/"grid_review.json").write_text(json.dumps(report,indent=2)+"\n")
    print(json.dumps(report,indent=2))


if __name__ == "__main__":
    main()
