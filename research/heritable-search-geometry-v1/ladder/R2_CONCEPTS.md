# HSG Lane E — R2 (distribution-level) lifts of concept atoms, part 1

Parent: Kolmogorov measure theory (standard). Standing structure: every R2 lift
puts μ ∈ 𝒫(X) on a measurable space (X, 𝓑); nonnegative measurable functionals
always integrate in [0,∞] (extended reals), so existence is free — finiteness is
the only substantive demand.

## G01 Σ_t — R2: search over state distributions — LIFT_SURVIVES
- Definition. μ ∈ 𝒫(𝓢), 𝓢 given the product σ-algebra ⊗ of component ones.
  Search-over-distributions = the process may randomize/hedge over states.
- Verdict: LIFT_SURVIVES. Condition (purely structural, not an assumption
  removed): the product σ-algebra must be fixed once; under it 𝒫(𝓢) is a
  well-defined measurable space and μ exists for every component space.

## G02 L_t language — R2: random language (decidability removed) — LIFT_SURVIVES
- Definition. Language = point of 2^{Σ*} ≅ {0,1}^{Σ*}; with Σ* countable this is
  Cantor space (standard Borel). Random language = Borel μ on Cantor space.
- Removal of (i) decidability: measure theory never used decidability. The
  decidable languages form a countable (hence Borel, measure-possibly-0) subset;
  lifting to all of 2^{Σ*} strictly generalizes.
- Verdict: LIFT_SURVIVES. Cost: *use* of an undecidable language (membership
  queries) must be priced as oracle access; that pricing is bookkeeping in B
  (G10), not an obstruction to the lift itself.

## G04 H_t inherited structure — R2: inheritance as distribution — LIFT_CONDITIONAL
- Definition. Population = μ_H ∈ 𝒫(𝓗); inheritance = sampling descendants from
  a reproduction kernel over 𝓗. Removes (ii) finiteness of H.
- Condition. With 𝓗 infinite, "descend from the fittest" needs a measurable
  argmax/selection. Sufficient: fitness functional measurable with compact
  level sets, or finite-support truncation of the population.
- Verdict: LIFT_CONDITIONAL — condition: measurable selection of parents exists
  (the selection step is where finiteness was silently doing work).

## G05 E_t ecology — R2: task distribution (formalized) — LIFT_SURVIVES
- Definition. E_t ∈ 𝒫(𝓣), 𝓣 task space with σ-algebra; burden of a state
  becomes B_E(Σ) = ∫ b(Σ,τ) dE_t(τ) — an expectation over tasks.
- This is the reading HST v1 already implies; formalizing costs nothing.
- Verdict: LIFT_SURVIVES (as definition; theorems about it are lane F/G's).

## G06 R_t resource policy — R2: randomized policy — LIFT_SURVIVES
- Definition. R2 randomized policy = kernel from observed state to resource
  actions (standard MDP formalism); randomization is exactly what a kernel is.
- Measurability enters only when *integrating* costs through the policy (G10);
  as an object the randomized policy exists.
- Verdict: LIFT_SURVIVES (object); integrability handled at G10.

## G08 C constitution — R2: distribution over constitutions — LIFT_SURVIVES
- Definition. μ_C ∈ 𝒫(𝒞), 𝒞 = Cantor space (G08-R1). Constitutional
  uncertainty = search may hold mass on several constitutions.
- Verdict: LIFT_SURVIVES; σ-structure inherited from R1 verbatim. Stops here —
  assumption-v removal is lane G's.

Verdicts: G01 SURVIVES, G02 SURVIVES, G04 CONDITIONAL, G05 SURVIVES,
G06 SURVIVES, G08 SURVIVES.
