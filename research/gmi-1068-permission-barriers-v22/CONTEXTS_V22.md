# V22 partial contexts and relative enabling

Read [THEORY_V22.md](THEORY_V22.md). All target and evaluator meanings below
are fixed across the compared permission sets.

## V2.1 — actual admission, image and target incidence

Raw histories are H=X times List A. Fix original P subset H, selector K subset H,
and actual V15 Context (E,nu,preorder). nu is defined on E independently of P.
A fixed-start selector is literally h.start=x; it is not an unused parameter.
Define L_S(h) iff P(h), K(h), and End(M[S],h.start,h.word) succeeds.
The new scenario has admission L_S and exactly the old Context. In particular,
ambient defined values at histories outside L_S do not become attained values.

The actual observation is ILLEGAL outside L_S, UNDEFINED in L_S outside E,
and VALUE(nu(h)) in L_S intersect E. Its attainable image is
A_S={v | exists h in L_S intersect E, nu(h)=v}.
Let target T be declared. Define an eligible witness (h,y,R) by P(h), K(h),
F(h.start,h.word)=(y,R), h in E, and nu(h) in T.
V1.2 then gives
A_S intersects T nontrivially iff exists eligible (h,y,R), R contained in S.
Proof: expand the actual image and target intersection. A left witness supplies
an admitted evaluated history; V1.2 supplies R. Conversely an eligible enabled
witness gives actual gated success and its same evaluated value in A_S and T.
Impossibility is the negation, equivalently no such eligible enabled witness.

If S is contained in S', V1.2 gives L_S contained in L_S'. The unchanged
partial evaluator transports that inclusion to A_S contained in A_S'. This
retains P/E separation and needs no order condition on arbitrary target T.
It does require unchanged evaluations, target meaning and physical semantics.
The image still forgets history identity; witness extraction retains it.

## V2.2 — generic incidence and available permissions

Abstract an eligible witness family W indexed by identities h with support R(h).
Cap(S) means some h in W has R(h) contained in S. The actual construction above
instantiates this definition by a proved equivalence. An arbitrary history
support callback requires that equivalence as an explicit premise instead.

Fix baseline S0 contained in available U. Only W_U={h in W: R(h) contained in U}
can become enabled by permitted additions. Let D be contained in U minus S0.
For h in W_U define deficit d(h)=R(h) minus S0. Then
Cap(S0 union D) iff exists h in W_U, d(h) contained in D.
Proof: R contained in S0 union D iff R minus S0 contained in D; the forward
witness also has R contained in U. Conversely availability and the deficit
inclusion give the original enabled witness. An off-U witness is not a repair.

An enabling addition need not be relief: if Cap(S0) already holds, D=empty
is enabling. Relief additionally requires not Cap(S0). The unique minimal
addition for an already successful baseline is empty; no unique cause follows.

## V2.3 — exact inclusion-minimal additions

Permit the full powerset of U minus S0. Call D minimal enabling when Cap(S0 union
D) and no proper subset of D enables it. Then D is minimal enabling iff D is an
inclusion-minimal member of the family {d(h):h in W_U}.
Forward: extract d(h) contained in D by V2.2. This deficit is itself an allowed
enabling addition, so minimality forces d(h)=D. Any smaller family member would
contradict the same minimality. Reverse: a family member enables; if D' proper
subset D enabled, V2.2 would give a family member d(g) contained in D', strictly
smaller than D, a contradiction. Neither direction requires finite U.
The Python minimal_additions API returns sets, while target_witnesses retains
the complete identity/support records. From those records, select every witness
whose baseline-relative deficit equals the chosen set; these are its backpointers.
No addition-certificate object is silently claimed as a returned API value.

If only a restricted intervention family Delta is permitted, this characterization
can fail because an extracted deficit may not belong to Delta. Example: a target
requires {a}, but the only permitted change is {a,b}; that change is minimal
among allowed changes but is not any witness deficit. Retain Delta membership
and compare its actual enabled contexts instead of silently assuming all subsets.

## V2.4 — conservative old one-history specialization

For baseline histories H0 inside candidate universe H*, assign empty support to
H0 and singleton permission {h} to each h in H* minus H0. Admission with S is
H0 union {h in H* minus H0: h in S}, intersected with any fixed original P.
Use the unchanged partial evaluator. Adding permission h0 gives exactly the
old one-history admission H0 union {h0}; image/target equivalence follows by the
same existential witness. Undefined histories add no value. Different histories
with equal values remain different additions and history witnesses.

This is a generic history-admission specialization. Arbitrary independent
whole-history controls need not be representable by independent edge gates on
a fixed shared graph. The old checker is replayed on its actual declared fixture,
not promoted to a general causal detector. If baseline capability already holds,
its helper can list additions that preserve success; call them relief only under
baseline impossibility. Finite candidate rosters do not exhaust arbitrary words.
