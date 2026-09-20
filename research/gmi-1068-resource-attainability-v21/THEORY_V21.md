# V21 execution theorem: actual finite histories and residual resources

Read CORE.md first. This file proves U1 at the paper level. Exact kernel
registrations and implementation correspondence are delimited separately.

## U1.1 — weighted execution

Fix the immutable V8 Machine m with state S, action A, observation O and edge
payload E. Its transition is m.next:S→A→Option(E×S); its run retains every
intermediate observation and emits an illegal response on a missing edge.
Declare cost:E→Nat. Neither cost nor physical admission is inferred from values.
For a finite word w define weighted execution W(s,w):Option(S×Nat) by

- W(s,[]) = some(s,0).
- If m.next(s,a)=none, W(s,a::u)=none.
- If m.next(s,a)=some(e,t), evaluate W(t,u); none remains none, while
  some(v,c) becomes some(v,cost(e)+c).

This uses the actual same transition function at every step. Define End(m,s,w)
by the same recursion retaining only the state. Induction gives
W(s,w)=some(t,c) for some c iff End(m,s,w)=some(t).
Uniqueness follows because both functions are deterministic. Equivalently,
the V8 Response is successful, meaning its final constructor is done and no
illegal constructor occurs. The empty word succeeds even without outgoing edges.
An undefined observation value is still an observation, not an execution failure.

For all u,v, the exact composition law is
W(s,u++v)=bind W(s,u) (fun(t,c) => map (fun(z,d)=>(z,c+d)) W(t,v)).
Proof: induct on u. The empty case is zero identity. For a cons, a missing edge
makes both sides none; after a present edge, a failed tail again makes both none.
For a successful tail, apply the induction hypothesis and associativity of Nat
addition. The same proof for End binds through the actual intermediate endpoint.
No concatenation of independently chosen unrelated paths is licensed.

## U1.2 — residual execution iff accumulated cost fits

Let m_b be the ACTUAL V8 budgetMachine m cost: state (s,b), observation m.obs(s),
and edge e to t admitted exactly when cost(e)≤b, ending at (t,b−cost(e)).
For every s,w,b,t,r:

End(m_b,(s,b),w)=some(t,r)
iff exists c, W(s,w)=some(t,c) and c≤b and r=b−c.

Proof by induction on w. For [], equality of pairs gives t=s and r=b;
choose c=0. Conversely those equations give the actual empty execution.
For a::u, a missing original transition makes both sides false. A present edge
has cost k. A successful lifted first step requires k≤b; the induction hypothesis
for u at resource b−k gives tail cost d≤b−k and r=(b−k)−d.
Thus c=k+d≤b and r=b−c. Conversely k+d≤b implies k≤b and d≤b−k,
so that exact lifted edge is admitted and the induction hypothesis succeeds.
The arithmetic uses Nat nonnegativity and the admitted-subtraction guard;
truncated subtraction by itself is not an affordability test.

Consequently larger b'≥b preserves each successful word and physical endpoint,
with residual b'−c. It does not preserve the residual state as an equal pair.
Zero costs and cycles require no special exception: induction is on finite words.
Generic S and A may be empty; Python V8's finite constructor is nonempty.

## U1.3 — full successful response and continuation composition

When lifted execution succeeds, its entire V8 Response equals the unrestricted
response for the same s and word. Proof: the empty responses have equal
observations. At a cons, U1.2 admits the identical original edge. Both emit the
same current observation and edge payload; the successful tails agree by the
induction hypothesis. This includes every intermediate observation and cost
payload. It is stronger than endpoint equality for this same-history comparison.
It is not full-trace equivalence between arbitrary different initial states.

Using U1.1 and U1.2, successful execution of u++v with initial b is equivalent
to actual prefix execution ending at (t,r), followed by actual suffix execution
from (t,r). If their costs are c,d, then r=b−c and final residual is b−(c+d).
Proof: End composition gives the runtime equivalence; weighted composition and
U1.2 give precisely c≤b and d≤b−c, equivalent to c+d≤b.
The suffix does not receive the original allowance again.

## Scope and ownership

The theorem concerns fixed deterministic transitions and declared Nat costs.
It proves finite-word feasibility, not a policy's probability of success or an
infinite execution property. The budgeted failure trace can retain a prefix even
when W returns none; no theorem equates arbitrary failure traces with none.

Mohri's weighted-path multiplication and classical path-cost reasoning own the
mechanism. The new evidence required here is the explicit connection to actual
V8 run/budgetMachine and V15 partial contexts, rather than an abstract cost filter
with an unverified runtime interpretation. RESOURCES_V21 gives the broader
ordered accumulation semantics and states exactly when a final-cost test works.
