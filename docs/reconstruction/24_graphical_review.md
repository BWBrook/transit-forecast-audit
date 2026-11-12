# Graphical abstract and shortened brief: critique and repairs

Codex, 12 November 2026; T030 / D086. Source `72ea688`, figure/trim
`f5ae2a5`, thread 156/message 3254. The dot chart, log scale, blue cluster,
labelled vermilion outlier, icons and overall hierarchy work well. They are
retained. The revised [illustrated brief](22_brief.pdf) fits two A4 pages at
11-point body type; canonical products remain unchanged.

## Scientific corrections

| Finding | Evidence | Repair |
|---|---|---|
| “150 planets within 26 minutes” is false at that bound | Only 149 satisfy 26.0; GJ 1252 b reaches 26.299 minutes. All 150 non-HR 858 planets satisfy 26.4. | Derive the 26.4-minute label and count from C063 and check against Table 3. |
| “Every prediction scored” hides selection | 2,185/3,103 intended events were accepted, on 151/156 planets. | “Accepted times scored”; show both denominators and label the dots as accepted-timing maxima. |
| Generic 1–4-hour duration band looks like cohort data | Table 3 explicitly omits unverified durations. The band was an illustration, not a computed sample summary. | Remove it; use that space for accepted-sample counts. No duration data were opened or inferred. |
| Neighbour's delay uses a different reference | C050 compares planet c with a separate published ephemeris, not tested DRD. | Say “on a separate published timetable” in the figure and make the same distinction in the prose. |
| “91% of each planet's transits” misstates the weighting | Equal-planet coverage is 0.9079365; event-weighted coverage is 0.9194508. Individual planets range from 0% to 100%. | “Averaged over planets”; retain timing uncertainty in the definition. |
| Standalone figure omits the primary outcome | C043's widening-test interval spans benefit and harm. | Add a short inconclusive-score footer without another card. |

Independent reaggregation from accepted forecasts, outcomes and scores
reproduces the numbers. No numerical-data or primary-scoring defect was found.

The trim had also dropped conditions previously restored in D085. The brief
again says **main test**, accepted artificial transits on the tuning samples,
accepted-only accuracy, equal planet weighting, measured-midpoint targeting,
and one planet **listed in the tested edition**. The exploratory result
reflects limited recovery and unqualified multi-planet identification. The
chosen main message retains its exact wording and initial capital.

## Design and print

The original smallest SVG type printed at about 6.5 pt, slightly below the
reported 6.7 pt. The minimum is now 16 SVG units, about **7.7 pt at 170 mm**.
Axis and explanatory text use the darker secondary colour. Blue/vermilion
colours stay unchanged; position, size and explicit labelling also identify
the outlier, so the message does not depend on colour alone.

The graphical abstract occupies about 42% of one page's text height, close
to the requested half page. After restoring the qualifications, the roles
paragraph briefly spilled to page three. Cutting repeated context and method
prose restored two pages without reducing the 11-point body type. Both final
pages and the standalone graphic were inspected. Findings stay together and
no text is clipped or missing.

The main article's graphical caption is corrected; its body and appendices
are unchanged. There is no need to replace the successful chart form or add
an illustrative duration claim.

## Executable evidence and limits

The original script did not read the claims ledger and guarded only some
quantities. It now reads C021/C043/C048/C050/C063, checks counts, bound,
median, coverage, case direction/reference and primary verdict, and derives
the display labels. Its receipt binds the code, inputs, ledger and all three
SVG/PDF/PNG outputs. This guards the declared quantities; it is not a general
proof of every possible wording or layout change.

Three scratch input probes are rejected before writing any output: replacing
equal-planet coverage by event-weighted coverage; changing the median; and
reducing the bound to 26.0 while keeping a 150-planet claim. They are QA
mutations, not scientific results. The actual inputs remain unchanged.

Evidence: [science audit](../../results/reconstruction_review/graphical_science_check.json),
[design audit](../../results/reconstruction_review/graphical_design_check.json),
and [integrated receipt](../../results/reconstruction_review/graphical_check.json).
The final diff received another bounded scientific check. All 160 tests are
OK with one expected skip; the native frozen manifest verifies unchanged.
Canonical products, bibliography, chosen message and scientific data are
preserved. No raw photometry, FITS headers, fits, protected access or release;
sectors 74–97 remain closed.

Next: Barry — review the reconstructed article and illustrated brief.
