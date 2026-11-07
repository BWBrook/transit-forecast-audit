# Replication confirmation of t015v3 (no Tmag multiplier)

**Claude (Opus 5.5), 7 November 2026. Prespecified after the first confirmation
and before any replication photometry was requested.** This amends the decision
rules of [sprint2_outcome_design.md](sprint2_outcome_design.md) §4. Nothing else
changes: the timing code is the code frozen at `2c39f0a`, with rule version
`t015v3@2c39f0a+4b5c9602a29b`. The criteria, estimands, bootstrap and seed are
unchanged as well.

## Why a replication, and why only one

The first confirmation used 120 prespecified hosts; 106 of them produced timed
injections (1,496 events). It failed the prespecified primary rule:

- **t015v3c fails.** It meets the z-RMS criterion: 1.053 [1.015, 1.091]. It
  misses coverage, with a lower bound of 0.922 against 0.93. It also misses the
  Tmag 13.5 endpoint, [1.06, 1.20] against 1.15. The multiplier fitted on the 45
  development hosts over-corrects: on new hosts, faint stars are not
  conservative. That verdict stands, and t015v3c is not ready.
- **t015v3 passes every criterion on the same data.** It was the prespecified
  secondary rule. z-RMS 0.985 [0.951, 1.017]; coverage 0.944, lower bound
  0.930; mean z +0.001 [−0.051, +0.053]; Tmag endpoints [0.97, 1.06] and
  [0.88, 1.00]; noise ratios 1.000 and 1.004.

The design said that t015v3 "cannot replace a failed t015v3c after the fact".
That remains true of this sample. A pass found by choosing among rules after
seeing the data is not a confirmation. The fixed rule t015v3 can, however, be
tested once on hosts that have never been sampled. A single test of a rule fixed
in advance keeps its error rate whatever motivated the test. Its evidence, and
not the first sample's, decides qualification.

There will be no further replication. If this one fails, the outcome pipeline is
not ready, or it is narrowed by the prespecified rules (§4 there). The two
confirmation samples are reported separately and never pooled for the decision.

## Sample

- **Frame.** The D039 frame hosts that neither D039 nor the first confirmation
  reached: 37, 36, 51 and 33 hosts in strata A to D, after the one host with no
  product.
- **Draw.** 30 per stratum in the existing SHA-256 rank order. Sectors come from
  the hash `t015v2:confirm2:<TIC>:<sector>`, with the same product rules as the
  first confirmation.
- **Recorded in** `results/sprint2/confirm2/selection.csv`: 120 hosts, 30 per stratum, all with SPOC 120 s and TESS-SPOC 200 s; 82 of them were in the R5 remeasurement.
- **Prior contact with these hosts.** Many of them are also in the development
  remeasurement (R5). The frozen rule timed their real transits for the
  forecast comparison, and nothing in the timing rule changed as a result.
  Injection calibration at other phases is a separate estimand. This contact is
  disclosed as a limitation; it is not used as an exclusion.

## Decision for this replication

- **Rule.** t015v3 on the production set, judged by the A2 criteria as amended
  in §4.
- **All criteria pass.** Then t015v3 is qualified for single-DRD-planet hosts
  with Tmag below 13.5, S56–S73, catalogue-period identification and PDCSAP
  photometry. Every stratum, recovery and control result is reported alongside.
- **Only a Tmag endpoint fails.** The population narrows as §4 specifies.
- **Pooled z-RMS, coverage or bias fails.** The rule is not ready.
- **Product types.** Each is assessed separately with the same rule.

```bash
uv run scripts/sprint2_confirm2.py select
uv run scripts/sprint2_confirm2.py run
.venv/bin/python scripts/sprint2_analysis.py analyse --sample confirm2
```
