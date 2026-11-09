# Independent article v0.6 review against D076

Codex (GPT-6.1-sol), 9 November 2026, read-only review of article at
`1d9a150` / checkout `dbc24bd`. No photometry or headers read, no original
source/results edited. Parent review covers bibliography and rendered PDFs.

## Overall

The principal numerical and inferential corrections are implemented. Sections
3.2–3.3 match the saved accuracy/coverage evidence; Section 3.8 correctly
states the restricted exact optimum and notes that the later/pooled optima can
beat proportional allocation while losing additive. The S105 interval is
explicitly conditional. The paper does not prescribe universal padding and
keeps the one gross miss tied to accepted planets. No new numerical defect
was found in these central results.

Remaining material corrections below are wording/provenance corrections, not
new analyses or reasons to reopen a protected block.

## Material findings

1. **Forecast independence overstatement** — `manuscript/paper.md:22`, `:118`
   (also contributions `:554`). The abstract says “a forecast-blind measurement
   rule”, and Section 2.4 says “a forecast-independent pipeline”. The method
   uses the DRD catalogue period and a P/4 forecast-dependent acceptance gate,
   as correctly disclosed at lines 122 and 128. Qualify these summaries as
   “epoch-blind catalogue-period identification with a frozen timing and
   acceptance rule”; do not imply independence of the final accepted sample
   from the forecast. This is a substantive D076 selection constraint.

2. **Blanket prospective-commit claim is false** — `manuscript/paper.md:188`.
   “The responses below were each designed and committed before execution”
   exceeds the record. Specific T017/T020 designs and amendments were committed
   before their corresponding executions. The interpretation diagnostics and
   later exact-oracle audit were retrospective analyses delivered in evidence
   commits with their outputs; for example D076's exact oracle is at
   `06fc2ca`. Replace the blanket sentence with the factual common property
   (post-unblinding analyses of saved/inspected data) and name the specific
   pre-execution designs where applicable. A dated programme proposal is not
   preregistration of every subsequent analytical detail.

3. **Hard recovery boundaries contradict the reported controls** —
   `manuscript/paper.md:501`. “Identification excludes period errors above
   0.5% and per-transit timing variations above about an hour” is too absolute.
   Section 4.5 itself reports 18/44 identifications at ±0.6% period offset and
   13/96 timings at a 70-minute displacement. Say the search is restricted to
   ±0.5% of catalogue period and recovery falls sharply for large per-transit
   displacement; those controls demonstrate censoring risk, not universal
   exclusion beyond a physical threshold. This does not weaken the actual
   strict P/4 terminal acceptance restriction, which is separately documented.

4. **Extraction-artifact exclusion in abstract is broader than the evidence** —
   `manuscript/paper.md:30`. The pattern “argues against a shared clock or
   extraction artefact” should be narrowed to “disfavours a simple common
   timing offset”. The body at lines 300–302 correctly qualifies simple
   effects, shared photons, blends/identity and absent pixel validation.
   Preserve the same qualification in the abstract; do not let its broad
   summary undo the body caveat. “Physical and foreshadowed” at line 479 also
   reads more conclusively than D076's strong but non-unique astrophysical
   interpretation; “coherent departure with antecedent information” is safer.

## Smaller clarifications that improve consistency

- `:239`, heading “The verdict does not depend on the loss scale” overstates
  the formal comparison. The alternate-scale intervals are post-unblinding
  conditional intervals, while the primary verdict uses joint-refit
  uncertainty. The table/caption is accurate. Prefer “All three conditional
  intervals span zero; the point contrast depends on normalisation”.
- `:487`, “Targeting cannot be learned at this rarity” can be read as a general
  rarity threshold; D076 establishes insufficient positive examples here and
  a restricted empirical allocation result. Prefer “Insufficient evidence
  here to train and validate a targeting rule”.
- `:512` groups the execution rerun with post-unblinding analyses, then says
  “their intervals are conditional”. The corrected execution contains the
  original joint-refit primary interval. Restrict the conditional-interval
  statement explicitly to secondary/sensitivity summaries.
- `:411` says the original σ43/118/241 s white-noise claims have no retained
  script/output/receipt “in the delivered package”. Those exact original
  numbers remain unverified, but a later reproducible white-noise script and
  output do exist (`scripts/sprint2_white_noise.py`, introduced at `191a1a9`,
  `results/sprint2_review/white_noise.json`, with different median sigmas
  42.2/113.4/232.3 s). Label the missing-evidence statement as the historical
  C029–C030 audit, or distinguish the original claim from that later added check.
  Do not silently imply that no current reproducer exists.

## Checks performed

Read the abstract, Methods 2.1–2.7, all of Sections 3 and 5–7, and the retained
Section 4 for conflicting interpretations. Compared the focal results against
D076, C043–C064 and saved accuracy/oracle/coverage tables. In particular the
six M0 coverage points (0.4311/0.6186/0.7415/0.8451/0.90794/0.97143) are below
their nominal probabilities; Section 3.3's statement is supported. Accuracy
rounding, denominator and loss-scale point/interval values agree. The “about
2%” illustration at line 487 is compatible with a two-sided exact 95% upper
endpoint after zero of roughly 180 independent fully observed hosts, but the
interval convention should be named to distinguish it from the one-sided
1.6% illustration in D076.
