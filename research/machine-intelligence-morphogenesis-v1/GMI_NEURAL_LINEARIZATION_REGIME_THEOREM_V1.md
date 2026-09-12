# GMI neural linearization regime theorem v1

Status: **FORMAL FEATURE-DRIFT REGIME BOUND / T1-T2 NARROWING**

Date: 2026-09-12.

Purpose: give GMI a measurable condition under which a developed neural system is well described by its initial linearized/fixed-feature model, and a falsifier for explanations that assume a frozen kernel while features materially change.

## 1. Response map and Jacobian regularity

Let a finite registered probe set produce vector response

\[
f:\mathbb R^p\to\mathbb R^m
\]

with Jacobian `J(theta)`. Let development move from `theta_0` to `theta=theta_0+Delta`.

Assume the Jacobian is `L_J`-Lipschitz in operator norm along the segment:

\[
\|J(\theta_0+u)-J(\theta_0+v)\|_{op}
\le L_J\|u-v\|_2.
\]

## 2. Theorem NL-1 — exact Taylor remainder bound

The linearized predictor is

\[
f_{lin}(\theta_0+\Delta)=f(\theta_0)+J_0\Delta.
\]

Then

\[
\boxed{
\|f(\theta_0+\Delta)-f_{lin}(\theta_0+\Delta)\|_2
\le \frac{L_J}{2}\|\Delta\|_2^2
}.
\]

### Proof

Use the fundamental theorem of calculus:

\[
f(\theta_0+\Delta)-f(\theta_0)-J_0\Delta
=\int_0^1[J(\theta_0+t\Delta)-J_0]\Delta\,dt.
\]

Apply the Lipschitz bound and integrate `t`. QED.

## 3. Theorem NL-2 — tangent-kernel drift bound

Define the finite-probe tangent Gram matrix

\[
K(\theta)=J(\theta)J(\theta)^T.
\]

Let `r=||Delta||` and `M=||J_0||_{op}`. The Jacobian drift is at most `L_J r`. Hence

\[
\boxed{
\|K(\theta)-K(\theta_0)\|_{op}
\le 2M L_J r+(L_Jr)^2
}.
\]

### Proof

Write `J=J_0+E`, `||E||<=L_Jr`. Then

\[
JJ^T-J_0J_0^T=J_0E^T+EJ_0^T+EE^T
\]

and apply submultiplicativity. QED.

## 4. Registered fixed-feature regime

For a required response tolerance `epsilon_f` and tangent-kernel drift tolerance `epsilon_K`, a sufficient fixed-feature/lazy condition over the registered probe set is

\[
\frac{L_J}{2}r^2\le\epsilon_f
\]

and

\[
2ML_Jr+(L_Jr)^2\le\epsilon_K.
\]

Inside this regime, explanations and response laws based on the initial feature/Jacobian geometry have an explicit approximation guarantee on the probe set.

Outside it, a fixed-kernel explanation has **no guarantee from this theorem**; feature/Jacobian evolution must be measured rather than assumed negligible.

## 5. Feature-learning pressure is not feature-learning success

Large certified kernel drift can establish that fixed-feature approximation is poor, but it does not prove the changed features are useful or improve protected generalization. Conversely, small parameter motion in a highly curved map can still produce material feature drift.

Thus GMI should separate:

```text
representation/feature drift
optimization progress
protected-risk improvement
```

rather than label every non-lazy trajectory “feature learning” in a beneficial sense.

## 6. Negative twins

- Linear model: `L_J=0`; the linearization is exact for arbitrarily large parameter movement.
- Small movement/curvature: fixed-feature explanation is certified locally.
- Large `r` or curvature: initial NTK/fixed-feature response laws need not transfer.
- Probe-set insufficiency: small drift on an incomplete probe set does not prove global function/kernel stability.

## 7. GMI consequence

A zero-prior neural development descriptor should include measurable intervals for

```text
parameter displacement r
Jacobian norm M
Jacobian curvature/Lipschitz scale L_J
tangent-kernel drift
protected response linearization error
```

This provides one explicit bridge between the fixed-kernel and representation-changing regimes.

## Claim ceiling

This is a deterministic local/finite-probe regime bound. It does not solve high-dimensional feature-learning dynamics, stochastic SGD, or generalization; it tells the theory when a fixed-feature approximation is or is not justified.
