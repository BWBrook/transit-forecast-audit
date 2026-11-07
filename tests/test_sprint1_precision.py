import importlib.util
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sprint1_precision", ROOT / "scripts" / "sprint1_precision.py"
)
PRECISION = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = PRECISION
SPEC.loader.exec_module(PRECISION)


class Sprint1PrecisionTests(unittest.TestCase):
    @unittest.skipUnless(
        (ROOT / "results/sprint1/inventory/planet_sector_product_inventory.csv").exists(),
        "full inventory integration requires the archived bulk inputs",
    )
    def test_future_design_uses_declared_core_and_extension_only(self):
        core, core_summary = PRECISION.load_future_events({"core"})
        union, union_summary = PRECISION.load_future_events({"core", "extension"})

        self.assertEqual((core_summary["planets"], core_summary["hosts"], len(core)), (156, 156, 3107))
        self.assertEqual((union_summary["planets"], union_summary["hosts"], len(union)), (184, 175, 3399))
        self.assertEqual(union_summary["planets_by_cohort"], {"core": 156, "extension": 28})
        self.assertEqual(len({row["event_id"] for row in union}), len(union))
        self.assertFalse({row["cohort"] for row in union} - {"core", "extension"})

    def test_synthetic_future_design_excludes_flags_and_unresolved_cohorts(self):
        start = PRECISION._date_jd("2025-11-20")
        ephemeris = SimpleNamespace(t0_bjd_tdb=start, period_days=2., sigma_t0_days=.001, sigma_period_days=.00001)
        inventory = []
        for planet, cohort, public in (("synthetic_core", "core", "True"),
                                        ("synthetic_extension", "extension", "True"),
                                        ("synthetic_unresolved", "unresolved", "True"),
                                        ("synthetic_flagged", "core", "True"),
                                        ("synthetic_unavailable", "core", "False")):
            inventory.append({"planet":planet,"host":planet,"cohort":cohort,"sector":"100",
                              "product":"SPOC_120","strict_a_opportunity_count":"3",
                              "eligible_product_by_as_of":public,"conservative_start_utc":"2025-11-20",
                              "conservative_end_utc":"2025-11-24","product_t_min_mjd":str(start-2400000.5),
                              "product_t_max_mjd":str(start+4-2400000.5),"tmag":"11"})
        catalogues = ({"DRD":{r["planet"]:ephemeris for r in inventory}}, None, {"DRD":{"synthetic_flagged"}})
        with patch.object(PRECISION,"read_csv",return_value=inventory), \
             patch.object(PRECISION.core,"load",return_value=catalogues), \
             patch.object(PRECISION.core,"covariance_rows",return_value={}), \
             patch.object(PRECISION.core,"correlation",return_value=0.), \
             patch.object(PRECISION,"timing_sigma_references",return_value=([{"host":"synthetic_reference","tmag":11.,"sigma_s":30.}],{})):
            core, _ = PRECISION.load_future_events({"core"})
            union, _ = PRECISION.load_future_events({"core","extension"})
        self.assertEqual(len(core),3)
        self.assertEqual({r["planet"] for r in union},{"synthetic_core","synthetic_extension"})
        self.assertEqual(len(union),6)
        self.assertEqual(len({r["event_id"] for r in union}),6)

    def test_selected_weights_remain_planet_balanced(self):
        planet_index = np.asarray([0, 0, 1, 1, 1, 2])
        mask = np.asarray([[True, False, True, True, False, False]])
        weights, active = PRECISION.selected_weights(mask, planet_index, 3)

        self.assertEqual(active.tolist(), [2])
        self.assertAlmostEqual(weights.sum(), 1.0)
        self.assertAlmostEqual(weights[0, planet_index == 0].sum(), 0.5)
        self.assertAlmostEqual(weights[0, planet_index == 1].sum(), 0.5)
        self.assertAlmostEqual(weights[0, planet_index == 2].sum(), 0.0)

    def test_tmag_match_is_local_median_not_single_host(self):
        references = [
            {"host": f"h{index}", "tmag": float(index), "sigma_s": float(10 * index)}
            for index in range(1, 8)
        ]
        sigma, status = PRECISION.matched_sigma(4.1, references, neighbours=5)

        self.assertEqual(sigma, 40.0)
        self.assertEqual(status, "nearest_5_tmag_median")

    @unittest.skipUnless(
        (ROOT / "data/derived/sprint1/release_transfer/a_1.087/c2/parameters.json").exists(),
        "full development-design integration requires the archived bulk inputs",
    )
    def test_model_half_widths_and_primary_weights_are_valid(self):
        design = PRECISION.load_development_design("release_transfer")

        self.assertAlmostEqual(design.weights.sum(), 1.0)
        self.assertTrue(np.all(design.denominator > 0))
        for method in PRECISION.METHODS:
            self.assertTrue(np.all(np.isfinite(design.half_widths[method])))
            self.assertTrue(np.all(design.half_widths[method] > 0))

    def test_synthetic_design_preserves_shared_hosts_and_predictive_variance(self):
        models = {method:{"b":1.,"s_log_lambda":0.} for method in PRECISION.METHODS}
        models["M2"]["s_log_lambda"] = 1.5
        events = [{"event_id":f"synthetic_{i}","planet":planet,"host":host,"forecast_epoch":i,
                   "sigma_t0_s":10.,"sigma_p_s":.1,"rho":0.,"forecast_variance_s2":100.+.01*i*i,
                   "sigma_s":5.,"outcome_scale":1.}
                  for i,(planet,host) in enumerate((("a","shared"),("a","shared"),("b","shared"),("c","other")))]
        design = PRECISION.make_design("synthetic_only",events,models)
        self.assertAlmostEqual(design.weights.sum(),1.)
        by_host = dict(zip(design.host_names,design.host_weights))
        self.assertAlmostEqual(by_host["shared"],2/3)
        self.assertAlmostEqual(by_host["other"],1/3)
        np.testing.assert_allclose(design.denominator,np.sqrt(design.forecast_variance+25.))
        self.assertTrue(np.all(design.half_widths["M2"]>design.half_widths["M0"]))


if __name__ == "__main__":
    unittest.main()
