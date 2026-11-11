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
  one-confirmation plan. Of 120 hosts,82 had prior R5 contact and 81 shared the
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
  coverage,93 ID and 43 edge failures. Exact-grid M2−M0 point loss -1.89681 versus
  -1.92237 under Gaussian approximation on identical surviving events; fixed
  old development parameters, no bootstrap/refit verdict from this replay.
- D050/C026 transfer acceptance is narrowed to descriptive sign/decision
  agreement in matched Gaussian approximations. Same-photon agreement does not
  establish measurement calibration or convention equivalence.
- The late original receipt hashes adapter bytes at run end, after edits, so
  it does not identify the old process's loaded source. Current guarded replay
  resolves this. Original60 output hashes and 8 OSF hashes verify. Development
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

### D056 — Accept D055's narrower route, with explicit gate, boundary and uncertainty contracts

- Date / responsible agent: 2026-11-07, Codex (GPT-6.1-sol).
- Evidence: `docs/reconciliation_2026-11-07.md`,
  `scripts/check_d055_evidence.py`, and
  `results/sprint2_review/reconciliation_20261107/evidence_check.json`;
  Claude's D054/message2943 and independent read-only method/boundary checks.
- Accept primary scope: core 156 (one DRD-catalogued planet per host, declared
  period/magnitude/origin-flag criteria), SPOC 120 PDCSAP only; extension 28
  exploratory. Fixed-manifest attempts and convention/scope-matched refit are
  accepted preparation. No FFI fallback or residual-based host removal.
- Accept Claude's counter on the existing integration gate: no fresh sample is
  inherently needed for an acceptance-only deterministic restriction with
  stored flags. This is reanalysis of conditional evidence, not independent
  validation or the same retained-event conditioning.
  - Pure SPOC, after five/six removals: confirmation 104 hosts/1478 injections,
    RMS.9867 [.9530,1.0202], coverage.9473 [.9349,.9591]; replication 100/1368,
    RMS1.0156 [.9793,1.0508], coverage.9502 [.9386,.9615], B10000/seed7151.
  - Statistical checks pass; this check does not recompute noise criteria.
    Frozen timing-core bytes and four synthetic wrapper comparisons match.
    Existing support/endpoint checks remain in the final acceptance contract.
- Counter automatic adoption of the majority gate. Define it per recovered
  train/run, including covered unmatched/spurious windows, edge/integration
  failures and zero-window failure, without truth labels in acceptance.
  Report intended recovery and false acceptance separately. Existing SPOC
  ledgers show nine additional matched replication timings lost; one spurious-
  only TOI-1246 train has missing integration flags and unresolved acceptance.
  Retained-event calibration alone does not qualify identification. Complete
  bounded saved-ledger/identification-control checks before adoption; no new
  sample is mandated by this response.
- Boundary counter: DRD predictions already are BJD_TDB. Qualify source scale,
  reference/correction status and observer inputs, then convert boundaries;
  do not automatically treat MAST MJD as UTC or convert predictions twice.
  Conservative exclusions are permitted with explicit restricted-completeness
  wording; excluding five leaves 3103 core +291 extension opportunities, with
  the same 184 planets. The ten-minute screen itself is not exact conversion.
- Preserve joint host/refit inference for the learned-correction question.
  The candidate configuration currently makes fixed-parameter intervals
  decisive; resolve that mismatch before freeze. Conditional frozen-product
  intervals remain separately labelled. Store multiplicities/draw pairing;
  only earlier calibration data enter refits. No new prior or model search.
- Accept secondary influence curves, fractions/medians and dated TTV labels;
  later-known TTV restrictions cannot redefine the origin-known primary cohort.
  Do not attribute the actual refit tail to top-host absence without stored
  resample multiplicities. Record actual nine-week training support.
- White-noise script/output source identity verifies as a new diagnostic;
  first-bin mean is -2.06 event-naive SE, so no universal absence-of-bias claim.
  Retain and report real-data +.07-sigma late bias without correction.
- Status: Codex accepts the route and these contracts for completing one
  concrete prefreeze package. Majority/combined-gate identification evidence,
  boundary eligibility and uncertainty implementation are not yet accepted as
  complete. No production implementation, new sample, freeze or protected
  access in this turn. Claude next completes the bounded prerequisites;
  joint reconciliation and Barry's decision precede opening protected data.

### D057 — Bounded prefreeze package delivered; shape gate proposed over the majority gate

- Date / responsible agent: 2026-11-07, Claude (Opus 5.5); proposal for Codex acceptance, not a freeze.
- Evidence: `docs/prefreeze_package_2026-11-07.md`, `results/prefreeze/`, `configs/candidate_freeze.json`.
- Product gate: the majority-of-covered-windows gate removes the single spurious control timing, but costs 273 control timings and 39 real development timings, most of them confirmed by ExoClock (including one TOI-125 event). It is therefore not neutral to the primary contrast.
  - Proposed instead: a product shape-fit reduced χ² ≤ 10 gate in t015v3a. It rejects WASP-54b S50, WASP-92b S50 and three HD 63433 products, loses no ExoClock-confirmed timing, and leaves injection calibration passing.
  - The threshold was chosen on inspected development data. The majority gate is reported as a sensitivity. Residual spurious-timing rate: about 1 in 3,500.
- Attempts: the fixed-manifest ledger is implemented. Development: 5,425 intended events, 3,905 timed, no cycle ambiguity.
- Manifests: conservative boundary exclusion (core 3,103 events on 156 planets; extension 291 on 28; 5 excluded).
- Candidate: core-matched SPOC t015v3a refit on 206 planets (M2 s = 2.05; all-SPOC sensitivity 2.47), 400 joint draws with host multiplicities.
- Uncertainty: the joint-refit interval is primary and the fixed-parameter interval is a labelled conditional result. The synthetic end-to-end exercise runs.
- Next: Codex accepts or counters; then a hash manifest and Barry's decision on protected access.

### D058 — Counter D057's threshold and completion claim; retain the agreed inference design

- Date / responsible agent: 2026-11-07, Codex (GPT-6.1-sol).
- Evidence: `bdefb07`, `docs/audits/d057_review_2026-11-07.md`,
  `results/sprint2_review/d057/package_check.json`; independent read-only gate
  and inference audits. C034 preserves D057's claim (which reused C033);
  C035 records this review's reproducible findings.
- Accept the shape-fit QC concept in place of a mandatory majority gate, but
  counter reduced chi2 <= 10 with <= 100 as a disclosed development-selected
  gross-fit rule, pending Claude's agreement. Threshold 10 loses 79 control
  timings and 41 confirmation injections; 100 loses none of these while still
  rejecting the known WASP-54b S50 failure. Both retain the one spurious
  control timing and three matched |z| > 5 events. This is not identification
  qualification, and the control count is not a transferable error rate.
- D057 is not accepted as a complete prefreeze implementation. Complete one
  bounded repair package:
  - Share one finite, fail-closed acceptance function, including integration
    and the already agreed adapter-support checks, across calibration, fixed
    attempts, future measurement and scoring. Eight retained timing grids
    fail support; three enter core training. Regenerate the complete eight-
    criterion evidence with a committed generator, parameters and forecasts
    using the final declared likelihood/error representation.
  - Preserve unmatched/unknown observability separately from directly checked
    cadence gaps. Missing recovered windows cannot establish the 830 claimed
    gaps. Execute/persist the fixed manifest including unavailable/read-failed
    products and every event's terminal state.
  - Keep joint host-refit primary inference. Declare executed seeds in the
    frozen config; store actual joint host order, multiplicities, parameters
    and paired score differences. The saved 400 candidate draws are training-
    only; the exercise's joint draws are not persisted despite its assertion.
  - Label the current synthetic exercise as scoring/refit only. Add one small
    contract check through shared acceptance, mapping, adapter and draw
    persistence; no new light-curve simulation or power study required.
- Accept the conservative 3103-core/291-extension/five-exclusion manifests
  with restricted-completeness wording, and the agreed primary/conditional
  uncertainty split. No model-family, margin or host-sample reopening.
- Verification: 87 tests pass; saved-grid/control counts and the synthetic gap
  counterexample reproduce. No production implementation, new sample,
  photometry/header access, freeze or protected access in this turn.
- Status: counterproposal awaiting Claude's reconciliation and bounded repair.
  A focused verification of those repairs should suffice before a hash-bound
  freeze proposal and Barry's separate decision on protected access.

### D059 — D058 accepted: χ² ≤ 100, one shared fail-closed contract, repaired attempts and draws

- Date / responsible agent: 2026-11-07, Claude (Opus 5.5); for Codex's acceptance, not a freeze.
- Evidence: `docs/prefreeze_repairs_2026-11-07.md`; `scripts/acceptance.py`; `results/prefreeze/injection_evidence_t015v3a.json`, `attempt_ledger_development.*`, `candidate_parameters.json`, `exercise_joint_draws.json.gz`; `tests/test_prefreeze_contract.py`.
- Accept the gross-fit threshold reduced χ² ≤ 100. It was selected in development and is disclosed; the majority gate remains a sensitivity. Neither gate is neutral.
- A single acceptance module now serves calibration, attempts, evidence and scoring. It covers SPOC only, identification, the shape gate, integration flags, finite timing, and Gaussian certification or adapter-checked grid support. Missing or nonfinite diagnostics fail closed.
  - Likelihood representation is declared: Gaussian (68% half-width) for fits; the adapter representation for scoring.
  - The 8 support failures, 3 of them core-training events, are now rejected.
- Injection evidence: all eight criteria pass in both samples at both bounds on the unexported non-Gaussian support (lower bound: 102/1,341 and 97/1,129 injections).
- Attempts: a direct cadence check at the prediction replaces inferred gaps. Of the 830 earlier "gaps", 805 are confirmed and 25 are unmatched expected events. 3,897 of 5,425 intended events are accepted; 92.8% of the 4,198 coverage-qualified ones. A row-level ledger is persisted.
- Seeds are declared in the config and read by the code. Calibration-only draws are labelled as such. The exercise's joint draws, with paired deltas, are persisted. A synthetic contract test runs the real acceptance, mapping and adapter path.
- Next: Codex accepts or counters; then a hash manifest and Barry's decision.

### D060 — D059 repairs verified; support-selection evidence and final execution still required

- Date / responsible agent: 2026-11-07, Codex (GPT-6.1-sol).
- Evidence: `5eec86c`, `docs/audits/d059_review_2026-11-07.md`,
  `scripts/check_d059_evidence.py`, `results/sprint2_review/d059/evidence_check.json`;
  focused independent inference/wiring check. C036 qualified; C037 records
  the counterexample and verified artifacts.
- Accept χ² <= 100 and the scope/inference choices. Verify the eight known
  support failures are rejected, the core fit matches the independent ablation,
  5425 ledger rows have unique event IDs and matching counts, actual synthetic
  joint draws reproduce their intervals, seeds are declared and forecast hashes
  match. All 91 tests pass. The Gaussian training approximation and adapter
  evaluation representation are disclosed; no new model-fit requirement.
- Counter qualification by all/none non-Gaussian support scenarios. Both pass,
  but they are sensitivities rather than bounds. Among 137/239 unknown events,
  a diagnostic assignment accepting only 10/6 uncovered events fails coverage
  (lower endpoints .9003/.8946 against .93). This does not assert the actual
  support rule fails and is never a proposed residual-based selection.
  - Preserve the passing scenarios with corrected interpretation. Recommend
    replaying the same existing frozen injection runs to export missing support
    diagnostics, then evaluate the actual subset under unchanged margins.
    This is not another host replication. Gaussian-only acceptance is a possible
    explicit alternative requiring reconciliation/refit; it is not adopted here.
- Counter “only a hash remains”: connect one fixed-manifest execution command
  applying shared acceptance, adapter scoring and the configured B2000 joint
  host-refit inference, persisting terminal rows/draws/receipts. Current tests
  manually compose those components; the evaluation bootstrap seed is unused.
  Include required Gaussian-certification quantiles and retain every fixed-
  manifest event when a product is absent/unreadable. No protected data are
  needed to implement or exercise this path on synthetic/development inputs.
- Terminology: the 805 directly checked failures are insufficient coverage at
  prediction, not necessarily zero cadences. The 92.8% recovery is conditioned
  on the declared >=.75 window and in-transit coverage thresholds.
- Status: bounded counterproposal. No threshold, model family, margins, weights
  or primary inference redesign requested. No production edits, new sample,
  photometry/header access, freeze or protected access in this review. Claude
  next completes actual-support evidence and final-path wiring; a focused check
  precedes the hash-bound freeze proposal and Barry's protected-access decision.

### D061 — Actual support qualifies t015v3a; one executable final path from manifest to decision

- Date / responsible agent: 2026-11-07, Claude (Opus 5.5); for Codex's focused check, not a freeze.
- Evidence: `docs/prefreeze_final_path_2026-11-07.md`; `scripts/prefreeze_replay.py`, `results/prefreeze/replay/`; `results/prefreeze/injection_evidence_t015v3a.json`; `scripts/final_measure.py`, `scripts/final_evaluation.py`, `scripts/check_final_chain.py`; `results/prefreeze/final_path_dev/`, `results/prefreeze/final_chain_check.json`; `tests/test_final_evaluation.py`.
- Accept D060. The all/none support scenarios are sensitivities, not bounds; D059's sentence "the evidence does not depend on the unexported support outcomes" is retracted.
- Requirement 1, actual support:
  - Replayed every SPOC removal-mode injection run of both frozen samples with the same hosts, files, seeds and truths and the unchanged timing core. Every one of the 1,478 and 1,368 saved timed rows reproduces err, σ and `gauss_ok` exactly. The 17 rows with integration flags are now labelled `integration_unresolved`; they were already rejected.
  - Exported grids under the adapter's own support check: 136/137 and 232/239 pass.
  - Under the actual rule all eight criteria pass in both samples, with unchanged margins and seed:
    - confirmation 104 hosts / 1,477 injections, z-RMS [0.953, 1.021], coverage [0.934, 0.959];
    - replication 100 / 1,361, z-RMS [0.980, 1.052], coverage [0.938, 0.961], mean z +0.070 [0.013, 0.126], reported and not corrected.
- Requirement 2, final path:
  - `final_measure.py` takes the fixed manifest and writes I1 windows, product diagnostics (read failures included) and directly measured coverage at every prediction.
  - `final_evaluation.py evaluate` writes one terminal row per manifest event, applies the shared acceptance, scores accepted rows through the adapter and runs B = 2,000 joint host refits with the declared evaluation seed. It persists draws, multiplicities, parameters, deltas and receipts.
  - It fails closed unless all three hold:
    - the draw scorer reproduces the adapter (≤ 1e-9);
    - the calibration refit reproduces the frozen parameters (≤ 1e-6).
  - Every draw is scored exactly, about 1.5 h on 8 cores at B = 2,000. Interpolating a grid-quantile table was tried and abandoned: a quadrature wiggle of about 1e-4 s brought it within 1.3e-6 of its tolerance.
  - The conditional fixed-parameter bootstrap has its own declared seed, 20261109.
  - The protected era refuses without `configs/protected_access.json` recording Barry's decision.
- Fail-closed details: missing Gaussian quantiles now return `gauss_certification_unresolved`, and injection rows are adapted explicitly. Absent or unreadable manifest products keep their event rows.
- Development verification:
  - The B = 200 exact exercise over 5,109 development hindcast events (3,778 accepted, 285 on grids) passes every reproduction check. Its scores carry no inferential content.
  - The chain check measures 25 hosts and 677 events from light curves. All 579 windows keep their saved status, with a median timing difference of 0.002 s (at most 2.1 s, from the DRD rather than DRC identification period), then evaluates end to end.
  - The full test suite passes (94 tests).
- Next: Codex's focused check; then the hash-bound freeze manifest and Barry's decision on protected access.

### D062 — Accept D061 after a minimal access-guard repair; close D060 requirements

- Date / responsible agent: 2026-11-08, Codex (GPT-6.1-sol).
- Evidence: `3ac3d57`, `docs/audits/d061_review_2026-11-08.md`,
  `results/sprint2_review/d061/package_check.json`; two independent read-only
  specialist checks and independent final-path execution. C038–C040.
- Accept actual support on the same frozen SPOC injections. All 376 grid
  hashes and support outcomes verify; 136/137 and 232/239 pass. The evidence
  generator reproduces the committed JSON byte for byte; all eight criteria
  pass with unchanged margins, B10000 and seed. Coverage lower bounds are
  .9338 and .9381. The late bias remains reported, not corrected. This is
  conditional development qualification after amendments, not a new replication.
- Accept the executable fixed-manifest → terminal ledger → shared acceptance
  → adapter scoring → configured joint-refit path. Independent execution on
  the full saved 5109-event development manifest reproduces 3778 accepted,
  285 grid-scored, adapter agreement 1.46e-12 and zero calibration drift.
  Saved B200 draws, host multiplicities, source/config/input hashes, private
  receipt hash and chain measurement-source hash verify. Hindcast scores have
  no forecast-validation interpretation.
- Repair made by Codex: the guard previously accepted any nonempty decision,
  including a synthetic `DO NOT OPEN` from Claude. It now requires exact
  `authorised_by: Barry W. Brook`, `decision: authorise_protected_access`, a
  nonblank string `decision_id` and canonical valid ISO date. Measurement and
  evaluation share this check. Negative/positive temporary-record tests and
  denial-preserves-time-limits test pass; independent review accepts the repair.
  No real access record was created. All 96 tests pass.
- The repair changes only `era_limit` and a date import; the remaining numerical
  source AST matches the source hashed by the saved run. No measurement or
  large bootstrap rerun is needed for this validation-only repair.
- Status: D061 accepted for the hash-bound freeze proposal; D060's two
  requirements are closed. Threshold, margins, scope and primary inference
  stand. No protocol freeze or protected access is authorised by this decision.
- Next: Claude assembles the hash-bound proposal and portable score receipt.
  Bind the full replay/calibration evidence chain as well as final code/config,
  environment specification, lists, parameters and forecasts. These are
  bookkeeping tasks, not another scientific qualification round. Barry's
  separate decision on that concrete package precedes any protected access.

### D063 — Hash-bound freeze proposal; protected access binds to one verified package

- Date / responsible agent: 2026-11-08, Claude (Opus 5.5); a proposal for Barry's decision, not a freeze.
- Evidence: `docs/freeze_proposal_2026-11-08.md`; `results/freeze/freeze_manifest.json` (SHA-256 `eb387f3ec42a4048e491c1fc77d28bac9e10b75418036d11936f6fed9b4e2b7f`); `scripts/freeze_manifest.py`; `tests/test_final_evaluation.py`.
- What the manifest binds:
  - 73 files: 19 code, 4 environment (including uv locks that pin the replay and measurement environment: numpy 2.3.5, scipy 1.18.1, astropy 8.0.2, lightkurve 2.5.1), 2 config, 8 event lists and roster records, 3 parameters, 3 forecasts, 10 calibration and ephemeris inputs, and 24 injection-evidence files;
  - 780 likelihood-grid hashes: 404 development calibration grids and 376 replay grids;
  - the evaluation `.venv` package list.
- Binding checks: original and replay diagnostics are equal in both samples; replay grids match their ledger hashes; forecast content and parameters match the receipt; core forecasts equal the core manifest. All pass.
- The five local OSF inputs match `results/pilot_v1/source_manifest.csv`.
- Access guard: keeps Codex's exact affirmative fields and adds one requirement. The record must cite the manifest SHA-256 and the package must verify unchanged, so Barry's decision authorises exactly this package. The change touches only `era_limit`; `check_d061_package.py` still verifies the saved development run. All 97 tests pass.
- The portable development receipt is committed; it records the original receipt hash, which equals the hash in the run summary.
- The protected-run commands and the decision rule are recorded in the manifest and the document. The declared open limits are unchanged.
- Next: Codex verifies independently; Barry decides on protected access.

### D064 — Independently verified corrected freeze proposal; Barry's access decision pending

- Date / responsible agent: 2026-11-08, Codex (GPT-6.1-sol).
- Evidence: bound verifier repair `bc85326`, corrected proposal/evidence
  `db5e959`, `docs/audits/d063_manifest_review_2026-11-08.md`,
  `results/sprint2_review/d063/independent_manifest_check.json`; C042.
- Supersede the unapproved D063 fingerprint. Exact current manifest SHA-256:
  `5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1`.
  Source commit: `bc853261cd301d5e0b08e7ffd4eab8b5cab98f80`, committed before
  rebuilding, contains every recorded tracked byte.
- Independent review found and Codex repaired three bookkeeping issues:
  - bind the two omitted reachable local modules;
  - compare interpreter version as well as installed packages, propagating
    environment-inspection failures;
  - refuse build/verify when tracked bytes do not match the source commit.
  Independent review and regression tests accept these changes. Numerical code,
  data, calibration, event lists, forecasts and scientific choices are unchanged.
- Verification by a separate implementation: 75 file hashes/sizes/gzip-content
  hashes and all tracked source blobs match; 780 grid hashes and aggregate
  match; conservative import closure has 21 bound modules; Python 3.13.16 and
  17 packages match; measurement/replay lock package versions agree. Five OSF
  inputs match download provenance. Core3103 + extension291 + exclusions5
  exactly partition the source3399, with exact forecast coverage of both sets.
  Portable receipt transformation and original-receipt linkage verify.
- Supplied verifier reports zero mismatches and eight true detailed binding
  checks. All 99 tests pass. A temporary uv cache resolves the tool sandbox's
  global-cache access limitation without changing the inspected environment.
- Status: ready for Barry's explicit decision to freeze this exact package and
  authorise the recorded protected primary/exploratory runs. No record has been
  created; no protected data, photometry or headers opened. Nothing is frozen
  by this decision. D062 scientific acceptance and declared limits stand.
- If Barry authorises, the actual record must use this current full hash,
  exact affirmative fields, date and decision ID; the guard requires a clean
  package verification. The old `eb387f3e…` proposal is not the approval target.
- Next: Barry — authorise or decline protected access for the concrete package.

### D065 — Package frozen; protected primary evaluation inconclusive

- Date / responsible agent: 2026-11-08, Claude (Opus 5.5), on Barry's authorisation.
- Authorisation: Barry, 8 November 2026, "Authorised." (board messenger, replying
  to Codex's D064 question), confirmed directly in the Claude session: "approve
  writing the D065 access record". Record `configs/protected_access.json` cites
  manifest `5ec7c0f363bca641430c68c0ff57fdbf788cda9e32f80dddea7c7cd9121c57d1`;
  committed `b2f54de` before any protected request. The package is frozen.
- Evidence: `docs/final_results_2026-11-08.md`; `results/final_primary/`,
  `results/final_extension/`; measured inputs under `data/derived/final_*/measured/`; C043–C044.
- Primary (core, 3,103 events; 2,185 accepted on 151 planets): planet-balanced
  standardised IS95 M2 − M0 = −0.121, 95% joint-refit interval [−1.84, 2.20]
  (B = 2,000). **Decision by the fixed rule: inconclusive.** Conditional
  fixed-parameter interval [−1.98, 1.12]. Fail-closed checks pass (adapter
  2.2e-12, refit 0.0).
- Description: M2 raises planet-balanced 95% coverage from 0.908 to 0.976 and
  widens intervals about 1.7-fold; the score gain and width cost cancel. 26.5%
  of planets improve; median planet delta +1.05.
- Exploratory extension (291 events): 72 accepted on 5 planets; −11.2 [−56.4, 6.3]; uninformative.
- Execution: the first core measurement with the recorded relative `--out`
  failed on 71 grid-writing products (`relative_to` needs an absolute path) and
  9 MAST disconnects. These are execution failures independent of outcomes. It
  was set aside unchanged, and the identical command was rerun with an absolute
  path. No frozen file changed; verify is clean after the run; 99 tests pass.
- Remaining: declared strata, sensitivities and secondary diagnostics need a
  post-unblinding script applied exactly as declared; independent review (T012) first.
- Next: Codex reviews the protected run independently.

### D066 — Independent D065 review accepts the primary result and complete rerun

- Date / responsible agent: 2026-11-09, Codex (GPT-6.1-sol), with bounded
  independent numerical, execution and specification checks by three delegates.
- Evidence: `98d5d04:results/final_review/{numerics,provenance}/`,
  `docs/audits/d065_review_2026-11-09.md`; C045. The current access record
  equals `b2f54de`; frozen manifest SHA remains `5ec7c0f3…` and verifies clean.
- Decision: accept the primary −0.121 [−1.84, 2.20] **inconclusive** result
  and the complete absolute-path rerun. All 224 previously completed product
  diagnostics, 1,817 windows and 71 grids persist unchanged; same 304 products.
  No frozen source/config/input or original result was edited. No new raw
  photometry/header access or protected measurement was needed for this review.
- Corrections to D065: the path exception is triggered by non-Gaussian
  likelihood output, so it is not independent of measured outcome shape.
  It does not select on forecast residual/score; the complete rerun restores
  the intended pipeline. Increased coverage/width are descriptive; the wide
  score interval establishes neither benefit nor harm, not equivalence.
  Extension interval uses 1,989 defined draws out of 2,000 because eleven
  union-host resamples contain no evaluation host; preserve frozen nanquantile.
- Validation: independent equal-planet arithmetic, all seeded multiplicities,
  conditional intervals, closed-form Gaussian scores, independent grid
  convolution/roots and bounded full-draw/dense-likelihood refits. These are
  not a second full 2,000-refit run or a new photometry extraction. Recorded
  chronology is consistent saved Git/filesystem evidence, not an immutable
  invocation audit; exact CLI arguments were not in the original receipt.
- Consequence: correct the result narrative and proceed with declared
  secondaries under openly dated conventions. Primary result stays fixed.
- Status: adopted; closes independent review of D065.

### D067 — Declared secondaries completed; conditional inference kept explicit

- Date / responsible agent: 2026-11-09, Codex (GPT-6.1-sol).
- Scope: saved authorised outcomes/grids only; no new host sample, model
  search, measurement or change to the frozen package/primary verdict.
  `98d5d04:docs/secondary_execution_2026-11-09.md` records conventions before
  computing variant metrics; implementation is explicitly post-unblinding.
- Evidence: `f679e80:results/final_secondaries/`,
  `results/final_review/secondary_checks.json`,
  `docs/final_secondaries_2026-11-09.md`; C046–C047.
- Completed: lead/Tmag/covariance/core-extension/product strata, full and
  prediction-qualified recovery, gain-host removal k=0–5, dated current
  catalogue TTV labels, and all ten declared sensitivity settings plus baseline.
  All settings refit development data where required; protected values do not
  train the calibration. Original/restricted attempt denominators are reported.
- Results: removing HR858 changes the fixed-fit mean −0.121 to +0.602 without
  changing the primary cohort. Sensitivity point contrasts range −0.723 to
  +0.640. Every reported conditional interval spans zero, but these B=10,000
  host intervals hold scenario fits fixed and are not joint-refit inference or
  new improves/worsens/inconclusive decisions. The primary joint interval stands.
- Conventions not frozen beforehand are disclosed: inherited coarse lead bins,
  development brightness bins, equivalent integration-status normalisation for
  the majority gate, fixed-fit host influence, and conditional secondary seed
  20261109. All events are first-year/C2/SPOC; retain empty cells. TTV labels
  use the current NASA default-row flag retrieved independently of scores;
  physical unflagged status and discovery timing remain unknown. No new label
  screens the historical cohort. Journal boundary screen is numeric and
  conservative, not an exact time-system conversion.
- Validation: three delegates cross-checked specification, implementation and
  reported numbers. Parent independently reproduces all scenario aggregation
  and conditional intervals and 19,240 Gaussian M0 standardised scores
  (max error 2.3e-13). Baseline/all-SPOC fits match frozen counterparts. All
  input/output hashes verify; figure visually checked. Full suite:
  `.venv/bin/python -m unittest discover -s tests -v` — 115 tests, one expected
  local skip, no failures. Frozen verifier remains clean. Bulk score caches
  are ignored/regenerable; small summaries, source metadata and receipts saved.
- Consequence: update result reports, claims and agent guide. Article and brief
  are still dated development drafts; integrating final results is the next
  writing tranche. No publication/release in this turn.
- Status: completed implementation; Claude cross-review and writing next.

### D068 — Claude cross-review accepts the D066–D067 secondaries; article and brief integrated

- Date / responsible agent: 2026-11-09, Claude (Opus 5.5).
- Cross-review: independent code (not Codex's scripts) reproduces from the
  frozen `scores.csv` the influence curve k = 0–5 (−0.121, +0.602, +0.928,
  +1.031, +1.119, +1.165), 40 gain hosts, median +1.045, the TTV-label groups
  (3 flagged −36.666; 148 unflagged +0.619), the raw-minute contrast (−8.460),
  recovery 2,185/3,103 and 2,181/2,369 with four accepted unqualified, and all
  eleven sensitivity point aggregates from `per_planet.csv`. No discrepancy.
- Accepted: Codex's D066 correction to D065 (the path fault depended on
  measured likelihood shape, not on forecast residuals or scores).
- New check (C048): HR858b's gain is a real ephemeris departure, not a
  measurement artefact. Coherent 16-transit sequence about 6.3 h early,
  consistent with published TTVs in HR 858 = TOI-396 that predate DRD.
- Interpretation adopted in the article: the interval score's losses are
  bounded by added width and its gains are unbounded, so a population tail
  calibration pays a small premium on most planets against rare gross misses;
  the planet-balanced mean, and hence the decision, turns on a handful of
  hosts. Targeted prediction of which ephemerides will fail is the suggested
  next question, not a claim.
- Products: `manuscript/paper.md` v0.4 (new §2.6 frozen protocol, §3
  held-out evaluation, development evidence moved to §4, discussion and
  limitations rewritten, contributions updated); `docs/brief.md`/`brief.pdf`
  (two A4 pages); `results/final_review/figures/planet_deltas.*`; agent guide
  updated. Bonfanti et al. 2025 identifier listed for Zotero import.
- Next: Codex reviews the article and brief against the ledger; Barry reviews
  before any release.

### D069 — Article and brief reviewed; score interpretation corrected

- Date / responsible agent: 2026-11-09, Codex (GPT-6.1-sol), from `9eade0b`.
  Two bounded delegates independently checked article claims and C048's saved
  rows/source identity. Parent reviewed the brief, independently derived the
  score contrast, integrated fixes and inspected rendered products. The
  article delegate rechecked revised §3/§5 and the brief without a new finding.
- Evidence: `97386cb:docs/audits/d068_products_review_2026-11-09.md`,
  `docs/audits/d068_hr858_source_review_2026-11-09.md`,
  `results/final_review/d068_interval_score.json`,
  `results/final_review/d069_products_validation.json`; C048–C049.
- Numerical disposition: all new article terminal counts, scores, fitted
  parameters, recovery, influence and sensitivity values match the ledger;
  one majority-gate upper interval rounding is corrected +1.16 → +1.15.
- Correction to D068's interpretation: absolute miss scores are unbounded,
  but the difference between two fixed finite intervals is bounded and
  saturates beyond both intervals. For nested symmetric widening at alpha
  .05, −19dw ≤ DeltaIS ≤ dw. Parent and delegate derived this independently;
  27 labelled synthetic cases match exactly, and all 2,185 saved event
  penalties are no greater than added standardised width. This changes the
  explanation, not the frozen score definition or inconclusive verdict.
- C048: coherent saved HR858b timing departures and actual absence from the
  frozen training set reproduce. Internal diagnostics do not prove absence
  of every extraction/identification error or establish the physical cause.
  The correct Bonfanti source is arXiv:2411.14911, DOI
  10.1051/0004-6361/202451300; supplied link 2604.15035 concerns another system.
  Pre-origin TTV knowledge is verified, while DRD's flag follows its own
  detection rule rather than a comprehensive literature inventory.
- Products: article v0.5, two-page brief and guide agree on accepted-timing
  selection, conditional secondary inference, bounded audit checks and
  targeting as a hypothesis. Historical qualification/status, simulation scope,
  freeze scope and the brief's confusion between timing-likelihood shape and
  physical TTVs are corrected. Source links/mission acknowledgement and
  identifier list added without constructing bibliography entries.
- Validation: 115 tests run, one expected local skip, no failures; frozen
  manifest unchanged. Figure 1 rebuilt with source/output hashes. Brief is
  two A4 pages; article review build is 23 A4 pages. Both have no missing
  glyph warnings or out-of-margin text after visual/render correction.
  Review article PDF is ignored at `manuscript/build/paper.pdf`; build arguments
  and hashes are in the validation receipt.
- Remaining: Barry reviews the products; formal Zotero imports and two older
  prior-art citation placeholders remain before release. No protected
  measurements, new model fitting, release or external contact in this turn.
- Status: reviewed and revised, ready for Barry; D068's unbounded-gain
  explanation and categorical artefact exclusion are superseded here.
- Next: Barry — review the article and brief.

### D070 — References written from verified metadata; Zotero becomes a fallback

- Date / responsible agent: 9 November 2026, Claude (Opus 5.5).
- Question: should the remaining citations wait for Barry's Zotero import?
- Decision: no. Barry, 9 November 2026 (Claude session, direct): "We should
  treat that Zotero route as a fall-back now, not a mandated hard gate ...
  Hand-writing it (and any verified reference) is now fine; I will always do
  a DOI sweep at the end anyway". The shared policy (`policy/shared.md`,
  claude-config `441e109`) and the agent guide rule now say so.
- Change: eight entries added to `references/references.bib`,
  `references.csl.json` and `literature_evidence.json` from registered
  DOI metadata (doi.org content negotiation; arXiv API cross-check), with full
  author lists: Bonfanti et al. 2025 (TOI-396 = HR 858), Ricker et al. 2015,
  Jenkins et al. 2016, Caldwell et al. 2020 and the MAST TESS-SPOC collection
  DOI, Ma et al. 2025 (ExoEcho I, AJ 169, 169), Agol et al. 2021 and
  Jontof-Hutter et al. 2016. Metadata corrections: JATIS article number
  014003 and issue year 2015; Van Laerhoven surname; sentence-case title for
  Jontof-Hutter et al. The article's two prior-art placeholders and its
  inline source links now cite these entries. The superseded
  `references/identifiers_2026-11-09_final.txt` is removed.
- Validation: article rebuilds (23 A4 pages) with every key resolved and no
  `[CITATION NEEDED]` left. No numbers, claims or frozen inputs changed.
- Status: adopted. Barry's DOI sweep precedes release.

### D071 — External review accepted; revision programme proposed

- Date / responsible agent: 9 November 2026, Claude (Opus 5.5); proposed,
  awaiting Codex.
- Question: how to respond to Barry's commissioned GPT-6 Pro review of v0.5
  (archived in `docs/external_review/2026-11-09_gpt6pro/`). Barry, 9 November
  2026: "please work with Codex (but you should start: take turns as usual) to
  decide on the new actions required, and revise the three parts of the paper
  accordingly."
- Evidence:
  - The review's new numbers reproduce from our saved data (loss-scale signs,
    HR858b zero coverage under M0–M3, precision ratio, five zero-accepted
    planets, P/4 gate).
  - An independent HR858 extraction reproduces all 16 frozen b timings and
    finds c about 9.5 h late, with d on time (C050, provisional).
  - DRD's HR858b input timings end in November 2020 and show reduced χ² 5.5
    about the issued line.
  - TESS S74–S97 has never been opened.
- Decision (proposed): accept R01–R10. Retain the frozen experiment
  unchanged. Run Stage 0 repairs now. Develop an issue-time triage question on
  inspected data, then freeze and test it on S74–S97 after Barry authorises
  opening. Rewrite the three products only once the scope is fixed. The v0.4
  "insurance" interpretation is withdrawn.
- Details: `docs/review_response_2026-11-09.md`.
- Status: proposed; Codex to challenge, especially the Stage 2 design and the
  gross-miss endpoint.

### D072 — Stage 0 executed; new-test chronology and cohort counterproposal

- Date / responsible agent: 9 November 2026, Codex (GPT-6.1-sol), from
  `87cc6ff`; evidence `064cbf5`. Bounded parallel work supplied independent
  measurement, diagnostic/benchmark and information-ledger implementations;
  the parent checked receipts, joins, metadata and key numerical results.
- Decision and scope: accept the integrated question and Stage 0 repairs,
  preserve the frozen primary experiment and its inconclusive verdict.
  Counter D071's Stage 2 wording pending reconciliation with Claude. Nothing
  here freezes a new protocol, authorises S74–S97 or releases a product.
- C050 is supported as coherent shared-photon timing evidence, not exclusion
  of every extraction/blend/identity error or a unique dynamical explanation.
  The extra HR858b event maps to an existing unresolved-integration rejection.
  Its released timing chi-square divided by nominal N−2 is 5.52; the
  standardised residual RMS is 2.20, not 5.5 times the stated errors.
- T017: design/sample/triggers committed before fits (`c61c0fc`). Preserved
  the checker's first masking defect, committed an explicit same-sample
  repair (`3dc88c1`), then executed all 35 products. Influential timings agree
  closely overall. Seven ordinary-control triggers still meet the fixed
  broader-review condition; adjudicate them before agreeing a further
  tranche. Three HR858 PDCSAP shape-sensitivity flags remain. This is not an
  all-pass validation or established defect in the frozen outcomes (C051).
- T018: three-scale conditional intervals, coverage curves, stored-s spread,
  full population flow, zero-accepted cases and selection/estimand text are
  complete. Independently recomputed summaries agree to numerical precision.
  A 499-file portable package replays both score CSV hashes exactly; 463
  grids are included. It does not remeasure, refit or rerun joint uncertainty.
  Both evidence archives have checksum-verified data-store copies (C052–C053).
  A separately committed 12-run synthetic photometry design (`03fbf67`)
  exercises the actual frozen pipeline; finite score/capture counterexamples
  are interpretation controls, not performance or qualification (C056).
- T019: uniform release-input ledger and current companion-candidate screen
  complete; historical companion/TTV certification and origin durations
  remain unknown where unverified. Preserve forecast issue separately from
  timing-artifact availability: DRB's artifact follows by 44,925.965 seconds,
  DRC's by 53.188 seconds. No candidate-block overlap is found in the DRD
  timing inputs; this does not make DRD available in 2024 (C054).
- New-test counterproposal: DRD on S74–S97 is a data-cutoff hindcast. Prefer
  DRC for a principal issued-forecast question, subject to verified decision
  time/features. Every existing-roster host had 2026 products attempted,
  including failures. Expand and audit a new cohort across all prior use;
  the 41-target no-current-cache DRC-core metadata lead is neither a
  qualified cohort nor power evidence. Its 369 opportunities are coarse
  DRD predictions, not a final DRC manifest. S74 straddles the cutoff day.
  A rule trained with 2026 outcomes then tested in 2024–2025 is locked
  retrospective validation, not forward chronological prediction (C055).
- Fix one practical primary budget/endpoint, flagged fraction, duration,
  referral cost and ambiguous/non-recovered handling before freezing.
  Measured-time coverage is not observing capture; do not inflate an
  allocated schedule by later measurement errors. Conditional score
  propriety needs stated observation/selection assumptions; the fact that
  reported errors are estimated later alone does not disprove it.
- Verification: 141 tests, one expected local skip, no failures. Checked
  579 receipt hashes. The local evaluation environment had drifted; retained
  it and restored the exact frozen pins, after which the native manifest
  verifier reports zero mismatches. No frozen scientific file changed;
  measurement uses its separately retained pinned runtime. No S74–S97
  photometry or headers were opened. The old article/brief PDFs remain
  historical drafts; full three-product rewrite follows reconciliation.
- Evidence: `docs/d071_counter_review_2026-11-09.md`, T017/T018/T019 reports,
  `docs/d071_injection_controls.md`, C050–C056 and
  `results/d071_review/execution_receipt.json`.
- Status: repairs adopted/executed within the existing envelope; new-test
  counterproposal awaits Claude. Next: Claude — adjudicate controls and
  reconcile D072 before T020–T021. Barry's access decision follows a concrete
  independently reviewed freeze package.

### D073 — T017 controls adjudicated; new test fixed as a locked retrospective DRC test

- Date / responsible agent: 9 November 2026, Claude (Opus 5.5), from
  `6405766`; proposal for Codex's challenge, not a freeze.
- Question: do the seven T017 control triggers reveal frozen timing faults,
  and what exact design should T020–T021 build?
- Evidence: `docs/d073_adjudication_2026-11-09.md`;
  `results/independent_validation/t017_adjudication/` from
  `scripts/t017_adjudicate.py` (no photometry opened); C050 checker run on
  cached TOI-157 S98 (`results/independent_validation/toi157_s98/`).
- Findings: every control trigger is checker-side. `t017_compare.py` pairs on
  ungated absolute distance, whose tied optima shift trains by a cycle; a
  P/4-capped cost recovers pairs in four products (WASP-82b PDCSAP 6→9,
  TOI-157b 10→11, WASP-170b 4→5, HR858b S105 SAP 2→4). All 25 frozen timings
  still unpaired are `insufficient_window_coverage` refusals, and all are
  timed by the other route or the C050 checker. WASP-18b's ambiguity is its
  secondary eclipse (phase 0.503) and a broad residual around transit. Zero
  control large discrepancies after gating (C057). HR858b S105 shows a
  sign-consistent 7–22 min departure of four independent route/flux timings
  from three frozen timings; immaterial against the 6–7 h miss, material to
  how its convolved score is described.
- Decision and scope: no broader 2026 remeasurement tranche; an independent
  audit of a random sample of new-block products joins the freeze package.
  Accept D072's corrections (HR858b z-RMS 2.2, not "5.5 times"; PDCSAP label
  for c; weighting labels; conditional propriety). The new test is a locked
  retrospective, host-held-out test of one release-feature rule on issued DRC
  forecasts (origin 2022-09-27T15:26:09Z), primary cohort the audited
  DRC-core hosts with no 2026 attempt, rule developed on roster hosts only.
  Outcome identification and the P/4 gate centre on DRD, never on the DRC
  forecast under test. Primary endpoint: planet-balanced capture difference,
  triage (q = 10%, pad fixed in development) minus each of two equal-budget
  comparators (proportional and additive); success requires both lower 95%
  host-bootstrap bounds > 0. Feasibility gate: projected interval width from
  development data decides confirmatory versus descriptive before access.
- Consequences: Codex amends T017 pairing (C051 regenerated) and adds an
  HR858b S105 rescore sensitivity to T018; T020 then T021 follow D073 section
  4. Article, brief and guide rewrite waits for T020. The D071 memo carries
  corrections for the scatter and artefact wording.
- Status: proposed. S74–S97 remain closed; nothing released.

### D074 — D073 repairs verified; no competitive triage candidate selected

- Date / responsible agent: 9 November 2026, Codex (GPT-6.1-sol), from2661f82.
  Evidence cb38a33; earlier development8309328; designs6768a75/2e8c9e9.
- Accept D073's control adjudication with attribution limits. Fix the pairing
  before regeneration (506ab58): 347 pairs, independent DP exact, all25
  remaining unpaired route rows coverage refusals, no control large difference.
  Six raw flags remain explained rather than thresholds relaxed (C058).
- S105 bounded sensitivity complete: M2−M0 −0.089004, conditional interval
  [−1.880,+1.124]; all HR858 events remain uncovered. Other outcomes unchanged;
  this does not replace frozen outcomes or the primary interval (C059).
- DRD identification and DRC scoring work with unchanged numerical core,
  TWO epochs and canonical IDs; synthetic actual-function proof retains a
  one-day miss. A new scope-bound access preflight must precede S74–S97
  requests/headers; old D065 does not authorise an arbitrary new manifest
  (C060). No new access has been activated.
- Accept locked retrospective DRC/internal-feature question and equal budgets;
  qualify endpoint as measured-midpoint capture/midpoint-window minutes.
  Full-transit/duration equivalence requires assumptions; ±2sigma is a
  sensitivity, not a latent bound. Keep intended-population unknowns visible.
  Replace the selected-training-gain feasibility threshold with a meaningful
  precision/effect target or an honest held-host development projection.
- T020 has an adverse developmental result (C061): same six rankings and
  fixed pads on earlier/inspected2026/pooled roster-host outcomes, C2/zero,
  always select no pad. Every positive-pad candidate loses to at least one
  equal-budget comparator. Independent reaggregation checks216 candidate rows
  and30 fold choices. No accepted case meets the >60min AND3sigma definition;
  HR858b has no named matched DRC forecast. Do not interpret identical-policy
  zero intervals as equivalence, power or a useful candidate.
- Recommendation: no new-data freeze for the present candidate. Claude should
  independently check the negative screen and reconcile whether to synthesise
  the paper or justify a materially changed developmental question. No silent
  pad/feature/cohort search for a positive result. T021 is not ready; no access
  decision is requested from Barry.
- Verification: 157 tests, one expected skip, no failures; exact evaluation
  environment restored, native freeze verification zero mismatches. Parent
  reaggregates S105 all3 scales and checks67 source/generated hashes. Sensitivity
  bulk archive remotely checksum-verified; no frozen scientific file changed,
  S74–S97 photometry/headers unopened, nothing released.
- Full reasoning: docs/d074_response_2026-11-09.md; T017 amendment, S105,
  identification and T020 reports. Status: repairs/development executed;
  scientific recommendation awaits Claude's independent review.
- Next: Claude — review the negative development result and scope before T021
  or integrated three-product rewrite.

### D075 — Negative triage result is structural; synthesise the paper now

- Date / responsible agent: 9 November 2026, Claude (Opus 5.5), from
  `55e9f33`; independent review of D074/T020 and scope proposal for Codex's
  challenge.
- Evidence: `docs/d075_scope_2026-11-09.md`; `results/t020_review/` from
  `scripts/t020_review.py` (separately written; saved tables only).
- Findings (C062): a hindsight oracle ranking loses to both equal-budget
  comparators in every slice and at every pad (by 11–38 points). A rule-free
  ceiling (baseline + flagged/accepted planets) exceeds the weaker
  minimum-budget comparator by at most 1.5 points. DRC-core errors: median
  about 1 min, maximum 30.4/36.6 min, none over 60 min; measured-midpoint
  capture 0.56–0.62 at forecast SD and 0.88–0.93 with the measurement SD
  added. The frozen 2026 DRD test has exactly one gross-miss planet of 151
  (HR858b, not in DRC); the next-largest planet maximum is 26 min.
- Decision and scope: accept D074. The D073 endpoint was measurement-noise
  dominated in this population (Claude's design error); no retuning. No
  new-block test of a triage rule: one positive case cannot train or
  validate one. Synthesise now around forecast accuracy, calibration, the
  inconclusive frozen correction, the visible HR858b failure and the
  unlearnability of triage at this rarity. A descriptive S74–S97 gross-miss
  rate study is recorded as an optional later extension, not requested.
- Consequences: Claude drafts article v0.6, the brief and the agent guide on
  the D075 section 4 outline after Codex's challenge; T021 is closed
  unexecuted.
- Status: proposed. S74–S97 closed; nothing released.

### D076 — Accept synthesis, correct the oracle and bound accuracy/calibration claims

- Date / responsible agent: 9 November 2026, Codex (GPT-6.1-sol), from
  `d7f4bea`; independent evidence `06fc2ca`.
- Decision: accept D075's stop/synthesise direction. T021 closes unexecuted;
  S74–S97 remain closed. Claude can draft T022 now under the corrections in
  `docs/d076_reconciliation_2026-11-09.md`; Codex reviews the draft, then Barry.
  No new-data or publication decision is requested.
- All three saved `t020_review.py` products reproduce exactly. Its MAE ranking
  is a hindsight heuristic, not an optimal allocation oracle. The memo's
  ceiling table mixes stronger/weaker comparators; success against both uses
  the larger capture fraction. Correct loose margins: −2.052/+1.492/+0.668
  percentage points (earlier/2026/pooled). The positive loose bounds alone
  establish neither impossibility nor lack of value.
- An exact allocation DP independently proves the bounded negative result:
  no permitted flag subset beats both equal-budget comparators on these
  saved accepted outcomes. Best joint gains −8.7745/−3.6937/−4.3786 points,
  all at 15 min. Later/pooled optima beat proportional slightly but lose
  additive. Keep q, pad grid, endpoint and finite-data scope explicit (C064).
- Accuracy wording: 150/151 accepted DRD planets have all accepted timings
  within 26.4 min (or 27), not 26.0; pooled-event median 1.115 min versus
  equal-planet-mass median 1.315. One observed gross-miss planet among the
  accepted sample is not a catalogue-wide rate (C063).
- Calibration wording: 90.79% is planet-balanced convolved measured-time
  coverage under C2 reconstruction and supplied likelihood assumptions;
  it is not issued-SD-only or latent calibration. Keep primary joint-refit
  and S105 conditional intervals separate. Noise attribution, universal
  padding advice, negligible observing cost and a proven advance warning
  are not established. Independent implementations share SPOC photons.
- The +1/+2/+3 min uniform-pad audit is a post-review descriptive sensitivity,
  not T020 retuning. +3 min gives 94.01% accepted DRD midpoint capture and
  adds 18,618 midpoint-window minutes before operational constraints. No
  full-transit scheduling recommendation follows.
- Optional zero-of-183 binomial illustration is one-sided (1.624% upper95),
  assuming independent equal-risk complete ascertainment; the metadata lead
  is not a qualified sample. No new study is needed for this rewrite.
- Verification: 160 tests, one expected skip, no failures. Three oracle
  regressions, nine separate parent exhaustive checks, 87 rounded cells and
  native review reproduction. Frozen manifest unchanged; no photometry or
  headers opened, no new access or release.
- Status: scope adopted; quantitative/interpretive corrections govern T022.
  Evidence: new oracle/accuracy audits, C063–C064 and the D076 memo. Original
  D075 script/results remain preserved for explicit correction during rewrite.
- Next: Claude — draft article v0.6, brief and guide under D076; Codex reviews.

### D077 — Article v0.6, brief and agent guide rewritten on the D076 scope (T022)

- Date / responsible agent: 9 November 2026, Claude (Opus 5.5), from
  `477e110`; for Codex's review, then Barry's.
- Decision and scope: the three products now lead with the frozen question,
  the selected accepted population, minute-scale accuracy (C063), conditional
  measurement-convolved undercoverage (C063), the inconclusive primary on
  three loss scales (C043, C052), HR858b as a physical departure with
  antecedents that are not a validated rule (C050, C051, C054, C057, C059) and
  the bounded allocation result (C061, C064). D076 wording is used for every
  accuracy, calibration, advice and HR858b statement; the insurance reading is
  withdrawn; no universal padding advice or catalogue-wide rate is given.
  Article: new title, Section 2.7 (post-review analyses), P/4 gate and
  conditional-propriety disclosure, Sections 3.2, 3.3, 3.5 and 3.8, rewritten
  discussion and limitations, contributions including the external review.
  Two verified references added (Lissauer et al. 2024; Agol et al. 2024).
- Validation: article builds at 29 A4 pages with every citation resolved;
  brief builds at two A4 pages and was visually checked; 160 tests pass with
  one expected skip. Development Section 4 is unchanged apart from table
  renumbering.
- Status: draft for review. S74–S97 closed; nothing released.

### D078 — v0.6 reviewed and corrected to v0.6.1; ready for Barry

- Date / responsible agent: 9 November 2026, Codex (GPT-6.1-sol), from
  `dbc24bd`; products/audits `513db40`.
- Decision: accept the central v0.6 results and complete targeted corrections
  across article, brief and guide. The reviewed products are ready for Barry;
  no additional research or data-access decision precedes his review.
- Three independent bounded reviews cover article semantics/numbers,
  brief/guide consistency and primary-source verification of Lissauer/Agol
  2024. Parent checked the new Agol calibration/later-timing precedent and
  acknowledged it explicitly. The changed scientific passages were rechecked.
- Corrections: combined conditional coverage rather than attribution to
  measurement noise or catalogue SD alone; accepted-sample accuracy rather
  than prospective assurance; both budget comparators and five discrete pads;
  coherent shared-photon HR858b evidence rather than unique cause/exclusion;
  epoch-blind search versus forecast-dependent acceptance; specific design
  commitments versus retrospective diagnostics; reduced recovery rather than
  hard universal cutoffs; joint primary versus conditional diagnostics.
- Guide historical defects/writers are explicitly superseded or isolated;
  pinned-interpreter instructions and C063/C064 evidence paths are repaired.
  Original white-noise non-reproducibility is dated separately from the later
  retained synthetic check. No numerical result, code, data or frozen byte
  changes. One overlong path was rendered as a short link to prevent clipping.
- Verification: article 29 A4 pages, brief two A4 pages; all citations resolved.
  Full-size brief, article contact sheets, selected full-size figure/table
  pages and repaired page checked. Body bounding boxes/glyph checks pass;
  no build warnings. Sources, PDF hashes and commands are recorded in
  `results/final_review/d078_products_validation.json`. 160 tests, one expected
  skip, no failures; native freeze verifier reports zero mismatches.
- Limits retained: selected accepted timings, reconstructed covariance,
  conditional measurement likelihood, incomplete recovery/lineage,
  shared photons and limited multi-planet scope. This is human-review
  readiness, not release/submission or an external-specialist endorsement.
- Evidence: `docs/audits/d078_product_review_2026-11-09.md` and three adjacent
  v0.6 review reports; revised products and literature-access record.
- Status: adopted. S74–S97 remain closed; no formal release or submission.
- Next: Barry — review article and two-page brief before release.

### D079 — Reconstruction steps 1–2 reviewed; proposals for reconciliation

- Date / responsible agent: 10 November 2026, Codex (GPT-6.1-sol), from
  `0f390f3`, T023, discussion 156.
- Support the reader-first/product-first reconstruction. Correct clear scope
  and historical-status errors in the drafts only. Preserve Barry's main-message
  quote with a labelled alternative; retain the provisional four figures and
  three tables. No final venue or presentation decision is made here.
- Independent reviews: `docs/reconstruction/06_hypotheses_numbers_review.md`
  and `07_displays_product_review.md`; parent narrative/venue judgment in
  `08_narrative_venue_review.md`. The new H1–H3 differ from the recorded
  pre-access hypotheses; the transferable correction retains its prespecified
  primary standing. Accepted-sample accuracy and conditional convolved coverage
  do not imply catalogue-wide performance or a safe observing window.
- Arithmetic checks: recovery is 2,181/2,369 among prediction-time
  coverage-qualified opportunities; input residual RMS is 2.198 quoted-error
  units; the latest inspected DRC comparison reaches about 3.94 years after
  issue. Receipt: `results/reconstruction_review/number_check.json`.
- Display feasibility: saved files suffice without new photometry. Show
  observation/access chronology separately; standardised non-Gaussian errors
  need a qualified diagnostic or later exact PIT. The per-planet product
  needs metadata joins and explicit unknowns, including five zero-accepted
  primary planets. No displays built and no step 3 inferred.
- Venue: conditional preference for ApJS as a reference product; AJ remains
  plausible under its official scope. Five-paper examples are not formal
  requirements, absence evidence, or citation-count targets. Corrected AAS
  table-format guidance; the abstract limit is a maximum, not a word target.
- Verification: saved-table arithmetic independently cross-checked; abstract
  under 150 words, both message candidates 25 words; diff whitespace clean.
  Native freeze verifier reports no mismatches for manifest `5ec7c0f3…`.
  Eight recorded product/bibliography/config hashes remain unchanged.
  No analysis/code/environment changes; unit suite not rerun for draft edits.
  S74–S97 remain closed; no release.
- Next: Claude — reconcile these drafts with Barry before his step 3.

### D080 — Step 3a section abstracts reviewed; matching limitation clarified

- Date / responsible agent: 10 November 2026, Codex (GPT-6.1-sol), from
  `f916923`, T024, thread 156/message 3160. Clear corrections in
  `docs/reconstruction/09_section_abstracts.md`; rationale and sources in
  `10_step3a_review.md`. These are draft section plans for reconciliation,
  not manuscript edits or new scientific results.
- Important qualification: P/4 bounds distance to the nearest assigned DRD
  cycle, not necessarily the physical error of the same transit. A +0.9P
  displacement can map to the next cycle with residual −0.1P if that intended
  event and the other checks permit it. No observed alias is claimed; zero
  `cycle_ambiguous` rows does not rule out such aliases. Matching/selection
  provides no completeness guarantee. Frozen matches/results are unchanged.
- Corrected H1 to conditional combined undercoverage, without a padding amount
  or isolated cause; H2 to unresolved after unstable development transfer,
  not untestable because of one gross miss; H4 distinguishes conditional
  midpoint containment from operational/full-transit capture. H3 retains the
  prespecified inconclusive joint-refit verdict and conditional score semantics.
- Removed the withdrawn insurance reading; all 16 accepted HR858b timings
  remain outside every model's 95% interval. Restricted the allocation claim
  to the tested 10% policy/padding grid and both equal-budget comparators.
  Corrected catalogue-defined host scope, injection point coverages versus
  uncertainty intervals, and planned versus completed product status.
- Verification: independent number/status and gate/score reviews plus final
  semantic recheck; parent saved-table recomputation and code-level gate
  counterexample. Receipt: `results/reconstruction_review/step3a_check.json`.
  Counts 267/267/297/298 use conservative whitespace tokens including run-in
  headings and bullet markers, excluding section titles and abstract labels.
  Native freeze verifier has no mismatches; eight product/config hashes and
  receipt input hashes unchanged; whitespace check clean. No code/environment
  changes or local unit-suite rerun for draft edits.
- Earlier reconstruction and Barry's chosen message are preserved. No raw
  photometry/headers, fitting, displays, access authorisation or release;
  sectors 74–97 remain closed. No later step is inferred.
- Next: Claude — reconcile these draft corrections with Barry before the next step.

### D081 — Step 3b paragraph framework reviewed; clear corrections proposed

- Date / responsible agent: 10 November 2026, Codex (GPT-6.1-sol), from
  `660ff9e`, T025, thread 156/message 3164. Reviewed draft in
  `docs/reconstruction/11_paragraph_abstracts.md`; rationale in `12`, primary
  reference checks in `13`. Earlier section abstracts and chosen message stay fixed.
- Retain reader-first/product-first order. Split the combined H2/H4/allocation
  paragraph, move the padding illustration to H4 and the S105 sensitivity to
  measurement robustness, and separate benchmark reuse from a future data study.
  The framework has 33 paragraphs (6/8/11/8), all with three or four sentences
  and at most 27 words per sentence. Thirty was a draft count, not a constraint.
- Material corrections: 730 of 918 unaccepted opportunities lack qualifying
  prediction-time coverage (734 total includes four accepted). The three-minute
  illustration uses forecast-only windows and equal planet weights: midpoint
  containment 0.9400798843. S105's interval is fixed-fit conditional, not a
  recalculation of the primary joint interval. The b/c/d pattern comes from
  one checker; two independent programs reproduce b. Tested-model failure
  does not show every possible uniform rescaling would fail.
- Restore M7's measurement-inclusive per-event normaliser, conditional score
  interpretation and inconclusive branch. Keep nearest-cycle/P/4 ordering;
  distinguish UTC issue dates from BJD_TDB event times and unconverted boundary
  exclusions. H2 stays unresolved; the allocation result retains its fixed
  10% policy/padding grid and both budget comparisons. Label planned products
  and post-review longer-horizon evidence accurately; remove blanket prior-art
  absence and unmeasured curator-cost claims.
- Three bounded independent checks cover scientific/numerical wording,
  structure and missing references; the first two include final rechecks.
  Eight DOI-bearing candidates and the AAS website are source-checked; all
  25 existing keys resolve. Dietze's journal is PNAS. Bibliography import
  remains deferred under the existing freeze, without a new approval gate.
  Generic bootstrap support does not certify the particular joint-refit method.
- Verification: parent saved-table arithmetic and matching sentence/framework
  IDs, receipt `results/reconstruction_review/step3b_check.json`; ten preserved
  artifact hashes and previous numerical inputs unchanged; native freeze
  verifier clean; diff whitespace clean. No code/environment changes or local
  unit-suite rerun for prose/source checks. No manuscript, brief, guide,
  bibliography or scrivmark changes; no raw photometry, headers, fitting,
  displays, new access authorisation or release. S74–S97 remain closed.
- Next: Claude — reconcile step 3b, then continue when Barry supplies the next stage.

### D082 — Step 3c full draft reviewed and cut

- Date / responsible agent: 10 November 2026, Codex (GPT-6.1-sol), from
  `f7a3d60`, T026, thread 156/message 3180. Revised reconstruction in `14`,
  rationale and pending production in `15_step3c_review.md`.
- Keep the structure; remove repeated prior-work and forecasting exposition,
  evaluative coda, binomial future-study aside and smaller rhetorical repeats.
  Under one count convention, main text is 3,760 → 3,482 words: −278 (7.4%).
  The abstract is 187 words in one paragraph, now including the primary
  −0.12 [−1.84,+2.20]. Retain the verified concrete JWST example.
- Restore compact conditional scoring and shape/noise assumptions; distinguish
  Gaussian calibration fitting from Gaussian/grid scoring. Keep M1/M3, 399
  primary grids and extension summary. Appendix plans retain all four models,
  propriety details and extension defined/undefined draws.
- Correct misplaced Track-R covariance percentage and overinterpretation of
  old mixture-scale estimates by removing unnecessary historical numbers.
  Separate injection recovery from accepted-injection calibration; qualify
  reported uncertainty ratios versus full-grid SD, M1's score ranking by
  scale, and S105's fixed-fit interval versus frozen primary inference.
  Restrict allocation findings to their policy/endpoint, without causal rarity
  attribution. Unrecovered errors are unknown, not zero/absent errors.
- Source checks: Agol's five July 2024 fit-excluded timings predate the
  September preprint, so do not imply verified post-issue observation;
  specify planet h for the drift. Brook's predictions were tested, without
  implying proper-score use. Bonfanti's two/five-hour values are simulated
  semi-amplitudes. Clarify boundary exclusions, covariance availability,
  reciprocal versus independent verification, Sonnet drafting credit and
  reviewed correspondence snapshots.
- Three bounded reviews plus numerical/editorial final rechecks; parent
  checked timing implementation, source chronology, parameters, reported ratios
  and Table 1's exact 3,103-event accounting. Receipt:
  `results/reconstruction_review/step3c_check.json`. Native freeze verifier
  clean; eleven preserved artifacts and earlier numerical inputs unchanged;
  diff whitespace clean. No code/environment changes or local unit-suite rerun.
- Figures, Table 3, Table 2 percentile cells, Fig. 3a choice, appendix assembly,
  bibliography import and final back matter remain production work, not built
  by this review. Manuscript, brief, guide, bibliography, scrivmark and earlier
  reconstruction stages stay unchanged. No raw photometry/headers, fitting,
  new access or release; S74–S97 closed.
- Next: Claude — reconcile the full draft and its cuts before the next stage.

### D083 — Step 3c production independently checked and draft repairs applied

- Date / responsible agent: 2026-11-10 / Codex.
- Scope: T027, thread 156/message 3186; production `05ae64f`, handoff
  `cba6dbe`. Saved outcomes/grids and public DOI metadata only. No raw
  photometry, FITS headers, fits, protected access or release.
- Independent PIT calculation imports no project code, reconstructs grid
  weights and uses adaptive integration. M0/M2 discrepancies below
  4.5e-15/1.4e-12; all coverage classifications reproduce. The early excess
  is not a grid-sign defect and remains descriptive. Quantiles use inverse
  weighted empirical CDFs without interpolation; now declared (C065).
- Table D1's eight criteria and development contrasts/intervals reproduce.
  Correct intended-injection versus exported-row denominators, four-core plus
  one-extension boundary exclusions, final 3,394 inventory, the false
  coverage-distortion ratio, identification-conditioned recovery, DRC event
  timestamps versus availability, 400 development resamples and coverage rounding.
- All 6,624 Table 3 cells agree with source tables. Correct its 36-column
  dictionary, issued marginal-error provenance and unverified duration fields.
  Replace extreme-selected excerpt with first ten core labels alphabetically,
  explicitly illustrative rather than representative. Both CSVs unchanged.
- Inspect main figures and all eight online pages; repair chronology/total
  labels, neutral uniform reference, reported 68% timing-bar definition,
  dates and single-event forecast band. Final PDF: 151 panels, 2,185 timings,
  no out-of-page text. All eight candidate bibliography records parse and
  match live registered DOI metadata; canonical bibliography unchanged.
- Counter to reconciliation wording: no error/score entered the failing path
  does not prove statistical independence. Draft section 2.6 states the
  implementation fact. Full-manifest rerun and D066 acceptance unchanged.
- Evidence: `docs/reconstruction/17_production_review.md` and five receipts in
  `results/reconstruction_review/` (PIT, appendices, Table 3, DOI, parent).
  Four numerical production outputs byte-identical; eleven preserved artifacts
  hash-identical; native manifest verifies; 160 tests OK, one expected skip.
- Status: adopted draft corrections for Claude's reconciliation. No change to
  the frozen protocol, primary result or canonical paper products.
- Next: Claude — reconcile D083, then Barry describes step 4.

### D084 — Step 4 cross-check: retain structure, repair scope and counting units

- Date / responsible agent: 2026-11-11 / Codex; T028, thread156/message3205,
  source `6d9e27f` (detailing `391c900`, clarity `8918cd1`).
- Independent checks cover appendices, primary sources/formatting and captions;
  parent checks the main text, saved numerics, reference build and integration.
  Work uses saved outcomes and public metadata only: no raw photometry, headers,
  fits, new access or release. Canonical products and earlier drafts preserved.
- Four appendix flags: E2 needs per-column sample counts, F needs planets versus
  flux-route flags, t015v3 is unscaled by brightness but keeps implementation
  repairs, and 2,186 development versus 2,185 held-out events is correct.
  Clarify the 399 non-Gaussian rows and the historical development-rule scope.
- Retain accepted-only accuracy in abstract/close, name the standardised score,
  restore Agol's July/September chronology and the rerun's absolute path, and
  distinguish weighted medians from averages. Event coverage recount is
  2,009/2,185 = 91.945%, so display 91.9%, not 92.0%; no estimate changes.
- Repair caption meanings: marker size is not area proportional to count;
  Figure3 tests combined uncertainty and uses conditional fixed-parameter
  intervals; Figure4 distinguishes 17/11/5 independent from 16 frozen timings
  and defines bars. Table2 separates quantile weights; Table3 defines units.
- Ten original new DOI entries and six UAT IDs verify. Science citations support
  their sentences. Correct funding credit and distinguish early FFI use from
  frozen SPOC-only calibration. Add four verified draft software credits,
  resolving tess-point's placeholder. Main bibliography unchanged.
- Verification: 47 citation keys resolve; scratch citeproc/math conversion has
  no warnings; numerical table cells and document headings preserved. Thirteen
  preserved artifacts match their hashes, displays/PIT unchanged; native frozen
  manifest verifies; 160 tests OK, one expected skip. No code/environment changes.
- Evidence: reconstruction reviews20–21 and `results/reconstruction_review/`
  `step4_{appendix,caption,source}_check.json`, parent `step4_check.json`.
- Status: adopted targeted draft corrections; no restructure, new scientific
  claim or alteration to frozen results. Claude reconciles, then Barry reads.
- Next: Claude — reconcile D084, then Barry reviews the completed reconstruction.

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
