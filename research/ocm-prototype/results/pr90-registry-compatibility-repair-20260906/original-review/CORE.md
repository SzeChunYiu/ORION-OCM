# PR90 — mutable-registry regression confirmed

Exact repaired PR head: `57392b3f5d564de11743ac8b11dc27295b7c3aa2`.
Baseline: `53d404f56140386f43d591cc8697cdf6be7669a1`.
Candidate space SHA256: `07eb5327f05850e11472bbe4d1c1ce9599b8c55413f1dc727246e1fa9ae780b5`.
Only space.py differs in the isolated five-module packages.

## Executed control

One small Python process on laptop billy; no checkout edits or broad suite.
Command: `/home/billy/orion-director-work/20260906/g1-env/bin/python -B control.py`.
Both arms pass three clean controls: adding atoms, adding edges, additive registry extension.

The baseline rejects each following operation after an existing type/relation becomes invalid.
The repaired PR returns a space, and that returned object's own validate() rejects it:

1. Remove an old atom type; add a different, still-registered atom type.
2. Remove an old atom type; call with_atoms() with no additions.
3. Remove an old relation; add a different, still-registered relation.
4. Remove an old relation; call with_edges() with no additions.
5. Replace relation_types with a dictionary excluding the old relation; add a valid edge.
6. Replace atom_types with a set excluding the old type; add a valid atom.

The public TypeRegistry contains mutable sets/dictionaries. Frozen Atom/KnowledgeSpace
attributes do not establish an immutable registry. Local checks of additions therefore do
not preserve the previous full-current-registry validation contract for retained objects.
Minimal repair: restore original replace/full-validation, including empty additions.
The prior digest repair is retained; it does not resolve this separate regression.

## Separate resource observation

After warming the old five structural indexes, materializing atom_view, edge_view and the
cached evidence universe added respectively 40, 40 and 216 shallow bytes on this host.
The last contains three evidence identifiers; no identifier objects are counted again.
index_resources() reported exactly the same vector before and after all three additions.
Its documentation promises structural-index/shallow-container accounting, not total RSS.
The structural proxy containers are omitted; explicitly include the new cache categories
or delimit their separately reported scope. These numbers are a tiny allocation observation,
not timing, total-process-memory, scaling or scientific evidence.

Raw observed.json includes every result/error, exact source hashes and before/after vectors.
control.stdout/stderr preserve the actual invocation. Source hashes matched before and after.
SHA256SUMS.json binds this subpacket except itself. Original digest-review files are unchanged.
