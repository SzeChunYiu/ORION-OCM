# Z3 — exact resource paths and the projection boundary

Let c(f) be a Nat cost on each actual C arrow, with c(id)=0 and
c(f;g)=c(f)+c(g) for every legal composite. These are declared data/laws, not
consequences of categoryhood. Use actual V5.resourceCategory through the transparent
V11 adapters described in [RESTRICTIONS](RESTRICTIONS_V26.md).

## Z3.1 — construction and projection

Objects are (a,r). An arrow (a,r)→(b,s) is an actual f:C(a,b) with r=c(f)+s.
Identity uses 0+s=s. For arrows with r=c(f)+s and s=c(g)+t, addition gives
r=c(f)+c(g)+t=c(f;g)+t, supplying the composite subtype proof. Category laws
follow by subtype extensionality from C; no new product is chosen.
Projection Q sends (a,r) to a and each subtype arrow to f. These formulas
preserve identities/composition, so Q is a genuine functor and homwise faithful.
It generally collapses different balances, so Z2 does not give full raw transport.
It does give preservation of every successful tree and every actual typed path.

For a fixed base f:a→b and r, an outgoing lift exists exactly when c(f)≤r.
A lift yields r=c(f)+s and thus the inequality. Conversely set s=r−c(f);
Nat subtraction under that inequality gives r=c(f)+s, hence an actual lift.
Any such s equals r−c(f), by Nat cancellation. This is an arrow over the supplied
f, not merely some transition with the same endpoints.

## Z3.2 — exact same-path lifting

For an actual typed path p define |nil|_c=0 and |cons(f,p)|_c=c(f)+|p|_c.
Induction using the two cost laws proves c(eval p)=|p|_c.
Map resource paths by Q using actual nil/cons. Claim: for any r, there exist s
and an actual resource path q:(a,r)→(b,s) with map_Q(q)=p iff |p|_c≤r.
Moreover every such lift ends at s=r−|p|_c.

Necessity follows by induction along q. Each edge gives r_i=c(f_i)+r_(i+1);
substitution yields r=Σc(f_i)+s. Exact projection identifies this sequence with p,
so its sum is |p|_c. Therefore the inequality and residual formula follow.
For sufficiency induct on p. Nil lifts to nil at (a,r), using 0≤r.
For cons(f,p'), c(f)+|p'|_c≤r implies c(f)≤r. Form the actual first lift
with residual r'=r−c(f). Nat arithmetic yields |p'|_c≤r'; induction constructs
q' projecting exactly to p'. Cons of that edge and q' is the required q.
This constructs every intermediate balance and the literal same arrow sequence.
Lifting only the evaluated composite would not establish the path statement.

## Z3.3 — failed joins and insufficient resource are distinct

In the chain a→b→c, let f,g each cost1. Resource arrows
f:(a,1)→(b,0), g:(b,1)→(c,0) are individually valid but do not compose:
their middle objects differ. Their projected base arrows compose. This is a
lawful homwise faithful functor failing raw failure reflection, exactly as Z2 predicts.
For the genuine base path f;g from balance1, no coherent lift exists because 2>1.
From balance2 there is a lift 2→1→0. These are different queries: the first raw
pair has inconsistent supplied anchors; the second seeks consistent anchors.
An ill-typed base path cannot be made well typed by increasing the resource.

## Z3.4 — finite adapter and boundaries

For any finite base category with these exact Nat costs, select resource objects
with balances0..M and all resource arrows between them. This is a full subcategory:
identities stay inside and composites retain their endpoint objects. Nonnegative
cost ensures intermediate balances of a lift from r≤M also lie in0..M.
Thus the finite stepwise adapter realizes Z3.2 on its stated starting range.
It does not encode every Nat balance or arbitrary physical resources.

The registered calibration uses base arrows (i,j), 0≤i≤j≤2, cost j−i and M=2.
There are9 objects and14 arrows; labels retain the actual base arrow and initial
balance. Projection of a returned path must be the literal original path request.
Nonzero additive Nat cost cannot be freely assigned to torsion/idempotent arrows:
if f;f=f, additivity forces c(f)+c(f)=c(f), hence c(f)=0. Do not substitute
such an invalid cost model to fabricate a resource counterexample.
Subadditive, signed, peak, vector and history-dependent resources need their own
stated semantics; V21 treats several broader laws, none is silently imported here.
