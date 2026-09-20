# Admission and optional structure: mathematical interface

[Freeze](FREEZE_V26.md) precedes this study. Write f;g for executing f then g.
A category C has actual objects O, endpoint-indexed Hom, identities and associative,
unital composition. It need not be finite, skeletal, free, inhabited or computable.
Literal object equality, rather than isomorphism of objects, determines raw joins.

## Observer and scope

A bundled arrow is (a,b,f) with f:C(a,b). Define m_C(x,y)=Some(a,d,f;g)
when x=(a,b,f), y=(c,d,g) and b=c, and None otherwise; transport along the
endpoint equality is implicit. Proof irrelevance makes the equality witness immaterial.
A raw tree is Arrow(x), Empty(a), or Seq(t,u). Its response R_C is x at an Arrow,
id_a at Empty(a), and Option-bind of m_C at Seq. A failure is a tagged None,
not an ordinary arrow. Every tree has finitely many leaves; there is no unanchored
null tree. This is the actual V25 observer over actual V11 category data.
Python additionally validates the entire syntactic tree before semantic evaluation.

Typed V11 paths have endpoints by construction; nil_a is an empty path at a,
and concatenation requires matching endpoints. Their evaluation agrees with the
actual V25 pathTree interpretation. Raw trees additionally observe failed joins;
this extra observation is why arbitrary functors need a stronger hypothesis.

## Z1: inherited admission

Let P be an endpoint-indexed predicate on actual C arrows. The inherited wide
restriction exists iff every id_a satisfies P and P is closed under C composition.
Its inclusion fixes objects and maps a subtype arrow to its value. It preserves
all raw responses, failure and output equality, plus actual paths and evaluation.
This reuses V5's construction through operation-preserving V11 adapters.
Complete proofs and the necessity of inherited operations are in [RESTRICTIONS](RESTRICTIONS_V26.md).

## Z2: exact functor criterion

For an actual functor F:C→D the following are equivalent: its object map is
injective; all bundled partial products commute with Option.map F; all raw-tree
responses commute with Option.map F. No arrow injectivity is required.
Every functor still preserves successful trees and typed paths. To reflect equality
of successful bundled outputs, object injectivity and homwise faithfulness suffice.
[FUNCTORS](FUNCTORS_V26.md) proves these statements and gives both separation examples.
The all-raw-tree criterion depends on the declared literal-name observer; it is
not invariant under arbitrary equivalence of categories, nor claimed to be novel.

## Z3: resource-state lifting

For a Nat-valued cost c preserving identities and addition under composition,
V5 resource objects are (a,r); arrows over f obey r=c(f)+s. Projection to C is
a functor, generally not injective on objects. A typed path p lifts over exactly
its own arrow sequence from balance r iff its summed edge cost is at most r;
the final balance is r minus that sum. [RESOURCES](RESOURCES_V26.md) gives the
construction, residual uniqueness and failed-join counterexample.

## Z4: optional rows are observer-relative, not arbitrary information erasure

The six immutable removed-component rows have distinct arguments. Tensor and
symmetry have structural countermodels; deterministic functions supply ordinary
sequential categories without independent stochastic/choice fields. Rich kernels
and relations retain probabilities and branches inside their arrows. Locally
discrete higher structure adds no independent information to this observer.
Closed admission can be represented by Hom, but closure or physical admissibility
cannot be inferred from the bare choice of a predicate. [OPTIONAL](OPTIONAL_V26.md)
and its exact source-keyed ledger separate these statements.

All paper proofs quantify over their stated general carriers. Exact Lean coverage
is recorded in FORMAL_SCOPE and the reviewed theorem ledger; Python calibration
is not a general kernel certificate or certified extraction. Standard enriched
packaging and ordered Real interpretations retain inherited paper boundaries.
The finite corpus [CONTROLS](CONTROLS_V26.md) tests the actual implementations and
counterexamples. Original R1-009 and complete-theory/physical adequacy remain open.
