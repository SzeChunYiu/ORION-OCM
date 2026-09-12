# GMI deep-linear development barrier theorem v1

Status: **EXACT NONCONVEX DEVELOPMENT BASE LAW / T1 NARROWING**

Date: 2026-09-12.

Purpose: prove in the smallest deep model that representational adequacy does not determine developmental accessibility, and derive the exact depth/initialization dependence of gradient-flow progress.

## 1. Balanced scalar deep-linear world

Consider an `L`-layer scalar linear network

\[
f_w(x)=\left(\prod_{\ell=1}^L w_\ell\right)x
\]

on the registered input `x=1`, with target coefficient `a>0` and loss

\[
\mathcal L(w)=\frac12\left(\prod_\ell w_\ell-a\right)^2.
\]

The target is exactly representable for every depth `L>=1`.

Assume balanced positive initialization

\[
w_1(0)=\cdots=w_L(0)=s_0>0.
\]

Gradient flow preserves balance, so write `w_\ell(t)=s(t)` and define the realized product

\[
q(t)=s(t)^L.
\]

## 2. Theorem DL-1 — exact product dynamics

For balanced gradient flow,

\[
\dot s=(a-s^L)s^{L-1},
\]

and therefore

\[
\boxed{\dot q=L(a-q)q^{2-2/L}}.
\]

### Proof

For any layer,

\[
\frac{\partial\mathcal L}{\partial w_\ell}
=(q-a)\prod_{j\ne\ell}w_j.
\]

Under balance this equals `(q-a)s^{L-1}`. Gradient flow gives the first equation. Since `q=s^L`,

\[
\dot q=Ls^{L-1}\dot s
=L(a-q)s^{2L-2}
=L(a-q)q^{2-2/L}.
\]

QED.

## 3. Theorem DL-2 — exact zero-initialization obstruction

For every `L>=2`, the all-zero state is stationary:

\[
w_1=\cdots=w_L=0
\implies
\nabla\mathcal L=0,
\]

even though the protected loss is `a^2/2>0` and exact zero-loss realizations exist.

For `L=1`, by contrast, `\dot q=a-q`, so zero initialization immediately moves toward the target.

Thus depth changes developmental accessibility without changing representability.

## 4. Theorem DL-3 — small-initialization development-time barrier

Let `0<q_0<q_1<=a/2`. The exact time to move from `q_0` to `q_1` is

\[
T=\frac1L\int_{q_0}^{q_1}
\frac{dq}{(a-q)q^{2-2/L}}.
\]

Because `a-q<=a`,

### Depth two

\[
T\ge \frac{1}{2a}\log\frac{q_1}{q_0}.
\]

### Depth `L>2`

\[
\boxed{
T\ge
\frac{q_0^{-(L-2)/L}-q_1^{-(L-2)/L}}
{a(L-2)}
}.
\]

Hence as `q_0 -> 0`, the minimum development time diverges logarithmically for `L=2` and polynomially for every `L>2`.

The same target that a shallow linear model reaches with an `O(log(1/epsilon))` first-order law can therefore have an arbitrarily large depth/initialization burden in this nonconvex parameterization.

## 5. Developmental coordinates exposed by the theorem

A zero-prior neural-development predictor must distinguish at least:

```text
representational adequacy
multiplicative depth / parameterization
initial realized signal q_0
local gradient transmission
productive-basin geometry
step/flow law
required target tolerance
```

Parameter count alone does not determine accessibility.

## 6. Negative twins and repairs

- Nonzero favorable initialization can remove the exact stationary obstruction.
- Skip/residual pathways can create a first-order signal path absent in the pure product parameterization.
- Normalization/reparameterization/optimizer state can change the product dynamics.
- The theorem is not evidence that deeper networks are generally worse: depth-separation theorems show that depth can simultaneously reduce representation burden on compositional targets.

GMI therefore predicts a lifecycle tradeoff between representational compression and developmental accessibility rather than a monotone depth preference.

## 7. Claim ceiling

This is an exact balanced scalar deep-linear gradient-flow theorem. It does not solve high-dimensional nonlinear basin geometry, stochastic optimization or feature-learning dynamics, but any general neural-development law must reduce correctly to this limit.
