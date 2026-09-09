# R5 — G10: burden telescoping along orbits

Row: G10 (burden B), rung R5 (ladder question: burden telescoping along orbits;
parents_hint: T18 telescoping, HST-owned at R0).

## Verdict (first sentence)

PARENT_SUFFICIENT — the tower property of conditional expectation owns the telescoping
along random orbits: for the stopped burden process B(Σ_t) with Σ_{t+1} ~ K_t(·|Σ_t),
`E[B(Σ_T)] = B(Σ_0) + Σ_{t<T} E[B(Σ_{t+1}) − B(Σ_t)]` for any deterministic horizon T,
with no further assumption; the STOPPED version (first-admission stopping time τ*) needs
the named integrability/finite-horizon condition (optional stopping), which is the only
place the R0 form (T18) and the R5 form differ.

## Exact owned statement

Linearity of expectation along the kernel (Doob's tower property / Markov property):
E[B(Σ_{t+1}) | Σ_t] = (K_t B)(Σ_t), so E[B(Σ_T)] − B(Σ_0) = Σ_t E[(K_t B − B)(Σ_t)] —
an identity, not an inequality. Parent: standard Markov-process expectation theory (the
same parent class as T18's R0 telescoping; nothing new at R5 beyond naming the
conditional-expectation step).

## Conditional (named, OCM-checkable)

LIFT_CONDITIONAL for the stopped form: if the horizon is the random first-admission time
τ*, the telescoped sum equals E[B(Σ_{τ*})] only under E[τ*] < ∞ (finite expected
stopping time — checkable by the finite-state absorption computation of the A_T12
witness). Under drifting ecology (assumption vi removed) the identity survives per
realization but the BOUND (T18's fixed-ε conclusion) does not — that is T18/lane-owned
territory, recorded not re-derived.

## What HSG records as residual

The explicit bridge "T18's R0 telescoping = tower property read along the kernel orbit"
(one line); the stopped-form condition naming. No further claim.
