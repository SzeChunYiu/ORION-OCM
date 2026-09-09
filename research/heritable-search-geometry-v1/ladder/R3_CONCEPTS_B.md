# HSG Lane E — R3 (kernel-level) lifts of concept atoms, part 2

## G09 U update map — R3: K_t = U∘Q_t as compositional Markov kernel — LIFT_CONDITIONAL
- Definition. The central lift: one step of search is the composed kernel
  K_t(Σ, A) = ∫ Q_t(Σ, dΣ') U(Σ', A); the trajectory law exists by
  Ionescu-Tulcea (parent) *provided every factor is measurable*. Removes (iii).
- Finding: assumption (iii) is definitional here, not removable. Non-measurable
  U ⇒ the composition integral is undefined ⇒ K_t is not a kernel; the lift's
  object ceases to exist. What IS possible is a strict weakening: on analytic
  (Souslin) state spaces, universally measurable U still yields universally
  measurable composed kernels and an Ionescu-Tulcea law on the universally
  completed product — strictly weaker than Borel (iii), strictly stronger than
  nothing.
- Verdict: LIFT_CONDITIONAL — condition: U universally measurable and 𝓢
  analytic (Borel case included). Bare removal of (iii): fails definitionally.

## G10 B burden — R3: kernel-conditional burden B(Σ,τ) — LIFT_CONDITIONAL
- Definition. B(Σ,·) = expected remaining cost conditioned on state (and task):
  a regular conditional expectation of the cost functional, i.e. itself a
  kernel. Frozen-price removal (vii) is lane F's.
- Condition: regular conditional distributions exist for all conditioning
  variables when 𝓢 is standard Borel (Polish); on general measurable spaces
  conditional burden exists only as an a.e.-equivalence class and cannot be
  chosen as a kernel.
- Verdict: LIFT_CONDITIONAL — condition: 𝓢 standard Borel.

## G11 Ev evolvability — R3: kernel evolvability — LIFT_CONDITIONAL
- Definition. Ev(K) = ℙ_{Σ'~K(Σ,·)}[Σ' is a useful descendant] = ∫ 1_useful dK(Σ,·):
  the probability that a one-step (or n-step, by Ionescu-Tulcea composition)
  kernel descendant is useful. Replaces point-boolean evolvability with a
  kernel functional; xiii's iid note handled as in G03 (conditional on state).
- Condition: the usefulness event must be measurable in 𝓢; if usefulness is
  defined via verifier verdicts (G07), measurability follows from V being a
  kernel; if defined semantically (undecidable language worlds, G02), it can be
  merely analytic — then ℙ is still defined for universally completed spaces.
- Verdict: LIFT_CONDITIONAL — condition: usefulness event measurable (or
  analytic + universal completion).

## G16 module amortization scalars — R3: kernel-conditional amortization — LIFT_CONDITIONAL
- Definition. Amortization conditioned on state and task:
  𝔼[c_m/N_m | Σ,τ] — a regular conditional expectation (kernel) of the R2
  random amortized cost (G16-R2), so pricing adapts to the search's regime.
- Condition: same as G10-R3 — regular conditional distributions require 𝓢
  standard Borel; Jensen gap from R2 persists conditionally (Jensen applies to
  each conditional law), so conditional amortization remains biased low if the
  naive scalar form is used.
- Verdict: LIFT_CONDITIONAL — condition: 𝓢 standard Borel.

## G17 bias/prior family — R3: prior as kernel parameter — LIFT_CONDITIONAL
- Definition. K(Σ, dθ) into parameter space Θ, then prior p_θ applied: the
  state stochastically *selects the bias*. The family becomes a fibered object
  𝒫(𝓧) ⊇ {p_θ} with θ ~ kernel. KL between fiber elements as at R2.
- Condition: θ ↦ p_θ must be a measurable map Θ → 𝒫(𝓧) (i.e. the family is a
  statistically coherent parametrization: dominated, jointly measurable — same
  condition as G17-R2); then K(Σ,·) pushes forward to a prior kernel on 𝒫(𝓧)
  and Dobrushin ⚠ contraction bounds the drift of the selected bias:
  d_TV of two states' selected-prior laws ≤ δ(K)·d_TV of the states.
- Verdict: LIFT_CONDITIONAL — condition: measurable parametrization
  (domination + joint measurability). Assumption-vi removal is lane G's.

Verdicts: G09 CONDITIONAL, G10 CONDITIONAL, G11 CONDITIONAL, G16 CONDITIONAL,
G17 CONDITIONAL.

## Lane E synthesis (R1–R3, concept atoms)
- Clean survivals are exactly the lifts that ARE standard definitions: G03, G07
  (kernel formalizations), G01-R1/R2, G02-R2, G05-R2, G06-R2, G08, G10-R2, G16-R2.
- Every R3 lift re-imposes measurability *somewhere*: assumption (iii) is not
  removable, only relocatable or weakenable (Borel → universal, G09).
- The one structural failure is G13: growth does not dominate under overhead.
- Two atoms are already owned by parents: G12, G14.
