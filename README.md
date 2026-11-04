# Transit Forecast Audit

**Research seed and inspected development pilot · 4 November 2026 · no held-out results**

A project for Barry W. Brook to evaluate the predictive reliability of exoplanet
transit ephemerides using historical forecasts and later independent timing
measurements. The methodological starting point is retrospective evaluation:
freeze the information available at an origin, make the prediction, and compare
it with subsequent observations across replicated systems.

## The central question

> For a historically defined population of transiting planets, how does the
> calibration and practical precision of issued transit forecasts change with
> forecast horizon, and can a simple correction learned from earlier forecast
> errors improve performance in a later, untouched evaluation period?

**Important literature finding:** this is not the first retrospective test of
transit predictions. ExoClock IV already compares older releases with later TESS
timings in Section 5.1 / Table 5. Start by reproducing that benchmark. The potential
contribution is a more explicitly specified, horizon-dependent, planet-balanced
evaluation of issued forecast distributions, with independently tested
recalibration if justified. Its novelty is **provisional**. See
[the literature review](docs/literature_review.md) and
[the novelty decision](docs/novelty_gate.md).

## Read these first

1. [START_HERE.md](START_HERE.md): exact first tasks for the two agents.
2. [Project brief](docs/project_brief.md): questions, hypotheses, scope and the
   connection to Brook et al. (2000).
3. [Literature review](docs/literature_review.md): the nearest studies and what
   they already establish.
4. [Data sources](docs/data_sources.md) and [pilot feasibility](docs/pilot_feasibility.md):
   where historical products and outcomes might be obtained, with access gaps.
5. [Evaluation protocol](docs/evaluation_protocol.md) and
   [statistical specification](docs/statistical_models.md): exact estimands,
   covariance, measurement uncertainty, scoring and temporal separation.
6. [AGENTS.md](AGENTS.md): shared scientific and repository working rules.

## What is ready

- A cited initial literature review and source-evidence records, with metadata
  that can be imported through BibTeX or CSL JSON.
- A proposed protocol, hypotheses, scope boundaries and a staged work plan.
- A source and data contract that preserves issue dates, availability dates,
  observational lineage and uncertainty conventions.
- A small Python package with covariance-aware linear ephemerides, chronological
  checks, proper scores and planet/host-level aggregation.
- Meaningful numerical and leakage tests and a reproducible **synthetic-only**
  demonstration.
- Shared agent instructions, a decision log, task board, manuscript outline and
  prompts for independent scientific criticism.
- A public repository with MIT code and CC BY-SA 4.0 project content.

## What the seed does not establish

**Update 2026-11-04 (pilot v1).** The DRB, DRC and DRD OSF release files have
been acquired with hashes. ExoClock IV Table 5 now reproduces exactly for DRB
and DRC, and DRD differs by one boundary measurement. The pilot is development
material and makes no population claim. See
[results/pilot_v1/README.md](results/pilot_v1/README.md) and decisions
D012–D019. Still open: exposure-level lineage and the prior used for the
outcome mid-times, an untouched evaluation era, and the citing-literature
sweep. The `seed_demo` outputs remain synthetic.

**Independent review, 2026-11-04:** a separate R implementation confirms DRB/DRC
from hash-verified source files. The covariance and measurement-error claims
are now narrower: local excess dispersion is reproducible, but its cause is not
identified, and issued covariance remains missing. See
[the review](docs/independent_review.md),
[updated prior-art assessment](docs/literature_update_2026-11-04.md) and D020–D024.
The [claims ledger](coordination/claims.md) indexes the verified findings C001–C004.
The protocol remains unfrozen. Keep all TESS light curves after 2025-11-18
unopened until freeze.

**Second review, 2026-11-05:** independent REML supports a conditional outcome
scale near 1.087, and stable integration confirms broad between-planet forecast
heterogeneity. Coarse quadrature understated the number of posterior tail
classifications, and official schedule metadata invalidate the inventory's
already-observed interpretation. A shorter released training span is a promising
development predictor, pending chronological validation. See the
[tranche-2 review](docs/tranche2_independent_review.md),
[heavy-tail prior art](docs/literature_update_2026-11-05.md) and D030–D033.

**Timing-pipeline and chronological review, 2026-11-05:** the four-host timing
pilot demonstrates conditional recovery, but overlapping known-shape injections
do not establish a transferable outcome scale. The production mixture now has
continuous tail summaries and host-bootstrap uncertainty. Training span gives
a small chronological point gain but becomes severely overconfident in some
training resamples; it is not selected for the final analysis. See the
[third-turn review](docs/third_turn_review_2026-11-05.md). No protocol freeze or
protected-outcome inspection has occurred.

The numerical package is a foundation, not a complete ingestion or light-curve
reduction pipeline. It does not convert HJD/UTC to BJD/TDB, recover omitted
covariances, establish exposure lineage automatically, fit nonlinear orbital
models, or estimate a production recalibration rule. See
[implementation status](docs/implementation_status.md).

## Run locally

Requires Python 3.11+ and NumPy. From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m unittest discover -s tests -v
python -m transit_audit demo --output results/my_first_demo
```

On Windows, activate with `.venv\Scripts\Activate.ps1` in PowerShell. If NumPy is
already available and you prefer not to install the package, on a POSIX shell:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
PYTHONPATH=src python -m transit_audit demo --output results/my_first_demo
```

Each demonstration needs a new output directory so that results are not silently
overwritten. The included [synthetic summary](results/seed_demo/synthetic_summary.json)
is a worked software example, not an astronomical result.

## The three analyses

| Track | Information used | Interpretation |
|---|---|---|
| R: reproduction | Match the published benchmark's definition exactly | Can we reproduce the earlier result? |
| A: issued forecasts | An immutable forecast artifact available before the later event | How reliable were forecasts that could actually have been used? |
| B: chronological refits | Only measurements demonstrably available at each cutoff | How would a standardised modelling procedure have performed? |

Do not merge these tracks or rename a present-day refit as a historical forecast.
Track B is an explicitly labelled fallback/secondary analysis if Track A lacks
enough auditable distributional information.

## Repository map

| Location | Purpose |
|---|---|
| `docs/` | Scientific background, design, data contract, feasibility and handoff |
| `references/` | Evidence records and bibliography; no bundled article PDFs |
| `configs/` | Provisional research configuration; not a frozen analysis plan |
| `data/templates/` | Empty ledger templates for real source records |
| `data/fixtures/` | Clearly labelled small reference/validation fixtures |
| `src/transit_audit/` | Executable numerical foundation |
| `tests/` | Scientific invariants, chronology and workflow checks |
| `scripts/` | Reproducible utility commands and environment capture |
| `results/seed_demo/` | Small synthetic example outputs |
| `coordination/` | Work queue, decisions and agent handoffs |
| `manuscript/` | An outline with questions and planned figures; no invented results |

## Getting started with Git

After extracting the archive, `cd transit-forecast-audit` and inspect:

```bash
git status
git log --oneline -1
```

The active repository uses `main` and
[BWBrook/transit-forecast-audit](https://github.com/BWBrook/transit-forecast-audit)
as `origin`. [Archive notes](docs/archive_notes.md) describe the original seed.

## Scientific ownership and citation

The project belongs to Barry's research workflow. Claude and Codex are tools for
analysis, implementation and criticism; their agreement does not validate a
scientific claim. Record evidence, derivations and reproducible checks. The
code is MIT-licensed and project text, figures and data are CC BY-SA 4.0;
third-party data retain their own terms. See `LICENSE` and `LICENSE-CONTENT`.

Seed prepared with OpenAI research/coding assistance on 2026-11-04. Every
astronomical conclusion, literature interpretation and source schema should be
revisited by the project agents before it enters a manuscript.
