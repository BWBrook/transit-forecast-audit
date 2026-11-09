# Independent review of the v0.6 brief and agent guide

Codex, 9 November 2026, from `dbc24bd`. Read-only semantic review of
`docs/brief.md` and `docs/agent_guide.md` against D076, C043–C064 and the
article's stated scope. No product, ledger, raw photometry or header was
changed/read. No network requests, environment changes or new analyses.
This report is the only file written by this reviewer. Line numbers below
refer to the reviewed source at `1d9a150`.

## Decision

The headline numbers now match D076, and the guide's new concepts preserve
most of its important qualifications. The brief still has material
interpretive drift; the guide retains contradictory legacy instructions.
Make the targeted corrections below before presenting the products as having
passed the D076 review. No further research or new-data access is needed.

| Location | Finding | Required correction |
|---|---|---|
| Brief 9, 31 | “The quoted uncertainty ranges were slightly too narrow” and the shortfall “partly reflects our own measurement uncertainty” imply an attribution the comparison does not establish. C063 already incorporates the supplied measurement likelihood. The shortfall is not simply the effect of omitting that uncertainty. | Identify the compared ranges as combining the reconstructed catalogue forecast and supplied measurement uncertainty. Say coverage is conditional on that description and cannot isolate the catalogue SD or the cause of undercoverage. |
| Brief 35 (also 11) | “The one big miss is physical”, “the signature of planets tugging on each other”, and “against a clock or software error” restore a stronger causal/artifact-exclusion claim than D076 permits. | Report reproduction by independent implementations on shared SPOC photons. The b/c/d pattern supports timing variations and disfavors a simple common clock shift; it does not uniquely identify dynamics or exclude every software/extraction/identity error. |
| Brief 39 | “No choice of planets did so” omits both the fixed pad grid and requirement to beat BOTH equal-budget comparators. The exact later/pooled optimum can beat proportional allocation while losing additive. “Capture more transits” also reads as physical observing capture, rather than the accepted measured-midpoint endpoint. | Name the fixed tenth, five tested pads from 15 to 240 min, accepted measured-time containment and both ways of sharing the same time evenly. Do not generalise to all allocations, continuous pad choices, full-transit capture or all warning rules. |
| Brief 43 | “Observers can rely on these predictions to within minutes for planets like those tested” is a prospective reliability/operational assurance, exceeding the selected accepted-timing description. | Describe the observed minute-scale agreement and explicitly retain the recovery/selection scope. No validated safety margin or future-capture guarantee follows. |
| Brief 51 | “A file-path fault was fixed” can imply a frozen-code repair. The actual execution correction changed the output-path form and reran unchanged frozen code. | Say the output path was corrected and the unchanged code rerun in full, preserving previously completed results. |
| Guide 154–156, with 82 | Non-PEP commands still use project `uv run --extra analysis python`, despite the explicit warning that project synchronisation can change the exact frozen runtime. Bare `python` commands elsewhere are also not pinned to the evaluation interpreter. | Use `.venv/bin/python` for the non-PEP analysis commands; retain the separately pinned PEP 723 measurement-script commands. Label historical replay that needs different environments/commits as isolated replay. |
| Guide 132–147, 195–203 | The “Decisive commands” include legacy freeze/receipt writers that can overwrite hash-bound pre-access artifacts in the expanded raw archive. A later warning says not to regenerate the receipt in place, but the executable list remains easy to follow unsafely. | Mark the old generation commands as historical, not current-checkout instructions. Reproduce them only in an isolated checkout at their recorded evidence version; use the native current verifier for the authorised package. |
| Guide 311–312 | C063/C064 evidence map names only `results/d075_review_checks/`, which is the parent/native reproduction check, rather than the primary corrected accuracy/oracle result directories. | Point C063 to `results/d075_accuracy_audit/` and C064 to `results/d075_oracle_audit/`; list the parent receipt as an additional independent check. |
| Guide 316–345, especially 334 | The current-looking “Known limitations and open defects” retains old unresolved shape/calibration statuses and says “All results are development material” under “Limitations to state in any derivative work”. This directly contradicts the current frozen primary and can restart superseded work. | Clearly mark this block as a dated historical snapshot, superseded by D051–D076/current Section 12. Scope “all results” to the old development outputs, and prevent old “Open” labels being read as current tasks or freeze blockers. |

## Compact replacement wording for the brief

These are source suggestions, not edits made by this reviewer.

For the coverage sentence:

> In this comparison, the uncertainty ranges combine the reconstructed catalogue
> forecast with our measurement uncertainty. Counting each planet equally,
> the nominal 95% ranges contained 90.8% of accepted measured times. This
> shortfall does not identify which part of that uncertainty description is
> wrong.

For the later coverage paragraph, remove the claimed causal attribution:

> These ranges include our measurement uncertainty. Their undercoverage depends
> on that description and on the reconstructed catalogue covariance, so it
> does not establish that the catalogue's uncertainty alone is too small.

For HR858b:

> Two separate timing programs reproduce HR858b's large departure from the same
> TESS data. Planet c runs late while d is nearly on time. The pattern supports
> timing variations and argues against a simple shared clock shift, although
> the programs share photons and there are no pixel-level checks.

For the targeting paragraph:

> We tested wider time windows for a tenth of the planets, using five extra
> pads from 15 to 240 minutes. No permitted choice contained the accepted
> measured times better than both ways of sharing the same extra time across
> all planets. This result applies to that fixed comparison, so we stopped
> without opening the untouched data to test a warning rule.

For the first sentence of “What it means”:

> Among the transits we could measure in these selected samples, most
> prediction differences were minutes; a future observation still needs its
> own timing and observing-window assessment.

## Checks that do pass

- The 151/2,185 and 150/151 within 26.4 min figures match C063. The earlier
  DRC bound of 37 min for 128 accepted planets is accurate with its stated
  sample qualifier; “up to four years” is a coarse description of the
  inspected blocks, not continuous monitoring.
- The brief's −0.12 [−1.84, +2.20] comparison retains the frozen joint-refit
  interval and its inconclusive meaning. The guide explicitly distinguishes
  primary joint-refit inference and conditional sensitivity implementation.
- The 40/151 improvement count, 70% intended recovery and 92%
  prediction-qualified recovery match the ledger's different denominators;
  they are not coverage fractions or full-transit capture.
- The guide's new covariance, conditional/convolved coverage, fixed-policy
  allocation, two-epoch and closed-block concepts are substantially aligned
  with D076. Its new primary-runtime paragraph is correct; the executable
  legacy command list needs to be made consistent with it.
- Neither the brief nor guide makes the optional “about 2%” illustration as
  a numerical rate claim. The article's illustration remains for the parent
  and article reviewer to check.

The highest-value corrections are the brief's coverage attribution, HR858b
causal certainty, targeting scope and prospective reassurance, followed by
removing the guide's current-looking historical instructions. These are
bounded source corrections; they do not change any numerical result.
