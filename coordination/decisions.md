# Decision log

Record substantive choices and the evidence that changed them. This is a working
scientific record; a `proposed` item is not a frozen preregistration.

| ID | Date | Decision / rationale | Status |
|---|---|---|---|
| D001 | 2026-11-04 | Start with exoplanet transit forecast reliability, reflecting Barry's experience in retrospective model evaluation. | User choice |
| D002 | 2026-11-04 | Treat ExoClock IV Table 5 as mandatory prior work and a reproduction target. The broad validation idea already exists. | Adopted |
| D003 | 2026-11-04 | Separate reproduction R, issued-artifact evaluation A and chronological refits B. | Adopted |
| D004 | 2026-11-04 | Investigate DRB forecasts and later TESS outcomes first; add DRC after the first provenance chain works. | Proposed operational starting point |
| D005 | 2026-11-04 | First paper emphasises horizon-dependent calibration/precision and one earlier-trained correction. Scheduling optimisation is ancillary. | Proposed scope |
| D006 | 2026-11-04 | Use full covariance, explicit time conventions, independent observation lineage and historical availability. Unknowns stay unknown. | Adopted |
| D007 | 2026-11-04 | Use a small Python/NumPy core; permit R as an independent implementation or later analysis layer. | Seed implementation choice |
| D008 | 2026-11-04 | Use equal-planet, then equal-origin/event summaries and host-cluster uncertainty for the main proposal; retain measurement-weighted reproduction separately. | Proposed analysis |
| D009 | 2026-11-04 | Defer final cohort, lead-time bands and evaluation era until metadata feasibility, without inspecting the final outcomes. | Open scientific design |
| D010 | 2026-11-04 | Do not infer an unconditional missed-transit rate from a catalogue of successfully measured events. | Adopted estimand boundary |
| D011 | 2026-11-04 | Repository licence, final name and eventual collaborators remain owner choices; no external remote or contacts created. **Updated by Claude:** licence and remote are settled by Barry's 2026-11-02 Open-by-default policy (MIT code, CC BY-SA 4.0 content, public `BWBrook/transit-forecast-audit`). Final name and collaborators remain open. | Partly resolved |
| D012 | 2026-11-04 | Claude. Treat the OSF version-1 release files (hashes in `results/pilot_v1/source_manifest.csv`) as the issued forecast artifacts. Every file has a single OSF version, uploaded before the journal publication date. The OSF upload proves existence at that time, not public visibility, so the conservative issue date stays the journal date. arXiv v1 and the OSF upload are sensitivity anchors. | Adopted |
| D013 | 2026-11-04 | Claude. Availability anchors: DRB training end 2020-12-31, OSF 2021-10-27, arXiv 2021-10-26, journal 2022-02-09. DRC: 2021-12-31, OSF 2022-09-27, arXiv 2022-09-20, journal 2023-02-14. DRD: 2023-12-31, OSF 2025-11-17, arXiv 2025-11-18, journal 2026-02-11. Encoded in `scripts/reproduce_table5.py::ISSUE`. | Adopted |
| D014 | 2026-11-04 | Claude. Every TESS outcome dated 2022-01-01 to 2024-01-03 (the DRD mid-time file) is now **inspected development material**. It may train the recalibration but can never serve as untouched evaluation. | Adopted (invariant 10) |
| D015 | 2026-11-04 | Claude. Track R is complete. Table 5 reproduces exactly for DRB and DRC; DRD differs by one measurement at z≈1. The published definition excludes the 42 DRD TTV-flagged planets, which is screening on information that postdates the forecasts. The project's primary cohort rule therefore uses **flags known at origin only**: DRB's own non-linear flag, or the 19 DRC TTV planets. Hindsight flags appear only as a reproduction sensitivity. | Adopted (invariant 9) |
| D016 | 2026-11-04 | Claude. Covariance tier for ExoClock releases: *reconstructed, negligible*. The published T0 sits at the weighted pivot, giving abs(corr) ≤ 0.09 (≤ 0.05 except TOI-216). Report the sensitivity bound and do not impute zero silently. Evidence: `results/pilot_v1/covariance_completeness.csv`. | Qualified by D021; not recovered posterior covariance |
| D017 | 2026-11-04 | Claude. Primary extension is re-aimed to a **variance-components evaluation**: Var(O−C) = a²σ²_Tmid + b²σ²_pred(h) + τ²(h). *a* is identified without any forecast, from scatter within a TESS visit; *b* and τ are fitted on the 2022–2023 development era. The reason is that for DRC the forecast contributes a median 13% of σ²_O−C, and the TESS σ alone are about 7–11% too small, so Table 5 coverage confounds measurement and forecast calibration. Replaces the single-multiplier proposal in `configs/pilot_provisional.json` once confirmed by independent review. | Not accepted as stated; attribution and grouping corrected by D022; model remains proposed |
| D018 | 2026-11-04 | Claude. Proposed untouched era: DRD as issued (OSF 2025-11-17) against TESS transits from 2025-11-19 onward, which are in no ExoClock release and have not been inspected. These would be measured by a pre-specified pipeline that is independent of the forecast. Freeze the protocol (T009) before any of these light curves is fitted. A secondary observation-cutoff hindcast era is 2024-01-04 to 2025-11-17 (after DRD's training cutoff but before its issue). | Proposed |
| D019 | 2026-11-04 | Claude. Primary summaries are planet-balanced with host-cluster bootstrap. Measurement-pooled results are reported only for reproduction. In the pilot the planet-balanced 3σ miss rate is about twice the pooled rate. | Adopted (confirms D008) |
| D020 | 2026-11-04 | Codex. Independent base-R parsing/scoring of eight hash-verified artifacts exactly reproduces DRB and DRC Table 5 columns; DRD retains its one-count boundary mismatch and Initial remains unreproduced. The 42-flag rule and denominator are a numerically supported reconstruction, not recovered publisher code. Raw row trace, runtime and results: `results/pilot_v1/independent_review/table5_*`; analysis: `docs/independent_review.md`. | Adopted; qualifies D015's full-completion wording |
| D021 | 2026-11-04 | Codex. Keep issued Cov(T0,P) missing. Published weighted-pivot methods and released-input WLS support a conditional C2 approximation where source-fit/input equivalence is credible; material mismatches remain C3/sensitivity. Reconstructed rho with published marginals changes Track R total variance by at most about 0.27%/0.98%/2.94% (DRB/C/D), but these are sensitivities, not posterior bounds. Not all published pivots are the nearest integer to the WLS pivot. | Adopted qualification of D016 |
| D022 | 2026-11-04 | Codex. The original 20-day consecutive-gap rule chains 333/425 groups beyond 20 days (maximum 378.6 days). Capping total span and fitting a local slope leaves RMS 1.0968 across 4173 retained timings/336 planets, but identifies conditional local dispersion, not measurement multiplier a. Synthetic counterexamples show exact confounding with white latent jitter and blindness to common offsets. Catalogue outcome selection further conditions the sample. Require joint residual covariance and recovery simulations before fitting a,b,tau as separable components. | Diagnostic correction adopted; D017 model still proposed |
| D023 | 2026-11-04 | Codex. Barry's chat instruction is to keep TESS light curves dated after 2025-11-18 unopened until protocol freeze (paraphrase, 2026-11-04). This lock is stronger than D018's fitting-only wording and remains in force. OSF upload/arXiv submission are not verified first-public availability; strict Track A retains journal 2026-02-11 as conservative DRD anchor pending exact-parameter availability evidence. The sealed interval is not automatically the eligible issued-forecast interval. | Adopted; user boundary and chronology clarification |
| D024 | 2026-11-04 | Codex. Continue the pilot, narrow the candidate extension to availability-aware, component-aware forecast evaluation with a later investigator-unseen test. TESS-only uncertainty checks and extra scatter already appear in Ivshina & Winn (2022); injection-recovery validation also has prior art. T001 remains open because a complete citation graph was unavailable. Next: development-event lineage and timing/injection feasibility, then identifiable covariance model and protocol freeze. | Adopted next gate; no novelty claim or frozen model |
| D025 | 2026-11-04 | Codex. Barry explicitly said "My call is \"track it\"!" in this chat about `docs/gpt-6-pro_ideation.md`. Track the supplied document unchanged as historical ideation, not current findings. | User-authorised version control |
| D026 | 2026-11-05 | Claude. The local TESS excess scatter scales with σ_Tmid rather than adding as white jitter. Over 4173 events and 336 planets in span-capped groups, the scale+jitter REML fit gives a = 1.087 (planet-bootstrap 1.043–1.117) and τ ≤ 11 s. The LR for scale given jitter is 27; for jitter given scale it is 1.5. Binned z-RMS is flat in σ. This answers D022's fixed-σ counterexample, but not σ-proportional physical variance or selection. Use a = 1.09 as a fixed outcome scale with sensitivities 1.0 and 1.2 until T015 injections test it. Evidence: `results/pilot_v1/local_noise/`, `docs/development_tranche2.md` §1. | Conditional refinement accepted under D030; not measurement-error attribution |
| D027 | 2026-11-05 | Claude. Forecast miscalibration is heavy-tailed between planets. An event-level Gaussian with shared ephemeris covariance gives b ≈ 98 (DRC), and a discrete failure mixture is multimodal. A two-stage model is adopted for development: robust visit means, then V_p = se² + b²λ_p XCX′ with log λ_p ~ N(0, s²). DRB: b = 2.25 [1.87, 2.72], s = 1.09. DRC: b = 0.98 [0.71, 1.28], s = 3.13 [2.78, 3.74], with 15 of 316 planets at λ > 10 (11 of them TESS-era systems). Recovery on the real DRC design is unbiased for (b, s) in (1, 0), (1, 1), (1.5, 1), (1, 2.5) and the fitted values. The primary calibration estimands become (b, s) and the planet-level tail fraction; pooled k-σ coverage is secondary. Evidence: `results/pilot_v1/variance_components/`, §2. | Point estimates supported; tail labels and interpretation superseded by D031; original intervals not independently qualified |
| D028 | 2026-11-05 | Claude. T016 metadata inventory (tess-point pointings, Exoplanet Archive coordinates, no photometry). 224 DRD planets on 206 hosts fall in sectors S98–S110, already observed, with about 5071 DRD-predicted transits. 171 planets and about 4006 transits fall in windows starting after the DRD journal date. Median DRD forecast SD there is 1.05 min, and the forecast's median share of σ²_O−C is about 23%. Sector windows are approximate (midtime ± 13.7 d); the official orbit table failed TLS here and is needed at freeze. Evidence: `results/sealed_inventory/`. | Approximate inventory only; already-observed and strict-A counts not accepted under D033 |
| D029 | 2026-11-05 | Claude. Proposed prospective extension: issue a heavy-tailed predictive distribution for each DRD ephemeris (scale mixture fitted on 2022–23, optionally with issue-time predictors of λ). Score it against DRD's Gaussian-as-issued on the sealed era with proper scores, planet-balanced, host-clustered. S98–S100 are Track B, S101 onward Track A (D023). | Proposed; for T006/T009 |
| D030 | 2026-11-05 | Codex. Independent error-contrast REML reproduces a=1.086576, tau=5.005 s and LR 27.39/1.48. A 400-replicate host bootstrap gives a 1.04984–1.12091; the tau percentile endpoint is 11.56 s, not a universal physical bound. Accept a=1.087 as a development sensitivity and the distinction between common scale and common homoscedastic jitter; retain selection, sigma-proportional variance and removed-offset limitations. `docs/tranche2_independent_review.md`, `results/pilot_v1/tranche2_review/noise_*`. | Adopted conditional refinement; T015 required |
| D031 | 2026-11-05 | Codex. Stable SVD likelihood plus high-order/adaptive integration confirms DRB (b,s)=(2.24949,1.09314), DRC (0.97626,3.14868). Continuous posterior medians give DRC 29 above lambda=10 and 9 above 100, replacing 15/10 from coarse nodes. This classification is distinct from posterior expected counts and population tail probability (~23.2% above 10). Original rank-two algebra fails at extreme mixing scales. Use stable reference code before extension, and requalify posterior summaries and host-aware uncertainty. `mixture_*` review artifacts. | Numerical correction adopted; model and prospective score choice remain proposed |
| D032 | 2026-11-05 | Codex. Three issue-release predictors were explored in the marginal mixing likelihood using five host-held-out development folds. Training span improves the planet-balanced per-window log score versus constant mixture by 0.02709 nats [conditional paired-host interval 0.00673,0.05399]; epoch count and TESS inclusion lack clear gains. Literature-only has no variation; historical multiplicity unresolved. All 1264 held-out densities agree with adaptive integration within 2.41e-7. Nominate training span for chronological development validation, with no final predictor choice or freeze. `metadata_*`, `predictor_*` review artifacts. | Exploratory development evidence; no sealed or causal claim |
| D033 | 2026-11-05 | Codex. Official HEASARC calendar metadata shows extended S98, interrupted S99, S100 straddling DRD availability and S110 still in progress on 5 November. The old day-after-publication constant is one UTC day early (2461082.5 vs intended 2461083.5). Do not classify S100 wholly as Track B or count S110 future predictions as observed. Exact target windows/product availability and time-system handling remain required; this review does not recompute the approximate inventory counts. `schedule_*` review artifacts. | Inventory qualification adopted; metadata-only refresh before freeze |
| D034 | 2026-11-05 | Claude. T015 development validation. A forecast-independent pipeline (blind BLS, ±60-min uniform timing prior, sector-shared batman shape, β·sqrt(χ²_ν) error scaling) timed 27 SPOC 120-s transits of HD209458b, WASP-69b, WASP-80b and HAT-P-12b in S49–S56. All 27 match ExoClock DRD mid-times (median −2.7 s, max \|z\| 0.66; a same-photon pipeline check). Across 261 real-noise injections, z-RMS is 1.03 [0.90, 1.17] with scaled σ and 1.25 with white σ, and bias is −1.7 s [−3.9, 0.1]. This implies ExoClock σ are about 1.12× too small [0.96, 1.29], consistent with D026/D030 but weak. WASP-80b's DRB miss is not a measurement artefact. FFI and faint targets are untested. Evidence: `results/t015/`, `docs/t015_pipeline_report.md`. | Reviewed under D035: conditional recovery accepted; general scale and per-outcome freeze claims not accepted |

| D035 | 2026-11-05 | Codex. D034 injection point estimates reproduce (scaled z-RMS 1.03318, white 1.25435), but 260/261 fitting intervals overlap and 26 clusters are parent transits from only four hosts/five products. Same fitted shapes and post-PDCSAP injections support conditional recovery, not full-pipeline or ExoClock-wide calibration. Do not freeze per-outcome z-RMS scaling. A synthetic check exposes a one-second quantile-grid bias; the TSTOP guard occurs after Lightkurve table reading and its stated boundary is inconsistent. All five verified products are from 2022; no protected access occurred. Evidence `4c369df:results/t015_review/`, `docs/third_turn_review_2026-11-05.md`. | Audit accepted; Claude retains pipeline corrections and stratified validation |
| D036 | 2026-11-05 | Codex. Completed production mixture: stable SVD likelihood, checked 384-node quadrature, continuous posterior summaries, explicit optimizer diagnostics and 400 host resamples per release. DRC b=0.97626 [0.71156,1.35722], s=3.14869 [1.57636,4.21090]; intervals are percentile bootstrap conditional on fixed a/cohort/covariance convention/family. Original artifacts retained; new outputs `4c369df:results/pilot_v1/variance_components_v2/`. | Implemented and independently checked; no model qualification for sealed scoring |
| D037 | 2026-11-05 | Codex. Observation-cutoff DRC development hindcast trains on 2022 and scores 2023–2024-01-03, with fixed a=1, 133 early/206 late planets. Span point gain is 0.01276 nats/window versus constant mixture, but joint-host resampling with early refitting gives percentile range −9.07197 to +0.04295. Some span fits lose heterogeneity and reverse slope, becoming overconfident for short-baseline extrapolations. Independent higher-order/adaptive replays reproduce four extreme losses. Do not select the span rule; any regularization/tail constraint needs further development validation. Predictors were nominated after inspecting the era; historical availability is unresolved. `4c369df:results/pilot_v1/chronological_calibration/`. | Adverse development evidence; no prospective gain or freeze |
| D038 | 2026-11-05 | Claude. Corrected T015 per D035, then prespecified a stratified validation before requesting any new photometry. Corrections: trapezoid CDF on a 10-s grid refined to min(1 s, σ/25); gap-aware β with N−3 degrees of freedom; a guard that checks MAST t_max before the request and header TSTOP ≤ BTJD 3313.49 before flux is read; exposure taken from TIMEDEL. Re-timing the 27 D034 transits moves them +1.0 s (range 0.7–1.9) and leaves σ unchanged (median ratio 0.99). Design: 48 single-DRD-planet hosts, 12 per Tmag stratum by hash rank, odd ranks calibration and even ranks validation; TESS-SPOC 200 s plus paired SPOC 120 s; two injection runs per product rerunning BLS, shape and timing with real windows removed; disjoint windows within each product; SAP sensitivity; acceptance criteria fixed in advance. | Design `26590c3:docs/t015_validation_design.md`; corrected re-timing `results/t015_corrected/` |
| D039 | 2026-11-05 | Claude. The prespecified primary test passes. TESS-SPOC 200-s PDCSAP on 18 validation hosts (263 injections): 95% coverage 0.958 [0.934, 0.981], z-RMS 0.981 [0.920, 1.045], bias +0.08σ [−0.07, 0.19], failures 7.4%. SPOC 120 s also passes (0.951, 0.970, +0.09σ). The secondary multiplier is not adopted: calibration k = 0.92 worsens validation coverage. No Tmag stratum is freeze-ready under the per-stratum rule (3–6 hosts), mostly on the point-estimate bias criterion. Faint stars have conservative σ (z-RMS 0.88–0.92). ICC of z is about 0 by run and by host, so no shared bias component is detected. For the same real transits, our σ exceed ExoClock's by 1.09–1.11 across 40 hosts; this does not identify a multiplier (D035). FFI and 2-min timings agree (322 pairs, median +0.5 s, σ ratio 1.01). Gaps: periods over 12 d, multi-planet hosts and periods under 1.4 d. | Proposed for T009, pending Codex review; per-stratum confirmation sample needed. `results/t015_validation/`, `docs/t015_validation_report.md` |

### D040 — Proposed two-sprint programme and review cadence

- Date / responsible agent: 2026-11-05, Codex; draft for Claude's revision.
- Authority: Barry's chat requests more ambitious autonomous tranches and the
  sequence draft → Claude revision → Codex sprint 1 → Claude sprint 2 →
  Codex review/fix of sprint 2 → Claude review/fix of sprint 1 → reconciliation
  (paraphrase). Routine stages do not require another approval round.
- Proposal: `docs/two_sprint_plan_2026-11-05.md`. Build the complete development
  forecast experiment, then qualify the outcome method and integrate a candidate
  freeze package plus article, broad-audience brief and agent guide. Each sprint
  has deliverables, scientific acceptance criteria, ownership and failure paths.
- Interpretation: D038–D039 remain pending independent review; this planning
  entry accepts none of their scientific claims. Retain the protocol's primary
  interval-score contrast as the draft recommendation. Missing issued covariance
  and outcome-error transfer must be resolved or reflected in narrower claims.
- Boundary: protected photometry remains closed through both sprints and
  counter-reviews. Reconciliation determines freeze readiness. No publication,
  protected-data access or substantive sprint implementation occurs in this turn.
- Status: proposed; Claude to critique and revise before sprint 1 begins.

### D041 — Claude's revision of the two-sprint plan

- Date / responsible agent: 2026-11-05, Claude (Opus 5.5).
- Change: the revision section of `docs/two_sprint_plan_2026-11-05.md`
  (R1–R9, I1–I3, A1–A2) governs wherever it conflicts with the D040 draft.
- Substance:
  - The DRB→DRC release-transfer hindcast is a primary development
    comparison, because DRB b = 2.25 and DRC b = 0.98.
  - The comparator set is closed at M0–M3. M2 is a tails-only mixture with
    b = 1.
  - The primary 95% interval score is standardised by each event's issued
    predictive SD, which keeps it proper.
  - The timing prior is centred on the data, so forecast tails are not
    truncated. Catalogue-period identification is accepted with a ±0.5%
    window and a blind epoch search.
  - Outcome-error transfer is tested by remeasuring the development cohort
    with our pipeline and refitting under both error conventions.
  - Confirmation: 120 fixed new hosts, 30 per stratum, with a continuous Tmag
    model and 90% interval criteria. The margins are tied to sprint 1's
    outcome-scale tolerance. The per-stratum 0.1σ bias margin is retired as
    unattainable (sizing: `scripts/t015_confirmation_sizing.py`), and D039's
    verdict is unchanged.
  - Short periods get a two-part window.
  - Extension to P > 12 d and multi-planet hosts is gated on sprint 1's
    inventory.
  - Claude checks sprint 1's interface once at the start of sprint 2.
- Status: revision proposed. Codex's acceptance or counter-proposal
  reconciles it, then sprint 1 begins. No implementation or new photometry
  in this turn.

### D042 — Execute the revised programme with explicit scientific qualifications

- Date / responsible agent: 2026-11-06, Codex.
- Accept D041's sprint route and closed M0–M3 comparison. Specific execution
  qualifications are recorded at the top of
  `docs/two_sprint_plan_2026-11-05.md` before new fits: conditional rather than
  issue-fixed outcome-error score weighting; M0 reconstructed covariance;
  M2 changes predictive width; identification selection remains possible;
  exact 95% versus 2-sigma quantiles and likelihood/prior semantics; tolerance
  anchored to an explicit outcome convention; and metadata-based OR extension
  gate. No new regularisation prior or open model search.
- Read D038–D039 as claims under audit. Carry out the complete sprint 1 with
  independent timing, metadata and literature work while the parent implements
  forecast scoring and design precision. Preserve null/failure outcomes.
- Authority: Barry's current handoff and already authorised two-sprint cadence.
  Protected outcomes remain closed; no protocol freeze or final evaluation.
- Status: adopted for sprint 1 execution; qualifications remain visible for
  Claude's sprint 2 interface check and scheduled counter-review.

### D043 — Public-release availability and bounded novelty resolved for sprint 1

- Date / responsible agent: 2026-11-06, Codex.
- Evidence: `docs/sprint1_literature_review.md`, OSF public-node/file logs and
  `results/sprint1/literature/`; 82 returned OpenAlex forward citations screened.
- Decision: DRD public availability is 2025-11-18 09:43:24 UTC. Use the next
  whole day for strict-A metadata eligibility; retain journal-date sensitivity.
  The DRC timing file followed its forecast by 53 seconds, so the original
  release-transfer comparison is a proxy. The delayed-origin reconstruction
  has available inputs but was constructed now and is not an issued correction.
- Novelty: continue with a bounded combination claim; no first claim for
  retrospective forecasts, covariance propagation or heavy tails. Citation
  index disagreement and unavailable ADS enumeration remain search limits.
- Status: adopted development interpretation. Protected data remain closed.

### D044 — Forecast experiment complete; primary improvement and tolerance unqualified

- Date / responsible agent: 2026-11-06, Codex.
- Evidence: `docs/sprint1_report.md`, independent `sprint1_scoring_review.md`,
  `results/sprint1/forecasts/`, `comparison.csv`, `handoff.json`.
- Decision: retain M0–M3 and report all development comparisons. At a=1.087,
  C2, M2–M0 standardised IS95 is -2.445 [-5.756, 0.187] for release transfer
  and -2.628 [-6.351, 0.067] chronologically. Both are inconclusive with 400
  host resamples and refitting. Coverage/log-score gains are tail-risk evidence,
  not typical-planet improvement. Most planets have worse interval scores.
- Sensitivity: point signs remain negative on a=0.85–1.25; same-decision tested
  region around reference is 1.05–1.25. It does not certify outcome calibration.
  I3 therefore supplies a null measurement tolerance, not reciprocal A2 margins.
  C2, zero and rho endpoints all remain inconclusive at reference.
- Interface: I2 is executable; exact 95% quantiles and I1 provenance are checked,
  duplicate reductions/failures retained, non-Gaussian likelihood semantics
  explicit. Independent event-cycle mapping remains Claude's sprint-2 work.
- Validation: numerical audit, direct adapter replay and 70 passing tests;
  source-stable run receipts preserve hashes. Development only; no rule freeze.

### D045 — Outcome validation requires repair; metadata extension passes R8

- Date / responsible agent: 2026-11-06, Codex.
- Evidence: `docs/sprint1_timing_audit.md`, `sprint1_inventory.md`,
  `sprint1_precision.md` and corresponding `results/sprint1/` tables/receipts.
- Decision: D039 successful-event calculations reproduce, but pooled
  freeze-readiness and the 7.4% mixed-denominator failure interpretation do not.
  13/48 planned primary runs do not succeed; missing truth events prevent an
  end-to-end event recovery estimate. Host weighting changes the bias verdict.
  Uncorrected log-host-MSE endpoints fail a known-Gaussian coverage control.
- Claude owns the attempt/truth ledger, one-to-one matches, arithmetic/declared
  host target, validated endpoint model, removal/shape/identification controls,
  development remeasurement and convention-specific model refits. A2 margins
  require a scientifically justified amendment before confirmation download;
  no tolerance is inferred from an inconclusive score contrast.
- R8: 156 core plus 28 extension planets (184 on 175 hosts) pass the metadata
  arm, +17.95%; 3399 opportunities are not confirmed outcomes. Allow extension
  implementation subject to identification qualification. Simulated SE does
  not decrease; core and union are different target populations.
- Precision: 4000-replicate fixed-rule stress simulations condition on assumed
  future measurement precision and model truth. They omit refit uncertainty
  (separately analysed) and do not qualify protected performance or recovery.
- Status: sprint 1 complete; Claude's sprint 2 interface check and execution
  next, then the agreed reciprocal reviews. No protected access or freeze.

### D046 — Sprint-1 interface accepted (R9)

- Date / responsible agent: 2026-11-07, Claude (Opus 5.5).
- Evidence: replay of `make_forecasts` then `score` on the release-transfer development events reproduces `scores.csv` byte for byte; 70 tests pass.
- Decision: I2/I3 are accepted as delivered, including labels, the null certified tolerance and the catalogue-route qualification. The I1 production path was exercised in sprint 2. 21 of 404 non-Gaussian grids are truncated by the ±60-min prior and are refused by the adapter, so they are recorded as failed attempts (S2-05).

### D047 — Outcome rule t015v3 and amended A2, frozen before confirmation

- Date / responsible agent: 2026-11-07, Claude.
- Evidence: `docs/sprint2_outcome_design.md`, frozen at `2c39f0a` (source hash `4b5c9602a29b`); `results/sprint2/dev/`, `estimand_negative_controls.json`, `identification_summary.json`.
- Decision: repairs S1-01, S1-02 and S1-04.
  - an intended-truth ledger with a gated one-to-one assignment;
  - equal-host estimands, with an arithmetic Tmag model replacing log-MSE;
  - catalogue-period identification with a blind epoch, and R7 windows;
  - exact 95% quantiles and likelihood grids;
  - removal, subtraction and shape-misspecification controls.
- Margins: u = 1.10, mean-z ±0.15, coverage lower bound 0.93 and Tmag endpoints [0.80, 1.15]. They are derived from the distortion that outcome errors cause in forecast coverage (at most about 2.5–2.8 points). This replaces the null A1 tolerance; it is not inferred from the inconclusive contrast.
- Primary rule t015v3c: σ × g(Tmag), fitted on the 45 inspected development hosts. Secondary rule: t015v3 without the multiplier.
- Status: superseded in outcome by D048–D049; the repairs are retained.

### D048 — t015v3c fails confirmation; one replication of t015v3 prespecified

- Date / responsible agent: 2026-11-07, Claude.
- Evidence: `results/sprint2/confirm/summary.json` (120 hosts; 106 timed; 1,496 events); `docs/sprint2_replication_design.md`, committed at `9375b3c` before any replication download.
- Decision: t015v3c fails coverage (lower bound 0.922) and the Tmag-13.5 endpoint ([1.062, 1.195]): the development multiplier over-corrected.
  - t015v3 passed every criterion as the secondary rule, which by design does not qualify it.
  - A single replication of fixed t015v3 on 120 never-sampled frame hosts was prespecified, with no further replication allowed.

### D049 — Replication fails: outcome pipeline not ready

- Date / responsible agent: 2026-11-07, Claude.
- Evidence: `results/sprint2/confirm2/summary.json` (120 hosts; 102 timed; 1,377 events); `docs/sprint2_report.md` §3.
- Decision: t015v3 fails z-RMS (1.095 [1.002, 1.214]), coverage (0.929, lower bound 0.908) and both Tmag endpoints. The outcome pipeline is **not ready** under prespecified criteria. No margin is relaxed and no host is changed.
- Exploratory, post-hoc: hosts with at least four timed transits are calibrated in both confirmations (z-RMS 0.992 and 1.012; coverage 0.944 and 0.953). The failure sits in hosts with one to three transits.
  - This proposes a metadata-defined narrower scope (S2-02).
  - That scope requires its own prespecified test before any freeze.

### D050 — Convention transfer accepted; candidate freeze package not freeze-ready

- Date / responsible agent: 2026-11-07, Claude.
- Evidence: `results/sprint2/forecasts/convention_comparison.json`, `diagnostic_wasp54_s50.json`, `candidate_parameters_t015v3.json`; `results/sprint2/freeze_candidate/`; `configs/candidate_freeze.json`.
- Decision: R5 transfer is accepted. On matched transits, ExoClock timings × 1.087, t015v3c and t015v3 keep the negative sign and the inconclusive decision in both designs.
- Remeasurement: 4,615 attempted and 3,946 timed events across 294 planets. Same-photon agreement with ExoClock: z-RMS 0.36, median difference −0.1 s.
- The single spurious timing (WASP-54b S50) moves the chronological all-timed M2 contrast from −1.37 to −0.08. It is a defect (S2-01), not an exclusion.
- Candidate package: 184 planets, 3,399 DRD events, draft forecasts and a 996-file access receipt with no violations. Not freeze-ready: the outcome rule is unqualified (D049), S2-01 and S2-05 are open, and the reciprocal reviews are pending.
- Next: Codex reviews and fixes sprint 2 under Barry's order. Protected outcomes remain closed.

### D051 — Independent correction reverses the frozen SPOC replication verdict

- Date / responsible agent: 2026-11-07, Codex (GPT-6.1-sol).
- Evidence: `docs/sprint2_review.md`, `sprint2_statistics_review.md`,
  `results/sprint2_review/statistics/`, independent reconstruction and regression
  tests. The original result tables remain unchanged.
- Defects: product preference was chosen after timing, substituting FFI after
  SPOC failures; asymmetric containment used -lo<=fitted-truth<=hi instead of
  -hi<=fitted-truth<=lo. Both are implementation errors against the frozen rule.
- Corrected frozen analysis: confirmation t015v3c still fails (105 timed hosts,
  1495 injections). Secondary t015v3 passes that sample. Replication t015v3
  passes all frozen criteria (100 timed SPOC hosts,1374 injections): RMS 1.0144
  [.9787,1.0509], coverage 0.9502 [.9382,.9611], mean 0.0690 [.0116,.1239], both
  endpoints and noise controls pass. FFI separately fails.
- Consequence: D049's replication-failure interpretation and C025's sparse-host
  explanation are superseded. Equal-host weights remain the declared target;
  no transit-count restriction, altered criteria or further replication.
- Scope: conditional calibration of the frozen sampled SPOC rule. The amended
  numerical implementation, end-to-end recovery, FFI and multi-planet extension
  are not qualified by this correction. Protected outcomes stay closed.

### D052 — Replication and pass margins have bounded development interpretations

- Date / responsible agent: 2026-11-07, Codex.
- Evidence: the two design commits `2c39f0a`/`9375b3c`, exact unchanged timing
  source, analytic margins and independent controls under `sprint2_review/`.
- Interpretation: the second test was an adaptive extension after primary
  failure, prespecified before its injection analysis, not part of the original
  one-confirmation plan. Of 120 hosts,82 had prior R5 contact and81 shared the
  same host-sector. Code freeze supports a bounded conditional test but does
  not alone guarantee a study-wide error rate or unseen-photometry independence.
- The margins reproduce under independent Gaussian forecast/outcome errors.
  They are an operational coverage-distortion budget, not a bound on general
  interval loss or all subgroups. Keep the frozen criteria for the corrected
  test; sprint1's certified measurement tolerance remains null.
- Controls: coverage and endpoints retain finite-design bootstrap error; report
  simulation uncertainty. No criterion is moved after seeing these controls.
- Status: adopted interpretation for counter-review, not protocol freeze.

### D053 — Numerical support repairs, descriptive convention agreement and candidate limits

- Date / responsible agent: 2026-11-07, Codex.
- Evidence: `docs/sprint2_timing_review.md`, `sprint2_claims_review.md`, source-
  guarded I1 replay and `results/sprint2_review/` receipts/hashes.
- Repair: existing mass-outside-fine/coarse-fine-shift flags now yield
  integration_unresolved and prevent Gaussian certification. The adapter also
  refuses unresolved timed rows. A separated 3% mode is the regression fixture.
  Root solving is accelerated with bounded CDF truncation error; the model and
  full log-density quadrature are unchanged. Changed timing source requires
  separate qualification; full-support likelihoods remain unresolved.
- Replay:2777 attempts,2291 timed (291 grids),37 integration failures plus313
  coverage,93 ID and43 edge failures. Exact-grid M2−M0 point loss -1.89681 versus
  -1.92237 under Gaussian approximation on identical surviving events; fixed
  old development parameters, no bootstrap/refit verdict from this replay.
- D050/C026 transfer acceptance is narrowed to descriptive sign/decision
  agreement in matched Gaussian approximations. Same-photon agreement does not
  establish measurement calibration or convention equivalence.
- The late original receipt hashes adapter bytes at run end, after edits, so
  it does not identify the old process's loaded source. Current guarded replay
  resolves this. Original60 output hashes and8 OSF hashes verify. Development
  source bytes behind an uncommitted hash and white-noise controls are missing.
- Candidate:184 planets,3399 opportunities retained; five near numeric time
  boundaries marked unresolved. This is not a UTC–BJD conversion. Identification,
  fixed intended-event denominators, multi-planet scope and exact eligibility
  remain open. No post-hoc majority-window rule was installed.
- Products: article/brief/guide corrected together; brief rendered and verified
  as two A4 pages. Next is Claude counter-review and reconciliation. No protected
  photometry or new samples were accessed.

### D054 — Claude counter-review accepts D051, qualifies D053; sprint-1 review finds no numerical defect

- Date / responsible agent: 2026-11-07, Claude (Opus 5.5).
- Evidence: `docs/claude_reciprocal_review_2026-11-07.md`;
  `results/sprint2_review/claude_amended_gate_check.json` and `white_noise.json`;
  `results/sprint2_review/claude_sprint1_review.json`.
- Sprint 2: both analysis defects were independently confirmed, and the
  corrected replication pass is accepted. The ≥4-transit scope (S2-02) is
  withdrawn. The integration gate is exactly evaluable on the frozen ledgers:
  SPOC passes in both samples (5 and 6 injections removed) and FFI fails the
  replication. The late bias of +0.07σ (interval excluding zero) is reported,
  not corrected.
- Provenance: commit `d9c1570` swept Codex's uncommitted edits to five files in
  the shared checkout; recorded here, history not rewritten.
- Sprint 1: tail numerics are exact against independent adaptive integration;
  no chronological in-sample leakage was found.
  - The release-transfer training window is in effect 2021-10-28 to 2021-12-30
    (172 events, 15 planets).
  - The inconclusive primary contrasts depend on 2–5 gain hosts: the sign
    reverses after dropping the top 3 (chronological) or 5 (release transfer).
    A fixed-parameter bootstrap would call release transfer an improvement, so
    refit uncertainty is decisive.

### D055 — Proposed reconciliation: ready only for a narrower declared question (awaiting Codex)

- Date / responsible agent: 2026-11-07, Claude; proposal, not adopted.
- Scope: core 156 planets, with the 28 extension planets exploratory; SPOC
  120-s PDCSAP; t015v3a, i.e. frozen t015v3 plus the integration fail-closed
  gate.
- Before freeze:
  - a prespecified >50%-of-covered-windows product gate (S2-01);
  - a fixed DRD-manifest attempt denominator;
  - UTC→BJD_TDB resolution of the 5 boundary events;
  - prespecified host-dependence secondary summaries;
  - a SPOC-only t015v3a candidate refit, hashed together with forecasts,
    code and roster at freeze.
- Opening protected outcomes remains Barry's decision after reconciliation.

## New entry template

### D0XX — short title

- Date / responsible agent:
- Question:
- Evidence and source/analysis paths:
- Options considered:
- Decision and scope:
- Consequences for code, protocol and manuscript:
- Validation / independent review:
- Status: proposed / adopted / superseded, with replacement ID if relevant.
