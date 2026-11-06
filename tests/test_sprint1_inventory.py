import sys
import unittest
from datetime import date
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from sprint1_inventory import (  # noqa: E402
    JOURNAL_STRICT_A_START,
    STRICT_A_START,
    classify_product,
    cohort,
    count_opportunities,
    mjd,
)


class Sprint1InventoryTests(unittest.TestCase):
    def test_mjd_anchor_dates_are_explicit(self):
        self.assertEqual(mjd(date(2025, 11, 19)), 60998)
        self.assertEqual(mjd(date(2026, 2, 12)), 61083)
        self.assertEqual(STRICT_A_START, date(2025, 11, 19))
        self.assertEqual(JOURNAL_STRICT_A_START, date(2026, 2, 12))

    def test_product_classification_requires_expected_cadence_and_release(self):
        base = {
            "provenance_name": "SPOC",
            "t_exptime": 120,
            "t_max": 60990,
            "t_obs_release": 60999,
            "dataRights": "PUBLIC",
        }
        got = classify_product(base, as_of_mjd=61000)
        self.assertEqual(got["product"], "SPOC_120")
        self.assertTrue(got["observed_by_as_of"])
        self.assertTrue(got["public_by_as_of"])
        self.assertTrue(got["eligible_product_by_as_of"])

        future = {**base, "t_max": 61001}
        self.assertFalse(classify_product(future, as_of_mjd=61000)["eligible_product_by_as_of"])
        unpublished = {**base, "t_obs_release": 61001}
        self.assertFalse(classify_product(unpublished, as_of_mjd=61000)["eligible_product_by_as_of"])
        ffi = {**base, "provenance_name": "TESS-SPOC", "t_exptime": 200}
        self.assertEqual(classify_product(ffi, as_of_mjd=61000)["product"], "TESS-SPOC_200")
        fast = {**base, "t_exptime": 20}
        self.assertEqual(classify_product(fast, as_of_mjd=61000)["product"], "")

    def test_opportunity_count_is_closed_interval_and_never_negative(self):
        self.assertEqual(count_opportunities(100.0, 2.0, 100.1, 104.1), 2)
        self.assertEqual(count_opportunities(100.0, 2.0, 104.1, 100.1), 0)
        self.assertEqual(count_opportunities(100.0, -1.0, 100, 101), 0)

    def test_core_and_extension_rules_are_disjoint_and_explicit(self):
        e = SimpleNamespace(period_days=3.0)
        self.assertEqual(cohort("Planetb", e, 12.0, {"Planet": ["Planetb"]}), ("core", "single_drd_host_tmag_lt_13.5_period_le_12d"))
        self.assertEqual(cohort("Planetb", SimpleNamespace(period_days=13.0), 12.0, {"Planet": ["Planetb"]})[0], "extension")
        self.assertEqual(cohort("Planetb", e, 12.0, {"Planet": ["Planetb", "Planetc"]})[0], "extension")


if __name__ == "__main__":
    unittest.main()
