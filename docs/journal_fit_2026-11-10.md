# Journal-format cross-check: article v0.6.1 against AJ norms

10 November 2026. Requested by Barry during his presupervision read, as input to
the revision. Comparison run by a Claude Sonnet 5.5 subagent at the request of
Claude Opus 5.5; draft metrics re-verified by Claude Opus 5.5 against
`manuscript/paper.md` at `0a946a6`. No manuscript text was changed.

Caveats: counts for the comparison papers come from their arXiv versions
(word counts approximate, about ±10%); DOIs and reference counts come from
Crossref. Published versions were not checked for data-availability or AI
statements.

## Comparison papers (all AJ)

1. Thygesen, Rodriguez et al. 2024, "The K2 and TESS Synergy. III. Search and
   Rescue of the Lost Ephemeris for K2's First Planet", doi:10.3847/1538-3881/ad60bf
2. Im, Saidel, Knutson et al. 2025, "Kepler-1624b Has No Significant Transit
   Timing Variations", doi:10.3847/1538-3881/ae1464
3. Biswas, Jiang et al. 2026, "Revisiting the Orbital Dynamics of the Hot
   Jupiter WASP-12 b with New Transit Times", doi:10.3847/1538-3881/ae4c86
4. Biswas, Bisht, Jiang et al. 2024, "Probing the Possible Causes of the
   Transit Timing Variation for TrES-2b in TESS Era", doi:10.3847/1538-3881/ad6d66
5. Sonbas, Kaplan et al. 2025, "A Combined TESS and Ground-based Study of
   Transit Timing Variations in HAT-P-16, TOI-1516 and TOI-2046 Systems",
   doi:10.3847/1538-3881/ae0f19

| | Ours (v0.6.1) | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| Title | Descriptive, plus ~25-word findings subtitle | Series + target | Result as title | Gerund, target | Gerund, target | "A Combined … Study" |
| Abstract | 571 words, structured with bold run-in labels, leads with question and design | 208, one paragraph | 156, one paragraph, ends on result | 244, one paragraph | 267, one paragraph | 219, one paragraph |
| Body length (excl. refs) | 13,663 words; 29 pp. | ~9.8k | ~6.8k | ~11k | ~12k | ~10.4k |
| Figures / tables | 8 / 7 | 5 / 5 | 5 / 2 | 13 / 11 | 4 / 6 | 30 / 13 |
| Appendices | None | None | None | Yes (individual fits) | Yes | Yes |
| Software / data | Prose §6 | Software: and Facilities: lines, MAST DOIs | MAST DOIs | MAST DOI, machine-readable tables | MAST link | Software: line |
| AI statement | §7, named systems and roles | None | None | None | None | None |
| References | 27 | 98 | 70 | 109 | 158 | 59 |

All five comparison papers lead with observations: new or archival photometry,
transit fits, O–C or TTV analysis, then model comparison. Prose is plain "we",
with values given as value ± error and almost no bold run-in headings or body
lists.

## AAS author guidelines (journals.aas.org/manuscript-preparation, read 10 Nov 2026)

- Abstract: one paragraph, at most 250 words.
- Order: title page (running head ≤ 44 characters), abstract, text,
  acknowledgments, appendices, references.
- UAT keywords are collected at acceptance.
- Data behind figures can be archived (AAS Data Guide).
- Software is cited in a "Software:" line after the acknowledgments
  (AAS convention, not stated on that page).
- Any LLM used in preparing the manuscript must be acknowledged and cited
  (AAS policy, doi:10.3847/25c2cfeb.c3619710).

These rules are shared by AJ and ApJS, so the fixes below do not depend on
the choice between them.

## Incongruities, ranked by editor and referee impact

1. **Abstract is 571 words against a 250-word limit**, and structured.
   Fix: one paragraph of about 220 words leading with accuracy (median 1.11
   min; 150 of 151 planets within 26.4 min) and the HR 858 b six-hour miss,
   with the inconclusive frozen contrast in one sentence.
2. **Reference list is thin**: 27 against 59–158. Fix: cite the timing, TTV,
   orbital-decay and ephemeris-maintenance literature properly.
3. **Length and structure**: 13.7k words, with the seven-subsection
   development-evidence §4 after the headline results. Fix: keep the held-out
   evaluation in the main text; move §4 and most post-review checks to
   appendices.
4. **Frame**: the frozen design and inconclusive contrast lead. Fix: lead with
   accuracy and the HR 858 b miss; present the frozen test as how the result
   was earned.
5. **184 inline claim IDs.** Fix: strip them in the journal build; keep them in
   the repository version, brief and agent guide.
6. **Back matter.** Fix: add Software: and Facilities: lines; make data and AI
   statements unnumbered back matter (keep the AI statement in full, as AAS
   policy requires it); remove commit and decision IDs from the text.
7. **Title.** Fix: replace the subtitle with one sentence stating the result.
8. **Style.** Bold run-in headings, body lists and process language
   ("frozen", "post-unblinding") are rare in AJ. Fix: plain subsection
   headings and prose.
9. **Display items.** No residual figure for the whole sample and no sample
   table. Fix: add an ensemble residual (O–C in minutes) figure and a sample
   table, flagged machine-readable. The existing HR 858 b O–C figure stays.

## Journal fit

No AJ paper from 2023–2026 tests forecast calibration or freezes a test of
catalogue ephemerides; four of the five comparison papers each study one
system. The closest peers (Shan et al. 2023; Ivshina & Winn 2022; ExoClock
II–IV) are in ApJS. Claude's recommendation after this check: ApJS first,
AJ second. Barry decides.
