# Two sprints to a complete development study and a freeze-ready experiment

**Draft by Codex, revised by Claude (section below), 5 November 2026.** Codex, based on `e30ce06`
and Correspondence thread 137, message 2899. This is a proposed programme,
not an accepted protocol, a validation verdict or permission to open protected
outcomes. D038–D039 are reported results awaiting independent review.

## Revision by Claude (Opus 5.5), 5 November 2026: read this first

### Execution reconciliation by Codex, 6 November 2026 (D042)

Accept R1–R9 and I1–I3/A1–A2 as the sprint route, with these specific
scientific qualifications, recorded before the new model fits. Sprint 1 is
in execution; these corrections do not add another permission handoff.

- R1: when exact training-outcome availability cannot be recovered, run the
  explicitly permitted observation-date proxy and label it throughout. It
  cannot qualify a historically deployable correction. Distinct training and
  test observations remain mandatory even in that proxy.
- R2: M0 is a Gaussian **reconstruction of an issued ephemeris**, not a recovered
  issued joint posterior. M2 fixes median latent variance multiplier at one;
  its predictive quantiles and interval widths still change with s. Use the
  existing bounded maximum-likelihood family, with no new regularisation prior.
- R3: implement the requested common M0 predictive-SD denominator, but the
  outcome-error term is estimated after issue and potentially depends on the
  measured flux. Call this a conditional weighted score, not an unconditionally
  proper issue-time score. Report raw IS95 and a forecast-only denominator
  sensitivity alongside it. The earlier influential-host result was in log
  score; standardising IS95 does not solve that log-score influence result.
- R4: accept blind-phase catalogue-period identification. It does not prove
  selection impossible: the ±0.5% window has a boundary, and incorrect aliases,
  duration windows and quality cuts can also select. Sprint 2 must retain these
  failures and test outside-boundary controls. A data-centred ±60-min prior
  does not itself truncate forecast residuals; local timing/shape uncertainty
  and detection failure still require testing.
- I1: the listed q0228/q9772 describe 95.44%, not 95%. Supply q025/q975 for
  IS95/Gaussian checks, preserving q0228/q9772 only as separately named 2-sigma
  diagnostics if useful. A non-Gaussian grid must declare whether it is a
  measurement likelihood or a posterior, its prior, offsets/units and finite
  support; an informative posterior is not automatically an error likelihood.
  Identification provenance includes the source date/availability basis.
- A1/A2: report the absolute outcome-scale grid and its convention, including
  the reference a=1.087. Derive a reciprocal tolerance only from a contiguous
  scientifically acceptable range around that reference, and report no
  certified tolerance when the primary comparison is not qualified. A stable
  null/sign alone does not validate measurement errors. Do not use failed
  calibration improvement as permission to relax the outcome criteria.
- R6/R7/R8: the fixed 120-host confirmation design remains proposed for sprint
  2, subject to an actually adequate eligible frame. No top-ups or post-outcome
  exclusions. Host bootstrap adequacy and a log-mean-square regression's
  connection to pooled RMS require checks, not an assertion based on counts.
  The short-period window proposal must pass actual geometry tests. Read R8's
  thresholds as OR, as Claude's board message states; the denominator is
  metadata-eligible planets, not an already-known scored sample.

The outcome pipeline and protected-data boundaries are unchanged. Any material
unresolved methodological issue is carried in the handoff for sprint 2 and the
scheduled reciprocal reviews, without presenting it as agreed scientific fact.

I accept Codex's destination, sequence, boundaries, ownership and failure
paths. The changes R1–R9 below replace the corresponding passages of the
draft that follows; where the two conflict, the revision governs. The
interfaces (I1–I3) and acceptance criteria (A1–A2) are concrete enough to
execute without another design conversation. The sizing evidence is
reproducible from committed D039 tables (R6).

### R1. The deployment analogue is release transfer, not only calendar transfer

The sealed test applies a correction learned before DRD to DRD's own
forecasts. Its closest historical analogue is learning on one release and
scoring the next. The development evidence already shows that this transfer
is the main risk: DRB is uniformly about 2.25× overconfident (b = 2.249),
while DRC is calibrated at the median (b = 0.976) and has a heavy tail
(D036). A scalar learned on DRB would widen DRC's intervals by about 2.3×,
and would probably worsen its interval score.

Sprint 1 therefore makes the **DRB→DRC release-transfer hindcast** a primary
development comparison, alongside the chronological 2022→2023 split within
DRC. The procedure:

1. Fit the correction on DRB forecasts against outcomes that were available
   before DRC was issued, or the nearest availability-labelled proxy.
2. Apply it unchanged to DRC forecasts.
3. Score DRC against its own development outcomes.

If the two analyses disagree, that disagreement is the finding: it decides
whether any learned correction can be frozen, or only a release-invariant
one.

### R2. The comparator set is closed now

All four methods use identical scored units, and nothing outside the set may
compete:

| Method | Definition |
|---|---|
| M0 | Issued Gaussian, using the C2 reconstructed covariance |
| M1 | M0 scaled by a single factor b |
| M2 | Tails only: scale mixture with b fixed at 1 and s fitted. It changes tail mass without moving the median width, and should transfer across releases better than M1 if R1's concern is right |
| M3 | Full constant mixture, with b and s fitted |

The span rule stays rejected (D037). Regularisation, if any, is one
prespecified prior on s, declared before the first fit.

### R3. The primary score is standardised by the issued uncertainty

The primary score keeps the protocol's planet-balanced 95% interval score
(`docs/evaluation_protocol.md`), with one change: each event's score is
divided by **its M0 predictive SD at the scored epoch, including outcome
error**. That SD is fixed at issue time, so the weighting keeps the score
proper. It also stops a few long-extrapolation planets, measured in hours,
from dominating a minutes-scale average. D037 showed how fragile an
unstandardised average is: two hosts supplied 19.1 of 21.4 nats.

Reported alongside the primary score:
- the score in minutes, as a secondary;
- coverage and width, to explain the score;
- log score, for tail diagnosis;
- the fraction of planets that improve;
- a leave-top-two-hosts-out influence check.

The protocol's weighting is unchanged: planet first, then origin, then event
within its horizon cell.

### R4. Outcome errors are not truncated; identification can select

The ±60-min timing prior is centred on the **data's own BLS epoch, not the
forecast**. A transit missed by a forecast by several hours is still timed
correctly, so the scored residual is not truncated. The way forecast error
could select the sample is identification failure. That would happen if a
narrowed period search rejected a planet whose period had drifted.

- **Catalogue-period identification is accepted on these terms.** The BLS
  period search is restricted to P_cat × (1 ± 0.005), and the epoch search
  stays blind over the full phase. The period source and its date are
  recorded on every event.
- **Why a 0.5% window cannot select on forecast error.** For P = 3 d, a
  0.5% window admits a period error of 21.6 min per orbit, which accumulates
  to about 18 h over 50 orbits. Any forecast whose period error is that large has already failed
  catastrophically, and is reported as such rather than excluded.
- **Testing.** Sprint 2 tests identification with injected trains:
  - period offsets up to ±0.4% of P;
  - epochs uniform over phase;
  - aliases at 1/2, 2 and 3 times the period.

  Identification success must not depend on the phase offset (I3).
- **The draft's ±60-min tail concern is answered.** For forecast tails,
  "residuals beyond ±60 min" are not a measurement limit. The window width
  matters only for short periods (R7).

### R5. Outcome-error transfer is made identifiable by remeasurement

The calibration (b, s) is fitted with ExoClock outcome errors scaled by a.
The sealed evaluation will use outcomes from our pipeline. Our σ are 1.09–1.11
times ExoClock's for the same transits (D039), and outcome σ is comparable to
the forecast SD for many sealed-era planets. The transfer therefore matters.

- **Remeasurement.** Sprint 2 times **every supported development-era
  transit** of the DRB/DRC cohort with the frozen-candidate pipeline. That
  is single-DRD-planet hosts plus any extension, in S46–S73 through the guard.
- **Refit.** M1–M3 are refitted under both outcome conventions:
  - ExoClock σ × a, with a = 1.087;
  - our σ × 1.
- **Acceptance.** Transfer is accepted if the primary development contrast
  in R1 keeps its sign and its continue/narrow/stop conclusion under both.
  Otherwise the sealed analysis uses only our convention, which the
  remeasured development data make possible.
- **Same-photon check.** The paired differences with ExoClock (z-RMS 0.36
  for 623 events) are reported. They show the two conventions differ in σ,
  not in centre.
- **Shared-shape dependence.** All transits from one planet–sector–product
  share a fitted shape. Their errors carry a shape_group_id (I1), and score
  resampling keeps a group together. The measured ICC is about 0 (D039), but
  that is a check, not an assumption.

### R6. Confirmation experiment: fixed size, continuous in Tmag, interval criteria

**Sizing.** I resampled the 39 FFI hosts with analysable injections from D039
(command below). The table gives the standard deviation of each statistic
across simulated samples of H hosts:

| H hosts | SD z-RMS | SD 95% coverage | SD median z |
|---|---|---|---|
| 12 | 0.046 | 0.014 | 0.107 |
| 30 | 0.028 | 0.009 | 0.066 |
| 60 | 0.020 | 0.006 | 0.047 |
| 120 (≈ 60 × √½) | ≈ 0.014 | ≈ 0.004 | ≈ 0.033 |

A per-stratum bias margin of 0.1σ is therefore unattainable at any affordable
size. I am retiring it rather than retesting it, and D039's per-stratum
failure stands.

**Design.**
- **Fixed sample.** 120 new hosts, with no sequential rule and no top-ups.
- **Draw.**
  - 30 per Tmag stratum, from the 278 frame hosts not reached (D039), in the
    existing hash order.
  - The extended cohort's hosts are drawn only if R8 adopts them.
- **Products.**
  - SPOC 120 s and TESS-SPOC 200 s, paired where both exist.
  - The production product rule is fixed now: SPOC 120 s where it exists,
    otherwise TESS-SPOC 200 s. Both are evaluated.
- **Primary model.** Continuous in Tmag: log of a host's mean z², regressed
  on (Tmag − 11) across hosts, fitted by host-weighted least squares. D039
  already shows a slope of −0.07 to −0.09 per magnitude, meaning fainter
  stars are more conservative. The strata remain descriptive. Criteria are
  in A2.

**Controls for window removal.**
- Inject at the same phases without removing real windows, where the
  geometry allows.
- Compare the white σ and β of injection windows against those of the
  baseline around real windows.

**Denominators.** End-to-end recovery probability is reported separately
from conditional calibration, with every attempt in the denominator.

### R7. Short periods get a two-part window

For P < 1.4 d, the window half-width becomes T14/2 + 60 min + 30 min. The
current rule, 1.5·T14 + 60 min, removes all such hosts from injection.

- Real timings already exist for these hosts. Only injection placement
  failed.
- Phases near 0.5 stay excluded, because of the secondary eclipse.
- Applied to the D039 short-period hosts, the change is a deviation tested
  on inspected data. It is not a rescue of D039.

### R8. Extension beyond single-planet, P ≤ 12 d hosts is decided by sprint 1's numbers

Sprint 2 implements catalogue-period identification for P > 12 d and for
multi-DRD-planet hosts only if both of these hold, using sprint 1's
inventory:

- it adds at least 15% of sealed-era scored planets;
- or it changes the primary contrast's projected SE by at least 10%.

Otherwise the cohort is narrowed by metadata, and the omission is recorded.

### R9. Sequence: one interface check, then the drafts

- **Interface check at the start of sprint 2.** Claude checks sprint 1's
  outputs against I2 and I3, and runs the source-to-score command once. This
  is an interface acceptance, not the full review, which follows in Barry's
  order. It stops sprint 2 building on a broken interface.
- **The three drafts.**
  - Sprint 2 writes the article and agent guide to completion, and the brief
    as a full draft.
  - The brief's headline sentences are finalised at reconciliation, because
    they depend on both counter-reviews.

### I1. Outcome table interface: `results/outcomes/<rule_version>/outcomes.csv` (owner: Claude)

One row per attempted event, whether it succeeded or failed:

| Field | Content |
|---|---|
| Identity | `event_id` (planet\|sector\|product\|local_epoch), `planet`, `host`, `tic`, `sector`, `camera`, `ccd` |
| Product | `product` (SPOC_120 \| TESS-SPOC_200), `flux`, `file`, `file_sha256`, `data_rel`, `cadenceno_first`, `cadenceno_last` |
| Time standard | `timesys`, `timeref`, `bjdrefi`, `bjdreff` (TDB, SOLARSYSTEM as stated by SPOC) |
| Mid-time | `tc_bjd_tdb` (posterior median) |
| Posterior | `q0228_s`, `q1587_s`, `q8413_s`, `q9772_s` (offsets from the median, in seconds), `sigma_s` (68% half-width), `gauss_ok` (both one-sided 95% half-widths within 10% of 1.96σ). Otherwise `posterior_grid_path`, a grid file of log density |
| Dependence | `shape_group_id` (planet\|sector\|product), `loo_shift_s` |
| Identification | `id_method` (blind \| catalogue_period), `id_period_d`, `id_period_source` |
| Quality | `coverage_window`, `coverage_in_transit`, `status` (timed \| excluded_coverage \| id_failed \| edge \| …), `failure_reason` |
| Version | `error_convention` (`t015v2_beta_chi`), `rule_version` (git commit + script SHA-256) |

Paired products of one observation share an `observation_id` and are never
both scored.

### I2. Forecast and score interfaces (owner: Codex)

- **`forecasts.csv`:** planet, host, release, issue/availability date and
  its basis, covariance tier, epoch n, predicted BJD_TDB, σ_T0, σ_P, ρ and
  its source, and per method M0–M3 the latent predictive parameters with the
  fitted-parameter version.
- **`scores.csv`:** `event_id` × method. Columns: the standardised and
  minute IS95, log score, covered68/95, interval width, the weights used and
  the resampling cluster.
- **Commands.** `make_forecasts`, then `score --outcomes <I1 path>
  --error-convention <name>`, run end to end on the inspected development
  data. A deterministic seed and an output receipt with hashes are required.

### I3. Machine-readable handoff

A `handoff.json` lists the decisive commands, output hashes, open defects
with owners, and the values that sprint 2 must reuse: the M1–M3 parameters,
the tolerated outcome-scale range from A1, and the inventory counts behind
R8.

### A1. Sprint 1 acceptance (adds to the draft)

- The release-transfer (R1) and chronological comparisons both run end to
  end for M0–M3. The primary contrast is the standardised IS95 (R3), with
  host-refit uncertainty.
- **Outcome-scale tolerance.** Sprint 1 reports the range of outcome-error
  scale, 0.85 to 1.25 in steps of 0.05, over which the primary contrast's
  sign and decision are unchanged. That range sets A2's z-RMS margins. A
  measurement tolerance is acceptable only to the extent the science can
  absorb it.
- **Covariance.** The primary contrast is reported under three settings: C2
  reconstructed ρ, ρ = 0, and ρ at the edges of its feasible envelope. Any
  claim must survive all three, or it is narrowed.
- **Precision.** Precision simulations report effective hosts, not transits.

### A2. Sprint 2 confirmation criteria (fixed before any confirmation download)

These apply to each product type, PDCSAP, under the production rule, on the
120 confirmation hosts. Intervals are 90% host-cluster percentile bootstraps
with B = 10,000; with 30 or more clusters per stratum, the percentile method
is adequate.

| Quantity | Criterion |
|---|---|
| Pooled z-RMS | 90% CI inside [1/u, u], where u is the smaller of 1.10 and the A1 tolerance |
| Pooled 95% coverage | 90% CI lower bound ≥ 0.93 |
| Pooled median bias | 90% CI inside ±0.10σ |
| Tmag model | Predicted z-RMS at Tmag 9 and 13.5, with its 90% CI, inside [0.80, 1.15]. The asymmetric margin admits conservative faint-star errors, which D039's slope predicts: about 0.88 at Tmag 13.5 |
| End-to-end recovery | Per stratum, with a 90% CI; no threshold. It enters the eligible-population statement, not calibration |
| Window-removal control | Injection windows' white σ and β match the neighbouring real-window baseline: median ratio within ±5% |

- **Failure.** If a criterion fails, the declared population is narrowed to
  where the Tmag model passes, or the pipeline is not ready. Both outcomes
  are recorded, and nothing is resampled.
- **Reproduce R6.** `python scripts/t015_confirmation_sizing.py` resamples
  hosts from `results/t015_validation/injections.csv` (PDCSAP), with 4,000
  draws per H and seed 7.

## Destination and execution order

Answer one coherent question: **can a correction learned from earlier forecast
errors improve the reliability and useful precision of later issued transit
forecasts, once outcome uncertainty, historical availability and dependence
are handled explicitly?**

The endpoint of this programme is an executable, scientifically reviewed
experiment, a complete development analysis, and publication-shaped drafts.
It is not another list of small feasibility tasks. A robust null result, a
narrower defensible population, or a demonstrated inability to identify the
proposed comparison is an acceptable scientific outcome.

Barry's 5 November chat instruction specifies the sequence: Codex drafts;
Claude critiques and revises; Codex executes sprint 1; Claude immediately
executes sprint 2; Codex critiques and fixes Claude's work; Claude critiques
and fixes Codex's work; then the collaborators reconcile. This paragraph is a
paraphrase. Routine choices and repairs stay inside each sprint; no intermediate
permission round is needed. The handoffs carry exact commits, commands,
outputs and unresolved scientific issues. The board records handoffs; it does
not automatically start the other agent.

**Protected data remain closed throughout both sprints and both reviews.**
Reconciliation records whether the package is ready for a protocol freeze.
Freeze and the first protected evaluation are the next programme, not something
silently incorporated into this draft. Preserve the distinction between an
investigator-unseen retrospective test and genuinely future observations.

## Sprint 1 — Codex: build the complete forecast experiment

**Outcome:** one reproducible development run from released source artifacts to
paired forecast scores, uncertainty, design precision and an eligible target
inventory. Claude receives a working analysis into which validated outcomes can
be inserted, plus a concrete audit of the current timing experiment.

### 1. Establish what the existing validation actually supports

Independently reproduce D038–D039 from the committed event, run and product
tables and trace the decisive code. Audit host weighting, failed runs and
missing-event denominators; matching injected truth to recovered windows;
noise overlap across runs/products; refitted shared shapes; and the effect of
removing real-transit windows. Challenge the claim that a small estimated ICC
establishes negligible dependence. Use targeted development replays when a
table-only audit cannot distinguish an actual defect from a concern.

Deliver a short actionable defect/claim table with reproducers. Repair forecast
code owned by Codex, but leave timing-pipeline repairs to sprint 2 unless a
small change is essential to establish the audit result. Do not spend the whole
sprint reviewing T015, or turn every finding into a separate handoff.

### 2. Resolve the population, forecast origin and comparator

Replace the approximate sector inventory with archived target/product metadata,
official observation windows and verified release availability. Separate
scheduled, observed, publicly available and eligible products. Do not download
protected FITS files, including merely to inspect their headers. Metadata alone
cannot establish quality-selected cadence coverage: label predicted transits as
opportunities, not successful observed timings. Resolve ambiguous boundaries
conservatively and retain a reason for every exclusion or unresolved row.

Specify both the historical cohort and the outcome pipeline's supported subset;
show their intersection and what is lost. Preserve exposure lineage and treat
FFI/120-s and SAP/PDCSAP reductions of the same observation as paired checks,
not independent outcomes. Origin-known TTV flags govern historical exclusions.

Resolve missing issued covariance explicitly. An audit of an issued point
ephemeris with a reconstructed uncertainty distribution is not validation of
the joint distribution as issued. Carry C2 reconstruction and C3 covariance
sensitivities through the actual comparison. If the conclusion depends on an
unidentified covariance choice, narrow the claim; do not silently set covariance
to zero or rename the analysis Track B. Any Track B fallback requires its own
availability-correct input ledger.

### 3. Complete a small, defensible forecast comparison

Reuse the stable mixture and chronological code. Compare the declared
unadjusted baseline, a single forecast-scale correction, and the constant
population scale mixture. The failed training-span rule remains an adverse
development result, not a candidate to keep tuning until it wins. If the
constant mixture needs regularization, specify a small bounded comparison
before running it and preserve the reason and all results.

Use earlier-only fitting with chronological development blocks where the data
support them, and host-aware resampling that refits calibration. Audit source
release transfer as well as calendar transfer. Observation dates alone do not
prove historical training availability. A present-day reconstruction with
unresolved availability remains a development stress test, not a historical
deployment simulation.

**Recommended primary contrast:** paired change in planet-balanced 95% interval
score, retaining the protocol's existing choice. Report coverage and interval
width to explain that score; use log predictive density as a secondary test of
tail failures. Fix whether the scored unit is a transit or a visit and its
within-planet weighting before comparisons; use identical units for every
method. Preserve shared ephemeris and outcome dependence in simulations and
uncertainty. Compare predictive distributions for measured outcomes by
convolving the applicable outcome model; keep latent timing intervals separate.

Build an explicit interface for Claude's outcome table: event/host/product and
cadence identity; time standard; mid-time and uncertainty or likelihood
representation; shared-shape/group information; quality/failure reason; and
measurement-rule version. Do not mix ExoClock errors and the new pipeline's
errors under a single empirically assumed multiplier. Sprint 1 uses labelled
outcome-error sensitivities; sprint 2 must rerun the calibration/scoring chain
under the adopted measurement convention.

### 4. Determine whether the experiment can answer the question

On the actual metadata design, simulate coverage and score precision under a
calibrated null, broad heterogeneity, a few influential hosts, shared outcome
offsets, covariance uncertainty and selection/failure. Distinguish power from
precision and effective hosts from transit counts. Define an attainable
scientific comparison rather than claiming that a large event total suffices.

Complete the bounded ExoClock III/IV citing-literature screen and closest-method
comparison, with dated search routes, identifiers and unresolved access gaps.
Update the novelty decision from sources actually read. This is a documented
search, not a claim to have proved the absence of all prior work.

**Sprint 1 acceptance:** runnable source-to-score workflow; audited cohort and
metadata inventory; a single proposed primary contrast; model/measurement and
covariance sensitivities; quantified attainable precision; an evidence-backed
continue/narrow/stop recommendation; and the T015 defect table. A correction
need not improve scores to pass. Supply a compact development results report
and a machine-readable handoff sufficient for sprint 2 without another design
conversation.

**Ownership:** forecast/inventory adapters, `forecast_variance_components.py`,
`chronological_calibration.py`, associated tests/results, novelty/precision
analysis, and new review artifacts. Extend existing modules before creating
new ones. Timing implementation remains Claude's. Shared coordination documents
are updated at handoff, when execution ownership transfers.

## Sprint 2 — Claude: qualify outcomes and assemble the complete study

**Outcome:** a measurement procedure qualified for a declared population,
integrated with sprint 1, and a complete candidate protocol with development
figures and three linked communication products.

### 1. Repair the outcome experiment as one coherent system

Resolve sprint 1's substantive T015 findings. Account for detection/search
failures, edge truncation, missing recovered events, window-removal effects,
shape estimation and dependence. Keep the original failed strata and their
prespecified verdict visible. Changes to their criteria define an amended
design requiring new evidence; they cannot retroactively make D039 pass.

Catalogue period may be used for **signal identification** if its provenance
and role are explicit. Prefer an origin-available value when available; using
later information requires a different, qualified claim. It must not constrain
the scored epoch through a narrow forecast-centred prior or silently act as a
fixed multi-transit timing relation. Test the entire identification, shape and
timing path with injected phase/period offsets and aliases, including residuals
beyond the present ±60-minute window. If the design cannot recover such events,
report that selection rather than concluding that forecasts have no large tails.

Resolve short-period windows first because the current disjointness rule drops
part of the nominal population. Extend long-period/multiple-catalogue-planet
handling only if the metadata/precision assessment shows it materially improves
the study. Otherwise specify a justified, metadata-defined narrower cohort;
one DRD planet per host does not prove physical single-planet status.

### 2. Run one adequately designed confirmation experiment

Use the existing inspected sample for development. Before requesting or fitting
new confirmation photometry, commit selection, estimands, acceptance margins,
minimum host counts, failure accounting and the analysis. Determine sample size
from host-level simulation, with a proposed ceiling of **120 additional hosts**
in the already permitted development era, approximately balanced over relevant
brightness strata and product types. Paired products do not add hosts. All new
photometry must satisfy the pre-request development-date guard.

Use interval/equivalence criteria tied to tolerable bias and undercoverage,
with widths supported by the design; do not require a confidence interval to
contain exactly one as evidence of useful calibration. Preserve sensitivity
to conservative but inefficient errors. Distinguish successful-recovery timing
calibration from end-to-end recovery probability, and retain every failed
attempt in the appropriate denominator. Compare the window-removal treatment
against controls that can expose selection of unusually quiet noise.

Fix a sample or a valid sequential rule in advance. Do not keep adding hosts or
relaxing margins until the result passes. A failed confirmation leads to a
documented narrower claim or a not-ready verdict. SAP sensitivity does not by
itself validate the upstream PDC response to a synthetic transit.

### 3. Integrate measurements, calibration and the future test

Generate the matched earlier development outcomes needed to support the chosen
error convention, and rerun sprint 1's full forecast comparison. A new outcome
pipeline cannot inherit calibration fitted under old outcome errors without
testing the transfer. Test shared-shape dependence and the independence of
calibration inputs from scored observations.

Deliver a candidate protocol and executable configuration covering cohort,
availability anchors, covariance tiers, supported observation regimes, outcome
failures, primary contrast, secondary summaries, chronological fitting,
uncertainty, sensitivity analyses and the rule for any later amendment. Include
the metadata-defined evaluation roster and forecast-generation command. Record
an access receipt confirming that protected outcomes remain unopened.

Exercise the complete evaluation path on synthetic and inspected development
data. Final forecasts, model parameters, cohort and code must ultimately be
hashed together at the real freeze, after reviews; a draft forecast table is
not yet a frozen prediction.

### 4. Write the scientific account now

Produce a substantive article draft with development methods/results/figures,
a broad-audience brief of at most two A4 pages, and an agent guide with exact
reproduction commands and limitations. All three use the claims ledger and
clearly separate development findings from the still-empty final-evaluation
results. Include negative evidence and the actual reason for the chosen model.
Use verified reference identifiers and existing bibliography workflows; no
invented entries. These are repository drafts, not a submission or release.

**Sprint 2 acceptance:** repaired and tested measurement implementation; a
completed, honestly adjudicated confirmation experiment; integrated development
analysis under consistent outcome errors; a candidate freeze package; and the
three source-linked drafts. If qualification fails, deliver the complete
failure evidence and the strongest supported scope. Do not manufacture a
freeze-ready verdict to meet the sprint endpoint.

**Ownership:** timing/validation scripts and tests, new confirmation artifacts,
outcome adapter, integrated protocol/configuration and communication products.
Claude may modify the sprint 1 integration interface after its handoff, recording
the reason and regression evidence. Neither agent rewrites the other's evidence.

## Counter-reviews and reconciliation

1. **Codex reviews/fixes sprint 2:** independently reproduce the primary
   validation and integrated score summaries; challenge selection, dependence,
   epoch/shape leakage and access guards; trace every headline draft claim.
   Fix demonstrated defects within scope and rerun affected analyses.
2. **Claude reviews/fixes sprint 1:** independently challenge numerical tails,
   proper scores, resampling, calibration chronology, release transfer,
   covariance assumptions, inventory and novelty; fix demonstrated defects and
   rerun affected analyses. Recheck any sprint 2 result those changes invalidate.
3. **Reconcile:** retain disagreements and adverse evidence, ensure all claims
   refer to the final code/output versions, and issue one joint recommendation:
   ready to freeze, ready only for a narrower declared question, or not ready
   with a concrete blocker. Review agreement alone is not validation.

Use existing scripts, manifests and coordination files. Run the full scientific
test suite after relevant changes plus targeted independent numerical/source
checks; avoid building a new orchestration framework. Commit coherent units,
scan staged changes before public pushes, and export reviewed correspondence
snapshots at handoff. Keep large regenerable data out of Git.

Routine implementation, bounded experiments and repairs are autonomous after
Claude's plan revision is reconciled. Fit local work to this machine's resources;
use the established Nectar workflow for heavier runs. Interrupt Barry only for
a material change of question, protected-data boundary, publication commitment,
resource envelope, or an irreducible scientific choice outside this plan.

## Requested critique from Claude

Revise this draft before execution. In particular: is the sprint division
workable; does the primary interval-score contrast remain the right question;
is the covariance/measurement transfer identifiable enough for the proposed
comparison; and can a confirmation design within the stated ceiling qualify
the useful target population? Replace weak choices with concrete alternatives.
Return a revised plan and exact accepted interfaces/criteria, not just agreement.
