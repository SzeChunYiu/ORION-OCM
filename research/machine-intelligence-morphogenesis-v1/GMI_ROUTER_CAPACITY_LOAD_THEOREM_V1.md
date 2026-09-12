# GMI router capacity and load-balance theorem v1

Status: **FORMAL CONDITIONAL-SPECIALIZATION RESOURCE LAW / T5-R4 NARROWING**

Date: 2026-09-12.

Purpose: make expert load balance and communication part of the exact routing objective rather than treating semantic expert choice as independent of hardware/resource capacity.

## 1. Batch assignment model

A batch contains `B` items and `K` available specialists. Item `i` routed to specialist `j` incurs registered semantic/resource cost

\[
c_{ij}=\ell_{ij}+r_{ij},
\]

where `ell_ij` is protected semantic loss contribution and `r_ij` includes communication/dispatch burden under the frozen price vector.

Let binary assignment `x_ij` satisfy

\[
\sum_jx_{ij}=1.
\]

Specialist `j` receives

\[
n_j=\sum_i x_{ij}.
\]

## 2. Theorem RL-1 — deterministic load/makespan law

Suppose specialist `j` processes `s_j` routed items per unit time and experts execute in parallel. Ignoring common fixed overhead, any assignment has service makespan at least

\[
\boxed{T\ge \max_j\frac{n_j}{s_j}}.
\]

Under the registered fluid/serial-per-expert model, this bound is attained by each specialist continuously processing its own queue, so it is the exact service time.

For equal service rate `s`,

\[
T=\frac{\max_j n_j}{s}.
\]

The ideal divisible balanced lower bound is `B/(Ks)`. Hence the load-imbalance slowdown factor relative to that ideal is

\[
\boxed{\rho_{load}=\frac{K\max_jn_j}{B}\ge1}.
\]

For integer batches the true best feasible maximum load is `ceil(B/K)`; the formula above is a convenient continuous normalization.

## 3. Capacity-constrained semantic routing

For a target service window, let expert capacities be integers `C_j`. The exact finite routing problem is

\[
\min_{x_{ij}\in\{0,1\}}
\sum_{i,j}c_{ij}x_{ij}
\]

subject to

\[
\sum_jx_{ij}=1,
\qquad
\sum_i x_{ij}\le C_j.
\]

This is a capacitated bipartite min-cost-flow problem. The standard network-flow constraint matrix is totally unimodular, so the linear-program relaxation has an integral optimum when capacities are integral.

Thus this registered routing problem is globally solvable in polynomial time; local top-k routing is an implementation heuristic, not the semantic definition of the optimum.

## 4. Congestion/shadow-price interpretation

The LP dual associates a nonnegative congestion price `lambda_j` with expert capacity. At an optimum, used routes are supported by adjusted costs of the form

\[
c_{ij}+\lambda_j.
\]

An overloaded semantically attractive expert acquires positive shadow price, making an otherwise slightly worse specialist lifecycle-optimal.

GMI therefore predicts specialization from **semantic heterogeneity plus capacity prices**, not heterogeneity alone.

## 5. Relation to the quadratic specialization law

`GMI_QUADRATIC_SPECIALIZATION_PHASE_THEOREM_V1.md` supplies an exact semantic penalty for sending mode `k` to the wrong quadratic specialist. In the present theorem that penalty can populate `ell_ij`; communication and load prices then determine the actual resource-aware routing phase.

This separates three causes of expert-system failure:

```text
experts insufficiently distinct/useful
router semantic confusion
resource/load congestion
```

## 6. Negative twins

- Infinite/very large equal capacities: load prices vanish; semantic routing dominates.
- Identical specialists: routing/load balance can improve throughput but not semantic quality.
- One uniquely necessary specialist: balancing away from it can violate semantics; more capacity or morphology expansion is needed rather than forced uniformity.
- Nonparallel hardware: the simple makespan law changes and the hardware schedule must be registered explicitly.

## 7. Claim ceiling

This closes the finite assignment/capacity layer of GKF-06. It does not solve expert learning, router representation, stochastic token arrivals, network contention, nonlinear expert overlap or real MoE protected generalization.
