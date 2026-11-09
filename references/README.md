# References and the literature evidence record

This directory contains a **curated starter bibliography**, checked on
4 November 2026. It supports the initial research framework. It is not a
systematic review, a complete exoplanet-timing bibliography, or evidence that a
proposed extension has never been attempted.

## Files and their roles

| File | Purpose |
|---|---|
| `literature_evidence.json` | The verification ledger: bibliographic identity, material inspected, supported claims, limitations and questions requiring further reading |
| `references.bib` | BibTeX version of the curated literature records (17 seed records, 8 added under D070 from registered DOI metadata), suitable for a manuscript or reference-manager import |
| `references.csl.json` | CSL JSON version using the same stable citation identifiers |
| `../docs/literature_review.md` | Narrative synthesis, nearest prior work and a proposed reading sequence |

The source articles and release documentation remain the scientific authorities.
The evidence ledger is authoritative for **what this repository seed checked**.
A citation's presence in the BibTeX or CSL file does not mean that its complete
methods, appendices or data have been assessed. Several records explicitly have
abstract-only access depth.

No abstracts, full papers or third-party article PDFs are redistributed in this
bibliography. DOI links and available manuscript links are recorded instead.

## Import and refresh

Import `references.bib` into the reference manager used for the project, or use
`references.csl.json` directly in a compatible manuscript workflow. The stable
keys, such as `Kokori2026ExoClockIV` and `Brook2000PVA`, match the evidence ledger.
Keep those identifiers consistent when integrating the bibliography with Zotero
and the repository's Markdown manuscript.

Before preparing a submission:

1. Retrieve current verified publisher/DOI metadata for each cited work.
2. Compare the imported record with the paper, including title, publication
   year, journal, article identifier and author list.
3. Replace abbreviated author lists with complete verified lists.
4. Preserve the local citation key or update all manuscript citations together.
5. Record substantive corrections and any deeper source reading in
   `literature_evidence.json`, then keep the BibTeX and CSL versions aligned.

A metadata refresh is not a replacement for reading the source. If a newly read
paper changes the novelty assessment, update `docs/novelty_gate.md` and the
research protocol as well as its bibliography entry.

## Deliberately abbreviated author lists

Some multi-author papers have only their verified leading authors in this seed.
The evidence ledger marks these with `authors_truncated: true`.

- **BibTeX:** these records end their author field with `and others`, explicitly
  signalling an incomplete list.
- **CSL JSON:** the available leading authors are retained, and `note` explicitly
  states that the list is abbreviated. CSL consumers do not all render that
  note, so a generated bibliography can otherwise appear complete. Refresh these
  records before using a rendered author list in a paper.

Do not invent missing names, reorder authors from memory, or treat the current
leading-author subset as the complete author list. The completeness flag refers
to the seed record, not to the source publication.

## Date and identifier conventions

The `year`/`issued` value follows the conventional journal citation. Separate
online and issue dates, where checked, are retained in the evidence ledger and
bibliographic notes. These can differ substantially: ExoClock I has a 2022
journal citation and a 2021 online date; the ORBYTS paper has a 2021 journal
citation and a 2020 online date.

An arXiv submission date is **not automatically a public announcement timestamp**.
Neither a bibliographic year nor a current DOI resolution establishes when an
exact forecast artifact became usable. Operational issue dates belong in the
forecast-provenance records, supported by release or archive evidence.

For broad BibTeX/CSL compatibility, article or abstract identifiers are placed in
the `pages`/`page` field when a conventional page range does not apply. The
corresponding note identifies this convention; these values are not article
lengths. The Lissauer et al. item is explicitly a **conference abstract**, not a
full refereed research article. Missing DOIs are omitted rather than invented.

**Identity trap:** do not attach arXiv `2503.19290` to Kaye & Aigrain (2025).
That identifier belongs to an unrelated paper. The verified identity for Kaye &
Aigrain is DOI `10.1093/mnras/staf334`.

## Priority for the next literature pass

Start with ExoClock IV Section V.1/Table 5 and its released implementation, then
the older DRB/DRC releases. The direct retrospective benchmark in that paper
precludes a claim that this project is the first such evaluation. Search its
citing literature for the specific proposed additions: forecast issue-date
reconstruction, horizon-conditioned calibration, planet-balanced evaluation,
proper scoring and chronological recalibration. Record affirmative evidence
and unresolved questions; an unsuccessful keyword search does not establish
novelty.
