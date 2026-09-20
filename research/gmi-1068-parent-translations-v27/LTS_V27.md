# AA1 — relation-LTS, powerset coalgebra and paths

Fix a label type A and state types S,T, possibly empty. Let R(s,a,t) be a
predicate. This is a relation-LTS, with no multiplicity of equal triples.
Parent: Rutten, Universal coalgebra, Example2.1 and Theorem2.5, printed pp9–13.
Dependencies: classical sets/functions and actual V11 indexed Path.

## AA1-A — exact relation and successor roundtrips

Define succ_R(s)(a,t) iff R(s,a,t), and rel_alpha(s,a,t) iff alpha(s)(a,t).
Both composites are the original predicate, pointwise; function/proposition
extensionality packages this as equality. Empty carriers need no special case.
For f:S→T define image_f(U)(a,u) iff ∃t,U(a,t) and f(t)=u.
The identity equation uses witness u in one direction and substitution in the
other. Composition follows by combining/splitting witnesses through f then g.
Thus B(X)=P(A×X) and B(f)=image_f form the actual labelled powerset functor.

At a state s, the square B(f)(succ_R(s))=succ_Q(f(s)) says exactly:
Forward: R(s,a,t) implies Q(f(s),a,f(t));
Back: Q(f(s),a,u) implies ∃t,R(s,a,t) and f(t)=u.
Equality implies Forward by inserting t into its left side and Back by reading
its right-to-left inclusion. Conversely each implication supplies one inclusion.
Back is existence of a matching preimage, not injectivity or unique inverse.

For graph(f)={(s,f(s))}, relational bisimulation requires each R-successor to
have a Q-successor again in graph(f), and conversely. Its first clause forces
the matching target to be f(t), giving Forward. Its second clause is Back.
These substitutions prove graph-bisimulation iff the actual coalgebra square.
This is not a theorem equating trace equality with bisimulation.

## AA1-B — actual labelled generators and free paths

Use the V11 graph G_R(s,t)={a:A | R(s,a,t)}. A generator is its actual label
with transition proof. A singleton exists with label a exactly when R(s,a,t).
Proof irrelevance identifies proofs of the same triple; no multigraph IDs enter.
The actual inductive Path has nil at its source and cons of one generator with
a path from its target. Its category composition is actual append, and identities
are nil. V11 proves the identity/associativity laws and lawful interpretation.

Define labels(nil)=[] and labels(cons e p)=e.label::labels(p).
Induction on p proves labels(append p q)=labels(p)++labels(q).
Forward maps e:s→t to the same a:f(s)→f(t), justified by its Forward proof.
Map nil to nil, and cons to cons of mapped generator and recursively mapped tail.
Structural induction proves map(nil), map(cons), map(append), endpoints and
labels unchanged. Applying V11 evaluation to a lawful supplied interpretation
commutes with this generator map by the same nil/cons induction.
No category of bounded paths is used: a cyclic finite LTS has arbitrarily long paths.

## AA1-C — lift the same finite target path

Assume Forward and Back, a start s and p:Path G_Q (f(s)) u.
We construct ∃t,∃q:Path G_R s t, (f(t),map(q))=(u,p) in the dependent endpoint/path bundle.
Induct on p. For nil choose t=s and q=nil; the bundled equality is reflexive.
For a first edge labelled a to v, Back supplies t1 with R(s,a,t1) and f(t1)=v.
Substitute this endpoint equality. Apply induction to the remainder starting at t1.
Prepend the actual source edge to its lifted path. Forward maps it to the original
labelled target edge; subtype proof irrelevance identifies their transition proofs.
Together with the inductive bundled equality this is exactly p, not another path
with the same labels. This proof is finite structural recursion using existential
choices. It yields neither a unique lift nor an effective selector for predicates.

No injective state map is needed. Several source paths may map to the same p.
Finite Python lift_path returns every lift in its finite model; the general
existence proof does not certify that implementation or provide global infinite
path lifting. There is no silent claim about compactness or dependent-choice runs.

## Representation and falsifiers

The executable graph assigns sorted stable IDs to distinct triples and uses the
actual V11 finite path API. A graph stores source/target while label lookup retains
A. The endpoint graph alone does not recover labels or unused label-set cardinality;
the supplied LTS/edge registry and declared label set retain those data.
Equal endpoints with different labels remain different generators.
Inputs with duplicate triples are rejected; they would be a different multigraph
interface, not extra evidence for this relation theorem. A declared bijective
label rename is an explicit adapter, never an implicit fixed-label map.

A dead source into a target loop is Forward but fails Back; a source loop into
a dead target is Back but fails Forward. Even with a nonempty mapped transition,
an extra target successor without preimage defeats Back. Comparing only traces
can miss a changed intermediate target state, so the oracle must certify the
whole edge path and endpoint. Dropping one of several valid lifts must be detected.
Branching a.(b+c) versus a.b+a.c has equal finite trace sets but no root bisimulation:
a single successor enabling both b,c cannot match one enabling only b or only c.
