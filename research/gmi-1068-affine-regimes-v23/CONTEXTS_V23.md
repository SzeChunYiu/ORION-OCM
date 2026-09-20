# V23 — actual partial contexts and identity-preserving decoding

## W1.2 — common-value context

Use THEORY_V23 notation. On W=I times A define
(i,x)<=W(j,y) iff y<=x in A: larger in this preorder means smaller cost.
Reflexivity/transitivity follow from scalar order. Different identities with
equal scores are equivalent under this preorder, not equal as typed values.
Define the actual ambient partial evaluator nu_t on E by nu_t(i)=(i,f_i(t));
leave it undefined exactly outside E. Admission P is a separate predicate.
The observation is illegal when not P, undefined when P and not E, and the
stated value when P and E. An E-true/P-false ambient evaluation still exists,
although public observation is illegal. These are actual V15 tag semantics.

Its attained image is A_t={(i,f_i(t)):i in D}. The context supplies the order;
preference direction is not extracted from this unlabelled image alone.
For i in D, another image value is strictly better exactly when its scalar cost
is strictly smaller: the strict part requires reversed weak comparison and
failure of its converse. Totality turns that into ordinary strict scalar order.
Thus (i,f_i(t)) is maximal iff no active j has f_j(t)<f_i(t), equivalently
f_i(t)<=f_j(t) for every active j. Projecting the full maximal set gives Win(t).
This works for arbitrary I without asserting a maximum exists.

## W1.3 — coded context, genuine transport and decoding

Define coded value type I and i<=t j iff f_j(t)<=f_i(t).
Its actual partial evaluator returns i on E; admission remains P.
Define dec_t(i)=(i,f_i(t)). It is injective because pair equality implies equality
of first coordinates. Moreover i<=t j iff dec_t(i)<=W dec_t(j).
Thus dec_t preserves AND reflects order. Injectivity alone does not prove this;
an injective order-reversing map is a counterexample.

Actual V17 postcomposition maps the evaluator through dec_t and supplies W order.
The result is undefined off E and exactly (i,f_i(t)) on E, so it equals the
common-value context, with the same admission P.
Every attained coded identity is in D and decodes to its corresponding common value;
conversely every common attained value has that identity as a preimage.
Order preservation/reflection carries strict comparisons both ways. Therefore
dec_t maps the full coded maximal set exactly onto the common maximal set.
This is an actual constructor/field bridge, not equality of named selectors alone.

Finite Python uses positional integer codes for unique external labels. An explicit
decoder returns the external identity and exact score; the code order follows score
comparisons. The same code at two parameters may decode to different scalar values.
Only its fixed identity projection compares winner membership across parameters.
P/E, decoded scores and order matrices must be checked even when D is empty.
The zero-candidate case has empty carrier and empty attained/maximal sets.

## W1.4 — aliases versus quotienting and old value images

Distinct identities with the same affine coefficients both win whenever their
common score is minimal. Score equality erases neither identity nor backpointer.
A preorder quotient collapses their equivalence class and cannot replace this frontier.

Original R3 check_r3.py instead supplies performance/cost values and forms their
set image. Histories h3,h4 both map to (2,3), correctly giving one old value.
Historical replay must preserve that deduplication. In the identity-refined affine
reconstruction, use score c-p*t on each evaluated history with value (p,c), the
negative of the old scalar score. New winner IDs project onto exactly the old
winning performance/cost values. h3/h4 may both win while their old value appears once.
Undefined hU contributes no score-bearing attained value or winning identity.

At t=1 the old winning value is (0,0); at t=3/2 values (0,0),(2,3) tie;
at t=3 the winner is (2,3). These follow algebraically from the four unique value
lines; actual replay is separately required. This projection does not transport
every Gamma/Pref/SEL result.
