# Seed validation record

**Date:** 2026-11-04. **Scope:** the delivered repository and synthetic numerical
foundation. No real-data forecast audit or ExoClock benchmark reproduction has
been performed.

## Numerical and workflow verification

Command from the repository root:

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```

The final seed suite contains **32 passing tests**. It checks analytical weighted
fit variance, full covariance propagation and recentering invariance, invalid or
missing covariance, independent measurement-error convolution, proper-score
conventions, repeated-event weighting, host resampling, historical publication
leakage, duplicate atomic exposures, explicit time-standard validation and a
deterministic end-to-end synthetic demonstration that refuses overwrite.

An independent reviewer found and repaired three classes of guard failure:
duplicate exposures inside a split, malformed lineage inputs, and invalid
covariance accepted under extremely unequal parameter scales. Details are in
`docs/scaffold_review.md`.

## Delivery verification

- JSON and CSV artifacts parse, and bibliography IDs agree across the evidence,
  BibTeX and CSL exports.
- Relative Markdown file links resolve within the delivered tree.
- The package installs locally without fetching dependencies in the validation
  environment, and the installed CLI runs its synthetic demonstration.
- The Git worktree is clean at delivery and `git fsck` reports no repository errors.
- The ZIP extracts into one project directory; the extracted Git repository and
  test suite pass their checks.

These checks establish that the seed is usable. They do not validate externally
hosted API responses, complete historical release schemas, real exposure
independence or the project's provisional claim to novelty. Those remain the
first research tasks.
