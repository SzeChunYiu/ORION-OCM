# GMI Metric Memory and Low-Rank Derivations v1

Status: **FORMAL ZERO-PRIOR KNOWN-FAMILY HARDENING**

Status date: 2026-09-12.

Purpose:

> Derive two major classical machine-intelligence properties from measurable geometry: nearest-neighbor/case memory from metric smoothness and coverage, and low-rank/PCA-like state from optimal rank-constrained approximation.

---

# 1. Nearest-neighbor memory from Lipschitz geometry

Let `(X,d)` be a metric space and target function

\[
f:X\to\mathbb R
\]

be `L`-Lipschitz:

\[
|f(x)-f(x')|\le L d(x,x').
\]

Let memory contain exact labeled exemplars

\[
S=\{(x_i,f(x_i))\}_{i=1}^n.
\]

For query `x`, choose a nearest stored exemplar

\[
x_{NN}(x)\in\arg\min_{x_i\in S}d(x,x_i)
\]

and predict

\[
\hat f(x)=f(x_{NN}(x)).
\]

## Theorem MM-1 — exact Lipschitz nearest-neighbor error bound

For every query,

\[
|f(x)-\hat f(x)|
\le
L d(x,S),
\]

where

\[
d(x,S)=\min_{x_i\in S}d(x,x_i).
\]

If the registered query set/domain has covering radius

\[
r(S)=\sup_x d(x,S),
\]

then

\[
\|f-\hat f\|_\infty\le Lr(S).
\]

### Proof

Apply Lipschitz continuity to `x` and its nearest stored exemplar. QED.

### GMI derivation consequence

Explicit exemplar memory is justified when:

```text
metric/similarity geometry is meaningful
local variation is bounded/smooth
coverage radius is small enough for the protected tolerance
writes are cheap or target is locally volatile
shared global compression is not much cheaper
```

The zero-prior complexity coordinate is not `kNN` by name; it is approximately

\[
L\times r(S)
\]

combined with memory/search/update burden.

### Negative twin

If no useful Lipschitz/metric relation exists, nearby exemplars need not constrain the target. Then storing more nearby cases can fail to reduce protected error predictably, and the memory family degenerates toward arbitrary lookup.

---

# 2. Coverage burden and dimensionality

Suppose a compact metric domain requires `N(epsilon)` exemplars to achieve covering radius at most `epsilon`.

Then MM-1 implies that target error at most `tau` is guaranteed when

\[
r(S)\le\frac{\tau}{L}.
\]

Thus an upper bound on required memory is the covering number

\[
N(\tau/L).
\]

### Interpretation

Nearest-neighbor/case-memory capability can scale badly when the metric covering number grows rapidly with dimension. This gives GMI a structural explanation for both its strength in local low-dimensional regimes and its weakness under high-dimensional sparse coverage.

---

# 3. Low-rank representation from optimal rank-constrained approximation

Let data/operator matrix

\[
A\in\mathbb R^{m\times n}
\]

have singular values

\[
\sigma_1\ge\sigma_2\ge\cdots\ge0.
\]

## Parent theorem MM-2 — Eckart–Young–Mirsky

Among all matrices `B` of rank at most `r`, the truncated singular-value decomposition

\[
A_r=\sum_{i=1}^r\sigma_i u_i v_i^T
\]

minimizes Frobenius approximation error, with

\[
\min_{\operatorname{rank}(B)\le r}\|A-B\|_F^2
=
\sum_{i>r}\sigma_i^2.
\]

This is established parent mathematics.

### GMI derivation consequence

Define retained spectral mass

\[
E_r=\sum_{i\le r}\sigma_i^2
\]

and residual mass

\[
R_r=\sum_{i>r}\sigma_i^2.
\]

If rank-`r` state/factor burden `C_r` plus registered approximation penalty `lambda R_r` is lower than the burden of full state, GMI should derive a low-rank latent/factor representation.

This is a zero-prior route to PCA/factor models/low-rank matrix states without historical architecture names.

---

# 4. Exact resource/loss crossover

Let full representation burden be `C_full`. Under squared Frobenius semantic loss, rank `r` is preferred iff

\[
C_r+\lambda\sum_{i>r}\sigma_i^2<C_{full}.
\]

The best registered rank solves

\[
r^*\in\arg\min_r
\left(C_r+\lambda\sum_{i>r}\sigma_i^2\right).
\]

### Negative twin

If the spectrum is flat and protected tolerance is strict, tail energy remains large until `r` approaches full rank. The low-rank advantage disappears.

---

# 5. Relation to adapters and representation learning

The same singular/rank geometry appears in several distinct settings:

```text
PCA/factor representation:
    low rank in data/state covariance or matrix structure

low-rank adaptation:
    low rank in required update/residual matrix

mode sharing:
    low rank in stacked mode-parameter matrix
```

These are not one species, but they share a common GMI mechanism: a low-dimensional linear subspace carries most of the registered semantic variation.

---

# 6. Gap update

Known-family derivation gains:

```text
kNN/case memory:
    exact Lipschitz/covering error law CLOSED
    metric validity, intrinsic dimension and real search cost OPEN

PCA/low-rank factor state:
    optimal rank-error law PARENT-THEOREM CLOSED
    pre-outcome effective spectrum under task semantics OPEN
```

---

# 7. Claim ceiling

The Lipschitz theorem is deterministic and the low-rank theorem is classical matrix approximation. Real nearest-neighbor systems require metric learning/noise handling; real representation learning may discover nonlinear manifolds rather than linear subspaces. Those remain separate response-law atoms.
