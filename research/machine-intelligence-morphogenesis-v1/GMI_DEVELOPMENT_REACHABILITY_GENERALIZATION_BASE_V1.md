# GMI Development Reachability and Generalization Base v1

Status: **FORMAL CALIBRATION THEORY / ZERO-PRIOR BASE CASE**

Status date: 2026-09-12.

Purpose:

> Give GMI exact/standard base-case laws for two quantities that remain major blockers in neural zero-prior derivation: data needed to identify a reusable law, and optimization steps needed to reach a coefficient solution.

These theorems are not a solution to deep-network optimization/generalization. They are reduction targets that the broader theory must recover in simple regimes.

---

# 1. Finite-law family: description complexity implies data burden

Let `H` be a finite family of deterministic predictors with `|H|=M`. Assume realizability: the true predictor `h*` belongs to `H`. Examples are drawn IID from a fixed source distribution. Use zero-one error.

## Theorem DG-1 — consistent finite-class learner bound

For any `epsilon in (0,1)` and `delta in (0,1)`, after `n` IID examples, the probability that there exists a hypothesis `h in H` with true error greater than `epsilon` but zero empirical error is at most

\[
M(1-\epsilon)^n
\le
M e^{-n\epsilon}.
\]

Therefore if

\[
n\ge
\frac{\ln M+\ln(1/\delta)}{\epsilon},
\]

then every empirically consistent hypothesis has true error at most `epsilon` with probability at least `1-delta`.

### Proof

For a fixed hypothesis with true error `p>epsilon`, the probability that `n` IID samples miss every error is `(1-p)^n < (1-epsilon)^n`. Union bound over at most `M` hypotheses gives the result. QED.

## Corollary DG-1.1 — semantic family size links memory and learning burden

The same quantity `log M` that lower-bounds exact identity of one law among `M` candidates also controls the finite-class sample bound.

Thus, in a registered finite-law ecology,

\[
\text{state description complexity}
\leftrightarrow
\text{developmental data burden}
\]

through `log M`.

This gives GMI a first-principles reason to prefer a compact reusable law when the legal target family is small: it reduces both retained state and identification burden.

### Negative twin

If the target family is the unrestricted set of `q^N` exact labelings on `N` independent keys, then

\[
\ln M=N\ln q.
\]

The data/description advantage of a compact shared law disappears without additional structure.

### Claim boundary

This is a finite realizable IID classification theorem. Real regression/neural systems need approximation, noise, non-IID development, continuous parameter precision and implicit bias. Those remain separate atoms.

---

# 2. Exact gradient-development law for quadratic coefficient learning

Consider the strictly convex quadratic objective

\[
L(\theta)=\frac12(\theta-\theta^*)^T H(\theta-\theta^*)+C,
\]

where `H` is symmetric positive definite with eigenvalues

\[
0<\mu=\lambda_{min}(H)\le\lambda_{max}(H)=L.
\]

Gradient descent with constant step size `eta` gives

\[
\theta_{t+1}=\theta_t-\eta\nabla L(\theta_t).
\]

Let `e_t=theta_t-theta*`.

## Theorem DG-2 — exact spectral reachability law

\[
e_t=(I-\eta H)^t e_0.
\]

Therefore the worst-direction Euclidean contraction factor per step is exactly

\[
\rho(\eta)=\max_i|1-\eta\lambda_i(H)|.
\]

Convergence for every initialization occurs iff

\[
0<\eta<\frac{2}{L}.
\]

### Proof

`nabla L(theta)=H(theta-theta*)`; substituting yields `e_{t+1}=(I-eta H)e_t`. Orthogonally diagonalize `H` and apply the recurrence independently in each eigendirection. QED.

## Theorem DG-3 — optimal constant step for the spectral interval

Among constant step sizes minimizing the worst contraction over all eigenvalues in `[mu,L]`,

\[
\eta^*=\frac{2}{L+\mu}
\]

and

\[
\rho^*=\frac{L-\mu}{L+\mu}
=\frac{\kappa-1}{\kappa+1},
\qquad
\kappa=\frac{L}{\mu}.
\]

### Consequence

To reduce the worst-direction parameter error by a factor `epsilon`, it is sufficient/necessary in the worst eigendirection that

\[
(\rho^*)^t\le\epsilon,
\]

so

\[
t\ge
\frac{\ln(1/\epsilon)}{-\ln\rho^*}.
\]

Condition number is therefore an exact pre-outcome optimization-burden coordinate in this base regime.

## Negative twins

```text
mu -> 0:
    condition number diverges and the worst-direction convergence becomes arbitrarily slow.

eta >= 2/L:
    some eigendirection fails to contract; development can diverge or oscillate without convergence.

preconditioning changes spectrum:
    the same representational family can have radically different development burden.
```

### GMI consequence

Representation sufficiency alone cannot predict developmental viability. GMI must include optimization geometry in `B*_dev`.

For quadratic coefficient machines, the relevant exact coordinates include

```text
spectral interval [mu,L]
condition number kappa
initial error decomposition
step-size policy
optimization horizon
```

---

# 3. Relationship to neural zero-prior derivation

The deep-network gap is now more precisely stated.

A satisfactory neural development law must reduce to DG-2/DG-3 in a locally quadratic/linear regime but also account for:

```text
nonconvex basin accessibility
feature learning / representation change
flat directions and degeneracy
stochastic gradients
implicit regularization
width/depth effects
normalization/residual dynamics
data curriculum and optimizer state
```

A candidate neural theory that cannot recover the quadratic spectral law in the appropriate limit fails a basic calibration.

---

# 4. Updated gap typing

```text
GKF-01 shared-law compressibility:
    finite exact family -> log(M) state + finite-class data law CLOSED
    approximate/noisy real family -> OPEN

GKF-02 neural reachability:
    strictly convex quadratic coefficient regime CLOSED
    nonlinear/nonconvex feature-learning regime OPEN-BLOCKING

GKF-03 neural generalization:
    finite realizable hypothesis family CLOSED conditionally
    modern overparameterized continuous neural regime OPEN-BLOCKING
```

---

# 5. Claim ceiling

These theorems make the remaining neural gap smaller and falsifiable; they do not imply that condition number or finite-class size alone explains deep learning.

The next step is to test candidate nonlinear descriptors against protected families while requiring exact recovery of these base laws in their limiting regimes.
