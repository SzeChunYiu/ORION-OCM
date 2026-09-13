# Terminal-cost reconstruction — TCR-1–4

Scope: finite deterministic coordinate-query policies, exact adequate actions,
and supplied nonnegative rational query and terminal resource vectors.

## Parents and the concrete missing premise

[Javdani et al. (2014), §2](https://proceedings.mlr.press/v33/javdani14.pdf)
allows overlapping decision regions and stops when all remaining hypotheses
fit one region. Its objective charges tests. The repository's
[RQR-1–4](../gmi-grand-unification-v1/RELATIONAL_QUERY_RECONSTRUCTION_THEOREM_V1.md)
therefore explicitly excludes output-dependent cost from Boolean stopping
reconstruction. Nothing below contradicts that scoped theorem.

[Smallwood and Sondik (1973)](https://pubsonline.informs.org/doi/10.1287/opre.21.5.1071)
provides the finite-horizon policy-value-vector dynamic-programming parent.
Here a static exact-query state and all-input adequacy replace its probabilistic
observation/control model. Coordinatewise antichains retain joint resource
feasibility without selecting one prior or scalar objective. This is a finite
specialization of established decision-tree and vector-backup mechanisms,
not a new general dynamic-programming algorithm or physical law.

## Fixed execution interface

Let X={0,1}^n be the labelled admitted inputs, A a nonempty finite action set,
and R(x) subseteq A the adequate actions. Empty rows expose infeasibility.
The only input access is an exact coordinate query i, with supplied charge
q_i in Q_+^d, d>=1. Queries change neither x nor the relation.
At a leaf the policy chooses one action a, adequate for every input reaching
that leaf, and pays the supplied vector t(x,a) in Q_+^d exactly once.
Input-dependent terminal cost is assessed after choosing a; it is not a free
observation supplied to the controller. The complete table is supplied.

All finite deterministic trees are admitted, initially without input advice.
Correctness holds on every x, including inputs with zero probability in any
later expectation. For tree T, v_T(x,j) sums executed query charges plus the
terminal charge. Resource order is pointwise over both labelled x and j.
Action identities require a retained dictionary; costs do not encode outputs.
Policy code/storage, interpreter overhead, data acquisition, synthesis and
physical realization are separate charges and are not reconstructed here.

For partial assignment p, C(p) is its nonempty labelled subcube. Define

    K_R(p) = {(t(x,a))_(x in C(p)) : a in intersection_(x in C(p)) R(x)},
    L_R(p) = Min K_R(p),

where Min removes strictly coordinatewise dominated distinct vectors. Keep
an adequate action witness with every retained vector. Empty K has empty Min.
L is an optimization invariant, not all attainable terminal profiles.

## TCR-1 — exact finite construction and pruning

For each p, union its K_R(p) with all unfixed-coordinate options. For query i,
choose one child vector u_b at each p_b=(p,i=b) and splice

    w(x,j) = q_i(j) + u_(x_i)(x,j).

With full K and no pruning this constructs exactly the no-repeat tree profiles.
With L at leaves and Min after every union it constructs exactly their
pointwise Pareto frontier. Preserve an actual tree witness at each backup.

Proof: induction on the number of unfixed coordinates. A no-repeat tree is
either a common-action leaf or a first unfixed query followed by two such
trees. These alternatives are complete and every construction is executable.
Child coordinatewise domination is preserved by splicing and addition of the
same query vector. Every discarded finite-set vector has a retained dominator,
so pruning cannot remove an undominated parent profile. QED.

Stopping being feasible does not justify removing query options: a query may
permit cheaper adequate actions. No child averages replace pointwise vectors.

## TCR-2 — all finite trees, invariance and joint feasibility

A repeated coordinate has a predetermined answer on its current transcript.
Replace it by the reached child. This preserves the final action on each x
and removes nonnegative query charges. Iterating gives a no-repeat tree with
no greater cost. Thus TCR-1's finite frontier is also the exact frontier of
all finite trees. Zero-cost repetition adds no new minimal profile. With a
nonempty adequate row everywhere, querying all bits constructs a feasible
tree; an empty row makes every tree inadequate.

If two tasks have identical L(p) on every labelled subcube, with the same
query interface and charges, their frontiers coincide by the same recurrence.
If they instead have identical full K(p), their complete no-repeat profile
sets coincide. Neither statement supplies the other task's action dictionary.
Equality of L need not preserve dominated or wasteful profiles.

For any common family of coordinatewise nondecreasing functionals, every
joint finite upper-bound constraint is feasible iff some single retained
profile meets all bounds. This includes expected and worst-case resource
coordinates under any supplied prior. Arbitrary nonmonotone objectives,
lower-bound constraints, randomization, stochastic queries and changed
execution primitives are outside this claim. Separate coordinate minima
cannot be assembled into an executable combined witness.

## TCR-3 — Boolean stopping loses terminal work

Take n=1, q_0=1, A={c,e,u,v} with t(c)=0, t(e)=3 and t(u)=t(v)=0:

| Input | R | S |
|---|---|---|
| 0 | {c,e,u} | {c,e,u} |
| 1 | {c,v} | {e,v} |

The labelled subcube stopping flags agree everywhere, as do action alphabet
and row sizes. R emits c at zero cost. S's only common root action is e,
costing (3,3); querying once and choosing cheap leaf actions costs (1,1),
which is its exact frontier. R has frontier (0,0). Boolean feasibility cannot
reconstruct total work; L retains the missing root charge. A policy that
always stops at the first adequate cell fails on S.

## TCR-4 — retain joint outcomes and the zero-cost parent

At n=0 let two adequate actions cost (0,2) and (2,0). Both are minimal; no
action meets (0,0). Retaining marginal minima invents a nonexistent policy.
With scalar input-dependent charges (0,2) versus (2,0) on two inputs, taking
the pointwise cheaper action without paying the information needed to choose
it similarly invents an unavailable zero-cost root action.

When every terminal charge is zero, K(p) is either empty or the singleton
zero vector, exactly RQR's Boolean stopping information. The full backup
therefore recovers its no-repeat query profiles and the pruned backup its
frontier. Positive and negative controls include zero queries, zero-mass
obligatory inputs, incomparable vectors, dominated terminal actions and
permuted action labels with transported cost dictionaries.

## Representation and remaining costs

A dense supplied model stores |X||A| adequacy bits and d|X||A| rationals,
plus query vectors and action/header encodings. K examines 3^n labelled cells
and may retain |A| profiles per cell before pruning. The construction exposes
cell visits, child Cartesian pairs and generated vector entries; its finite
enumeration can still be exponentially large. Those are abstract development
counts, not timings, bit-complexity bounds, controller storage or lifetime
costs. A richer platform theorem must supply and charge those mechanisms.
