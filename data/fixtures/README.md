# Small reference fixtures

## published_benchmark_targets.csv

This file transcribes **existing published aggregate results** for the DRB and DRC comparisons in:

Kokori et al. (2026), *ExoClock Project. IV. A Homogeneous Catalog of 620 Updated Exoplanet Ephemerides*, ApJS 283:5, Section 5.1 and Table 5. DOI: [10.3847/1538-4365/ae3238](https://doi.org/10.3847/1538-4365/ae3238).

Readable sources:

- [Published article, author-repository copy](https://orca.cardiff.ac.uk/id/eprint/184907/1/pdf.pdf), journal p.12, Table 5.
- [Pinned preprint](https://arxiv.org/html/2511.14407v1), Section V.1 and Table 5.

The values were checked against these sources on 4 November 2026.

**These are not results computed by this project, and they are not raw transit measurements.** The paper compares earlier ephemerides with TESS timings acquired after 2022-01-01. Its DRD and initial-ephemeris columns are deliberately not included in this two-row fixture.

### Field interpretation

- **release:** the older forecast release evaluated by the published comparison.
- **planets:** published number of planets in that comparison.
- **measurements:** published number of timing measurements.
- **within_1sigma_fraction** through **within_4sigma_fraction:** the four published success percentages divided by 100. They retain the precision of the printed percentages.
- **source_doi / source_section:** provenance for the transcribed numbers.
- **definition_status:** unresolved for both rows.

The unresolved status is intentional. The exact residual-sign/absolute-value convention, uncertainty propagation, event membership, measurement filtering and treatment of dependence must be established from the source methodology, data and, if necessary, implementation before calling a reproduction successful. The acquisition-date threshold is also not identical to an operational forecast-issuance threshold.

Do not infer exact counts of successful predictions by multiplying these rounded fractions by the denominators. Do not treat 1,585 or 3,604 timings as that many independent planets. Do not tune a new method to reproduce these four rounded percentages and call that an independent validation.

### Intended use

Use this fixture as a named target for **Track R: reproduction**. A completed reproduction should explain its inputs, event list, definitions and denominator. Only after that comparison should the project apply its separately defined Track A/B protocol.

The synthetic example outputs under results/seed_demo are a different type of artifact: software demonstrations generated from simulated observations. They must never be pooled with this published reference table or presented as new empirical findings.

## Other fixture policy

Any future fixture must state whether it is synthetic, hand-transcribed published data, or a small excerpt from an acquired archive. Retain source identifiers, licences, units and uncertainty conventions. A few factual table values do not grant permission to redistribute entire source articles or datasets.

