# Local/global/graph operator theorems v1

## Expert review lanes

- **Formal semantics / distributed algorithms:** checks exact information-dependence boundaries.
- **Symmetry / representation:** checks vertex-relabeling equivariance under transported state and graph.
- **Resource semantics:** checks raw reads/writes/edge traversals/fold operations independently of semantic output.
- **Hostile verification:** constructs smallest topology/state/edge counterexamples and malformed-input failures.

## LOC-1 — pointwise locality

For `POINTWISE(f)`, `x'_v=f(x_v)`. Therefore changing any `x_u` with `u!=v`, or changing graph topology, cannot affect site `v` in one synchronous step.

Frozen witness `f(a)=a+1 mod 3` satisfies this exactly over every registered state/graph.

## GLOB-1 — permutation-equivariant global dependence

Let `a=⊕_{u∈V}x_u` where `⊕` is permutation invariant, and let `x'_v=phi(x_v,a)` with the same `phi` at every site. Under any vertex permutation `pi`, the global aggregate is unchanged and sitewise application transports pointwise, hence

`GLOBAL(pi*x, pi*E)=pi*GLOBAL(x,E)`.

The frozen sum-mod-3 witness also has a strict remote-dependence counterexample: changing site 2 can change site 0 even when no graph edge connects them.

## GRAPH-1 — one-hop graph locality

For `NEIGHBOR_UPDATE`, site `v` uses only `x_v` and the multiset of values at `N(v)` from the pre-step state. Therefore a non-neighbor state change and a non-incident edge change cannot affect `v` in one step. A neighbor-state or incident-edge change can.

The frozen hostile suite includes both directions; locality is not inferred from naming.

## EQ-1 — vertex relabeling equivariance

For all 8 three-site simple graphs, all 27 `Z3^3` states and all 6 vertex permutations, each registered operator satisfies exact transported-state equality. This is 1,296 checks per operator, 3,888 total, with zero mismatches.

The theorem is scoped to the registered finite carrier and the commutative/permutation-invariant fold. It does not imply arbitrary-group or infinite-graph equivariance.

## RES-1 — exact raw resource accounting

One synchronous step emits `(site_reads,site_writes,edge_reads,aggregate_ops)`.

- POINTWISE: `(3,3,0,0)`.
- GLOBAL_BROADCAST: `(6,3,0,2)`.
- NEIGHBOR_UPDATE depends on graph degree: edge-count 0/1/2/3 gives exactly `(3,3,0,0)`, `(5,3,2,0)`, `(7,3,4,1)`, `(9,3,6,3)`.

The primary implementation and an independent oracle compute these values by separate code paths.

## SEP-1 — local/global/graph-local channels are machine-distinct

Frozen counterexamples establish:

- topology changes leave POINTWISE/GLOBAL unchanged but can change NEIGHBOR_UPDATE;
- a remote non-neighbor state change leaves POINTWISE and NEIGHBOR_UPDATE at site 0 unchanged but changes GLOBAL_BROADCAST;
- a neighbor-state change changes NEIGHBOR_UPDATE at site 0;
- an incident edge can change site 0 while a non-incident edge cannot.

Thus the three contracts expose distinct information channels without architecture-family labels.

## Falsifiers

Any equivariance/resource mismatch, accepted malformed graph/state/permutation/fold, or failure of a registered separation hostile makes the tranche RED.
