# Factorized KnowledgeSpace FK-1 zero-copy tranche

Programme: #115  
Parent implementation: #119 / `main@a88eb2cc63dd08da5a23e981d83177be0b73eebb`

## Scope

This tranche removes detached whole-atom-map copies from existing **read-only**
paths in:

- `src/ocm/kso/navigation_sparse.py`;
- `src/ocm/kso/extraction.py`.

The public mutable-copy `KnowledgeSpace.atom_map()` API is unchanged. Navigation,
extraction objectives, approximation labels, warrant/liveness behavior and output
ordering are unchanged. The replacement is the existing cached read-only
`ks.atom_view`.

## Hostile control

`tests/m1/test_sparse_extraction_zero_copy.py` monkeypatches `KnowledgeSpace.atom_map`
to raise and requires sparse matrix construction/activation plus reacting,
exact-bounded and greedy extraction to keep working, including revocation gating.

## Qualification

The branch-specific qualification completed successfully before this note:

- zero-copy hostiles and inherited KSO controls: GREEN;
- exact engineering recorder: GREEN;
- all M1–M12 wrapper verification: GREEN;
- immutable successor engineering receipt committed by GitHub Actions;
- receipt full suite: 1145 passed;
- receipt focused suite: 133 passed.

The receipt commit is bot-authored, so this documentation-only human successor
exists to let ordinary pull-request workflows run on the same qualified source
bytes. It is outside the `src/` change being qualified.

## Claim boundary

Allocation cleanup only. This does not establish a wall-clock speedup, sparse
`k << N` execution, local query scaling, lower whole-lifetime cost, OCM novelty,
or a scientific residual. Cold cached-index construction and all remaining global
work continue to count under #115/#70/#72.
