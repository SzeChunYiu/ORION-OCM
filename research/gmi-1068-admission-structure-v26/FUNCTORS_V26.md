# Z2 — exactly when raw failures survive a functor

Let F:C→D be an actual functor, with object map F0 and dependent Hom map F1.
Its bundled map sends (a,b,f) to (F0a,F0b,F1f). It preserves the supplied identity
and composition operations. Define tree transport structurally on both leaf sorts.
Parents are [Functor.Basic](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/Basic.html)
and [Functor.FullyFaithful](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Functor/FullyFaithful.html).
The following proof is an elementary consequence for the explicitly declared raw observer.

## Z2.1 — the three equivalent conditions

(A) F0 is injective.
(B) For all bundled x,y, m_D(Fx,Fy)=Option.map F(m_C(x,y)).
(C) For every raw tree t, R_D(map F t)=Option.map F(R_C(t)).

A implies B. If source endpoints match, the target endpoints match and the
functor composition law identifies the returned arrows. If source endpoints do
not match, F0 injectivity keeps target endpoints unequal, so both sides are None.
B implies C. The Arrow case is immediate and Empty uses the identity law.
For Seq, induction supplies child response equations; split None/Some for both
children and use B in the Some/Some case. All finite bracketings are covered.
C implies A. Suppose F0a=F0b. The tree Seq(Empty a,Empty b) has a successful
mapped evaluation: its two identity arrows are composable in D. Equality C forbids
a None source response, so a=b. This includes all source objects without an
inhabitedness assumption; the empty-object case is vacuous.
Thus A, B, C are equivalent; in particular the pair condition cannot conceal
an object-collapse defect behind homwise functoriality.

## Z2.2 — what every functor preserves

For any successful source product, its endpoint equality remains true after F0,
and F1 preserves composition. Induction restricted to successful trees therefore
proves R_C(t)=Some z implies R_D(map F t)=Some(Fz), with no injectivity premise.
The same nil/cons induction on an actual typed path proves evaluation preservation;
there is no source-failure branch in its type. Restricting C to typed paths would
therefore invalidate the converse inference to object injectivity.

If F0 is injective and each F1:C(a,b)→D(F0a,F0b) is injective, the bundled map
is injective: output equality first recovers a,b, then faithfulness recovers f.
Option.map F is injective, giving equality reflection of raw responses when C holds.
Faithfulness alone is only a condition on each fixed pair of endpoints; it does
not prevent different object labels or different bundled hom-sets from collapsing.

## Z2.3 — two exact separations

The one-object category BC2 has identity0, toggle1 and XOR composition. Its unique
functor to the terminal category has injective object map, so all raw responses
commute. It maps both arrows to the same identity, so arrow information is lost.
Hence all-tree transport alone cannot justify full-output recoverability.

Let I have objects a,b and one arrow u_xy for each ordered pair; composition is
u_xy;u_yz=u_xz and identity u_xx. Every Hom is a singleton, and every arrow
is invertible. The unique functor I→1 is fully faithful and essentially surjective.
Nevertheless Empty(a);Empty(b) fails in I for a≠b and succeeds after mapping.
Even categorical equivalence does not reflect this literal-name raw failure.
The two-object discrete category→1 is a smaller faithful but not full control.

These examples do not refute functor laws: those laws only concern legal source
composites. A validator requiring reflected joins would assume condition A rather
than independently test it. General maps may repeat images and need not be surjective.
All syntactic descendants and map entries must still be structurally valid; semantic
failure does not excuse malformed later leaves or incorrect returned endpoint bundles.
