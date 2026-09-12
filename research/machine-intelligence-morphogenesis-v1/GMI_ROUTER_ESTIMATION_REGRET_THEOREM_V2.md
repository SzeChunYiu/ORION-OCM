# GMI Router Estimation Regret Theorem v2

Status: **LEARNED-ROUTER DECISION LAYER HARDENING / R4**

Date: 2026-09-12.

The prior capacity theorem makes routing a constrained assignment/min-cost-flow problem. The remaining question is how estimation error degrades that decision.

Let `F` be any common feasible assignment set for `N` routed items, including capacity/load constraints. Let true assignment costs be `c_{ik}` and predicted costs `hat c_{ik}` with
\[
|\hat c_{ik}-c_{ik}|\le\epsilon
\]
for every legal item/expert pair.

Let `a*` minimize true total cost and `ahat` minimize predicted total cost over the **same feasible set**.

## RE-1 — uniform learned-router regret bound

\[
\boxed{
C(\hat a)-C(a^*)\le 2N\epsilon.
}
\]

### Proof

For any assignment `a` of `N` items,
\[
|\hat C(a)-C(a)|\le N\epsilon.
\]
Then
\[
C(\hat a)
\le \hat C(\hat a)+N\epsilon
\le \hat C(a^*)+N\epsilon
\le C(a^*)+2N\epsilon.
\]
QED.

The result is independent of whether the feasible assignment is solved by min-cost flow, matching, or another exact optimizer.

## RE-2 — robust phase margin

If the true best assignment beats the second-best feasible assignment by margin `Delta`, the predicted router is guaranteed to preserve the true optimum whenever
\[
2N\epsilon < \Delta.
\]

Thus routing learnability should be reported through a **cost-estimation interval relative to the assignment margin**, not only top-1 classification accuracy.

## Executed finite calibration

50,000 deterministic random `N=4, K=2, capacity=2` assignment worlds with integer costs and `epsilon=1` perturbations produced:

- zero violations of `2N epsilon`;
- maximum observed regret `5`, below the analytic cap `8`.

## Claim ceiling

This closes the decision sensitivity layer conditional on a valid cost estimator. Learning representation overlap, expert quality, communication cost and nonstationary capacity remain empirical.
