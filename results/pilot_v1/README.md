# Pilot v1: Track R reproduction and feasibility audit

**Claude (Opus 5.5), 2026-11-04. Development material only.** All TESS
outcomes used here (record dates 2022-01-01 to 2024-01-03) have now been
inspected. They can be used for development and recalibration fitting. They
can never be relabelled as an untouched evaluation era (decision D014).

## How to regenerate

```bash
python3 scripts/acquire_osf.py --manifest results/pilot_v1/source_manifest.csv
python3 scripts/reproduce_table5.py
python3 scripts/covariance_completeness.py
python3 scripts/tess_measurement_calibration.py
uv run --extra analysis python scripts/pilot_dossiers.py
```

Raw bytes land in `data/raw/osf/` (gitignored, CC BY 4.0, read-only). The
manifest records OSF file GUIDs, version counts, upload times and SHA-256
hashes. A rerun refuses to proceed if any hash changes.

## 1. Sources and inclusion flow

| File | Content |
|---|---|
| `source_manifest.csv` | Eight OSF artifacts (DRB, DRC, DRD ephemerides and mid-times), each at OSF version 1 with SHA-256 |
| `inclusion_flow_drb.csv` | All 180 DRB planets, each with a stage code |

The DRB flow, using metadata and outcome existence but no outcome values:

| Stage | Planets |
|---|---|
| In DRB | 180 |
| No TESS timing dated 2022+ in DRD | 44 |
| Flagged non-linear in DRB itself (known at origin) | 2 |
| All outcomes on or before the DRB journal date | 1 |
| **Eligible development cohort** | **133** |

*No TESS timing in DRD* is a statement about this outcome source. It is not
evidence that no transit was observed (AGENTS invariant 12).

## 2. Ten-planet dossiers

`pilot_dossiers.csv` has one row per queue planet. `pilot_pairs_drb.csv` holds
184 forecast–outcome pairs, each with eligibility codes. `plots/<planet>.png`
shows the DRB forecast band as issued, the DRB input timings, the later TESS
outcomes and the DRC and DRD means. Each plot was inspected.

- **WASP-52b and WASP-74b** have no 2022+ TESS timing in DRD
  (`no_tess_2022plus_timing_in_DRD`).
- **WASP-12b** is the positive control. It was flagged non-linear in DRB, and
  the TESS 2023 outcomes sit 6–9 min early, with |z| up to 13.
- **WASP-80b** is an ordinary-queue planet with no flag at any release. It
  misses by about 4σ (O−C ≈ −1.1 min against a forecast σ of 0.28 min).
  **HD209458b** reaches z ≈ −2.9.
- **Qatar-1b** was flagged TTV in DRC and unflagged in DRD. It shows how
  hindsight flags change the cohort.
- Lead times run from −8 to 665 days after the DRB journal date (6 pairs
  precede it). The extrapolation age is 453–1081 days after the last DRB input.

## 3. Reproduction of ExoClock IV Table 5 (Track R)

`table5_reproduction_check.json` and `table5_variants.csv` (rows `R0_*`) hold
the result. The definition that reproduces the published table is:

- outcomes are DRD `all_mid_time_data.txt` rows from source `space`, with ID
  ending `_TESS` and an ID date of 2022-01-01 or later;
- the planet must be in the evaluated release;
- the **42 planets flagged for TTVs in DRD** are excluded (DRD §4.4: 30
  multi-planet and 12 others);
- epochs are nearest-integer;
- success is |O−C| / sqrt(σ_Tmid² + σ_T0² + (n σ_P)²) < k, with no covariance
  term and pooled over measurements.

| Release | Planets | Measurements | <1σ | <2σ | <3σ | <4σ | Match |
|---|---|---|---|---|---|---|---|
| DRB | 130 | 1585 | 48.01 | 76.53 | 93.50 | 98.30 | **exact** |
| DRC | 308 | 3604 | 62.32 | 91.32 | 98.34 | 99.61 | **exact** |
| DRD | 424 | 4716 | 66.41 (pub. 66.39) | 93.70 | 99.28 | 99.96 | 1 of 4716 differs |

The DRD difference is one measurement at the 1σ boundary. The nearest cases
have z = 0.99984 and 0.99988. That is consistent with ExoClock using
unrounded in-house parameters, but this is not verified. The "Initial" column
was not attempted: the table of initial ephemerides at insertion is not in the
release files (DRD `tab_parameters.csv` carries later references).

## 4. What the reproduction reveals (sensitivities, development data)

From `table5_variants.csv`. "S2" excludes only the flags known when the
forecast was issued: DRB's own non-linear flag for DRB, and the 19 DRC TTV
planets for DRC.

| DRC vs TESS 2022+ | Planets | Pooled 3σ miss | Planet-balanced 3σ miss [95% host-cluster CI] |
|---|---|---|---|
| R0 published (DRD-era flags removed) | 308 | 1.66% | 2.80% [1.58, 4.24] |
| S2 flags known at origin | 316 | 2.46% | 5.06% [2.86, 7.71] |
| S1 no flags removed | 330 | 3.79% | 5.74% [3.53, 8.35] |
| S3 S2, events after arXiv v1 (2022-09-20) | 239 | 2.98% | 5.55% |

DRB: R0 6.5% pooled 3σ miss; S2 7.5%; S1 9.6%.

1. **The published cohort uses hindsight flags.** The excluded planets were
   flagged in DRD, whose fit includes the same 2022–2023 TESS data that are
   being scored. Removing them removes many of the failures. With only the
   flags available at issue, the DRC 3σ miss rate rises from 1.66% to 2.46%
   per measurement and to about 5% per planet. ExoClock IV's statement that
   problematic Ariel observations will be "below 2.0%" depends on this choice.
2. **The estimand matters.** The planet-balanced miss rate is roughly twice
   the measurement-pooled rate. Densely observed, well-behaved planets
   dominate the pooled figure.
3. **About 35% of the DRC test measurements (1269 of 3621 under S2) precede
   any public DRC artifact.** They are valid observation-cutoff hindcasts, not
   operational forecasts (Track B, not Track A).
4. **The scored quantity is mostly TESS measurement error.** For DRC the
   forecast contributes a median 13% of σ²_O−C. It exceeds half in only 9% of
   measurements; for DRB it is 36% and 37%. A forecast-free test
   (`tess_measurement_calibration.csv`) uses scatter within a TESS visit
   (≥3 transits within 20 days, 4563 events, 349 planets). Quoted σ_Tmid are
   about 7–11% too small (robust scale 1.07, RMS 1.12), with only 64.5% inside
   1σ. ExoClock IV reads DRC's 62.3% as "almost following the normal
   distribution", but the TESS error bars alone produce most of that 1σ
   shortfall. Table 5 therefore says little about whether the ephemeris
   uncertainties are calibrated.

## 5. Covariance and time-system completeness

`covariance_completeness.csv` covers 1250 planet-releases.

- **No release publishes Cov(T0, P).** In every release the published zero
  epoch is the integer epoch nearest the weighted-mean pivot of that release's
  inputs: |Δ| < 0.5 epoch for 99% (DRB), 94% (DRC) and 95% (DRD) of
  planets, and at most 11 (DRB) or 6 (DRC, DRD) epochs. As a result the implied |corr(T0, P)| is at most 0.03 for DRB and
  0.09 for DRC and DRD. It exceeds 0.05 only for 4 planet-releases, all in the
  TOI-216 TTV system. Omitting covariance is a negligible approximation for
  this benchmark: tier *reconstructed, negligible*.
- **The DRB refit reproduces the issued values** from the released per-planet
  inputs, with the published scaling factors: T0 within ±6 s, P within
  0.05 s, and σ_T0 and σ_P within ±17% (median ratio 1.00). The residual σ
  differences suggest ExoClock used posterior rather than WLS uncertainties.
- **The DRC and DRD refits** (assuming `all_mid_time_data.txt` is the fitted
  input set) reproduce P to within 0.1 s for 97% (DRC) and 92% (DRD) of
  planets. TOI-216.01/.02
  fail, as expected for a strong-TTV system.
- **Time standard.** All releases state BJD_TDB. DRB inputs mix ExoClock and
  literature timings that ExoClock converted, and the conversion inputs are
  not in the release. The outcome TESS timings are SPOC-derived BJD_TDB
  through the ExoClock pipeline. The status is *stated by release*, not
  independently verified.
- **DRB training duplicates.** 110 of 180 planets have more than one timing on
  the same date, for example three 2014-03-16 HAT-P-12b timings from one paper.
  Whether they are distinct exposures is unresolved; this affects the
  training weights, not the outcomes.
- **Outcome independence.** By date alone, TESS 2022+ outcomes are disjoint
  from DRB and DRC inputs (latest inputs 2020-12-30 and end-2021). The
  exposure-level lineage (sector, cadence IDs) and the mid-time prior used by
  the ExoClock TESS fits are not in the release (`lineage_date_only`,
  `outcome_prior_unverified`).

## 6. Recommendation: **continue, with the extension re-aimed**

Track R is complete and exact. Track A on the 2022–2023 era is feasible but
already inspected, so it is development only. The pilot changes which
extension is worth testing:

1. **Primary extension:** a variance-components forecast evaluation,
   Var(O−C) = a²σ²_Tmid + b²σ²_pred(h) + τ²(h). Here *a* is identified
   forecast-free from within-visit scatter, and *b* and τ come from between-
   visit means as functions of horizon. Use planet-balanced weights,
   origin-only flags and host-cluster uncertainty. The pilot suggests the
   published benchmark cannot separate forecast miscalibration from
   measurement miscalibration, and that its cohort rule drops failures.
2. **Untouched evaluation era:** DRD was issued 2025-11-17/18 (OSF and arXiv).
   TESS transits from 2025-11-19 onward are in no ExoClock release and have
   not been inspected. Freeze the protocol, then measure those mid-times with
   a pre-specified, forecast-independent pipeline. That gives a genuine
   prospective test of DRD as issued, including the recalibration (a, b, τ)
   learned on 2022–2023.
3. Before any novelty claim, complete the citing-literature sweep of
   ExoClock IV (T001; only two quick searches so far found no extension of
   Table 5).
