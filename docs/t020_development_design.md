# T020: bounded release-feature triage development

Codex, 9 November 2026, D073 response. This fixes the development search before
executing it. It does not freeze a new test or authorise S74–S97 access.

Use saved S56–S73 intended-event ledger rows on current-roster hosts only,
restricted to the DRC-core definition (one catalogue planet per DRC host,
period <=12 d, saved magnitude <13.5, no release-labelled DRC TTV flag).
Retain all intended events for budgets, including failures; do not use other
hosts' outcomes. Join accepted timings by the ledger's exact window ID.
Record the release-label availability limit; no external predictor is used.

The canonical event and DRD identification epoch are separate from the DRC
forecast epoch. Associate a DRC prediction by rounding the DRD-predicted
opportunity, never the measured timing. Report offsets >P/4 and period
mapping limits; do not use observed error to change cycles. Compute DRC
forecast variance with the existing C2 reconstructed covariance, explicitly
not a recovered issued joint posterior. Repeat with zero covariance as a
sensitivity. Features use DRC predictions and the released timing table at the
2022-09-27T15:26:09Z bundle origin; DRD is not a predictor.

Compare six single-feature risk rankings, with larger always flagged first:
median forecast SD; median extrapolation age/input baseline; issued-line
z-RMS; negative released timing count; median age since last input; fraction
of released rows labelled space. Missing feature values fail qualification,
not imputation from outcomes. Ties break by canonical planet name. Flag
ceil(0.10 * number of intended planets), reporting the actual fraction.
Try additive half-window pads 15, 30, 60, 120 and 240 minutes, plus no pad.
Choose the feature/pad maximising the smaller of the two planet-balanced
capture gains, with smaller pad then feature order breaking ties.

Baseline half-window is 1.95996398454 times DRC forecast SD. Triage adds the
pad to flagged planets. Proportional and additive comparators receive EXACTLY
the same total scheduled midpoint-window minutes over ALL intended events,
not only accepted events. The proportional multiplier and uniform additive
pad are solved separately within each evaluation batch from forecast-only
information and the selected flags. Durations, overheads, scheduling conflicts
and observatory visibility are outside this midpoint-window proxy.

Fit on all development hosts for a candidate, and perform a deterministic
five-fold host split (seed 2026110920). Each training fold selects its feature
and pad internally; the held-out fold flags its own top tenth by that frozen
ranking. Preserve host groups; no tuning on held-out captures. Cross-fitted
summaries are developmental stability checks, not confirmatory evidence.
Conditional host-bootstrap intervals (10,000 draws) apply to these realised
cross-fitted decisions without repeating development selection. Report the
fold choices and direct gains on all candidates to expose instability.

Capture is the indicator that the accepted measured midpoint lies in the
forecast-only interval. Primary descriptive summaries average within planet,
then across planets with accepted outcomes. Report intended/accepted counts,
zero-accepted planets and recovery by flag. Separate all-intended binary
completion bounds for missing outcomes exploit the nested common-centre
windows; they are not latent-time confidence bounds. Also report a +/-2
reported-sigma midpoint envelope as an ambiguity sensitivity, not a calibrated
confidence set or hard bound on truth. No measurement error widens a schedule.

The frozen M2 distribution is a labelled reference only, without budget
matching or a new fit; it already used some of these development outcomes.
No candidate-host outcomes enter this exercise. A new-test cohort, exact
manifest, feature-availability certification, access gate and feasibility
assessment still require T021 and independent review before Barry decides.

## Dated developmental extension before longer-horizon scoring

The first, saved S56–S73 run has 1,493 intended events on 93 planets, 1,078
accepted on 92; no accepted error meets the proposed >60-minute/3-sigma gross
miss definition (maximum 30.39 minutes). Every positive pad loses to at least
one equal-budget comparator and every fold selects no pad. This is a valid
negative result, not an estimate that a rare-gross-miss rule is useful.

Before scoring the longer-horizon slice, fix this extension: reconstruct DRC
forecasts for the ALREADY INSPECTED 2026 roster events, apply exactly the same
DRC-core/release-feature conditions, six directions, q, pad grid and host folds.
Evaluate this slice separately and pooled with the earlier slice, keeping hosts
together across eras and including all intended events for budgets. No rule
feature or pad is added in response to the negative result. Preserve the first
run unchanged; the new script/output subdirectory is separate. These outcomes
are development, not a new test or independent confirmation. The longer-horizon
and pooled candidates require separate held-out evaluation; none changes the
frozen experiment. DRD is an identification reference only; all primary rule
features and forecast windows remain DRC-derived.
