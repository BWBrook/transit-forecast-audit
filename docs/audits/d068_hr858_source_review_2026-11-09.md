# Independent HR 858 b source and saved-timing check

Codex (GPT-6.1-sol), 9 November 2026, reviewing C048 and
`scripts/check_hr858b.py` from `9eade0b`. This check reads saved authorised
timings, diagnostics and calibration inputs, not raw FITS, headers or a new
measurement. It does not invoke Claude's HR 858 checker for the numerical
recomputation. Small numerical evidence is in
`results/final_review/d068_hr858/independent_check.json`.

## Findings and disposition

| Finding | Independent evidence | Disposition |
|---|---|---|
| Six-hour forecast departure and fitted local sequence | Centered least squares and direct joins of the 16 saved outcomes/forecasts reproduce all displayed values | Numerical claim supported, conditional on the saved identification and extraction |
| "Not a measurement artefact" | A coherent train and good product-shape diagnostics are internal checks; no independent extraction or identification was supplied | Replace categorical exclusion with evidence supporting a coherent ephemeris departure; do not claim a proven physical cause |
| "No development-era timing exists" | Saved development table has zero HR858b rows; the actual frozen calibration reconstruction has 206 planets and neither HR858b nor host HR858 | State absence from this development dataset/frozen training set, not absence of observations generally |
| Bonfanti identifier versus supplied link | arXiv 2411.14911 describes TOI-396; the supplied 2604.15035 link describes TOI-5624 | Retain correct identifier/DOI and correct the link; no hand-authored bibliography entry |
| Pre-origin TTV knowledge and DRD flag | Correct paper predates DRD; HR858b is absent from ExoClock IV's own 42 detected-TTV list and local transcription | Supported source contrast, not proof that ExoClock violated its flag's own detection criterion |

## Numerical reproduction

There are 16 distinct accepted event IDs and 16 distinct DRD epochs (643–665)
in sectors 105–107. Residuals range from −404.042271 to −355.199213 minutes,
mean −380.631221 minutes; forecast SDs range from 15.902667 to 16.435730
minutes. A centered, unweighted straight-line fit gives a local period of
3.58394976646 days and RMS residual 4.260779 minutes. The DRD catalogue row
gives period 3.585266 days. Product shape reduced chi-square values are 2.712,
1.203 and 1.461. These match Claude's reported rounding.

Calling the fitted sequence a local drift relative to the issued ephemeris
is justified. The sequence is approximately linear over this observation
span, so it does not itself demonstrate curvature, periodic TTVs, a dynamical
model or absence of a systematic identification/extraction error. Good shape
fits and agreement across sectors support the timing interpretation but do
not independently establish the identity of every event. The forecast miss
remains part of the fixed primary analysis; this check neither excludes it
nor changes its score.

The actual frozen calibration helper reconstructs 206 training planets.
Neither HR858b nor HR858 is present, corroborating zero saved HR858b
development rows. This supports non-participation in that calibration fit;
it does not assert that earlier timing observations do not exist elsewhere.

## Source identity and chronology

The correct source is [Bonfanti et al., arXiv:2411.14911](https://arxiv.org/abs/2411.14911),
with [full text v2](https://arxiv.org/html/2411.14911v2), journal reference
*Astronomy & Astrophysics* 693, A90 (2025),
[DOI 10.1051/0004-6361/202451300](https://doi.org/10.1051/0004-6361/202451300).
The arXiv record dates v1 to 22 November 2024 and v2 to 10 December 2024,
both before DRD's public-file availability on 18 November 2025.

Table 1 identifies TOI-396 as HR 858 and TIC 178155732, matching the saved
target. Section 5.2 and the conclusions report significant timing variations
for planets b and c. The dynamical simulations are distinct from the new
protected outcomes: the paper predicts possible timing excursions, rather
than measuring these sector-105–107 events. It therefore establishes
pre-origin knowledge of TTVs, not an independent validation of our new timings.

The supplied [arXiv:2604.15035v1 link](https://arxiv.org/html/2604.15035v1)
instead describes the TOI-5624 system; it cannot support HR 858 claims.

[ExoClock IV, Section III.2](https://arxiv.org/html/2511.14407v1#S3.SS2)
gives the 30 multi-planet and twelve other objects flagged by its own
periodogram criterion; HR858b/TOI-396b is absent. The frozen local
`data/fixtures/exoclock_ttv_flags.csv` likewise has 42 DRD entries and no
HR858b. The numeric DRD ephemeris is present in the source catalogue. This
supports "not flagged in DRD" under the project's origin-label definition,
while acknowledging that the DRD flag is a release-specific detection rule,
not necessarily a comprehensive inventory of all previously published TTVs.

The remaining publication reference workflow is Barry's Zotero import of the
verified identifier/DOI. This review adds source links and evidence, not a
manually constructed bibliography.
