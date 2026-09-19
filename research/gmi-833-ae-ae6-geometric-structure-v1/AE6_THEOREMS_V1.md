# AE6 named results

Every result below is stated at the registered finite scope of `FREEZE_V1.md`:
the ambient space is `{0,1}^4` with Hamming distance, the blocks are `{x0,x1}`
and `{x2,x3}`, the union rank cap is 3, the per-block support cap is 2, the
coordinate-permutation group is the symmetric group on the four coordinates with
its full 30-element subgroup lattice, and the description code is the registered
Kraft-compliant integer code. All quantities are exact rationals or integers; no
float appears in any claim. Route A is `ae6_geometric_structure_v1.py`, route B
is `independent_geometry_oracle_v1.py`, and the two agree on every value
recorded here.

Throughout, `architecture class` names one of the frozen exactly-enumerable
model families `M_local[k]`, `M_shared[G]`, `M_modular`, `M_monolithic`. It never
names a network, a layer count or a parameter budget.

## Definition D-AE6 (the six structure predicates)

For a registered source `P` on `{0,1}^4` with support `S` and deterministic
target `Y = t(X)`:

- `LOW_INTRINSIC_DIMENSION` holds when `dim(S) < 4`, where `dim(S)` is the GF(2)
  affine dimension of `S`.
- `UNION_OR_STRATIFICATION` holds when `S` is the union of at most 3 GF(2)
  cosets, each **contained in** `S` and each of dimension at most `k`, for some
  `k` strictly below `dim(S)`. The predicate is monotone in `k`, so only
  `k = dim(S) - 1` has to be tested.
- `SPARSE_COMPOSITIONAL` holds when `S` is the product of its two block supports
  and each block support has at most 2 values.
- `SYMMETRY_ORBIT` holds when some nontrivial subgroup of the
  coordinate-permutation group leaves both `S` and the exact masses invariant.
- `GRAPH_TOPOLOGICAL` holds when the Hamming-1 graph induced on `S` is connected;
  its cycle rank is the parameter.
- `NON_GEOMETRIC_ALGORITHMIC` holds when `S` is the accepting set of the
  registered small Boolean circuit, `dim(S) = 4`, the stabilizer is trivial, and
  the cycle rank lies outside the registered geometric range.

The registered geometric cycle-rank range is `{0, 1, 5, 17}`, derived from the
definition of a coset: a coset of dimension `d` induces a `d`-cube, with
`d * 2^(d-1)` edges on `2^d` vertices and cycle rank `d * 2^(d-1) - 2^d + 1`.

---

## AE6-1 — the six predicates form a hierarchy with an explicit strictness table

**Scope.** The registered 8-source roster on `{0,1}^4`.
**Quantifiers.** All 30 ordered pairs of distinct classes; for each pair, either
a named roster source in the first and not the second, or an explicit statement
that the pair is not separated together with its reason.

Of the 30 ordered pairs, **23** carry a registered witness and **7** are reported
as not separated. Five of the seven have the same cause and one of those five is
proved impossible rather than merely unwitnessed (AE6-2); one is a proved
containment; one is a roster gap that is named as such.

The phrase `data lie on a manifold` is replaced by this table: a source is
described by which of the six predicates it satisfies and by the exact
invariants recorded with it — affine dimension, maximal-coset dimensions, block
support sizes, invariance subgroup count, edge count, component count, cycle
rank and degree sequence.

**Assumptions.** The ambient space, the blocks, the caps and the subgroup
lattice are those frozen in `FREEZE_V1.md`; masses are exact rationals; the
target is deterministic.
**Dependencies.** D-AE6; the exact GF(2) dimension routine; the subgroup lattice
of the coordinate-permutation group; AE6-2 for the reasons attached to the
non-separated pairs.
**Falsifiers.** A registered source whose membership vector differs between the
two routes; an ordered pair reported as separated whose named witness does not
in fact satisfy the first predicate and fail the second; an ordered pair
reported as not separated for which some roster source realizes the pattern.
**Strongest parents.** The manifold hypothesis and intrinsic-dimension
literature (Tenenbaum, de Silva and Langford 2000; Roweis and Saul 2000;
Fefferman, Mitter and Narayanan 2016; Pope and colleagues 2021) and the
union-of-manifolds and stratification literature (Vidal 2011; Brown and
colleagues 2023) own the idea that data support may be low-dimensional or
stratified. Nothing in the idea is claimed here; only the exact finite
instantiation and its machine-checked separation table are this tranche's.

**Forbidden extrapolation.** The table is a statement about eight registered
sources on a 16-point space. It says nothing about real data, about asymptotics,
or about which predicate is common in practice.

---

## AE6-2 — the frozen union predicate is near-universal, and that is why five pairs cannot separate

**Scope.** Every one of the 65535 non-empty supports of `{0,1}^4`.
**Quantifiers.** Exhaustive: the predicate is evaluated on all of them.

Of the **65519** supports of affine dimension at least 1, exactly **65503**
satisfy `UNION_OR_STRATIFICATION` and exactly **16** do not. The 16 exceptions
are precisely the supports of size **15** — the cube with one point removed —
and their coordinate-permutation stabilizers have orders 4, 6 and 24, never 1.

Two consequences follow immediately.

1. No class can be separated *from* `UNION_OR_STRATIFICATION` by a source of
   affine dimension at least 1 unless that source is one of the 16.
2. `NON_GEOMETRIC_ALGORITHMIC` requires a trivial stabilizer, and every one of
   the 16 has a nontrivial one. So `NON_GEOMETRIC_ALGORITHMIC` without
   `UNION_OR_STRATIFICATION` is **impossible** at this scope, not merely absent
   from the roster.

The reading the predicate is meant to carry is recovered by a refinement that
is reported alongside it: the multiset of dimensions of the **maximal** cosets
contained in the support. A single coset has one such dimension; a genuinely
stratified support has at least two. That invariant is what AE6-3 uses.

A companion exhaustive certificate gives the second proved non-separation: over
all **100** supports that are block products with at most 2 values per block,
the maximum affine dimension is **2**, so `SPARSE_COMPOSITIONAL` is contained in
`LOW_INTRINSIC_DIMENSION`, and **0** of the 100 have a trivial stabilizer, which
is why the roster cannot separate `SPARSE_COMPOSITIONAL` from `SYMMETRY_ORBIT`
without non-invariant masses.

**Assumptions.** The frozen predicate is read as `union`, with every piece a
subset of the support, not as `cover`. Under the `cover` reading the predicate
would be weaker still.
**Dependencies.** D-AE6; the exhaustive support census; the permutation
stabilizer computation.
**Falsifiers.** A support of affine dimension at least 1 and size other than 15
that fails the predicate; a size-15 support that satisfies it; a size-15 support
with a trivial stabilizer; a block product with at most 2 values per block whose
affine dimension exceeds 2.
**Strongest parents.** Boolean-function analysis and the affine geometry of
`GF(2)^n` (O'Donnell 2014) own the underlying combinatorics. The observation
that a union-of-manifolds description is weak without a bound on the number and
regularity of the pieces is already present in Vidal (2011) and Brown and
colleagues (2023); the exact count at this scope is what is new here.

**Forbidden extrapolation.** The count `65503 of 65519` is specific to `n = 4`
and to a rank cap of 3. It does not say that union-of-manifolds descriptions are
vacuous in general; it says that at this scope, with these caps, the frozen
predicate carries almost no information and must be refined before it can do
work.

---

## AE6-3 — a learnable distribution that violates a smooth-manifold assumption

**Scope.** The registered source `S_NONMANIFOLD_LEARNABLE` and the registered
rule class `M_local[2]`.
**Quantifiers.** One exhibited source; three independent certificates; one exact
accuracy.

The support is the union of a dimension-2 coset and a dimension-1 coset meeting
in exactly one point. Three exact certificates say it is not a manifold at this
scope:

1. the Hamming-1 degree sequence is `[1, 2, 2, 2, 3]`, so the local
   neighbourhood size is not constant;
2. the maximal cosets contained in the support have two distinct dimensions,
   `{1, 2}`;
3. the two registered pieces have different dimensions and intersect, so the
   local dimension jumps at the meeting point.

On this source the target `x0 XOR x2` is attained by a member of `M_local[2]` at
exact accuracy **1**, at integer cost **13** bits.

**Assumptions.** `Manifold` is read at the registered scope as `constant local
dimension`, made exact by the induced Hamming-1 degree sequence and by the
maximal-coset dimensions; there is no continuum limit here and none is claimed.
**Dependencies.** D-AE6; AE6-2 for the maximal-coset invariant; the exact
accuracy computation over the registered rule class.
**Falsifiers.** A constant degree sequence; a single maximal-coset dimension; a
member of `M_local[2]` scoring below 1; a smaller-cost member of another
registered class matching it.
**Strongest parents.** Stratified and union-of-manifolds data models (Vidal
2011; Brown and colleagues 2023) own the claim that real supports need not be
single smooth manifolds. This result contributes only the exact finite witness
and the three machine-checked certificates.

**Forbidden extrapolation.** Learnability here means exact accuracy 1 for one
member of one registered finite rule class at one integer budget. It is not a
sample-complexity statement and not an optimization statement.

---

## AE6-4 — low dimension is neither statistically nor causally sufficient, and the literal conjunction is unsatisfiable

**Scope.** All supports of `{0,1}^4` for the impossibility half; the registered
source `S_LOWDIM_USELESS` and the repaired composite witness for the positive
half.
**Quantifiers.** Exhaustive over 480 dimension-1 cases and over 34112 cases of
support size at most 4; one exhibited composite witness.

*The register's gloss is met exactly.* `S_LOWDIM_USELESS` has support inside a
GF(2) coset of dimension **1**, exact mutual information **0** bits with the
target, and exact interventional effect **0**.

*The added clause of prediction `AE6-P3` cannot be met, by any source.* Two
independent obstructions:

1. For a deterministic target, exact zero mutual information with the input
   forces the target to be constant on the support. A constant target is not
   equal to any coordinate or its complement on a coordinate that varies, so no
   coordinate determines it in the non-vacuous sense. This obstruction does not
   mention dimension at all. It is checked exhaustively on **34112** cases of
   support size at most 4, with **0** violations.
2. Affine dimension 1 forces a support of exactly two points. On two points any
   coordinate taking both values determines the target exactly, hence carries
   strictly positive information, contradicting the zero-information clause.

The conjunction is therefore reported `REFUTED`, with **0** of the **480**
(support, target) pairs at dimension 1 satisfying it.

*Row 3 is closed on the repaired composite witness.* Its support factorizes
exactly as `L (+) T`, where `L` is a GF(2) factor of dimension **1** on block
`{x0,x1}` and `T` is a factor of dimension **2** — full dimension in its block —
on `{x2,x3}`, and the measure is an exact product measure. Then:

- exact mutual information between `L` and the target: **0** bits;
- exact interventional effect of `L` on the target: **0**;
- best accuracy of any rule reading `L` alone: **1/2**, exactly the base rate;
- best accuracy of a single coordinate of `T`: **1**, with interventional
  effect **1**.

A maximally low-dimensional structure is therefore exactly useless on both the
statistical and the causal channel while the task is solved exactly by the
full-dimension part.

**Assumptions.** The structural model is the registered one: the two blocks are
exogenous and independent, the target is a deterministic function of the
coordinates, and `do` acts by setting a block or a coordinate. Mutual
information is in bits and is exact because the zero case is a finite rational
identity.
**Dependencies.** D-AE6; the exact product-measure test; the exhaustive
dimension-1 certificate; the exhaustive zero-information identity.
**Falsifiers.** A dimension-1 support and deterministic target satisfying the
full conjunction; a case at support size at most 4 where zero mutual information
and a constant target come apart; a nonzero exact interventional effect for the
composite witness's dimension-1 factor; a rule reading that factor alone scoring
above the base rate.
**Strongest parents.** Pearl's do-calculus owns the interventional notion;
Shannon's mutual information owns the statistical one. The warning that
dimension alone does not imply task relevance is implicit in Pope and colleagues
(2021). What this result adds is the exact finite pair — a gloss-faithful
witness and a repaired composite witness — plus the machine-checked proof that
no single source can carry the whole conjunction.

**Forbidden extrapolation.** This refutes a sufficiency claim, not a usefulness
claim. It does not say low-dimensional structure is generally useless; it
exhibits one exact case where it is, which is enough to break the implication.

---

## AE6-5 — when locality should favour a local operator, and when it should not

**Scope.** The registered derivation worlds `D_LOCAL_POS` and `D_LOCAL_NEG`, the
named class `M_local[2]` at integer cost **13** bits, and the comparator
`M_monolithic` at the same integer budget.
**Quantifiers.** One condition, one positive world, one matched failure world.

*Condition (exact).* Some 2-subset of coordinates determines the target exactly
on the support, that is `max over 2-subsets J of acc_J = 1`.

*Positive.* On `D_LOCAL_POS` the condition holds, `M_local[2]` attains exact
accuracy **1** at cost 13 bits, and the comparator at the same budget attains at
most **7/8**. At that budget the monolithic branch admits at most one term, and
the best single term is a coordinate.

*Matched failure.* On `D_LOCAL_NEG`, the uniform cube with the conjunction of
all four coordinates as target, the condition fails: the best 2-subset attains
**15/16 < 1**. There `M_local[2]` attains **15/16** while the comparator at the
same budget of 13 bits attains exactly **1**, because the conjunction is a
single term. The named class is strictly worse, with exact accuracy drop
**1/16**.

The condition is therefore falsified on the roster and the derivation is not an
`UNFALSIFIED_CONDITION`.

**Assumptions.** Cost is the integer description length under the registered
Kraft-compliant code; accuracy is exact rational; the comparator is evaluated at
the same integer budget, never at a larger one.
**Dependencies.** D-AE6; the registered code and its Kraft certificate (AE6-8);
the exact accuracy computation over every registered class.
**Falsifiers.** A member of `M_local[2]` scoring below 1 on the positive world; a
monolithic description within 13 bits scoring above 7/8 there; a 2-subset
determining the target on the failure world; the named class not being strictly
worse on the failure world.
**Strongest parents.** Locality and weight sharing in convolutional models
(LeCun, Bottou, Bengio and Haffner 1998) and the junta literature in Boolean
analysis (O'Donnell 2014) own the underlying idea that a target depending on few
coordinates is cheap to describe. The residual here is the exact
condition-plus-matched-failure pair at a shared integer budget.

**Forbidden extrapolation.** This is a statement about two registered worlds at
one integer budget under one code. It is not a law about when convolutional
architectures win.

---

## AE6-6 — when symmetry should favour parameter sharing, and when it should not

**Scope.** The registered derivation worlds `D_SYM_POS` and `D_SYM_NEG`, the
named class `M_shared[SymN]` at integer cost **12** bits, and the comparator
`M_monolithic` at the same integer budget.
**Quantifiers.** One condition, one positive world, one matched failure world.

*Condition (exact).* The source measure and the target are invariant under the
registered subgroup, checked against every element of the group.

*Positive.* On `D_SYM_POS` — the uniform cube with the weight threshold at 3 as
target — the condition holds and `M_shared[SymN]` attains exact accuracy **1** at
cost **12** bits. The unshared class, the shared family over the trivial
subgroup, costs **23** bits with **16** orbits; the shared class has **5**
orbits. The cost reduction is exactly **11** bits, exactly equal to the orbit
count reduction **16 - 5 = 11**, which is the register's prediction stated as an
identity rather than an inequality. The comparator at the same budget of 12 bits
attains at most **13/16**; the best local class inside that budget attains
**11/16**.

*Matched failure.* On `D_SYM_NEG` — the uniform cube with a single coordinate as
target — the condition fails, because a single coordinate is not invariant under
the group. There `M_shared[SymN]` attains **11/16**, obtained by the orbit rule
that predicts 1 above the weight threshold, while the comparator at the same 12
bits attains exactly **1**, because a single coordinate is a one-term
description. Exact accuracy drop **5/16**.

**Assumptions.** Invariance is exact and is required of the measure and of the
target, not only of the support. Orbit averaging is realized here as the
restriction to functions constant on orbits; that restriction is exactly the
projection onto the invariant subspace.
**Dependencies.** D-AE6; the full subgroup lattice; the registered code; the
orbit partition.
**Falsifiers.** An invariant function scoring above the reported optimum on the
positive world; a cost reduction different from the orbit reduction; an
invariant function scoring above 11/16 on the failure world; a monolithic
description within 12 bits scoring above 13/16 on the positive world.
**Strongest parents.** The exact generalization benefit of equivariance is
parent-owned. Elesedy and Zaidi (2021) prove that for an invariant target the
orbit-averaging projection strictly reduces risk, with the reduction equal to
the norm of the component of the predictor orthogonal to the invariant subspace;
group-equivariant networks and their weight sharing are owned by Cohen and
Welling (2016), LeCun and colleagues (1998) and the geometric deep learning
programme (Bronstein, Bruna, Cohen and Velickovic 2021).

What is parent-owned: that projecting onto the invariant subspace cannot hurt
when the target is invariant, and that it strictly helps when the predictor has
a non-invariant component. What is this tranche's residual: the *cost* side made
exact and integer — the identity `cost reduction = orbit count reduction = 11`
under a named Kraft-compliant code — together with the matched failure in which
the same projection costs exactly `5/16` of accuracy because the condition is
false. Elesedy and Zaidi bound the benefit under the invariance hypothesis; they
do not price the hypothesis being wrong, which is what the failure half does
here.

**Forbidden extrapolation.** Nothing here licenses
`SYMMETRY_ALWAYS_JUSTIFIES_PARAMETER_SHARING`. The failure world is the
counterexample: sharing under a group the target does not respect is strictly
worse at the same budget.

---

## AE6-7 — when compositional latent factors should favour a modular representation, and the comparator that provably cannot show otherwise

**Scope.** The registered derivation worlds `D_COMP_POS` and `D_COMP_NEG`, the
named class `M_modular` at integer cost **14** bits, and two comparators at that
budget.
**Quantifiers.** One condition, one positive world, one matched failure world,
one exhaustive containment certificate.

*Condition (exact).* The target factorizes through the registered blocks as
`g(h1(B1), h2(B2))` with one-bit block summaries. Equivalently the 4-by-4 block
value matrix of the target has at most two distinct rows and at most two
distinct columns; route B decides membership that way.

*Positive.* On `D_COMP_POS` — the uniform cube with target
`(x0 AND x1) XOR (x2 OR x3)` — the condition holds, `M_modular` attains exact
accuracy **1** at cost **14** bits, and `M_monolithic` at the same budget attains
at most **5/8**. Inside that budget `M_local[2]` attains **3/4** and the best
shared class attains **3/4**, so the modular class is uniquely optimal there.

*The monolithic comparator cannot produce the matched failure, and this is
proved.* At a budget of 14 bits the monolithic branch admits at most one term.
There are exactly **17** such functions and **every one of them is already a
member of `M_modular`**, because a one-term description is a conjunction of
literals and a conjunction factorizes across the blocks. So `M_modular` is at
least as accurate as that comparator on **every** source, and no world can make
it strictly worse. The containment is sharp: it fails at one more term. The
modular class itself has **520** distinct members.

*Matched failure, against a comparator that is not contained in the class.* On
`D_COMP_NEG` — the uniform cube with the weight threshold at 3 as target — the
condition fails: the best modular member attains **7/8 < 1**, because one bit per
block cannot separate the three possible block weights. `M_shared[SymN]`, which
costs **12** bits and is therefore inside the same budget of 14, attains exactly
**1**. The named class is strictly worse, with exact accuracy drop **1/8**.

**Assumptions.** The block decomposition is the registered one; a block summary
is one bit; cost is integer description length under the registered code; the
failure comparator must lie inside the same integer budget.
**Dependencies.** D-AE6; the registered code (AE6-8); the exhaustive modular
membership enumeration; the exhaustive monomial-count table.
**Falsifiers.** A modular member scoring above 7/8 on the failure world; a
one-term monolithic function that is not modular; a shared class inside 14 bits
scoring below 1 on the failure world; a modular member scoring below 1 on the
positive world.
**Strongest parents.** Depth and compositionality separations (Poggio, Mhaskar,
Rosasco, Miranda and Liao 2017; Telgarsky 2016) own the claim that hierarchically
composed targets are cheaper for compositional models than for flat ones. This
result contributes the exact finite instance, the shared integer budget, and the
containment certificate that identifies which comparator the argument may use.

**Forbidden extrapolation.** The containment result is a fact about this code at
this budget. It does not say monolithic models are generally weaker; it says
that at 14 bits under this code the monolithic branch is a subset of the modular
one, so an honest matched failure has to be stated against a different
comparator.

---

## AE6-8 — the bound ledger, the hostiles and the null

**Scope.** Every threshold this package states, the five registered hostiles,
and the registered 200-trial null.
**Quantifiers.** Ten bound records; five hostiles; 200 trials.

*Bounds.* Ten records are emitted. Each carries `kind`, `bound_value`,
`range_lo`, `range_hi`, a `range_derivation` that derives both endpoints from
the definition of the bounded quantity and never from the roster's values, a
computed `vacuous` flag, a separate `attained_by` witness, and a `violated_by`
witness drawn from an explicitly relaxed class. **None** is vacuous and **none**
is `UNFALSIFIED_BOUND`. Attainment is recorded and is not treated as evidence of
non-vacuity.

The registered description code is Kraft-compliant with exact sum
`1372503309540478908673/2361183241434822606848`, and the bound `<= 1` is falsified
by the explicitly relaxed code that drops the self-delimiting term-count field,
whose exact sum is `90031258052692244737/73786976294838206464 > 1`. The
accuracy bounds are falsified by widening the named class: `M_local[4]` breaks
the locality bound, a strictly smaller subgroup breaks the symmetry bound, and a
two-bit block summary breaks the modular bound. The two row-3 bounds, both `0`,
are falsified by the relaxed companion source in which the same dimension-1
factor does carry the target, giving exactly `1` bit and interventional effect
exactly `1`.

*Hostiles.* Five, each asserted potent before it is asserted detected:
a rank routine capped at 2 pivots moves a dimension from **4** to **2**;
dropping the mass-invariance clause moves an invariance verdict from **false**
to **true**; a leaked block split moves a modular accuracy from **3/4** to
**1**; an inflated monolithic budget moves a comparator accuracy from **5/8** to
**1**; and moving one support point moves a cycle rank from **1** to **2**. Each
is then detected, by route B recomputation, by comparison against the registered
blocks, or by comparison against the registered integer cost.

*Null.* The detector is the row-3 conjunction. It is run on **200** randomized
tasks over random block geometry drawn by a registered integer generator whose
parameters are implementation constants outside the register, fixed before the
first run and unchanged since. It fires on **3** of the 200; every firing trial
is listed individually with its exact mutual information, interventional effect
and block accuracies, and every one is a genuine instance of the same
phenomenon, so the rate is a reproducibility rate rather than a false-alarm
rate. The detector does **not** fire on the clean registered witnesses, which is
asserted separately. The magnitude `accuracy on the full-dimension block minus
accuracy on the low-dimension block` is bounded above by `1 - base rate <= 1/2`
by definition, and the planted witness attains that definitional maximum `1/2`,
so a strictly-exceeds-the-largest-null comparison is structurally impossible for
this quantity; that is stated plainly and the exact firing rate is the primary
comparison.

**Assumptions.** Ranges are read off the definitions of the bounded quantities:
an accuracy is a probability, a class containing the constant functions attains
at least the base rate, mutual information with a binary target is at most one
bit, an interventional effect is a difference of probabilities, a cycle rank is
non-negative and at most `32 - 16 + 1` on this cube, and a Kraft sum of a finite
description set is non-negative and at most half the description count.
**Dependencies.** All of AE6-1 through AE6-7 for the quantities being bounded;
the registered code for the Kraft records; the registered generator for the null.
**Falsifiers.** A bound whose `violated_by` object does not in fact break it; a
`vacuous` flag disagreeing with the recomputation from `bound_value`,
`range_lo`, `range_hi`; a hostile whose perturbed value equals its true value; a
firing null trial that is not a genuine instance; the detector firing on a clean
registered witness.
**Strongest parents.** Kraft's inequality and the Shannon code-length framework
own the description-code side; standard permutation-null practice owns the null
design. Nothing here is claimed novel against either.

**Forbidden extrapolation.** The null is over a registered synthetic family. It
gives no evidence about how often the row-3 phenomenon arises in real data, and
the prospective real-dataset row of the issue comment is explicitly left open.
