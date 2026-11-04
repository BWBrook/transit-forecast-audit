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
| D011 | 2026-11-04 | Repository licence, final name and eventual collaborators remain owner choices; no external remote or contacts created. **Updated by Claude:** licence and remote are settled by Barry's 2026-11-02 Open-by-default policy (MIT code, CC BY-SA 4.0 content, public `BWBrook/transit-forecast-audit`). Final name and collaborators remain open. | Partly resolved |
| D012 | 2026-11-04 | Claude. Treat the OSF version-1 release files (hashes in `results/pilot_v1/source_manifest.csv`) as the issued forecast artifacts. Every file has a single OSF version, uploaded before the journal publication date. The OSF upload proves existence at that time, not public visibility, so the conservative issue date stays the journal date. arXiv v1 and the OSF upload are sensitivity anchors. | Adopted |
| D013 | 2026-11-04 | Claude. Availability anchors: DRB training end 2020-12-31, OSF 2021-10-27, arXiv 2021-10-26, journal 2022-02-09. DRC: 2021-12-31, OSF 2022-09-27, arXiv 2022-09-20, journal 2023-02-14. DRD: 2023-12-31, OSF 2025-11-17, arXiv 2025-11-18, journal 2026-02-11. Encoded in `scripts/reproduce_table5.py::ISSUE`. | Adopted |
| D014 | 2026-11-04 | Claude. Every TESS outcome dated 2022-01-01 to 2024-01-03 (the DRD mid-time file) is now **inspected development material**. It may train the recalibration but can never serve as untouched evaluation. | Adopted (invariant 10) |
| D015 | 2026-11-04 | Claude. Track R is complete. Table 5 reproduces exactly for DRB and DRC; DRD differs by one measurement at z≈1. The published definition excludes the 42 DRD TTV-flagged planets, which is screening on information that postdates the forecasts. The project's primary cohort rule therefore uses **flags known at origin only**: DRB's own non-linear flag, or the 19 DRC TTV planets. Hindsight flags appear only as a reproduction sensitivity. | Adopted (invariant 9) |
| D016 | 2026-11-04 | Claude. Covariance tier for ExoClock releases: *reconstructed, negligible*. The published T0 sits at the weighted pivot, giving abs(corr) ≤ 0.09 (≤ 0.05 except TOI-216). Report the sensitivity bound and do not impute zero silently. Evidence: `results/pilot_v1/covariance_completeness.csv`. | Adopted |
| D017 | 2026-11-04 | Claude. Primary extension is re-aimed to a **variance-components evaluation**: Var(O−C) = a²σ²_Tmid + b²σ²_pred(h) + τ²(h). *a* is identified without any forecast, from scatter within a TESS visit; *b* and τ are fitted on the 2022–2023 development era. The reason is that for DRC the forecast contributes a median 13% of σ²_O−C, and the TESS σ alone are about 7–11% too small, so Table 5 coverage confounds measurement and forecast calibration. Replaces the single-multiplier proposal in `configs/pilot_provisional.json` once confirmed by independent review. | Proposed; needs Codex review |
| D018 | 2026-11-04 | Claude. Proposed untouched era: DRD as issued (OSF 2025-11-17) against TESS transits from 2025-11-19 onward, which are in no ExoClock release and have not been inspected. These would be measured by a pre-specified pipeline that is independent of the forecast. Freeze the protocol (T009) before any of these light curves is fitted. A secondary observation-cutoff hindcast era is 2024-01-04 to 2025-11-17 (after DRD's training cutoff but before its issue). | Proposed |
| D019 | 2026-11-04 | Claude. Primary summaries are planet-balanced with host-cluster bootstrap. Measurement-pooled results are reported only for reproduction. In the pilot the planet-balanced 3σ miss rate is about twice the pooled rate. | Adopted (confirms D008) |

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
