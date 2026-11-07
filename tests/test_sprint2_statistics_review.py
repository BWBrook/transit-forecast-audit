import gzip
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import sprint2_analysis as sa


class Sprint2StatisticsReview(unittest.TestCase):
    def test_controls_use_compressed_sprint2_counts_without_running_simulations(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder)
            dev = output / "dev"
            dev.mkdir()
            with gzip.open(dev / "ledger.csv.gz", "wt") as f:
                f.write("host,product,status,mode\na,SPOC_120,timed,remove\n"
                        "a,SPOC_120,timed,remove\nb,TESS-SPOC_200,timed,remove\n"
                        "a,SPOC_120,timed,subtract\na,SPOC_120,edge,remove\n")
            for name in ("runs.csv", "products.csv", "real_transits.csv"):
                (dev / name).write_text("status\n")
            with patch.object(sa, "OUT", output), patch.object(sa, "ROOT", output):
                with patch.object(sa, "simulate", side_effect=RuntimeError("stop before simulation")) as sim:
                    with self.assertRaisesRegex(RuntimeError, "stop before simulation"):
                        sa.check(SimpleNamespace(reps=1, boot=1))
                    self.assertEqual(sim.call_args.args[2].tolist(), [2, 1])
            self.assertFalse((output / "estimand_negative_controls.json").exists())

    def test_failed_preferred_product_does_not_trigger_fallback(self):
        available = [
            {"host": "a", "product": "SPOC_120", "status": "product_id_failed"},
            {"host": "a", "product": "TESS-SPOC_200", "status": "timed"},
            {"host": "b", "product": "TESS-SPOC_200", "status": "timed"},
        ]
        timed = [row for row in available if row["status"] == "timed"]
        self.assertEqual(sa.production(timed, available), [available[2]])

    def test_asymmetric_interval_contains_truth_in_fitted_coordinates(self):
        # Fitted time 100, interval [90, 130]: truth 125 is inside; truth 75 is outside.
        self.assertTrue(sa.interval_covers(100 - 125, 10, 30))
        self.assertFalse(sa.interval_covers(100 - 75, 10, 30))
        self.assertTrue(sa.interval_covers(-30, 10, 30))
        self.assertTrue(sa.interval_covers(10, 10, 30))
        self.assertFalse(sa.interval_covers(-20, 10, 30, 0.5))
        self.assertTrue(sa.interval_covers(-14, 10, 30, 0.5))


if __name__ == "__main__":
    unittest.main()
