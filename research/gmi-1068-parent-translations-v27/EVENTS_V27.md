# AA4 — classical events and labelled tests

Parent interpretation: CDP sectionsII.E–F distinguishes events, tests, closed
scalars and operational equivalence. Here the model is finite and classical;
no quantum purification, general ancilla equivalence or adaptive test is derived.
Actual matrix and sum operations are the immutable V14 operations.

## Scalar premises and finite sums

Retain V14 Weight: additive commutative monoid, associative unital multiplication,
distributivity and zero laws, 1≠0, a+b=0 iff a=b=0, and a*b=0 iff a=0 or b=0.
Add commutative multiplication and a partial order with 0≤x for every carrier
value and monotonicity of addition and both multiplication arguments.
These are primitive algebra/order hypotheses, not assumed matrix inequalities.
Some retained support assumptions are stronger than the inequalities alone need.

For a finite sum, monotonicity follows by induction from addition monotonicity.
Every term is ≤ the whole sum: isolate that term and use nonnegativity of the
remaining sum. Empty sums are zero. Finite interchange of two sums follows by
induction from associativity/commutativity of addition. Distributivity moves a
fixed multiplier through a sum by induction. All uses below are these finite laws.
General nonnegative Real/Rat carriers satisfy the paper assumptions; a generic
kernel theorem still needs an actual instance to claim those types inside Lean.
The Nat instance witnesses consistency, not fractional probability mixtures.

## AA4-A — event category and normalized slice

An n→m Event is a matrix p with rowSum(p,i)≤1. Entries are nonnegative through
the carrier premise. Compose p then q by (p;q)(i,k)=Σ_j p(i,j)*q(j,k).
By finite sum interchange/distribution,
rowSum(p;q,i)=Σ_j p(i,j)*rowSum(q,j).
Each term is ≤p(i,j)*1=p(i,j), so rowSum(p;q,i)≤rowSum(p,i)≤1.
Identity is the delta matrix and its row sum is one. Actual V14 matrix identity
and associativity equations lift to Events by extensionality/proof irrelevance.
This constructs a category; it does not assume one as a field of Event.
Zero matrices satisfy their bounds for every n,m, including n>0,m=0.

A normalized Event has all row sums exactly one, precisely V14 Kernel's premise.
Both directions keep the matrix coefficient unchanged; their roundtrips follow
by extensionality. The inclusion preserves actual identity and composition.
Normalization of a composite follows from the same row formula with rowSum(q)=1.
When n=0 normalization is vacuous even if m=0; for n>0,m=0 it contradicts 1≠0.
Thus a zero-output event is valid even when a normalized channel cannot exist.

## AA4-B — test components and paired-outcome composition

A finite shape is Fin n or a Cartesian product of two such shapes recursively.
Its sum is the ordinary finite sum in the base case and nested sum for products.
Induction on shape gives linearity, monotonicity, zero, and exchange of shape sums
with state sums; no unproved flat-product enumeration is required.

A Test from n to m has one matrix E_u for each outcome u and normalized aggregate
P(i,j)=Σ_u E_u(i,j). Component Event bounds are DERIVED: each E_u(i,j)≤P(i,j),
then its row sum is ≤ the normalized aggregate row sum one. Equivalently exchange
the row/outcome sums and bound one outcome term by their total. This works with
zero entries and repeated equal matrices; their outcome identities remain distinct.
Python accepts already-checked Event values, while Lean starts with matrices;
this is an explicit interface refinement, not the generic theorem's hypothesis.

For Tests E:n→m and F:m→k use outcome pairs (u,v), coefficient
G_(u,v)(i,l)=Σ_j E_u(i,j)*F_v(j,l). Every G is the actual Event composite.
Exchange the two outcome sums and state sum, then distribute both factors:
Σ_(u,v) G_(u,v)(i,l) = Σ_j (Σ_u E_u(i,j))*(Σ_v F_v(j,l)) = (P;Q)(i,l).
The aggregate is therefore normalized by the normalized-matrix composition law.
This proves pair closure without dropping any outcome or dividing any row sum.
Zero matrices remain legitimate labelled outcomes in this equation.

An empty outcome shape gives the zero aggregate. If there is an input i,
normalization yields 0=1, contradicting inherited one_ne_zero. With no inputs,
normalization is vacuous, so empty tests remain legitimate.
An injective supplied encoder u↦externalID preserves distinct outcomes; pairing
two encoders remains injective by equality of first and second projections.
No theorem infers those external names from probabilities. Three nested tests
have labels ((u,v),w) versus (u,(v,w)); a global labelled-test category needs an
explicit reassociation interface. Literal equality of those encodings is not claimed.

## AA4-C — coefficient observations separate classical events

For i:Fin n let prep_i:1→n be the delta row, and for j:Fin m let effect_j:m→1
be the delta column. Each satisfies the Event bound (column rows are zero or one).
Actual multiplication gives prep_i;p;effect_j as the 1×1 matrix [p(i,j)].
Thus equality of every such closed observation implies equality of every
coefficient, hence equality of Events. Conversely equal Events give equal
observations under the same compositions. For an empty input or output index,
there are no coefficients and all matrices of that shape are already equal;
the universal-observation conclusion is correctly vacuous, not a chosen default.

A 1→1 Event is a scalar x≤1 (and 0≤x); sequential composition is multiplication.
A one-state Test is a labelled family with sum one. These realize only the
classical closed-probability roles. General operational transformation equivalence
may inspect arbitrary ancillas; no such completeness theorem follows merely from
our finite classical basis extraction. Full probability matrices retain more
information than support relations, as the unchanged V14 rational witness shows.

## AA4-D — concrete failures prevent stronger readings

Composing the scalar events [1/2] and [1/2] must return [1/4], not [1].
Conditioning or row renormalization would change the event and closed observation.
Tests with labels0,1 and weights(1/2,1/2) or(1,0) share aggregate[1] but differ
as labelled outcomes. Summing them is an intentional information-losing map.
A zero-probability outcome still has an ID and must survive test composition.
Negative coefficients, sums greater than one and an unnormalized test violate
premises. Arbitrary exact Fraction outputs need not lie on the generating grid.
Finite calibration tests these equations; it is not a general Real kernel instance.
