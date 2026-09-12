# GMI approximate predictive-state spectral theorem v1

Status: **FORMAL FINITE PREDICTIVE-STATE LAW / T4 NARROWING**

Date: 2026-09-12.

Purpose: extend exact future-response/Hankel results to an approximate finite predictive-state dimension with an explicit error spectrum.

## 1. Finite predictive matrix

Let registered histories be `h_1,...,h_m` and registered future tests/events be `t_1,...,t_n`. Define

\[
P_{ij}=Pr(t_j\mid h_i).
\]

A `d`-dimensional linear predictive state is a factorization

\[
P=AB,
\qquad A\in\mathbb R^{m\times d},\ B\in\mathbb R^{d\times n}.
\]

## 2. Theorem PS-1 — exact linear dimension

The minimum exact linear predictive-state dimension equals

\[
rank(P).
\]

### Proof

Any factorization through dimension `d` has `rank(P)<=d`. Conversely, a rank factorization of `P` through `r=rank(P)` gives an exact `r`-dimensional representation. QED.

This is a finite predictive-matrix statement; positivity/stochastic-realizability constraints can require additional structure for a particular implementation family.

## 3. Theorem PS-2 — optimal approximate rank

Let singular values of `P` be

\[
\sigma_1\ge\sigma_2\ge\cdots.
\]

By Eckart-Young-Mirsky, the minimum Frobenius error among rank-`r` linear predictive representations is

\[
E_r^2=\sum_{i>r}\sigma_i^2.
\]

Therefore an `epsilon`-accurate finite predictive state in Frobenius geometry exists with dimension `r` iff

\[
\sum_{i>r}\sigma_i^2\le\epsilon^2.
\]

Under operator-norm error the optimal residual is `sigma_{r+1}`.

## 4. Measurement uncertainty

If an observed predictive matrix `P_hat` satisfies

\[
\|P_{hat}-P\|_2\le\eta,
\]

then every singular value moves by at most `eta`. Consequently a rank/effective-rank claim is stable only when the relevant spectral gap exceeds the uncertainty margin. This connects directly to `GMI_EFFECTIVE_RANK_ESTIMATION_THEOREMS_V1.md`.

## 5. Lifecycle realization phase

The semantic spectral dimension does not uniquely choose RNN, SSM, explicit belief state, memory or attention. Let `C_R(r,epsilon)` denote the full lifecycle burden of realization family `R` achieving the required predictive error. GMI selects among families only after the predictive-state lower bound is combined with serve/update/parallelism/history-access prices.

## 6. Negative twins

- Flat/no-gap spectrum: dimension is unstable under small measurement error.
- Long spectral tail: aggressive state compression incurs unavoidable predictive error.
- Finite-horizon matrix: cannot certify unseen unbounded-horizon distinctions without a process assumption.
- Nonlinear sufficient state: may compress a high linear rank; PS-1/PS-2 are linear representation laws, not universal nonlinear lower bounds.

## Claim ceiling

This closes exact/approximate finite **linear** predictive-state dimension and error. Nonlinear partially observed state discovery, finite-data future-test design, and protected RNN/SSM/belief-state crossover remain OPEN-BLOCKING.
