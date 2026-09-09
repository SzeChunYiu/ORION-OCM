# HSG Lane E — R3 (kernel-level) lifts of concept atoms, part 1

Parents: Ionescu-Tulcea (standard) — a sequence of measurable stochastic kernels
K_n from the running product space to the next coordinate induces a unique
probability law on the infinite product with those finite-dimensional
marginals (kernel composition always exists and is associative, *given
measurability of every factor*). Dobrushin 1956 ⚠ — ergodic coefficient
δ(K) = sup_{x≠y} d_TV(K(x,·),K(y,·)) contracts: d_TV(μK,νK) ≤ δ(K)·d_TV(μ,ν)
(PARENT_STATEMENT_UNVERIFIED_TEXT: coefficient form verified against standard
textbook statements, not the 1956 original).

## G01 Σ_t — R3: kernel state — LIFT_CONDITIONAL
- Definition. State becomes a kernel K: 𝓢×𝓑(𝓢)→[0,1]: the "next state" is a
  distribution indexed by the current one. Removes (ii) finiteness: kernels on
  general (uncountable) spaces are standard — no obstruction.
- Removal of (iii) measurability: a non-measurable K is not a kernel; the
  object itself degenerates to an arbitrary function into 𝒫(𝓢).
- Verdict: LIFT_CONDITIONAL — condition: each coordinate of K measurable.
  Assumption (iii) is not removable at R3; it can only be relocated from "the
  update map" to "the state kernel", or weakened Borel → universally
  measurable (see G09).

## G02 L_t language — R3: language-valued kernel — LIFT_CONDITIONAL
- Definition. K_L: 𝓢 → 𝒫(2^{Σ*}) — the state stochastically *selects or drifts
  the working language*; removes (i) decidability and (ii) finiteness.
- Well-posed part: 2^{Σ*} is Cantor space (G02-R2), so K_L is a kernel into a
  standard Borel space; existence is free.
- Condition: every consumer of L (expression well-formedness, verifier hooks)
  must be restated as oracle access with semi-decidable membership at best;
  semantics are then upper-semicomputable and their cost accounting lands in
  G10's burden, not in the kernel's well-definedness.
- Verdict: LIFT_CONDITIONAL — condition: oracle-cost semantics for membership.

## G03 Q_t proposal kernel — R3: Q as measurable stochastic kernel — LIFT_SURVIVES
- Definition (the R3 reading, formalized): Q_t: 𝓢 × 𝓑(𝓐) → [0,1], measurable in
  the state for each event, a probability measure on proposals for each state.
  Proposals are conditionally i.i.d. given the state — the xiii-iid note
  becomes a conditional-independence statement, not an assumption.
- Parent: Ionescu-Tulcea supplies the law of the induced proposal process.
- Verdict: LIFT_SURVIVES. This is the definition of a transition kernel; it
  exists exactly when (iii) holds for Q, which is part of the definition here
  rather than a removed assumption.

## G05 E_t ecology — R3: ecology-valued kernel — LIFT_CONDITIONAL
- Definition. K_E: 𝓢 → 𝒫(𝒫(𝓣)) — the ecology itself drifts: the state indexes
  a distribution over task-distributions. Removes (ii) finiteness of E.
- Condition: 𝒫(𝓣) needs a σ-algebra; the evaluation σ-algebra is canonical, and
  if 𝓣 is Polish, 𝒫(𝓣) is again Polish (weak topology) so K_E lives on a
  standard Borel space and Ionescu-Tulcea applies verbatim. For non-Polish 𝓣,
  natural ecology functionals are not automatically measurable.
- Verdict: LIFT_CONDITIONAL — condition: 𝓣 Polish (or evaluation σ-algebra
  fixed and functionals checked measurable case by case).

## G06 R_t resource policy — R3: kernel policy — LIFT_CONDITIONAL
- Definition. Policy-valued kernel K_R: 𝓢 → 𝒫(Policy); the state stochastically
  selects *which resource policy* is in force. Removes (iii).
- Removal of (iii) measurability of R: randomized policies must be integrated
  to price cost; a non-measurable policy makes 𝔼[cost] undefined. The
  assumption cannot be deleted — only relocated (into K_R's measurability).
- Verdict: LIFT_CONDITIONAL — condition: policy measurability re-imposed at
  the kernel level; (iii) is load-bearing, not removable.

## G07 V_t verifier — R3: randomized verification kernel — LIFT_SURVIVES
- Definition. V: 𝓢 × 𝓞 × 𝓑({0,1}) → [0,1]: verdict accept/reject is drawn from
  a kernel indexed by state and object. Soundness (iv, kept — lane G removes)
  becomes quantitative: P(accept | object false) ≤ β soundness error;
  completeness P(accept | object true) ≥ 1−α.
- This is the standard randomized-verification abstraction; composition of
  verification with proposals is again Ionescu-Tulcea.
- Verdict: LIFT_SURVIVES with (α,β) carried explicitly.

Verdicts: G01 CONDITIONAL, G02 CONDITIONAL, G03 SURVIVES, G05 CONDITIONAL,
G06 CONDITIONAL, G07 SURVIVES.
