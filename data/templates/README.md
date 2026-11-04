# Ledger templates

The header-only CSVs are exchange contracts to develop during the pilot, not
claimed schemas of external archives. See `docs/data_contract.md`.

JSON arrays may occupy quoted CSV cells for list-valued fields. UTC timestamps
use ISO 8601; the normalised astronomical midpoint uses BJD_TDB days. Date-evidence
and time-system fields are required conceptually even when absent in the source;
leave unknowns explicit and route them to unresolved/sensitivity categories.

`pilot_candidate_queue.csv` is different: it contains ten named debugging
candidates from a verified paper table. All are explicitly unverified for this
study. The queue does not define the eventual population sample.
