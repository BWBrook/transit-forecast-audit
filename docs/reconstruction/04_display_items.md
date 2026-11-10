# Reconstruction, Step 1d: display items

Working draft, 10 November 2026, by Claude (Opus 5.5). It serves the main
message in `03_main_message.md` and the ApJS norms in
`docs/journal_fit_apjs_2026-11-10.md`.

## Diagnosis of v0.6.1

The draft has 8 figures and 7 tables. Almost all of them show interval
scores, contrasts and sensitivities: the support, not the message. No figure
shows how large the timing errors actually were, and nothing shows the reader
what a forecast, a window and a miss look like.

## Proposed main text: 4 figures and 3 tables

| # | Item | Shows | Status |
|---|---|---|---|
| Fig. 1 | **Context schematic**, two panels. (a) One forecast: predicted time, 95% window and measured transit, with the error and a miss labelled. (b) Timeline: DRC issued (Sep 2022), development TESS data (2022–Jan 2024), sectors 74–97 never opened, DRD issued (18 Nov 2025), freeze, held-out TESS data. | What is tested, and why the test is out of sample | New |
| Fig. 2 | **Accuracy, the main message**, three panels. (a) Distribution of absolute timing error for all 2,185 transits, log minutes, with the median marked. (b) Each planet's worst error, ranked: 150 planets under 26.4 min, then HR 858 b at about 400 min. (c) DRC 2022 forecasts: error against years since issue, for 128 planets (development data). | Accurate to minutes; one exception; holds over four years | New, from saved event tables |
| Fig. 3 | **Calibration**, two panels. (a) Standardised residuals (error divided by combined forecast and measurement SD) against N(0,1), in the style of Kokori II and III. (b) Coverage against nominal probability for M0 and M2 (exists). | Intervals slightly narrow, by minutes; the correction overshoots | (a) new; (b) adapted |
| Fig. 4 | **The exception**, two panels. (a) HR 858 b, c and d O–C in sectors 105–107 (exists). (b) HR 858 b's catalogue inputs ending in 2020, the issued line and its forecast window, against the measured 2026 transits. | The miss is real, physical and foreshadowed | (a) exists; (b) new |
| Table 1 | **Sample and outcome flow**: 156 hosts, 3,103 predicted transits, observed, measured, accepted (2,185 on 151 planets). Merges the current Table 1 and the cohort text. | Who was tested; selection is visible | Adapted |
| Table 2 | **Headline numbers** in one place: error median, 95th and 99th percentiles and maximum; coverage under M0 and M2; width ratio; IS95 under M0 and M2; M2 − M0 with its joint interval. Event-weighted and planet-balanced columns. | Every number the abstract cites | Adapted from current Tables 2 and 3 |
| Table 3 | **The product**: per-planet table, about 10 rows printed, full version machine-readable online. Columns: planet; DRD epoch, period and SDs; number of accepted transits; median and maximum error; coverage; flags (new in DRD, input span, input scatter, TTV literature). | The deliverable, citable and reusable | New, from the benchmark (C053) |

The frozen M2 − M0 contrast appears as one line of Table 2 and one sentence of
text. It does not need its own figure.

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

Figure 1 is drawn. Figure 2, Figure 3a, Figure 4b and Table 3 are generated
from saved, frozen event tables, so no data are reopened. Generated items are
Codex's in the current split.
