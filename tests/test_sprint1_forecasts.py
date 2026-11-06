import json
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
HAS_SCIPY=importlib.util.find_spec("scipy") is not None
if HAS_SCIPY:
    from scipy.integrate import quad
    from scipy.special import ndtr
    import forecast_variance_components as f
    import sprint1_forecast_core as c
    from sprint1_outcome_adapter import likelihood_grid, grid_score, production_rows, score_outcomes


@unittest.skipUnless(HAS_SCIPY,"scipy is in the optional analysis extra")
class SprintForecastTests(unittest.TestCase):
    def test_correlated_and_singular_ephemeris_covariance_matches_dense(self):
        n=np.array([-4.,0.,12.])
        y=np.array([4.,-.2,2.])
        for rho in (-1.,-.8,0.,.8,1.):
            p={"n":n,"m":y,"se":np.array([.3,.4,.7]),"st0":1.3,"sp":.11,"rho":rho}
            V=(p["st0"]**2+p["sp"]**2*np.outer(n,n)
               +rho*p["st0"]*p["sp"]*(n[:,None]+n[None,:]))
            np.testing.assert_allclose(np.diag(V),c.forecast_variance(p["st0"],p["sp"],n,rho),atol=1e-14)
            for scale in (.001,1.,100.):
                total=np.diag(p["se"]**2)+scale*V
                expected=-.5*(np.linalg.slogdet(total)[1]+y@np.linalg.solve(total,y)+3*np.log(2*np.pi))
                actual=f.planet_ll(f.precompute([p],[y]),scale)[0]
                self.assertAlmostEqual(float(actual),expected,places=8)

    def test_mixture_quantiles_against_adaptive_integral(self):
        for s in (.1,2.5,5.):
            ratios=np.array([.01,1.,100.])
            q=c.mixture_quantiles(ratios,s,order=384)
            for r,qq in zip(ratios,q):
                for p,value in zip((.841344746,.975),qq):
                    got=quad(lambda z:np.exp(-z*z/2)/np.sqrt(2*np.pi)*ndtr(value/np.sqrt(r*r+np.exp(s*z))),-12,12,epsabs=1e-11)[0]
                    self.assertAlmostEqual(got,p,delta=3e-5)

    def test_scores_match_existing_gaussian_and_are_unit_consistent(self):
        from transit_audit.scoring import score_one
        event={"forecast_variance_s2":400.,"sigma_s":8.,"outcome_scale":1.,"residual_s":70.}
        actual=c.predictive_scores([event],{"b":1.,"s_log_lambda":0.})
        ref=score_one(2459000.+70/86400,2459000.,400/86400**2,8/86400,levels=(.95,))
        self.assertAlmostEqual(actual["is95_minutes"][0],ref["interval_score_seconds_0.950000"]/60,delta=2e-5)
        self.assertAlmostEqual(actual["negative_log_score_seconds"][0],ref["negative_log_score_seconds"],delta=1e-5)
        self.assertAlmostEqual(actual["is95_standardised"][0],actual["is95_minutes"][0]*60/np.sqrt(464))

    def test_flat_prior_likelihood_grid_and_reject_informative_posterior(self):
        x=np.linspace(-40,40,801)
        raw={"units":"seconds","coordinate":"true_midtime_minus_reported_midtime",
             "kind":"posterior","prior":"uniform","prior_constant_over_support":True,
             "offset_s":x.tolist(),"log_density":(-.5*(x/5)**2).tolist()}
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"grid.json"
            path.write_text(json.dumps(raw))
            grid=likelihood_grid(path)
            result=grid_score(15,100,{"b":1.,"s_log_lambda":0.},grid,np.sqrt(125))
            simple=c.predictive_scores([{"residual_s":15.,"forecast_variance_s2":100.,"sigma_s":5.,"outcome_scale":1.}],{"b":1.,"s_log_lambda":0.})
            for metric in ("is95_minutes","negative_log_score_seconds","width95_minutes"):
                self.assertAlmostEqual(result[metric],simple[metric][0],places=7)
            raw["prior"]="forecast_gaussian"
            path.write_text(json.dumps(raw))
            with self.assertRaisesRegex(ValueError,"Informative posterior"):
                likelihood_grid(path)

    def test_production_product_choice_does_not_fallback_on_fit_success(self):
        rows=[{"event_id":"a","observation_id":"same","product":"SPOC_120","flux":"PDCSAP","status":"id_failed"},
              {"event_id":"b","observation_id":"same","product":"TESS-SPOC_200","flux":"PDCSAP","status":"timed"}]
        chosen,omitted=production_rows(rows)
        self.assertEqual(chosen[0]["status"],"id_failed")
        self.assertEqual(len(omitted),1)
        with self.assertRaisesRegex(ValueError,"Ambiguous"):
            production_rows([rows[0],rows[0]])

    def test_missing_failure_row_cannot_disappear_from_score_denominator(self):
        from types import SimpleNamespace
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            (p/"forecasts.csv").write_text("event_id\none\ntwo\n")
            (p/"outcomes.csv").write_text("event_id\none\n")
            args=SimpleNamespace(forecasts=p/"forecasts.csv",outcomes=p/"outcomes.csv")
            with self.assertRaisesRegex(ValueError,"attempted-outcome sets"):
                score_outcomes(args)


if __name__=="__main__":
    unittest.main()
