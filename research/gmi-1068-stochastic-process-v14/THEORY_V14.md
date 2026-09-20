# Finite stochastic and nondeterministic process instances

Read [FREEZE_V14.md](FREEZE_V14.md). These are classical process categories and
registered counterexamples, not an empirical discovery. Execute A first, then B;
write their composite A;B. Objects include the empty finite set.
Let S be a nonnegative-weight carrier: an additive commutative monoid with 0,
associative unital multiplication, both distributive and zero laws, and 0≠1.
For support results also require a+b=0 iff a=b=0, and ab=0 iff a=0 or b=0.
These are primitive scalar assumptions, not assumed matrix/category conclusions.
Nonnegative rationals and nonnegative reals satisfy them by their ordinary laws.
The abstract interface has no order; nonzero is equivalent to positive only
in these declared ordered specializations. Multiplication need not commute.

## N1-A — normalized finite matrices form a category

For finite X,Y, an S-kernel A:X→Y is a matrix with Σ_y A(x,y)=1 for every x.
For S=Q_nonnegative or R_nonnegative this means precisely nonnegative entries
and row sums one. Define `(A;B)(x,z)=Σ_y A(x,y)B(y,z)` and let I_X(x,x')
be 1 when x=x' and 0 otherwise. All entries remain in S.
Finite-sum distributivity follows by induction from scalar distributivity;
swapping two finite sums follows from additive associativity and commutativity.
Consequently, for every x,

`Σ_z (A;B)(x,z) = Σ_y A(x,y)(Σ_z B(y,z)) = Σ_y A(x,y) = 1`.

Identity normalization is the sum of one 1 and zeros for every x. Expanding
either identity composite leaves exactly the term at its matching index.
For A:X→Y, B:Y→Z, C:Z→T, both parenthesizations have entry
`Σ_y Σ_z A(x,y)B(y,z)C(z,t)`: distribute, reassociate products and interchange
the finite sums. Thus identities and associativity are proved, not postulated.
There is exactly one matrix 0→Y, with no entries. For nonempty X there is no
kernel X→0: each empty row sums to 0, contradicting normalization and 0≠1.
These cases are included in the category; dimensions cannot be inferred solely
from an empty array. All statements transport along finite-set enumerations.

**Assumptions.** Finite index sets; the stated semiring laws; row normalization.
**Dependencies.** Finite-sum induction, distributivity and reindexing; no support axioms needed.
**Falsifiers.** A reversed multiplication convention, failed normalization, omitted empty dimensions or a matrix law inserted as a scalar premise.
**Strongest parents.** [Fritz Examples2.5 and8.2](https://arxiv.org/html/1908.07021v8); standard stochastic matrices and semiring matrices, parent-owned.

## N1-B — total relations form a category

For arbitrary types X,Y, a total relation R:X→Y is R⊆X×Y with
∀x∈X,∃y∈Y,R(x,y). Define `(R;T)(x,z)` iff ∃y,R(x,y) and T(y,z).
Given x, totality first gives y and then z, proving composition total.
Equality is the identity relation. Substituting equal endpoints proves both
unit laws. Both bracketings of R;T;U hold exactly when there exist y,z with
R(x,y), T(y,z), U(z,w); regrouping these witnesses proves associativity.
No choice of a simultaneous selector is needed for this pointwise argument.
The empty source gives a unique total relation; a nonempty source admits no
total relation into the empty target. Totality excludes dead ends: arbitrary
possibly empty-output relations instead form the larger ordinary relation category.
No probabilities, independence assumptions or transition frequencies are implied.

**Assumptions.** Relations with explicit source/target types and pointwise totality.
**Dependencies.** Equality, conjunction and existential witness manipulation.
**Falsifiers.** An empty output set accepted for an inhabited source, or a wrongly typed middle witness.
**Strongest parents.** [Fritz Examples2.6 and3.3](https://arxiv.org/html/1908.07021v8), finite multivalued maps/nonempty powerset; the same elementary relational proof works for arbitrary types.

## N1-C — faithful deterministic embeddings

For f:X→Y on finite sets, define D_f(x,y)=1 if y=f(x), else 0. Its row sum
is one. D_id=I and `(D_f;D_g)(x,z)=D_g(f(x),z)=D_(g∘f)(x,z)`.
If D_f=D_g then their entries at (x,f(x)) agree for every x. Since 1≠0,
g(x)=f(x); thus f=g, including the vacuous empty-source case.
The graph relation G_f(x,y) iff y=f(x) is total on arbitrary types. Equality
gives G_id, and the unique intermediate value f(x) gives G_f;G_g=G_(g∘f).
Equality of graphs implies equality of functions by evaluating at (x,f(x)).
Thus both embeddings preserve identities/composition and are faithful.
An S-kernel whose every row has exactly one nonzero entry is Dirac: normalization
forces that entry to equal one. Conversely every Dirac row has that support.
In ordinary rational/real probabilities, a normalized {0,1}-valued row has
exactly one 1. This last assertion is not made for every abstract S: Boolean
addition is idempotent and permits several 1s in a normalized row.

**Assumptions.** Functions with declared endpoint types; finite sets for matrix sums; 0≠1.
**Dependencies.** N1-A/N1-B, indicator-sum elimination and function extensionality.
**Falsifiers.** Collapsed 0=1, lost source types, or claiming Boolean-semiring normalization implies single-valued support.
**Strongest parents.** [Fritz Examples2.5 and10.3](https://arxiv.org/html/1908.07021v8); deterministic inclusions are classical, with finite-state interpretation stated explicitly.

## N1-D — support is a functor under explicit scalar hypotheses

First prove by induction that a finite sum equals zero iff every summand equals
zero. The empty sum gives both sides vacuously; the step uses a+b=0 iff a=b=0
and the induction hypothesis. Negating gives a nonzero sum iff some term is
nonzero (classical logic suffices). Combining with ab=0 iff a=0 or b=0 yields

`Σ_i a_i b_i ≠ 0  iff  ∃i, a_i≠0 and b_i≠0`.

For nonnegative rational/real entries this is also the finite-sum positivity
statement: a sum of nonnegative terms is positive iff some term is positive,
and a product is positive iff both factors are positive. It uses the primitive
ordered scalar facts; no matrix-support conclusion is assumed.
Define supp(A)(x,y) iff A(x,y)≠0. A normalized row has a nonzero entry because
its sum is 1≠0; hence supp(A) is total. The displayed equivalence gives
supp(A;B)=supp(A);supp(B). Since 1≠0, supp(I)=equality and supp(D_f)=G_f.
Thus support preserves identities/composition. It need not be faithful, as N2 shows.

The assumptions matter. Over signed rationals take A=(1/2,1/2) and
B=((1,0),(-1,2)). Both row sums remain one, but A;B=(0,1): a nonzero path
to the first output cancels. Removing nonnegativity invalidates support transport.
To isolate zero divisors without cancellation, use S=N×N with componentwise
operations. Put u=(1,0),v=(0,1),1=u+v. A=(u,v), B=((v,u),(0,1)) have
normalized rows but the first composite entry uv+v0 is zero despite a supported
path. This S is zero-sum-free but has zero divisors. The registered modular
control also exhibits zero-divisor failure; modular arithmetic additionally
allows additive cancellation, so it does not isolate that assumption by itself.

**Assumptions.** N1-A plus zero-sum-free addition and no zero divisors; 0≠1.
**Dependencies.** Derived finite-sum support equivalence, scalar product support and row normalization.
**Falsifiers.** Signed cancellation, zero divisors or numerical thresholding that erases a tiny positive rational.
**Strongest parents.** [Fritz Examples2.5–2.6 and8.2](https://arxiv.org/html/1908.07021v8) supply the matrix/relation constructions; the Boolean support homomorphism is their elementary algebraic connection, not GMI novelty.

## N2 — a closed seven-arrow rational process category

On B={false,true}, let I be identity, F the flip matrix, and K_p the matrix
with both rows (1-p,p), for p in P={0,1/3,1/2,2/3,1}. These seven matrices
are nonnegative and normalized. All compositions are fixed by identity and

`F;F=I`, `K_p;K_q=K_q`, `F;K_p=K_p`, `K_p;F=K_(1-p)`.

For K_p;K_q, each output probability is q times the total incoming mass, or
(1-q) times that mass. Flip on the input merely exchanges equal rows; flip
on the output exchanges the two probabilities. P is closed under p↦1-p,
so these equations prove closure. Category laws follow from actual matrix laws;
the finite kernel model additionally checks the actual rational operations.
The interpretation is faithful: I and F have unequal rows, every K_p has equal
rows, I differs from F at (false,false), and distinct K_p differ at their
true-output entry p. The four deterministic arrows are I,F,K_0,K_1.
K_(1/3) and K_(2/3) have identical full supports but distinct probability of
{true}, namely 1/3 and 2/3, from either input. Support therefore loses event
probabilities even inside a closed finite category. This is not a label-only test.
The frozen calibration grid over dimensions 0,1,2 is not this closed category:
its composites may leave the grid and must be retained exactly.

**Assumptions.** Ordinary exact rational arithmetic and the displayed actual matrices.
**Dependencies.** N1-A; explicit matrix entries and seven-arrow composition equations.
**Falsifiers.** An out-of-family composite, equal interpreted matrices for distinct labels, or support equality hiding an untested probability claim.
**Strongest parents.** [Fritz Example2.5](https://arxiv.org/html/1908.07021v8); the seven-arrow witness is a registered concrete instance of classical finite stochastic processes.

## N3 — uniformization does not preserve relational composition

For each finite total relation, assign equal probability to every permitted
output in each row. This gives a kernel with the same support, but not a functor.
Take R from one source to two outputs a,b, both permitted. Let T permit only x
from a, and y,z from b. Uniformize separately: the composite probabilities are
(1/2,1/4,1/4). R;T permits x,y,z, whose uniformization is (1/3,1/3,1/3).
They differ, although their supports agree. Thus this proposed canonical
probability assignment does not respect sequential composition. No conclusion
about every possible assignment or functorial section is asserted.

**Assumptions.** Finite nonempty relation rows, ordinary rational uniformization and the stated typed relations.
**Dependencies.** N1-B and ordinary multiplication of the displayed row probabilities.
**Falsifiers.** Different composite distributions accepted as equal, reversed execution order, or replacing distribution equality with support equality.
**Strongest parents.** [Fritz Examples2.5–2.6](https://arxiv.org/html/1908.07021v8); this elementary counterexample tests a proposed bridge, not a new probability law.

## Evidence and authority boundary

Generic Lean matrix laws quantify over the full Weight interface, including
support hypotheses unused by those matrix-law proofs; N1-A gives the sharper
ordinary-semiring paper theorem. Arbitrary rational/real instances of Weight
remain paper specializations. N1-C's exactly-one-support converse is also
paper-only; the kernel registers forward Dirac construction and faithfulness. A concrete Nat instance
establishes consistency but admits only deterministic normalized rows. The separate
seven-arrow model uses actual Std.Internal.Rat entries and supplies nontrivial
kernel-checked probability. Consult FORMAL_SCOPE_V14 for exact registered coverage.
The finite executable oracle is separate from Lean, not a certified extraction.
This round formalizes optional instances inside the sequential framework. It does
not derive a unique probability law, eliminate useful stochastic modelling, prove
all measure theory, infer a prior or recover every intelligence architecture.
Only GMI2-R1-008 is eligible for closure after the registered evidence gates pass.
