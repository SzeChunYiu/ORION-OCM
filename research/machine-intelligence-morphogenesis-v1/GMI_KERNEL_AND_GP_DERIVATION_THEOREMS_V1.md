# GMI Kernel and Gaussian-Process Derivation Theorems v1

Status: **FORMAL ZERO-PRIOR KNOWN-FAMILY HARDENING / PARENT THEORY INTEGRATION**

Status date: 2026-09-12.

Purpose:

> Derive finite kernel expansions and kernel-based probabilistic belief states from the geometry of function-space regularization and Gaussian conditioning rather than historical family names.

---

# 1. RKHS development objective

Let `H` be a reproducing-kernel Hilbert space with kernel `k`. Given observations at `x_1,...,x_n`, consider objectives of the form

\[
J(f)=\Phi(f(x_1),...,f(x_n))+\lambda\|f\|_H^2,
\qquad \lambda>0,
\]

where `Phi` is any loss depending on the function only through its values on the observed points.

Let

\[
S=\operatorname{span}\{k(x_1,\cdot),...,k(x_n,\cdot)\}.
\]

## Theorem KG-1 — representer theorem by orthogonal decomposition

Every minimizer of `J` lies in `S`. Therefore it has a finite expansion

\[
f^*(\cdot)=\sum_{i=1}^n\alpha_i k(x_i,\cdot).
\]

### Proof

For arbitrary `f in H`, decompose

\[
f=f_S+f_\perp
\]

with `f_S in S` and `f_perp orthogonal S`.

By the reproducing property,

\[
f_\perp(x_i)=\langle f_\perp,k(x_i,\cdot)\rangle_H=0
\]

for every observed point. Hence `Phi` is identical for `f` and `f_S`, while

\[
\|f\|_H^2=\|f_S\|_H^2+\|f_\perp\|_H^2.
\]

With `lambda>0`, any nonzero orthogonal component strictly increases the objective. QED.

### GMI derivation consequence

When the ecology supplies:

```text
similarity geometry encoded by k
loss depending on observed function values
function-complexity penalty in the corresponding RKHS norm
```

GMI should derive a finite weighted similarity expansion over observed anchors. No historical `kernel method` macro is required.

---

# 2. Resource law

The exact representation uses at most `n` coefficients plus kernel/reference state. Serving a new query by naive evaluation costs `O(n)` kernel evaluations.

Thus kernel realization has a natural lifecycle trade:

```text
small/moderate n + useful prior similarity geometry:
    attractive

very large n with expensive kernel evaluation:
    serving burden grows unless approximation/sparsification is introduced
```

A finite-dimensional explicit feature map can move the realization toward coefficient state when that is cheaper.

---

# 3. Negative twin

The representer theorem does **not** choose a good kernel. If registered similarity geometry is unrelated to the target semantics, the finite expansion is still mathematically valid but can generalize poorly or require many anchors.

Therefore the zero-prior unresolved variable is kernel/geometry adequacy, not existence of a kernel expansion.

---

# 4. Gaussian-process belief state

Let a finite vector of latent function values be jointly Gaussian. Partition latent variables into observed/training values `f_X` and query values `f_*`:

\[
\begin{bmatrix}f_X\\f_*\end{bmatrix}
\sim
\mathcal N\left(
\begin{bmatrix}m_X\\m_*\end{bmatrix},
\begin{bmatrix}K_{XX}&K_{X*}\\K_{*X}&K_{**}\end{bmatrix}
\right).
\]

With Gaussian observation noise variance `sigma^2`, observed labels are

\[
y=f_X+\epsilon.
\]

## Parent theorem KG-2 — Gaussian conditioning

The exact posterior query distribution is Gaussian with

\[
\mathbb E[f_*|y]
=
m_*+K_{*X}(K_{XX}+\sigma^2I)^{-1}(y-m_X),
\]

and

\[
\operatorname{Cov}(f_*|y)
=
K_{**}-K_{*X}(K_{XX}+\sigma^2I)^{-1}K_{X*}.
\]

### GMI derivation consequence

If uncertainty over a smooth/similarity-structured function is semantically required and Gaussian closure is a good approximation, the posterior state has two first-class components:

```text
posterior mean / prediction
posterior covariance / uncertainty
```

This is a concrete instance of the general probabilistic-belief domain derivation.

---

# 5. Computational phase law

Naive exact GP update/inference involves solving with the `n x n` covariance matrix, typically cubic preprocessing/factorization burden and quadratic state in `n` absent structure.

Therefore exact GP-like belief is predicted to lose lifecycle advantage as `n` becomes large unless the kernel admits exploitable structure or sparse/low-rank approximations.

This gives a zero-prior pressure toward inducing points, low-rank features, local kernels or parametric compression without naming those historical methods.

---

# 6. Gap update

```text
kernel expansion existence under RKHS regularization        CLOSED
finite kernel serve-burden structure                         CLOSED
Gaussian posterior mean/covariance form                      PARENT-THEOREM CLOSED
kernel/geometry adequacy estimator                            OPEN-BLOCKING
large-n sparse/approximate representation selection           OPEN
protected kernel-vs-parametric-vs-memory crossover            OPEN
```

---

# 7. Claim ceiling

These results derive structural properties given an RKHS/Gaussian prior geometry. They do not solve the zero-prior problem of discovering the right kernel or proving that real targets satisfy Gaussian-process assumptions.
