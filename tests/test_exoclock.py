import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import numpy as np

from transit_audit.exoclock import (Ephemeris, MidTime, host_of, read_catalogue,
                                    read_drb_ephemerides, read_mid_times,
                                    residuals_without_covariance)

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "osf"


class ParserTests(unittest.TestCase):
    def test_drb_flags_and_columns(self):
        row = "\t".join(["X-1b", "2457000.1", "0.0001", "2.5", "0.000001", "1.2"] + ["0"] * 8
                        + ["True", "False", "url"])
        with TemporaryDirectory() as d:
            p = Path(d) / "e.txt"
            p.write_text("# header\n" + row + "\n")
            e = read_drb_ephemerides(p)["X-1b"]
        self.assertEqual(e.flags, ("nonlinear",))
        self.assertEqual(e.period_days, 2.5)

    def test_drc_header_without_planet_label_is_read(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "m.txt"
            p.write_text("Tmid (BJD_TDB)\tTmid unc.\tsource\tID\n"
                         "X-1b  2459600.5\t0.001\tspace\tX-1b_10_2022-01-21_TESS\n")
            m = read_mid_times(p)[0]
        self.assertEqual((m.planet, m.tess_date), ("X-1b", "2022-01-21"))

    def test_malformed_catalogue_row_is_rejected(self):
        with TemporaryDirectory() as d:
            p = Path(d) / "c.txt"
            p.write_text("Planet T0 unc P unc\nX-1b 2457000.1 0.0001 2.5\n")
            with self.assertRaises(ValueError):
                read_catalogue(p)

    def test_host_labels(self):
        self.assertEqual(host_of("TOI-216.01"), "TOI-216")
        self.assertEqual(host_of("55Cnce"), "55Cnc")
        self.assertEqual(host_of("HD209458b"), "HD209458")


class ResidualTests(unittest.TestCase):
    def test_sigma_uses_epoch_scaled_period_error_and_measurement(self):
        e = {"X-1b": Ephemeris("X-1b", 2450000.0, 1e-4, 2.0, 1e-6)}
        ev = [MidTime("X-1b", 2450000.0 + 1000 * 2.0 + 3e-4, 2e-4, "space", "X-1b_1000_2022-01-01_TESS")]
        n, oc, pred_sd, sig = residuals_without_covariance(e, ev)
        self.assertEqual(n[0], 1000)
        self.assertAlmostEqual(oc[0], 3e-4, places=9)
        self.assertAlmostEqual(sig[0], np.sqrt(2e-4**2 + 1e-4**2 + (1000 * 1e-6) ** 2))


@unittest.skipUnless((RAW / "wpjtn" / "all_mid_time_data.txt").exists(),
                     "acquired OSF artifacts not present (run scripts/acquire_osf.py)")
class Table5ReproductionTests(unittest.TestCase):
    def test_drb_and_drc_columns_reproduce_exactly(self):
        sys.path.insert(0, str(ROOT / "scripts"))
        import reproduce_table5 as r
        with TemporaryDirectory() as d:
            r.main(["--output", d])
            import json
            checks = json.loads((Path(d) / "table5_reproduction_check.json").read_text())["checks"]
        self.assertTrue(checks["DRB"]["exact"])
        self.assertTrue(checks["DRC"]["exact"])
        self.assertEqual(checks["DRD"]["measurements"], [4716, 4716])


if __name__ == "__main__":
    unittest.main()
