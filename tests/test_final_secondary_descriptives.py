"""Synthetic checks of subset weighting, recovery and the declared gain-host curve."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import final_secondary_descriptives as s


def event(identity, planet, host, status="accepted", coverage=True):
    return {"event_id": identity, "planet": planet, "host": host, "status": status,
            "coverage_qualified": coverage}


def score(identity, planet, host, value, method="M0"):
    return {"event_id": identity, "planet": planet, "host": host, "method": method,
            **{key: "1" if key in ("covered68", "covered95") else str(value) for key in s.METRICS},
            "weight": "999"}


class SecondaryDescriptives(unittest.TestCase):
    def test_planet_weights_are_rebuilt_within_each_subset(self):
        events = [event("a1", "A", "HA"), event("a2", "A", "HA"),
                  event("a3", "A", "HA"), event("b1", "B", "HB")]
        rows = [score(e["event_id"], e["planet"], e["host"], value, method)
                for e, value in zip(events, (2, 4, 6, 20)) for method in s.METHODS]
        scores = s.validate_scores(rows, events)
        _, models = s.summarize(events, scores)
        self.assertEqual(models["M0"]["is95_standardised"], 12)
        counts, subset = s.summarize([events[0], events[-1]], scores)
        self.assertEqual(subset["M0"]["is95_standardised"], 11)
        self.assertEqual(counts["accepted_planets"], 2)
        self.assertEqual(counts["fraction_planets_improved"], 0)

    def test_gain_hosts_rank_by_summed_planet_contribution_and_stay_whole(self):
        planets = [{"planet": "A1", "host": "HA", "delta": -5},
                   {"planet": "A2", "host": "HA", "delta": -5},
                   {"planet": "B", "host": "HB", "delta": -9},
                   {"planet": "C", "host": "HC", "delta": 4},
                   {"planet": "D", "host": "HD", "delta": None}]
        ranking, curve = s.gain_host_influence(planets)
        self.assertEqual([r["host"] for r in ranking], ["HA", "HB", "HC"])
        self.assertEqual(ranking[0]["contribution_to_original_mean"], -2.5)
        self.assertEqual(curve[0]["mean_planet_delta"], -3.75)
        self.assertEqual(curve[1]["removed_hosts"], "HA")
        self.assertEqual(curve[1]["removed_planets"], 2)
        self.assertEqual(curve[1]["remaining_planets"], 2)
        self.assertEqual(curve[1]["mean_planet_delta"], -2.5)
        self.assertEqual(curve[2]["mean_planet_delta"], 4)
        self.assertFalse(curve[3]["available"])
        self.assertIsNone(curve[3]["mean_planet_delta"])

    def test_gain_host_ties_use_alphabetical_order(self):
        ranking, curve = s.gain_host_influence([{"planet": "B", "host": "HB", "delta": -2},
                                               {"planet": "A", "host": "HA", "delta": -2}])
        self.assertEqual([r["host"] for r in ranking], ["HA", "HB"])
        self.assertEqual(curve[1]["removed_hosts"], "HA")
        self.assertEqual(curve[1]["fraction_planets_improved"], 1)
        self.assertIsNone(curve[2]["mean_planet_delta"])
        self.assertEqual(curve[2]["reason"], "no remaining accepted planets")

    def test_recovery_keeps_unknown_and_unqualified_coverage_separate(self):
        events = [event("a1", "A", "HA"), event("a2", "A", "HA", "edge", None), event("a3", "A", "HA"),
                  event("b1", "B", "HB", "edge"), event("b2", "B", "HB", coverage=False)]
        rows = [score(e["event_id"], e["planet"], e["host"], 3, method)
                for e in events if e["status"] == "accepted" for method in s.METHODS]
        counts, _ = s.summarize(events, s.validate_scores(rows, events))
        self.assertEqual(counts["coverage_unknown_events"], 1)
        self.assertEqual(counts["coverage_unqualified_events"], 1)
        self.assertEqual(counts["accepted_coverage_qualified_events"], 2)
        self.assertEqual(counts["accepted_coverage_unqualified_events"], 1)
        self.assertEqual(counts["event_recovery_all_intended"], 3 / 5)
        self.assertAlmostEqual(counts["planet_balanced_recovery_all_intended"], 7 / 12)
        self.assertEqual(counts["event_recovery_coverage_qualified"], 2 / 3)
        self.assertEqual(counts["planet_balanced_recovery_coverage_qualified"], .5)

    def test_empty_cell_is_preserved_without_zero_score_or_recovery(self):
        counts, models = s.summarize([], {})
        self.assertEqual(counts["intended_events"], 0)
        self.assertEqual(counts["accepted_planets"], 0)
        self.assertIsNone(counts["event_recovery_all_intended"])
        self.assertIsNone(counts["fraction_planets_improved"])
        self.assertTrue(all(v is None for m in models.values() for v in m.values()))

    def test_missing_or_duplicate_method_fails_instead_of_changing_subset(self):
        events = [event("a", "A", "HA")]
        rows = [score("a", "A", "HA", 3, method) for method in s.METHODS]
        with self.assertRaisesRegex(ValueError, "exactly cover"):
            s.validate_scores(rows[:-1], events)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            s.validate_scores(rows + [rows[0]], events)

    def test_band_boundaries_and_proxy_anchor(self):
        self.assertEqual([s.lead_band(x) for x in (0, 1, 1.00001, 3, 3.00001, 5, 5.00001, None)],
                         ["nonpositive", "(0,1] years", "(1,3] years", "(1,3] years",
                          "(3,5] years", "(3,5] years", ">5 years", "unknown"])
        self.assertEqual([s.tmag_band(x) for x in (9.9, 10, 11, 12, 13.5, None)], list(s.TMAG_BANDS))
        self.assertEqual(s.numeric_anchor_jd("2000-01-01T12:00:00Z"), 2451545)

    def test_ttv_join_preserves_unflagged_unknown_and_all_event_statuses(self):
        events = [{**event(name, name, "H" + name), "cohort": "core"} for name in ("A", "B", "C")]
        labels = [{"planet": "A", "host": "HA", "cohort": "core", "archive_ttv_flag": "0",
                   "current_catalogue_ttv_label": s.TTV_LABELS[1]},
                  {"planet": "B", "host": "HB", "cohort": "core", "archive_ttv_flag": "1",
                   "current_catalogue_ttv_label": s.TTV_LABELS[0]}]
        before = [(r["event_id"], r["status"]) for r in events]
        joined = s.join_ttv_labels({"primary": events}, labels)
        self.assertEqual([r["current_catalogue_ttv_label"] for r in events],
                         [s.TTV_LABELS[1], s.TTV_LABELS[0], "unknown"])
        self.assertEqual(joined["current_label_counts"], {key: 1 for key in s.TTV_LABELS})
        self.assertEqual(joined["match_status_counts"], {"matched": 2, "missing_label_row": 1})
        self.assertEqual([(r["event_id"], r["status"]) for r in events], before)
        self.assertTrue(all(r["ttv_discovery_date"] == r["new_since_origin"] == "unknown" for r in events))

    def test_ambiguous_identity_mismatch_and_inconsistent_ttv_flag_remain_unknown(self):
        events = [{**event(name, name, "H" + name), "cohort": "core"} for name in ("A", "B", "C")]
        labels = [{"planet": name, "host": "H" + name, "cohort": "core", "archive_ttv_flag": "0",
                   "current_catalogue_ttv_label": s.TTV_LABELS[1]} for name in ("A", "B", "C")]
        labels[0]["host"] = "wrong host"
        labels.append(dict(labels[1]))
        labels[2]["current_catalogue_ttv_label"] = s.TTV_LABELS[0]
        joined = s.join_ttv_labels({"primary": events}, labels)
        self.assertEqual(joined["current_label_counts"], {"unknown": 3})
        self.assertEqual([r["ttv_label_match_status"] for r in events],
                         ["identity_mismatch", "ambiguous_label_rows", "unknown_or_inconsistent_catalogue_label"])


if __name__ == "__main__":
    unittest.main()
