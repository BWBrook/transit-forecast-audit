# Reconstruction, Step 1a: working abstract

Working draft, 10 November 2026. Not for submission. Claude (Opus 5.5) wrote
the first draft. Codex reviewed it (`06`–`08`, thread 156), and Claude then
reconciled the two versions. The framing follows Barry's instruction in chat
that day: "the product is pitched as the main goal and the calibration test is
support". Numbers come from C010, C015, C043, C046, C050, C054, C062 and C063.
The choice of journal is deferred.

**Reconciliation note.** Codex found that the hypotheses in my first draft
were retrospective. The study's real prior hypotheses were written before
held-out access, in `bc85326:docs/project_brief.md` (8 November 2026). They
now replace mine, which is what Barry's method asks for. I accepted all of
Codex's numerical and scope corrections, listed in `06`. Two of its changes I
reversed: I put back the plain-language "why" and the statements of use,
which Barry's method requires, and kept them within what the evidence
supports.

**Why are you doing this?**
Observers book telescope time for transits from catalogue predictions and
their stated uncertainties. Earlier comparisons checked ephemerides against
later timings. None that we found scored an issued release's uncertainties
on data that had not been opened when the test was fixed.

**What are your aims or research questions?**
Core: measure how well one issued ExoClock release predicted later TESS
transit times, and provide the comparison as a reusable per-planet table.
Sub-aims: the four questions recorded beforehand, below.

**What hypotheses underpin them?** These were recorded before access, with
theory behind each. A linear ephemeris omits timing variations and some noise
sources, and its uncertainty assumes the input errors are right.
- *H1, conditional calibration.* If the model and input errors are right,
  measured times follow the issued forecast convolved with measurement error.
  No direction of departure was assumed.
- *H2, information span.* Planets with short or patchy histories may do worse
  than their stated precision implies.
- *H3, transferable calibration.* A correction learned from an earlier
  release's errors improves a proper score on a later one. This was the
  prespecified primary test.
- *H4, practical cost.* Windows based on formal uncertainty may contain fewer
  transits than intended. A missed-transit rate needs attempted-observation
  denominators.

**What did you do?**
Before opening later TESS data, we froze the cohort, forecasts, measurement
and acceptance rules, and the primary test. Searches used the catalogue
period, and acceptance required a match within a quarter period. We scored
2,185 accepted timings and independently re-timed the influential cases.

**What did you find?**
The pooled median absolute error was 1.1 min. Every accepted timing on 150 of
151 planets fell within 26.4 min. The combined 95% intervals covered about
91% of timings per planet. The correction was inconclusive. HR 858 b arrived
six hours early.

**What do these results mean?**
- *H1, departure found.* Coverage fell short of nominal (interval 87.8–93.4%),
  but only by minutes. The cause is unidentified.
- *H2, untested.* Development associations were weak and unstable (C010,
  C015), and the held-out data contain one gross miss.
- *H3, inconclusive.* The correction widened intervals 1.7-fold, with a score
  change of −0.12 [−1.84, +2.20].
- *H4, not measured.* Window containment depends on transit duration and
  scheduling, which we did not model. Recovering only 70% of intended
  transits shows why the denominator matters.

**What is it good for, and how does it generalise?**
For the planets tested, the predictions were good to minutes, and the table
shows where they were not. HR 858 b's features suggest a flag that future
releases could test. Freezing a published forecast and scoring it later suits
any prediction that states its uncertainty.

## Notes for the next steps

- **Where we stand on the long-standing question.** Are published
  uncertainties honest predictions of future error? It has been asked of
  weather, epidemiology, ecology (Brook et al. 2000) and ephemerides (Lissauer
  et al. 2020, 2024). Position our fixed, issued-release benchmark against
  ExoClock IV, Shan et al. and Agol et al. Claim only what our bounded search
  supports.
- **Shan et al. 2023.** They found 31 offset planets among 262 screened. Our
  cohorts, horizons and selection differ, so failure rates cannot be compared
  directly. The comparison is still worth a paragraph.
- **HR 858 b's features.** These are a hypothesis for future releases, not a
  finding.
