# GMI Multi-Task Gradient Interference Theorems v1

Status: **FORMAL NONLINEAR LOCAL HARDENING / CONDITIONAL SPECIALIZATION DEVELOPMENT LAW**

Status date: 2026-09-12.

Purpose:

> Extend shared-versus-specialized theory from static mode-rank geometry to actual differentiable development. Quantify when an update for one task/mode helps or harms another through gradient alignment and curvature.

---

# 1. Two differentiable task losses

Let shared parameter state be

\[
\theta\in\mathbb R^d.
\]

Task/mode losses are differentiable functions

\[
L_i(\theta),\qquad L_j(\theta).
\]

Define gradients

\[
g_i=\nabla L_i(\theta),
\qquad
g_j=\nabla L_j(\theta).
\]

Take one gradient step for task `j`:

\[
\theta'=\theta-\eta g_j,
\qquad \eta>0.
\]

---

# 2. First-order interference law

## Theorem GI-1 — local cross-task effect

As `eta -> 0`,

\[
L_i(\theta')-L_i(\theta)
=
-\eta g_i^Tg_j+O(\eta^2).
\]

Thus:

```text
g_i^T g_j > 0:
    the j-update locally helps task i to first order

g_i^T g_j = 0:
    no first-order cross-task effect

g_i^T g_j < 0:
    the j-update locally harms task i to first order
```

### Proof

Apply the first-order Taylor expansion of `L_i` at `theta` in direction `-eta g_j`. QED.

---

# 3. Finite-step curvature bound

Assume `L_i` has `beta_i`-Lipschitz gradient on the segment between `theta` and `theta'`. By the descent/smoothness lemma,

\[
L_i(\theta-\eta g_j)
\le
L_i(\theta)
-
\eta g_i^Tg_j
+
\frac{\beta_i\eta^2}{2}\|g_j\|^2.
\]

## Theorem GI-2 — sufficient finite-step no-harm condition

A sufficient condition for the `j` update not to increase task `i`'s loss is

\[
g_i^Tg_j
\ge
\frac{\beta_i\eta}{2}\|g_j\|^2.
\]

### Interpretation

Positive alignment must be large enough to dominate curvature at the chosen step size. Merely having nonnegative cosine similarity is not a finite-step guarantee.

---

# 4. Guaranteed interference under negative alignment

Assume additionally a matching lower smoothness/Taylor remainder bound such as Hessian operator norm at most `beta_i` in absolute value along the segment. Then

\[
L_i(\theta-\eta g_j)
\ge
L_i(\theta)
-
\eta g_i^Tg_j
-
\frac{\beta_i\eta^2}{2}\|g_j\|^2.
\]

## Corollary GI-2.1

If

\[
-g_i^Tg_j
>
\frac{\beta_i\eta}{2}\|g_j\|^2,
\]

then the update provably increases `L_i`.

This is an exact local **negative-transfer certificate** under the registered curvature bound.

---

# 5. Gradient-alignment matrix

For `m` modes define

\[
G_{ij}=g_i^Tg_j
\]

or normalized cosine matrix

\[
C_{ij}=
\frac{g_i^Tg_j}{\|g_i\|\|g_j\|}
\]

when gradients are nonzero.

### GMI interpretation

Static parameter mode rank measures how many independent directions the exact mode functions require.

Gradient alignment measures whether **learning those functions through shared parameters is developmentally cooperative or conflicting** at the current state.

Both matter:

```text
low mode rank + aligned gradients:
    strong pressure toward shared realization

high mode rank but aligned reusable features:
    sharing may still be developmentally efficient

strong persistent negative gradient interactions:
    specialization/local modules/routing become more valuable
```

---

# 6. Exact specialization removes direct shared-coordinate interference

Partition parameters into disjoint blocks

\[
\theta=(\theta_1,\ldots,\theta_m)
\]

and suppose task `i` depends only on block `theta_i`.

## Theorem GI-3 — block specialization gives exact cross-mode update isolation

An update supported only on block `theta_j` leaves every `L_i` with `i != j` exactly unchanged.

### Proof

By assumption those losses do not depend on `theta_j`. QED.

### Cost

Isolation may duplicate useful parameters, increase memory, reduce statistical sharing and add routing/maintenance burden. It is not automatically optimal.

---

# 7. Shared-core + specialized residual decomposition

Let

\[
\theta=(\theta_{shared},\phi_1,\ldots,\phi_m)
\]

where `phi_i` is mode-local.

This gives a structural compromise:

```text
aligned/common gradient components -> shared core
conflicting/mode-specific components -> local residual blocks
```

The optimal split minimizes:

\[
\text{shared development burden}
+
\text{interference/forgetting penalty}
+
\text{specialist state/serve/routing burden}.
\]

This is the development analogue of the earlier representation-level shared-basis + residual law.

---

# 8. Gradient projection as a local anti-interference mechanism

For one old task with gradient `g_o`, an update direction `d` has zero first-order effect on old loss when

\[
g_o^Td=0.
\]

Projecting a proposed new-task direction onto the orthogonal complement of old gradients can remove first-order interference, subject to curvature and loss of new-task progress.

This links multi-task specialization to the continual-learning nullspace theory.

---

# 9. Negative twins

## Perfect alignment

If all task gradients are positive scalar multiples of one another in the relevant development region, parameter isolation removes useful transfer and duplicates state without reducing interference.

## Independent observable modes with disjoint semantics

If gradients remain strongly conflicting and routing is cheap, specialized blocks can dominate shared updates.

## Changing alignment

A system can begin with aligned low-level features and become conflicting at higher-level specialization. Static architecture choice may therefore be inferior to developmental morphogenesis.

---

# 10. Gap update

`GKF-06 conditional specialization` / T5 now has:

```text
mode-span rank representation law                    CLOSED
execute-all versus routed serving law                CLOSED
local gradient-interference law                      CLOSED
finite-step curvature-aware no-harm condition        CLOSED
exact block-isolation theorem                        CLOSED
shared-core + local-residual structural compromise   CLOSED

pre-outcome/early-development alignment prediction   OPEN
alignment drift across training                      OPEN-BLOCKING
router/load-balance/communication lifecycle law      OPEN-BLOCKING
protected dense-vs-specialized prediction            OPEN-BLOCKING
```

---

# 11. Claim ceiling

These are local differentiable-development laws. They do not prove gradient alignment remains stable through training, that neural MoE is globally optimal under conflict, or that block specialization beats other anti-interference mechanisms.
