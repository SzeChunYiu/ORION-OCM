# GMI Transfer Modulus Theorems v1

Status: **FORMAL CROSS-ECOLOGY HARDENING / EXACT BASE BOUNDS**

Status date: 2026-09-12.

Purpose:

> Replace vague claims of "transfer" with quantitative bounds relating ecology/source shift to protected-risk shift. Also state exact support-shift no-go results showing when source evidence cannot determine target performance at all.

---

# 1. Setup

Fix one developed machine/species `M`. Let source ecology distribution be `P` and target ecology distribution be `Q` over registered task instances `z`.

Let protected loss be

\[
\ell_M(z)\ge0.
\]

Define risks

\[
R_P(M)=\mathbb E_P\ell_M(Z),
\qquad
R_Q(M)=\mathbb E_Q\ell_M(Z).
\]

A **transfer modulus** is any justified function `omega` such that

\[
|R_Q(M)-R_P(M)|\le\omega(P,Q,M)
\]

for the registered assumptions.

There is no universal small modulus without assumptions on both distribution shift and loss geometry.

---

# 2. Total-variation bound for bounded protected loss

Assume

\[
0\le\ell_M(z)\le L_{max}.
\]

Use total variation convention

\[
TV(P,Q)=\sup_A|P(A)-Q(A)|
=\frac12\|P-Q\|_1
\]

when densities/masses exist.

## Theorem TM-1 — bounded-loss transfer modulus

\[
\boxed{
|R_Q(M)-R_P(M)|
\le
L_{max}\,TV(P,Q)
}
\]

### Proof

For any measurable `f` with values in `[0,L_max]`, the variational characterization of total variation gives

\[
|\mathbb E_P f-\mathbb E_Q f|
\le L_{max}TV(P,Q).
\]

Apply `f=ell_M`. QED.

### Interpretation

Small total-variation shift guarantees small protected-risk shift only when loss is bounded. High-consequence unbounded tails require stronger control.

---

# 3. Density-ratio transfer bound

Assume `Q` is absolutely continuous with respect to `P` and

\[
w(z)=\frac{dQ}{dP}(z)
\le W
\]

almost surely, for finite `W>=1`.

## Theorem TM-2 — multiplicative target-risk bound

For nonnegative loss,

\[
\boxed{
R_Q(M)
=\mathbb E_P[w(Z)\ell_M(Z)]
\le
W R_P(M)
}
\]

### Consequence

A source risk bound transfers multiplicatively when target density does not overweight any source-covered region by more than `W`.

### Negative twin

If no finite density-ratio bound exists because target concentrates heavily on rare source events, tiny average source risk can coexist with large target risk.

---

# 4. Wasserstein transfer for Lipschitz loss

Let task space carry metric `d`, and suppose machine loss is `K`-Lipschitz:

\[
|\ell_M(z)-\ell_M(z')|
\le
K d(z,z').
\]

## Parent theorem TM-3 — Wasserstein-1 transfer modulus

By Kantorovich-Rubinstein duality,

\[
\boxed{
|R_Q(M)-R_P(M)|
\le
K W_1(P,Q)
}
\]

where `W_1` is the Wasserstein-1 distance.

### GMI interpretation

A species can transfer under geometrically smooth ecology shift even when exact support points change, provided its protected loss changes smoothly in the task metric.

The relevant coordinates are therefore:

```text
ecology transport distance
loss/task sensitivity K
```

not merely whether train and test datasets have different names.

---

# 5. Support-shift no-go

Let there exist measurable set `A` such that

\[
P(A)=0,
\qquad
Q(A)=\alpha>0.
\]

## Theorem TM-4 — source data cannot distribution-free determine target loss on unseen support

There exist two legal loss worlds `ell_0,ell_1` that agree `P`-almost surely but have different target risks by as much as `alpha L_max` under bounded loss.

### Construction

Set both losses equal outside `A`. On `A`, set

\[
\ell_0=0,
\qquad
\ell_1=L_{max}.
\]

Since `P(A)=0`, all source-risk/source-observation statistics are identical. But

\[
R_Q(\ell_1)-R_Q(\ell_0)
=\alpha L_{max}.
\]

QED.

### Consequence

No source-only estimator can certify target behavior on genuinely unseen support without a structural assumption, intervention, simulator/model, or target data.

This is the transfer analogue of the zero-prior identifiability collisions.

---

# 6. Obligation-relative transfer

Raw input distribution shift can be large while semantic obligation shift is small, or vice versa.

Let semantic quotient be

\[
q(z)=s.
\]

If machine loss depends only on `s`, transfer should be measured on the induced quotient distributions

\[
P_S=q_\#P,
\qquad
Q_S=q_\#Q,
\]

rather than necessarily on raw surface distributions.

## Theorem TM-5 — quotient transfer can be tighter

If `ell_M(z)=\tilde\ell_M(q(z))`, then

\[
R_P(M)=\mathbb E_{P_S}\tilde\ell_M(S),
\qquad
R_Q(M)=\mathbb E_{Q_S}\tilde\ell_M(S).
\]

Therefore TM-1/TM-3 may be applied directly to semantic quotient distributions.

### Interpretation

A surface remint that preserves semantic quotient can have large raw distance but zero semantic transfer penalty.

Conversely, a tiny surface change that flips a high-loss semantic distinction can have large protected impact.

---

# 7. Transfer of capability envelopes

For species `S` with development budget `b`, let protected capability/loss envelope be

\[
L_S^*(P,b).
\]

A transfer theorem for one fixed developed machine does not automatically transfer the whole developmental envelope: target ecology can alter which development path/morphology is optimal.

Define developmental transfer regret

\[
Reg_{P\to Q}(b)
=
L_Q(S_P^*(b))-L_Q^*(b),
\]

where `S_P^*(b)` is source-optimal development under budget `b`.

This is the correct quantity for asking whether a **species/development policy**, not just a frozen predictor, transfers.

Bounding it requires additional assumptions about how candidate-development losses shift across ecologies.

---

# 8. Parent/model selection under shift

Suppose two realizations `A,B` have source risk gap

\[
R_P(A)-R_P(B)=\Delta_P.
\]

If both have bounded-loss transfer moduli `omega_A,omega_B`, then target ordering is guaranteed preserved whenever

\[
|\Delta_P|>\omega_A+\omega_B
\]

with the appropriate sign.

### GMI consequence

A morphology/family preference near the source frontier should not be claimed to transfer when uncertainty/modulus exceeds the observed source advantage.

This gives an abstention criterion for cross-family predictions.

---

# 9. Transfer modulus as a registered prediction object

For every transfer claim report:

```text
source ecology P
target ecology Q
semantic quotient used for comparison
loss/capability coordinate
assumption class
estimated distance/divergence
loss sensitivity / density-ratio bound
resulting risk uncertainty interval
support-shift audit
morphology-development change audit
```

A single average transfer score is not enough.

---

# 10. Gap update

Former transfer-modulus gap now has exact bases:

```text
bounded-loss TV transfer                                CLOSED
bounded density-ratio target-risk transfer              CLOSED
Lipschitz-loss Wasserstein transfer                      PARENT-THEOREM CLOSED
unseen-support impossibility                             CLOSED
semantic-quotient transfer framing                      CLOSED
source-family ordering robustness criterion              CLOSED

real semantic quotient/distance estimation               OPEN
loss-sensitivity estimation                              OPEN
source-optimal development -> target-optimal regret      OPEN-BLOCKING
protected cross-domain/species transfer                  OPEN-BLOCKING
```

---

# 11. Claim ceiling

These are standard/elementary distribution-shift bounds integrated into GMI. They do not prove arbitrary real-world transfer. Their role is to make transfer claims assumption-indexed, quantitative and falsifiable, and to identify support shift as a hard no-go for source-only certainty.
