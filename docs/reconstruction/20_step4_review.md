# Step 4 cross-check

Codex, 11 November 2026; T028 / D084. Reviewed `6d9e27f`, including the two
step 4 passes `391c900` and `8918cd1`, in thread 156/message 3205.

The structure and main message stand. The compressed draft retains the
inconclusive primary result and its numerical evidence. Targeted corrections
below repair a few lost conditions, ambiguous counting units and caption
definitions. The canonical article, brief, guide, bibliography, scrivmark and
earlier reconstruction drafts remain unchanged. No raw photometry, FITS
headers, fits or new data access were used.

## Four reported appendix issues

| Issue | Evidence and conclusion | Disposition |
|---|---|---|
| E2 row counts differ from cells | `convention_comparison.json` uses catalogue training/scored counts 15/238 and 133/206; our timing conventions use 70/217 and 124/186. Scores and intervals are correct. | Remove ambiguous all-timed row counts; state both pairs by column in the caption. |
| Seven triggers versus six flags | Original comparison flagged seven control planets. After amended pairing, six planets span seven flux-route flags: WASP-18 b flags both flux versions; TOI-157 b drops below the unmatched threshold. | Name planets and flux-route flags separately. All remaining triggers have adjudications. |
| “Uncorrected rule passed” | Corrected saved summaries concern t015v3 without the brightness multiplier, on SPOC 120-s products. Analysis-bug repairs remain applied; the later amended rule uses the same samples. | State the rule and product explicitly; retain the absence of independent replication for the final rule. |
| 2,186 versus 2,185 timings | Frozen calibration: 2,186 development timings, 206 planets. Held-out evaluation: 2,185 timings, 151 planets. | Both are correct and refer to different sets. |

The independent appendix check also confirms that Claude's cut preserved all
675 numeric tokens, 45 mathematical expressions, 61 claim-ID occurrences,
two citation keys and 28 headings in order. That check alone cannot catch a
changed referent: B.4's “those are scored from the grid” incorrectly points
back to Gaussian-qualifying timings. It now says the **remaining 399** use
the grid. “Retrieved blind to scores” now says “retrieved without using
scores”, without implying an unrecorded formal blinding procedure.

Evidence: [appendix audit](../../results/reconstruction_review/step4_appendix_check.json).

## Main text and legends

- Keep the accuracy message conditional on accepted timings, including the
  abstract and final paragraph. The latter had become an operational planning
  assurance. It now restates what the measurements show. The correction's
  inconclusive **standardised interval score** is explicit; coverage itself
  did improve.
- Restore Agol's five fit-excluded **July 2024** timings and the **September**
  preprint date. “Five later timings” had reintroduced the chronology ambiguity
  corrected in D082; it does not establish a post-issue check.
- State the absolute output path used in the complete-manifest rerun.
- Keep the uncertainty-ratio summary as a **weighted median**, not an average.
  A separate recount gives event-weighted M0 coverage **2,009/2,185 = 91.945%**,
  or **91.9%** to one decimal, correcting 92.0%. Planet-weighted coverage and
  the primary inference are unchanged.
- Figure 2 marker area is `6 + 4.2√n`, not proportional to count. The caption
  now says size indicates count, as its legend shows.
- Figure 3 concerns combined forecast and timing uncertainty. Define M0/M2,
  the 2,185/151 sample, equal planet weights, post-review PIT and conditional
  fixed-parameter bootstrap intervals in the caption.
- Figure 4a contains 17/11/5 independent timings of b/c/d, distinct from the
  16 accepted b timings in panel b. Define counts and timing error bars.
- Table 2 distinguishes pooled and equal-planet quantiles; Table 3 defines
  model names and units. Planet names are join keys to the ledger, not an
  additional per-row hyperlink field.

All four figures remain unchanged and readable. The final caption/scope edits
were independently rechecked after integration, including the 2,009 count.
Evidence: [caption audit](../../results/reconstruction_review/step4_caption_check.json),
saved score tables, figure receipt and D082 source chronology.

## References and formatting

The original step 4 addition contains **ten**, not eleven, DOI-bearing
entries. All identities and all six UAT ID/label pairs verify. The Ariel,
orbital-decay and HR 858 discovery sources support their cited sentences.
The two-minute MAST DOI is correct, but the provenance sentence needed to
distinguish early FFI development from the **SPOC-only frozen calibration**.

The funding credit now names **NASA's Science Mission Directorate**, following
the mission's acknowledgment instructions. Four verified draft software
entries complete credits for tess-point, batman, astroquery and Lightkurve;
tess-point needs no import placeholder. The main bibliography is untouched.
Facilities and Software macros belong after acknowledgments at the AASTeX
build; the venue and final typesetting remain deferred.

The [source review](21_step4_source_checks.md) links the registered metadata,
primary papers and official citation/formatting instructions. Its
[receipt](../../results/reconstruction_review/step4_source_check.json) retains
source identities and hashes.

## Verification and handoff

- All 47 citation keys resolve in a scratch Pandoc citeproc build. Math
  conversion is warning-free after replacing legacy `\rm` subscript markup
  with equivalent `\mathrm{...}` markup in Appendix B.6.
- Main-text headings and structure are unchanged. Appendix numerical table
  cells are unchanged; revised counts and definitions are explicit above.
- Thirteen preserved products/planning artifacts match their pre-review
  hashes; saved figures, Table 3 and PIT outputs are unchanged.
- The native frozen manifest verifies without differences.
- `.venv/bin/python -m unittest discover -s tests -v`: 160 tests OK,
  one expected skip. No analysis code or environment changed.

Final hashes and numerical recounts are in the
[parent receipt](../../results/reconstruction_review/step4_check.json).
This completes the cross-check at the requested scope. Nothing has been
released; sectors 74–97 remain closed.

Next: Claude — reconcile D084, then Barry reviews the completed reconstruction.
