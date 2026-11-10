"""Build the per-planet comparison table (Table 3) and its companion files.

Run from the repository root: .venv/bin/python scripts/build_table3.py
Reads only saved files; writes only results/reconstruction_displays/table3_*.
"""
import csv, gzip, hashlib, json, math, statistics as st
from collections import defaultdict, Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
B = ROOT / "data/derived/revision_stage0/benchmark"
IL = ROOT / "results/information_ledger"
OUT = ROOT / "results/reconstruction_displays"
ROSTER = ROOT / "results/sprint2/freeze_candidate/roster.csv"
STATUSES = ["accepted", "no_cadence_coverage_at_prediction", "excluded_coverage",
            "integration_unresolved", "edge", "product_id_failed",
            "likelihood_support_unresolved", "unmatched_expected_event"]


def rd(p):
    op = gzip.open if str(p).endswith(".gz") else open
    with op(p, "rt", newline="") as f:
        return list(csv.DictReader(f))


def sha(p):
    h = hashlib.sha256()
    h.update(Path(p).read_bytes())
    return h.hexdigest()


def fnum(x):
    return float(x) if x not in ("", None) else None


def fmt(x, nd=6):
    if x is None:
        return ""
    if isinstance(x, float):
        return f"{x:.{nd}g}" if abs(x) < 1e5 else f"{x:.7f}"
    return str(x)


def mean(v):
    return sum(v) / len(v) if v else None


rel = {}
for r in rd(IL / "release_planets.csv"):
    rel[(r["release"], r["planet"])] = r
know = {}
for r in rd(IL / "origin_knowledge.csv"):
    know[(r["release"], r["planet"])] = r
roster = {r["planet"]: r for r in rd(ROSTER)}

COLS = ["planet", "host", "cohort", "tic", "drd_t0_bjd_tdb", "drd_period_d",
        "sigma_t0_s", "sigma_p_s", "rho", "covariance_tier",
        "n_intended", "n_coverage_qualified_at_prediction", "n_accepted",
        "n_no_cadence_coverage_at_prediction", "n_excluded_coverage",
        "n_integration_unresolved", "n_edge", "n_product_id_failed",
        "n_likelihood_support_unresolved", "n_unmatched_expected_event",
        "median_abs_error_min", "max_abs_error_min",
        "m0_coverage95", "m2_coverage95", "mean_std_is95_diff_m2_minus_m0",
        "input_baseline_days", "last_input_bjd_tdb", "issued_line_z_rms",
        "issued_line_reduced_chi2_nminus2", "n_release_inputs",
        "new_in_drd_by_name", "drd_origin_ttv_flag", "pre_origin_ttv_literature_status",
        "ttv_warning_source", "current_archive_ttv_flag", "current_archive_flag_retrieved_utc"]


def build(sub, cohort):
    d = B / sub
    term = rd(d / "terminal_ledger.csv.gz")
    inten = rd(d / "intended_forecasts.csv.gz")
    accf = {r["event_id"]: r for r in rd(d / "accepted_forecasts.csv")}
    acco = {r["event_id"]: r for r in rd(d / "accepted_outcomes.csv")}
    scores = rd(d / "expected_scores.csv")
    assert set(accf) == set(acco), "forecast/outcome event mismatch"
    byp_t = defaultdict(list)
    for r in term:
        byp_t[r["planet"]].append(r)
    fc = {}
    for r in inten:
        fc.setdefault(r["planet"], r)
    errs = defaultdict(list)
    allerr = []
    for e, o in acco.items():
        f = accf[e]
        err = abs(float(o["tc_bjd_tdb"]) - float(f["predicted_bjd_tdb"])) * 1440.0
        errs[f["planet"]].append(err)
        allerr.append((f["planet"], err))
    cov = defaultdict(lambda: defaultdict(list))
    isv = defaultdict(lambda: defaultdict(dict))
    for r in scores:
        cov[r["planet"]][r["method"]].append(float(r["covered95"]))
        isv[r["planet"]][r["method"]][r["event_id"]] = float(r["is95_standardised"])
    rows = []
    for p in sorted(byp_t):
        t = byp_t[p]
        c = Counter(r["status"] for r in t)
        assert set(c) <= set(STATUSES), c
        f = fc[p]
        dr = rel.get(("DRD", p))
        assert dr is not None, p
        ro = roster.get(p)
        e = errs.get(p, [])
        if e:
            diffs = [isv[p]["M2"][k] - isv[p]["M0"][k] for k in isv[p]["M0"]]
            m0c, m2c, dif = mean(cov[p]["M0"]), mean(cov[p]["M2"]), mean(diffs)
        else:
            m0c = m2c = dif = None
        nrows = fnum(dr["valid_timing_rows"])
        new = not ((("DRB", p) in rel) or (("DRC", p) in rel))
        k = know[("DRD", p)]
        row = dict(
            planet=p, host=t[0]["host"], cohort=cohort, tic=ro["tic"] if ro else "",
            drd_t0_bjd_tdb=dr["t0_bjd_tdb"], drd_period_d=dr["period_days"],
            sigma_t0_s=fnum(f["sigma_t0_s"]), sigma_p_s=fnum(f["sigma_p_s"]), rho=fnum(f["rho"]),
            covariance_tier=f["covariance_tier"],
            n_intended=len(t),
            n_coverage_qualified_at_prediction=sum(r["coverage_ok_at_prediction"] == "True" for r in t),
            n_accepted=c["accepted"],
            **{"n_" + s: c[s] for s in STATUSES[1:]},
            median_abs_error_min=st.median(e) if e else None,
            max_abs_error_min=max(e) if e else None,
            m0_coverage95=m0c, m2_coverage95=m2c, mean_std_is95_diff_m2_minus_m0=dif,
            input_baseline_days=fnum(dr["input_baseline_days"]),
            last_input_bjd_tdb=dr["last_input_bjd_tdb"],
            issued_line_z_rms=fnum(dr["issued_line_z_rms"]),
            issued_line_reduced_chi2_nminus2=fnum(dr["issued_line_reduced_chi2_Nminus2"]),
            n_release_inputs=dr["valid_timing_rows"],
            new_in_drd_by_name="true" if new else "false",
            drd_origin_ttv_flag=k["origin_release_ttv_flag"].lower(),
            pre_origin_ttv_literature_status=k["pre_origin_literature_ttv_status"],
            ttv_warning_source=k["warning_source"],
            current_archive_ttv_flag=k["current_archive_ttv_flag"],
            current_archive_flag_retrieved_utc=k["current_label_retrieved_utc"],
        )
        rows.append(row)
    return rows, allerr, term, inten


def write(path, rows):
    with open(path, "w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(COLS)
        for r in rows:
            w.writerow([fmt(r[c]) for c in COLS])


core, core_err, core_term, core_int = build("primary", "core")
ext, ext_err, ext_term, ext_int = build("extension", "extension")
OUT.mkdir(parents=True, exist_ok=True)
write(OUT / "table3_planets.csv", core)
write(OUT / "table3_extension.csv", ext)

acc = [r for r in core if r["n_accepted"] > 0]
pooled = st.median([e for _, e in core_err])
mx_ex = max(e for p, e in core_err if p != "HR858b")
hr = next(r for r in core if r["planet"] == "HR858b")
checks = {
    "core_rows_156": (len(core), 156),
    "intended_sum_3103": (sum(r["n_intended"] for r in core), 3103),
    "accepted_sum_2185": (sum(r["n_accepted"] for r in core), 2185),
    "coverage_qualified_sum_2369": (sum(r["n_coverage_qualified_at_prediction"] for r in core), 2369),
    "accepted_among_coverage_qualified_2181": (sum(1 for r in core_term if r["status"] == "accepted" and r["coverage_ok_at_prediction"] == "True"), 2181),
    "planets_with_accepted_151": (len(acc), 151),
    "pooled_median_abs_error_min_1.1148": (round(pooled, 4), 1.1148),
    "max_abs_error_excl_HR858b_min_26.299": (round(mx_ex, 3), 26.299),
    "HR858b_intended_24": (hr["n_intended"], 24),
    "HR858b_accepted_16": (hr["n_accepted"], 16),
    "HR858b_max_error_min_approx_404": (round(hr["max_abs_error_min"], 1), 404),
    "planet_mean_M0_coverage95_0.90794": (round(mean([r["m0_coverage95"] for r in acc]), 5), 0.90794),
    "planet_mean_M2_coverage95_0.97576": (round(mean([r["m2_coverage95"] for r in acc]), 5), 0.97576),
    "extension_intended_291": (sum(r["n_intended"] for r in ext), 291),
    "extension_accepted_72": (sum(r["n_accepted"] for r in ext), 72),
    "extension_planets_with_accepted_5": (sum(1 for r in ext if r["n_accepted"] > 0), 5),
}
tol = {"HR858b_max_error_min_approx_404": 1.0}
results = {}
for k, (got, want) in checks.items():
    ok = abs(got - want) <= tol.get(k, 1e-9)
    results[k] = {"got": got, "expected": want, "pass": bool(ok)}

sel = sorted(core, key=lambda r: r["planet"])[:10]
EX = [("planet", "Planet"), ("n_intended", "Intended"), ("n_accepted", "Accepted"),
      ("median_abs_error_min", "Median abs error (min)"), ("max_abs_error_min", "Max abs error (min)"),
      ("sigma_t0_s", "σT0 (s)"), ("m0_coverage95", "M0 cov95"), ("m2_coverage95", "M2 cov95"),
      ("input_baseline_days", "Input baseline (d)"), ("pre_origin_ttv_literature_status", "TTV literature status")]
lines = ["| " + " | ".join(h for _, h in EX) + " |", "|" + "---|" * len(EX)]
for r in sel:
    lines.append("| " + " | ".join(fmt(r[c], 4) if r[c] not in ("",) else "unknown" for c, _ in EX) + " |")
md = ("# Table 3 excerpt (10 of 156 core planets; not the population)\n\n"
      "Declared selection rule: the first ten core planets in alphabetical planet-label order, "
      "without sorting on measured errors or acceptance. This illustrates the format and is not "
      "a representative scientific sample. All 156 planets, including the five without accepted "
      "timings, are retained in the full table; the full tables are "
      "`table3_planets.csv` (core) and `table3_extension.csv` (exploratory). Errors are accepted "
      "TESS mid-time minus DRD forecast; coverage is 95% coverage of measured time averaged within "
      "planet. Literature status values come from `origin_knowledge.csv`: 'not_searched' means "
      "unknown, not absent.\n\n" + "\n".join(lines) + "\n")
(OUT / "table3_excerpt.md").write_text(md)

inputs = [ROSTER, IL / "release_planets.csv", IL / "origin_knowledge.csv"]
for sub in ("primary", "extension"):
    for n in ("terminal_ledger.csv.gz", "intended_forecasts.csv.gz", "accepted_forecasts.csv",
              "accepted_outcomes.csv", "expected_scores.csv"):
        inputs.append(B / sub / n)
receipt = {
    "script": "scripts/build_table3.py",
    "inputs_sha256": {str(p.relative_to(ROOT)): sha(p) for p in inputs},
    "outputs_sha256": {n: sha(OUT / n) for n in ("table3_planets.csv", "table3_extension.csv", "table3_excerpt.md")},
    "excerpt_planets": [r["planet"] for r in sel],
    "checks": results,
    "all_checks_pass": all(v["pass"] for v in results.values()),
}
(OUT / "table3_receipt.json").write_text(json.dumps(receipt, indent=2) + "\n")
print(json.dumps({k: v for k, v in results.items() if not v["pass"]}, indent=1) or "")
print("all pass:", receipt["all_checks_pass"])
