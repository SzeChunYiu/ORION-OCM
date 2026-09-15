# GMI #833 morphology transformation geometry v1

**Status:** finite exact foundation tranche; not full morphology topology or developmental equivalence.  
**Freeze:** `FREEZE_V1.md`, commit `fea6549a700681c0e830bf53cc53ab4f2dd5535f`.  
**Claim ceiling:** `GMI_TRANSFORM_CATEGORY_AND_DIRECTED_SCALAR_GEOMETRY_AT_REGISTERED_FINITE_SCOPE`.

## 1. Scientific object

Fix a registered scientific scope `Omega`. Objects are architecture-name-free morphology/mechanism classes already admitted by the #848 equivalence contract. This tranche does not change that equivalence relation.

A registered transform is

`T = (s,t,eps,rho,A,E)`

where `s,t` are source/target mechanism classes, `eps >= 0` is a declared semantic-distortion increment, `rho in R_+^d` is a raw lifecycle-resource vector, `A` is a finite consistent map of applicability assumptions, and `E` is a nonempty finite evidence set. The identity transform at `M` has `s=t=M`, zero error/resources, no assumptions, and a distinguished neutral identity-evidence marker.

Ordinary transforms with absent evidence are invalid. The identity evidence marker is neutral under composition and cannot be used as ordinary evidence.

Composition `G o F` is defined only if `target(F)=source(G)` and the union of their assumption maps is consistent. For a valid pair:

- source/target compose by endpoints;
- semantic error is added;
- resource vectors are added coordinatewise;
- assumptions are unioned canonically;
- nonidentity evidence is unioned canonically; the identity marker disappears next to ordinary evidence.

Any endpoint mismatch, contradictory assumption, negative resource/error, malformed resource dimension, or missing ordinary evidence fails closed.

## 2. TRANS-1A — category laws

### Identity

Let `1_M` be the identity at `M` and `F:M->N` any valid transform. By definition `1_M` contributes zero semantic error, the zero resource vector, the empty assumption map, and only the neutral identity-evidence marker. Therefore composition leaves every registered field of `F` unchanged:

`F o 1_M = F`, and `1_N o F = F`.

The executable checker compares the complete immutable transform object, not merely endpoints or behavior.

### Associativity

For composable valid transforms `F:M->N`, `G:N->P`, `H:P->Q`, assume the total union of their assumption maps is consistent. Endpoint composition is associative. Addition in `Q_+` and coordinatewise addition in `Q_+^d` are associative. Set/map union followed by canonical sorting is associative when the union is consistent. Evidence union with deletion of the neutral identity marker is associative. Hence

`H o (G o F) = (H o G) o F`.

If the global assumption union is inconsistent, at least one required composition fails closed; this tranche does not fabricate a morphism by choosing an order that hides the contradiction.

### Scope

This is an ordinary small finite-category style construction over registered objects and morphisms. Category theory owns the algebra. The GMI-specific content is the typed transform record and its integration with semantic error, lifecycle resources, assumptions, evidence, and fail-closed scientific governance.

## 3. DIST-1A — directed shortest-transform burden

Freeze resource weights `w_i > 0` and semantic-error weight `eta >= 0`. For a valid transform `T`, define

`c(T) = sum_i w_i rho_i(T) + eta eps(T)`.

Every edge cost is nonnegative. For a finite directed transform graph, define

`d_w(M,N) = inf/smallest total c along valid directed paths M -> N`,

with the empty path giving `d_w(M,M)=0` and with `d_w(M,N)=+infinity` when no valid path exists. At finite scope the infimum over reachable simple-cost candidates is attained by a shortest path; the implementation uses exact rational Dijkstra arithmetic and preserves `INF` for unreachable pairs.

### Identity zero

The empty path has cost zero, while nonnegative edge costs prevent a negative path. Therefore `d_w(M,M)=0`.

This is a pseudometric-style identity claim: zero distance between distinct objects is not excluded if a registered zero-burden transform exists.

### Directed triangle inequality

If either `d_w(A,B)` or `d_w(B,C)` is infinite, no finite right-side claim is made. Otherwise choose shortest finite paths `p:A->B` and `q:B->C`. Their concatenation is a valid path `q o p:A->C` with additive cost

`c(q o p)=c(p)+c(q)=d_w(A,B)+d_w(B,C)`.

Since `d_w(A,C)` is the minimum over all valid `A->C` paths,

`d_w(A,C) <= d_w(A,B)+d_w(B,C)`.

No symmetry premise is used. The exact witness has `d(A,C)=3` and `d(C,A)=9`.

### Unreachability

When there is no directed path from `M` to `N`, the distance is `+infinity`. The implementation never replaces this with a large finite sentinel. The finite receipt contains `d(A,E)=INF`.

## 4. Raw vector burden remains primary

The scalar `d_w` exists only after weights are frozen. It is not a universal morphology distance.

The hostile pair

`r_compute=(1,4,1)`, `r_memory=(4,1,1)`

is Pareto-incomparable. Under weights `(4,1,1)` the first is cheaper; under `(1,4,1)` the second is cheaper. This reproduces the #837 principle that positive scalarization preserves strict Pareto dominance but can reverse incomparable alternatives.

The stronger successor should therefore treat a transform's resource/error burden as an ordered-vector/Pareto object first and derive scalar Lawvere-style distances only conditionally. Quantale/ordered-monoid enrichment remains open.

## 5. Exact machine certificate

`transform_geometry_v1.py` uses `fractions.Fraction` for every finite numeric theorem witness. `test_transform_geometry_v1.py` checks:

- exact left/right identities;
- exact associativity;
- exact additive resource/error composition;
- endpoint mismatch failure;
- contradictory-assumption failure;
- missing-evidence failure;
- negative error/resource failure;
- invalid scalar-weight failure;
- directed shortest-path identity, triangle, asymmetry and unreachable behavior;
- deterministic GREEN receipt.

The deterministic receipt has 5 nodes, 5 directed edges, 25 ordered pairs, 125 ordered triples checked for triangle violations, and 6 hostile construction/composition cases. Normal and optimized Python must reproduce the receipt byte-for-byte.

## 6. Parent ownership

No novelty is claimed for:

- category identities/associativity;
- path concatenation;
- shortest paths with nonnegative weights;
- Lawvere/generalized directed metric ideas;
- Pareto order or weighted-sum scalarization.

The residual GMI contribution at this stage is a machine-checkable transform contract that connects those parent objects to architecture-independent morphology classes, evidence, assumptions and lifecycle resource accounting without claiming developmental equivalence.

## 7. Falsifiers

This tranche is RED at its claimed scope if any of the following occurs:

- an identity changes an ordinary transform's registered fields;
- composition depends on parenthesization for a compatible triple;
- an incompatible or evidence-free transform is admitted;
- a negative resource/error is admitted;
- any finite registered triangle violates the directed triangle inequality;
- an unreachable pair is assigned a finite distance;
- the asymmetric hostile becomes symmetric without changing the registered graph;
- a scalarization reversal is hidden while a universal scalar distance is claimed;
- normal and optimized execution produce different receipts.

## 8. Forbidden promotions

This tranche does not establish developmental naturality, stochastic-kernel naturality, grammar/remint invariance, a topology of the unrestricted intelligence space, P3/P4 recovery, known-form closure, held-family prediction, unknown-form discovery, or complete GMI.

The next dependency-ordered theorem target is **TRANS-2: developmental naturality**, including an exact hostile where static behavior preservation succeeds but update trajectories fail to commute.
