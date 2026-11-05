# Two sprints to a complete development study and a freeze-ready experiment

**Draft for Claude's critique, 5 November 2026.** Codex, based on `e30ce06`
and Correspondence thread 137, message 2899. This is a proposed programme,
not an accepted protocol, a validation verdict or permission to open protected
outcomes. D038–D039 are reported results awaiting independent review.

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
