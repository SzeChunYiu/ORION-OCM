# Sparse/extraction atom-view replay on main 179ad15

This result replays the source intent of PR #122 on
`179ad15d7bdab16d43e813b0eadb3eb62e075536` and qualifies the resulting source afresh.
Implementation commit: `1a7df95`.

Five read-only accesses use `KnowledgeSpace.atom_view`: sparse matrix construction,
sparse activation, reacting-subgraph extraction, bounded exact PCST, and greedy PCST.
The replay preserves the current-main files, including their trailing newlines.
No previous engineering receipt or branch-specific workflow is imported.

The hostile checks reject detached atom and edge maps in both navigation modes,
check exact activation on the fixture, and preserve revocation gating. The original
three hostiles failed against unchanged main before the five replacements.

- Targeted KSO/hostile controls: 70 passed in 46.36 seconds.
- Recorded engineering focused gate: 133 passed in 33.52 seconds.
- Recorded full gate: 1,147 passed in 273.27 seconds; no failures, errors, or skips.
- All twelve milestone wrappers verified the selected source-bound receipt.
- Execution host: billy-laptop; Python 3.11.14; `requirements-dev.lock` installed.

The immutable [execution receipt](provenance/engineering_revisions/runs/04199126326004a35c2d4de2288eff18dba1b538ed2580edf5e8983bf262b7a4/9fa7bb28a2844a71/RECEIPT.json) binds
source ID `04199126326004a35c2d4de2288eff18dba1b538ed2580edf5e8983bf262b7a4` and the archived executed source.

This establishes regression preservation and removal of the guarded detached map
copies. It does not establish meaningful speedup, query-local execution, or
active-subspace scaling. Whole-field scans and preparation still require the
separate integration and measurement work in issue #115.
