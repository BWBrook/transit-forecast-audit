import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT / "scripts"), str(ROOT / "src")]
from sprint2_freeze_package import boundary_status


class CandidateBoundary(unittest.TestCase):
    def test_utc_anchor_near_barycentric_prediction_is_unresolved(self):
        lower = 2460998.5
        self.assertEqual(boundary_status(lower + 8.8/1440, lower, lower+2), "unresolved_time_conversion")
        self.assertEqual(boundary_status(lower+2-8.8/1440, lower, lower+2), "unresolved_time_conversion")
        self.assertEqual(boundary_status(lower+1, lower, lower+2), "metadata_interior_only")
