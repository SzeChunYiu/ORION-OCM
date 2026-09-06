# Iterator custody correction

Final successor: **112 controls passed**, zero skipped, including 58 donor controls.
This corrects one standalone independent-checker input contract. The checker now
snapshots a one-shot revoked iterable once before creating its kernel and gated seed.

The first donor commit is `89f4e33b574bf876db01b5e11f0a1a6a1065c542`.
Its source and [original controls packet](../exact-sparse-donor-controls-20260906/CORE.md)
remain recoverable and byte-bound. The candidate solve_checked already passed a
frozenset, so the earlier 111 passing candidate/consumer controls are unaffected.

- [Retained red](raw/iterator-red.log): one actual control failed because the checker
  consumed an iterator twice and refused a correct all-zero revoked-seed result.
- [Final controls](raw/iterator-final.log): the same full scoped suite, 112 passed.
- [Bindings](BINDINGS.json): exact final seven source files, parent commit and recipe.
- [Artifact inventory](ARTIFACTS.json): all successor packet bytes except itself.

Only the checker and its meaningful regression changed. No numerical solver,
method, baseline, production source, historical raw record or dependency changed.
No timing study, optimization measurement or scientific promotion was performed.
The final research API and resource boundaries remain those in the original API.md.
