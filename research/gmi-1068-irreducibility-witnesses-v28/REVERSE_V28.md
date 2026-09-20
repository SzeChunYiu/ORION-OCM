# AB2 — a weak state observer does not recover admission

## Lawful original processes

On Bool define R0(a,b) iff a=b, and R1(a,b) iff a=b or (a=false and b=true).
Both relations are reflexive. R0 is transitive by equality substitution.
For R1, if either of two successive comparisons is an equality, substitute.
The remaining case would require the common intermediate value to be both true
and false; it is impossible. Therefore R1 is transitive.

For each R form a thin category: objects are Bool, Hom(a,b) consists of witnesses
of R(a,b), identity is reflexivity and composition is transitivity.
All parallel arrows are equal, so associativity and both identity laws follow.
This constructs the lawful process rather than assuming a category conclusion.

Hom_R0(false,true) is empty and Hom_R1(false,true) is inhabited.
The fixed-object category records therefore differ: equality would transport an
inhabitant into the empty Hom. They are not being compared modulo an object rename.

Both processes carry exactly original stateValue(false)=0, stateValue(true)=1.
Let the weak observation be this state function, optionally paired with a fixed
state-evaluation domain. Its values coincide in the two models. The target
false→true admission differs. The collision proof from AB1-C excludes recovery
of this admission target from that weak observation.

The original literal reverse theorem proves only the two reachability propositions.
The category construction and shared-stateValue equations are additional required
bridges, not consequences of the theorem's informal name.

## Common raw-history interface

Fix the labelled ambient Bool graph with arrows (0,0),(0,1),(1,0),(1,1).
For a reflexive relation R, admit the arrow (a,b) exactly when R(a,b).
A raw typed path is admitted iff every arrow in its word is admitted.
Every anchored empty path is admitted. This is actual V16 generated admission.

The singleton from false to true belongs to the R1 source but not the R0 source.
The endpoint evaluator uses the same stateValue, and may share any fixed endpoint
definedness predicate E. Its ambient evaluator data do not determine R.
The full admitted source does determine R on this fixed graph, by AB3.

The Python adapter builds an actual V19 Table/Typed thin category for each relation,
with explicit maps between all four ambient edge IDs and the present local arrows.
A missing arrow is None in the ambient-to-local map. Local integer positions are
not silently substituted for ambient labels.

## Four observations and their different information

weak_state stores the labelled state-value and definedness data; it omits R.
active_domain stores values only for histories in P∩E.
tagged stores every labelled ILLEGAL, UNDEFINED or VALUE response.
domain_signature stores membership of every history in the registered roster.

For the finite experiment, the roster contains all typed paths of lengths 0..3,
including every labelled singleton. Equality of these signatures implies equality
of primitive admission, hence equality of the complete generated domains.
This implication uses the generated-domain theorem. The finite roster is not
itself the infinite full source.

With E empty, active_domain is empty in every model even when R differs.
The weak and active observations can therefore collide on admission.
The tagged and singleton-complete domain observations cannot do so.

## Limits and parents

This is a counterexample for the declared weak observation and model class.
It gives no physical-admission law, no claim that every notion of context omits
its admitted source, and no independence under every possible observation.

The C4/V4 composition witness has identical all-word admission. It cannot replace
the present reverse witness, whose target is a difference in admission.

The mature parent is the classical preorder-to-category construction
(Stacks Project, tag 002Z), with category laws as in tag 0013.
V9 supplies the information criterion, V16 the generated-history bridge and
V15 the partial evaluator with independently stored P and E.
