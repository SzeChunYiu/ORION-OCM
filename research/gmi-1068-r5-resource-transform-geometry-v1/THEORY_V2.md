# R5-S1 — reachable cost sets and conditional directed geometry

R5 V1 remains historical evidence. The successor removes two proof defects and one existence overclaim.

## General derived object

Let `Proc(M,N)` be the substrate-admitted processes/paths from `M` to `N`, and let a declared resource account assign a cost vector `c(f)`.

The general derived object is the **reachable transformation cost set**:

`C(M,N) = { c(f) | f in Proc(M,N) }`.

If no admitted process connects `M` to `N`, then `C(M,N)` is empty. No finite burden is fabricated.

A Pareto frontier is a derived view of this set only when undominated elements exist. Finite nonempty registered cost sets have such elements. Arbitrary infinite sets need not.

For example, the scalar cost set `{1/n | n >= 1}` has no minimum: for every `n`, the element `1/(n+1)` is strictly smaller than `1/n`.

Therefore the universal layer must not identify "cost set" with "Pareto minimum/frontier."

## Scalar directed distance at registered finite scope

For a nonnegative weight vector `w` and a finite nonempty cost set:

`d_w(M,N) = min { w dot c | c in C(M,N) }`.

For an unreachable pair the finite implementation returns no finite distance; an extended-distance presentation may write this as `+infinity`.

Identity-zero requires a zero-cost empty/identity path under the declared resource account. It does not follow merely from the word "identity."

Triangle requires a subadditive composition account:

`c(g after f) <= c(f) + c(g)`

in the declared resource order. Under that premise, every composed M-to-N-to-P path supplies an M-to-P candidate, so the optimum M-to-P cost is no larger than the cost through N.

The registered finite graph derives this inequality from actual path costs. The Lean successor derives the same finite inequality from the explicit minimum formula; it does not take the conclusion as a hypothesis.

## Directed asymmetry

Nothing requires `C(M,N)` and `C(N,M)` to be equal or simultaneously nonempty. Compilation, irreversible physical transformations, information loss, or one-way interfaces can produce finite cost one way and no path the other way.

Thus the geometry is generally directed and extended, not a symmetric metric.

## Reachable balls and convertibility regions

Where a scalar distance is declared, a finite reachable ball is:

`B_w(M,r) = { N | d_w(M,N) is finite and d_w(M,N) <= r }`.

For the registered `w=(1,3)` fixture:
- radius 1 reaches A and B;
- radius 5 reaches A, B and C.

Order intervals and vector-resource regions are likewise derived from the declared convertibility preorder/cost-set order; no topology is imported without additional assumptions.

## Presentation relabeling and frontier transport

A bijection of process/path presentations transports the cost set when it preserves:
1. source/target reachability;
2. the contextual value/observation relevant to the comparison;
3. each declared cost vector.

The Lean successor proves generic reachable-cost-set transport from a bijection plus cost preservation.

The executable route performs a nontrivial node rename `A,B,C -> X,Y,Z`, rebuilds the transformed graph, re-enumerates its paths, and recomputes the cost set/frontier.

A negative control changes the transported direct-path cost to `(0,0)`; the recomputed frontier changes. Therefore lexical renaming alone earns nothing unless the scientific quantities are preserved.

## Strongest-parent ownership

General resource convertibility, ordered commutative monoids, categorical resource theories, Pareto order, and Lawvere-style directed/extended distance are established parent mathematics.

GMI's residual at R5 is the placement of these structures as **derived views of substrate-admitted processes plus declared context/resource accounting**, together with exact boundaries on when transport/frontier language is licensed.

The #833 MTG results remain richer in-corpus specializations where they add relabeling groupoids, naturality tiers, topology, or enriched algebra. R5-S1 does not reclaim those parent or historical results.

## Claim ceiling

`GRAND_GMI_V2_R5_S1_REACHABLE_COST_SET_AND_CONDITIONAL_DIRECTED_GEOMETRY_AT_REGISTERED_SCOPE`
