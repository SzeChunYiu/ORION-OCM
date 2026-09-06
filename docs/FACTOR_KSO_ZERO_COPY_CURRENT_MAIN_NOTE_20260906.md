# Factorized KnowledgeSpace FK-1 zero-copy current-main replay

Programme: #115  
Baseline: `main@63c3fe578e6c8c4e5d900208f1cdfa83344171ab`

## Scope

This is the current-main replay of the narrow FK-1 allocation cleanup that was
previously qualified on an older source baseline and deliberately not force-merged
after concurrent mainline movement.

Existing read-only paths in `navigation_sparse.py` and `extraction.py` use the
cached read-only `KnowledgeSpace.atom_view` instead of `atom_map()`, which returns
a detached mutable dictionary for compatibility. The public `atom_map()` API and
all navigation/extraction semantics remain unchanged.

## Qualification

The current-main source-bound workflow completed successfully before this note:

- zero-copy hostile/inherited controls: GREEN;
- exact engineering recorder: GREEN;
- all M1–M12 wrapper verification: GREEN;
- immutable successor engineering receipt committed;
- receipt full suite: 1145 passed;
- receipt focused suite: 133 passed.

This documentation-only human successor exists so ordinary pull-request workflows
run on the same qualified source bytes. It does not change the qualified `src/`
implementation.

## Claim boundary

Allocation cleanup only. No wall-clock speedup, active-subspace scaling, `k << N`
claim, lower lifetime cost, OCM novelty or scientific residual is established.
