# GMI #833 E3 — finite local/global/graph operators

This capsule extends the architecture-uncommitted G0 programme with three typed finite state-field operators:

- `POINTWISE` — one-site-local update;
- `GLOBAL_BROADCAST` — permutation-invariant whole-carrier aggregation followed by sitewise update;
- `NEIGHBOR_UPDATE` — one-hop graph-local aggregation followed by sitewise update.

The registered witnesses operate synchronously on three `Z3`-valued sites. They exist to prove exact semantic distinctions, relabeling equivariance and resource accounting at a finite scope; they are not architecture-family macros and do not establish neural/GNN universality.

The exact exhaustive certificate covers all 8 simple undirected three-site graphs, all 27 states and all 6 vertex relabelings for each operator. Every operator therefore receives 1,296 equivariance checks, with zero mismatches required.

Claim ceiling:

`GMI_FINITE_LOCAL_GLOBAL_GRAPH_OPERATOR_SEMANTICS_AT_REGISTERED_SCOPE`
