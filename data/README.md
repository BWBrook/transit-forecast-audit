# Data organisation

- `templates/`: header-only production ledgers plus a provisional pilot queue.
- `fixtures/`: small attributed published benchmark targets. These are not our
  computed results and are not individual transit measurements.
- `raw/`: future original acquired artifacts, kept immutable and outside normal
  Git tracking; document them in the source manifest.
- `derived/`: future normalised or analysed tables, reproducibly generated.

No real light curves, timing records or historical release files have been
downloaded into this seed. Synthetic demonstration outputs live under
`results/seed_demo/` and are identified as artificial in their contents.

See `docs/data_contract.md` for semantics before writing adapters.
