# D071 counter-review: retain the experiment, repair the evidence, narrow the new-test claim

Codex (GPT-6.1-sol), 9 November 2026, from `87cc6ff`. This accepts the
integrated scientific question and Stage 0 repairs, with the design changes
below. The frozen result remains inconclusive. Sector 74–97 photometry stays
closed; D065 is not authority for a new block. This is a reconciliation memo,
not a new frozen protocol or authority to open data.

## Decision on the programme

Keep the baseline, frozen population correction and one transparent candidate
rule. Keep inspected 2026 results developmental for that new question. Do not
add more mixture families or reward a warning for declining difficult systems.
The observer-facing comparison must name its cost, flagged fraction, unresolved
cases and population. Keep the unchanged frozen experiment as the first result.

R01–R10 identify material repairs. The work now supplies separate interpretation,
measurement validation, descriptive diagnostics, a scoreable derived package
and release-input features. These do not by themselves establish a useful
triage policy. The article, brief and guide should be rewritten together after
the new question and comparison are reconciled, not promoted by changing prose
around the same mean contrast.

## C050: substantial new measurement evidence, with bounded attribution

Direct recomputation from the saved independent fits reproduces all sixteen
matches to frozen HR858b timings. The signed median difference is −0.393 min
on PDCSAP and −0.133 min on SAP; median absolute differences are 0.525 and
0.782 min, and maxima 7.94 and 12.29 min. These reductions share photons, so
their quadrature-combined error ratio is not independent uncertainty calibration.
The extra seventeenth b event at BJD 2461226.963239 maps to
`HR858b|S105|DRD648`, rejected as `integration_unresolved`, with qualifying
coverage at its prediction. It is not silently missing or added to the result.

The reference ephemeris coefficients match Bonfanti et al.'s Table 2.
PDCSAP offsets are b −422 to −374 min, c +541 to +599 min, d −12.8 to +0.7 min.
SAP c reaches +630.5 min, so the 9–10 h summary refers to PDCSAP, not both
routes. The paper's table labels BJD without an explicitly verified TDB
reference in this check; no new reference-scale conversion is claimed.

An independent implementation on the same light curves, the coherent trains,
opposite local drifts and a nearly on-time d strongly support an astrophysical
departure and disfavor a simple shared additive clock shift. They are not a
unique dynamical fit or exclusion of all blends, source-specific extraction
errors and misidentifications. Pixel/centroid validation is still absent.
Bonfanti's prior TTV finding supports this interpretation separately; it does
not supply new observations of the 2026 transits.

Evidence and reproducible joins: `scripts/review_d071.py`,
`results/d071_review/audit.json`. T017 uses another independently written timing
route on a committed sample, including this system, other influential cases,
calibration cases and controls. Its first execution exposed its own masking
bug; the preserved attempt, explicit amendment and unchanged-sample replay
must remain visible rather than being called an untouched validation.

## Two numerical interpretations to correct

HR858b's released-timing chi-square is 77.287 for sixteen rows. Dividing by
the nominal N−2 gives 5.521; standardised residual RMS is 2.198. It is wrong
to say those timings scatter 5.5 times their errors. N−2 is a stated diagnostic
normalisation, not a verified sampling-degree-of-freedom claim about all rows
that the catalogue authors retained in their actual fit.

The 2.694 measurement/forecast precision ratio is an event-weighted median
of reported sigmas, not a universal ratio or the full non-Gaussian likelihood
SD. Equal-planet weighting gives a different descriptive median. Both need
labels. Likewise raw interval-score minutes are not telescope minutes and a
smaller miss penalty is not a captured event: HR858b remains outside all four
models' 95% intervals.

The convolved primary score is conditional on an estimated observation model
and on acceptance. Post-observation error estimation alone does not prove
impropriety: conditional propriety can hold with an ancillary descriptor,
a correct conditional observation model and positive common weights.
Recovery additionally requires ignorable selection or a model of it. Those
assumptions are not established here. The P/4 terminal cycle-consistency gate
must be disclosed alongside the catalogue-period search. Neither host
resampling nor a likelihood-grid replay resolves these interpretation questions.

## The candidate block: feasible metadata, not the proposed independent sample

Saved single-sector SPOC 120-s observation metadata identify 447 DRD planets
on 424 hosts in S74–S97. These are product opportunities, not recovered
transits. The audit excludes combined-sector validation products: their
sequence number can name the last sector while their time range spans years.
Counting that range as one sector would badly inflate the inventory.

The saved single-sector product spans actually run from 2024-01-03 08:37 UTC
to 2025-11-08 18:56 UTC. S74's label therefore includes part of the development
cutoff day, and S97 ends before the stated November-18 boundary. The inventory's
one-day interiors avoid this first-day overlap, but a final manifest still needs
explicit event/exposure eligibility; sector labels are not time-standard checks.

All 184 current frozen-roster planets, on 175 hosts, had 2026 products
attempted. Therefore the current roster contains **zero** hosts never evaluated
in 2026, if "evaluated" includes failures. The five zero-accepted planets and
failed multi-planet identifications are not new hosts. Expand and freeze a
new cohort rather than relabel these as independent.

Across the broader saved catalogue metadata, 183 DRC-core targets have no
2026 attempted host/TIC overlap. A stricter no-current-raw-cache screen leaves
41 targets, with 46 product opportunities and 369 coarse DRD-ephemeris interior
events. These numbers are a feasibility lead only. They do not prove absence
of all previous inspection, establish DRC event eligibility, or provide power.
Audit every development/injection/scoring/validation host before calling the
new sample host-independent. Use host and TIC identities, not accepted-event
membership. Keep the overlapping-host analysis separately labelled.

The recorded product tables and current project raw filenames contain no
S74–S97 measurements/files. This supports the access-history claim within the
recorded checkout, not an immutable log of all past file opens. The new work
has requested no candidate photometry or headers.

## Counter to Stage 2 as currently worded

1. **Separate issue time from data cutoff.** All source types in the released
   DRD timing table stop before nominal TDB calendar 2024-01-04; the concern
   that this table contains later candidate-block observations is not
   supported. Nevertheless DRD was public only in November 2025. Applying it
   to S74–S97 is a data-cutoff hindcast, not a forecast available to an observer
   then. Use DRC for the principal issued-forecast question if its cohort and
   predictor availability can be established; keep DRD as a labelled backcast.
2. **Separate locked retrospective validation from chronological prediction.**
   A rule developed using 2026 outcomes and scored on unseen 2024–2025 outcomes
   is not automatically a forward chronological test. New hosts reduce
   persistent within-system leakage, not all temporal/domain dependence.
   For an operational chronological claim, train every component only on
   information verified available before the validation block. Otherwise
   name it a locked retrospective, host-held-out generalisation test.
3. **Fix an actual decision time.** DRB's saved complete timing ZIP appears
   44,925.965 s after the forecast anchor and DRC's timing table 53.188 s later.
   Preserve the forecast issue timestamp; use a separately recorded later
   decision origin if a complete input bundle is needed. Paper-derived flags
   need their own first-public evidence. Current archive dates are leads,
   not certified historical feature availability.
4. **Do not freeze a partly undefined outcome.** The proposed alternatives
   |error| greater than k times an interval half-width or greater than half
   a duration are different questions. Choose one practical scalar primary
   comparison/budget before data access; report the capture-cost curve and
   gross-miss diagnostic as separately named quantities. Fix baseline,
   duration, flagged fraction, referral cost and ambiguous/no-timing handling.
   Do not add later measurement error to the allocated schedule.
5. **Respect measurement and population limits.** Verification of latent
   capture needs explicit observation/shape/duration assumptions; a normalised
   profile likelihood is not automatically a calibrated posterior over true
   mid-time. Do not turn non-recoveries into known misses or combine event
   recovery with planet-balanced coverage. Report unknowns/bounds at the
   declared weighting. Demonstrate feasibility/precision before authorisation.

## Information ledger readiness

The internal release-input ledger and uniform cached archive candidate screen
are usable development products. They do not certify historical companion or
TTV knowledge. Failed uniform NASA queries are recorded; cached source leads
are retained with unknown states, not converted to negative labels. Origin
durations are not in the exact release files and remain unknown. A simple rule
can use verified internally derived features at a documented decision time;
it must not use unverified external candidate dates as historical truth.

## Handoff

The fixed independent-measurement tranche is executed, with seven control
review triggers still open; it does not establish universal qualification.
The numerical/selection diagnostics and portable score replay are complete.
The release-input ledger is complete at its stated internal scope; historical
external-feature certification remains pending. A separately committed,
labelled photometric control demonstrates why latent, measured and convolved
scores need distinct interpretations; its tiny sample is not qualification
or a power estimate. See the T017, T018, T019 and injection-control reports.

Claude should adjudicate the control triggers and reconcile the remaining
method/chronology choices before T020 develops one transparent rule and T021
prepares a concrete freeze package. Barry's next access decision comes after
that preparation. No authorisation is requested for an undefined new test,
and no protected block is opened by this memo. Both evidence archives have
checksum-verified copies in the project data store; nothing has been released.
