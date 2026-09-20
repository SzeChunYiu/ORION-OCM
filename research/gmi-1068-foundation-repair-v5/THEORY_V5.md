# R1/R2 foundation repair V5

This additive successor corrects two universal readings in the historical
R1/R2 theories. It retains their useful conditional constructions and does not
earn whole-round closure. Read FREEZE_V5.md before this document.

## R1-A: exactly when admissibility can be absorbed into Hom

Fix a category C and predicates P(f) on its typed arrows. Keep the same objects,
the same underlying arrows for identities and composites, and equality inherited
from C. Then restricting Hom(A,B) to {f : C(A,B) | P(f)} gives a category with
these inherited operations **if and only if**:

1. P(id_A) for every retained object A.
2. P(f) and P(g) imply P(g composed with f), for every composable pair f,g.

Proof of necessity: the restricted identity must be an element of the relevant
subtype, proving (1). Applying restricted composition to admitted f,g produces
an admitted arrow whose underlying arrow is their C-composite, proving (2).
For sufficiency use the subtype witnesses to define these operations. The
associative and unit equations follow from those in C by subtype extensionality.
This is a wide subcategory construction; no fullness is claimed.

The requirement that operations are inherited matters. An unrelated operation
on the same subset can define a different category and says nothing about
whether physical sequential composition preserves admission. The theorem also
does not infer P, decidability of P, or adequacy of a physical state description.

Counterexamples in the one-object category with arrows natural numbers,
composition addition and identity zero:

- P(n) iff n <= 1 retains identity and the unit-cost arrow, but their twofold
  composition has cost 2 and is excluded.
- P(n) iff n > 0 is composition-closed but excludes identity.

Thus the historical R1 assertion that forbidden arrows can simply be removed
from Hom needs closure assumptions. A fixed per-run resource restriction can
still be used as R3's external history restriction; it need not be a category.
This repairs GMI2-R1-006 and the related R1-001/007/009/010 obligations locally,
with an explicit bridge to GMI2-R3-002.

## R1-B: constructive resource-state revival

Assume a declared cost c from C's arrows to natural numbers, with
c(id)=0 and c(g composed with f)=c(f)+c(g). Form C_c:

- Objects are (A,r), with r the remaining resource.
- An arrow (A,r) -> (B,s) is an underlying f:A->B with r=c(f)+s.
- Identity is the underlying identity. Composition is inherited.

The identity equation follows from zero cost. If r=c(f)+s and s=c(g)+t,
then r=c(f)+c(g)+t=c(g composed with f)+t, so composition is well typed.
Associativity and unit laws again follow by subtype extensionality.
Forgetting balances preserves identities and composition and is therefore a
functor to C. This is a change of configuration objects, not deletion of arrows
at unchanged interfaces.

For any underlying f and initial balance B, there exists a terminal balance s
with B=c(f)+s iff c(f)<=B. Necessity is nonnegativity; sufficiency chooses
s=B-c(f). Therefore projection of outgoing arrows from (A,B) recovers exactly
the original cost-bounded arrows from A, without introducing a replenishment
assumption. In particular a unit-cost run at balance 1 reaches balance 0, where
a second unit-cost run cannot start. The bad untyped concatenation is absent.

The cost law and state adequacy remain premises. Refunds, concurrency,
history-dependent restrictions and several resources require their own declared
state and accounting laws; they are not covered by this natural-number theorem.
For arbitrary prefix-dependent admissibility a full-history state can restore
a transition presentation when allowed prefixes and extensions are given, but
that observation is not a finite-state compression theorem. Non-prefix-closed
acceptance conditions additionally require a terminal acceptance predicate.

## R2-A: scalar aggregation does not require a single prior measure

Fix a finite nonempty context index set and a calibrated real-valued performance
profile v. An aggregate is a declared functional F on its declared profile
domain. Choosing its domain, calibration and comparison rule is context
structure. It does not follow that F must be expectation under a fixed measure.

With two coordinates, F_min(v)=min(v_1,v_2) and F_max(v)=max(v_1,v_2) are both
coordinatewise monotone, invariant under coordinate permutation, and preserve
constant profiles. Yet for p=(2,0), q=(1,1):
F_min(p)<F_min(q), while F_max(p)>F_max(q).
These axioms and the same profiles therefore do not determine a unique ranking.
This is a non-uniqueness countermodel, not a theorem about primitive-symbol count.

Neither functional on all real two-coordinate profiles equals a fixed weighted
sum: on e_1=(1,0), e_2=(0,1), min gives 0,0 but on e_1+e_2 it gives 1.
Linearity would instead give 0. Max gives 1,1 but gives 1 on their sum,
contradicting linearity's 2. A measure selected separately for each profile is
not the fixed measure claimed by that representation.

Both have robust representations using a declared *set* of priors:
min_i v_i = inf_{p in simplex} sum_i p_i v_i and
max_i v_i = sup_{p in simplex} sum_i p_i v_i.
Every convex average lies between the coordinate extremes; concentrating mass
at an extreme attains equality. This does not privilege any single prior.
A worst-case decision rule still declares objectives, a context set and a rule;
lack of a chosen probability prior does not eliminate those assumptions.

## R2-B: exactly where finite probability weights are forced

For n>=1, let F:R^n->R be linear. Then F is coordinatewise monotone and
F(1,...,1)=1 iff there is a unique vector p with p_i>=0 and sum_i p_i=1
such that F(v)=sum_i p_i v_i for all v.

Proof: let e_i be the coordinate basis and p_i=F(e_i). Because e_i>=0 and
linearity gives F(0)=0, monotonicity gives p_i>=0. Linearity and the basis
expansion imply F(v)=sum_i v_i F(e_i); normalization gives sum_i p_i=1.
The basis evaluations also give uniqueness. Conversely a probability-weighted
sum is linear, monotone and normalized by direct substitution.
Without normalization one gets nonnegative finite weights, not necessarily a
probability measure. Infinite index sets require additional domain, convergence,
measurability and representation hypotheses; this proof does not cover them.

Legg-Hutter's environment-weighted definition is one declared specialization,
with its environment class, reward convention and reference machine. Its
existence does not force every aggregation into that form. Historical
GMI2-R2-007/008 and the R2-4 context-schema entry require this successor boundary.
GMI2-R2-006 retains its existing linear/Pareto scope; it does not imply that
nonlinear aggregation is impossible.

## Evidence boundary and parent ownership

AdmissibilityV5.lean kernel-checks the restriction iff theorem, both admission
counterexamples, the resource category, its projected cost bound and exact
existence condition, the empty-balance obstruction, finite ranking reversal and
nonadditivity of natural-number min/max. It imports only Std. The real-vector
linear representation and robust simplex representations above are paper
proofs, not silently claimed as Lean theorems. Finite executable enumeration
tests registered instances; it does not replace either general proof.

These are standard category and finite-dimensional order/linear-algebra
constructions applied to repair GMI's claim placement. Parent mathematics and
the Legg-Hutter specialization remain parent-owned. PARENTS_V5.json records the
primary sources and exact adaptations.

No prior-free optimality, unique ontology, arbitrary physical closure,
all-family intelligence derivation, or complete R0-R17 theory follows.
In the registered DAG, an R1 change reaches R2-R17; an R2 change reaches
R3-R17. Parent bindings must be refreshed and dependent claims reviewed.
This is invalidation of inherited authority, not refutation of every historical
conditional theorem. All original atomic IDs must remain stable.
