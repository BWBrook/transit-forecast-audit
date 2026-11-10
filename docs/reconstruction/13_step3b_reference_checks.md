# Step 3b reference checks

Checked by Codex on 10 November 2026 against `11_paragraph_abstracts.md` at
`660ff9e`. This is a source check, not a bibliography or manuscript edit.
Identities were checked against DOI-bearing publisher records and, where
available, Crossref metadata; the supporting abstract or relevant passage was
also read. The sentences below are proposed paraphrases, not source quotations.
No photometry, headers or protected sectors were accessed.

## Candidate sources

| Candidate and verified identity | Passage read and one sentence it supports | Need and limit |
|---|---|---|
| **JWST overview:** Jonathan P. Gardner et al. (2023), *The James Webb Space Telescope Mission*, **PASP 135, 068001**. DOI [10.1088/1538-3873/acd1b5](https://doi.org/10.1088/1538-3873/acd1b5); [author preprint](https://arxiv.org/abs/2304.04869). | [Published paper, §3.1.11](https://ntrs.nasa.gov/api/citations/20250006005/downloads/36_Gardner_2023_PASP_135_068001.pdf): “JWST time-series spectroscopy observes exoplanet transits with observing windows extending beyond the transit.” Its WASP-39b example has 8.23 hours of observations around a 2.8-hour transit. | **Optional I1 example.** Gardner is the correct first author; this is distinct from Rigby's commissioning-performance paper. It illustrates an observing window, not a general quantified scheduling cost or miss rate. |
| **Ariel:** Giovanna Tinetti et al. (2018), *A chemical survey of exoplanets with ARIEL*, **Experimental Astronomy 46, 135–209**. DOI [10.1007/s10686-018-9598-x](https://link.springer.com/article/10.1007/s10686-018-9598-x). | Publisher abstract and §1.1: “Ariel's atmospheric survey relies on transit/eclipse spectroscopy and planetary ephemerides.” The paper also includes phase-curve observations. | **Useful direct I1 motivation.** Do not broaden this to all atmospheric measurements being possible only during transit. One mission reference may suffice; both mission overviews are not required. |
| **TTV theory:** Eric Agol, Jason Steffen, Re'em Sari and Will Clarkson (2005), *On detecting terrestrial planets with timing of giant planet transits*, **MNRAS 359, 567–579**. DOI [10.1111/j.1365-2966.2005.08922.x](https://doi.org/10.1111/j.1365-2966.2005.08922.x); [primary abstract](https://arxiv.org/abs/astro-ph/0412032). | Abstract: “Planet–planet gravitational perturbations cause departures from strictly periodic transit times.” | **Useful foundational I3 attribution.** Supports the mechanism, not this study's drift magnitudes or a claim of independent forecast validation. |
| **TTV theory:** Matthew J. Holman and Norman W. Murray (2005), *The Use of Transit Timing to Detect Terrestrial-Mass Extrasolar Planets*, **Science 307, 1288–1291**. DOI [10.1126/science.1107822](https://doi.org/10.1126/science.1107822); [primary abstract](https://arxiv.org/abs/astro-ph/0412028). | Abstract: “Gravitational interactions with an additional planet can create measurable transit-timing variations.” | **Useful alongside Agol** to acknowledge the independent foundational contributions; not necessary to cite both repeatedly. The preprint has a slightly different title; use the journal title for its DOI. |
| **BLS:** G. Kovács, S. Zucker and T. Mazeh (2002), *A box-fitting algorithm in the search for periodic transits*, **A&A 391, 369–377**. DOI [10.1051/0004-6361:20020802](https://doi.org/10.1051/0004-6361:20020802); [primary abstract](https://arxiv.org/abs/astro-ph/0206099). | Abstract: “We use box-fitting least squares to search for periodic transit-shaped signals.” The algorithm fits a periodic two-level signal with a short lower-flux state. | **Include for M4 method attribution.** It does not establish our ±0.5% search range, phase implementation, quarter-period association rule or timing calibration; those require our methods and evidence. |
| **Ecological forecasting:** Michael C. Dietze et al. (2018), *Iterative near-term ecological forecasting: Needs, opportunities, and challenges*, **PNAS 115, 1424–1432**. DOI [10.1073/pnas.1710231115](https://doi.org/10.1073/pnas.1710231115). | [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5816139/), abstract, “Predictability and Forecast Uncertainty” and “Model Assessment and Improvement”: “Iterative ecological forecasting evaluates probabilistic predictions against observations using explicit model–data comparisons.” | **Optional I5/D7 context. Correct the proposed journal: PNAS, not Ecological Applications.** This 2018 synthesis does not establish early ecological priority; Brook (2000) is the existing historical example. |
| **Preregistration:** Brian A. Nosek, Charles R. Ebersole, Alexander C. DeHaven and David T. Mellor (2018), *The preregistration revolution*, **PNAS 115, 2600–2606**. DOI [10.1073/pnas.1708274114](https://doi.org/10.1073/pnas.1708274114). | [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC5856500/), abstract and “Preregistration Distinguishes Prediction and Postdiction”: “Committing to questions and analytic steps before knowing outcomes distinguishes prediction tests from post hoc exploration.” | **Optional M6 rationale.** The source does not verify our freeze, hashes, access decision or observational independence, and should not imply an external registry was used. Cite native receipts for those facts. |
| **Bootstrap:** A. C. Davison and D. V. Hinkley (1997), *Bootstrap Methods and their Application*, Cambridge University Press. Book DOI [10.1017/CBO9780511802843](https://doi.org/10.1017/CBO9780511802843). | Publisher description and [Chapter 8 summary](https://www.cambridge.org/core/books/abs/bootstrap-methods-and-their-application/complex-dependence/20B4EBEB97AEEB73BB141A1EAF2795EC): “Bootstrap resampling must respect the level at which observations repeat and the dependence between observations.” The chapter discusses resampling groups/blocks. | **Optional general M7 reference.** The accessible material does not verify our particular joint calibration/evaluation host resampling with refitting; specify that algorithm in the protocol. Full chapter access was gated. Use original book year **1997**, not its 2013 online date. |
| **AAS machine-readable guidance:** American Astronomical Society, [Data Guide](https://journals.aas.org/data-guide/), “Machine Readable Tables,” accessed 10 November 2026. **Website; no DOI verified for this page.** | Official guidance: “AAS machine-readable tables supply structured data with metadata describing each column's format, units and meaning.” | **Useful production link, usually unnecessary as a scientific reference in R9.** It sets a format; it does not demonstrate that our table exists or satisfies it. Do not borrow a DOI from a separately linked recommendations paper. |

## Existing keys and the I1 substitution

All **25 year-bearing citation keys** already proposed in `11` match entries in
`references/references.bib`; the eight new DOI-bearing works above do not yet
have entries. In particular:

- **`Ricker2015TESS` exists**; the shorter `Ricker2015` is not its key. Ricker et
  al., *Transiting Exoplanet Survey Satellite*, JATIS **1, 014003** (2015), DOI
  [10.1117/1.JATIS.1.1.014003](https://doi.org/10.1117/1.JATIS.1.1.014003).
  The [primary abstract](https://arxiv.org/abs/1406.0151) supports the TESS survey
  and two-minute target cadence. It does **not directly support I1's atmospheric
  observing-window/uncertainty claim**. Use it for TESS in M3; use the Ariel or
  JWST source for the mission example. The existing `Dragomir2020` is the
  ephemeris-maintenance source already proposed in I3; its key was checked here,
  but its full text was not re-reviewed in this bounded task.
- **`KayeAigrain2025` exists**: Laurel Kaye and Suzanne Aigrain, *Transit
  ephemerides and timing variations from Kepler and K2 to TESS*, MNRAS **538,
  2283–2310** (2025), DOI [10.1093/mnras/staf334](https://doi.org/10.1093/mnras/staf334).
  [Publisher paper §5.1](https://academic.oup.com/mnras/article/538/4/2283/8093570)
  explicitly propagates epoch–period covariance in future timing uncertainty;
  this directly supports I3/M2. Its updated ephemeris fits must not be presented
  as independent held-out forecast tests.

The main corrections are therefore the Dietze journal and the role assigned to
Ricker. Gardner's proposed identity is sound. New references can remain few:
BLS for method attribution, the TTV foundations for mechanism, and the mission
source that best motivates the paragraph. The remaining candidates add context
or production guidance rather than evidence for the numerical results.
