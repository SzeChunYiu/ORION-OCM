# R5 — A_T12: what periodicity becomes for kernel dynamics

Row: A_T12 (T12 finite-state literal open-endedness limit, PROVED at R0: closed
deterministic finite system must eventually repeat). R5 ladder question: "what does
periodicity become for kernel dynamics: ergodic vs escaping mass".

## Verdict (first sentence)

PARENT_SUFFICIENT — the finite Markov chain convergence theorem (Perron–Frobenius
spectral form; standard modern statement Levin–Peres–Wilson, "Markov Chains and Mixing
Times", Ch. 1 and 4) owns the replacement: for a finite-state kernel P, the state space
decomposes as transient states plus closed irreducible classes R_i; every initial law μ
splits as μP^t → Σ_i α_i π_i + (escaping-to-null transient mass), α_i = absorption mass
of class R_i, when each R_i is aperiodic, and the Cesàro (time-averaged) convergence
holds ALWAYS (aperiodic or not) — recurrence-as-exact-repetition is replaced by
ergodic decomposition, exactly as the ladder question predicted.

## Exact owned statement (parent)

For finite P: (1) 𝓢 = T ⊔ R_1 ⊔ … ⊔ R_m with T transient and each R_i closed
irreducible (period d_i possibly > 1). (2) For μ supported anywhere,
μ P^t = Σ_i α_i(μ) π_i + e_t with ‖e_t‖_TV → 0 iff all visited R_i are aperiodic; with
periods d_i > 1 the limit cycles among d_i cyclic subclasses. (3) Regardless of period,
(1/T)Σ_{t<T} μ P^t → Σ_i α_i π_i (ergodic theorem for finite chains). (4) "Escaping
mass": in an OPEN system (mass can leave, R7 territory) absorption is replaced by loss
to the boundary — recorded here as the R5/R7 seam, owned by the open-Markov parents, not
proved here.

## T12's own conclusion at R5 (the HSG reading)

Literal infinite non-repeating NOVELTY stays impossible in the deterministic-repetition
sense only for deterministic maps; for kernel dynamics the correct statement is
WEAKER-LOOKING but equivalent in substance: the law of states converges to a stationary
mixture (or Cesàro-converges); empirical state-novelty beyond the recurrent-class
vocabulary vanishes in the time-average. The R5 lift of "must eventually repeat" is
"must eventually converge in Cesàro average / cycle on a finite decomposition" — T12's
open-endedness caveat (horizon-scoped, relative, or expanding space) survives verbatim;
expanding space is the only escape and is R6 territory (state space grows with t).

## Machine witness

`witness_ergodic_decomposition.json`: exhaustive check over enumerated 3-state kernels
(brute force, exact Fractions) that (i) every kernel's powers Cesàro-converge, (ii) the
limit equals the absorbed-mass mixture, (iii) a periodic example cycles while its
Cesàro average converges. Witness certifies the finite specialization only.

## Assumption pass (A3)

- Remove xii-finite-state: infinite state spaces break the DECOMPOSITION finiteness
  (countably many classes, no convergence without contraction) — this pass is exactly
  where R5 statements become CONDITIONAL on Dobrushin contraction (R5_SEMIGROUP_G09) or
  compactness; recorded, not re-proved.
