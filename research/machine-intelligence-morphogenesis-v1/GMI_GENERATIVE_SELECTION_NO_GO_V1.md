# GMI generative selection no-go v1

Status: **FORMAL NO-GO / T6 NARROWING**

Date: 2026-09-12.

Purpose: show why semantic likelihood alone cannot derive autoregressive versus latent versus flow versus score/diffusion realization when several families can represent the same target exactly.

## 1. Cross-entropy identity

For target distribution `P` and admissible model `Q` under a common measure,

\[
E_P[-\log q(X)] = H(P)+KL(P\|Q),
\]

with the standard discrete or continuous integrability qualifications.

For realization family `R`, define its best semantic log-loss

\[
L_R^*=H(P)+\inf_{Q\in R}KL(P\|Q).
\]

## 2. Theorem GS-1 — exact-family semantic tie

If two realization families `R_1,R_2` both contain the target distribution `P`, then

\[
L_{R_1}^*=L_{R_2}^*=H(P).
\]

Therefore no selector that observes only the optimum semantic log-likelihood/cross-entropy can distinguish the two families.

This includes any pair of sufficiently expressive exact factorizations on a target lying in both admissible supports.

## 3. Theorem GS-2 — approximation only identifies KL projection, not lifecycle winner

If a family cannot represent `P` exactly, its irreducible semantic penalty is

\[
A_R=\inf_{Q\in R}KL(P\|Q).
\]

But two families with the same `A_R` can have arbitrarily different training, sampling, serving, memory, precision or update burden. Thus `A_R` alone still cannot choose the lifecycle-optimal form.

## 4. Required GMI object

For quality tolerance `epsilon`, define the resource-constrained family envelope

\[
C_R^*(\epsilon)=
\inf_{Q\in R:\ KL(P\|Q)\le\epsilon}
\pi^T B(Q),
\]

where `B` includes development/search, sampling/serve, memory, communication, precision, verification and update costs as applicable.

The generative-family prediction is a **burden-curve comparison**, not a universal semantic-loss ranking.

## 5. Architecture-specific coordinates that still require estimation

```text
AR: conditional-law complexity, sequence depth, cache/reuse and parallelism
flow: invertible transport complexity, Jacobian cost, support/topology constraints
latent: quotient/component complexity, inference/amortization gap, posterior mismatch
score/diffusion: score-field complexity, noising path, solver/sampling steps, discretization error
energy: normalization and mixing/sampling burden
adversarial: witness/discriminator complexity and game optimization accessibility
```

## 6. Negative twin

Any benchmark where all families are allowed unlimited compute and each reaches the exact target has no power to test a GMI morphology prediction: all semantic losses tie at `H(P)`. Such a benchmark can compare implementations only after resources are charged.

## Claim ceiling

This no-go explains why GKF-10 cannot be closed by likelihood theory alone. It does not predict the unresolved family burden curves `C_R^*(epsilon)`; those remain OPEN-BLOCKING and require theory plus protected measurement.
