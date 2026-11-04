# Initial literature review: the reliability of exoplanet transit forecasts

**Research status:** reconnaissance and protocol design; no empirical transit analysis has been performed for this repository. **Literature checked:** 4 November 2026. This is a focused initial review, not a systematic review or an established claim of novelty. Bibliographic identities, access depth and unresolved questions are recorded in [`references/literature_evidence.json`](../references/literature_evidence.json).

## 1. The central finding that changes the project

**A retrospective coverage test already exists in ExoClock IV.** The project should begin by reproducing and extending it. A claim to the first retrospective validation of exoplanet ephemerides would be incorrect.

Kokori et al. (2026; preprint 2025), *ExoClock Project IV*, Section V.1 and Table 5, compare older ExoClock releases with TESS timings acquired after 1 January 2022. For DRC, the table contains 308 planets and 3,604 measurements; its reported success rates are 62.32% at one sigma and 98.34% at three sigma. The authors explicitly label the DRD comparison optimistic because those observations contributed to that release. These are the closest published results to the proposed project. The section was inspected in the [arXiv v1 full text](https://arxiv.org/html/2511.14407v1#S5.SS1); check it against the [version of record](https://doi.org/10.3847/1538-4365/ae3238) before finalising a reproduction.

This finding strengthens the project's starting point while narrowing its possible contribution. It provides a benchmark, relevant public products, and an identifiable analysis to extend. The first research decision is whether a more explicit forecast-evaluation design yields a materially new answer.

**Proposed central question:**

> For a prespecified population of known transiting planets, how does the calibration and practical precision of historical ephemeris forecasts vary with forecast horizon, and can a simple recalibration learned from earlier forecast errors improve predictions in a later, untouched evaluation period?

The scope of “historical” must be declared. Testing an actually issued ephemeris and refitting a model using observations before a historical cutoff answer different questions. Both can be scientifically sound; they should remain separate analysis tracks.

## 2. The connection to Brook et al. (2000)

Brook et al., *Predictive accuracy of population viability analysis in conservation biology*, used 21 long ecological time series, estimating parameters from their first halves and evaluating predictions against their second halves. The paper assessed predictive performance across systems and software implementations. Its relevant inheritance here is temporal separation between fitting and evaluation, replication across systems, and an explicit test of predictive claims. [Nature 404:385–387; DOI:10.1038/35006050](https://www.nature.com/articles/35006050).

This analogy is methodological. Transit times have a simple periodic baseline, while their measurements and departures from periodicity introduce different uncertainties. A literal half-record split is not automatically the most useful design: the horizon, observing cadence and information actually available at a decision date should determine the split. As in a replicated ecological study, thousands of measurements on a few systems do not create thousands of independent systems.

## 3. Four forms of evidence that must remain distinct

| Evidence | What it establishes | Role in this project |
|---|---|---|
| Fit residuals using all observations | Compatibility with data already used | Diagnostics and debugging; not a future-performance estimate |
| Old and new ephemerides projected to the same future date | How an update changes the prediction | Useful context; the new prediction is not the future observation |
| Earlier-data fit tested on later observations | Temporal generalisation of a specified procedure | Retrospective hindcasting track, with every fit restricted to its cutoff |
| A versioned, publicly issued ephemeris tested on observations acquired afterwards | Performance of a forecast product an observer could have used | Operational historical-forecast track |

The distinction affects the scientific interpretation, not just the terminology. An ephemeris released in September can legitimately be tested against observations from the preceding March if those observations were withheld from its fit. That is an out-of-sample test, but it is not a forecast that a member of the public could have used to schedule the March event. Later reprocessing of the old photometry creates another distinction between reconstructing an old algorithm and evaluating the original published product.

Every proposed test should therefore name the forecast issue date, last training observation, information-availability cutoff, target observation date, and source version. Unknown dates should stay unknown until evidence resolves them.

## 4. The closest astronomical literature

### 4.1 ExoClock I: infrastructure, selection and the definition of success

Kokori et al., *ExoClock project: an open platform for monitoring the ephemerides of Ariel targets with contributions from the public*, appeared online in 2021 and in *Experimental Astronomy* 53:547–588 in 2022. It establishes the network's observational and validation practices and a timing-precision target expressed as a fraction of transit duration. [DOI:10.1007/s10686-020-09696-3](https://doi.org/10.1007/s10686-020-09696-3).

**Use here:** understand what the forecast product was designed to do and which targets receive attention. Its use of “cross validation” includes broader data-validation practices; the phrase alone is not evidence of a chronological forecast benchmark. Historical versions of prioritisation rules matter for any later investigation of monitoring allocation. A new allocation algorithm belongs after the initial forecast audit, unless it becomes essential to its interpretation.

### 4.2 ExoClock II: population-level uncertainty problems were already recognised

Kokori et al. (2022), *ExoClock Project II*, provides 180 updated ephemerides. Section 6.3 compares old and new predictions for 2028 and finds differences broader than expected from the quoted Gaussian uncertainties. The fitting procedure also enlarges uncertainties to account for excess scatter. [ApJS 258:40; DOI:10.3847/1538-4365/ac3a10](https://doi.org/10.3847/1538-4365/ac3a10); [full preprint](https://arxiv.org/pdf/2110.13863).

**Use here:** underestimation of timing uncertainty and error inflation are established issues. Recommending a scale multiplier by itself is not a new method. The useful extension would evaluate a multiplier learned only from earlier forecast errors, against later observations, alongside its cost in interval width. Comparisons between two updated fits must also account for their shared inputs if interpreted probabilistically.

### 4.3 ExoClock III: homogeneous processing and incomplete temporal coverage

Kokori et al. (2023), *ExoClock Project III*, integrates 18,170 timing points for 450 planets. Its light-curve and literature cutoffs are the end of 2021. It explicitly discusses remaining biases and the importance of the years covered by observations. [ApJS 265:4; DOI:10.3847/1538-4365/ac9da4](https://doi.org/10.3847/1538-4365/ac9da4); [full preprint](https://arxiv.org/pdf/2209.09673).

**Use here:** a long baseline alone is an incomplete description of the training information. Observation count, distribution through time, gaps and source composition are reasonable prespecified candidate predictors of forecast failure. Quality cuts in a catalogue are also part of its selection process. Reproducing a release and constructing a forecast-evaluation cohort can require different inclusion rules, which must be documented separately.

### 4.4 ExoClock IV: the mandatory reproduction target

The retrospective exercise described in Section 1 is the project's principal novelty constraint. Its released observation and ephemeris products are the natural first resources for a replication. [Kokori et al. 2026, DOI:10.3847/1538-4365/ae3238](https://doi.org/10.3847/1538-4365/ae3238).

**Questions for a full reproduction:** verify how its success statistic is implemented, including absolute versus signed residuals and the construction of the residual uncertainty; identify the exact timing records and duplicated events; recover the forecast versions; determine the weighting implicit in the pooled percentages; and reproduce the denominators before attempting additional models. An unexplained discrepancy is first a reproduction problem, not evidence of an error in the original study.

### 4.5 Shan et al. (2023): archival predictions versus later TESS timings

Shan et al., *TESS Timings of 31 Hot Jupiters with Ephemeris Uncertainties*, compares archival predictions with TESS timings for 262 hot Jupiters and then focuses on 31 discrepant systems. Its methods identify an August 2021 NASA Archive extraction and report consistency statistics for the wider sample. [ApJS 264:37; DOI:10.3847/1538-4365/aca65f](https://doi.org/10.3847/1538-4365/aca65f); [full preprint v2](https://arxiv.org/html/2111.06678v2).

**Use here:** testing earlier ephemerides against newer timings is established. The selected discrepant subset is useful for stress testing and physical interpretation, but cannot alone estimate a population failure rate. Reconstruct each source ephemeris's inputs rather than assuming that every row extracted from an archive at a particular date predates the observation used to test it. Do not transfer proposed period-decay interpretations into the seed as settled facts.

### 4.6 Ivshina & Winn (2022): a major timing compilation

Ivshina and Winn, *TESS Transit Timing of Hundreds of Hot Jupiters*, provides 8,667 measurements for 382 systems, together with updated ephemerides and code. [ApJS 259:62; DOI:10.3847/1538-4365/ac545b](https://doi.org/10.3847/1538-4365/ac545b); [article repository](https://transit-timing.github.io/).

**Use here:** a valuable alternate timing compilation and a cross-check on provenance. Different catalogues can include the same photons or literature measurements; agreement between catalogues does not establish independent validation. The abstract and author-hosted product description were checked for this review; full method and record-level assessment remain required before defining a new benchmark with these data.

### 4.7 Kaye & Aigrain (2025): long-baseline updates and selection through detection

Kaye and Aigrain, *Transit ephemerides and timing variations from Kepler and K2 to TESS*, revisits 111 planets. Section 5.1 explicitly includes epoch–period covariance in forecast-uncertainty propagation. Its processing excludes some undetected, incomplete or discrepant transit measurements. [MNRAS 538:2283–2310; DOI:10.1093/mnras/staf334](https://doi.org/10.1093/mnras/staf334).

**Use here:** covariance-aware propagation is an established astronomical method. Separately, a timing catalogue designed to identify well-measured transits may not represent all forecast failures. Outcome-dependent exclusions require review before reusing the sample for calibration. An undetected transit can arise from inadequate sensitivity or gaps as well as a bad prediction; it cannot simply be counted as a timing failure. Selected full-text method sections and the abstract were inspected; no exhaustive assessment of the paper's validation design is claimed.

### 4.8 Mallonn et al. (2019): deliberately difficult ephemerides

Mallonn et al., *Ephemeris refinement of 21 hot Jupiter exoplanets with high timing uncertainties*, combines new professional and amateur observations for a sample selected for uncertain timings. Some observed deviations are hours long. [A&A 622:A81; DOI:10.1051/0004-6361/201834194](https://doi.org/10.1051/0004-6361/201834194).

**Use here:** demonstrates the practical consequences of poor predictions and offers potential historical case studies. Its selection is suitable for a challenge set, not a prevalence estimate. If revisiting its predictions for later years, preserve the original sample and issued forecast information rather than selecting only systems subsequently known to be problematic.

### 4.9 Edwards et al. (2021): useful follow-up, selected cohort

Edwards et al., *Original Research by Young Twinkle Students (ORBYTS): ephemeris refinement of transiting exoplanets*, studies eight planets chosen for large uncertainty or a lengthy gap since observation; seven fall outside earlier one-sigma timing uncertainties. The journal issue is 2021, while the publisher records online publication in May 2020. [MNRAS 504:5671–5684; DOI:10.1093/mnras/staa1245](https://doi.org/10.1093/mnras/staa1245).

**Use here:** another direct precedent for comparing predictions with new observations. Record online availability separately from bibliographic year. A forecast can be publicly available well before its volume's publication year, which affects retrospective cutoffs.

### 4.10 Dragomir et al. (2020): why forecast horizon matters

Dragomir et al., *Securing the Legacy of TESS through the Care and Maintenance of TESS Planet Ephemerides*, models ephemeris deterioration and follow-up strategies, with checks using real TESS candidates. Short observing baselines motivate continuing ephemeris maintenance. [AJ 159:219; DOI:10.3847/1538-3881/ab845d](https://doi.org/10.3847/1538-3881/ab845d); [preprint](https://arxiv.org/abs/1906.02197).

**Use here:** horizon and follow-up timing already have a physical and operational rationale. Separate calculated growth in formal uncertainty from empirically observed error growth. The project's new evidence would concern how predictive claims perform, conditional on the actual historical information, rather than merely re-deriving uncertainty accumulation.

### 4.11 Wang et al. (2024): model comparison and influential observations

Wang et al., *Long-term Variations in the Orbital Period of Hot Jupiters from Transit-timing Analysis Using TESS Survey Data*, analyses 326 systems and uses leave-one-out checks when evaluating candidate period changes. [ApJS 270:14; DOI:10.3847/1538-4365/ad0847](https://doi.org/10.3847/1538-4365/ad0847); [associated CDS record](https://cdsarc.cds.unistra.fr/viz-bin/ReadMe/J/ApJS/270/14?format=html&tex=true).

**Use here:** cross-validation is already used in transit-timing research. Influence analysis and future forecasting answer different questions. A quadratic model supported by fit statistics or deletion of an influential point need not outperform a linear model beyond the observation window. Any quadratic comparator should be selected and tuned without future timings.

## 5. Mathematical and physical foundations to read alongside the catalogues

**Deeg (2015), *Period, epoch, and prediction errors of ephemerides from continuous sets of timing measurements*.** Explains reference-epoch placement and prediction errors for periodic timings. Its simplifying assumptions should not be silently extended to irregular, heterogeneous observations. The lesson for implementation is to preserve full parameter covariance and test invariance when the reference epoch changes. [A&A 578:A17; DOI:10.1051/0004-6361/201425368](https://doi.org/10.1051/0004-6361/201425368).

**Eastman, Siverd & Gaudi (2010), *Achieving Better Than 1 Minute Accuracy in the Heliocentric and Barycentric Julian Dates*.** Establishes why a Julian date without an explicit time standard is insufficient for precision comparisons. [PASP 122:935–946; DOI:10.1086/655938](https://doi.org/10.1086/655938). This project should keep the original time representation, the conversion provenance and the standardised BJD_TDB value. Unresolvable time standards belong in an explicitly uncertain stratum, rather than receiving guessed corrections.

**Lissauer et al. (2020), *Perturbations, TTVs and the (Un)reliability of Ephemerides of Kepler Planets*.** This is a conference abstract, not a full journal analysis. It explains why a precisely estimated mean period over an observing window can still be an imperfect long-term predictor when dynamical variations occur on longer timescales. [AAS abstract 306.02](https://baas.aas.org/pub/2020n6i306p02/release/1). Use it as a route to the dynamical literature, not as quantitative evidence for an error rate.

**Gneiting & Raftery (2007), *Strictly Proper Scoring Rules, Prediction, and Estimation*.** Provides the statistical foundation for judging probability forecasts, including interval scores that account for width and misses. [JASA 102:359–378; DOI:10.1198/016214506000001437](https://doi.org/10.1198/016214506000001437). Higher coverage can be purchased with arbitrarily wide intervals, so coverage and practical concentration must be assessed together.

**Gneiting, Balabdaoui & Raftery (2007), *Probabilistic forecasts, calibration and sharpness*.** Supplies complementary calibration and distributional diagnostic concepts. [JRSS B 69:243–268; DOI:10.1111/j.1467-9868.2007.00587.x](https://doi.org/10.1111/j.1467-9868.2007.00587.x). The astronomical contribution would be a consequential application and empirical finding, not the invention of forecast scoring.

## 6. A chronology that agents must preserve

| Release | Verified data boundary | First arXiv submission date (not an issue timestamp) | Journal citation |
|---|---|---|---|
| ExoClock DRB / II | Network observations and submissions through end 2020; inspect other inputs individually | 26 October 2021 | Kokori et al. 2022 |
| ExoClock DRC / III | Light curves and literature timings through end 2021 | 20 September 2022 | Kokori et al. 2023 |
| ExoClock DRD / IV | Light curves and literature timings through end 2023 | 18 November 2025 | Kokori et al. 2026 |

These dates come from the respective [DRB](https://arxiv.org/abs/2110.13863), [DRC](https://arxiv.org/abs/2209.09673) and [DRD](https://arxiv.org/abs/2511.14407) submission histories. Submission may precede public announcement; an ephemeris may also have appeared earlier on the project website or OSF. Therefore these dates are provenance anchors, not automatically operational issue dates. Verify public announcement or artifact history for the strict issued-forecast track. The acquisition and publication dates of individual training records must also be distinguished.

**Implication:** some observations can be after a data cutoff but before a verified public issue date. The repository must retain enough metadata to identify those cases and classify the evaluation appropriately. A current, continuously updated web table cannot by itself reconstruct the historical forecast an observer saw.

## 7. Candidate contributions and the mandatory novelty gate

The following are **proposals**, not findings from the literature search:

1. **Horizon-specific reliability.** Estimate calibration and useful interval widths as functions of both time since issue and time since the last training observation. Use coarse prespecified strata before fitting flexible trends.
2. **An explicit population estimand.** Compare the result for a randomly selected eligible planet with the result for a randomly selected measured transit. A densely observed short-period planet receives very different influence under the two questions.
3. **Strictly chronological recalibration.** Fit a small number of scale or extra-variance terms to early forecast errors, freeze them, and evaluate a later era. Improvement must include a proper score or comparable width-versus-miss criterion.
4. **Operational consequences.** Translate forecasts into a clearly defined timing margin. Report the observed performance of that rule, conditional on the cohort and observation availability. Full-transit capture also depends on duration, baseline requirements, visibility and interruptions.
5. **A reusable historical benchmark.** Release forecast versions, evaluation-event identities and selection decisions so others can compare methods on the same problem without reconstructing provenance from scratch.

Before a novelty claim or large data acquisition, read the full versions of the closest papers and search their citing literature for these particular components. Record whether an apparent extension already exists, whether it changes the estimand enough to matter, and whether the available metadata support it. The broad search conducted here did not establish prior absence of proper scoring or horizon-specific calibration across astronomy.

Three viable outcomes of that gate are: a distinct empirical extension; a useful reproduction and benchmark with a narrower claim; or a decision to change the question before expensive analysis. Publication potential should be assessed from the result of this gate, not promised by the seed.

## 8. Recommended reading and execution order

1. **ExoClock IV Section V.1 and Table 5**, plus its data descriptions. Write an exact reproduction specification.
2. **ExoClock II and III methods and releases.** Trace the older ephemerides and their training membership.
3. **Deeg and Eastman et al.** Resolve epoch, covariance and timing-convention choices before computing residuals.
4. **Shan; Ivshina & Winn; Kaye & Aigrain.** Examine alternate timing products and whether their selection or extraction could truncate forecast errors.
5. **Gneiting & Raftery and Gneiting et al.** Freeze the evaluation target and scores before seeing the final test era.
6. **Mallonn, Edwards and Dragomir.** Check that the interpretation answers an observing problem, rather than producing a calibration statistic without practical meaning.

The first milestone is a small, traceable reproduction, not a large new catalogue. Once that works, choose one primary extension and reserve the more ambitious questions about nonlinear physical models and optimal telescope allocation for a later stage.
