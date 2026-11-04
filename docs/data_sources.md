# Data sources, historical availability and provenance

**Status: preliminary reconnaissance, checked 4 November 2026.** Public sources support a credible pilot, but no real timing data have yet passed this project's eligibility checks. The live ExoClock JSON payload and OSF release files were not downloaded in this reconnaissance. Their field-level contents, hashes, file histories and complete covariance information remain to be checked. A source being publicly described is different from a particular historical file having been acquired and verified.

## 1. Recommended acquisition order

| Priority | Source | Role in this project | Present evidence and remaining work |
| --- | --- | --- | --- |
| 1 | ExoClock II / Data Release B (DRB) | Historical forecast cohort with the longest convenient follow-up | Version-specific paper tables are readable; OSF release is identified. Obtain original release files and reconcile the publication and preprint versions. |
| 2 | TESS products at MAST | Independently measured outcomes after forecast issuance | Archive and metadata documentation verified. Actual target/sector coverage and usable complete transits have not been queried. |
| 3 | ExoClock III / Data Release C (DRC) | Second historical forecast cohort | Paper and archived catalogue identified; machine-readable file retrieval and version history unresolved. |
| 4 | ExoClock IV / Data Release D (DRD) | Reproduce existing validation; obtain later measured timings; eventual recent-forecast cohort | Paper identifies observations through 2023 and public data products. Later-release processing and quality-selection require an explicit independence audit. |
| 5 | NASA Exoplanet Archive Planetary Systems (PS) | Match planet identities and locate publication-specific ephemerides | Official column definitions and TAP interface verified. Current rows are not, by themselves, historical archive snapshots. |
| 6 | ETD / VarAstro | Secondary ground-based outcomes and provenance cross-checks | Current portal and usage terms verified. Legacy ETD URLs have moved; individual records require time-standard and migration checks. |
| 7 | ExoClock live planet catalogue | Current cross-matching and feasibility triage | Documented JSON endpoint; mutable state, without a documented historical-issuance or covariance field. Do not use it as a past forecast. |

This order is a design recommendation. It is intended to get one auditable prediction–outcome pair working before building a large ingestion system.

## 2. Release ledger: observation cutoff is not forecast issuance

| Release | Observation / submission cutoff stated by the study | arXiv v1 submission date | Verified version-of-record publication date | Data deposit identified |
| --- | --- | --- | --- | --- |
| ExoClock I / DRA | Network observations submitted before 15 April 2020; see source for inclusion details | 2020-12-14 | 2021-08-11; journal issue is 2022 | [10.17605/OSF.IO/3W7HM](https://doi.org/10.17605/OSF.IO/3W7HM) |
| ExoClock II / DRB | Network submission cutoff 2020-12-31; audit individual literature inputs separately | 2021-10-26 | **2022-02-09** | [10.17605/OSF.IO/WNA5E](https://doi.org/10.17605/OSF.IO/WNA5E) |
| ExoClock III / DRC | Paper states light curves acquired and literature timings published by end 2021; reconcile each input's provenance | 2022-09-20 | **2023-02-14**; journal issue is March | [10.17605/OSF.IO/P298N](https://doi.org/10.17605/OSF.IO/P298N) |
| ExoClock IV / DRD | Light curves acquired and literature timings published by end 2023 | 2025-11-18 | **2026-02-11**; journal issue is March | [10.17605/OSF.IO/WPJTN](https://doi.org/10.17605/OSF.IO/WPJTN) |

Sources: version-specific arXiv records and the dates printed in the journal articles [D1–D7]. An official newsletter dated 2021-12-07 states that DRB is open [D8]. This provides a dated public-availability witness, not an exact original upload timestamp.

**Date interpretation rules proposed for the audit:**

1. Preserve the date type as well as the date. An arXiv *submission* timestamp is not an independently verified public-announcement timestamp. A journal issue month is not its online publication date.
2. The conservative first implementation can evaluate the exact journal-table version using the verified version-of-record date. Use a strict later calendar day when only day-resolution evidence exists.
3. A preprint-origin sensitivity analysis should use that exact version and verify when its numerical table was publicly available. Do not pair the earlier preprint date with a corrected later table.
4. For a DOI-linked OSF project, inspect file-version identifiers, timestamps and any release notes. A project DOI alone does not prove that the current file is unchanged since release.
5. Record the maximum acquisition date of the actual inputs as a separate quantity. An outcome is genuinely subsequent only if it is later than both the adopted forecast issuance and the training-data boundary.
6. A later measurement of an earlier transit is not a future event. It may be useful for replication or measurement comparison, but not as a prospective-from-issuance outcome.
7. A reconstructed model fitted today to old measurements is a separate experiment. Historical-operational reconstruction additionally requires evidence that those measurements were publicly available by the cutoff.

A useful distinction is therefore between **issued-forecast evaluation**, **availability-aware reconstruction**, and **observation-date-only hindcasting**. Keep their results separate.

## 3. What can be recovered from ExoClock?

The release papers describe observation products, fitted mid-times, ephemerides and supporting metadata. The DRB paper specifically describes links to contributing ExoClock/ETD observations and literature references [D2]. These are promising foundations for tracing inputs; their exact serialized schemas have not yet been inspected.

The ExoClock planet-information page documents this endpoint [D9]:

~~~text
https://www.exoclock.space/database/planets_json
~~~

It documents a dictionary keyed by planet, including:

| Documented key | Meaning relevant to this project |
| --- | --- |
| name | Planet label |
| t0_bjd_tdb | Reference mid-time in BJD_TDB |
| t0_unc | Reference mid-time uncertainty; confirm the serialized convention against the release documentation |
| period_days | Orbital period in days |
| period_unc | Period uncertainty; confirm serialized units |
| duration_hours | Transit duration in hours |
| total_observations, recent_observations | Current observing-history summaries |
| priority, current_oc_min | Current prioritisation and timing-deviation summaries |
| ra_j2000, dec_j2000 | Coordinates for identity checks |

The documentation states that its epochs have been converted to BJD_TDB, that an unspecified original time basis is assumed to be UTC, and that the larger asymmetric error is used [D9]. Preserve these transformations as provenance; an assumption in an upstream catalogue is not an independently verified clock standard.

**Not established:** a live-API history endpoint; per-value first-publication times; a covariance key; full posterior samples; stability of records across downloads. Those absences from the documented schema are reasons to inspect the release artifacts, not proof that no such information exists anywhere.

**Covariance acquisition plan.** Search release descriptions and fit products for Cov(T0, P), a correlation coefficient or joint posterior draws. If unavailable, label it missing. The papers' centring of the reference epoch near the weighted mean reduces correlation but does not establish that the covariance is exactly zero for every published fit. Recovering it by refitting old timings belongs to the reconstructed-model experiment, not silently to the issued-forecast experiment. Published-rounding effects should also be retained or examined explicitly.

**Fallbacks if OSF retrieval remains difficult:**

- Use a version-specific paper table for a very small manually checked pilot.
- Obtain the official machine-readable journal tables; the DRC and DRD articles identify them [D3, D4].
- DRC has an identified VizieR catalogue, **J/ApJS/265/4** [D10]. The catalogue landing page was accessible; its ReadMe and data files were not successfully retrieved here.
- The DRD arXiv abstract explicitly states that machine-readable Tables 7 and 8 are included in its TeX source [D7]. Fetch a pinned source version rather than an unversioned latest copy.
- Do not infer missing metadata from a newer release merely to make an old record pass validation.

## 4. NASA Exoplanet Archive: use coherent reference-specific rows

The PS table exposes publication-specific parameter sets; the composite table can combine parameter sources. For an ephemeris, keep period and reference mid-time from the same fitted solution. Preserve all matching PS rows during discovery rather than retaining only the current default [D11].

A proposed, **not yet executed**, TAP query is:

~~~sql
SELECT pl_name, hostname, tic_id, pl_refname, default_flag,
       pl_orbper, pl_orbpererr1, pl_orbpererr2,
       pl_tranmid, pl_tranmiderr1, pl_tranmiderr2,
       pl_tsystemref, pl_trandur, ttv_flag,
       pl_pubdate, releasedate, rowupdate
FROM ps
WHERE tran_flag = 1
  AND pl_orbper IS NOT NULL
  AND pl_tranmid IS NOT NULL
~~~

All field names above were checked against the official PS definitions [D11]. The official TAP documentation explains schema queries and synchronous retrieval [D12]. Check the live schema again before implementing an adapter.

Important semantics [D11]:

- **pl_pubdate:** publication date for the parameter reference.
- **releasedate:** date that parameter set was released by the NASA archive.
- **rowupdate:** most recent update of that row.
- **pl_tsystemref:** time reference frame/standard for the PS temporal parameters.
- **pl_tranmid_systemref:** a related field in PSCompPars; it is not a substitute field name in PS.
- **ttv_flag:** has a specified dynamical meaning; it is not a comprehensive historical list of every timing anomaly.

None of these dates alone proves what every value in a currently retrieved row looked like at a past date. Preserve the query, retrieval time and file hash, then inspect the cited original publication. Do not replace unknown historical flags with present-day classifications.

## 5. TESS / MAST: the preferred outcome source

Start with public calibrated light curves where possible; use pixel-level extraction only if necessary. Do not download the full mission. The MAST mission page and API documentation establish the access route [D13–D15].

Documented observation metadata include **obs_id**, **obsid**, **obs_collection**, **provenance_name**, **sequence_number**, **t_min**, **t_max**, **t_obs_release**, and **dataRights**. The three time fields are queried in MJD. Product records include **dataURI**, **productFilename**, **parent_obsid**, **prvversion**, and **productSubGroupDescription** [D14–D15].

For each acquired product retain:

- TIC identifier, coordinates, sector, camera/CCD if supplied, cadence and mission.
- Observation ID and exact product URI/filename.
- Acquisition interval, dataset-release metadata, processing version and header provenance.
- Download time, checksum and the archive query.
- Every exposure or cadence interval used to obtain a transit mid-time.
- Timing, flux and quality definitions from that exact product.

A current product may have been reprocessed after its original data release. The dataset release date is not automatically the first availability date of the exact current calibration. This matters particularly for availability-aware reconstruction of *training* data. Using a later reduction to measure a genuinely later outcome can be defensible, but its dependence on shared shape assumptions and timing priors still needs to be assessed.

The official TESS tutorials document BJD reference keywords and TDB time scale [D16]. Parse the FITS headers. A common representation is time relative to BJD 2457000, but do not add that offset to an Astropy Time object already converted to full JD. Do not add the barycentric correction twice. Preserve original representations alongside the normalised BJD_TDB values.

**Avoid duplicate evidence.** SPOC and another pipeline may process the same exposures. Multiple cadence products may overlap. Multiple filters can measure the same physical transit. Use an exposure-level provenance map and an event-level identity rather than treating filenames or catalogue rows as independent events.

## 6. ETD now lives within VarAstro

The official current ETD portal is:

~~~text
https://var.astro.cz/en/Home/ETD
~~~

The legacy var2.astro.cz/ETD address did not resolve in this reconnaissance. VarAstro explains that observations attach first to stars and are associated with planets through transit fitting [D17].

Individual records can contain a creation timestamp, observing interval, observer, instrument, time standard, fitted HJD mid-time, quality rating and legacy TRESCA identifier. One verified example is a HAT-P-32 observation [D18]. This is evidence of available provenance fields, not a guarantee of a stable bulk API or historical timestamps for all records.

Before use:

- Determine whether a creation timestamp records original submission, migration or a reanalysis.
- Retain the original time standard; HJD does not by itself specify UTC/TDB.
- Cross-match TRESCA IDs against ExoClock and published tables.
- Preserve the observer and original source for attribution.
- Separate independent observations from repeated fits of the same exposure series.

VarAstro explicitly permits scientific use with appropriate credit to the original paper or observer, and requests attribution to the portal [D19]. This does not remove the need to inspect the terms attached to other archives or specific contributed products.

## 7. Recommended provenance tables to implement

These are a proposed *research data contract*, not a claim about existing upstream schemas.

| Table | Minimal content |
| --- | --- |
| source_artifacts | artifact ID, source URL/DOI, exact version, retrieved_at_utc, SHA-256, date evidence, licence/attribution, parser version |
| forecasts | forecast ID, planet ID, artifact ID/row locator, issuance date and basis, model family, T0/P and uncertainties, covariance status/value, time basis, rounding precision, training boundary, original flags |
| timing_measurements | measurement ID, planet ID, event ID/epoch, mid-time and uncertainty, original and normalised time basis, source record, acquisition date, public-availability evidence, reduction method, quality decisions |
| exposure_lineage | parent exposure/cadence IDs, child product and measurement IDs, telescope/mission/campaign, overlap decisions |
| forecast_inputs | forecast ID linked to all known contributing measurement/exposure IDs, plus unresolved input summaries |
| eligibility | forecast–outcome pair, allowed experiment, checks, unresolved fields, exclusion code, reviewer and date |

Store missing values as missing. In particular, a missing covariance is not zero; an unknown first-availability date is not the observation date; and no observed transit is not a successful forecast.

## 8. Reuse and reproducibility

The seed repository contains methods, bibliographic metadata and synthetic examples. This reconnaissance did not establish the licence of every OSF file, and the seed does not redistribute whole downloaded catalogues. On acquisition, record product-level terms and required acknowledgements. Published article licences and separately deposited data licences should not be assumed identical.

For a publication, deposit a machine-readable forecast–outcome ledger and derived quantities to the extent permitted, together with retrieval scripts, exact source identifiers and hashes. Preserve enough provenance for another researcher to reconstruct exclusions, not just successful matches.

## Sources

- **D1.** ExoClock I, publication and data information: https://link.springer.com/article/10.1007/s10686-020-09696-3 ; preprint: https://arxiv.org/abs/2012.07478
- **D2.** ExoClock II, pinned preprint and release description: https://arxiv.org/html/2110.13863v1 ; journal publication-date evidence: https://orca.cardiff.ac.uk/id/eprint/159708/1/Kokori_2022_ApJS_258_40.pdf
- **D3.** ExoClock III, journal article (author-repository copy): https://oro.open.ac.uk/87494/1/pdf.pdf ; DOI: https://doi.org/10.3847/1538-4365/ac9da4
- **D4.** ExoClock IV, journal article (author-repository copy): https://orca.cardiff.ac.uk/id/eprint/184907/1/pdf.pdf ; DOI: https://doi.org/10.3847/1538-4365/ae3238
- **D5.** ExoClock II arXiv version history: https://arxiv.org/abs/2110.13863
- **D6.** ExoClock III arXiv version history: https://arxiv.org/abs/2209.09673
- **D7.** ExoClock IV arXiv version history and source-table note: https://arxiv.org/abs/2511.14407
- **D8.** Official ExoClock newsletter, 7 December 2021: https://www.exoclock.space/documents/Issue_22_Dec2021.pdf
- **D9.** Official ExoClock live-catalogue documentation: https://www.exoclock.space/database/planets
- **D10.** VizieR ExoClock III catalogue landing page: https://cdsarc.cds.unistra.fr/viz-bin/cat/J/ApJS/265/4
- **D11.** NASA Exoplanet Archive PS/PSCompPars field definitions: https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html
- **D12.** NASA Exoplanet Archive TAP documentation: https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html
- **D13.** TESS at MAST: https://archive.stsci.edu/missions-and-data/tess
- **D14.** MAST observation fields: https://mast.stsci.edu/api/v0/_c_a_o_mfields.html
- **D15.** MAST product fields: https://mast.stsci.edu/api/v0/_productsfields.html
- **D16.** Official TESS light-curve tutorial: https://heasarc.gsfc.nasa.gov/docs/tess/LightCurveFile-Object-Tutorial.html
- **D17.** Current ETD portal: https://var.astro.cz/en/Home/ETD
- **D18.** Example VarAstro observation record: https://var.astro.cz/en/Observations/91678?transid=10099
- **D19.** VarAstro data-use and attribution policy: https://var.astro.cz/en/Home/DataUsage

