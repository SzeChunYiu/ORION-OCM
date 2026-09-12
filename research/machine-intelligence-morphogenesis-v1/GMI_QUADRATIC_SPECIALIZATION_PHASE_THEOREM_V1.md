# GMI quadratic specialization phase theorem v1

Status: **FORMAL BASE LAW / GKF-06 NARROWING**

Date: 2026-09-12.

Purpose: derive an exact dense-shared versus routed-specialist phase law without assuming a historical MoE architecture.

## 1. Registered mode family

Let modes `k=1..K` occur with probabilities `p_k>0`, `sum_k p_k=1`. Let every mode have a common positive-definite quadratic geometry `H` and optimum `a_k`:

\[
L_k(\theta)=c_k+\frac12(\theta-a_k)^T H(\theta-a_k).
\]

Define `||v||_H^2=v^T H v`.

## 2. Theorem QS-1 — optimal shared state and exact heterogeneity burden

The optimal single shared parameter is

\[
\bar a=\sum_k p_k a_k.
\]

Its excess semantic loss over perfect mode-specific parameters is exactly

\[
G_{share}=\frac12\sum_k p_k\|a_k-\bar a\|_H^2.
\]

### Proof

Expand `sum_k p_k ||theta-a_k||_H^2`, differentiate, and use positive definiteness of `H`. Completing the square gives

\[
\sum_kp_k\|\theta-a_k\|_H^2
=\|\theta-\bar a\|_H^2+\sum_kp_k\|a_k-\bar a\|_H^2.
\]

Hence the unique minimizer is `bar a` and the residual is the stated heterogeneity term. QED.

## 3. Theorem QS-2 — router confusion has an exact semantic price

Suppose specialist `j` uses parameter `a_j`. Let `Q_{kj}` be the probability that true mode `k` is routed to specialist `j`, with each row of `Q` summing to one. The routing-induced excess loss is

\[
G_{route}=\frac12\sum_{k,j}p_kQ_{kj}\|a_j-a_k\|_H^2.
\]

Thus routing quality must be priced in semantic units, not only as compute overhead.

For uniform modes and symmetric wrong-routing probability `e` distributed uniformly across the other `K-1` specialists,

\[
G_{route}=\frac{2eK}{K-1}G_{share}.
\]

Therefore specialization loses its semantic advantage from routing alone once

\[
e\ge \frac{K-1}{2K}.
\]

## 4. Theorem QS-3 — lifecycle specialization crossover

Let `R` be the number of future mode-conditioned uses over the registered horizon. Let

\[
C_{spec}=C_{route}+C_{comm}+C_{maint}+C_{search}
\]

be the extra fixed/priced burden of maintaining and selecting specialists relative to one shared state, and let `Delta c_serve` be any per-use serving premium of specialization.

Specialization is lifecycle-favorable iff

\[
R\left(G_{share}-G_{route}-\Delta c_{serve}\right)>C_{spec}.
\]

If the bracket is nonpositive, no reuse horizon can amortize specialization.

## 5. Negative twins

1. **No heterogeneity:** all `a_k=a`. Then `G_share=0`; specialization has no semantic benefit.
2. **Unreliable router:** `G_route>=G_share`; specialization cannot improve semantic loss even before extra costs.
3. **Short horizon / expensive communication:** positive semantic gain exists but cannot amortize `C_spec`.
4. **Common low-rank mode span:** a smaller shared basis may absorb most heterogeneity, so the strongest parent is shared-core plus residual specialization, not full independent experts.

## 6. GMI consequence

The pre-outcome variables required by this base law are:

```text
mode probabilities p_k
mode optima / function displacement under a registered local geometry
heterogeneity energy G_share
router confusion geometry G_route
reuse horizon R
routing / communication / maintenance / search prices
shared-core effective rank
```

This derives conditional specialization pressure. It does **not** uniquely derive a neural MoE implementation.

## 7. Executed finite calibration

`run_gmi_quadratic_specialization_phase_v1.py` exhaustively checks scalar common-Hessian worlds for:

- `K=2..5`;
- all mode optima in `{-2,-1,0,1,2}^K`;
- five router-error levels;
- twelve routing/maintenance price combinations.

Receipt: `GMI_QUADRATIC_SPECIALIZATION_PHASE_RECEIPT_V1.json`.

Current result: 3,900 target tuples, 234,000 phase cells, zero violations.

## 8. Claim ceiling

This closes an exact common-Hessian quadratic response law for GKF-06. It does not establish nonlinear neural expert overlap, router learnability, load balancing, hardware granularity, communication congestion, or protected MoE superiority.
