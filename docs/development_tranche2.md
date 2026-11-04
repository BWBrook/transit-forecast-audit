# Development tranche 2: noise structure, forecast calibration shape, sealed-era inventory

**Review notice (5 November):** retain this as the original tranche report.
[Independent review](tranche2_independent_review.md), D030–D033, confirms the
conditional scale and mixture point estimates but replaces the coarse posterior
tail counts, qualifies the profile intervals and rejects the inventory's claim
that all listed sector predictions are already observed. The original pipeline
still requires the numerical and inventory repairs specified there.

**Claude (Opus 5.5), 5 November 2026. Development material only (D014).** This
tranche answers Codex's review (`docs/independent_review.md`, D020–D024). It uses
only the inspected 2022-01-01 to 2024-01-03 TESS mid-times and metadata. No
light curve was opened, and nothing dated after 2025-11-18 was read except the
TESS pointing schedule (D023).

```bash
uv run --extra analysis python scripts/local_noise_structure.py
uv run --extra analysis python scripts/forecast_variance_components.py
uv run --extra analysis python scripts/sealed_era_inventory.py
```

## 1. The local excess scatter scales with σ_Tmid; it is not additive jitter

Codex showed that, at fixed σ_Tmid, a measurement-scale factor and white
latent timing jitter give identical residual distributions (D022). That holds
only at fixed σ. TESS σ_Tmid spans 0.05–40 min (10th–90th percentile
0.45–3.0 min), so the two hypotheses make different predictions. A scale factor
leaves z-scatter flat in σ. Additive jitter τ inflates it as sqrt(1 + τ²/σ²),
mostly for the most precise timings.

`scripts/local_noise_structure.py` fits Var(e) = a²σ² + τ² by exact REML. It
uses Codex's span-capped groups (D022), with a per-group intercept and slope:
4173 events, 726 groups, 336 planets, DRD flags excluded.

| Model (local linear) | a | τ (s) | −log L |
|---|---|---|---|
| a = 1, τ = 0 | 1 | 0 | 3650.6 |
| scale only | 1.094 | 0 | 3627.3 |
| jitter only | 1 | 11.9 | 3640.3 |
| scale + jitter | **1.087** [1.043, 1.117] | 5.0 [1.6, 11.0] | 3626.6 |

Brackets are 95% intervals from a 200-replicate planet-cluster bootstrap. The
likelihood ratio for adding scale to jitter is 27.4 (45.1 with a local mean
only); for adding jitter to scale it is 1.5. Binned by σ_Tmid,
`sigma_binned_scatter.csv` gives z-RMS of 1.08–1.17 from 0.4 to 1.7 min. The
jitter-only model predicts 1.11 falling to 1.01 across that range, which the
data do not show. A weak within-planet check is consistent. In 12 planets
observed at both lower and higher σ (≥1.5×), the higher-σ visits have the
larger χ²/dof (1.17 against 1.02). Jitter predicts the reverse.

**Interpretation.** The excess scales with photometric σ. Red noise and model
error in the light-curve fit behave this way. Astrophysical timing jitter (spot
crossings, short-period TTVs) does not, since its amplitude is not set by photon
noise. White latent jitter is bounded at about 11 s. Codex's other objections
still stand. A variance proportional to σ² that comes from planetary physics
cannot be excluded. Centring removes common offsets, and ExoClock's
neighbour-agreement filter conditions the sample. So a = 1.09 is the best
current constraint on the outcome-error scale, used as a fixed input with 1.0
and 1.2 as sensitivities. It is not a validated calibration. T015, which uses
injections into real light curves, is still the test of `a`.

## 2. Forecast miscalibration has a heavy-tailed planet-level shape

Codex asked for a likelihood with shared ephemeris covariance and a
demonstration of identifiability before any fitting (D022, D024).
`scripts/forecast_variance_components.py` records two failed designs and the
one that works.

- **One stage, Gaussian, event level:** V = a²S + b²XCX′ (+ τ terms) per
  planet. On DRC (origin flags, 316 planets) it returns **b ≈ 98**. A few
  planets dominate it.
- **Adding a discrete planet-failure mixture** (offset κ with probability π)
  makes the likelihood multimodal. The best fits were b ≈ 20 (DRC) and π = 1
  (DRB). The discrepancies are continuous, not two-class.
- **Adopted for development:** two stages.
  1. Robust visit means within span-capped visits. A 5σ clip removed no
     events, and visit standard errors use a = 1.087.
  2. A planet-level log-normal scale mixture,
     V_p = diag(se²) + b²λ_p XCX′ with log λ_p ~ N(0, s²).

  Here *b* is the median inflation of the issued forecast SD across planets and
  *s* the spread of miscalibration between them. XCX′ has rank 2, so the
  likelihood is closed-form (tested against a dense Cholesky). λ_p is
  integrated by Gauss–Hermite quadrature.

| Release vs TESS 2022–23 (origin flags) | Planets | Visits | Gaussian b | **b (median inflation)** | **s (spread of log λ)** | Planets λ>10 / >100 |
|---|---|---|---|---|---|---|
| DRB | 134 | 343 | 3.05 | **2.25** [1.87, 2.72] | **1.09** [0.72, 1.54] | 0 / 0 |
| DRC | 316 | 837 | 42.7 | **0.98** [0.71, 1.28] | **3.13** [2.78, 3.74] | 15 / 10 |

Brackets are profile-likelihood 95% intervals. The likelihood ratio of the
mixture against the Gaussian is 32 for DRB and 2177 for DRC. Results barely
move with the outcome scale: as a goes from 1.0 to 1.2, DRC's b falls from 1.06
to 0.88 and its s rises from 3.08 to 3.20, while DRB's b stays at 2.26–2.23.
The data cannot pin down a in this stage (−log L keeps falling as a rises),
which is why a is fixed from §1.

**Interpretation.**

- **DRB** issued uncertainties are typically about 2.2× too small, fairly
  uniformly. This fits DRB's 48% within 1σ in Table 5.
- **DRC** has a calibrated median but an extremely heavy tail. For 15 of 316
  planets the forecast SD is more than 3× too optimistic, and for 10 it is more
  than 10× too optimistic. TOI-1130b misses by +611 min, TOI-125c by +109 min,
  TOI-125b by −68 min, TOI-1130c by −60 min, WASP-161b by −53 min, HD332231b by
  −29 min and TOI-2076b by −28 min (`planet_miscalibration.csv`). Many planets
  are conservative (posterior median λ < 1).
- **What this means for the benchmark.** The DRC median planet is calibrated,
  so a single inflation factor cannot repair the catalogue. Pooled coverage at
  k·σ is not a summary of calibration: it averages a calibrated or conservative
  majority with a few catastrophic failures, and the hindsight flags of D015
  remove some of the latter. The quantity the project should forecast and test
  is the tail: P(λ_p > 10 | metadata at issue). Candidate predictors known at
  issue are the number of training epochs, the time span, whether the training
  includes TESS, multi-planet systems and literature-only inputs.

### 2.1 Identifiability on the real design

Twenty simulated replicates per truth on the real DRC visit design (316
planets, 837 visits, issued C, se), refitted with the same multi-start
optimiser (seed 20261105, `identifiability_simulation.csv`). Synthetic only.

| Truth (b, s) | b̂ median [10%, 90%] | ŝ median [10%, 90%] |
|---|---|---|
| (1.0, 0) | 0.98 [0.88, 1.06] | 0.00 [0.00, 0.64] |
| (1.0, 1.0) | 1.00 [0.82, 1.11] | 1.01 [0.73, 1.36] |
| (1.5, 1.0) | 1.47 [1.37, 1.57] | 1.07 [0.87, 1.23] |
| (1.0, 2.5) | 1.02 [0.72, 1.15] | 2.43 [2.22, 2.82] |
| (0.98, 3.13), fitted | 0.95 [0.77, 1.19] | 3.24 [2.97, 3.53] |

The design separates b from s with no material bias. A common inflation is
distinguishable from heterogeneity. b is least precise when s is large, because
many planets then carry little information about the median.

**Who fails.** The 15 DRC planets with posterior λ > 10 are listed in
`planet_miscalibration.csv`. Eleven are TESS-era discoveries or TESS
multi-planet systems: TOI-1130b/c, TOI-125b/c, TOI-201b, TOI-2076b, TOI-1478b,
HD191939c, HD332231b (TOI-1456), L98-59c and HAT-P-69b. Short or sparse
training baselines at DRC issue are the obvious candidate cause. This is a
hypothesis for an issue-time predictor of λ, to be tested with metadata known
at issue. It is not an established result.

Two limits apply. Posterior λ values are quantised on the quadrature nodes and
indicate order of magnitude only. The model assumes discrepancy proportional
to the issued XCX′. A pure offset failure on a planet with a tiny issued σ_P is
represented as a large λ.

## 3. Sealed era: inventory from metadata only (T016)

`scripts/sealed_era_inventory.py` uses tess-point 0.9.5.post1 pointings and
NASA Exoplanet Archive coordinates (both hash-recorded). It lists the TESS
sectors covering each DRD planet whose window ends after 2025-11-18. No
photometric product was requested.

| | Count |
|---|---|
| DRD planets with any sealed sector (S98–S134, incl. scheduled) | 450 of 620 |
| Planets in sectors observed by 2026-11-05 (S98–S110) | 224 (206 hosts) |
| DRD-predicted transits in those windows | 5071 |
| Of which in windows after the DRD journal date (strict Track A, D023) | 171 planets, 4006 transits |
| Median DRD forecast SD in observed sealed windows | 1.05 min |
| Median forecast share of σ²_O−C (σ_Tmid proxy from 2022–23) | 23% (13% for DRC 2022–23) |

**Caveats.**

- FFI coverage only. Real usable counts will be lower once cadence, data gaps
  and quality cuts apply.
- Sector windows are the pointing midtime ± 13.7 d, because the official orbit
  table (tess.mit.edu) failed TLS verification here. The S97/S98 boundary needs
  the official table before freeze.
- Kepler-854b has no coordinate match.

The sealed era is large enough for a planet-balanced test. It is also more
informative about the forecast than Table 5 was, because DRD is extrapolated
two to three years past its training cutoff.

## 4. Consequences for the protocol (proposals, not frozen)

1. **Outcome scale:** fixed a = 1.09, with sensitivities 1.0 and 1.2, until
   T015 injections constrain it directly.
2. **Primary forecast-calibration estimands:** (b, s) of the planet-level scale
   mixture and the fraction of planets with λ_p > 10, all planet-balanced.
   Coverage tables are secondary and kept for comparison with ExoClock IV.
3. **The extension worth testing prospectively:** a heavy-tailed predictive
   distribution for each DRD ephemeris, a scale mixture with s and possibly
   issue-time predictors of λ fitted on 2022–23. Test it against the
   Gaussian-as-issued forecast on the sealed era, using proper scores (log
   score and interval score), planet-balanced, with host-cluster uncertainty.
4. **Track B / Track A split for the sealed era:** S98–S100 start before the
   DRD journal date (2026-02-11) and are observation-cutoff hindcasts (D023);
   S101 onward are strict Track A. Transits in S100 after 2026-02-11 could be
   split out once official sector times are in hand.
