# R5 — A_T05 / G16: amortization as renewal-reward along use trajectories

Rows: A_T05 (T05 macro amortization threshold, PROVED at R0 as arithmetic on frozen
expectations), G16 (module amortization scalars H_eff, ΔC_use, C_build, C_maint,
C_rev). R5 ladder question: amortization identity with RANDOM use counts, renewal-reward
form; "verify the parent form" (renewal-reward ⚠).

## Verdict (first sentence)

PARENT_SUFFICIENT — the renewal-reward theorem owns the randomized form (verified
against standard primary sources, Ross "Introduction to Probability Models", Prop. 7.3
class; statement below): if module uses form a renewal process with i.i.d. inter-use
spans X_n (E[X] = 1/λ) and the per-cycle cost/reward has finite mean, then the long-run
amortized cost per unit time is E[cost per cycle]/E[cycle length] almost surely, and
per-USE it is E[cost per cycle]/E[uses per cycle]; T05's identity is the specialization
where each use is one cycle: amortized per-use cost → C_build/H_eff + C_maint·(E[lifetime
in uses]/H_eff-adjacent) + E[C_rev]/E[uses per revision] + ΔC_use — i.e. T05's threshold
`H_eff · ΔC_use > C_build + C_maint·L + E[C_revision]` IS the renewal-reward breakeven
with H_eff = expected uses over the module's regenerative lifetime.

## Exact parent statement (verified)

Renewal-reward: with i.i.d. pairs (X_n, R_n), X_n > 0 cycle lengths, R_n reward in cycle
n, E|R| < ∞, E[X] < ∞: (1/T)Σ_{n≤N(T)} R_n / T → E[R_1]/E[X_1] a.s. and in mean (Wald's
equation supplies the expectation form). Cost = negative reward. Applied with cycles =
module uses: per-use amortized overhead → E[overhead per use-cycle] which equals T05's
left/right sides exactly when build/maintenance/revision are charged into their
respective cycles; the checker (`witness_renewal_reward.json`) verifies the identity on
an exact-Fraction discrete use process, including the deviation when uses are NOT
regenerative.

## Conditional (named, OCM-checkable) — where the parent stops

LIFT_CONDITIONAL: the identity holds along a use trajectory iff the use process is
REGENERATIVE at the module boundary (i.i.d. inter-use spans, or Markov-modulated with a
regeneration state). If use intensity is state-dependent WITHOUT regeneration (ecology
drift, assumption vi removed), the ratio E[R]/E[X] is replaced by a state-averaged
functional and T05's fixed H_eff must be replaced by the stationary use rate — the named
condition is "registered use process is regenerative; else report stationary use rate",
OCM-checkable by regeneration-state logging. This is the honest boundary: renewal-reward
does not cover non-regenerative trajectories, and no cheaper parent does.

## Assumption pass (A3)

- Remove vi-fixed-ecology: exactly the conditional above; verdict degrades from
  PARENT_SUFFICIENT to LIFT_CONDITIONAL under this removal — recorded as the pass result.

## Registry note

A_T05 R5 = PARENT_SUFFICIENT (renewal-reward, verified); G16 R5 = same content as
A_T05 R5 (the scalar alphabet lives in T05's identity), landed as its own
PARENT_SUFFICIENT row for per-atom coverage (fold verdict; the earlier "NOT_APPLICABLE
as an independent row" wording here is superseded by AMEND_2).
