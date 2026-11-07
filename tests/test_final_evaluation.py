"""Synthetic contract test of the final-evaluation path (D060): fixed manifest -> terminal ledger -> acceptance -> adapter -> draw scorer."""

import argparse
import csv
import json
import sys
import tempfile
import unittest
from collections import namedtuple
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src"), str(ROOT / "tests")]
import acceptance as A  # noqa: E402
import final_evaluation as fe  # noqa: E402
from sprint1_outcome_adapter import score_outcomes  # noqa: E402
from test_prefreeze_contract import grid, i1  # noqa: E402

Eph = namedtuple("Eph", "t0_bjd_tdb period_days")
DRD = {"Pb": Eph(2460000.0, 3.0)}
DIAG_OK = {"status": "ok", "shape_rchi2": "1.1"}


def man(n, sector="60"):
    return {"event_id": f"Pb|S{sector}|DRD{n}", "observation_id": f"Pb|S{sector}|DRD{n}", "planet": "Pb",
            "host": "P", "sector": sector, "forecast_epoch": str(n)}


def fc(m, shift_s=30.0):
    return {"event_id": m["event_id"], "observation_id": m["observation_id"], "planet": "Pb", "host": "P",
            "release": "DRD", "predicted_bjd_tdb": str(2460000.0 + 3.0 * int(m["forecast_epoch"]) + shift_s / 86400),
            "forecast_variance_s2": "3600", "M0_b": "1", "M0_s_log_lambda": "0", "M1_b": "2", "M1_s_log_lambda": "0",
            "M2_b": "1", "M2_s_log_lambda": "2", "M3_b": "1.1", "M3_s_log_lambda": "1.9", "parameter_version": "test"}


class FinalPath(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())

    def test_missing_gaussian_certification_fails_closed(self):
        row = i1("a", 2460000.0, 60)
        row.pop("q025_s")
        row.pop("q975_s")
        self.assertEqual(A.accept(row, DIAG_OK), "gauss_certification_unresolved")
        inj = {"status": "timed", "sigma_s": "60", "gauss_ok": "True", "lo95_s": "117.6", "hi95_s": "117.6"}
        self.assertEqual(A.event_state(A.injection_row(inj)), A.ACCEPTED)
        self.assertEqual(A.event_state(A.injection_row({**inj, "lo95_s": ""})), "gauss_certification_unresolved")

    def test_manifest_ledger_scoring_and_draw_scorer(self):
        good, bad = grid(self.tmp / "g.json", 90), grid(self.tmp / "b.json", 90, truncate=True)
        manifest = [man(0), man(1), man(2), man(3), man(4), man(5, "61"), man(6, "62"), man(7)]
        w0 = i1("w0", 2460000.0, 60)
        w1 = i1("w1", 2460003.0, 90, gauss=False, grid_path=good)
        w2 = i1("w2", 2460006.0, 90, gauss=False, grid_path=bad)
        w3 = i1("w3", 2460009.0, 60)
        for k in ("q025_s", "q975_s"):
            w3[k] = ""
        w5 = {**i1("w5", 2460015.0, 60), "sector": "61"}
        windows = [w0, w1, w2, w3, w5, {**i1("w9", 2460030.0, 60)}]
        products = {("Pb", "60"): DIAG_OK, ("Pb", "61"): {"status": "read_failed: x"}}
        coverage = {"Pb|S60|DRD4": {"coverage_window_at_prediction": "0.9", "coverage_in_transit_at_prediction": "1"}}
        ledger, outside = fe.terminal_ledger(manifest, windows, products, coverage, DRD)
        status = {r["event_id"]: r["status"] for r in ledger}
        self.assertEqual(len(ledger), len(manifest))
        self.assertEqual(status, {"Pb|S60|DRD0": A.ACCEPTED, "Pb|S60|DRD1": A.ACCEPTED,
                                  "Pb|S60|DRD2": "likelihood_support_unresolved",
                                  "Pb|S60|DRD3": "gauss_certification_unresolved",
                                  "Pb|S60|DRD4": "unmatched_expected_event",
                                  "Pb|S61|DRD5": "product_read_failed", "Pb|S62|DRD6": "product_unavailable",
                                  "Pb|S60|DRD7": "unmatched_observability_unknown"})
        self.assertEqual([w["event_id"] for w in outside], ["w9"])

        outs, fcs = fe.scoring_inputs(ledger, windows, [fc(m) for m in manifest])
        self.assertEqual([o["event_id"] for o in outs], ["Pb|S60|DRD0", "Pb|S60|DRD1"])
        for name, rows in (("o.csv", outs), ("f.csv", fcs)):
            fe.write_csv(self.tmp / name, rows)
        dest = self.tmp / "s.csv"
        score_outcomes(argparse.Namespace(forecasts=str(self.tmp / "f.csv"), outcomes=str(self.tmp / "o.csv"),
                                          error_convention=fe.CONVENTION, outcome_scale=1.0, output=str(dest),
                                          max_tc_bjd=fe.era_limit("development")))
        with dest.open() as fh:
            adapter = {(r["method"], r["event_id"]): float(r["is95_standardised"]) for r in csv.DictReader(fh)}
        ev = fe.event_representation(outs, fcs)
        models = {m: {"b": float(fcs[0][m + "_b"]), "s_log_lambda": float(fcs[0][m + "_s_log_lambda"])}
                  for m in ("M0", "M1", "M2", "M3")}
        for m, mdl in models.items():
            sc = fe.score_events(ev, mdl)
            for i, e in enumerate(ev):
                self.assertAlmostEqual(sc[i], adapter[(m, e["event_id"])], delta=1e-9)

    def test_protected_era_refuses_without_access_record(self):
        if fe.ACCESS.exists():
            self.skipTest("access record present")
        with self.assertRaises(SystemExit):
            fe.era_limit("protected")

    def test_access_record_requires_affirmative_barry_decision(self):
        record = self.tmp / "access.json"
        valid = {"authorised_by": "Barry W. Brook", "decision": "authorise_protected_access",
                 "date": "2026-11-08", "decision_id": "synthetic-test-only"}
        invalid = [{**valid, "decision": "DO NOT OPEN"}, {**valid, "authorised_by": "Claude"},
                   {**valid, "date": "not-a-date"}, {**valid, "date": "20261108"},
                   {**valid, "decision_id": ""}, {k: v for k, v in valid.items() if k != "decision_id"}, []]
        with patch.object(fe, "ACCESS", record):
            for value in invalid:
                with self.subTest(record=value):
                    record.write_text(json.dumps(value))
                    with self.assertRaises(SystemExit):
                        fe.era_limit("protected")
            record.write_text("invalid json")
            with self.assertRaises(SystemExit):
                fe.era_limit("protected")
            record.write_text(json.dumps(valid))
            self.assertIsNone(fe.era_limit("protected"))

    def test_denied_record_keeps_measurement_guards(self):
        import final_measure as fm
        record = self.tmp / "access.json"
        record.write_text(json.dumps({"authorised_by": "Claude", "decision": "DO NOT OPEN", "date": "2026-11-08"}))
        limits = fm.tp.MAX_MJD, fm.tp.MAX_BTJD
        with patch.object(fe, "ACCESS", record):
            with self.assertRaises(SystemExit):
                fm.set_era("protected", self.tmp / "grids")
        self.assertEqual((fm.tp.MAX_MJD, fm.tp.MAX_BTJD), limits)


if __name__ == "__main__":
    unittest.main()
