# GMI #833 Pareto transform algebra and forward topology v1

**Freeze:** `FREEZE_V1.md`, commit `39894c4b5a25521d78568955f687a10a672bce42`.  
**Claim ceiling:** `GMI_PARETO_TRANSFORM_ALGEBRA_AND_FORWARD_TOPOLOGY_AT_REGISTERED_FINITE_SCOPE`.

## 1. Why a scalar morphology distance is not primary

The merged DIST-1A result shows that once a positive price vector is frozen, minimum directed transform burden is a Lawvere-style scalar pseudometric. But #837 already establishes that positive scalarizations can reverse Pareto-incomparable alternatives. Therefore GMI should retain transform burden as a nonnegative vector first.

Let a burden vector include whatever nonnegative coordinates are registered at scope, for example semantic distortion, compute, memory, communication, energy, latency, or other lifecycle coordinates. This tranche uses finite rational vectors for exact checking.

For finite `S subseteq Q_+^d`, let `PF(S)` contain exactly the Pareto-minimal vectors: `v in S` remains when no distinct `u in S` satisfies `u_i <= v_i` for all coordinates with strict inequality somewhere.

A Pareto frontier is represented by its canonical sorted antichain.

## 2. Finite Pareto antichain algebra

Define

`A (+) B = PF(A union B)`

and

`A (*) B = PF({a+b : a in A, b in B})`.

The empty frontier is `0` (unreachable/no alternative) and `I={0_vector}` is the sequential identity.

### PF idempotence

`PF(PF(S))=PF(S)` because all and only dominated vectors were removed on the first application.

### Choice laws

Set union is associative, commutative and idempotent. Applying `PF` before or after additional union cannot change the final minimal elements: a vector discarded as dominated cannot later become minimal merely because more alternatives are added. Hence `+` is associative, commutative and idempotent, with empty frontier as identity.

### Composition identity and absorbing element

`a+0=a`, so `A*I=A=I*A`. If either side is empty there is no composable burden pair, so `A*0=0=0*A`.

### Composition associativity

Vector addition is associative. Before Pareto reduction, both `(A*B)*C` and `A*(B*C)` generate exactly all vectors `a+b+c`. Pareto reduction therefore yields the same antichain.

### Distributivity

Before Pareto reduction,

`A*(B union C) = (A*B) union (A*C)`.

If `b'` dominates `b`, then for every nonnegative `a`, `a+b'` dominates `a+b`; therefore pruning a dominated operand before Minkowski addition cannot create a new minimal sum. The same holds on the left. Thus `*` distributes over Pareto `+`.

The executable certificate enumerates every subset of `{0,1,2}^2`, yielding 20 distinct Pareto frontiers, and checks the registered unary, pair and four triple laws over the complete 20-frontier universe: 100 unary, 400 pair and 32,000 triple-law assertions.

This is finite idempotent-semiring / multiobjective-path mathematics. A complete quantale or unrestricted enriched-category claim is intentionally deferred.

## 3. Multiobjective transform closure

For a finite directed morphology graph, associate each edge `(M,N)` with the Pareto frontier of available direct transform burdens. Put `I` on every diagonal and empty frontier on absent edges. Floyd-Warshall-style closure using `+` and `*` gives `H(M,N)`, the Pareto frontier of attainable path burdens at the registered finite scope.

Because burdens are nonnegative, inserting a cycle cannot strictly improve a path vector; a cycle can be deleted without worsening any coordinate. Hence finite simple-path closure suffices for Pareto minima.

The witness contains four nodes. It includes:

- a one-way zero-burden `A -> B` transform;
- `B -> C` burden `(1,1)`;
- two direct `A -> C` alternatives `(5,0)` and `(0,5)`;
- `C -> A` burden `(6,6)`;
- isolated `D` except for its identity.

Closure yields

`H(A,C) = {(0,5),(1,1),(5,0)}`

and leaves `H(A,D)` empty.

### Why coordinatewise infimum is invalid

For `S={(1,4),(4,1)}`, coordinatewise infimum is `(1,1)`, but `(1,1)` is not attainable. Replacing a Pareto frontier by coordinatewise minima can therefore fabricate a nonexistent machine transformation. The hostile is frozen in the receipt.

## 4. Scalar Lawvere projection

Freeze strictly positive weights `w>0`. Define

`d_w(M,N)=min_{v in H(M,N)} w dot v`,

with `+infinity` for an empty frontier.

Identity path gives `d_w(M,M)=0`. If finite paths realizing burdens `a in H(M,N)` and `b in H(N,P)` are concatenated, their cost is `a+b`; closure contains a Pareto vector no worse than that sum. Positive scalarization preserves coordinatewise dominance, hence

`d_w(M,P) <= d_w(M,N)+d_w(N,P)`.

Symmetry is not required. In the witness `d(A,B)=0`, while under weights `(1,1)`, `d(B,A)=14`.

The checker verifies every ordered triple for three frozen positive price vectors `(1,1)`, `(3,1)`, and `(1,3)`.

### Scalarization loses information

The distinct frontiers

`F1={(1,4),(4,1)}`

and

`F2={(1,4),(2,3)}`

both have scalar minimum `5` under `(1,1)`, yet under `(1,4)` their minima are respectively `8` and `14`. Thus one scalar distance cannot reconstruct the transformation frontier. This is why `H` is primary and `d_w` is conditional.

## 5. TOPO-1A — forward budget-ball topology

Let `b in Q_{>0}^d` be a strictly positive burden budget. Define the strict forward ball

`B_b(M) = {N : exists v in H(M,N), v_i < b_i for every i}`.

### Basis theorem

These balls form a basis for a forward topology on the finite morphology set.

**Coverage.** The zero identity burden lies strictly below every positive `b`, so `M in B_b(M)`.

**Local refinement.** Suppose `N in B_b(M)`. Choose witness `v in H(M,N)` with `v<b` coordinatewise. Set residual budget `r=b-v`, which is strictly positive. If `P in B_r(N)`, choose witness `w in H(N,P)` with `w<r`. Sequential composition provides burden `v+w<b`. Pareto closure contains an attainable `u<=v+w`, so `u<b`; hence `P in B_b(M)`. Therefore

`B_r(N) subseteq B_b(M)`.

The ordinary basis theorem now generates a topology from arbitrary unions of these forward balls.

The executable certificate checks this refinement property in 433 source/budget/member cases over 64 positive 2D budgets, then enumerates all subsets of the four-node witness and verifies that the sampled basis generates a 12-open-set topology closed under pairwise unions and finite intersections.

## 6. Directed/non-Hausdorff boundary

A zero-burden transform from `A` to `B` puts `B` in every positive forward ball around `A`; the reverse direction has positive burden. Consequently the topology need not behave like a symmetric metric topology and need not be Hausdorff or `T1`.

This is a feature, not a defect: compilation, forgetting, quotienting, or irreversible developmental transformations can naturally be directional.

No smooth-manifold structure is asserted. Continuous parameter manifolds may exist inside particular morphology strata, but the global GMI object can contain directed discrete transitions and nonseparated points.

## 7. Relation to GAUGE-1

GAUGE-1 proved the registered quotient mechanism and transform burdens invariant under pure semantic remints. Therefore the finite Pareto/frontier construction here can be applied to quotient classes rather than syntax labels. This tranche does not re-prove search/reachability invariance; changing grammar description length or proposal order can still change which transformations are discovered within finite search budgets.

## 8. Falsifiers

The scoped claim is RED if any checked Pareto law fails, path closure invents an unreachable finite vector, coordinatewise-infimum fabrication is treated as attainable, any frozen scalarization violates triangle inequality, the scalar-information-loss hostile disappears, the forward-ball refinement condition fails, sampled open sets violate the topology axioms, or optimized/normal receipts differ.

## 9. Parent ownership and claim boundary

Pareto antichains, Minkowski sums, multiobjective shortest paths, idempotent semirings, Lawvere-style directed metrics, and topology generated by a basis are parent mathematics. GMI's residual here is their disciplined coupling to verified morphology transformations, semantic/resource burden and representation-invariant quotient objects.

This tranche does not establish a complete quantale-enriched category, a universal intelligence-space topology, Hausdorffness, manifold structure, a universal scalar price vector, P3 known-form recovery, empirical morphology transitions, or complete GMI.
