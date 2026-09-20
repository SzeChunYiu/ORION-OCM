# R5 successor: costs, minima and transport

Freeze: `3a56e2d1fe83909a9fb9bed10dbd8d14d32d2b65`.
This repairs specific R5 claims and leaves whole-round closure OPEN because R4
and the broader parent-bridge audit have not been re-earned. It does not rewrite
`gmi-1068-r5-resource-transform-geometry-v1`.

## G1. Scalar distance with attainment

Let objects have composable processes, identities, and costs c(f) in [0,infinity).
Assume c(id)=0 and c(g∘f)≤c(f)+c(g). For a nonempty process set with an attained
minimum define d(a,b)=min{c(f):f:a→b}; for an empty set define d(a,b)=infinity.
Assume these minima exist whenever used. Nonnegativity and the identity witness
imply d(a,a)=0. If f and g attain d(a,b) and d(b,c), their composite is admissible,
so d(a,c)≤c(g∘f)≤d(a,b)+d(b,c). If either leg is unreachable the extended-real
inequality holds trivially. Symmetry and separation of different objects do not
follow: a zero-cost nonidentity process is permitted.

The Lean artifact proves identity and triangle for natural-number costs using
actual witnesses and minimization over every admissible process. It does not
assume the conclusion. Minimality of the two legs is only needed to interpret
those costs as distances, not for the stronger candidate-wise bound.

## G2. Infima without attainment

For arbitrary process sets use infimum in [0,infinity], with inf(empty)=infinity.
Identity is as above. If both leg infima are finite, for each epsilon>0 choose
f,g costing less than their respective infima plus epsilon/2. Composition gives
d(a,c)<d(a,b)+d(b,c)+epsilon. Let epsilon decrease to zero. The other cases are
trivial. This establishes a directed extended pseudometric, without promising a
minimum-cost process. This is a paper proof; the Lean bundle does not cover reals.

## G3. Pareto sets are not existence certificates

For an attainable vector-cost set V⊆[0,infinity)^d, define its feasible upper set
U(V)={b:some v∈V satisfies v≤b}. Define Min(V) by no strictly dominating member.
Min(V) can be empty when V is nonempty. For V={1/n:n≥1}, every element is
strictly dominated by 1/(n+1), inf(V)=0 is unattained, and U(V)=(0,infinity).
Thus empty Min(V) must never be relabeled UNREACHABLE. A finite nonempty V has a
minimal element and every member dominates a minimal element (finite descent).
For nonempty compact V, minimizing sum_i v_i on compact V proves existence;
for each x∈V do so on V∩{v:v≤x} to prove coverage below x. Compactness is
sufficient, not necessary; unbounded and noncompact sets require separate facts.

Scalarization also loses information. In V={(0,2),(1,1),(2,0)}, weights (1,0)
select only (0,2). In V={(0,2),(1,3/2),(2,0)}, the middle point is Pareto minimal
but minimizes no strictly positive linear weighting. Therefore a scalar optimum
is not the entire multiobjective frontier. Nonnegative weights may even tie
strictly dominated points when zero-weight coordinates are ignored.

## G4. Exact transport with hypotheses

Let B:P→P' be a bijection between feasible process sets, preserving the declared
context responses (including legality/undefinedness as distinct semantic cases).
Let φ:V→V' be an order isomorphism of attainable costs, with c'(B(p))=φ(c(p)).
Then v is minimal in V iff φ(v) is minimal in V'. Proof: a strict dominator on
either side pulls back/pushes forward to a strict dominator, a contradiction.
This holds even for infinite V and empty frontiers; it does not establish
existence of a minimal or infimum-attaining element. The Lean theorem proves the preorder version (minimal modulo
mutual comparison) from an order-reflecting surjection. Finite tests independently
rename graph nodes and transform coordinates; they also alter costs while
preserving node names, which must fail transport.

A merely monotone map need not reflect strict domination: projecting (0,1) and
(1,0) to the first coordinate destroys one frontier point. Mere injectivity,
lexical renaming, or a fixed cost vector copied twice does not prove transport.
Preservation of resource tests is an extra contextual-equivalence requirement.
No corrected R4 result is assumed by these stand-alone conditional theorems.

## G5. Finite operational check and ownership

The executable compares Floyd–Warshall minima with independent exhaustive simple
path enumeration for all 4096 three-node directed graphs whose six off-diagonal
edges are absent or cost 0,1,2. Nonnegative cycles can be deleted without raising
cost; thus simple paths suffice here. Every ordered source/target pair and
triangle is checked. Separate negative controls exercise negative edges,
miscomputed composition, unreachable directions, changed cost and nonreflecting
projection. Infinite claims rest on G2/G3 proofs, not sampled 1/n values.

Resource convertibility and ordered combination are inherited mathematics:
Tobias Fritz, *Resource convertibility and ordered commutative monoids*,
[arXiv:1504.03661v2](https://arxiv.org/abs/1504.03661v2), Definitions 2.1 and 3.1
(the ordered/preordered commutative-monoid setup; do not infer our exact
cost-of-morphism hypotheses from object convertibility alone).
The contribution here is repairing the GMI application and its verification,
not claiming a new general resource or shortest-path theorem.

## Claim ceiling

CONDITIONAL_RESOURCE_GEOMETRY_WITH_EXACT_FINITE_CHECKS; R5 remains OPEN.
No unique metric, Pareto attainment in all spaces, physical cost validation,
architecture emergence, or complete GMI follows.
