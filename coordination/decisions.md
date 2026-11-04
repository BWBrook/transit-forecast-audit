# Decision log

Record substantive choices and the evidence that changed them. This is a working
scientific record; a `proposed` item is not a frozen preregistration.

| ID | Date | Decision / rationale | Status |
|---|---|---|---|
| D001 | 2026-11-04 | Start with exoplanet transit forecast reliability, reflecting Barry's experience in retrospective model evaluation. | User choice |
| D002 | 2026-11-04 | Treat ExoClock IV Table 5 as mandatory prior work and a reproduction target. The broad validation idea already exists. | Adopted |
| D003 | 2026-11-04 | Separate reproduction R, issued-artifact evaluation A and chronological refits B. | Adopted |
| D004 | 2026-11-04 | Investigate DRB forecasts and later TESS outcomes first; add DRC after the first provenance chain works. | Proposed operational starting point |
| D005 | 2026-11-04 | First paper emphasises horizon-dependent calibration/precision and one earlier-trained correction. Scheduling optimisation is ancillary. | Proposed scope |
| D006 | 2026-11-04 | Use full covariance, explicit time conventions, independent observation lineage and historical availability. Unknowns stay unknown. | Adopted |
| D007 | 2026-11-04 | Use a small Python/NumPy core; permit R as an independent implementation or later analysis layer. | Seed implementation choice |
| D008 | 2026-11-04 | Use equal-planet, then equal-origin/event summaries and host-cluster uncertainty for the main proposal; retain measurement-weighted reproduction separately. | Proposed analysis |
| D009 | 2026-11-04 | Defer final cohort, lead-time bands and evaluation era until metadata feasibility, without inspecting the final outcomes. | Open scientific design |
| D010 | 2026-11-04 | Do not infer an unconditional missed-transit rate from a catalogue of successfully measured events. | Adopted estimand boundary |
| D011 | 2026-11-04 | Repository licence, final name and eventual collaborators remain owner choices; no external remote or contacts created. | Open nonblocking choices |

## New entry template

### D0XX — short title

- Date / responsible agent:
- Question:
- Evidence and source/analysis paths:
- Options considered:
- Decision and scope:
- Consequences for code, protocol and manuscript:
- Validation / independent review:
- Status: proposed / adopted / superseded, with replacement ID if relevant.
