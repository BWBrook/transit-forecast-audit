# T020 development: no competitive allocation rule selected

Codex, 9 November 2026. Development only; S74–S97 remain closed. The search
and its longer-horizon extension were committed before their executions
(`6768a75`, `2e8c9e9`). The first result is preserved at `8309328`.

## Decision

None of six release-feature rankings with the fixed positive half-window pads
15, 30, 60, 120 or 240 minutes beats both equal-budget comparators in either
inspected era or their pooled analysis. The selector chooses **no additional
pad** in every full fit and every host-held-out training fold. There is no
competitive triage candidate to freeze from this bounded search. Do not
interpret identical no-pad policies' zero contrasts or [0,0] intervals as
statistical equivalence, adequate power or evidence that no other rule works.

The present evidence does not justify opening another block to confirm a
benefit of this candidate. Claude should independently review the negative
result and decide whether the scientific question warrants a materially
different development proposal, or whether to synthesise the evidence now.
No access decision is requested from Barry.

## Data and comparison

All data are already inspected outcomes from current-roster hosts. The longer
slice scores **DRC**, not DRD, against the stored 2026 timings. DRD supplies
canonical identification opportunities/cycles only. No measured timing is
used to choose a DRC cycle, feature or budget. No catalogue input from after
the DRC bundle origin enters a rule feature. Release-label/magnitude cohort
availability still needs the stated historical audit before a new test.

| Development scope, C2 | Intended planets / events | Accepted planets / events | Baseline measured-midpoint capture | Best positive-pad ranking | Gain vs proportional / additive |
|---|---:|---:|---:|---|---:|
| S56–S73 | 93 / 1,493 | 92 / 1,078 | 0.5566 | Fewest input timings, +15 min | −0.1525 / −0.2256 |
| Inspected 2026 | 129 / 2,771 | 128 / 1,974 | 0.6229 | Fewest input timings, +15 min | −0.1053 / −0.2170 |
| Pooled | 129 / 4,264 | 128 / 3,052 | 0.5979 | Fewest input timings, +15 min | −0.1097 / −0.2289 |

Gains are capture-fraction differences, not percentages. All positive pads
lose to at least one comparator; the table selects the largest minimum gain.
Zero-covariance sensitivity gives the same choice and conclusion. All six
full fits and thirty five-fold training selections choose zero pad. For the
first row's best positive-pad rule, each policy spends exactly 9,205.638842
midpoint-window minutes across **all intended events**. Missing outcomes do
not reduce the budget or the number of planets eligible for flagging.

The earlier-only sample has one zero-accepted planet, TOI-269b; it stays in
the budget/flag population. Tables report zero-accepted cases in every slice,
recovery by flag, and intended-population binary-completion bounds. Reported
capture means average accepted events within planet, then accepted planets;
they do not identify performance for the full intended population.

The baseline is the un-convolved DRC forecast window ±1.959964 forecast SD.
This is a **measured-midpoint endpoint**; its fractions are not the convolved
95% coverage from the frozen DRD experiment, latent timing coverage or full
transit capture. C2 is the existing reconstructed covariance convention,
not an issued joint posterior. The frozen M2 reference on the earlier slice
has measured-midpoint capture 0.8902 at 15,344 midpoint-window minutes,
versus baseline 6,026; it is neither independent nor budget-matched.

## Why this is not yet a test of warning about gross misses

No accepted timing in these DRC-core development samples meets D073's
>60-minute AND >3 forecast-SD gross-miss definition. The largest absolute
DRC errors are 30.39 min in the earlier slice and 36.62 min in the 2026 slice.
HR858b is absent under that name from the DRC catalogue. It cannot serve as
a DRC positive training example without an issued DRC forecast and a verified
cross-release identity. Current examples motivating rare
multi-hour failures therefore do not establish learnability in this core.

The pads begin at 15 minutes because this bounded search concerns substantial
extra scheduling around a flagged tenth. It does not rule out smaller pads,
other rankings or a wider population. Those would be new developmental
choices and must be justified openly, not silently searched until one wins.

## Interpretation and verification

Rankings are six single DRC-input features, with fixed directions. Flags are
ceil(10% of intended planets), so the achieved full-sample fractions differ
slightly from 10%; the earlier sample flags 10/93. The pad is selected by the
smaller gain against proportional and additive spending. Each evaluation
batch spends exactly the same total forecast-only midpoint-window minutes
for triage and its comparators. Host folds keep both eras/planets of a host
together; each training fold selects its feature/pad without test captures.

Conditional host-bootstrap intervals condition on realised selected rules;
they do not repeat the search and are developmental summaries. Missing-event
binary completion bounds are separate from the accepted endpoint. The ±2
reported-sigma envelope is an ambiguity sensitivity, not a rigorous bound on
true timing. Observatory visibility, duration, baseline, overhead and scheduling
conflicts remain outside the midpoint-window cost surrogate.

Five meaningful policy-contract regressions pass. An independent implementation
recomputes candidate gains, budget identities and fold selections. The initial
72 candidate rows agree to 1.11e-16, with every earlier-fold choice reproduced. The longer-horizon replay checks
144 further candidate rows and 20 fold selections to 5.55e-17, including
original ledger links and both eras of each host.
Source tables, code and outputs are hashed in receipts. The earlier design
bytes are retained as `results/t020_development/design_at_first_run.md`;
the later dated extension does not overwrite that design evidence.

Reproduce the two analyses with `.venv/bin/python scripts/t020_development.py`
and `.venv/bin/python scripts/t020_longer_horizon.py` in the restored evaluation
runtime. Separate independent replay is `scripts/t020_independent_check.py`.
These commands read saved tables only, never photometry or headers.
