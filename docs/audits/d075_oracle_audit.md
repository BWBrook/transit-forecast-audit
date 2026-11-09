# D075 oracle and ceiling audit

Codex, 9 November 2026. This independently recomputes the saved-table allocation
problem. No photometry, headers, new observations or network requests are used.
The original review script and outputs are unchanged.

## Findings

Claude's numerical MAE-ranking and coarse-ceiling tables reproduce: 87 rounded
numeric cells agree exactly. Their interpretation needs two corrections.

1. Ranking planets by realised mean absolute error is a hindsight heuristic,
   not an optimal capture-allocation oracle. Very large errors may remain
   uncaptured even after padding, while small errors just outside a narrow
   window may be recoverable. Unequal intended event counts also change the
   equal-budget comparators. Failure of that ranking alone does not prove
   that every admissible allocation fails.
2. Success against **both** comparators means beating the larger comparator
   capture. D075's displayed "weaker comparator" column uses proportional
   capture for the earlier slice, but additive capture for the other two,
   where additive is stronger. With the correct stronger-comparator comparison,
   the loose rule-free ceiling's maximum joint-gain margins are −2.052,
   +1.492 and +0.668 percentage points. Thus "at most 1.5 points" is defensible
   after correcting the label/earlier entry, but the positive bounds alone do
   not prove impossibility or establish that such a gain has no value.

The stronger claim can nevertheless be checked directly for the **fixed
policy class and these accepted outcomes**, rather than inferred from the
MAE ranking. An exact finite-allocation calculation finds no winning subset.

| Saved population | Best possible minimum gain against both comparators | Pad at joint optimum |
|---|---:|---:|
| Earlier S56–S73 | −8.7745 percentage points | 15 min |
| Inspected 2026 | −3.6937 percentage points | 15 min |
| Pooled | −4.3786 percentage points | 15 min |

These are global hindsight optima over all eligible subsets of
ceil(10% × intended planets), for every allowed positive pad
15/30/60/120/240 min. Every other allowed allocation has an equal or smaller
minimum gain. This supports stopping this policy search on the saved data.
It does not establish that forecast warnings are universally unlearnable,
that another flagged fraction/pad/endpoint cannot work, or that measurement
noise is the cause of every apparent miss.

The true optimum need not lose to **each** comparator separately. At its
2026 joint optimum it gains 1.5447 points over proportional allocation but
loses 3.6937 points against additive allocation. The pooled optimum similarly
gains 1.1978 points over proportional and loses 4.3786 against additive.
Therefore report "cannot beat both under these constraints", not "even the
optimal oracle loses to both".

## Exact calculation

For a fixed pad, each planet has:

- a known allocation cost equal to its number of **all intended events**;
- an observed capture benefit equal to its accepted-event mean capture
  increment if flagged, with zero benefit for zero-accepted planets.

A dynamic programme over number of flagged planets and summed integer cost
maximises the sum of those planet benefits. Conditional on summed cost, total
triage minutes and both uniform comparators are fixed. For every feasible
cost, evaluate baseline plus optimal benefit, subtract the larger comparator
capture, and select the largest difference. This covers every flag subset
without using the review's MAE ranking or T020 implementation helpers.

The implementation retains stored baseline widths, counts missing events in
the budget, keeps the fixed accepted-planet denominator, reconstructs the
selected flag set, and checks the optimum by direct event-level rescoring.
Three synthetic tests compare the dynamic programme with exhaustive subset
enumeration under unequal event counts/missing outcomes, demonstrate why MAE
ranking is not the optimum, and verify that success against both uses the
stronger comparator.

Reproduce with:

```sh
.venv/bin/python scripts/d075_oracle_audit.py
.venv/bin/python -m unittest discover -s tests -p test_d075_oracle_audit.py -v
```

`results/d075_oracle_audit/summary.json` retains every pad's optimal subset,
budget, comparator captures and exact gain. `review_reproduction.json` records
the 87-cell reproduction. `receipt.json` hashes source inputs and outputs.
This is a retrospective finite-data optimisation, not a fitted predictive
rule, independent validation, power analysis or evidence of latent capture.
