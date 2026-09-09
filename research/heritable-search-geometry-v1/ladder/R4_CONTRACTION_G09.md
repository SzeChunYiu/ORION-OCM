# R4 — G09 update map: Dobrushin contraction of the composed development kernel

Row: G09 (U update map), rung R4. One rung lift from the R3 kernel reading `K_t = U∘Q_t`.

## Verdict (first sentence)

LIFT_CONDITIONAL — the naive composed-kernel contraction `δ(K_t) ≤ δ_TV(Q_t)` is FALSE in
general (machine-witnessed: a 3-state development with deterministic state-dependent U
has `δ(K_t) = 1` while `δ_TV(Q_t) = 3/4`); the bound holds under the named, OCM-checkable
condition **state-shared transport**: U's transport step does not read Σ (a fixed
measurable T with U(Σ,x) = T(x)); the parent machinery that owns both the true
inequalities is Dobrushin (1956, verified): `δ(PQ) ≤ δ(P)δ(Q)` for kernels on a common
space, and the max-coupling triangle that yields the general repair bound
`TV(K_s, K_s') ≤ t_{ss'} + (1 − t_{ss'})·Δ_U(s,s')` with `t = TV(Q_s, Q_s')`,
`Δ_U(s,s') = sup_x TV(law U(s,x), law U(s',x))` (vacuous when U is state-dependent and
deterministic, since Δ_U = 1).

## Exact owned statements (parent, verified)

Dobrushin, "Central Limit Theorem for Nonstationary Markov Chains. I/II", Teor. Veroyatn.
i Primenen. 1(1):72–89, 1(4):365–425 (1956). For a kernel P on a common state space,
`δ(P) := sup_{x,y} ‖P(x,·) − P(y,·)‖_TV = 1 − inf_{x,y} Σ_z min(P(x,z), P(y,z))`; δ(P) is
the operator norm of P on zero-mass signed measures, giving `‖μP − νP‖_TV ≤ δ(P)‖μ−ν‖_TV`
and `δ(PQ) ≤ δ(P)δ(Q)`; the coupling characterization (TV = min-coupling mismatch) gives
the data-processing and triangle bounds used below. Checker certifies δ(PQ) ≤ δ(P)δ(Q) on
3375 enumerated 3-state kernels + 600 distinct pairs, exact Fractions.

## Why the naive composition bound fails (the substantive R4 fact)

`K_t(·|Σ) = law of U(Σ, x, e)`, `x ~ Q_t(·|Σ)`. Data processing gives TV-invariance only
for a FIXED map: T#Q_s vs T#Q_s' — here the map itself depends on s, so on the
optimally-coupled event x = x' the outputs U(s,x) and U(s',x) can still be disjoint point
masses. Consequence for HSG: contraction of the development kernel is NOT bought by
mixing the proposal kernel; it exists only when (a) the proposal kernels overlap across
states AND (b) the update's state-read does not split the coupled proposals. HST's U
reads Σ by definition (Σ_{t+1} = U(Σ_t, x, e)) — the condition is genuinely restrictive,
and the named restoration is either a state-shared transport step or paying the Δ_U term
in the repair bound.

## Assumption passes (A3, one removal per pass)

- Remove iii-measurability: coefficient still definable on finite 𝓢; checker is finite
  scope. At infinite scope U must be measurable for K_t to be a kernel — named restored
  assumption, not re-proved.

## Machine witness

`../hostiles/witnesses/witness_dobrushin_composition.json`: submultiplicativity sweep;
state-shared transport example (δ(K) = ½ ≤ δ(Q) = ½); state-dependent falsification
(δ(K) = 1 > ½ = δ(Q)); the repair bound verified pair-exact. Witness certifies the
finite specialization only, never the rung verdict.

## What HSG may NOT claim

No "curvature of the development map"; no empirical claim that any OCM kernel has δ < 1
(P4); no canonical metric (TV named per HSG_DEFINITIONS §3(a)).

Cross-references: R5 orbits (`R5_SEMIGROUP_G09.md`); Ev sensitivity uses the same
coupling parent (`R4_EV_SENSITIVITY_G11.md`).
