# HSG Lane E — R2 (distribution-level) lifts of concept atoms, part 2

Parent: first-order stochastic dominance (FOSD, standard). μ FOSD-dominates ν
iff F_μ(x) ≤ F_ν(x) for all x, iff ∫f dμ ≥ ∫f dν for every bounded increasing
measurable f (real-valued case).

## G10 B burden — R2: burden as expectation — LIFT_SURVIVES
- Definition. B(Σ) = 𝔼[total cost] over all stochastic coordinates (proposals,
  verification randomness, tasks): B = ∫ c dℙ_Σ with c ≥ 0 measurable.
- Kolmogorov parent: nonnegative measurable c always integrates in [0,∞].
  Existence of B is therefore assumption-free; only *finiteness* of B(Σ) is a
  real assumption, now explicit rather than hidden.
- Verdict: LIFT_SURVIVES. Frozen-price removal (vii) is lane F's.

## G13 A_t ⊆ A_{t+1} + M overhead — R2: dominance between strategy
## distributions, with M > 0 (viii-M=0 removed) — LIFT_FAILS
- Claim tested: net-value distributions of the strategy archive are FOSD-
  ordered in t (later dominates earlier) once acquisition overhead M > 0 is
  charged.
- GROSS dominance survives trivially (FOSD parent): adding strategies to the
  support can only raise the pointwise max; a growing set is gross-monotone.
- NET dominance FAILS. Minimal counterexample (hostiles/G13_M_overhead_FOSD.md):
  two steps, incumbent s1 with net value 10; step 2 acquires s2 worth 10+ε
  gross, overhead M > ε charged at the step. V_1 = 10; V_2 = 10+ε−M < 10.
  FOSD of μ_2 over μ_1 fails at threshold v = 10−δ for small δ > 0.
- Rescue condition (named, not claimed): net FOSD is restored iff every
  acquisition is voluntary and accepted only when gross gain ≥ M — i.e. the
  dominance is a property of an acceptance policy, not of the growth law.
- Verdict: LIFT_FAILS (the unconditional growth⇒dominance reading);
  counterexample artifact in hostiles/.

## G15 archive/ratchet — R2: distribution over archives — LIFT_CONDITIONAL
- Definition. Archive = finite multiset of artifacts; archive space =
  ⋃_n 𝓧^n/S_n (symmetric products), measurable if 𝓗 is. R2 archive = μ ∈
  𝒫(archive space); ratchet = archive-value distributions FOSD-ordered in t.
- Condition. The ratchet ordering holds iff retention is elitist (keep-the-best
  with value measurable). Elitism/capacity removal (ix, x) is lane F's; at R2
  the ordering is exactly a restatement of elitism, not a theorem.
- Verdict: LIFT_CONDITIONAL — condition: elitist retention.

## G16 module amortization scalars — R2: random use-counts — LIFT_SURVIVES
- Definition. Per-module use-count N_m is a random variable; amortized per-use
  cost c_m/N_m is then random with 𝔼[c_m/N_m] ≥ c_m/𝔼[N_m] (Jensen: x↦1/x
  convex on (0,∞)).
- Consequence recorded: naive scalar amortization (divide by expected uses) is
  biased low — the R2 lift is well-posed but strictly larger than the R0 scalar.
- Verdict: LIFT_SURVIVES (definition) with the Jensen flag above; assumption-vi
  removal is later lanes'.

## G17 bias/prior family — R2: KL family of priors — LIFT_CONDITIONAL
- Definition. Prior family {p_θ: θ ∈ Θ} with KL divergence as the family
  metric: D_KL(p_θ‖p_θ') = ∫ log(dp_θ/dp_θ') dp_θ when absolutely continuous,
  +∞ otherwise.
- Condition. θ ↦ D_KL(p_θ‖·) is a measurable functional only under domination
  (single dominating measure) and jointly measurable densities. Without it the
  KL family is not a measurable parameterized object.
- Verdict: LIFT_CONDITIONAL — condition: dominated family, jointly measurable
  densities. Assumption-vi removal is lane G's.

Verdicts: G10 SURVIVES, G13 FAILS, G15 CONDITIONAL, G16 SURVIVES,
G17 CONDITIONAL.
