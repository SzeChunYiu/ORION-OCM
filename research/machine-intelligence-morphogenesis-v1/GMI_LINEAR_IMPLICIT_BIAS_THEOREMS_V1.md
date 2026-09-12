# GMI Linear Implicit-Bias Theorems v1

Status: **FORMAL DEVELOPMENT-LAW HARDENING / EXACT OVERPARAMETERIZED LINEAR REGIME**

Status date: 2026-09-12.

Purpose:

> Prove in an exact overparameterized base case that the development rule selects among many equally training-perfect realizations. This separates representational capacity from developmental selection and supplies a calibration target for broader neural implicit-bias/generalization theory.

---

# 1. Underdetermined realizable linear system

Let

\[
X\in\mathbb R^{n\times d},\qquad n<d,
\]

and assume `X` has full row rank and the system

\[
X\theta=y
\]

is realizable.

Consider squared loss

\[
L(\theta)=\frac12\|X\theta-y\|_2^2
\]

and gradient descent

\[
\theta_{t+1}=\theta_t-\eta X^T(X\theta_t-y).
\]

---

# 2. Row-space invariance

## Theorem IB-1 — zero initialization stays in the data row space

If

\[
\theta_0=0,
\]

then for every `t`,

\[
\theta_t\in\operatorname{row}(X)=\operatorname{im}(X^T).
\]

### Proof

The initial state is in the row space. Every update increment is of the form `X^T v`, hence also lies in the row space. Induction completes the proof. QED.

---

# 3. Minimum-norm interpolant

Because `X` has full row rank, the unique interpolating solution in the row space is

\[
\theta_*=X^T(XX^T)^{-1}y.
\]

## Theorem IB-2 — row-space interpolant is the minimum-Euclidean-norm solution

Every solution to `X theta=y` can be uniquely decomposed as

\[
\theta=\theta_*+z,
\qquad z\in\ker X,
\]

with `theta_*` orthogonal to `z`. Therefore

\[
\|\theta\|_2^2=\|\theta_*\|_2^2+\|z\|_2^2,
\]

so `theta_*` is the unique minimum-norm interpolant.

---

# 4. Gradient descent selects the minimum-norm interpolant

Let nonzero eigenvalues of `X^TX` lie in `[mu,L]` on the row space.

## Theorem IB-3 — zero-initialized gradient descent converges to the minimum-norm interpolant

If

\[
0<\eta<\frac{2}{L},
\]

then

\[
\theta_t\to\theta_*=X^T(XX^T)^{-1}y.
\]

### Proof

By IB-1, all iterates remain in the row space, where `X^TX` is positive definite. The quadratic spectral convergence theorem applies on that subspace. The unique zero-loss point in the row space is `theta_*`. QED.

### GMI consequence

Among infinitely many representationally equivalent exact fits, the registered update law plus initialization selects a specific semantic/developmental state.

Representation alone does not determine the trained species.

---

# 5. Initialization nullspace is preserved

Write arbitrary initialization as

\[
\theta_0=r_0+z_0,
\qquad
r_0\in\operatorname{row}(X),\quad z_0\in\ker X.
\]

## Theorem IB-4 — nullspace component is invariant under gradient descent

For every `t`,

\[
\operatorname{Proj}_{\ker X}\theta_t=z_0.
\]

If the row-space component converges, the limiting interpolant is

\[
\theta_\infty=\theta_*+z_0.
\]

### Proof

Every gradient `X^T(Xtheta-y)` lies in the row space and is orthogonal to `ker X`; updates cannot change the nullspace projection. QED.

### Interpretation

Even in a convex loss with no bad local minima, initialization can select among indistinguishable training solutions when the parameterization is overcomplete.

---

# 6. Ridge regularization removes the exact nullspace ambiguity

For

\[
L_\lambda(\theta)=\frac12\|X\theta-y\|^2+\frac\lambda2\|\theta\|^2,
\qquad \lambda>0,
\]

the objective is strictly convex with unique minimizer

\[
\theta_\lambda=(X^TX+\lambda I)^{-1}X^Ty.
\]

As `lambda -> 0+`,

\[
\theta_\lambda\to X^T(XX^T)^{-1}y=\theta_*.
\]

Thus explicit norm regularization and zero-initialized gradient descent select the same minimum-norm limit in this registered setting by different mechanisms.

---

# 7. Generalization is not determined by the training solution alone

Minimum parameter norm is a development-law property, but whether it predicts low protected risk depends on the source distribution/target geometry.

Two worlds can agree on `(X,y)` and therefore produce the same `theta_*` while assigning different labels/distributions off the observed training subspace.

Therefore implicit bias can explain **which interpolant is selected**, but a separate source assumption is still required to predict generalization.

This is consistent with the zero-prior identifiability no-go: training fit plus optimizer does not distribution-free identify unseen semantics.

---

# 8. Gap update

`GKF-02 neural reachability/development` gains:

```text
quadratic spectral convergence                         CLOSED
nonlinear dead-ReLU accessibility counterexample      CLOSED
overparameterized linear implicit selection           CLOSED
initialization-nullspace dependence                    CLOSED
```

`GKF-03 neural generalization` gains a sharper decomposition:

```text
which interpolant development selects                 CLOSED in linear base case
whether that interpolant generalizes                  source-dependent / OPEN
```

Remaining open:

```text
implicit bias of nonlinear feature-learning networks
stochastic optimizer effects
normalization/depth/width dependent selection
generalization under realistic source assumptions
held-family predictive law
```

---

# 9. Claim ceiling

These theorems are exact for overparameterized linear least squares. They do not imply that modern deep networks minimize Euclidean parameter norm or that minimum norm universally explains neural generalization.
