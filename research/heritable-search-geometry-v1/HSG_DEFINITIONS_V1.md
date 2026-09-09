# HSG Definitions V1 (frozen)

Frozen by `HSG_FREEZE_V1.json` before any ladder artifact. A lane may not edit these;
a needed change is a declared, sha-chained amendment to the freeze and re-derivation of
affected rows. HSG does not redefine HST objects — it locates each on the rung ladder
and defines what the object BECOMES at each rung. HST v1 (`../heritable-search-transformation-v1/`)
stays frozen and canonical at its own scope.

## 1. The rung ladder (binding types)

| rung | object of study | binding type |
|---|---|---|
| R0 point | one fixed Σ, deterministic U | element |
| R1 set | 𝓢 the space of search states; families/sets of objects | set + closure operators (Reach_B, cones) |
| R2 distribution | μ ∈ 𝒫(𝓢) | probability measure |
| R3 kernel | K: 𝓢 → 𝒫(𝓢) | Markov kernel; Blackwell order applies |
| R4 geometry/topology | (𝓢, d, 𝒜, μ) + kernel family 𝓚 with invariants | metric/measure space; contraction coefficient δ_d(K) (Dobrushin), OT cost W_d, information-geometric distances on 𝓚 |
| R5 dynamics | (K_t)_{t∈T} iterates; semigroup ⟨𝓚⟩ (#145 closure) | semigroup element, orbit, ergodic decomposition, transfer operator |
| R6 meta-dynamics | t ↦ K_t as a kernel-valued process; C time-varying | process on 𝓚 ∪ {constitution states} |
| R7 multilevel/open | coupled family (𝓢^ℓ, K^ℓ)_{ℓ∈Λ} + exchange kernels; measures not conserved | open Markov family; cones as module boundaries |

## 2. Central lifts (the ones the ladder exists for)

- **U: R0 → R3.** HST's `Σ_{t+1} = U(Σ_t, x, e)` with `x ~ Q_t` composes into ONE Markov
  kernel `K_t = U ∘ Q_t : 𝓢 → 𝒫(𝓢)`. The development process is a kernel process. This
  lift is definitional (composition), not a theorem.
- **B: R2 → R4.** Burden `B_t(τ)` becomes a function on the metric space; the geometric
  questions are Lipschitz continuity (does near-Σ mean near-burden?) and which metrics
  make it so. No metric is asserted canonical; metric choice is a registered parameter.
- **Reach: R1 → R5.** `Reach_B(O)` (set closure) becomes semigroup reach: the orbit
  structure of ⟨O⟩ on (𝓢, d). #145 owns the closure algebra; HSG asks the metric questions.
- **Inheritance economics: R0 → R2/R7.** `A_t ⊆ A_{t+1}` at zero overhead becomes a
  dominance statement between strategy distributions at R2, and a cross-level charging
  question at R7 (level-ℓ overhead charged to level-ℓ′ strategies).

## 3. Geometry discipline (what "geometry" is allowed to mean here)

An HSG geometric claim is ONLY one of: (a) a contraction/OT/information-geometric
inequality on 𝓚 or 𝒫(𝓢) with a named parent; (b) a Lipschitz/continuity statement for a
registered functional (B, Ev, hypervolume) under a named metric; (c) a locality statement
(cones vs metric balls). "Geometric intuition", pictures, and unparented vocabulary
("curvature of search", "manifold of intelligence") are barred from PROVED rows — they
may appear only as P4 hypotheses or in hostiles as named failure modes.

## 4. Assumption registry (ordered, one removal per pass)

Shared removal order for rows that carry these: (i) decidability of L membership;
(ii) finiteness of H/E; (iii) measurability of U/R; (iv) soundness of V (never a theorem
of HSG either); (v) fixed C; (vi) fixed τ/ecology; (vii) frozen scalarization/price vector;
(viii) M = 0 optional inheritance; (ix) elitism/selection; (x) unlimited archive capacity;
(xi) dependency-cone completeness; (xii) finite state space; (xiii) i.i.d./computable Q.
A row's `assumption_removals` field names its own ordered sublist.

## 5. Verdict semantics (frozen; matches HSG_FREEZE_V1.json)

LIFT_SURVIVES · LIFT_CONDITIONAL (condition named, OCM-checkable) · LIFT_FAILS (minimal
counterexample in hostiles/) · PARENT_SUFFICIENT (parent + exact owned statement) ·
NOT_APPLICABLE (reason recorded) · BLOCKED. A rung chain may not skip rungs in a SURVIVES
claim; a FAIL at rung r does not bar investigating r+1 (fails are per-rung facts).

## 6. What HSG deliberately does not define

A canonical metric on 𝓢 (choice is registered per campaign); "the geometry of intelligence"
as an object; novelty beyond T13's discipline; any semantic property of programs (T15 bars
it at every rung); and no claim that the ladder terminates — R7 is the last FROZEN rung,
not the last possible one (a further rung is an amendment, not a silence).
