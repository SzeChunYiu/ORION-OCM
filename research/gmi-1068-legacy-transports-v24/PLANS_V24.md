# V24 — rooted feasible plans and a shared ambient universe

## X3.1 — partial-loss context and exact feasible-plan image

Let plan type K have declared ambient universe U, and let histories H index
admission P_h, defined domain E_h and partial loss L_h:E_h->V. V has a declared
preorder and threshold eps. Define feasible(h,k) iff U(k),P_h(k),E_h(k) and
L_h(k)<=eps. The actual V15 context on plans evaluates to (k,L_h(k)) exactly on
E_h; admission is U and P_h. Its illegal/undefined/value observations remain distinct.
Use the target T={(k,l):l<=eps}. Then projecting the attained target-restricted
image to K gives exactly feasible(h): unpacking an image witness gives the four
conditions, and these conditions supply that same plan witness in reverse.
The context's pair order may be declared by the loss order; threshold membership
here depends on the supplied preorder, not on an unlabelled scalar encoding.

The original prior-free FORMAL_CORE section4 uses total L_Omega on its common
rooted-plan universe. Specialize U to that universe and P_h/E_h to true there.
Then the projection is exactly Gamma_plan_eps(h;s), preserving Omega,s,eps and
all old quantifiers. Partial evaluation is a generalization, not an invented
missing-source behavior. An alternative total identity evaluator with feasibility
placed in admission yields the same feasible set; it does not preserve the original
illegal versus undefined diagnostics, so it is not an equality of full observations.

## X3.2 — one common plan and empty-history semantics

For selected histories B define Common(B)={k:U(k) and for every h in B,feasible(h,k)}.
This is the intersection of feasible plan sets relative to U. Compatibility means
there exists ONE k in Common(B). It is not for each h there exists some plan k_h.
If B is empty, the universal condition is vacuous, so Common(B)=U; compatibility
then holds exactly when U is nonempty. If U is empty no common plan exists.
No finiteness, topology, or pairwise-to-global compactness principle is assumed.

For K={a,b,c}, feasible sets {a,b},{b,c},{a,c} have pairwise witnesses b,c,a,
respectively, but no plan lies in all three. Each plan is missing from one set.
Thus pairwise compatibility does not establish joint compatibility or a unique
coarsest equivalence quotient. The legacy source itself makes this distinction.

## X3.3 — injective transport with mapped ambient universe

Let q:K->K' be injective and keep the same history index/selection B.
Then q(Common(B))=q(U) intersect intersection_(h in B) q(feasible(h)).
Forward: a common witness k maps into q(U) and every mapped feasible set.
Backward: q(U) gives a plan k in U representing a proposed y. For each h in B,
membership of y in q(feasible(h)) gives k_h feasible there with q(k_h)=y=q(k).
Injectivity implies k_h=k; hence k is feasible at every h and is a common witness.
This proof works even for empty B because q(U) still supplies the preimage.
Dropping that mapped-universe guard would replace q(U) by all K' in the empty case.
For inclusion q:{a}->{a,b}, empty-family left side is {a}, not {a,b}.

A noninjective loss projection can fail even for two histories. Let both plans have
loss0 but only a be admitted in h0 and only b in h1. Each feasible loss image is {0},
yet no common plan exists. A shared plan-ID universe is indispensable; equal loss
numbers do not recover which plan realizes each loss.

The general logical/context transport is distinct from finite table calibration,
which must check all P/E outcomes, thresholds and subsets. A source-keyed plan
transport supplies no equivalence between plan Gamma and developmental AF profiles.
