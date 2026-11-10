# Journal-format cross-check: article v0.6.1 against ApJS norms

10 November 2026. This is the companion to `docs/journal_fit_2026-11-10.md`, the
AJ pass. Barry asked for it after the AJ pass suggested that our closest peers
publish in ApJS. A Claude Sonnet 5.5 subagent ran the comparison at the request
of Claude Opus 5.5. Claude Opus 5.5 checked the bibliographic claims on
Crossref; the corrections are below. No manuscript text was changed.

Caveats:

- Counts come from the arXiv versions of the papers (LaTeX source, or PDF text
  for Wang) and are approximate, to about ±10%. Published versions may differ.
- Journals, DOIs and reference counts come from Crossref.
- The AAS Data Guide could not be reached by script.

**Corrections from verification.**

- ExoClock IV is published: ApJS 283, 5 (11 February 2026),
  doi:10.3847/1538-4365/ae3238, confirmed on Crossref. The subagent wrongly
  found no record and left it out of the comparison. The bibliography entry is
  correct.
- Shan et al. 2023 is doi:10.3847/1538-4365/aca65f, which matches the
  bibliography. The other DOI, which had been supplied in the subagent's
  brief, does not resolve.

## Comparison (all ApJS)

| | Ours (v0.6.1) | Ivshina & Winn 2022 | Shan 2023 | Kokori II 2022 | Kokori III 2023 | Wang 2024 |
|---|---|---|---|---|---|---|
| DOI suffix (10.3847/1538-4365/…) | — | ac545b | aca65f | ac3a10 | ac9da4 | ad0847 |
| Sample | 151 planets | 382 | 262 screened, 31 studied | 180 | 450 | 326 |
| Abstract words | 571, structured | 160 | 214 | 246 | 269 (arXiv v1) | 179 |
| Main body words (excl. refs, appendices) | 13.7k | ~5.7k | ~6.1k | ~4.0k | ~5.4k | ~9k |
| Main-text figures / tables | 8 / 7 | 20 / 3 | 12 / 0 | 8 / 0 | 6 / 4 | 8 / 3 |
| Appendix | None | ~0.5k words, tables | ~10 pp of figure sets and a 31-row table | ~2k words and the full ephemeris table | ~50 of 77 pp | 3 short, ~13 pp |
| Large tables | Printed in text | Excerpt, machine-readable online, code on Zenodo | In appendix | OSF data DOI | OSF data DOI | Excerpt, machine-readable online, code online |
| Software/data back matter | Prose §6 | "Code" section | None | "Software and Data" | Same | None |
| AI statement | §7 | None | None | None | None | None |
| References | 27 | 526 | 115 | 425 | 655 | 202 |
| Sample-overview figure | No | Yes | No | Yes | Yes | No |
| Ensemble residual or O–C distribution | No | Yes (χ² distribution) | No | Yes (drift S/N against Gaussian) | Yes | No |
| Predicted-versus-observed figure | HR 858 b only | Per-planet residuals | Yes | Old versus new prediction | Old versus new prediction | Per-planet O–C |

Shan et al. is the closest peer. It compares TESS timings with archival
ephemeris predictions and finds offsets for 31 of 262 hot Jupiters; the
subagent reports a median offset of 17.8 min, not yet checked. Kokori II and
III show the ensemble drift-S/N-against-Gaussian figure, which addresses the
same question as our calibration analysis. Nabbie et al. 2026 (ApJS, a TESS TTV
catalogue of 76 systems) is weaker on topic and is worth citing only.

## AAS guidance specific to ApJS (journals.aas.org, 10 Nov 2026)

- **Scope.** "Extensive papers presenting significant new research",
  including catalogues and large data compilations. No length limit is given.
- **Abstract.** One paragraph of at most 250 words, as in AJ.
- **Large tables.** These must be machine-readable, in CDS/VizieR format.
- **Figures.** A figure may run to at most 3 printed pages; longer figure sets
  go online, with a truncated version in print.
- **Supporting data.** Encouraged, and reviewed on scientific grounds.
- **LLM use.** It must be acknowledged and cited.

## Departures from ApJS norms, ranked

1. **Product and frame.** Every peer delivers a reference product, such as
   timings or ephemerides, and leads with it.
   *Fix:* make the 151-planet table of forecasts against observed timings the
   deliverable, and lead with accuracy and the HR 858 b miss.
2. **Abstract** is 571 words against a 250-word limit.
   *Fix:* rewrite as one paragraph of about 220 words.
3. **No ensemble figure and no sample table.**
   *Fix:* add an O–C or standardised-residual distribution against a Gaussian,
   in Kokori style, and a sample table.
4. **References** number 27 against 115–655.
   *Fix:* cite the ExoClock, Ivshina & Winn, Shan and Wang lines of work, and
   the orbital-decay and TTV literature. Compare our results directly with
   Shan's 31 of 262 and with Kokori's drift scatter of twice the Gaussian
   expectation.
5. **Data release.**
   *Fix:* deposit per-planet forecasts, outcomes and timings with a DOI, and
   provide the main table as a machine-readable table.
6. **Main-text length** is 13.7k words against 4k–9k.
   *Fix:* move §4 and the post-review checks to appendices, which ApJS
   readily accepts.
7. **Style, claim IDs, back matter and title.** The fixes are as in the AJ
   note. Keep the AI statement.

## Changes from the AJ pass

- **Still hold:** the fixes to the abstract, references, claim IDs, back
  matter, title and style.
- **Change:**
  - Length is less severe, because ApJS readily accepts long appendices.
  - The sample table and ensemble figure become expected rather than useful.
  - "Software:" and "Facilities:" lines become low priority.
- **New:**
  - a data-release DOI and a machine-readable table;
  - an online figure set of per-planet O–C plots;
  - a direct comparison with Shan, Ivshina & Winn, and Kokori;
  - framing the paper around a reference product.

## Verdict

ApJS first is defensible, on one condition. If the paper releases the
per-planet forecast-against-outcome table as a reviewed data product, it fits
ApJS, and that journal's norms on appendices and data suit it better than
AJ's. If it stays a pure test of forecast calibration, an ApJS editor may judge
it out of scope, and AJ becomes the better first target. Neither pass favoured
a third journal. Barry decides.
