# Capability interaction laws — tranche 3

Scope: finite exact microscopes for the two cross-cutting rows that complete issue #602 F3. Evidence classes P1/P2. Claim ceiling **G2**.

## 1. Joint-only threshold / strict complementarity

Let capability coordinates `A` and `B` provide finite distinction capacities `a` and `b`. In this microscope the jointly usable code space is exactly Cartesian, so its cardinality is `a b`. The obligation is binary success at threshold `N`:

`U(a,b) = 1[a b >= N]`.

Let baseline capacities be `(a0,b0)` and upgrades be `(a1,b1)` with `a1 >= a0`, `b1 >= b0`.

**Theorem JT.** The target capability appears only when both upgrades are present iff

- `a0 b0 < N`,
- `a1 b0 < N`,
- `a0 b1 < N`, and
- `a1 b1 >= N`.

This is an iff because the four inequalities are exactly the truth conditions `U00=U10=U01=0`, `U11=1`. The discrete second interaction difference

`Delta = U11 - U10 - U01 + U00`

is therefore `+1` in every joint-only case.

**Exact witness.** `a0=b0=1`, `a1=b1=2`, `N=4`: capacities are 1,2,2,4, so only the joint upgrade succeeds. The matched negative twin lowers `N` to 2; either single upgrade then succeeds and joint-only emergence disappears.

This does not imply universal synergy. The theorem depends on a Cartesian joint code and a nonlinear threshold obligation. Change either assumption and the result need not survive.

## 2. Interference under a frozen hard budget

Let total hard resource budget be `R`. Capability A is feasible iff it receives at least `Q` units. When alone, A may use the full budget. Adding component B imposes an unavoidable maintenance cost `M` from the same hard budget and supplies no benefit measured on A's metric.

**Theorem IF.** Adding B harms A iff

`R >= Q` and `R - M < Q`.

*Proof.* Before B, A succeeds exactly when `R >= Q`. After B, at most `max(0,R-M)` remains available to A, so A fails exactly when this is below `Q`. Because `Q>0`, `R-M<Q` covers the same failure condition even when `M>R`.

**Witness.** `R=2`, `Q=2`, `M=1`: A succeeds alone and fails after B. A matched budget-restoration twin uses `R=3`; A then still receives 2 after B and the interference vanishes.

### Free-option monotonicity

Let `F_old` be A's old feasible configurations and let adding B be a free optional extension that preserves every old configuration, so `F_old subseteq F_new`. For the same A objective `f`,

`max_{x in F_new} f(x) >= max_{x in F_old} f(x)`.

Therefore an optional component cannot reduce *optimal* A performance merely by existing. Genuine interference requires a load-bearing coupling: mandatory maintenance, a hard shared budget, destructive parameter sharing, changed constraints, changed objective, or another mechanism that removes an old feasible solution. This is the adversarial control preventing the ledger from treating arbitrary performance regressions as intrinsic capability antagonism.

## Parent subtraction

JT is a finite complementarity/threshold-production result. IF is resource-constrained feasibility plus the elementary monotonicity of optimization over a superset. Neither is a novelty claim over those parents. The registered contribution is an architecture-independent, falsifiable F3 interaction contract that contains both positive complementarity and negative interference rather than assuming interactions have one sign.

## Closure boundary

Together with #670 and #671, this tranche supplies bounded P1/P2 evidence for all eleven registered F3 rows. It still does **not** provide the held-family, prospective morphology-to-capability predictor required for F4/V4/G6.
