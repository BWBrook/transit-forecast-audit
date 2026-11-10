# Reconstruction, Step 1d: display items

Working draft, 10 November 2026, by Claude (Opus 5.5). It serves the main
message in `03_main_message.md` and the ApJS norms in
`docs/journal_fit_apjs_2026-11-10.md`.

Codex's feasibility annotations (10 November) retain the provisional four-figure,
three-table plan. Detailed saved-file/column mappings are in
`07_displays_product_review.md`. Nothing is built at this stage.

## Diagnosis of v0.6.1

The draft has 8 figures and 7 tables. Almost all of them show interval
scores, contrasts and sensitivities: the support, not the message. No figure
shows how large the timing errors actually were, and nothing shows the reader
what a forecast, a window and a miss look like.

## Proposed main text: 4 figures and 3 tables

| # | Item | Shows | Status |
|---|---|---|---|
| Fig. 1 | **Context schematic**, two panels. (a) One forecast: predicted mid-time, its interval, and a measured mid-time with its own uncertainty; distinguish the forecast interval from the convolved scoring interval and a full observing window. (b) Separate observation and analyst-access lanes: DRC issue, development blocks, closed sectors 74–97, DRD issue (18 Nov 2025), subsequent TESS exposures, freeze (8 Nov 2026), then access to previously uninspected outcomes. | What is tested, and why it is out of sample for the analysts | New |
| Fig. 2 | **Accuracy, the main message**, three panels. (a) Absolute errors of 2,185 accepted timings, log minutes, with the pooled-event median marked; disclose weighting and handle any zero explicitly. (b) Each accepted planet's maximum error, ranked: 150 within 26.4 min, then HR 858 b at about 400 min; show unequal timing counts. (c) DRC errors against years since issue for 128 selected planets, in separated inspected development blocks reaching about 3.94 years. | Minute-scale agreement in the accepted sample; one exception | New, from saved event tables |
| Fig. 3 | **Calibration**, two panels. (a) Proposed standardised-residual plot: combined SD does not make non-Gaussian timings normal. Either label this a Gaussian-surrogate diagnostic or later calculate exact predictive PIT values from the saved likelihood grids, stating assumptions and planet weights. (b) Coverage against nominal probability for M0 and M2 (exists). | Conditional calibration of measured timings, not catalogue uncertainty alone | (a) new, diagnostic choice unresolved; (b) adapted |
| Fig. 4 | **The exception**, two panels. (a) HR 858 b, c and d O–C in sectors 105–107 (exists). (b) Its released input timings ending in 2020, the issued DRD line and its forecast-only interval, against 16 accepted 2026 timings; disclose 24 intended events and distinguish the convolved interval if also shown. | A coherent physical interpretation with antecedent warning features; no validated warning | (a) exists; (b) new from saved tables and released inputs |
| Table 1 | **Sample and outcome flow**: all 156 hosts and 3,103 intended opportunities, prediction-time cadence coverage, terminal statuses and 2,185 accepted timings on 151 planets. Show 2,181/2,369 coverage-qualified recoveries separately from four other accepted timings. | Who was tested; selection is visible | Adapted |
| Table 2 | **Headline numbers** in one place: error median, 95th and 99th percentiles and maximum; coverage under M0 and M2; width ratio; IS95 under M0 and M2; M2 − M0 with its joint interval. Event-weighted and planet-balanced columns. | Every number the abstract cites | Adapted from current Tables 2 and 3 |
| Table 3 | **The planned product**: about 10 rows printed, full version machine-readable. Retain all 156 primary planets, including five with no accepted timings, with statuses and null performance entries. Join issued epoch/period/errors, reconstructed covariance provenance, accepted counts, error summaries and coverage to release/input metadata. Historical TTV literature flags require dated sources; unsurveyed means unknown. Keep 28 extension planets separate. | A reference product with visible selection and source provenance | New curation and joins from C053 and existing ledgers; not yet released |

The frozen M2 − M0 contrast appears as one line of Table 2 and one sentence of
text. It does not need its own figure.

Its status as the prespecified primary test and its inconclusive result must
remain clear in the abstract, methods and headline table. Reordering the paper
does not retrospectively change that status. Table 2 must distinguish the
joint-refit primary interval from conditional secondary intervals, with
weighting and each definition of an error percentile made explicit.

## Appendices or supplement

- Loss-scale comparison (current Table 3 and its figure) and the sorted
  per-planet M2 − M0 figure.
- Primary contrast and influence diagnostic figure.
- Declared sensitivities (current Table 4) and the HR 858 b sector 105
  rescore.
- Independent timing checks and their adjudication (T017).
- Measurement qualification on injected transits (current Table 6 and its
  calibration-against-magnitude figure).
- Development evidence (current Tables 5 and 7, and the outcome-scale and
  convention figures).
- The warning-rule screen (T020), with the hindsight and ceiling results.
- Online figure set: O–C plots for all 151 planets.

## How many can the paper carry?

The main message is simple, so the main text should be short: about 6,000 to
8,000 words, with **4 figures and 3 tables**. A fifth figure is the ceiling.
The best candidate is the per-planet M2 − M0 figure, if referees want the
calibration test made visible. Beyond five, the support begins to outweigh
the finding. ApJS peers carry 6 to 20 figures, but they are catalogue papers
with many products to show. We have one product and one message.

## Work needed

Figure 1 is planned as a drawing. The other new displays are feasible from
saved outcomes, forecasts, likelihood grids, ledgers and already-downloaded
released inputs, without new photometry or headers. Table 3 additionally needs
metadata joins and source checks; C053 alone is not a finished catalogue.
Codex builds the agreed items later, after Barry supplies the next step.
