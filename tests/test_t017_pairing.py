"""Synthetic regressions for one-to-one post-extraction timing comparison."""

import sys
import unittest
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t017_compare import assignments


def rows(times):
    return [{"tc_bjd_tdb": t} for t in times]


class TimingPairingTests(unittest.TestCase):
    def test_unmatched_early_event_does_not_shift_a_transit_train(self):
        reference = rows([0., 4., 8.])
        independent = rows([-4., .01, 4.01])
        distance = np.abs(np.array([0., 4., 8.])[:, None] - np.array([-4., .01, 4.01]))
        old_i, old_j = linear_sum_assignment(distance)
        self.assertEqual(sum(distance[i, j] < 1 for i, j in zip(old_i, old_j)), 0)
        self.assertEqual(assignments(reference, independent, 4.), [(0, 1), (1, 2)])

    def test_cardinality_precedes_small_distance_and_literal_capping(self):
        reference = rows([0., .9])
        independent = rows([.1, -.8])
        distance = np.abs(np.array([0., .9])[:, None] - np.array([.1, -.8]))
        capped_i, capped_j = linear_sum_assignment(np.minimum(distance, 1.))
        self.assertEqual(sum(distance[i, j] < 1 for i, j in zip(capped_i, capped_j)), 1)
        self.assertEqual(assignments(reference, independent, 4.), [(0, 1), (1, 0)])

    def test_distance_breaks_ties_at_maximum_cardinality(self):
        self.assertEqual(assignments(rows([.4, 0.]), rows([.1, .5]), 4.), [(0, 1), (1, 0)])

    def test_gate_is_strict_and_matching_remains_one_to_one(self):
        self.assertEqual(assignments(rows([0.]), rows([1.]), 4.), [])
        matches = assignments(rows([0., .1, 4.]), rows([.02, 4.01]), 4.)
        self.assertEqual(matches, [(0, 0), (2, 1)])
        self.assertEqual(len({i for i, _ in matches}), len(matches))
        self.assertEqual(len({j for _, j in matches}), len(matches))


if __name__ == "__main__":
    unittest.main()
