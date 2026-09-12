# GMI Stability Generalization Theorems v1

Status: **FORMAL GENERALIZATION HARDENING / EXACT EXPECTATION BOUNDS**

Status date: 2026-09-12.

Purpose:

> Add algorithmic stability as a second exact base mechanism for generalization, complementary to finite-class description complexity. GMI should not force all generalization phenomena into one complexity measure.

---

# 1. Setup

Let training sample

\[
S=(z_1,\ldots,z_n)
\]

be IID from distribution `D`. Learning algorithm `A` outputs hypothesis `A(S)`. Loss is `ell(h,z)`.

Define population and empirical risks

\[
R(h)=\mathbb E_{z\sim D}\ell(h,z),
\qquad
\hat R_S(h)=\frac1n\sum_{i=1}^n\ell(h,z_i).
\]

For `S,S'` differing in one example, algorithm `A` has **uniform stability beta** if

\[
|\ell(A(S),z)-\ell(A(S'),z)|\le\beta
\]

for every test point `z`.

---

# 2. Expected generalization from uniform stability

## Theorem SG-1 — expected generalization gap is bounded by stability

If `A` has uniform stability `beta`, then

\[
\left|
\mathbb E_S[R(A(S))-\hat R_S(A(S))]
\right|
\le\beta.
\]

### Proof

Let `z_i'` be an independent ghost example and let `S^{(i)}` be `S` with `z_i` replaced by `z_i'`.

By exchangeability,

\[
\mathbb E_{S,z_i'}\ell(A(S^{(i)}),z_i')
=
\mathbb E_S\ell(A(S),z_i).
\]

Also

\[
\mathbb E_S R(A(S))
=
\mathbb E_{S,z_i'}\ell(A(S),z_i').
\]

Subtract and use stability:

\[
\left|
\mathbb E[R(A(S))]-\mathbb E[\ell(A(S),z_i)]
\right|
\le\beta.
\]

Average over `i`. QED.

### GMI interpretation

Generalization can arise because the **development map itself is insensitive to one-example perturbations**, even when the representational family is very large.

Thus development/update geometry belongs in the generalization theory.

---

# 3. Strongly regularized convex ERM is stable

Let parameter `w in R^d`. Assume for every example `z`, loss `ell(w,z)` is convex and `L`-Lipschitz in Euclidean norm:

\[
|\ell(w,z)-\ell(w',z)|\le L\|w-w'\|.
\]

Train by

\[
w_S
\in
\arg\min_w
\left[
\frac1n\sum_{i=1}^n\ell(w,z_i)
+\frac\lambda2\|w\|^2
\right],
\qquad \lambda>0.
\]

The objective is `lambda`-strongly convex.

## Theorem SG-2 — replace-one parameter stability

For datasets `S,S'` differing in one example,

\[
\|w_S-w_{S'}\|
\le
\frac{2L}{\lambda n}.
\]

### Proof sketch

Strong convexity gives

\[
F_S(w_{S'})\ge F_S(w_S)+\frac\lambda2\|w_S-w_{S'}\|^2
\]

and symmetrically for `F_{S'}`. Adding the inequalities cancels all common-example losses; only the replaced pair remains. Lipschitzness bounds the remaining difference by

\[
\frac{2L}{n}\|w_S-w_{S'}\|.
\]

Cancel one nonzero distance factor to obtain the result. QED.

## Corollary SG-2.1 — uniform loss stability

By Lipschitzness,

\[
|\ell(w_S,z)-\ell(w_{S'},z)|
\le
\frac{2L^2}{\lambda n}.
\]

Hence SG-1 gives

\[
\left|\mathbb E[R(w_S)-\hat R_S(w_S)]\right|
\le
\frac{2L^2}{\lambda n}.
\]

---

# 4. Resource/capability tradeoff

Increasing regularization `lambda` improves this stability bound but can increase approximation/bias loss. Therefore the zero-prior objective must balance at least:

\[
\text{approximation/bias}(\lambda)
+
\text{development/generalization instability}(\lambda,n)
+
\text{resource burden}.
\]

This is a concrete bias-stability-development phase law rather than “regularization is good.”

---

# 5. Negative twins

## Unstable interpolation

If changing one sample can cause order-one changes in predictions/loss, `beta` need not shrink with `n`; SG-1 supplies no small generalization guarantee even if empirical loss is zero.

## No distribution-free conclusion from train fit alone

Two development algorithms can achieve identical empirical loss while having very different stability. Thus training error alone is not a sufficient predictor of protected risk.

---

# 6. Relationship to other generalization mechanisms

GMI now has at least two formally distinct base mechanisms:

```text
finite semantic/hypothesis family:
    log(M) / PAC-style identification burden

algorithmic stability:
    small sensitivity of learned predictor to development-sample perturbation
```

Other mechanisms may matter in other regimes:

```text
margin/norm geometry
PAC-Bayes posterior/prior complexity
spectral/effective dimension
compression
implicit bias
feature-learning/source alignment
```

The theory should compare them empirically rather than prematurely collapsing them into one universal scalar.

---

# 7. Gap update

`GKF-03 neural/generalization` now contains:

```text
finite realizable family bound                     CLOSED
uniform-stability expected gap                     CLOSED
regularized convex ERM stability                    CLOSED
training-fit-only sufficiency                       REFUTED
modern overparameterized nonlinear prediction       OPEN-BLOCKING
mechanism-selection among stability/margin/etc      OPEN-BLOCKING
```

---

# 8. Claim ceiling

These are exact expectation/stability results under IID, convexity and Lipschitz/strong-regularization assumptions. They do not prove modern deep-network generalization is explained by uniform stability, nor do they give a universal high-probability neural risk law.
