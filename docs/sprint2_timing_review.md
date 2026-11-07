# Sprint 2 timing and identification review

Codex, 7 November 2026. This is a review of the existing development tables and
bounded synthetic profiles. No photometry was opened, no data were acquired,
and no confirmation or replication was rerun. The frozen t015v3 results remain
the results of their recorded source version. Reproduce this review with:

```bash
.venv/bin/python scripts/review_sprint2_timing.py
PYTHONPATH=tests .venv/bin/python -m unittest test_sprint2_timing_review test_sprint2_outcomes test_t015_numerics -v
```

The hash-recorded table checks and synthetic result are in
`results/sprint2_review/timing/audit.json`.

## Finding repaired: unresolved integration could pass Gaussian certification

`t015_timing_pipeline.time_transit` first integrates a coarse ±60-minute grid,
then integrates a fine grid within ten estimated standard deviations of its
median. It already flags mass omitted by the fine grid and unstable coarse/fine
medians. The frozen `sprint2_outcomes.time_windows` accepted these flagged rows
unless they also had prior-edge mass. Its Gaussian check used only the fine
grid's 68% and 95% quantiles.

A synthetic timing likelihood consisting of 97% N(0, 20²) plus 3%
N(1800, 20²), with coordinates in seconds, reproduces the defect through the
actual integration function. The fine support is about [−216, +218] seconds;
the omitted mass is 0.03; neither prior-edge test fires; endpoint relative
densities are below 5×10⁻²⁶. The quantile Gaussian check passes after the second
mode has been discarded. An endpoint-only check cannot detect that omission.
The mocked flux model and fixed baseline coefficients are a device for
supplying this specified chi-square profile, not simulated astronomical data.

The minimal repair in `scripts/sprint2_outcomes.py` makes either existing
`mass_outside_fine` or `coarse_fine_shift` flag a terminal
`integration_unresolved` status and prevents Gaussian certification. It retains
the integration diagnostics. Thresholds, fits and likelihood supports are
unchanged. The two regression tests cover the omitted secondary mode, an
unstable coarse/fine median, and successful acceptance of a resolved profile.

The old I1 table contains 32 timed rows with `mass_outside_fine`, one of which
also has `gauss_ok=True` (`LHS3844b|S68|SPOC_120|D2971`). This is a demonstrated
acceptance defect, not proof that 3% was omitted in any particular real row:
the old table does not retain the actual omitted-mass value. The amended source
has a different rule hash and has **no independent qualification**. Existing
confirmation results must not be relabelled as validation of this repair.
Among the other 31 flagged rows, 13 are already rejected by the adapter's
endpoint gate and 18 pass it. Including the Gaussian row, 19 numerical failures
therefore escape that gate. The union of integration-flagged and endpoint-
unresolved rows contains 40 of the 3,946 existing timings, before restricting
to any forecast cohort or calendar window.

## WASP-54b S50: demonstrated acceptance failure; BLS cause unresolved

All six reported S50 window centres are 12.1812 hours earlier than their
DRD-predicted event centres. The recovered period is the fixed catalogue
period, 3.69359933 days, and `period_constrained=False`. This is a constant phase
offset, rather than cumulative period drift within the sector. A DRD comparison
describes the diagnosed failure; it is not a permissible rejection rule.

The identification SNR is 429.85. The accepted product shape has reduced χ²
228.195 and q1 at its bound. Three windows satisfy the pipeline's coverage
criteria: two have prior-edge mass; the third is accepted, with reduced χ²
449.388, β=2.957, white σ=12.349 s and scaled σ=796.786 s. That third row passes
the Gaussian quantile test and has a LOO shift of only −0.287 s. Large residual
noise can therefore be converted into a broad, Gaussian-looking conditional
timing likelihood at the wrong window. Neither high BLS SNR, Gaussian quantiles
nor a small shape-LOO shift establishes correct transit identification.

These tables do not record the pre-shape BLS epoch, duration, phase profile or
alternate peaks. They cannot establish which photometric feature first drew
the search to this phase. Calling the root mechanism a particular alias,
detrending artefact or software bug would exceed this review's evidence. The
S46 product has reduced shape χ² 0.969 and agrees with catalogue timings; the
source identity and timing-standard fields do not suggest a uniform conversion
offset across both sectors.

A possible prospective check is product-level train consistency, with acceptance
specified before another qualification test. Requiring a strict majority of
covered windows to time would flag WASP-54b S50, using no forecast residual.
It would also reject K2-333b S72 (1/2 timed), Kepler-41b S54 (4/12) and
Kepler-435b S55 (1/3), removing six other currently timed rows. Their rejection
is not independently justified by this diagnostic. No such rule was installed.
Other prospective diagnostics worth specifying are per-window transit-versus-
baseline evidence and an explicit product-shape goodness-of-fit failure state.
Their thresholds and selection effects remain unqualified.

## Period and alias boundaries

The search uses catalogue P±0.5% with a blind epoch. When 0.5% of the time
baseline is shorter than its selected BLS duration, it fixes P to the catalogue
value. This is a heuristic resolution rule, not evidence that the true period
lies inside the range. S50 illustrates that catalogue-period restriction alone
does not identify the correct phase.

Existing development identification tests find 18/44 accepted products at
either ±0.6% period offset, versus 44/44 at ±0.4%. At ±0.4% there are still
unmatched and edge outcomes, and a maximum |z| of 7.45 for timed events on the
positive side. Aliases at twice and three times P produce many accepted
products; the twice-P test includes one spurious timed window. These tests
support conditional timing recovery and documented failures, not universal
alias detection. The ≥70-minute TTV tests also retain some timed events because
the matching gate is relative to the recovered train, whose epoch and period
can move; the gate is not an absolute TTV limit about the injected base train.

The `id_period` helper prefers DRC, then DRB, then DRD. Its description as the
“earliest” release is inaccurate: DRB predates DRC. The source and date are
recorded in I1, so this does not hide the actual choice. It should be described
as an explicit release preference unless a new choice is justified. The DRD
fallback is a present-development identification aid, not historical information
available before DRC or DRB issuance.

## Ledger and dependence checks

Across all products and control modes, the development, confirmation and
replication ledgers have 5,109, 8,120 and 7,684 distinct intended-truth IDs.
No truth ID is duplicated; every run with a recorded `n_truths` has that many
truth rows; no recorded match exceeds its 3,600-second gate. The Hungarian
assignment enforces one-to-one matching and is independent of recovered timing
residuals. Spurious windows have separate empty-truth rows, including four
spurious timed windows in the replication. They belong to an identification
false-positive denominator, not to calibration conditional on a matched truth.

There are 4, 6 and 5 timed truths labelled unobservable in the three samples.
This can occur because truth observability and recovered-window coverage use
different fitted shapes and centres. Calibration and recovery populations
therefore differ by design; their denominators must remain explicit. The
statistics review handles the separate product-selection defect.

The real-data I1 path is not an intended-event ledger. Successful products
enumerate recovered BLS windows; ID-failed products enumerate covered
DRD-predicted windows. An exception caught by `safe` returns no attempted-event
rows. Consequently “4,615 attempted” means rows emitted by these branches,
not an independently fixed denominator of all observable physical transits.
The frozen event manifest must remain the source of any future attempted-event
denominator.

All 4,615 existing I1 event IDs are distinct. Of 3,946 timed rows, 42 have no
estimable shape-LOO diagnostic. Among estimable rows the median absolute LOO
shift is 0.020σ and the 99th percentile 0.338σ; four exceed 1σ and the maximum
is 16.10σ. LOO keeps the period, BLS identification and windows fixed and
refits only shape. It omits shape uncertainty from the timing likelihood; it
cannot diagnose phase misidentification. The LOO refit also drops the original
identification-derived a/R* bounds because these bounds are not saved in the
returned shape. Its shift is therefore a conditional sensitivity diagnostic,
not a marginal timing error or a complete independent remeasurement.

## I1 likelihood semantics checked

The 404 stored non-Gaussian grids use the β·max(1,√χ²) error-scaled fit, matching
the reported σ: reconstructing their 68% widths differs from rounded table σ
by at most 0.000505 s. The adapter independently rejects 21 grids by its
endpoint test. This is separate from the fine-grid omitted-mass defect.

The flat timing prior is constant only within the original ±60-minute support;
the exported fine support can be narrower still. A saved grid is a conditional
profile likelihood in true-midtime-minus-reported-midtime, with fitted transit
shape fixed and baseline coefficients profiled. It is not an unconditional
sampling distribution of timing error and does not marginalise shape
uncertainty. The adapter's reflection is correct: for offset x=Ttrue−Treport,
the observed forecast residual is latent forecast error minus x. Its density
uses p_forecast(residual+x). The grid and Gaussian routes are therefore
consistent in sign. Conditional scoring still needs a calibrated outcome rule;
same-photon agreement cannot supply that calibration.

Full-support likelihoods, a qualified identification rule, a fixed physical-
event denominator and separate qualification of any amended timing source
remain open. This review adds no new sampling, replication or criteria.
