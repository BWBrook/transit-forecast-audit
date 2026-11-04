import importlib.util
import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))


@unittest.skipUnless(importlib.util.find_spec("scipy"),"scipy is in optional analysis extra")
class ChronologicalHostTests(unittest.TestCase):
    def test_shared_host_resampling_preserves_both_planets_and_time_blocks(self):
        from chronological_calibration import bootstrap_indices
        rng = np.random.default_rng(4)
        for _ in range(20):
            early,late = bootstrap_indices(np.array(["a","a","b"]),np.array(["a","b","b","c"]),rng)
            self.assertEqual(early[0],early[1])
            self.assertEqual(early[0],late[0])
            self.assertEqual(early[2],late[1])
            self.assertEqual(late[1],late[2])
            self.assertEqual(early[0]+early[2]+late[3],3)


if __name__ == "__main__":
    unittest.main()
