# Z4 — six optional rows and their different proofs

The immutable source is R1 IRREDUCIBILITY_V1.json, section
removed_from_universal_minimum. Its ceiling is relative to registered universal
requirements, not a unique ontology. [OPTIONAL_LEDGER](OPTIONAL_LEDGER_V26.json)
preserves all six component/status pairs in order. Nonnecessity of an independent
field does not imply recoverability of every enriched observation after erasure.

## Tensor and symmetry

V13's one-object reset category has exactly three arrows: identity e and resets z0,z1. Execute f then g. Resets satisfy z0;z1=z1 and
z1;z0=z0, so composition is noncommutative. Only e is invertible: any composite
with a reset is constant. Suppose any monoidal structure exists on this unchanged
category. Both unitors are invertible and hence e. Their naturality forces the
tensor's left and right unit to be e; bifunctoriality supplies interchange.
The Eckmann–Hilton substitutions then identify tensor with composition and make it
commutative, a contradiction. The universal tensor quantifier is earned by necessary
laws; failure of one proposed tensor would not suffice. Standard-monoidal-to-necessary-
data extraction retains V13's paper boundary. The actual category is wrapped in V11.

For symmetry use V13's category with reset-monoid objects and a C2 loop at each
object, with no cross-object arrows. Object tensor is monoid multiplication and
arrow tensor is XOR; XOR interchange and zero structural arrows give the registered
coherence laws. A braiding between z0⊗z1 and z1⊗z0 would need an arrow between
distinct objects, impossible. This is a lawful nonbraided chosen tensor with genuine
nonidentity arrows. It does not rule out alternative tensors on the same category.
Parents: [Riehl Appendix E.2](https://emilyriehl.github.io/files/context.pdf) and
[Baez's Eckmann–Hilton discussion](https://math.ucr.edu/home/baez/week258.html), as mapped in V13.

## Probability and nondeterministic choice

Finite sets and actual functions form a category by ordinary composition, including
empty finite sets. Its sequential observer needs no separate probability/choice
field. V14 additionally constructs genuine normalized-matrix and total-relation
categories; adapting their actual operations to V11 makes them instances of the
same sequential interface without discarding the rich arrows.
Dirac maps and function graphs preserve identities/composition and are faithful.
The V14 finite-sum and existential-witness proofs supply these facts; they are
not assumed merely because a record is named Category. Matrix signatures use
V14's full Weight interface, including support hypotheses unnecessary for some laws.
Ordered Real/Rat interpretations remain paper-level; the concrete seven-arrow
model uses actual rational operations and supplies nontrivial probabilities.

In that model K_(1/3) and K_(2/3) have identical supports but different event
probabilities. Thus support can preserve sequential composition and still lose
information. Relation branches similarly remain part of the arrows. Uniformizing
R={a,b}, T(a)={x}, T(b)={y,z} before composition gives (1/2,1/4,1/4), whereas
uniformizing the composite gives (1/3,1/3,1/3). This refutes that particular section,
not every possible probability assignment or selector. No prior is inferred.
Primary parent: [Fritz Examples2.5,2.6,8.2,10.3](https://arxiv.org/html/1908.07021v8), with V14's exact finite versus general interpretation boundaries.

## Higher cells: the locally discrete construction

For any actual C, retain its objects and arrows. For parallel arrows f,g put
Two(f,g)=PLift(f=g). Vertical identities are lifted reflexivity and composition
is lifted transitivity. Equality induction proves the local category laws.
Horizontal composition sends p:f=f' and q:g=g' to congrArg2(comp) p q.
It preserves identity2-arrows and vertical composition, again by equality induction;
this proves interchange on the actual local hom categories.
Associator and left/right unitors are the lifted equalities supplied by C's laws,
with inverse equalities given by symmetry. Naturality and each typed pentagon or
triangle compare parallel equality proofs, which agree by proof irrelevance.
These are concrete coherence components, not assumed arbitrary higher laws.
Underlying objects/Hom/id/comp remain literally C, so structural recursion proves
that the V25 sequential observer is unchanged. This is the locally discrete
construction; see [Mathlib LocallyDiscrete](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Bicategory/LocallyDiscrete.html).
Standard bundled bicategory packaging is distinct from proving these components;
FORMAL_SCOPE states which is actually kernel registered. Arbitrary nontrivial
2-cells, higher observations and physical transformations are not recoverable from
this example. The old informal descriptions-as-objects suggestion is not used.

## External admission

Closed admission is representable as the Hom subtype with all inherited laws,
as proved in [RESTRICTIONS](RESTRICTIONS_V26.md). Thus after the admitted category
is supplied no independent predicate field is required by the sequential observer.
This does not determine admission on excluded ambient arrows or establish physical
safety. Arbitrary predicates can omit identities or fail composition closure.
[RESOURCES](RESOURCES_V26.md) provides one explicit state-lifting repair under exact
additive Nat costs, rather than pretending every failed predicate was closed.
These six arguments jointly address original006 within its registered scope only.
