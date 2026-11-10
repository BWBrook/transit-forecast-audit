# Step 3b review: paragraph messages and evidence

Codex (GPT-6.1-sol), 10 November 2026, from `660ff9e`; T025/D081,
thread 156/message 3164. Clear corrections are incorporated in `11`.
The reader-first/product-first order and Barry's chosen message are retained.
The reconciled section abstracts, manuscript, brief, guide, bibliography and
scrivmark state are unchanged. No displays or new observations are produced.

## Structure

Use **33 paragraphs: 6 Introduction, 8 Methods, 11 Results, 8 Discussion**.
Thirty was the draft count, not Barry's constraint. The important constraint
is one message and three or four short sentences per paragraph.

- Split old R8 into information span (R8), midpoint containment versus
  operational capture (R9), and the bounded allocation screen (R10).
- Move the retained three-minute illustration to R9, keeping R4 on calibration.
- Move the sector-105 sensitivity from pre-issue features (R7) to measurement
  robustness (R6). Its conditional uncertainty is explicitly identified.
- Split old D7 into benchmark reuse/generalisation (D7) and a possible later
  data study (D8).
- Convert outline lists inside paragraph abstracts to prose. Restore the
  actual H1–H4 questions in I6 and the conditional interpretation/full decision
  rule in M7. Framework tables and order/coverage checks follow the new IDs.

The independent structural review and its final read found no further material
issues. Parent counting, manually checked against the text, finds all 33
abstracts at three or four sentences, with at most 27 words per sentence.
Reference signposts and figure abbreviations are excluded from that count.

## Scientific corrections

| Location | Finding and disposition |
|---|---|
| I3–I5 | Avoid categorical claims about all linear uncertainties and all earlier studies. ExoClock IV already evaluates old issued forecasts against later outcomes; DRD's comparison partly reuses its fit data. The novelty statement stays bounded to the documented search and combination of procedures. |
| M1 | “BJD_TDB throughout” conflated event times with UTC release dates and unconverted eligibility boundaries. Name the two references and the five conservative boundary exclusions, without claiming a conversion. |
| M4–M5 | Keep nearest-cycle assignment before P/4 and the shared fit/support checks. Injection evidence supports conditional calibration on the two frozen samples, not complete identification or fresh independent replication of the amended rule. |
| M7 | The per-event common M0 SD includes measurement error. State conditional timing/selection interpretation, joint calibration/evaluation host resampling and all three verdict branches. |
| R1 | There are 918 opportunities without accepted timings; **730**, not 734, lack qualifying prediction-time coverage. The 734 total unqualified opportunities include four accepted timings. Avoid inferring that the actual displaced transit was necessarily unobserved. Preserve five zero-accepted planets in the planned roster table, not “every table”. |
| R3 | The longer-horizon DRC comparison was made after review on already-inspected outcomes. It is not another untouched test or evidence that protected outcomes were used before the original freeze. |
| R4/R9 | Combined M0 coverage is different from forecast-only midpoint containment. The three-minute illustration starts with the forecast-only Gaussian 95% radius, adds three minutes per side, then averages equally over accepted planets. Recomputed containment is **0.9400798843**; it is not full-transit capture or scheduling advice. The Fig. 3a residual/PIT diagnostic choice remains open, not already drawn or automatically normal. |
| R6 | Two independent programs reproduce b's departure; the b/c/d pattern belongs to one separate check. It disfavors a simple common clock offset, not every measurement error. Fix the panel mapping: DRD errors in planned Fig. 4b versus the published-reference b/c/d pattern in Fig. 4a. |
| R6, sector 105 | The sensitivity gives −0.089004, conditional fixed-fit interval [−1.879705, +1.123684]. It did not recompute the primary joint-refit interval, which stays frozen and inconclusive. |
| R8/R10 | H2 concerns information span generally, not the count of gross misses. The allocation optimum is restricted to 10% of intended planets and five pads (15/30/60/120/240 min), against both equal-budget comparators. |
| R11 | The joined per-planet table is planned; the existing event-scoring package is prepared and replayable. Keep statuses, unknowns and the five zero-accepted planets visible. |
| D3 | All four tested models miss HR858b; that does **not** show that no possible uniform rescaling could contain it. Limit the statement to tested models and the observed concentration of score gains. |
| D5/D7–D8 | Curator effort was not measured; remove “would cost little”. Features remain unvalidated candidates. Reuse/generalisation needs observation/selection assumptions; a future gross-failure study needs genuinely prior forecasts and qualified recovery/cycle identity. |

The independent numerical/status review and final check support these fixes.
Parent separately checked the loss denominator, padding formula and saved
sector-105 conditional result. The earlier numerical receipt's input digests
still match, preserving the headline accuracy, coverage, width and primary
joint-refit values. No timing, match, score, analysis code or verdict changes.

## Reference audit

[`13_step3b_reference_checks.md`](13_step3b_reference_checks.md) checks the
eight DOI-bearing candidate works against source identities and relevant
abstracts/passages. All 25 existing citation keys resolve. Dietze (2018) is
**PNAS**, not *Ecological Applications*. Gardner (2023) is correctly Gardner-led;
Ricker belongs with the TESS data description, not the transmission-window claim.

The AAS table guide is a website without a verified DOI, and a production
resource rather than evidence that Table 3 exists. The bootstrap book supports
respecting dependence generally; the accessible chapter does not validate
our exact joint host-refit implementation. That procedure remains specified
and evidenced by our protocol and receipts. No bibliography entries are added
while the bibliography is frozen. Optional context references need not become
a numerical citation target. The unverified ExoClock II scatter comparison
is retained as an open source question, outside the paragraph claims.

## Verification and handoff

`results/reconstruction_review/step3b_check.json` records sentence/ID checks,
the loss count, padding reproduction, conditional sensitivity and input hashes.
Native frozen-manifest verification reports no mismatches. Ten preserved
artifact hashes match, including the section abstracts and chosen message.
The changes are draft prose/source checks, so no new unit tests or local
suite rerun is needed. No raw photometry, headers, fits or displays; sectors
74–97 stay closed; no release or later reconstruction step is inferred.

Next: Claude — reconcile step 3b, then continue when Barry supplies the next stage.
