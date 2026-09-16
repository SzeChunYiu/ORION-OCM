# GMI #833 E3 — local/global/graph operator freeze v1

**Parent:** #833 Section E  
**Child:** #882  
**Source main:** `43102437ebcbf6f818bb58b45470beffaf865029`  
**Status:** pre-implementation theorem/evidence freeze

This file freezes the typed carrier, operator signatures, finite exhaustive universe, resource semantics, separation hostiles, permutation-relabeling theorem targets, and claim ceiling before executor/tests/results/reconciliation/workflow.

## Scientific boundary

This tranche registers architecture-family-free finite state-field operators. It does not claim neural/GNN derivation, universal graph expressivity, stochastic dynamics, multi-agent communication, infinite-graph results, or morphology optimality.

Parent mathematics remains parent-owned: local distributed computation, cellular/local update systems, permutation-invariant set aggregation/equivariant maps, and graph-neighborhood/message-passing patterns.

## Registered carrier

- sites: `V=(0,1,2)`;
- values: `Z3={0,1,2}`;
- state: total map `x:V->Z3`;
- graph: undirected simple edge set over `V` with no duplicates or self-loops;
- update: synchronous, computed entirely from the pre-step state.

All `2^3=8` simple undirected graphs and all `3^3=27` states are in the exhaustive finite certificate.

## Operator contracts

### OP-L — POINTWISE

For registered unary `f:Z3->Z3`:

`x'_v = f(x_v)`.

Frozen witness: `f(a)=a+1 mod 3`.

Target: one-step output at `v` depends only on `x_v`; graph changes and other-site changes cannot affect `v`.

### OP-G — GLOBAL_BROADCAST

For commutative/permutation-invariant fold `⊕` and `phi`:

`a = ⊕_{u in V} x_u`, then `x'_v = phi(x_v,a)`.

Frozen witness: `⊕=sum mod 3`, `phi(self,a)=self+a mod 3`.

Target: vertex relabeling equivariance; remote-site change can affect every site in one step. Graph topology is not an input to this operator.

### OP-N — NEIGHBOR_UPDATE

For each site:

`a_v = ⊕_{u in N(v)} x_u`, then `x'_v = psi(x_v,a_v)`.

Frozen witness: `⊕=sum mod 3`, empty-neighborhood identity `0`, `psi(self,a)=self+a mod 3`.

Target: one-step output at `v` depends only on `x_v` and declared one-hop neighbors; a non-neighbor state change cannot affect `v`, but a neighbor-state or incident-edge change can.

## Relabeling target

For every permutation `pi` of `V`, transport state and graph by `pi`. Each registered operator must satisfy exact equivariance:

`Op(pi*x, pi*E) = pi*Op(x,E)`

where graph is ignored by OP-L/OP-G but still transported for a uniform checker.

Exhaustive certificate per operator:

`8 graphs * 27 states * 6 permutations = 1296` comparisons.

Zero mismatches are allowed for each of OP-L, OP-G, OP-N.

## Exact raw resources

Every one-step operator emits:

`(site_reads, site_writes, edge_reads, aggregate_ops)`.

Frozen accounting:

- POINTWISE on 3 sites: `(3,3,0,0)`.
- GLOBAL_BROADCAST: read all 3 sites for the fold, then each self value for update: `(6,3,0,2)` where a 3-element fold requires exactly 2 binary aggregate operations.
- NEIGHBOR_UPDATE on graph `E`: self reads `3`, neighbor reads `2|E|`, site writes `3`, edge reads `2|E|`, aggregate ops `sum_v max(deg(v)-1,0)`; isolated neighborhoods use identity `0` with zero aggregate ops.

Resource counts are part of the executable certificate and are independently recomputed from graph degree data.

## Separation hostiles

Required exact witnesses:

1. same state, empty graph vs one-edge graph: POINTWISE and GLOBAL outputs identical; NEIGHBOR output changes when the edge connects nonzero state.
2. remote-state twin for site 0 on a graph where site 2 is not adjacent to site 0: POINTWISE site-0 unchanged; GLOBAL site-0 changes; NEIGHBOR site-0 unchanged.
3. neighbor-state twin for site 0: NEIGHBOR site-0 changes.
4. incident-edge twin with fixed state: NEIGHBOR site-0 changes.
5. non-incident-edge twin with fixed state: NEIGHBOR site-0 unchanged.

These distinguish local, global, and graph-local information channels rather than naming architectures.

## Fail-closed hostiles

Reject before execution/certification:

- state missing a site, containing extra sites, or value outside `Z3`;
- edge endpoint outside carrier;
- self-loop;
- duplicate/reversed-duplicate edge in raw input;
- non-bijective relabeling;
- ordering-dependent/non-commutative fold supplied to the registered equivariance certificate.

## Claim ceiling

`GMI_FINITE_LOCAL_GLOBAL_GRAPH_OPERATOR_SEMANTICS_AT_REGISTERED_SCOPE`

Forbidden promotions:

- `UNIVERSAL_GRAPH_EXPRESSIVITY`
- `GNN_DERIVED`
- `NEURAL_ARCHITECTURE_DERIVED`
- `ARBITRARY_GROUP_EQUIVARIANCE`
- `INFINITE_GRAPH_RESULT`
- `STOCHASTIC_OPERATOR_COMPLETE`
- `MULTI_AGENT_COMPLETE`
- `MORPHOLOGY_SELECTION_OPTIMAL`
- `COMPLETE_GMI`

## Reconciliation boundary

After exact-head PR CI is green, only these #833 rows may change:

- `Add generic local/global operators.`
- `Add graph/local interaction operators.`

Every other Section-E row remains open.
