# D078: three-product review complete

Codex (GPT-6.1-sol), 9 November 2026, from `dbc24bd` / Claude's v0.6 at
`1d9a150`. The reviewed products are v0.6.1. They are ready for Barry's
review; no release or submission is authorised by this review. S74–S97 stay
closed. No raw photometry or headers were opened.

The main numbers and primary conclusion agree with C043–C064. The frozen
joint-refit result remains −0.121 [−1.84, +2.20], inconclusive. This review
changes wording, source positioning, historical guide instructions and layout;
it does not change code, data, models, outcomes or analysis choices.

## Review disposition

| Finding in v0.6 | Check and disposition |
|---|---|
| Brief calls catalogue ranges too narrow and attributes part of the shortfall to measurement uncertainty | Corrected to combined reconstructed forecast/measurement intervals and conditional accepted-sample coverage; no component is identified as the cause |
| Brief reassures observers that predictions can be relied on within minutes | Replaced by observed agreement among accepted timings and the need for a separate observing-window assessment |
| Brief's allocation summary omits the endpoint, discrete pad grid and success against both comparators | Names accepted measured times, five tested pads from 15 to 240 min and both equal-budget comparisons; no general operational capture claim |
| Physical-cause and artefact exclusions are stronger than D076 | Uses coherent shared-photon evidence, support for an astrophysical interpretation and rejection of a simple common timing shift; no unique cause or pixel validation |
| Abstract/methods/contributions call the pipeline forecast-blind or independent | Distinguishes epoch-blind catalogue-period search from forecast-dependent terminal acceptance; final uncorrected SPOC rule is named separately from the failed brightness variant |
| Every post-review analysis is said to have been committed before execution | Limits that chronology to the specific T017 designs/amendments and T020 designs; retrospective diagnostics remain explicitly post-unblinding |
| Universal identification/displacement cutoffs conflict with successful boundary stress tests | Describes a restricted period search and sharply reduced recovery, without a universal hard displacement cutoff |
| Loss-scale headline and limitations blur conditional diagnostics and joint primary inference | States that conditional intervals span zero; separates the corrected execution's joint primary from later conditional sensitivity intervals |
| Historical white-noise and guide defect claims appear current | Preserves the original missing-reproducer claim as historical and names the later separate reproducer; dates/supersedes old defect states and scopes old development-only language |
| Guide can resynchronise the frozen environment or overwrite bound evidence | Uses direct pinned Python for non-PEP commands and confines historical generation writers to isolated evidence checkouts; current verification remains read-only |
| Main C063/C064 guide evidence paths point only to parent reproduction checks | Links primary accuracy/exact-allocation audit directories, with parent checks retained separately |
| New Agol citation is presented only as forecast drift | Primary Section II also establishes uncertainty recalibration and later-timing checks; acknowledged as direct prior art without equating its design with ours |
| Long ideation-file path clips the article margin | Replaced its visible text with a short link; final bounding-box and visual checks pass |

## Independent checks

Three bounded reviewers independently checked article semantics/numbers,
brief/guide consistency, and the two new references. Their reports are retained
beside this file. The changed article and brief/guide passages were rechecked;
no material scientific mismatch remained after the specified corrections.
The final small scope clarifications (five discrete pads, shared-photon wording)
were applied. Parent checked the primary Agol text directly and retained the
full-text access scope in `references/literature_evidence.json`.

The two references' metadata match their DOI records. Lissauer et al. support
the period/TTV caveat. Agol et al. supply a relevant uncertainty-calibration
precedent, now stated explicitly in the introduction. These checks do not
constitute a new exhaustive novelty search.

## Product validation

- Article: 29 A4 pages; brief: two A4 pages.
- Both final brief pages inspected at full size. All article pages inspected
  in contact sheets, key tables/figures at full size, and the repaired final
  page 27 at full size. Final pages 28–29 were rerendered after that repair.
- No body text outside checked margins, replacement boxes or build warnings;
  citations resolve. Page-number footers are recorded separately from body
  margins. Sources, PDFs, build commands and hashes are in
  `results/final_review/d078_products_validation.json`.
- 160 tests, one expected skip, no failures. Native freeze verification reports
  zero mismatches against `5ec7c0f3…`.

## Remaining limits and handoff

The selected accepted-timing population, reconstructed covariance, conditional
measurement likelihood, shared photons, sparse catastrophic failures and
retrospective allocation scope remain explicit scientific limitations.
This is ready for human review, not a claim that those limitations are solved
or that an external specialist has reviewed the manuscript.

Barry should read the revised article and two-page brief. The guide and
review record provide the evidence trail. No additional research or access
decision is pending before that review.

Next: Barry — review the article and brief before any release.
