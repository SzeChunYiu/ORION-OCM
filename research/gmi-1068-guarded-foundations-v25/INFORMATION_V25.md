# Presented carriers and least retained observer information

## 1. Subtype presentation and padded operation

Fix L. A presentation consists of S:L→Prop and an actual lawful V19 Algebra on
A={x:L | S(x)}. Let lookup(x) be some⟨x,h⟩ if S(x), otherwise None.
Define p(x,y) by lifting both inputs, applying the subtype multiplication, then
mapping the output through Subtype.val. Proof irrelevance makes the choice of h
immaterial. Successful p(x,y)=some z implies S(x), S(y), S(z), by construction.
On present inputs the equation is exactly the mapped subtype operation.

Theorem Y2a: S(x) iff ∃y z,p(x,y)=some z.
Forward: for ⟨x,h⟩ choose its actual right local unit f; the product is x, so use
its ambient label as y and x as z. Reverse: success requires the first input lift.
Thus a whole lawful padded table already determines the carrier. No isolated
present row is possible under the local-unit premise. The empty carrier gives an
all-None table, including on nonempty ambient L.

## 2. Padded associativity and units

If x,y,z are all present, map subtype strong associativity through Subtype.val;
Option-map commutes with binds and the mapped intermediate output remains present.
If x is absent, both associations fail when x is lifted. If y is absent, the first
product on each side fails. If z is absent, the left's final product and right's
first product fail. Thus p is strongly associative on every ambient triple.
It need not have local units for absent elements and is not declared an Algebra L.

Let U_p(e) mean p(e,e)=some e and all defined left/right products by e preserve
the other input. Then U_p(e) iff e has a present subtype lift which is a true unit.
Forward: the self-product supplies S(e). Apply neutral laws to present input/output
lifts; injectivity of Subtype.val identifies outputs in the subtype.
Reverse: self-product follows from the subtype unit; any defined ambient product
lifts the other input, so its neutral equation maps to the required ambient result.
Absent e cannot be a unit because its self-product fails.

## 3. Exact observer equality

Let R_p be the raw observer of HISTORIES §4. Arrow(x) extracts membership:
R_p(Arrow x)=some x iff S(x). Binary query Seq(Arrow x,Arrow y) returns exactly
p(x,y), including absent input cases. Conversely S and p determine every response
by structural recursion, since p determines the unit predicate used by Empty.
Therefore two presentations on the same L have equal raw observers iff their
pairs (S,p) agree. By Y2a, this is also equivalent to equality of p alone.
Subtype proof terms and independently stored endpoint fields are not observed.

## 4. Attained-code recovery

For maps code:M→Z and f:M→W, Recoverable(code,f) means a decoder on the attained
image {z | ∃m,code(m)=z} returns f(m) at every attained code. V9 proves this iff
f is constant on every fiber of code. Necessity follows by applying the same
decoder to equal codes. For sufficiency, choose a representative of each attained
fiber and evaluate f there; fiber constancy makes the answer representative-independent.
This requires no default W-value at unattained z and permits empty M or W.

Apply this criterion to the pointwise equivalences in §3. For every family of
Presented L and every code:
Recoverable(code,R) iff Recoverable(code,(S,p)) iff Recoverable(code,p).
One can also compose the explicit extraction and recursive interpretation maps
with attained-image decoders. Both approaches retain the original raw-query interface.

This is the least-information characterization relative to the observer: every
sufficient code determines p, and p suffices. It is not a lower bound on bytes,
program length, independently stored cells, runtime or a canonical encoding.
A compressed formula for p is allowed. Isomorphic relabelings count as the same
representation only when query and response labels are transported as in ENCODINGS.

## 5. Necessary qualifications

If local units are omitted, an isolated present arrow has an all-None row, so a
padded table can fail to determine membership. Arrow singleton responses still
separate that presentation from absence. The Y2 equivalence is not exported to
this broader lawless class.

Likewise fixed external object names have an independent encoder. Raw unit labels
and named objects are different interfaces; ENCODINGS §3 retains that information
and proves the strengthened paired-information theorem instead of assuming it away.
The finite executable recovery routine checks fibers on its supplied finite family;
the arbitrary-family proof is not inferred from finite enumeration.
