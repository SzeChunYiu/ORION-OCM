# GMI Margin, Clustering and Boosting Theorems v1

Status: **FORMAL ZERO-PRIOR CLASSICAL-FAMILY HARDENING**

Status date: 2026-09-12.

Purpose:

> Add three mathematically crisp calibration families that GMI should derive from obligation geometry rather than historical names: max-margin separation, squared-distance clustering, and additive weak-learner boosting.

---

# 1. Maximum-margin linear classification

Given binary-labeled points `(x_i,y_i)` with `y_i in {-1,+1}`, consider affine classifier

\[
f(x)=\operatorname{sign}(w^Tx+b).
\]

Assume the data are linearly separable.

For any separating `(w,b)`, rescale so

\[
y_i(w^Tx_i+b)\ge1.
\]

Then geometric margin is at least

\[
\gamma=\frac1{\|w\|_2}.
\]

## Theorem MB-1 — max margin equals minimum norm under canonical scaling

Among linearly separating hyperplanes with functional margin at least 1, maximizing geometric margin is exactly equivalent to minimizing

\[
\frac12\|w\|_2^2
\]

subject to

\[
y_i(w^Tx_i+b)\ge1.
\]

### Derivation consequence

If the protected classification obligation is linearly separable and robustness to bounded input perturbation matters, GMI derives a coefficient state with a **margin/norm objective**, not merely any zero-training-error separator.

### Robustness corollary

For a point with signed score `m_i=y_i(w^Tx_i+b)>0`, any perturbation `delta` with

\[
\|\delta\|_2<\frac{m_i}{\|w\|_2}
\]

cannot flip that point's classification by Cauchy–Schwarz.

Thus margin has direct protected perturbation semantics.

### Negative twin

If labels are not linearly separable, hard-margin feasibility fails and GMI must add slack/loss, nonlinear features/kernel geometry, explicit memory, or a different carrier.

---

# 2. Cluster centroids from squared distortion

Let points assigned to one cluster be `x_1,...,x_n in R^d`. For representative `mu`, squared distortion is

\[
J(\mu)=\sum_{i=1}^n\|x_i-\mu\|_2^2.
\]

## Theorem MB-2 — cluster mean is the unique squared-error prototype

The minimizer is

\[
\mu^*=\frac1n\sum_i x_i.
\]

### Proof

Expand around the mean:

\[
\sum_i\|x_i-\mu\|^2
=
\sum_i\|x_i-\mu^*\|^2+n\|\mu-\mu^*\|^2.
\]

QED.

### GMI derivation consequence

When exemplar distinctions can be approximated by a small number of squared-distance prototypes, GMI derives **prototype compression**: retain cluster representatives rather than every exemplar.

This is the structural basis of k-means/centroid-like memory without assuming that algorithm historically.

---

# 3. Alternating assignment/update monotonically decreases k-means objective

Given `K` prototypes, define objective

\[
J=\sum_i\min_j\|x_i-\mu_j\|^2.
\]

## Theorem MB-3 — Lloyd-style coordinate descent monotonicity

Two alternating operations never increase `J`:

1. assign each point to its nearest current prototype;
2. replace each prototype by the mean of its assigned points.

### Proof

Nearest assignment independently minimizes each point's contribution for fixed prototypes. By MB-2, replacing a prototype by its cluster mean minimizes cluster distortion for fixed assignments. QED.

### Claim boundary

This proves monotonic descent to a local fixed point, not global optimality. Initialization/search remains a developmental-reachability issue.

---

# 4. Weak learner edge and additive boosting

Consider weighted binary examples with normalized weights `D_t(i)`. Weak learner `h_t in {-1,+1}` has weighted error

\[
\epsilon_t=P_{i\sim D_t}[h_t(x_i)\ne y_i]<\frac12.
\]

Define edge

\[
\gamma_t=\frac12-\epsilon_t>0
\]

and choose

\[
\alpha_t=\frac12\log\frac{1-\epsilon_t}{\epsilon_t}.
\]

The additive classifier score after `T` rounds is

\[
F_T(x)=\sum_{t=1}^T\alpha_t h_t(x).
\]

## Parent theorem MB-4 — exponential training-error bound

Under the standard multiplicative AdaBoost reweighting,

\[
\frac1n\sum_i\mathbf 1[y_iF_T(x_i)\le0]
\le
\prod_{t=1}^T Z_t,
\]

where

\[
Z_t=2\sqrt{\epsilon_t(1-\epsilon_t)}
=\sqrt{1-4\gamma_t^2}
\le e^{-2\gamma_t^2}.
\]

Hence

\[
\text{training error}
\le
\exp\left(-2\sum_{t=1}^T\gamma_t^2\right).
\]

### GMI derivation consequence

A staged additive residual/correction species is developmentally attractive when each affordable new weak learner retains a positive edge on the current weighted residual/error distribution.

The key zero-prior coordinate is **accessible weak-learner edge**, not the historical word `boosting`.

### Negative twin

If every legal weak learner has `epsilon_t=1/2` on the current residual distribution, then `gamma_t=0`, `Z_t=1`, and the theorem gives no progress. More rounds do not create guaranteed improvement.

---

# 5. Relationship among memory, prototype and coefficient state

GMI now has a graded exact/approximate sequence:

```text
arbitrary independent distinctions:
    explicit exemplar/table lower bound

metric-Lipschitz local structure:
    nearest-neighbor memory error controlled by coverage radius

clusterable squared-distance structure:
    prototype/centroid compression

low-rank/global basis structure:
    coefficient/factor compression
```

These are not disconnected historical algorithms. They are different compression points selected by the geometry of semantic variation and lifecycle prices.

---

# 6. Gap update

```text
max-margin classifier property:
    hard-margin/norm equivalence and perturbation margin CLOSED
    feature/kernel geometry selection OPEN

prototype/k-means property:
    optimal centroid and alternating monotonicity CLOSED
    K selection/global-search/metric adequacy OPEN

boosting/additive correction:
    weak-edge exponential training bound PARENT-THEOREM CLOSED
    zero-prior weak-edge accessibility/generalization estimator OPEN
```

---

# 7. Claim ceiling

These results cover exact classical base regimes. They do not establish global convergence of k-means, guarantee test generalization from boosting training error, or select a kernel/feature map for max-margin classification.
