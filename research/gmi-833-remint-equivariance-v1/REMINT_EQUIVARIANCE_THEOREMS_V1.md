# GMI #833 finite semantic remint equivariance v1

**Freeze:** `FREEZE_V1.md`, commit `8af4533512ae8ce97bfd062403e745eea8cfcbec`.  
**Claim ceiling:** `GMI_FINITE_SEMANTIC_REMINT_EQUIVARIANCE_AT_REGISTERED_SCOPE`.

## 1. Registered presentation object

Fix the finite architecture-name-free mechanism signature used by the current #833 morphology work:

`M=(X,x0,A,J,lambda,delta,iota,Delta,rho)`

with finite state carrier `X`, initial state `x0`, external actions `A`, intervention labels `J`, protected state labels `lambda`, total deterministic transition law `delta`, intervention responses `iota`, developmental edges `Delta`, and nonnegative raw resource vector `rho`.

A **state-presentation remint** is a bijection `r:X->X'`. Its action on `M` transports every state-indexed component:

- `x0' = r(x0)`;
- `lambda'(r(x)) = lambda(x)`;
- `delta'(r(x),a)=r(delta(x,a))`;
- `iota'(r(x),j)=iota(x,j)`;
- `(r(x),r(y)) in Delta'` iff `(x,y) in Delta`;
- external alphabets and `rho` are unchanged.

Anything that changes one of those semantic/resource fields is not a pure remint at this scope.

## 2. GAUGE-1A — remints form a groupoid

The identity bijection transports every component to itself. Every bijection `r` has inverse `r^-1`, and transporting by `r` then `r^-1` returns the original presentation. If `r:X->Y` and `s:Y->Z`, the composite `(s o r)(x)=s(r(x))` is a bijection and transporting directly by `s o r` equals sequential transport by `r` then `s` componentwise.

Thus finite presentation remints and their invertible arrows form the expected groupoid. This is ordinary bijection/isomorphism mathematics, not a new GMI theorem family.

## 3. Canonical fingerprint invariance

For an `n`-state mechanism, let `I(M)` be the set of all encodings obtained by assigning the states bijectively to canonical indices `{0,...,n-1}` and serializing the initial marker, external alphabets, protected labels, transitions, intervention responses, developmental edges and exact resource vector under that assignment.

Define

`Canon(M) = min I(M)`

under a fixed lexicographic serialization order.

### Theorem

For every valid remint `r:M->M'`,

`Canon(M)=Canon(M')`.

**Proof.** Every canonical index assignment `p:X->{0,...,n-1}` for `M` corresponds bijectively to assignment `p o r^-1:X'->{0,...,n-1}` for `M'`. Because `r` transports every registered semantic component, the two assignments generate exactly the same serialized structure. Therefore the sets of candidate encodings are equal, so their minima are equal. QED.

The executable witness exhausts all `3! = 6` remints of a three-state mechanism and obtains one fingerprint. Enumeration is a bounded certificate; the proof above supplies the general finite-bijection argument.

## 4. Quotient morphology consequence

The current morphology object is a presentation-independent equivalence class of the registered mechanism structure. Since every pure remint has the same canonical fingerprint, all reminted presentations map to the same finite quotient object.

This does not assert that canonical serialization is the unique or scalable quotient algorithm. It is an exact finite witness implementation.

## 5. Transform-geometry equivariance

Take a finite directed transformation graph whose nodes are presented mechanisms and whose edges carry unchanged nonnegative transform burdens. Quotient each endpoint by `Canon` and compute directed shortest burdens on those quotient nodes.

If every node presentation is independently reminted by a valid semantic remint and the corresponding edges retain the same source/target relation and burden, then every endpoint canonicalizes to its original quotient node. Therefore the canonicalized weighted graph is identical, and its directed shortest-burden matrix is identical.

The executable certificate uses three distinct mechanism classes, four directed transform edges, and nine quotient ordered pairs. Independently reminting all three mechanisms leaves the complete quotient distance matrix unchanged.

This is the finite transformation-geometry equivariance needed before morphology distances can be interpreted as representation-independent at this scope.

## 6. Semantic-mutation hostiles

A claimed remint is rejected when it is non-bijective or when the purported target changes any registered semantic coordinate. Exact hostiles separately mutate:

- protected outputs;
- transitions;
- intervention responses;
- developmental edges;
- lifecycle resources.

All use neutral state names. Thus lexical neutrality is not semantic remint invariance.

## 7. Search/reachability non-inference

GAUGE-1A is a statement about the registered semantic quotient and any transformation geometry built only from preserved quotient objects/burdens. It does **not** prove search invariance.

A finite budget-one control contains two semantically identical candidates but orders them differently. Forward and reverse enumeration return different first candidates. Thus a semantic remint theorem cannot erase encoding length, proposal order, optimizer path, tie rules, or finite search-budget effects.

This boundary is important for the P3/P4 programme: morphology conclusions must eventually survive alternate search implementations as a separate empirical/formal gate.

## 8. Falsifiers

This tranche is RED at its claimed scope if:

- remint identity, inverse, or composition fails;
- two valid remints yield different canonical fingerprints;
- a semantic/resource mutation passes as a pure remint;
- quotient-level transform distances change under valid endpoint remints with unchanged burdens;
- a non-bijective remint is accepted;
- semantic remint invariance is promoted into search/reachability invariance;
- normal and optimized execution disagree.

## 9. Parent ownership and forbidden promotion

Finite structure isomorphism, groupoids of bijections, canonical labeling by exhaustive permutations, and graph-isomorphism invariance are parent mathematics. GMI's residual is the explicit integration of those ideas with the registered morphology signature and transform geometry while preserving the separate search-prior gate.

This tranche does not establish universal grammar neutrality, search-prior invariance, reachability invariance, P3 known-form recovery, unrestricted topology invariance, or complete GMI.
