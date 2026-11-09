# Article v0.4 and brief: independent review and revisions

Codex (GPT-6.1-sol), 9 November 2026, from `9eade0b`. Two bounded
delegates independently checked the article's numerical/semantic claims and
C048's source identity/saved timing evidence. The parent reviewed the brief,
derived the score-contrast bound independently and integrated corrections.
This review changes prose and reproducible presentation/checking scripts,
not the frozen analysis, data, parameters, forecasts or primary verdict.
The revised article is v0.5 and awaits Barry's review; nothing is released.

The repository has no configured scrivmark round. Its existing claims ledger,
audit notes and Git diff retain this review without adding another review
database or migrating the manuscript build.

## Triage

| Finding in v0.4 | Evidence/check | Disposition in v0.5 |
|---|---|---|
| Unbounded gains from interval widening | Parent and delegate independently derive the contrast; counterexample has fixed gain even for arbitrarily distant outcomes | Correct discussion and Figure 1 caption; C049 |
| Most predictions trustworthy; coverage fixed; targeted forecasts better | Conditional accepted sample, point coverage/width and one prior-warning case do not establish those population/policy claims | State observed coverage and selection; targeting is a hypothesis |
| HR858b proven not a measurement artefact | Saved coherent sequence and shape diagnostics reproduce; no independent extraction/identification | Support a coherent departure without categorical exclusion of error; qualify C048 |
| No development timing exists | Actual frozen 206-planet training set and saved development table exclude HR858b/host | State dataset/training membership, not absence of observations generally |
| Wrong linked arXiv paper | Correct 2411.14911 concerns TOI-396/HR858; 2604.15035 concerns TOI-5624 | Use verified Bonfanti DOI/source; retain identifier import workflow |
| DRD flag implied comprehensive prior-literature screening | ExoClock IV flag uses its own detection rule | Preserve origin-label contrast without alleging a broken flag contract |
| Audit wording implied full independent rescoring/refitting | C045 checks all Gaussian M0 events, selected grid events and bounded refits | State exact check scope and stored-draw interval reproduction |
| Old support/denominator problems still unresolved | C038–C040 resolved these before freeze | Mark old stage historical and state resolution |
| Identification leaves forecast tails unaffected | Period/variation restrictions can censor severe errors | Correct selection language |
| Old B400/B200 and top-two-host methods read as current | Final B2000 joint inference and k=0–5 diagnostic | Distinguish development and final methods |
| Earlier −2.95 simulation treated as final design expectation | Earlier full-union fixed-parameter illustration, not final core/joint-refit | Qualify simulation scope |
| Majority upper interval rounded +1.16 | Stored endpoint 1.1549094 | Correct to +1.15 |
| M1 called worst without naming the score | Standardised and raw-minute rankings differ in Table 2 | Specify the primary standardised loss; raw point comparisons do not replace primary inference |
| Brief says all code/rules frozen, never sees prediction, bug affects physical TTVs | Primary freeze versus post-unblinding secondaries, catalogue-period search and non-Gaussian likelihood path | Correct each distinction |
| Everything public | Bulk inputs/grids remain outside Git | State public compact records and hash-bound external payloads |
| TESS/MAST acknowledgements missing | Official MAST guidance and NASA processing references checked | Add acknowledgement, verified links and import identifiers; no invented bibliography |

## Correct score interpretation

For fixed nested intervals, write outward endpoint shifts as dL,dU ≥ 0 and
Δw=dL+dU. At α=0.05,

`ΔIS = Δw − 40[min(dL,(l0−y)+) + min(dU,(y−u0)+)]`.

Since an outcome cannot occupy both disjoint tails, the bounds are
`Δw − 40 max(dL,dU) ≤ ΔIS ≤ Δw`; for symmetric widening these become
`−19Δw ≤ ΔIS ≤ Δw`. Beyond both lower or both upper endpoints the contrast
is constant. A single interval's loss is unbounded with residual size;
the contrast between fixed finite endpoints is not. These are eventwise
bounds, not a universal bound across varying widths or standardisation.

`scripts/check_interval_score_contrast.py` records exact numerical identity
in 27 labelled synthetic cases and checks that all 2,185 saved event penalties
are no greater than their added standardised width. The empirical inequality
check does not itself prove interval nesting. C049 is mathematical interpretation,
not a new astronomical result or a change to the frozen scoring rule.

## C048 and references

The independent source/numeric check is
`docs/audits/d068_hr858_source_review_2026-11-09.md` and its adjacent compact
evidence. Bonfanti's verified source is
[arXiv:2411.14911](https://arxiv.org/abs/2411.14911),
[DOI 10.1051/0004-6361/202451300](https://doi.org/10.1051/0004-6361/202451300).
It establishes pre-origin knowledge, not validation of our protected timings.

The TESS mission/SPOC references follow
[NASA's documentation](https://heasarc.gsfc.nasa.gov/docs/tess/documentation.html);
development FFI products follow the
[MAST TESS-SPOC page](https://archive.stsci.edu/hlsp/tess-spoc) and
[Caldwell's paper](https://arxiv.org/abs/2011.05495).
The acknowledgement paraphrases
[current MAST guidance](https://archive.stsci.edu/publishing/mission-acknowledgements).
Identifiers are collected in `references/identifiers_2026-11-09_final.txt`.
Formal Zotero imports and the earlier introduction placeholders for ExoEcho
and heavy-tail prior art remain editorial work before release.

## Validation and handoff

All new article table values, terminal counts, model parameters, recovery,
influence and TTV group aggregates match the compact evidence, apart from the
corrected rounding. Parent and delegate independently agree on the algebraic
correction. Numerical/semantic review supports handing the revised products
to Barry without changing the inconclusive primary verdict.

Render checks and final hashes are recorded in
`results/final_review/d069_products_validation.json`. The brief must remain two
A4 pages; the article is also rendered to inspect figures/tables and glyphs.
No release, external contact or protected measurement occurs in this review.
