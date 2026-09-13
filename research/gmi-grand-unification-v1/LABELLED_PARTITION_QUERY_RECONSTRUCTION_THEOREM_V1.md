# Labelled output partitions reconstruct exact query optima — LQR-1–4

Date: 2026-09-13. Status: finite constructive scope resolution.

## 1. Primary parents and scientific subtraction

[Hyafil and Rivest (1976), §2](https://people.csail.mit.edu/rivest/pubs/HR76.pdf)
register objects, binary tests and complete decision trees, with expected test
work as the objective. We adapt the stopping obligation from identifying an
object to identifying its required output class. Their hardness theorem for a
general test register is not automatically a hardness result for this special
coordinate-query problem. [Ambainis and de Wolf (2000), §2](https://homepages.cwi.nl/~rdewolf/publ/qc/avq.pdf)
defines deterministic expected queries under a supplied input distribution,
while requiring correctness even on zero-probability inputs. We use that
classical convention; no quantum or randomized access is introduced.

The mechanism is ordinary exact decision-tree optimization and leaf relabelling.
The GMI implication resolves one richer invariant left open by
[FPW](FULL_PARTITION_WIDTH_COMPUTATION_SEPARATION_V1.md): a *labelled partition*
can determine query optima where the entire indexed width collection cannot.
This is neither a new complexity theorem nor unrestricted reconstruction of
[the master's](GRAND_GMI_MASTER_THEORY_V1.md) physical transformation spectrum.

## 2. Fixed register and richer invariant

Fix X={0,1}^n, n>=0, with labelled coordinates i=0,...,n-1 and bit convention
x_i=(x>>i)&1. The sole input access is a deterministic exact query of coordinate
i, costing a supplied finite nonnegative rational c_i. Queries do not change x.
The finite total obligation is a single output f(x). All inputs are admitted;
there is no input-dependent advice. Supply a rational distribution mu on X,
possibly with zero entries, for an expected-work objective. Every tree must
terminate and be correct on *all* X. All output relabelling and writing are free
in this query coordinate; their implementation costs are not inferred.

The invariant is the partition with its embedding in the labelled cube:

    Pi_f = { f^(-1)(a) : a in image(f) }, or x ~_f y iff f(x)=f(y).

It includes exactly which inputs belong to each block, not just block counts,
sizes or a quotient with its cube coordinates forgotten. A canonical table of
class indices represents Pi_f. It does not recover actual output strings;
an additional class-to-output dictionary is needed to emit those strings.

## 3. LQR-1 — exact profile preservation under output relabelling

If Pi_f=Pi_g on the same labelled X, there is a unique bijection
b:image(f)->image(g) with g=b o f. First normalize unreachable leaves, if any,
to labels in image(f); this changes no execution. For trees with all leaf labels
in image(f), relabel each leaf a by b(a). This is an exact g-tree with the same
queries, branches and cost v_T(x) on every input. Applying b^(-1) reverses this
normalized construction. Unused output symbols have no query-cost significance.

**Proof.** Equality of partitions makes b(f(x))=g(x) well-defined and injective;
its image is image(g). Leaf correctness follows for every input reaching that
leaf. Query trajectories and query charges do not depend on output labels.
Thus the complete attainable pointwise query-cost sets are equal, including
wasteful trees. In particular, any fixed monotone functional of these vectors,
all expected costs under a common mu, worst-case cost, and their *joint*
feasibility/frontier agree. This is stronger than equality of separate minima.
It is a sufficient invariant, not a claim that query optima identify Pi_f.

## 4. LQR-2 — constructive exact optimization from the partition

A transcript is a partial assignment p in {*,0,1}^n, with nonempty compatible
subcube C(p). It permits stopping exactly when C(p) lies in one partition block.
Let m(p)=sum_(x in C(p)) mu(x). Define unnormalised expected remaining work A(p)
and worst remaining work W(p). At a stopping state both are zero. Otherwise:

    A(p) = min_(i unqueried) [c_i m(p)+A(p,i=0)+A(p,i=1)],
    W(p) = min_(i unqueried) [c_i+max(W(p,i=0),W(p,i=1))].

A and W generally require different minimizing trees. Keeping each argmin
constructs both; A(*) is the optimal expectation because m(*)=1.

**Proof.** A repeated query has its answer fixed by the transcript; remove it
without increasing any nonnegative query cost. Stop immediately on a
monochromatic subcube. Every remaining nonterminal tree begins with one of the
listed coordinates, and each branch must be exactly correct on its full
subcube. Induction on the number of unqueried coordinates proves the lower
bounds and constructs minimizing children. Even when m(p)=0, the branch must
receive a correct finite subtree; it cannot be erased as a success obligation.
Full queries always suffice. Thus minima are finite and attained, including
zero-cost queries and the constant n=0 case. No infinity is a resource allowance.

For simultaneous bounds, retain the pointwise Pareto set P(p). At a stopping
state it contains the zero vector. Otherwise concatenate every pair of child
vectors across their compatible inputs, add c_i on every input, take the union
over first queries and remove pointwise dominated vectors. Any discarded child
is replaceable on that branch without increasing any parent coordinate.
Induction yields the exact pointwise frontier of all admitted trees. Its members
witness joint mean/worst bounds; separate scalar minima do not suffice.

## 5. LQR-3 — a joint constraint with an explicit positive repair

Take f(x)=x_1 if x_2=0, and x_0 if x_2=1; costs (1,2,3). Inputs other than 111
have mass 1/15 each; 111 has mass 8/15. The exact joint (mean,worst) frontier is

    (19/5, 6), (64/15, 5).

Querying x_2 first then the selected bit gives mean 3+2(4/15)+1(11/15)=64/15
and worst 5. Query x_0 first, then x_1, and query x_2 only if those answers
differ: its mean is 1+2+3(4/15)=19/5 and worst 6. These are actual trees.

For the lower bound, a tree beginning with x_0 has, on x_0=0, the remaining
AND of x_1 and not x_2; some inputs force both remaining queries. A first x_1
has the analogous two-essential-bit branch. Thus both first choices have
worst 6. Exhausting the two possible orders in their residual two-bit functions
gives minimum mean 19/5 for either first choice. First x_2 requires the selected
bit on each branch and has minimum mean 64/15 and worst 5. These exhaust every
useful first query. Hence no tree attains (19/5,5). Allowing mean 64/15 revives
worst 5; allowing worst 6 revives mean 19/5. A valid scalar recurrence plus
independent minima would miss this shared-policy constraint.

## 6. LQR-4 — falsification boundaries

Projection x_0 and parity x_0 xor x_1 each have two blocks of size two, but their
worst query costs are 1 and 2 with unit costs. An arbitrary bijection of cube
points maps their abstract partitions; it need not preserve coordinate probes.
Thus an unlabelled partition or block-size list is insufficient. OR_2 and parity
also have equal all-partition widths by FPW, but different labelled partitions
and expected costs 3/2 and 2 under uniform inputs.

Even a fixed labelled partition needs its other registers: OR_2 mean changes
from 3/2 to 5/2 under costs (1,3), or to 1 under mass concentrated at 11.
Parity requires both coordinate queries even under mass concentrated at 00,
because correctness still holds on every input. Adding a unit-cost parity
primitive changes its optimum from 2 to 1 without changing its partition.

For set-valued success, equality of admissible-action sets is insufficient:
on two input worlds, action sets {a,b},{b,c} and {a},{c} induce the same two-block
set-equality partition, but only the first permits zero-query success. Stopping
requires the intersection over the whole compatible set to be nonempty.
Pairwise compatibility is also insufficient: {a,b},{b,c},{a,c} have nonempty
pairwise intersections and empty joint intersection. [RQR-1–4](RELATIONAL_QUERY_RECONSTRUCTION_THEOREM_V1.md)
constructs the relational extension from common-output feasibility on labelled
subcubes, with a matched joint-profile oracle and an interval-valued positive
repair. Its positive reconstruction is an immediate TDA/LQR corollary; output,
controller and changed-interface costs still require their own register.

## 7. Development and representation are charged separately

The partition is supplied, not learned for free. A dense canonical N=2^n entry
table with k blocks has N ceil(log2 k) class payload bits under this encoding;
its headers, cost/prior rationals and optional output dictionary are additional.
If supplied by enumerating f, all N evaluations and their native verification
work belong to acquisition. No efficient inference of this table is claimed.

The scalar algorithm visits at most 3^n partial states and evaluates at most
n 3^(n-1) first-query choices for n>=1 (zero for n=0). Across all states the
compatible-input count is 4^n. Our simple implementation scans all N inputs per
visited state: at most 6^n membership tests, plus at most 4^n class reads and
prior additions. These are explicit operation categories, not total CPU
instructions or bit-complexity bounds; exact rational arithmetic, validation,
allocation and output-tree construction also cost work. Full-profile synthesis
can be much larger; its child-profile combinations are counted separately.
A declared development accounting can charge each category and input/code
representation before amortizing deployment query work. No bound on controller
memory, code size, physical energy or output writing follows from this theorem.

## 8. Finite evidence and parent comparison

The checker compares reconstructed scalar optima and the *entire pointwise
frontier* with an independent tree-syntax oracle. Before seeing a partition,
that oracle generates every finite no-repeat coordinate tree, including early
stops and gratuitous queries after a class is known. It executes those shapes
on each input, then admits only trees whose leaves can be labelled consistently.
All partitions of cubes n=0,1,2,3 are registered, plus weighted and zero-mass
controls. Injective output renaming, actual synthesized-tree execution and the
selector's incompatible minima challenge the positive reconstruction claim.
The complete finite census is recorded in
[the receipt](GRAND_GMI_QUERY_PARTITION_RECEIPT_V1.json). It checks these authored
finite laws, not unknown empirical semantics or unrestricted kappa/tau.
