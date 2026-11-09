# Current catalogue TTV metadata diagnostic

Retrieved on **9 November 2026 (Hobart)** after unblinding, independently of
scores and host influence. `labels.csv` covers the frozen 184-planet roster:
8 current archive flags and 176 current unflagged catalogue rows. These are
descriptive catalogue states; an unflagged row leaves physical TTV status
unknown. No label is a TTV discovery date, evidence of absence, or evidence
that knowledge arose after the forecast origin. The original cohort and DRD
origin flags remain unchanged.

The source is the NASA Exoplanet Archive [Planetary Systems table](https://doi.org/10.26133/NEA12),
restricted to current `default_flag=1` rows for the target planets. The
[official column definitions](https://exoplanetarchive.ipac.caltech.edu/docs/API_PS_columns.html)
describe `ttv_flag` as concerning timing variations attributed to another
planet; this is narrower than all timing anomalies. `rowupdate`, `pl_pubdate`,
`releasedate` and `pl_refname` describe the current default parameter set.
They are retained as context and are not references or dates specific to the
TTV flag. The live TAP schema confirms `ttv_flag`, not `pl_ttvflag`.

Cached pre-freeze archive metadata supplied 183 exact planet-name matches
after whitespace removal; it contains no TTV flag. One additional match,
`HD108236d` to `TOI-1233.01`, is documented by the archive's
[planet alias service](https://exoplanetarchive.ipac.caltech.edu/docs/sysaliases.html)
and preserved in `alias_HD108236d.json`. Host-only matching is prohibited.
Every target matched a current default row; missing or ambiguous matches and
missing flags would remain unknown.

Raw JSON responses, exact query/URL, retrieval timestamps and SHA-256 hashes
are preserved alongside `labels.csv`. `provenance.json` records input and
script hashes. Rebuild without network access using
`.venv/bin/python scripts/final_ttv_labels.py`; `--acquire` fetches only
missing saved metadata. Existing responses are verified and reused.

No explicit dataset licence was established from the inspected official
documentation; no repository licence is imputed to the third-party source.
These files retain a small factual metadata extract, not photometry or paper
text. Follow the archive's [acknowledgement and source-citation guidance](https://exoplanetarchive.ipac.caltech.edu/docs/acknowledge.html).

This diagnostic operationalises the declared dated later-state label with a
newly retrieved current catalogue flag. It is not a comprehensive literature
classification or a new primary exclusion rule.
