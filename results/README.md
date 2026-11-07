# Results

Compact committed outputs, one directory per analysis. Everything here is
development evidence unless a file says otherwise: no final evaluation has been
run and no protocol is frozen. The claims ledger (`coordination/claims.md`)
indexes the evidence; `docs/agent_guide.md` maps each claim to its files.

| Directory | Contents |
|---|---|
| `seed_demo/`, `first_local_demo/` | Synthetic demonstrations of the numerical core. No astronomical content. |
| `pilot_v1/` | Pilot: Table 5 reproduction, covariance and noise reviews, mixture and chronological fits. |
| `sealed_inventory/` | Original geometric inventory, superseded by `sprint1/inventory/`. |
| `t015/`, `t015_corrected/`, `t015_review/`, `t015_validation/` | Timing-pipeline development, corrections, reviews and the 18-host validation. |
| `sprint1/` | Forecast experiment (M0-M3), availability, timing audit, inventory, precision; `handoff.json` is the entry point. |
| `outcomes/` | Interface outcome tables for rule `t015v3`. |
| `sprint2/` | Outcome rule development calibration, identification tests, confirmation and replication, convention comparison, candidate freeze package and figures. |

Use a unique directory per new run, with a configuration, source manifest, code
commit, environment capture and concise interpretation. Keep development and
final-evaluation outputs distinguishable, and do not overwrite the earlier run
that motivated a decision.
