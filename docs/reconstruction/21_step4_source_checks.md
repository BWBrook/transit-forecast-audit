# Step 4 source and formatting check

Codex, 11 November 2026, against `6d9e27f`. The registered metadata and
source-file hashes are in
[`step4_source_check.json`](../../results/reconstruction_review/step4_source_check.json).
This audit reads public metadata, papers and saved code/configuration only;
no raw photometry or FITS headers were opened. Canonical products are unchanged.

## Existing additions pass

Step 4 adds **ten**, not eleven, DOI-bearing bibliography entries: three
science papers, one data collection and six software papers. Every title,
year, volume, issue and page field where applicable, DOI and first author
matches live registered metadata. Long author lists are explicitly abbreviated.
Three initial Crossref requests were rate-limited; smaller selected-field
queries succeeded. No metadata remains unverified.

| Draft citation | Source-level support |
|---|---|
| Edwards & Tinetti 2022 | The [published paper](https://discovery.ucl.ac.uk/id/eprint/10148955/1/Tinetti_Edwards_2022_AJ_164_15.pdf) describes Ariel's candidate targets and explicitly discusses ExoClock ephemeris follow-up in section 3, p. 13. |
| Yee et al. 2020 | The [primary paper](https://arxiv.org/abs/1911.09131) reports shortening transit intervals and evidence favouring orbital decay. It supports the noninteraction example of ephemeris drift. Its online date is 27 December 2019; the January 2020 issue year used in the bibliography is valid. |
| Vanderburg et al. 2019 | The [published paper](https://oro.open.ac.uk/66383/1/66383.pdf), abstract and introduction, reports the TESS discovery of three approximately twice-Earth-size planets around naked-eye HR 858. |
| MAST two-minute light curves | The [MAST collection](https://doi.org/10.17909/T9-NMC8-F686) explicitly covers all-sector two-minute light curves. It is the correct held-out data citation, distinct from the [FFI collection](https://doi.org/10.17909/t9-wpz1-8s54). |

The software references match the packages' preferred citation identities:
[NumPy](https://numpy.org/citing-numpy/),
[SciPy](https://scipy.org/citing-scipy/),
[Matplotlib](https://matplotlib.org/stable/users/project/citing.html), and
[Astropy](https://www.astropy.org/acknowledging.html). Astropy encourages all
three project papers; these citations do not imply that those historical
versions were the runtime versions. The frozen environment remains the
source for exact versions.

## Correct the data and acknowledgment descriptions

The data-availability sentence currently says development used FFI light
curves. That obscures the final calibration's SPOC-only scope. Use:

> The frozen calibration and held-out measurements used SPOC two-minute light
> curves; early development also used TESS-SPOC full-frame-image light curves.

The product distinction is explicit in `configs/candidate_freeze.json`,
including “SPOC 120-s PDCSAP only; no FFI fallback”. Keep each collection's
citation beside its own product description.

Replace the funding phrase “NASA Explorer Program” with **NASA's Science
Mission Directorate**, as specified in the
[NASA TESS acknowledgment instructions](https://heasarc.gsfc.nasa.gov/docs/tess/faq.html).
The official [MAST archive handbook](https://archive.stsci.edu/manual/chap1.html)
supports the existing STScI/AURA and NAS5-26555 statement; no change to that
contract number is proposed.

## UAT, facilities and software

All six ID/label pairs match the [official UAT vocabulary](https://raw.githubusercontent.com/astrothesaurus/UAT/master/UAT.json):
498 Exoplanets; 464 Ephemerides; 1709 Transit photometry; 1710 Transit timing
variation method; 1882 Astrostatistics; 205 Catalogs. Both TESS and MAST are
valid [AAS facility keywords](https://journals.aas.org/facility-keywords/).
The draft's Facilities and Software lines therefore use valid concepts.
At the journal build, place their macros after the acknowledgments, as the
[AASTeX guide](https://journals.aas.org/aastex-v7-author-guide/) specifies.
This is a formatting step, not a new approval gate.

The Software line omits three directly used packages. `Model` in
`scripts/t015_timing_pipeline.py`, called by `final_measure.py`, uses batman
for the transit model. Acquisition uses Lightkurve and astroquery. Add their
credits. No audit of every indirect dependency is needed.

tess-point is already identifiable from its [ASCL record](https://ascl.net/2003.001)
and the [project's citation entry](https://github.com/tessgi/tess-point).
It does not need to remain a placeholder awaiting Barry's import.
The following draft entries resolve these four credits. The two paper
entries are independently checked against registered DOI metadata; the two
ASCL entries follow their projects' preferred citations, with long author
lists explicitly abbreviated. Lightkurve's [citation instructions](https://lightkurve.github.io/lightkurve/about/citing.html)
prefer ASCL 1812.013; a version-specific DOI is optional.

```bibtex
@misc{Burke2020TESSPoint,
  author = {Burke, Christopher J. and Levine, Alan and Fausnaugh, Michael and others},
  title = {{TESS-Point: High precision TESS pointing tool}},
  howpublished = {Astrophysics Source Code Library},
  year = {2020},
  month = mar,
  archiveprefix = {ascl},
  eprint = {2003.001},
  url = {https://ascl.net/2003.001}
}

@article{Kreidberg2015Batman,
  author = {Kreidberg, Laura},
  title = {{batman: BAsic Transit Model cAlculatioN in Python}},
  journal = {Publications of the Astronomical Society of the Pacific},
  year = {2015},
  volume = {127},
  number = {957},
  pages = {1161--1165},
  doi = {10.1086/683602}
}

@article{Ginsburg2019Astroquery,
  author = {Ginsburg, Adam and Sip{\H{o}}cz, Brigitta M. and Brasseur, C. E. and others},
  title = {{astroquery: An Astronomical Web-querying Package in Python}},
  journal = {The Astronomical Journal},
  year = {2019},
  volume = {157},
  number = {3},
  pages = {98},
  doi = {10.3847/1538-3881/aafc33}
}

@misc{Lightkurve2018,
  author = {{Lightkurve Collaboration} and Cardoso, J. V. d. M. and Hedges, C. and others},
  title = {{Lightkurve: Kepler and TESS time series analysis in Python}},
  howpublished = {Astrophysics Source Code Library},
  year = {2018},
  month = dec,
  archiveprefix = {ascl},
  eprint = {1812.013},
  url = {https://ascl.net/1812.013}
}
```

No scientific reference in the ten-entry addition needs removal or a changed
identity. The required repairs concern product provenance, the funding
phrase and software-credit completion. The main bibliography stays unchanged.
