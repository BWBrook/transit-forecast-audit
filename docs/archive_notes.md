# Archive and Git notes

The ZIP expands into one directory, `transit-forecast-audit/`. It includes the
working files and an initialized local Git repository on `main`, with an initial
seed commit. No remote, credentials, active hooks or external services are
configured. The commit is labelled as assistant-created seed work rather than
attributed as a scientific result by Barry.

After extracting, run `git status` and `git log --oneline -1` inside the directory.
The initial worktree should be clean. Normal Git commands can then add a remote
and push to the repository you create.

If an extraction tool omits Git metadata, the working files remain usable: run
`git init -b main`, add the files and make your own initial commit. If you prefer
a fresh history, copy the working files into a new repository instead. Preserve
the source/date/protocol records even if you replace the seed commit history.

Generated environments, caches, large raw downloads and subsequent analysis
outputs are ignored by default. Small original benchmark fixtures and the seed's
synthetic demonstration are tracked deliberately. Add new research artifacts
according to their size, reproducibility and attribution requirements.

The archive was checked by extracting it into a separate directory, validating
the Git repository and running its test suite. See `VALIDATION.md` for the exact
verification scope. This checks the delivered package; it does not establish
that the planned real-data study has succeeded.
