# GMI #1000 / #833-F finite reachability-fraction freeze v1

Source `main`: `5aaebc5a7bab7825f30c007d9fd5cd4e34f5118e`.

This prospective freeze was committed before implementing a traversal, oracle,
or result generator. It targets exactly one Section-F row:

> Measure reachable fraction under each developmental/search law.

## Fixed finite universe

The candidate universe and quotient are imported without modification from the
merged #966 `G0-fin-v1` package:

- structural budget `(code_cells, register_cells)=(2,2)`;
- protected input words `(), (0,), (1,)`;
- protected execution step cap `6`;
- quotient equality is equality of the complete protected observation table.

The quotient, rather than the presentation set, is the primary denominator.
The start presentation has one register and one table cell containing `HALT`.

## Frozen successor primitives

At a current presentation with `n` labels and `r` registers:

- `REWRITE` replaces exactly one instruction-table cell by any well-typed
  instruction at `(n,r)`;
- `GROW_CODE` appends one `HALT` cell when `n<2` and preserves all existing
  cells verbatim;
- `GROW_REGISTER` increments the zero-initialized register carrier when `r<2`
  and preserves the instruction table verbatim.

No primitive deletes a carrier cell. Reachability is reflexive-transitive
closure from the registered start.

## Complete declared law registry

`LAW_REGISTRY_V1.json` is exhaustive for this tranche and contains exactly:

1. `REWRITE_11`: `REWRITE` only, fixed to `(n,r)=(1,1)`;
2. `CODE_GROWTH_R1`: `REWRITE` plus `GROW_CODE`, with `r=1`;
3. `REGISTER_GROWTH_N1`: `REWRITE` plus `GROW_REGISTER`, with `n=1`;
4. `JOINT_GROWTH_22`: all three primitives under the `(2,2)` ceiling.

No post-outcome law may be added to v1. A successor registry requires a new
version and cannot retroactively enlarge this claim.

## Required evidence and falsifiers

- analytic reachable-set characterization for each law;
- primary exhaustive BFS over presentation successors;
- source-separated direct-product oracle that does not import the primary
  successor generator, traversal, or protected interpreter;
- exact quotient projection in both routes;
- invariance under all `5!` operation-token surface remints;
- hostiles for duplicate/unknown laws, illegal successor escape, removing
  rewrite or growth, semantics-changing pseudo-remints, and confusing
  presentation fractions with quotient fractions;
- deterministic normal and optimized-mode tests and byte-identical receipts.

## Claim ceiling and forbidden promotions

Allowed terminal:

`GMI_833_FINITE_REACHABLE_QUOTIENT_FRACTIONS_MEASURED_FOR_COMPLETE_DECLARED_LAW_REGISTRY_AT_REGISTERED_SCOPE`

`complete` modifies only the four-entry v1 registry. It never means all
possible developmental/search laws. This tranche does not claim universal
reachability, an unbiased law ontology, arbitrary budgets, stochastic or
adaptive dynamics, unbounded equivalence, optimizer convergence,
architecture-prior-free recovery, clustering, known-family recovery, or
complete GMI. It measures mass and does not re-prove #874 constrained
selection or #877 finite-prefix selection.
