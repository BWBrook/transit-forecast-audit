import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from review_d071 import raw_filename_identity, single_sector_spoc120


class MetadataScopeTests(unittest.TestCase):
    def test_ffi_cache_also_prevents_false_new_host_label(self):
        self.assertEqual(raw_filename_identity("hlsp_tess-spoc_tess_phot_0000000310002617-s0074_tess_v1_lc.fits"),
                         (74, "310002617"))
        self.assertEqual(raw_filename_identity("tess2024003055635-s0074-0000000310002617-0269-s_lc.fits"),
                         (74, "310002617"))
        self.assertIsNone(raw_filename_identity("unclassified.fits"))

    def row(self):
        return {"sequence_number": 74, "provenance_name": "SPOC", "t_exptime": 120,
                "dataRights": "PUBLIC", "t_min": 60312., "t_max": 60339.,
                "dataproduct_type": "timeseries",
                "dataURL": "mast:TESS/product/tess2024003055635-s0074-0000000310002617-0269-s_lc.fits"}

    def test_only_named_single_sector_light_curves(self):
        row = self.row()
        self.assertTrue(single_sector_spoc120(row))
        row.update(dataURL="mast:TESS/product/tess2018206190142-s0001-s0074-0000000310002617_dvt.fits",
                   t_min=58324.)
        self.assertFalse(single_sector_spoc120(row))

    def test_fail_closed_for_wrong_sector_or_cadence(self):
        for change in ({"sequence_number": 73}, {"sequence_number": 75}, {"t_exptime": 20},
                       {"dataRights": "EXCLUSIVE_ACCESS"}, {"t_max": None}, {"provenance_name": "TESS-SPOC"}):
            with self.subTest(change=change):
                self.assertFalse(single_sector_spoc120({**self.row(), **change}))


if __name__ == "__main__":
    unittest.main()
