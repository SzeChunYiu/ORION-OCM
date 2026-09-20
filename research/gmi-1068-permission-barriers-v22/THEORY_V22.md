# V22 execution theory

Read [CORE.md](CORE.md). The proof-level inventory is
[THEOREM_LEDGER_V22.json](THEOREM_LEDGER_V22.json); paper proof does not by itself
claim that its implementation or kernel registration has passed.

## V1.1 — actual permission gate and accumulated requirements

Let M be the immutable V8 deterministic partial machine, with state X, action A,
observation O and edge payload E. Its next(x,a) is either absent or (e,y).
Let Q be a permission type. Declare req(x,a) as a subset of Q for each present
edge. Its dependence on x and a is essential: equal payloads may belong to
edges with different requirements. Entries at absent edges have no operational role.
For S subset Q define M[S] with the same observations and with
next_S(x,a)=next(x,a) when that edge exists and req(x,a) is contained in S;
otherwise next_S(x,a) is absent. No destination, payload or cost is rewritten.

Define F(x,w), an optional pair (endpoint, requirement set), by actual recursion:
F(x,[])=(x,empty). If next(x,a) is absent, F(x,a::w) is absent. If it is (e,y),
compute F(y,w); an absent suffix stays absent; (z,R) gives (z,req(x,a) union R).
This is an actual accumulation over the executed state/action path, not a
caller-supplied admission oracle. Predicate-valued sets permit arbitrary Q;
finite words imply finite requirements only if every traversed req is finite.
Classical predicate gating need not be an effective decision procedure.

For physical endpoint execution End, F(x,w)=(y,R) implies End(M,x,w)=y.
Conversely any successful End supplies its recursively accumulated R.
Proof: induction on w. The empty equations agree. In a nonempty word both
inspect exactly next(x,a); failure agrees, and success reduces to the induction
hypothesis at its actual destination. The recursion uniquely determines R.

Concatenation obeys
F(x,u++v)=bind F(x,u) ((y,R) => map ((z,T)=>(z,R union T)) F(y,v)).
Proof: induction on u. The empty case uses empty union. An absent first edge
or failed suffix yields absence on both sides. Otherwise use the inductive
identity at the actual next state and associativity of set union. Thus repeated
permissions do not add duplicate requirements, while u and v remain distinct words.

## V1.2 — earned support/execution equivalence

For every x,w,y,S,
End(M[S],x,w)=y iff exists R, F(x,w)=(y,R) and R contained in S.
Proof by induction on w. Empty words use the empty requirement set and unchanged
state. For a::w, a missing physical edge makes both sides false. For next(x,a)
=(e,z), the left side succeeds exactly when req(x,a) is contained in S and the
suffix succeeds at z. Apply induction to that suffix. The two containment
conditions are equivalent to (req(x,a) union R) contained in S, which is exactly
the accumulator equation. Conversely split the union containment to authorize
the first edge and suffix. No feasibility implication is assumed in the premise.

Consequences: enabling all permissions recovers physical success; enlarging S
preserves successful words and endpoints; missing physical transitions cannot be
repaired by permissions. These follow by subset transitivity, not by a numeric
or verbal label such as "more power". Failure timing may change under enlargement.

## V1.3 — complete successful response and continuation

On complete gated success, actual V8 run(M[S],x,w)=run(M,x,w).
Proof: empty words return the same observation. For a successful nonempty word,
V1.2 guarantees that the first gate passes and the gated suffix succeeds. Both
runs emit the same current observation and actual edge payload. Induction gives
equality of the remaining response. Hence intermediate and final observations
are preserved, not only the endpoint. A rejected gate may instead stop earlier,
so arbitrary failed traces are outside this equality.

At a word cut, continuation starts at the actual prefix endpoint. The same
permission set S is retained, since these permissions are reusable authorization,
not a consumable Nat balance. Costs may be part of unchanged payloads or a fixed
admission restriction. Any activation charge or permission-dependent resource
interpretation is a different declared family, requiring its own semantics.

## Ownership and boundary

V8 supplies the process and response constructors. The kernel bridge reuses
V21 endpoint execution; Python directly traverses the actual V8 transitions. Word induction earns this gate's
relationship to accumulated requirements. The resulting monotone incidence has
the classical structure used in monotone Boolean and transversal reasoning.
Nothing here identifies hidden permission requirements from observation, proves
a physical causal model, or gives an all-history impossibility decision procedure.
