# Z1 — inherited admission and exact history preservation

Use [THEORY](THEORY_V26.md)'s observer. All objects of C remain present.
The strongest mature implementation parent is [Mathlib Widesubcategory](https://leanprover-community.github.io/mathlib4_docs/Mathlib/CategoryTheory/Widesubcategory.html).
The local parent is V5 AdmissibilityV5, which already proves the closure criterion.
V26 connects that actual construction to V11 paths and the actual V25 observer.

## Z1.1 — closure is necessary and sufficient

Suppose the restricted Hom(a,b) is {f:C(a,b) | P(f)}, with identities and
composition required to have the original underlying C arrows. A restricted
identity provides P(id_a). Composing any two admitted arrows provides P(f;g).
Thus all identities are admitted and P is composition-closed; no closure property
of an arbitrary new multiplication would establish this statement.
Conversely these two conditions supply restricted identities and composites.
Their underlying arrows obey C's laws. Subtype extensionality transfers associativity
and units, since predicate proofs do not add distinguishable arrow values.
This proves exactly the inherited-operation criterion, including empty categories.

The V11→V5 adapter retains O, Hom, id and composition. The reverse adapter reads
these same fields; both roundtrips agree on data and proof fields by proof irrelevance.
Construct R by applying actual V5.restrictedCategory to the first adapter, then
adapting back. The forgetful functor J has object map id and Hom map subtype.val.
It preserves id and composition by the defining underlying-operation equations.

## Z1.2 — partial products and raw trees

For bundled x=(a,b,f) and y=(c,d,g) in R, compare b and c.
If unequal, both partial products are None because J changes no object.
If equal, both products are Some(a,d,f.val;g.val) by the restricted composition
formula. Hence m_C(Jx,Jy)=Option.map J(m_R(x,y)) for every pair.
At an Empty leaf, J(id_R)=id_C; at an Arrow leaf equality is immediate.
Induct on Seq: if either child fails, induction makes its mapped child fail;
if both succeed, apply the pair equation. Therefore every raw response commutes.
This includes incompatible boundary joins, every bracketing and nested empties.

J is injective on bundled arrows: equality fixes endpoints and underlying arrows,
and subtype extensionality fixes the remaining component. Option.map J is likewise
injective, by distinguishing None/Some and then applying J injectivity. Consequently
mapped responses are equal iff original responses are equal; failure is reflected.
No fullness or surjectivity is used. The full object set is essential.

## Z1.3 — actual paths and absence of new identities

Map actual V11 nil to nil and cons(f,p) to cons(Jf,map p). Induction proves
compatibility with append. Evaluation commutes: nil uses J(id)=id, and cons uses
J(f;eval p)=Jf;J(eval p) followed by induction. The actual V25 pathTree theorem
then identifies this path equation with its bracketed response, rather than merely
using similarly named evaluators. Distinct paths may still have the same composite.

Any identity of the restricted category at a must equal its retained id_a: by
the identity laws, two identities compose to each one, forcing equality. Thus an
admitted nonidentity idempotent cannot replace an omitted original identity;
a restriction omitting that original identity failed Z1.1 in the first place.

## Limits and falsifiers

In the one-object Nat-addition category, P(n):n≤1 retains 0 but excludes 1+1;
there is no inherited restricted category. P(n):0<n is addition-closed but omits 0.
Neither failure is repaired by inventing a new identity or product under the same
claim. Resource-state lifting changes objects explicitly; see [RESOURCES](RESOURCES_V26.md).
An ambient arrow outside P is not an R arrow, even if its ambient execution succeeds.
Any ambient-input lifting API must reject/guard such leaves before claiming equality.
The result does not decide which P is physically justified or recover a predicate
on excluded ambient arrows from R alone. It removes an independent representation
field after the admitted category is supplied, not the scientific admission problem.
