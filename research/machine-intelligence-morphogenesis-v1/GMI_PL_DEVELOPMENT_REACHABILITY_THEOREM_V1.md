# GMI PL Development-Reachability Theorem v1

Status: **FORMAL NONLINEAR DEVELOPMENT HARDENING / CONDITIONAL SUFFICIENT LAW**

Status date: 2026-09-12.

Purpose:

> Extend exact quadratic development laws to a broader smooth possibly nonconvex regime. Give GMI a falsifiable sufficient condition under which gradient development has finite predictable burden, and contrast it with exact gradient-dead counterexamples.

---

# 1. Setup

Let development objective

\[
f:\mathbb R^d\to\mathbb R
\]

have global/registered infimum `f*` and be differentiable.

Assume on the entire trajectory region:

## L-smoothness

\[
\|\nabla f(x)-\nabla f(y)\|
\le
L\|x-y\|.
\]

## Polyak–Łojasiewicz condition

For some `mu>0`,

\[
\frac12\|\nabla f(x)\|^2
\ge
\mu(f(x)-f^*)
\]

for every trajectory state.

The PL condition does not require convexity.

---

# 2. Smooth descent lemma

For an `L`-smooth function,

\[
f(x-\eta\nabla f(x))
\le
f(x)
-
\eta\left(1-\frac{L\eta}{2}\right)
\|\nabla f(x)\|^2.
\]

For step size

\[
\eta=1/L,
\]

this becomes

\[
f(x_{t+1})
\le
f(x_t)-\frac1{2L}\|\nabla f(x_t)\|^2.
\]

---

# 3. Theorem PL-1 — geometric developmental convergence

Under `L`-smoothness and the `mu`-PL condition, gradient descent with `eta=1/L` satisfies

\[
f(x_{t+1})-f^*
\le
\left(1-\frac\mu L\right)
(f(x_t)-f^*).
\]

Hence

\[
f(x_t)-f^*
\le
\left(1-\frac\mu L\right)^t
(f(x_0)-f^*).
\]

### Proof

Combine the smooth descent inequality with

\[
\frac12\|\nabla f(x_t)\|^2
\ge
\mu(f(x_t)-f^*).
\]

QED.

---

# 4. Developmental burden to an adequacy threshold

Suppose protected development is considered adequate when

\[
f(x_t)-f^*\le\epsilon.
\]

## Corollary PL-1.1

It is sufficient that

\[
t
\ge
\frac{
\ln((f(x_0)-f^*)/\epsilon)
}{
-\ln(1-\mu/L)
}.
\]

Using `-ln(1-u)>=u` for `u in (0,1)`, the simpler sufficient estimate

\[
t
\ge
\frac L\mu
\ln\frac{f(x_0)-f^*}{\epsilon}
\]

captures the standard condition-number-like scaling up to integer rounding.

### GMI consequence

A species can have finite representational adequacy but still fail developmental viability. Under a verified PL/smoothness region, however, development burden becomes explicitly bounded by:

```text
initial excess loss
smoothness L
PL constant mu
target tolerance epsilon
per-step resource cost
```

These feed directly into `B*_dev`.

---

# 5. Relation to quadratic coefficient learning

For strongly convex quadratics, a PL inequality holds and the theorem recovers a geometric convergence law consistent with the earlier spectral analysis.

The quadratic spectral theorem is sharper because it tracks the exact eigendirection contraction. PL-1 is broader but coarser.

A valid general theory should reduce to both in their overlap.

---

# 6. Exact counterexample: dead ReLU violates PL

In `GMI_NEURAL_REACHABILITY_MICROTHEOREMS_V1.md`, the one-parameter ReLU task has, for every `w<0`,

\[
f(w)-f^*=1/2>0
\]

but

\[
\nabla f(w)=0.
\]

Therefore no `mu>0` can satisfy

\[
\frac12\|\nabla f(w)\|^2
\ge
\mu(f(w)-f^*)
\]

on a region containing those dead states.

This explains the exact developmental trap as failure of gradient dominance.

---

# 7. Reachable-region rather than global condition

A system need not satisfy PL everywhere. It is enough for a theorem like PL-1 that the registered development trajectory remains inside a region where the constants hold.

Thus initialization, curriculum, architecture, normalization or optimizer may matter because they determine which geometric region is reached.

The zero-prior prediction target becomes:

> can development enter and remain in a region with enough gradient dominance and tolerable smoothness to reach the semantic threshold within budget?

---

# 8. Stochastic-development gap

Real neural training uses stochastic gradients. PL-type stochastic convergence results require additional assumptions on gradient bias/variance and step schedules.

GMI must therefore register separately:

```text
full-gradient geometry
stochastic gradient variance/noise
batch/source process
optimizer state/momentum
trajectory-region validity
```

No deterministic PL claim may be silently transferred to SGD.

---

# 9. Gap update

`GKF-02` / T1 now contains:

```text
strictly convex quadratic exact spectral law         CLOSED
exact nonlinear dead-region counterexample           CLOSED
leaky-activation accessibility counterfactual        CLOSED
overparameterized linear implicit selection          CLOSED
smooth PL-region finite-burden sufficient law         CLOSED

pre-outcome PL/smoothness estimator for real nets     OPEN
feature-learning region transitions                  OPEN-BLOCKING
stochastic optimizer extension                       OPEN-BLOCKING
deep-network held-family reachability prediction      OPEN-BLOCKING
```

---

# 10. Claim ceiling

The PL condition is a strong conditional assumption. Many neural objectives do not satisfy a useful global PL inequality. This theorem supplies a sufficient development law and calibration target, not a claim of universal neural trainability.
