# GMI Symmetry Core + Residual Theorems v1

Status: **FORMAL ZERO-PRIOR HARDENING / EXACT LINEAR DECOMPOSITION**

Status date: 2026-09-12.

Purpose:

> Replace an all-or-nothing equivariant-versus-free choice with the exact decomposition naturally implied by the GMI residual theory: a reusable equivariant core plus a symmetry-breaking residual whose own complexity determines whether exceptions should be localized.

---

# 1. Orthogonal decomposition under a finite group

Let finite group `G` act orthogonally on the input/output space and let

\[
\Pi_G(A)=\frac1{|G|}\sum_{g\in G}R_g^T A R_g
\]

be the Frobenius projection onto the equivariant operator subspace.

Define

\[
A_{sym}=\Pi_G(A),
\qquad
R=A-A_{sym}.
\]

## Theorem SCR-1 — unique symmetric-core/residual decomposition

Every linear operator admits the orthogonal decomposition

\[
A=A_{sym}+R
\]

where `A_sym` is `G`-equivariant and `R` is Frobenius-orthogonal to every `G`-equivariant operator.

Moreover this decomposition uniquely minimizes residual norm among all equivariant cores:

\[
\|R\|_F^2
=
\min_{B\in\mathrm{Eq}(G)}\|A-B\|_F^2.
\]

This is the projection theorem already established in the symmetry-response layer.

---

# 2. Exact core + residual realization

Suppose exact protected semantics require the full operator `A`, so discarding `R` is not admissible.

Let:

```text
C_sym       lifecycle/state burden of the equivariant core
C_res(R)    burden of an exact residual realization
C_full      burden of an unrestricted full realization
```

## Theorem SCR-2 — exact hybrid adoption criterion

The exact symmetric-core + residual realization is cheaper than a full free operator iff

\[
C_{sym}+C_{res}(R)<C_{full}.
\]

The fully tied approximation is preferable only when the protected loss penalty for discarding `R` plus `C_sym` is cheaper than both exact alternatives.

Thus the correct three-way registered comparison is

\[
\min\left\{
C_{sym}+\lambda\|R\|_F^2,
\;
C_{sym}+C_{res}(R),
\;
C_{full}
\right\}.
\]

---

# 3. Sparse symmetry breaking

Assume residual `R` has exactly `s` nonzero entries over an alphabet/precision that costs `b_v` bits per nonzero value and index cost `b_i` per location.

A direct sparse residual code has burden approximately

\[
C_{res}^{sparse}
\le
s(b_i+b_v)+C_{indexing}.
\]

## Corollary SCR-2.1

If symmetry violations are sparse enough that

\[
C_{sym}+C_{res}^{sparse}<C_{full},
\]

then exact **shared core + local exceptions** is predicted even though strict equivariance is false.

### Negative twin

If symmetry-breaking residual is dense/unstructured, sparse residual burden approaches/exceeds the full free representation; GMI should abandon the hybrid.

---

# 4. Low-rank symmetry breaking

If residual matrix has low rank `r`, use the finite/real low-rank residual machinery.

A factorized residual has state burden scaling like

\[
O(r(m+n))
\]

parameters/field symbols rather than `mn` full entries.

## Corollary SCR-2.2

A globally symmetry-breaking but low-rank deviation can favor an equivariant core plus low-rank adapter rather than either exact hard tying or full untied parameters.

This connects the symmetry and adaptation theories without introducing a new architecture primitive.

---

# 5. Locality + symmetry residual

For convolution/local sharing, residual complexity can also be organized by location or factor.

Suppose most spatial regions obey one shared local rule but a subset `J` requires distinct local rules. Then the exact target can be represented as:

```text
one shared local operator
+ indexed local overrides on J
```

The phase boundary is the ordinary residual-versus-full law:

\[
C_{shared}+C_{override}(J)<C_{all\ local\ free}.
\]

Thus GMI predicts local specialization around symmetry violations rather than globally abandoning sharing when exceptions are localized.

---

# 6. Developmental interpretation

If the world initially obeys symmetry and later develops a small set of exceptions, rewriting all shared parameters can cause interference and unnecessary update burden.

A local residual state can preserve the stable symmetric core while admitting changes.

This yields a natural developmental progression:

```text
exact symmetry
    -> hard shared realization

small structured violation
    -> shared core + sparse/low-rank/local residual

dense persistent violation
    -> weaker sharing or full untied realization
```

This is a quantitative morphology transition, not an architecture-name rule.

---

# 7. Correction to the exact zero-prior symmetry twin

The predecessor toy used:

```text
positive: exactly circulant matrix
negative: one entry flipped
```

and compared only:

```text
strict orbit tying
free matrix
```

Within that candidate set, the winner flip is exact.

But the stronger neutral-search expectation should include a third candidate:

```text
orbit-tied core + one sparse exception
```

For a one-entry violation, that hybrid can be cheaper than the fully free matrix.

Therefore the predecessor twin is **not** a sufficient negative control for all sharing; it is only a negative control for *strict exact tying*.

The correct protected prediction is:

> one sparse symmetry violation should generally produce shared-core + residual when residual indexing burden is cheaper than freeing the entire operator.

---

# 8. Gap update

`GKF-04 approximate symmetry` is further narrowed:

```text
exact group projection / deviation                      CLOSED
strict sharing vs approximation crossover              CLOSED
exact shared-core + residual decomposition              CLOSED
sparse/low-rank residual hybrid law                    CLOSED
real task symmetry/residual complexity estimator        OPEN-BLOCKING
neutral recovery of hybrid under broad grammar          OPEN
```

---

# 9. Claim ceiling

These are exact linear representation/resource identities conditional on registered coding costs. They do not establish that real neural training will find the optimal decomposition or that symmetry residuals are sparse/low-rank in a given task.
