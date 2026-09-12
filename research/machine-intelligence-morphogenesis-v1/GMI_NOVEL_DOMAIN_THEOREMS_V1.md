# GMI Novel-Domain Theorems v1

Status: **EXACT FINITE THEORY HARDENING / DOMAIN NOVELTY NOT ESTABLISHED**

Status date: 2026-09-12.

Purpose:

> Turn selected novel-domain hypotheses into exact theorem statements, prove what is actually true, and explicitly record where the stronger new-domain claim fails or remains open.

This file deliberately distinguishes four levels:

```text
W0 EXISTENCE          native carrier/operator can solve a registered family
W1 NECESSITY/COMPRESSION
                      native state captures a distinction or compression absent from a weaker descriptor
W2 PARENT SEPARATION  no accepted bounded reduction to strongest existing domains
W3 EMPIRICAL NICHE    protected experiments recover the predicted frontier advantage
W4 DOMAIN STATUS      recurrent, parent-nonreducible structural domain at registered scope
```

Mathematics below can establish W0/W1 and selected parent-relative separations. It cannot by itself establish W3/W4.

---

# 1. N3 Relational-Constraint / Sheaf Intelligence

## 1.1 Exact parity-cycle family

Let `C_n` be a cycle with Boolean vertex variables

\[
x_1,\ldots,x_n\in\{0,1\}
\]

and edge constraints

\[
x_i\oplus x_{i+1}=b_i,\qquad i=1,\ldots,n
\]

with indices modulo `n`.

The local carrier consists of edge-local constraints. The global question is whether these local sections glue to one globally consistent assignment.

## Theorem N3-T1 — one-bit global obstruction

A global assignment exists iff

\[
\bigoplus_{i=1}^{n} b_i=0.
\]

If it exists, exactly two global assignments exist.

### Proof

XOR all `n` edge equations. Every vertex variable occurs exactly twice, hence cancels:

\[
\bigoplus_i(x_i\oplus x_{i+1})=0.
\]

Therefore global consistency requires `XOR_i b_i=0`.

Conversely, assume the parity is zero. Choose `x_1` arbitrarily. Recursively define

\[
x_{i+1}=x_i\oplus b_i.
\]

The final edge is satisfied exactly because the total XOR of the `b_i` is zero. The two choices of `x_1` give exactly two solutions. QED.

## Corollary N3-C1

For the solvability obligation, the global obstruction is exactly one bit:

\[
o(b)=\bigoplus_i b_i.
\]

The full set of `2^n` candidate vertex assignments is unnecessary.

## Negative twin

If the obligation is to output a particular full assignment rather than only decide existence, the obstruction bit is insufficient. At least one additional global degree of freedom is needed even in the consistent case.

## Parent-reduction result

A symbolic CSP/program machine computes the same parity obstruction in `O(n)` time and `O(1)` extra working memory after reading the constraints. Therefore N3-T1 establishes a real local-to-global obstruction mechanism but **does not establish N3 as a new domain relative to D4 symbolic/program computation**.

Current status:

```text
W0 GREEN
W1 GREEN
W2 OPEN / currently reduced on this family
W3 OPEN
W4 OPEN
```

This is consistent with current sheaf-theoretic distributed-computing work, where global sections encode task solutions and cohomological obstructions characterize incompatibility; that literature is a strong parent and must receive first refusal.

---

# 2. N8 Constructive / Autocatalytic Intelligence

## 2.1 Direct-constructor family

Let there be `k` possible future modules

\[
m_1,\ldots,m_k.
\]

For every bit vector

\[
a=(a_1,\ldots,a_k)\in\{0,1\}^k,
\]

define a machine `M_a` whose **current execution behavior is identical** for all `a`, but whose constructor set contains a direct constructor for `m_j` iff `a_j=1`.

The future ecology may issue challenge `j`, requiring the machine to instantiate `m_j` within the registered construction budget.

## Theorem N8-T1 — present-behavior insufficiency

No descriptor that depends only on current input-output behavior can exactly predict future challenge success for this family.

### Proof

All `M_a` have identical present input-output behavior by construction. Choose two bit vectors `a,a'` differing in coordinate `j`. The descriptor is identical, but future challenge `j` succeeds for one system and fails for the other. Therefore present behavior is not a sufficient developmental state. QED.

## Theorem N8-T2 — constructive-capability information lower bound

Any exact developmental descriptor that predicts success for all `k` future challenges must have at least `2^k` distinct states, hence at least `k` bits in the worst case.

### Proof

There are `2^k` distinct future response signatures, one for each `a`. If two different signatures shared one descriptor state, they differ on some challenge `j` and the descriptor would make the same prediction for two systems with different correct outcomes. Thus the descriptor must distinguish all `2^k` signatures. QED.

## Theorem N8-T3 — constructor closure is sufficient on the direct-builder family

Let

\[
Cl(M_a)=\{m_j:a_j=1\}.
\]

Then `Cl(M_a)` is an exact developmental sufficient state for all registered future challenges.

### Proof

Challenge `j` succeeds iff `m_j\in Cl(M_a)`. QED.

## Stronger interpretation

The theorem proves a genuine missing-state result:

> two machines can be identical in current morphology and current behavior yet differ in future intelligence because their reachable constructive closures differ.

This is stronger than an ordinary current-capability benchmark.

## Parent-reduction result

A sufficiently rich D8 morphogenetic/self-rewriting state can simply include the constructor set or a program generating its closure. Therefore these theorems establish **constructive closure as necessary developmental state**, but not yet a distinct domain beyond D8/D4.

A true W2 separation would require an obligation family where native constructive closure has a material lifecycle/scaling advantage over every bounded D8/D4 encoding, not merely a renamed state variable.

Current status:

```text
W0 GREEN
W1 GREEN — k-bit lower bound
W2 OPEN
W3 OPEN
W4 OPEN
```

---

# 3. N10 Event-Causal / Partial-Order Intelligence

## 3.1 Independent-event family

Consider `n` independent one-shot events. Any subset may already have happened; events may occur in any order.

## Theorem N10-T1 — snapshot state explosion

The ordinary global completed/not-completed snapshot space has exactly

\[
2^n
\]

reachable states.

### Proof

Every event independently has two statuses, and every subset of completed events is reachable. QED.

## Theorem N10-T2 — interleaving explosion

The number of complete total-order execution traces is

\[
n!.
\]

### Proof

Every permutation of the `n` independent events is a valid execution order. QED.

## Theorem N10-T3 — exact partial-order representation

The same execution family is represented exactly by an event structure with `n` event nodes and no causal edges or conflicts.

Every total execution is a linear extension of this one partial order.

Thus the carrier description is `O(n)` while extensional complete-trace listing is at least `Omega(n!)` traces and explicit snapshot reachability is `2^n` states.

## Important reduction result

This is a real representational separation against **naive extensional interleaving/snapshot representations**, but not against D4 symbolic/program systems: Petri nets, event structures, process calculi and unfolding methods already encode true concurrency compactly.

Therefore on the registered family:

```text
N10 works as a representation mechanism;
N10 does not currently survive D4 parent reduction.
```

Current status:

```text
W0 GREEN
W1 GREEN
W2 RED against strong D4 parent at this scope
W3 OPEN
W4 DEMOTED unless a stronger family is found
```

---

# 4. N11 Invariant / Obstruction Intelligence

## 4.1 Free-group-action family

Let

\[
X=A\times G
\]

where finite group `G` acts freely on the second coordinate. Let the protected target depend only on `a\in A` and be injective in `a`.

All states `(a,g)` for fixed `a` are semantically equivalent for this obligation.

## Theorem N11-T1 — optimal quotient-state cardinality

The minimum exact deterministic semantic state cardinality is exactly

\[
|A|.
\]

### Proof

At least `|A|` states are necessary because the target takes `|A|` distinct protected values. The quotient map

\[
q(a,g)=a
\]

uses exactly `|A|` states and is sufficient. QED.

## Corollary N11-C1 — exact information saving

Raw identity requires

\[
\log_2|A|+\log_2|G|
\]

bits, whereas the target quotient requires only

\[
\log_2|A|
\]

bits, saving exactly

\[
\log_2|G|.
\]

## Negative twin

If the protected obligation changes to reconstruct `(a,g)` exactly, the quotient is no longer sufficient and `|A||G|` states are necessary.

## Reduction result

This theorem is an exact instance of the already established GMI semantic-quotient theorem. It demonstrates why invariant representations can be optimal, but **does not create a new structural domain**.

Current status:

```text
W0 GREEN
W1 GREEN
W2 RED — reduced to general GMI quotient mechanism / D1-D4 realizations
W3 OPEN as an implementation family
W4 DEMOTED
```

---

# 5. What these proofs actually establish

The exact conclusions are intentionally narrower than the original hypotheses.

| Candidate | Exact mathematical result | Domain result |
|---|---|---|
| N3 relational/sheaf | local constraints can carry a one-bit global gluing obstruction; exact finite proof | mechanism works; new-domain status open and currently reducible to symbolic parents on the test family |
| N8 constructive | future constructive closure is information-theoretically necessary for developmental prediction; `k` independent future capabilities require `k` bits | strongest surviving candidate here; domain separation still open |
| N10 event/partial-order | `O(n)` native event representation vs `2^n` snapshots / `n!` interleavings | works, but strong symbolic parent already realizes the compression; demote at current scope |
| N11 invariant | quotient cardinality is exactly optimal; saves orbit-information bits | direct corollary of semantic quotient theory; not a new domain at current scope |

The correct scientific update is therefore:

> mathematical usefulness is much easier to prove than domain novelty.

A domain claim requires a parent-relative lower bound, not just an elegant representation.

---

# 6. Required next theorem class: parent-relative separation

For a surviving candidate `N`, define candidate burden `r_N(n)` and strongest-parent burden `r_P(n)` on the same protected obligation family.

The required W2 theorem is of the form

\[
\forall P\in\mathcal P_{strong},\qquad
r_P(n)\ge f(n),
\]

while

\[
r_N(n)\le g(n),
\]

with a material separation, ideally

\[
\frac{f(n)}{g(n)}\to\infty.
\]

The parent class must be constrained by a **representation/operation contract**, not by a weak implementation strawman. Otherwise a universal program representation simply reimplements the candidate and erases the claimed separation.

This is the central unresolved mathematical challenge for genuinely new classical domains.

---

# 7. New candidate-generation rule after theorem hardening

A new candidate should not be promoted merely because it admits an exact compact representation.

Prefer candidates where all three are plausible:

```text
1. novel sufficient-state object;
2. native operator algebra that is expensive to compile into parent domains under a meaningful contract;
3. natural complexity coordinate that predicts protected capability better than parent coordinates.
```

This rule substantially raises the bar for the next domain-generation cycle.

---

# 8. Claim ceiling

Allowed:

> Exact finite theorems now establish local-global obstruction sufficiency, constructive developmental-state necessity, partial-order compression and quotient-state optimality on registered families.

Not allowed:

```text
N3 is a new domain
N8 is a new domain
N10 is a new domain
N11 is a new domain
any theorem above establishes real-world superiority
```

The next decisive result must be a **strong-parent burden-separation theorem or protected empirical phase law**, especially for N8 and any future candidate that survives this theorem filter.