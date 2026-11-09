# v0.6 review: the two new references

Codex, 9 November 2026. Bounded primary-source check of the two references
added at `1d9a150`, including the claim at `manuscript/paper.md:42`.
No manuscript, bibliography, frozen file, photometry or header was changed.
No primary-source full text is stored in the repository.

## Identity and narrow claim

| Key | Registered identity verified | Disposition |
|---|---|---|
| `Lissauer2024KeplerPeriods` | DOI `10.3847/PSJ/ad0e6e`, PSJ 5(6), 152; 1 June 2024; all eight authors match the CSL entry in order | Citation identity and stated period-uncertainty/TTV claim supported |
| `Agol2024TRAPPIST1Forecast` | DOI `10.3847/2515-5172/ad8b46`, RNAAS 8(10), 274; 30 October 2024; all fifteen authors match the CSL entry in order | Citation identity and stated tens-of-minutes forecast-drift claim supported; specify planet h if tightening the sentence |

Registered metadata were read from the Crossref works API for
[Lissauer](https://api.crossref.org/works/10.3847/PSJ/ad0e6e) and
[Agol](https://api.crossref.org/works/10.3847/2515-5172/ad8b46).
Titles, dates, volumes, issues, article identifiers and DOI values match the
repository bibliography and CSL records.

Lissauer's abstract, Sections IV and V.1 were read beyond the snippet. They
explain why formal constant-period errors over the Kepler observing interval
can omit long-timescale TTV effects, with dynamical examples. This supports
the manuscript's bounded statement; it should not be promoted to an untouched
population forecast-validation experiment. [Primary text, Sections IV–V.1](https://arxiv.org/html/2311.00238v2#S4).

Agol's complete Introduction and Timing analysis were read. The prior
forecast's large divergence concerns TRAPPIST-1 h. The paper updates a dynamical
model with 23 JWST timings, scales forecast uncertainties by 3.14 using
leave-one-out prediction residuals, and reports five later July 2024 timings
within one forecast sigma. [Primary text, Section II](https://arxiv.org/html/2409.11620v1#S2).

## Material positioning correction

The Agol citation is currently used only for drift. Its uncertainty calibration
and later timing check are also relevant prior art. The "closest methods"
sentence immediately after it names other methods without acknowledging this
closer forecasting/calibration example. Add a short acknowledgment; do not
present uncertainty recalibration or later timing checks themselves as the
new contribution. Its small-system dynamical example does not reproduce this
study's multi-release population-transfer and planet/host aggregation design.

Suggested addition, to adapt to the paragraph:

> Agol et al. also recalibrated dynamical forecast uncertainties using
> leave-one-out timing predictions and checked several later observations.
> Our study tests transfer and aggregation across a catalogue population;
> it does not introduce forecast-uncertainty recalibration or later-time checks.

This is paraphrased review wording, not a quotation from the paper. The new
bibliography entries need no identity correction. The evidence ledger may
record the deeper access now achieved: Lissauer IV/V.1 and Agol II, rather
than abstract-only access. No broad literature screen was attempted.
