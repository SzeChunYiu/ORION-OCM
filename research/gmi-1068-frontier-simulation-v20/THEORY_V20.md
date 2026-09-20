# V20 theory — frontier construction and attainable images

## T1.1 — preorder semantics and construction

Let (W,≤) be a declared preorder. Set u<v iff u≤v and not v≤u, and
u~v iff u≤v and v≤u. The strict relation is irreflexive and transitive:
if u<v<w and w≤u, transitivity would give w≤v, contradicting v<w.
The equivalence ~ is transitive by the two preorder transitivity directions.
For A⊆W define ↓A={w | ∃a∈A,w≤a} and

    Max(A)={a∈A | ∀b∈A, a≤b implies b≤a}.

For finite supplied A, this is an executable filter over A and all comparisons
against A. It returns all maximal attained values, including distinct equivalent
ones. It does not presume antisymmetry, a total order or a scalar objective.

For every a∈A a maximal m∈A exists above a. One finite proof ascends strictly
whenever the current value is not maximal. If a<b, the set of elements strictly
above b is a proper subset of the set strictly above a: inclusion follows from
strict transitivity, and b belongs only to the latter. Its finite cardinality
decreases, so ascent stops at a maximal element. The accumulated preorder
comparisons give a≤m. Thus Max(A)⊆A and Max(A) is cofinal in A.
Transitivity now gives ↓A⊆↓Max(A); the converse follows from inclusion.
For A=∅, both frontier and downward closure are empty; cofinality is vacuous.

## T1.2 — representative selector and exact minimum

Enumerate Max(A) in a supplied finite presentation order. Keep a value if it
is not equivalent to an already kept value. Each step preserves the following
invariant: every processed maximal value is equivalent to exactly one retained
representative; representatives belong to A and represent different classes.
When the scan ends, its set R therefore meets each maximal equivalence class
exactly once. Choices are presentation-relative; no canonical tie resolution follows.

Cofinality of Max(A) and equivalence of each maximal value to its representative
give cofinality of R. Distinct representatives are incomparable: if r≤s,
maximality of r gives s≤r, contradicting their distinct equivalence classes.
For every cofinal subset C⊆A, each r∈R has some c∈C with r≤c.
Maximality gives c≤r, hence c~r. Chosen c values for different representatives
cannot coincide, since that would make their representatives equivalent.
This injects R into C and proves |R|≤|C|. R itself is cofinal, so the bound
is attained. For empty A the result is the empty representative set of size zero.
This is minimum cardinality among cofinal subsets of the attained set, not an
absolute memory, program-length or representation-size minimum.

## T1.3 — actual V15 partial-context specialization

A V15 Context k supplies E(h), an evaluator ν on the subtype {h | E(h)},
and the preorder on W. Admission P is separate. For a supplied history selector
H_x, construct

    A_x={ν(h) | H_x(h), P(h), E(h)}.

The notation ν(h) always includes its E proof; it is never evaluated outside E.
A finite supplied collection selected by H_x yields a finite image, even with
duplicate histories or equal returned values. Filter by P and E before taking
the image, then apply T1.1 and T1.2. Each returned frontier value has an actual
selected, admitted, evaluated history witness. Conversely every selected attained
value lies below a returned frontier value. Duplicates do not create new values;
preorder-equivalent distinct values remain distinct until selecting representatives.

This constructs the original R3 finite frontier for the actual attainable image.
The three ambient outcome tags retain their V15 meaning: not P is ILLEGAL;
P and not E is UNDEFINED; P and E returns VALUE(ν(h)). An ambient evaluation
can exist on an illegal history without making that history admissible.
Each history being finite does not imply a finite collection or a finite image.
Alternatively a separately proved finite image is sufficient for T1.1, even if
its history collection is infinite. The result does not add limit points or
infinite traces to the original finite-history attainability semantics.

## T1.4 — general sufficient condition beyond finite sets

On the subtype of attained values A define ascent R(b,a) iff a≤b and not b≤a.
Assume R is well-founded. By well-founded induction on a, prove that there
exists a maximal m above a. If a is maximal, choose a. Otherwise classical
negation of maximality supplies b∈A with a<b. The induction hypothesis at b
supplies maximal m with b≤m; transitivity gives a≤m. This proves cofinality
and the same downward-closure equation for arbitrary A under this condition.
The hypothesis is about the actual attained subtype, not a reverse relation
whose orientation would forbid descent instead of ascent.

Well-founded ascent is sufficient, not necessary, and supplies neither a finite
frontier nor an effective search procedure. Nat with a top has a cofinal maximum
despite infinite ascent. An infinite antichain has well-founded strict ascent
but every point is maximal. Nat alone has no maximal value. Adding one isolated
maximal point beside Nat gives a nonempty maximal set that is not cofinal.
[CONTROLS_V20.md](CONTROLS_V20.md) spells out these boundaries.
No Zorn import or unconditional infinite-frontier construction is needed here.

## Parent and proof boundary

Geilen–Basten–Theelen–Otten's Pareto algebra supplies the finite/well-founded
frontier mechanism. Their smaller-is-better partial order is dualized to this
larger-is-better preorder, with equivalent values handled explicitly.
The general well-founded induction is standard order theory.
The exact kernel registrations and the finite selector/cardinality calibration
are distinguished in the final theorem ledger; finite tests do not prove an
arbitrary-carrier theorem by themselves.
