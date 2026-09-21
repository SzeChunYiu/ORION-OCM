# Integrated R1 claim and proof structure

## Registered object of study
Fix a lawful category C with explicit object/arrow interfaces. Interpret graph
paths in C and observe arbitrary anchored trees through the actual partial
composition of bundled arrows. An empty leaf carries its own object.
The response is either failure or a bundled arrow with both endpoints.

There are two distinct quantifier levels.
A category presentation theorem fixes C and constructs its own maps.
A family recovery theorem fixes common model, query and output interfaces,
then compares observations of every model through the same encoders.
Neither theorem supplies the premises of the other automatically.

## AC1 — semantic presentation
Let G have the objects of C and let e map each generator to its typed C arrow.
The unique path interpretation E sends empty paths to identities and append to
composition. On each Hom, define p~q iff E(p)=E(q).
This relation is an equivalence and a two-sided concatenation congruence.
Its quotient category Q has objects unchanged and arrows [p].
The map L:Q→C, L[p]=E(p), preserves identities/composition and is faithful.

If every C arrow is E(p) for some typed p, L has an object-fixing inverse K.
Otherwise no inverse onto all C arrows is claimed.
With G=C.Hom and e the identity, singleton paths establish generation.
With a smaller generating graph, generation is a separate premise.
[PRESENTATION](PRESENTATION_V29.md) proves well-definedness and both inverses.

## AC2 — anchored observations and recoverability
For an actual functor F:C→D, mapping every tree and its output preserves all
partial responses exactly iff F is injective on literal objects.
Successful trees alone transport under the functor laws.
Faithfulness concerns arrows within one fixed Hom; it does not separate objects.
Object injectivity plus faithfulness makes the bundled output map injective.
These statements explain which information each integration adapter retains.

For Option-valued responses S:M→Q→Option A and T:M→R→Option B,
fix i:Q→R and injective j:A→B, and suppose
T(m,i(q))=Option.map(j)(S(m,q)) for all m,q.
This extension preserves None and maps some(a) to some(j(a)).
Then any representation z of models recovers the complete source signature
q↦S(m,q) iff it recovers q↦T(m,i(q)).
No injectivity of i is needed; full R-signature recovery is a stronger question.
[OBSERVERS](OBSERVERS_V29.md) and [INFORMATION](INFORMATION_V29.md) give proofs
and actual failure/repair controls.

## AC3 — joint compatibility, not new foundation axioms
The frozen DAG has a,b,c and ab; c and ab evaluate to the same target arrow.
Actual path enumeration, quotient class order and lexicographic target order
remain separately encoded. A proper six-to-seven label injection and permuted
object names connect the category to actual named interpreters.
A lawful wide restriction retains identities and a. Its inclusion transports
only trees whose arrow leaves belong to that restriction.
Removed b/c are availability controls, not counterexamples to lawful inclusion.

The independent fixture checks these interfaces jointly. It cannot replace the
inherited tensor obstruction, stochastic models, omission controls or parent
translations. Those retain their own hypotheses and original evidence.

## Original-relative minimality
The six survivor rows concern retained information or omitted laws.
Units and carrier membership may be reconstructed from suitable lawful tables;
they are not independent storage cells or irreducible syntax fields.
Fixed external object names additionally require their identity encoder.
The six removed rows mean optional for this sequential observer, not absence of
useful parallel, probabilistic, nondeterministic or higher structure.
The seven parent rows retain their own maps and losses; no common lossless
equivalence between all seven theories is asserted.

## Evidence and authority
The paper arguments are mathematical claims with explicit assumptions.
Only exact types that pass the actual isolated kernel audit count as registered
Lean evidence. Exact finite comparisons test executable adapters within their
frozen schedule; they do not prove the generic theorem.
The final receipt must bind the paper, scope, inherited sources and all controls.
Only the original R1 round is eligible; every original atom record is preserved.
