# V21 ordered resource accumulation

The Nat residual machine is a specialization. A general resource model need
not have subtraction, cancellation, commutativity or a least scalar capacity.

## U4.1 — declared ordered product and actual accumulation

Let (R,≤,product,e) be a preorder and a monoid: product is associative, e is a
two-sided identity, and multiplication is monotone in both arguments. Write
p*q for the product. Declare an edge weight w:Eedge→R on fixed physical
transitions. For a successful finite path e1,...,en define fold([])=e and
fold(e1::u)=w(e1)*fold(u). No commutation of factors is allowed.

With initial spent q, the accumulated result is q*fold(path). Sequential updating
q to q*w(e1) computes this same value by associativity and the identity laws.
Induction on the first word proves weighted concatenation:
weight(u++v)=weight(u)*weight(v), where v starts at u's actual endpoint.
Undefined physical prefixes remain undefined; this equation is conditioned on
the actual successful path, not arbitrary independently sampled edge labels.

Define cumulative execution Cum(q,b,w) to check q≤b BEFORE processing the word,
then follow each actual edge and recurse with spent q*w(edge). It succeeds
exactly when physical execution succeeds and EVERY prefix aggregate, including
q for the empty prefix, is ≤b. Proof: induction on w matches its initial check,
actual edge case and recursive suffix checks. On success it returns the physical
endpoint and q*fold(path). This theorem requires no positivity.
Capacity nesting follows directly: every prefix p≤b≤b' remains feasible at b'.
It compares the same initial spent q, transitions, weights and finite word.
For an actual fixed partial Context, define admission by P, selection and
success of this cumulative execution. Capacity nesting and U2 image_mono then
give nested images and declared-target capability for these general resources.
This corollary uses prefix admission; a joint FINAL-cost filter requires the
additional U4.2 hypothesis. No least capacity is required for nesting.

## U4.2 — when one final affordability check is enough

Assume e≤w(edge) for each edge of the actual path; a global sufficient assumption
is this inequality for every present transition. Each update is nondecreasing:
p=p*e≤p*w(edge) by monotonicity. Transitivity shows every prefix aggregate≤the
final aggregate, including the initial q. Therefore cumulative success iff
physical success and q*fold(path)≤b. Forward uses the last prefix check;
reverse transports final affordability to every prefix and applies U4.1.

For an empty word final aggregate is q, so the condition is exactly q≤b.
No assumption that every capacity is positive is used. Initial resource failure
must not disappear just because there are no actions. Positivity here concerns
declared edge increments relative to identity, not a universal theorem about
resource objects. The law permits zero and idempotent increments.

## U4.3 — exact relation to Nat residual accounting

Instantiate R=Nat, e=0, product=addition, usual order, and initial spent0.
Every cost is nonnegative, so U4.2 gives success iff total cost C≤b.
U1.2 gives the same condition for actual V8 residual execution, with final
residual b−C. At every successful prefix with spent p, the two representations
satisfy spent+residual=b. Induction preserves this equation when next cost k
satisfies p+k≤b: the corresponding residual guard is k≤b−p.
This is a proved adapter between two declared representations, not an assumed
subtraction operation on arbitrary monoids. A nonzero Nat initial spent q≤b
similarly corresponds to starting V8 with residual b−q.

## U4.4 — models and the boundaries they expose

Nat addition models cumulative consumption. Finite vectors of Nat, with
coordinatewise addition and order, model simultaneous declared constraints.
Nat with max and identity0 models peak capacity: its accumulated value is the
maximum demand, not a sum to subtract repeatedly. The product model
(t,p)*(u,q)=(t+u,max(p,q)) combines elapsed consumption and peak demand with
coordinatewise order. Each structure has associative product, identity,
monotonicity and e≤every element by its elementary coordinate laws.
They illustrate declared semantics, not inferred physical resource laws.

A positive noncommutative model is nonnegative 2×2 matrices satisfying I≤M
entrywise. Multiplication is associative, I is identity, and monotonicity follows
from addition/multiplication of nonnegative entries. Closure and positivity hold:
for M,N≥I, MN≥MI=M≥I. With
A=[[1,1],[0,1]] and B=[[1,0],[1,1]],
AB=[[2,1],[1,1]] while BA=[[1,1],[1,2]].
Both exceed I, but are unequal. Sequential order therefore cannot be erased.
The proof only needs monotonicity; a complete semiring or a path-aggregation sum
is not an assumption of the cumulative execution theorem.

Signed integer addition is an ordered monoid but has negative increments.
For a finite path let prefix sums include0 and define demand=max(all prefix sums).
With initial spent q, all prefixes fit b iff q+demand≤b. Proof: every prefix
sum≤demand gives the reverse implication; a finite prefix attaining demand gives
the forward implication. Thus maximum prefix demand repairs signed admission.
The final sum alone is insufficient. This is a separate declared signed model,
not a mutation of immutable V8's Nat costs or an automatic generic residual.

Fritz's resource-convertibility monoids explain why positivity/free disposal is
an extra assumption. Sequential, possibly noncommutative costs here adapt that
algebraic language rather than importing a universal resource interpretation.
Mohri's ordered path products are the stronger algorithmic parent; no generic
semiring distance is assumed to be the weight of an actual path.
