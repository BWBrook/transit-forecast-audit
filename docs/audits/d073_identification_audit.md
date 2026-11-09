# D073 independent audit: DRD identification with DRC scoring

Codex (GPT-6.1-sol), 9 November 2026. Bounded source and synthetic-interface
audit of D073 §4.3–4.5. No candidate-sector photometry or headers were read;
no network requests or protected commands were run. Frozen sources/configs
are unchanged. This does not qualify recovery on sectors 74–97.

## Decision

The unchanged measurement and acceptance functions can supply DRD-identified
outcomes to a separately constructed DRC forecast table. They do **not** have
a command-line switch for an arbitrary identification ephemeris. They already
hardcode DRD. Therefore do not replace their catalogue or their manifest epoch
with DRC. Keep two explicit epochs and one canonical observation identity in
the new data contract. A new outer entry point must bind access to the new
scope before invoking these reusable functions. D065 is not authorisation
for sectors 74–97.

The synthetic proof retains a one-day DRC forecast miss for a three-day
planet, despite that error exceeding P/4 = 0.75 day. Acceptance compares with
DRD; scoring compares with DRC. Confusing the two epochs loses the observation.
This supplies an executable interface proof, not an end-to-end transit-finding
test or a promise that DRD identifies every actual event.

## What the frozen path actually does

| Stage | Frozen behaviour | Required new-test interpretation |
|---|---|---|
| Input catalogue | `final_measure.measure_product` loads `load()[0]["DRD"]` | DRD identification catalogue remains hash-bound, despite scoring DRC |
| Identification | `sprint2_outcomes.identify` searches all epochs and periods within ±0.5% of DRD period; SNR ≥ 7 and boundary/depth checks | Epoch-blind conditional on catalogue period, not independent of all later catalogue information |
| Other-planet masking | DRD host membership, epochs, periods and marginal uncertainty formula | Preserve this known source of conditional recovery and multi-planet limitations |
| Physical shape/local timing | Existing `solution` and `time_windows`, same quality cuts and timing integration | No modification needed merely to score a different forecast release |
| Intended-event coverage | DRD T0 plus manifest `forecast_epoch` × DRD period, measured in unmasked quality-zero cadences | This coverage diagnoses data around the **identification reference**, not data around the DRC schedule |
| Measured-window identity | Recovered mid-time (otherwise window centre) rounded onto a DRD cycle | Window `drd_epoch` and manifest `forecast_epoch` are identification epochs |
| Final matching | `terminal_ledger` uses the supplied DRD map and manifest `forecast_epoch` | Keep DRD epoch in this legacy field; add explicit `identification_epoch` and `drc_epoch` alongside it |
| P/4 gate | `acceptance.terminal_status` compares the timing with its DRD prediction | DRC errors greater than P/4 can survive; DRD errors greater than P/4 still cannot |
| Forecast pairing | `scoring_inputs` joins forecast rows by canonical `event_id` and preserves observation identity | Forecast IDs must name the same intended event as measurement; a distinct DRC cycle number is metadata, not a new event identity |
| Scoring | Adapter uses forecast `predicted_bjd_tdb`/variance and outcome mid-time; it does not impose a DRC P/4 gate | DRC prediction and propagated uncertainty enter only after DRD-based acceptance |

D073's statement that the old search centres on the forecast being scored is
too broad. Its BLS epoch search is blind and its catalogue is always DRD. In
the original experiment the identification and forecast releases happened to
coincide. They can now differ without changing the numerical timing core.

DRD as an outcome-identification aid is later information: this is compatible
with a declared retrospective outcome audit, provided it never enters the
2022 rule features, scheduled-window centres/widths or selection of which
DRC forecasts are offered. It does not make the full measurement operation
historically available at the DRC origin.

## Executable synthetic check

Run `python scripts/d073_identification_contract.py` in the retained
measurement environment. Output is `results/d073_identification/contract.json`
and three synthetic CSV tables. The audit records hashes of every frozen
function source used.

The fixture has DRD cycle 10 at BJD 2460030 and DRC cycle 2 at BJD 2460031.
It invokes the actual measurement-row/coverage machinery, terminal ledger,
acceptance, forecast join and adapter. The download/read/hash and expensive
shape/timing-fit functions are explicit stubs; no FITS file exists or is opened.
The synthetic metadata's time standard is a fixture, not an astronomical
conversion. This scope is also labelled in the result.

Results:

- DRD identification epoch 10 is retained, with the DRD period 3 days passed
  to the shape/identification solver and coverage checked at DRD prediction.
- Terminal status is `accepted`; no windows fall outside the manifest.
- The accepted row joins a release-labelled DRC forecast. Its residual is
  −86,400 s and M0 95% measured-time coverage is zero. The adapter scores the
  large miss instead of discarding it.
- Replacing manifest `forecast_epoch` with the DRC epoch 2 yields
  `unmatched_expected_event`: silently using the wrong epoch is a real risk.
- Directly putting the DRC prediction into the P/4 acceptance gate gives
  `cycle_ambiguous`, confirming why the separation matters.
- Missing identification coverage remains `unmatched_observability_unknown`,
  while verified absence of cadences is a different terminal state.

Three regression tests pass in `tests/test_d073_identification_contract.py`.
The synthetic score is an interface output and has no scientific inferential
content. No real light curve was remeasured for this audit.

## Minimum adapter and freeze requirements

The new outer adapter should produce two linked tables before accessing any
new photometry:

1. Identification manifest: one canonical event identity, product ID, host/TIC,
   sector, DRD identification epoch/prediction and frozen boundary eligibility.
   For the unchanged functions, `forecast_epoch` explicitly aliases the DRD
   identification epoch. Do not reinterpret that field based on scored release.
2. DRC forecast table: the identical event/observation IDs, separate DRC cycle,
   issued prediction, uncertainty convention and origin-feature provenance.
   Fix the cross-release cycle map from catalogue/history metadata before
   measurement; never choose whichever DRC forecast is nearest a measured time.

Verify one-to-one cycle/order mapping across every product and flag ambiguous
cross-release mappings. Large DRC–DRD differences must not be removed because
the DRC forecast is poor. Their identity must instead be resolved by the fixed
cross-release map or retained as an explicit ambiguous opportunity. Report
both catalogues' P/4 exceedances and DRD-referenced recovery limits.

`--era development` still checks MAST end-time before a request and header
TSTOP before reading flux; sectors 74–97 exceed those limits. `--era protected`
verifies the existing D065 access record and old freeze manifest, then lifts
both numerical limits. The verifier does not compare an arbitrary command's
`--manifest` to the authorised old event list. Therefore the old protected
entry point is not an access gate for a new cohort, even if it can technically
be called with a new input path. **Do not use it as new-block authority.**
The new outer entry point needs a separate affirmative Barry decision tied
to the new freeze/manifest, product and time scope, checked before any request
or header read. Its default must refuse sectors 74–97. This audit does not
implement or activate that future access record.

Absolute output paths remain required by the known grid-path execution
limitation. The new wrapper should canonicalise the path before passing it
to frozen code. This changes output routing, not timing values.

## Endpoint and feasibility corrections

Measured-mid-time capture is a well-defined descriptive endpoint, conditional
on the measured outcomes and acceptance mechanism. It is not itself a latent
transit-capture probability. Keep all intended events and zero-accepted
planets visible; averaging only accepted events estimates accepted-event
performance. A fixed intended-population denominator with unknown recovery
outcomes can support explicit worst/best binary completion bounds, whereas
silently dropping unknown planets changes the target population.

The duration cancellation in D073 is conditional. If a scheduled full-transit
window is F ± (h + d/2) and the actual transit lasts exactly d, full capture is
equivalent to |true mid-time − F| ≤ h. Adding d to every policy's per-event cost
also preserves equal total budgets on a fixed event list. With unknown or
incorrect durations, this equivalence does not establish actual full-transit
capture or actual telescope-minute requirements. Use **mid-time window
minutes** for the present duration-free surrogate. Operational full-transit
language needs an issued duration and its stated assumptions.

A boundary within 2 reported σ is an ambiguity sensitivity, not a rigorous
bound on latent capture: reported σ is not a hard support bound, and some
timings have non-Gaussian likelihoods. Report the measured-time endpoint
exactly, then label the ambiguity analysis and its assumptions. Do not add
post-observation measurement error to allocated windows.

Finally, projecting an interval half-width and comparing it with the same
development-selected rule/pad's training gain is an optimistic feasibility
criterion. Fix a decision-relevant effect/precision target, or use honest
host-held-out development performance with uncertainty in the projection.
No power or confirmatory readiness follows from the interface check here.
