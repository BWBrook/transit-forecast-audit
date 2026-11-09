import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t019_information_ledger import calendar_label, timing_statistics
from t019_external_metadata import date_candidate


class InformationLedgerTests(unittest.TestCase):
    def test_reduced_chi2_is_not_rms_sigma(self):
        e = SimpleNamespace(t0_bjd_tdb=2450000., period_days=2.)
        rows = [{"time": 2450000 + 2*n + r, "sigma": .01, "source": "synthetic"}
                for n,r in enumerate((.01, -.01, .02, -.02))]
        result = timing_statistics(e, rows)
        self.assertAlmostEqual(result["issued_line_chi2"], 10., places=5)
        self.assertAlmostEqual(result["issued_line_reduced_chi2_Nminus2"], 5., places=5)
        self.assertAlmostEqual(result["issued_line_z_rms"], (10/4)**.5, places=5)
        self.assertNotAlmostEqual(result["issued_line_z_rms"], result["issued_line_reduced_chi2_Nminus2"])

    def test_last_input_is_observation_not_parameter_pivot(self):
        e = SimpleNamespace(t0_bjd_tdb=2450000., period_days=1.)
        result = timing_statistics(e, [{"time": t,"sigma": .01,"source": "synthetic"}
                                       for t in (2450010.,2450008.,2450009.)])
        self.assertEqual(result["last_input_bjd_tdb"],2450010.)
        self.assertEqual(result["input_baseline_days"],2.)

    def test_invalid_uncertainty_is_explicit_and_dof_undefined(self):
        e = SimpleNamespace(t0_bjd_tdb=2450000., period_days=1.)
        result = timing_statistics(e,[{"time":2450000.,"sigma":0.,"source":"synthetic"},
                                       {"time":2450001.,"sigma":.1,"source":"synthetic"}])
        self.assertEqual(result["invalid_timing_rows"],1)
        self.assertIsNone(result["issued_line_reduced_chi2_Nminus2"])

    def test_calendar_formatter_does_not_relabel_as_utc(self):
        self.assertEqual(calendar_label(2451545.),"2000-01-01")
        self.assertEqual(calendar_label(2460313.5),"2024-01-04")

    def test_partial_dates_remain_curation_leads(self):
        self.assertEqual(date_candidate("2020","2021-10-27"),"metadata_pre_origin_source_unverified")
        self.assertEqual(date_candidate("2021","2021-10-27"),"boundary_or_unknown")
        self.assertEqual(date_candidate("2021-09","2021-10-27"),"metadata_pre_origin_source_unverified")
        self.assertEqual(date_candidate("2021-10-27","2021-10-27"),"metadata_on_or_after_origin")
        self.assertEqual(date_candidate(None,"2021-10-27"),"unknown")


if __name__ == "__main__":
    unittest.main()
