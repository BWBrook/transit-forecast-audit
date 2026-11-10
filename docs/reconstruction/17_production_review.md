# Step 3c production cross-check

Codex, 10 November 2026; T027 / D083. Reviewed production commit `05ae64f`
and handoff `cba6dbe`, thread 156/message 3186. These are reconstruction
drafts. The canonical article, brief, guide, bibliography, scrivmark and
earlier reconstruction stages remain unchanged. No raw light curves or FITS
headers were opened; sectors 74–97 remain closed.

## Result

The numerical production items pass independent checks. The PIT sign is
correct, Table 2 quantiles reproduce, all Table 3 cells agree with their
sources, and all eight proposed references match registered DOI metadata.
Several appendix descriptions and display labels needed corrections, now
applied to the drafts. Nothing changes the frozen result.

## PIT and Table 2

An independent calculation imports no project modules. It reconstructs grid
weights and integrates M2 adaptively, rather than using the scoring adapter's
384-node quadrature. Its maximum PIT differences are $4.5\times10^{-15}$ for
M0 and $1.4\times10^{-12}$ for M2. Every 95% coverage classification agrees
with the frozen scores.

With residual $r=t_{\rm reported}-t_{\rm forecast}$ and saved grid coordinate
$x=t_{\rm true}-t_{\rm reported}$, measurement error is $-x$. The correct
contribution is therefore $\Phi((r+x)/\sigma)$, as implemented. M2 mixes
variance by $\exp(sZ)$, not standard deviation by that factor.

| Planet-weighted quantity | M0 | M2 |
|---|---:|---:|
| Inside the central 95% interval | 0.90793650 | 0.97576199 |
| Below it (early) | 0.06421676 | 0.01963094 |
| Above it (late) | 0.02784674 | 0.00460706 |

HR 858 b contributes $1/151=0.00662252$ to each early share. The early excess
persists without it and among Gaussian-only timings. This rules out a grid
sign mistake as the explanation; it does not identify a physical or
measurement cause. The draft now labels this post-review diagnostic, with
the observation and acceptance assumptions needed for the uniform reference.
Claim C065 records its descriptive status.

| Absolute error, minutes | Median | 95th percentile | 99th percentile |
|---|---:|---:|---:|
| Events weighted equally | 1.114776 | 6.362338 | 17.860334 |
| Planets weighted equally | 1.314948 | 9.040780 | 18.741974 |

These are inverse weighted empirical CDF quantiles, without interpolation.
The convention matters: the pooled 99th percentile is 17.86 minutes, whereas
linear interpolation gives 17.61. Table 2 and Appendix B.6 now state the
convention. Evidence: [independent PIT check](../../results/reconstruction_review/pit_independent_check.json).

## Appendices

The per-criterion injection values in Table D1 reproduce the saved evidence;
all eight criteria pass in both samples. The following prose repairs avoid
changing the evidence's meaning:

- The 2,021/1,931 denominators are intended injections, not all exported rows.
  The complete ledgers also contain seven/three unmatched-window rows.
- The boundary exclusions are four core plus one extension event. The 3,399
  pre-exclusion opportunities become 3,103 + 291 = 3,394 final opportunities.
- A 2.5-point coverage distortion is not a third of a 5–7-point shortfall.
  The joint scale/bias example allows about 2.75 points. Both are now stated
  directly, without the erroneous ratio.
- The 30/50-minute displacement controls identified 43/44 and 42/44 trials.
  Their 93/93 and 85/93 timed-event counts are conditional on identification.
- DRC contains event mid-times, but lacks per-row first-availability times.
  The 53-second same-day file lag cannot establish availability at the exact
  forecast origin.
- Development intervals use 400 host-refit draws, not the final test's 2,000.
  Chronological M0 coverage rounds to 0.897, not 0.898.

The reported development score contrasts and intervals also reproduce.
Evidence: [appendix check](../../results/reconstruction_review/appendix_production_check.json).

## Figures and Table 3

All four main figures were inspected at full size, and all eight online PDF
pages were inspected. Figure 1 now labels the actual final calibration
window; Figure 2c identifies its two-block total; Figure 3 uses a neutral
uniform reference. The online panels now identify their bars as reported
68% timing half-widths, show dates clearly and display the forecast band for
the single-timing planet WASP-106 b on a local date axis. The final PDF has
151 panels and 2,185 timings, with no out-of-page text.

Table 3 has **36 columns**, not 35. Independent checks compare all 6,624
cells across 156 core and 28 extension planets, with zero mismatches. The
dictionary now distinguishes issued marginal errors from reconstructed
correlation, and correctly describes the existing but unverified duration
fields. Five zero-accepted core planets retain their null summaries.

The printed excerpt now uses the first ten core labels alphabetically. This
is an outcome-independent illustration of the format, not a claim of
representative sampling. The complete core and extension CSVs are unchanged.
Evidence: [Table 3 and bibliography check](../../results/reconstruction_review/table3_bib_check.json).

## References and execution wording

All eight drafted bibliography records parse through Pandoc and match live
Crossref metadata for title, year, volume/issue/pages where applicable, and
first author. The long collaboration author lists remain explicitly
abbreviated. The main bibliography is unchanged. Evidence:
[live DOI check](../../results/reconstruction_review/bib_crossref_live.json).

One wording issue from Claude's reconciliation remains scientifically worth
distinguishing: the path fault used no forecast errors or scores, but that
does not establish statistical independence from them. Non-Gaussian timing
shape triggered it. Section 2.6 now states the code-path fact. The accepted
execution remedy remains the complete-manifest rerun and exact preservation
of completed first-attempt outputs; the D066 acceptance is unchanged.

## Verification and handoff

- Table 3's two CSVs and both PIT outputs are byte-for-byte unchanged.
- Eleven protected product/planning artifacts retain their pre-review hashes.
- The native frozen manifest verifies without differences.
- `.venv/bin/python -m unittest discover -s tests -v`: 160 tests pass, one
  expected skip.
- Parent checks, final output hashes and PDF checks are recorded in
  [production receipt](../../results/reconstruction_review/production_check.json).

These checks complete the production cross-check. Claude should reconcile
the draft corrections, especially the execution wording, before Barry
describes step 4. No new study, access or release is proposed here.

Next: Claude — reconcile D083, then Barry describes step 4.
