# AA2 — whole-system arrows and structured object names

Parent: Rutten pp9–13; mature reference Mathlib Endofunctor.Coalgebra.
These arrows relate whole systems; they are not the transitions inside a system.
Fix a universe and an actual Set endofunctor F, with a type map, function map,
and map(id)=id, map(g∘f)=map(g)∘map(f). These primitive laws are premises.

## AA2-A — category and faithful carrier forgetting

A System is (X,alpha:X→F(X)). A Hom from (X,alpha) to (Y,beta) is a function
f:X→Y with F(f)∘alpha=beta∘f. Identity satisfies this by F's identity law.
For f and g satisfying their squares,
F(g∘f)∘alpha = F(g)∘F(f)∘alpha = F(g)∘beta∘f = gamma∘g∘f.
Thus function composition is a Hom. Extensional function equality and proof
irrelevance yield associativity and both unit laws for these actual records.
No category law or morphism-composition conclusion is an assumed interface field.

The function category has types as objects and functions as arrows, with the
ordinary operations. Forgetting (X,alpha) to X and Hom to its function preserves
identities and composition literally. It is faithful on each fixed Hom because
equal functions imply equal Hom records. It need not be full or injective on objects.
For F(X)=P(A×X), its square specializes to AA1 Forward-and-Back by the actual
successor equations, rather than a new independently named morphism predicate.

## AA2-B — faithful forgetting can change raw definedness

Take F(X)=Bool×X. On the same Unit carrier define alpha0(*)=(false,*) and
alpha1(*)=(true,*). These are distinct Systems: equality of their step fields
would imply false=true. The underlying carrier function of either identity is
id_Unit. There is no cross-system Hom because its square would equate the bits.

The raw bracket Seq(Empty(alpha0),Empty(alpha1)) fails the typed boundary in the
System category. After forgetting, it is Seq(Empty(Unit),Empty(Unit)), which
succeeds and returns the identity. This is precisely V26's collapsed-empty
witness for a lawful functor with unequal objects and equal object images.
Faithfulness concerns arrows with fixed endpoints; it never promised preservation
of literal object inequality. No contradiction with ordinary functor laws occurs.
Every originally successful typed path still has a successful mapped path.

## AA2-C — retain tags to restore the exact raw observer

Define a target category Tagged whose objects remain the actual Systems,
but Hom(X,Y) consists of ALL functions between their carriers, without a square.
Identity and composition are ordinary functions; category laws follow as above.
The forgetful map from Systems to Tagged keeps the object exactly and drops
only the square proof on arrows. Its object map is identity, hence injective.
V26's theorem therefore preserves the full mapped V25 Option tree response,
including every failed boundary. The previous two Empty anchors stay unequal.

This repair changes the target interface: its Hom includes functions which do
not preserve dynamics. It supplies no full/equivalent identification with the
coalgebra category, and does not recover a step map from an untagged carrier.
Retaining actual structured objects explicitly retains the missing information.
It is not proof that raw syntax is invariant under arbitrary category equivalence.

## Levels and evidence

A fixed LTS provides a free path category on state objects. A powerset endofunctor
provides a category whose objects are entire LTSs. There is no identification of
these two object sets or Hom sorts. AA1 maps histories within systems under a
system homomorphism; AA2 constructs and studies those system homomorphisms.
The distinction is part of the translation, not a terminology exception.

The finite two-system fixture checks actual V26 functor/tree evaluation; it is
not a generic executable coalgebra-category constructor. Arbitrary System/category
proofs require the separately registered Lean construction. No result identifies
physical state spaces or chooses the functor appropriate to empirical data.
