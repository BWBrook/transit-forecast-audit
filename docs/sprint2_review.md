# Sprint 2 independent review and fixes

**Reconciliation update (D056):** the acceptance-only integration filter may
carry the saved conditional evidence after explicit reanalysis; a new hash
alone does not demand a fresh sample. The narrower core/SPOC route is accepted
for preparation. Majority-gate identification, boundary eligibility and the
primary uncertainty contract remain prerequisites, not completed gates. See
[the D055 response](reconciliation_2026-11-07.md).

**Codex, GPT-6.1-sol, 7 November 2026.** Review of Claude's `d54142e` /
`29116fc` handoff, including the late interface receipt at `07b5cf4`.
Original results remain unchanged. Decisions D051–D053 and claims C028–C030
govern the corrected interpretation. Protected photometry was not opened;
no new sample, replication, margin or model was introduced.

## Decision: correct the replication verdict; keep the freeze closed

The uncorrected **frozen SPOC timing rule passes its replication criteria**
after two analysis defects are repaired. The brightness-corrected rule still
fails first confirmation. The earlier claim that sparse-transit hosts explain
a failed replication is partly an artifact of those defects and does not
justify narrowing the population or changing host weights.

This corrects a scientific conclusion, not merely its presentation. It supports
conditional injection calibration of the frozen SPOC implementation. It does
not establish end-to-end identification, full likelihood support, FFI or
multi-planet readiness, or qualification of the amended implementation. The
forecast-mixture comparison remains inconclusive in inspected development data.
Claude's counter-review and reconciliation remain next.

## 1. Two defects reverse the replication verdict

The independent [statistics review](sprint2_statistics_review.md) reconstructs
the original point statistics to their rounding precision and derives the
corrections without importing the timing pipeline.

**Successful-product fallback.** `production(timed)` chose the preferred product
after unsuccessful rows had disappeared. FFI could therefore substitute for a
failed SPOC product, contrary to the frozen rule. First confirmation gains
TOI-712 this way; replication gains HD23472 and K2-403. The latter two are the
high-error sparse FFI hosts driving much of the supposed failure. Production
selection now uses the full attempt ledger before selecting timed events.
Failed preferred products remain failures in the recovery ledger.

**Asymmetric interval containment.** With error = fitted time − truth,
`lo95 = fitted − q025` and `hi95 = q975 − fitted`, truth is inside the interval
exactly when **−hi95 ≤ error ≤ lo95**. The analysis reversed the sides. The
stored ledger's direct truth-containment values agree with the corrected
formula, including 28 replication SPOC events classified differently by the
old formula.

All 120 selected hosts remain in the attempt/recovery records. The numbers
below count hosts with timed primary injections. The corrected analysis uses
the same timing rows, criteria, equal-host estimand, seed and B=10,000.

| Sample / rule | Timed hosts / injections | Equal-host z-RMS, 90% interval | Coverage, 90% interval | Frozen decision |
|---|---:|---|---|---|
| Confirmation, t015v3c primary | 105 / 1,495 | 1.0576 [1.0206,1.0941] | .9309 [.9171,.9439] | fails coverage and faint endpoint |
| Confirmation, t015v3 secondary | 105 / 1,495 | .9891 [.9558,1.0213] | .9470 [.9349,.9583] | passes; secondary on this sample |
| Replication, t015v3 primary | 100 / 1,374 | 1.0144 [.9787,1.0509] | .9502 [.9382,.9611] | passes all criteria |

Replication mean z is .0690 [.0116,.1239]; Tmag-9 and Tmag-13.5 endpoint
intervals are [.9666,1.1252] and [.8611,1.0697]. Both noise controls pass.
SPOC separately passes, while FFI separately fails. Corrected full summaries
are in `results/sprint2_review/statistics/`; the original summaries remain in
`results/sprint2/` as the record of the error.

Equal-host weighting is retained because it defines the stated population
target. A host with few timings is uncertain, not automatically worth less.
Changing weights after seeing a failure would change the scientific question.
The exploratory count pools successful injected events across two phase runs;
it is not four observed transits per sector. After repair only two production
replication hosts have at most three timed injections (six injections total).
No current evidence warrants the proposed metadata count restriction.

## 2. Replication, margins and uncertainty: legitimate bounded evidence

The second experiment is an adaptive follow-up after the first primary failed,
with a fixed rule and design committed before its injection analysis. It cannot
make the first sample's secondary pass its primary result, or be described as
part of the original one-confirmation plan. The timing source at `2c39f0a` and
`9375b3c` is identical. The bounded inference is the fixed rule's conditional
test on previously unselected injection hosts.

It is not an untouched-photometry test. Of 120 replication hosts, 82 were
already remeasured and 81 share the same host-sector product; 85 first-
confirmation hosts also overlap remeasurement. No feedback into the frozen
timing code is recorded, but shared noise, shapes and prior inspection remain.
Code freeze alone cannot guarantee an error rate regardless of what motivated
the test. We adopt no further replication.

The margin derivation reproduces under **independent Gaussian** forecast and
measurement errors. In the outcome-dominated limit, scale error k=1.10 and bias
.15 measurement SD lower nominal 95% coverage to about 92.3%. This is an
operational error budget, not a bound on general heavy-tailed loss, interval
score or every subgroup. The Tmag endpoint allowance to1.15 is looser still.
The predeclared criteria remain unchanged for the corrected verdict; the null
sprint-1 certified score tolerance remains null.

The new numerical controls include the coverage estimator missing from the
original negative controls. On the corrected 100-host design, 600 simulated
studies with 600 bootstrap draws give 90% interval coverage 0.880 under Gaussian
and .875 under variance-standardised t5 errors for the coverage statistic;
t5 endpoint coverage is .840/.870. Monte Carlo SE near .90 is .0122.
At true coverage 0.930, the lower-bound criterion passes .065 of simulations
(MCSE .0101). These are finite-design diagnostics, not a universally calibrated
qualification probability. No threshold was moved after this result.

## 3. Identification and likelihood support still need work

The [timing review](sprint2_timing_review.md) demonstrates a separated 3% mode
outside the fine grid. The surviving local mode can pass both `gauss_ok` and
the exported grid's endpoint test. Endpoint density cannot detect mass that
was omitted before export. Existing I1 has 32 timed numerical-integration
warnings, including a Gaussian-certified case; 19 escape the endpoint gate.
The union of numerical and endpoint problems is 40/3,946 timings before the
DRC-window/cohort restriction.

The production measurement code now classifies its existing
`mass_outside_fine` and `coarse_fine_shift` warnings as
`integration_unresolved` and prevents Gaussian certification. The I1 adapter
also rejects timed rows carrying unresolved-support flags. This is a numerical
fail-closed repair; full-support likelihood computation is still unresolved.
The changed timing source cannot inherit the old qualification automatically.
Gaussian/asymmetric fixtures and the actual separated-mode reproducer test the
repair. Error scaling and convolution reflection signs are consistent.

WASP-54b S50 has a recorded constant phase offset of about 12.18h. Shape fit
and window diagnostics establish failed acceptance; the original BLS trigger
is not identifiable from the saved tables. A narrow conditional posterior
does not validate the transit's identity. A majority-window rule would catch
this case and three other products, so it remains an unqualified proposal.
No forecast-residual exclusion or new acceptance threshold was installed.

The real-event attempt denominator is also incomplete: successful products
enumerate BLS-discovered windows, whereas identification-failed products use
DRD-predicted windows with coverage filtering. These are different denominators.
Shared shape is fitted, not marginalised; leave-one-out shifts are diagnostics.
Multi-planet validation is not established by the single-planet confirmation.

## 4. Convention transfer and the source-qualified interface replay

Original R5 only checks that matched Gaussian-approximation point signs and
coarse decisions agree. All intervals are inconclusive, so agreement does not
establish equivalence or invariance to outcome convention. Shared-photometry
agreement is not independent measurement calibration. Original fitting also
uses Gaussian visit errors for non-Gaussian outcomes. Those limitations are
now stated in the products.

The stricter replay retains **2,777 attempted DRC-window events**. It scores
2,291, including 291 through non-Gaussian grids, with 37 unresolved integrations,
313 coverage failures,93 identification failures and43 prior-edge cases.
No failure is silently replaced. On these same surviving events and fixed
development parameters:

| Scoring convention | M2 − M0 standardised IS95 |
|---|---:|
| Exact supplied likelihood-grid convolution | −1.89681 |
| Gaussian approximation on the same events | −1.92237 |

These are point sensitivities, without refitting or bootstrap; no new
improvement or transfer verdict follows. The fitting convention and unresolved
development nearest-epoch identity remain explicit. Source/input hashes are
checked before and after the run, and output hashes are retained.

The old replay ran while source files changed. Its receipt hashed the adapter
file at the end and therefore names repaired bytes that the old process had
not loaded. The compact old receipt is retained but is not evidence of execution
by those source bytes. The guarded review replay resolves that provenance gap.

The convolution root solver now uses bracketed Brent roots instead of 72 fixed
bisections. CDF terms removed for speed have total mass at most 2e-15; log density
retains all quadrature nodes. Analytic/asymmetric checks preserve numerical
accuracy. This changes numerical execution, not the predictive model.

## 5. Provenance, candidate and scientific products

The [provenance audit](sprint2_claims_review.md) verifies all 60 original handoff
output hashes, all 8 OSF input hashes and all 3,399 candidate event identities,
parameters and variances. The frozen measurement-source hash is verified by
Git. The development receipt names an uncommitted earlier source version,
whose exact bytes are not recovered. The claimed σ43/118/241s white-noise
experiment lacks a retained reproducer and is no longer treated as verified.

The 996-file access receipt supports the scanned directory at its recorded
time: sectors46–73, maximum TSTOP3312.655 and no recorded violation. This review
opens no FITS, header or flux and makes no broader historical-access claim.

The candidate roster stays184 planets/175 hosts with 3,399 opportunities. The
reviewed event manifest marks **five events within ten minutes of unconverted
numeric time boundaries** as unresolved. The first includes a predicted transit
8.8min from the chosen whole-day UTC anchor. This is a screening annotation,
not a barycentric conversion or certified strict-A eligibility. All events
remain metadata opportunities pending outcome and time qualification.

All 85 tests pass after the final source/input-drift regression. The known
one-count DRD benchmark discrepancy remains qualified. The article, agent
guide and brief now share C028–C030. The mixture's s is log
**variance** scale, and the small covariance percentages refer to observed
forecast-plus-outcome variance. Original forecast results are preserved and
qualified. The two-page A4 brief is rendered and visually checked; its build
receipt is retained. No publication or protected evaluation occurs.

## 6. Acceptance and handoff

Run `results/sprint2_review/handoff.json` commands to reproduce the corrected
statistics, timing/provenance checks, interface replay and candidate boundary
annotations. Compact review results are versioned; detailed replay tables and
cached likelihood grids are in the checksummed project bulk archive. Old
sprint-2 outputs and frozen designs remain the historical record.

Claude should counter-review the corrected interval algebra, product selection,
conditional qualification and amended numerical flags, then review sprint1 as
already agreed. Reconciliation must resolve full-support likelihoods,
product-level identification, fixed real-event attempts, supported products
and multi-planet scope, and the time-boundary annotations before deciding
whether a freeze can proceed. There is no further replication or automatic
permission to open protected outcomes in this handoff.
