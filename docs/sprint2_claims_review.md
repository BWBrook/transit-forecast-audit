# Sprint 2 provenance, candidate package and draft-claims review

Codex, 7 November 2026. This review checks the original Sprint 2 package at
`d54142e` / correspondence snapshot `29116fc`. Production repairs are being
integrated separately; original results below are arithmetic/source checks,
not endorsement of their statistical qualification. No FITS file was opened,
no photometry was downloaded, and no protected outcome was inspected in this
review. Only this document, the audit script and its assigned output directory
were written.

Reproduce the mechanical audit:

```bash
.venv/bin/python scripts/review_sprint2_provenance.py
```

Evidence: `results/sprint2_review/provenance/audit.json`, `handoff_hashes.csv`
and `source_hashes.csv`. The script refuses reads of FITS files or anything
inside `data/raw/mast/`. It reads recorded photometry identities rather than
recomputing raw FITS hashes.

## Result

The compact package has consistent stored bytes and candidate identities.
All 60 output hashes in `results/sprint2/handoff.json` match, as does its
handoff-script hash. All eight local OSF source artifacts match the source
manifest. The candidate roster, 3,399 events, 3,399 draft forecasts, parameter
file hashes and covariance calculations reconcile without a discrepancy.

The package remains a candidate. In particular, the paper's strong R5-transfer
wording, production qualification and proposed four-transit restriction require
reconciliation with the methodological review. A preserved number can be
reproducible while its interpretation or selection rule is wrong.

## Findings requiring reconciliation

1. **Recompute qualification before retaining the failed-replication/few-transit
   account.** The parallel statistical review identified success-dependent
   product fallback in `production(timed)`: failed preferred SPOC products can
   be replaced by FFI products after outcomes are known. Its correction belongs
   to that review, not this audit. Until reconciled, C025, the report decision,
   article Abstract/sections 3.6 and 4, brief sections on measurement and next
   steps, and guide qualification statements must describe the original
   algorithm's results as superseded arithmetic. The “four timed transits”
   split was chosen after inspection and conditions on successful outcomes.
   It is not the metadata rule “four predicted transits per sector.” Original
   sparse-host failures may reflect the product-selection defect rather than
   a valid population boundary. Do not redesign weights or discard hosts to
   explain that defect.

2. **R5 checks sign/decision agreement, not transfer equivalence.**
   `scripts/sprint2_forecasts.py` constructs its acceptance Boolean from equal
   signs and equal decision labels. The six matched M2 contrasts are negative
   and all six intervals cross zero. This reproduces the declared operational
   R5 gate; it does not establish equivalent calibrations, negligible convention
   effects or protected-era transfer. The matched release-transfer fit has
   only seven training planets. Use “the development sign/decision gate is
   met” and retain these limits. Article section 4's claim that the open
   question concerns the outcome rule “and not the transfer” exceeds this
   evidence. Same-photon agreement is not independent validation of outcome
   uncertainty.

3. **Correct the mixture definition.** The implementation uses
   `SD = b * sqrt(v_f) * exp(0.5*s*z)`: `log(lambda) ~ N(0,s^2)` multiplies
   forecast variance. The candidate configuration says this correctly.
   Article section 2.2 instead says that s is the log-scale SD of an SD
   multiplier. That changes the stated model. The guide should explicitly
   identify lambda as a variance multiplier as well.

   The same section misstates C004's denominator: 0.27%, 0.98% and 2.94%
   are covariance cross-term fractions of the *observed forecast-plus-outcome*
   variance. `covariance_review.csv` gives forecast-only maxima of 0.77%,
   1.36% and 8.14%. Correct the denominator or use the forecast-only values.

4. **Separate recorded non-access from proof of all historical non-access.**
   The recorded access receipt is a header-only directory scan at
   `2026-11-07T06:26:59Z`: 996 files, S46–S73, maximum TSTOP
   3312.655117498639, limit 3313.49, no recorded violations. This supports the
   scanned directory at that time. It does not prove that no file elsewhere
   was requested/opened earlier; the scan's `protected_outcomes_accessed`
   Boolean is computed from current guard violations. Article section 6's
   “No product after 2025-11-18 has been requested” requires a request audit
   that is not in this package. State the standing boundary and the observed
   receipt separately. No violation was found by this metadata review.

5. **Use the independently guarded interface replay for final source attribution.**
   The original package had no production scoring receipt and article section
   3.7 had `{{S2-INTERFACE}}`. During review, Claude added one at `07b5cf4`,
   also filling that slot. It records 2,777 attempts, 2,310 timed production
   events, 467 omissions and 309 non-Gaussian events. Its adapter source hash
   is `d0b32e7d...`, while the adapter committed in both `d54142e` and
   `07b5cf4` hashes to `81fd76c8...`. The recorded hash matches the repaired
   adapter later committed at `d9c1570`. The adapter hashes `Path(__file__)`
   at run end, so a source edit during scoring can attribute old imported code
   to new disk bytes. The predictive-core hash matches all three commits.
   Thus this late receipt does not certify the code loaded by the old process.
   Preserve the mismatch and use the independent replay with source hashes
   captured before execution and verified unchanged at completion. That
   replay is being checked separately. Preserve row counts, failure reasons
   and hashes in its committed compact receipt; an ignored intermediate alone
   would not make the paper reproducible.

6. **C022's white-noise claim lacks located reproducible evidence.** The report,
   design and paper quote sigma 43/118/241 s, raw z-RMS 1.00/1.00/1.03 and
   1,000–1,338 transits. These numbers are absent from the committed Sprint 2
   summary/receipts, and no matching simulation script or output was located
   in `scripts/` or `results/sprint2/`. The C022 reproduce commands do not
   reproduce this control. Archive the actual command, synthetic specification,
   seed, source hash and result, or remove/qualify these assertions. Even a
   successful finite control would support “no detected bias in those cases,”
   not “no algorithmic bias.” Likewise, the single shape stress test demonstrates
   sensitivity; it does not bound all real systematic shape errors (paper 3.4).

7. **Retain candidate time-coordinate qualification.** The roster calculation
   deliberately treats UTC/MJD bounds numerically as BJD_TDB without conversion.
   Event `EPIC246851721b|S98|DRD432` is only 8.8007 minutes beyond the numerical
   first-whole-day anchor, within the script's stated approximately nine-minute
   coordinate uncertainty. One-day sector-calendar margins do not resolve that
   start cutoff. This is not evidence of a pre-publication event (DRD was
   public the previous day); it prevents calling the declared whole-day boundary
   exact. Resolve with the documented astronomical conversion or an explicitly
   conservative boundary rule before freezing.

8. **Reconcile stale draft notes and the brief's precision.** Article section 5
   says the configuration still names t015v3c; it currently names unqualified
   t015v3. The section's sensitivity list also describes the obsolete primary
   convention. The guide's sections 9/10/12 retain resolved disputes about
   absent C022–C027 ledger rows, an absent handoff, M1 b around 10 versus 191,
   the 3,748 versus 3,416/2,230 matched denominators and raw versus corrected
   sigma ratios. These are different denominators/conventions or already-fixed
   text, not present contradictions. The brief says the interval [0.908,0.947]
   “fell short” of 0.93; the original criterion failed because its *lower bound*
   was below 0.93. The interval straddles the floor.

9. **Do not describe finite checks as exhaustive.** C024's “at every phase”
   exceeds 44 finite randomized trials; say “all 44 trials at each tested
   offset.” The report/paper's “only such case among 3,946 timings” supports
   “one identified case” unless an exhaustive, forecast-independent diagnostic
   is documented. Article language that the pipeline is “accurate for most
   planets” or “calibrated” for the post-hoc group should be replaced by the
   actual conditional calibration summaries, after product-selection repair.

## Source and chronology verification

The concatenated `sprint2_outcomes.py` plus `t015_timing_pipeline.py` source
hash is
`4b5c9602a29b3f00079d465ab5657d64bbba460292950abbfa709b3ba3522809`
at `2c39f0a`, `9375b3c` and `d54142e`. Confirmation and replication run
receipts match its prefix. The confirmation design/source and selected frame
are in `2c39f0a` (committed 05:25:24 UTC); the replication design/selection
are in `9375b3c` (06:03:32 UTC). Outcome records are committed subsequently.
This verifies version order and identical frozen timing source. Download logs
lack timestamps and receipts lack run start/end times; Git alone does not
independently prove “before any download.”

The development receipt instead records `t015v3@dc5d2b8+66a91f709666`.
The script did not exist in `dc5d2b8`; that HEAD labels a dirty, uncommitted
source state. The exact source corresponding to 66a91f709666 is not recoverable
from the examined commits. Therefore the report's claim that 4b5c9602a29b is
in “every run receipt” is false. This does not show a material change in the
timing algorithm, but the development source snapshot remains unverified.

The replication design explicitly discloses prior real-transit R5 contact with
82 hosts. “Never-sampled” means previously unreached injection-frame hosts;
it does not mean untouched host photometry. Frozen source plus separate
injection estimands are the stated justification. Preserve that disclosure
in the article and brief rather than calling these wholly unseen stars.

Across dev/confirmation/replication product tables and the I1 table, 990
distinct filenames have internally consistent recorded raw hashes; there are
no conflicting hashes for the same filename. Raw FITS bytes were not rehashed.
The difference from the 996-file access scan is not reconciled by its aggregate
listing hash, because it does not retain the per-file listing. Do not infer
that the six additional files are violations.

## Claim-to-table trace

| Claim | Checks against original compact tables | Status for reuse |
|---|---|---|
| C022 | `dev/summary.json` gives original production t015v3 z-RMS 0.944 and interval [0.884,1.005], ledger/run/product counts and removal controls. Exact run-source snapshot differs from frozen rule; white-noise controls not located. | Recalculate production summaries; qualify/archive missing control. |
| C023 | `estimand_negative_controls.json`: maximum absolute mean bias 0.007; nominal 90% interval coverage ranges 0.853–0.927 over the recorded five synthetic scenarios. | Correctly labelled simulation; finite simulation coverage, not general estimator proof. |
| C024 | `identification_summary.json`: 44/44 at ±0.4%, 18/44 at each ±0.6%; displaced-transit timed counts 93,85,13,1,0 at 30,50,70,90,120 min. | Finite development cases; conditional recovery and hour-scale selection, not arbitrary-forecast-error proof. |
| C025 | Original confirm/confirm2 summaries and exploratory JSON supply the quoted original values and timed-count split. | Production selection is under repair; original qualification and sparse-host explanation must be reconciled. |
| C026 | Outcome table decompresses to hash `99bb6d5d43ac0d69b6533d08aea4505c2b4d45e918c88d474fa23bff32cbe133`; 4,615 attempts = 3,946 timed + 470 coverage + 116 identification + 83 edge. Convention JSON matches quoted matched M2 contrasts and their inconclusive decisions. | Remeasurement arithmetic verified. Sign/decision gate only; nearest-epoch mapping and unresolved source lineage remain. |
| C027 | 184 planets/175 hosts, 156 core/28 extension, 3,399 distinct planet-epoch pairs; independent inventory reconstruction identical. All candidate forecast parameter hashes and values agree with t015v3 candidate file; 400 host-refit sets. | Metadata/draft package verified; no outcome qualification or protocol freeze. |

All 3,399 candidate rows have `C2_candidate` and use the recorded rounded WLS
correlation from `covariance_completeness.csv`. The source reconstruction
assumes each DRC/DRD timing release is the corresponding fitted input set;
period agreement within 3 published sigmas is a consistency screen, not proof
of the issued joint covariance. The audit reproduced each forecast variance
from the published marginal errors, cycle and recorded correlation. Future
event cycles are fixed from the issued DRD ephemeris; they are unique in this
manifest. This establishes predicted identities, not independent matching of
a later physical transit to a cycle. The development pipeline's nearest-cycle
mapping remains a separate known limitation.

## Products and attribution

The three products carry claim IDs and consistently label the final evaluation
as absent. Most headline original values trace to the tables listed above;
the exceptions and overstated interpretations are itemised here. C022–C027
lack an explicit evidence commit in their ledger rows; add `d54142e` for the
preserved original package and a separate repair commit for amended evidence.

No PDF/DOCX/page-image render of the brief was located. Its Markdown source
alone does not verify the required maximum of two A4 pages. Render the final
reconciled version at declared page size/margins/fonts and inspect both pages
before claiming this requirement is met.

Article contributions name Claude Opus 5.5, Claude Sonnet 5.5, Codex models
gpt-6 and gpt-5.6-luna, and GPT-6 Pro ideation. The public correspondence
contains the Codex model labels and Claude's statement that a Sonnet 5.5
subagent drafted the three products; the freeze commits credit Claude Opus
5.5. Thus the model names are traceable to the project record, though the
Sonnet attribution is a collaboration statement rather than a runtime receipt.
The article correctly states that per-task attribution between the two Codex
models is unresolved. The brief names only the drafting Sonnet version and
points to the article for remaining roles; avoid upgrading inferred task-level
attribution into a verified runtime fact.

No publication-readiness, historical universal non-access or qualified outcome
rule is certified by this provenance audit.
