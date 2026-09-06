# PR90 — digest cache compatibility regression proved

Read first: do not merge the digest memoization at PR head
`52d3be2938a3576fb2777bfcb5d415b397db0286` under the existing metadata API.

## Exact scope and finding

- Candidate `space.py` SHA256: `84d0923cb608fc6010e4254bb9a2211d533a5c32b3fd993540bb810024fab934`.
- Baseline: `53d404f56140386f43d591cc8697cdf6be7669a1`.
- Source modules were copied verbatim from Git objects / the supplied exact PR file.
- Only `space.py` differs between the isolated baseline and candidate packages.
- `Atom.meta` and `Hyperedge.meta` accept nested dictionaries/lists under `Any`.
- Their `as_dict()` methods copy only the outer tuple to a dict and expose nested aliases.
- After the first `digest()`, four ordinary nested-metadata changes alter the current
  canonical serialization while the PR still returns the previous digest.
- This invalidates digest-as-current-content identity; it is not a claim of hash collision.
- Frozen dataclass attributes and read-only top-level maps do not recursively freeze values.

## Actual isolated control

Run once on laptop billy using the existing G1 Python; no repository checkout changed.
`/home/billy/orion-director-work/20260906/g1-env/bin/python -B control.py`

Eight cases per implementation: unchanged repeated read; atom/edge nested input aliases;
atom/edge nested aliases returned by public `as_dict()`; fresh constructor after mutation;
new generations produced by `with_atoms` and `with_edges`.

- Baseline: 8/8 digests equal independent fresh canonical SHA256.
- PR candidate: 4/8 equal. All four nested-alias cases mismatch.
- Unchanged-state and all three fresh-generation controls pass in both implementations.
- Every mutation/generation actually changed the serialized content; this is checked.
- Source hashes were checked before and after execution.
- No OCMRuntime, model, solver, suite, benchmark or production replay was executed.
- Exit 0 means the diagnostic completed; the recorded PR verdict is
  `COMPATIBILITY_REGRESSION_PROVED`, not a passing compatibility check.

## Minimal repair

Remove `_digest_value` memoization and retain fresh canonical hashing until all
accepted hash-relevant values have an explicitly enforced immutable representation.
Independent structural lookup optimizations need not be discarded for this finding.
A recursive immutable snapshot with detached exports is a larger API/serialization
change requiring separate compatibility controls; a shallow copy or top-level proxy
will not repair these four demonstrated cases.

Raw evidence: `observed.json`, `control.stdout`, `control.stderr`, `control.py`,
`source-bindings.json`, and the eight exact source files. `SHA256SUMS.json` binds
all packet files except itself. No PR or issue write was performed by this review.
