# R4 — G10 burden: Lipschitz continuity of Σ ↦ B(Σ, τ)

Row: G10 (burden B, R2 object), rung R4. Question frozen in the atom table: for which
metrics d is Σ ↦ B(Σ,τ) Lipschitz; construct a hostile showing a natural metric where it
is NOT.

## Verdict (first sentence)

LIFT_FAILS — for the natural edit/assembly metrics on 𝓢 the burden functional is not
Lipschitz (not even continuous): a minimal two-state hostile has `d(Σ,Σ') = 1` while
`B(Σ,τ) − B(Σ',τ) = K·p` for arbitrarily large K, witnessed in
`hostiles/witnesses/hostile_burden_lipschitz.json`.

## Minimal counterexample (hostile H1)

State = archive containing one candidate program for task τ. Natural metric d = edit
distance (one archive rewrite = distance 1; the Levenshtein class registered for G02).
Σ has archive {a} where a is inadmissible for τ (never verified): B(Σ,τ) = N·p (expected
price of N draws, none ever admitted — or infinite; the witness uses the finite version
B = N·p with N the horizon). Σ' = archive {a'} where a' is a one-edit descendant that
admits immediately: B(Σ',τ) = p. Then `|B(Σ)−B(Σ')|/d(Σ,Σ') = N−1 → ∞`. One edit, one
task, finite space: no Lipschitz constant exists for the edit metric class.

## The surviving conditional (named, OCM-checkable)

LIFT_CONDITIONAL under the burden-pseudometric condition: B is 1-Lipschitz by definition
w.r.t. `d_B(Σ,Σ') := |B(Σ,τ) − B(Σ',τ)|` (a pseudometric — the trivial owned statement),
and for any other registered d, B is c-Lipschitz **iff** `d ≥ c⁻¹·d_B` on 𝓢, i.e. iff d
separates states by burden. OCM-checkable form: run B on a registered state sample; if
two states with |ΔB| large have small registered d, the metric is disqualified for burden
calculus. The failure is structural, not fixable by constants: burden depends on
ADMISSIBILITY (a V_c-contract predicate), and admissibility is discontinuous under every
edit metric — the same discontinuity that powers T03 aliasing and the A_T01 hostile.

## Assumption passes (A3)

- Remove vii-frozen-price-vector: B becomes vector-valued; per-coordinate verdicts
  identical (each coordinate is an expectation of a price), the hostile applies to any
  positive price coordinate. No rescue.
- Remove vi-fixed-ecology: hostile already uses a single task; ecology changes nothing.

## What HSG may claim

Only: (a) the hostile (residual, ours); (b) the named-metric conditional (a Lipschitz/
continuity statement in the HSG_DEFINITIONS §3(b) sense). The expectation-B is an R2
object; no R4 smoothness claim beyond Lipschitz-under-named-d.
