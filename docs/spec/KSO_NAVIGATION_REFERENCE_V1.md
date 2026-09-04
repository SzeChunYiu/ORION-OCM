# KSO_NAVIGATION_REFERENCE_V1 — query-conditioned navigation, the replaceable reference mechanic (M1)

Status: **M1 consolidation of contract §5–§7, §14, §25–§26, §29–§31, §33. NO NOVELTY CLAIM.** The navigation operator `Π_t` is a *candidate representational choice* (issue D1): mathematically explicit, replaceable by any mechanic that survives the same obligations. Implementation: `src/ocm/kso/navigation.py`, `revocation.py`, `extraction.py`, `firing.py`, `jump.py`. The coupling that defines the law — a truth-maintenance gate over spreading activation with frozen denominators — is `PARENT_PRODUCT_OWNED` (KS-P1; contract §34).

## 1. Seeds and query-conditioned relevance

A question is atomised to seeds `Q` and a seed distribution `s_Q` over `V` (contract §28; committed, deterministic). `navigation.seed_vector(ks, seeds)` normalises a non-negative mapping over atom ids (rejection `UNBOUND_SEED`); `navigation.uniform_seed` is the background seed. Relation relevance `β_r(Q) ≥ 0` is a real parameter (`navigation.Relevance`: a mapping or callable from relation type to a rational, resolved by `navigation._beta`); the inherited checker fixed it at 1, and `relevance=None` reproduces that checker exactly. Restart probability `α ∈ (0, 1]`.

## 2. Frozen denominators, the gated matrix, and the two modes

The pre-revocation **structural denominator** (contract §5) is a property of the registered structure for this query and is never renormalised after a revocation:

\[
D_Q(v)=\sum_{h:\,v\in T_h} w_h\,\beta_{r_h}(Q)\qquad(\texttt{navigation.structural\_denominators}).
\]

With gate `g_R(x) = 𝟙[ℓ³_R(Λ_x) = LIVE]` in WARRANTED mode (UNKNOWN is gated out) and `g ≡ 1` in EXPLORATORY mode (`navigation.NavigationMode`, `navigation._gate`), the matrix (`navigation.navigation_matrix`) is

\[
P_{Q,R}(v,u)=\sum_{h:\,v\in T_h,\,u\in O_h}\frac{w_h\,\beta_{r_h}(Q)}{D_Q(v)}\,\gamma_h(u)\;g_R(v)\,g_R(h)\,g_R(u)\prod_{z\in T_h}g_R(z),
\]

the fraction taken as zero when `D_Q(v) = 0`. The seed is gated the same way, entry-wise and **not** renormalised (contract §25; `navigation.gated_seed`): `s_{Q,R} = g_R ⊙ s_Q`. Exploratory results may suggest hypotheses; they cannot authorise a claim (contract §7).

## 3. KS-T03 substochastic; KS-T04 prune equivalence (matrix level)

**KS-T03 (PROVED; parent: personalised PageRank, Andersen, Chung & Lang 2006).** `0 ≤ Σ_u P_{Q,R}(v,u) ≤ 1`: structural shares sum to one (or zero) per tail, each `γ_h` sums to one, and gates in `{0,1}` only remove mass (contract §5). `NavigationMatrix.is_substochastic` is the predicate.

**KS-T04 (PROVED; PARENT_PRODUCT_OWNED).** Let `Prune_R(K)` remove every non-LIVE atom and every edge that is non-live or has a non-live tail, retaining the original denominators (`revocation.prune` → `revocation.PrunedSpace`). Then `P_{Q,R}(K) = P_{Q,∅}(Prune_R(K))` entry-wise on survivors and every removed row/column is zero (contract §5 proof). Two independent implementations must agree: `navigation.navigation_matrix` and `navigation.navigation_matrix_by_pruning` (and `revocation.navigation_matrix_on_pruned` on the pruned object). Mutant: `navigation.mutant_navigation_matrix_renormalize` (the RWR/CBR parents' retraction: dead mass redistributed onto survivors) must differ on the witness.

## 4. KS-T04b — exact-share retraction propagates to the fixed point (four parts)

For `D_R` the non-live set (atoms and heads of non-live edges; `revocation.reach_of_dead` gives `Reach(D_R)`, the ungated forward closure) and `a*_R` the fixed point with the gated seed (`navigation.fixed_point`): (i) `a*_R(v) = 0` for `v ∈ D_R`; (ii) `a*_R(u) = a*_∅(u)` for `u ∉ Reach(D_R)`; (iii) `a*_R ≤ a*_∅` entry-wise; (iv) lifting `R` restores `a*_∅` exactly. Proof: Neumann series term-wise (contract §25). `revocation.retraction_checker` (F2) asserts the mutation applied (an unapplied planted retraction is `CANNOT_CHECK`), exact zero on the revoked atom, downstream drop, unrelated atom unchanged, the renormalising parent differing, exact reinstatement, and agreement of the independent implementation (`revocation.RetractionReport`).

## 5. KS-T05 contraction and KS-T04c prune–solve equivalence

**KS-T05 (PROVED; parents: Banach fixed point; PPR).** `F(a) = α s + (1−α) Pᵀ a` satisfies `‖F(a) − F(b)‖₁ ≤ (1−α)‖a − b‖₁` (substochastic transpose is ℓ1-nonexpansive; contract §6), hence has a unique fixed point `a* = α[I − (1−α)Pᵀ]⁻¹ s`. Solvers: `navigation.restart_fixed_point_exact` (Gauss–Jordan over ℚ; a singular system is `CannotCheck`; `α = 0` is rejected), `navigation.restart_iterate` (exact iteration), `navigation.restart_fixed_point_float` (power iteration; geometric convergence at rate `1−α`; stops at ℓ1 change `≤ tol`, default `1e-12`, else `CannotCheck` after `max_iter`). The float solver is checked against the exact solver within the frozen tolerance (registry limitation).

**KS-T04c (PROVED at M1; consolidation of KS-T04 + KS-T05 + KS-T11a; parent as KS-T04).** Under identical normalisation (the same denominator convention and the same background vector on both sides),

\[
\operatorname{Solve}_{\rm warranted}(K,R,q)=\operatorname{Solve}_{\rm warranted}(\operatorname{Prune}_R(K),\varnothing,q)
\]

at the fixed point and at the reacting subgraph. *Proof.* By KS-T04 the gated matrix is block-structured: the survivor block equals the pruned matrix and every entry from or into a removed atom is zero; the gated seed is zero on removed atoms and equals `s_Q` on survivors (survivors are LIVE). Let `a'` be the unique fixed point on `Prune_R(K)` (KS-T05) and extend it by zero to `V`. On a survivor the fixed-point equation involves only survivor entries, which is the pruned equation, so it holds; on a removed atom `v`, `a(v) = α·0 + (1−α)Σ_u P(u,v)a(u) = 0` because column `v` is zero. The extension therefore solves the gated system, and by uniqueness (KS-T05) it *is* `a*_R`. For the reacting subgraph (KS-T11a): `navigation.gated_closure` on `K` under `R` uses live edges with all tails reached and live heads, exactly the edges and atoms that survive pruning, so it equals the warranted closure on `Prune_R(K)` under `∅`; surprise `ρ_Q` is a function of `a*` and the background, equal on survivors and zero on removed atoms (`ρ = 0` when `a* = 0`); live edges inside `V_Q` coincide. Hence `G_Q` coincides. ∎ Checker `revocation.prune_equivalence` returns `matrix_equal` and `fixed_point_equal` (the extraction level follows functionally from KS-T11a). Limitation: the same denominator convention on both sides; a renormalising pruner (the mutant) violates the hypothesis and the conclusion.

## 6. Reaction surprise ρ_Q (KS-T06, KS-T06b) — a registered design choice

With background `π` (fixed point of the uniform seed) and `ε`,

\[
\rho_Q(v)=a^*_Q(v)\Bigl[\log\frac{a^*_Q(v)+\varepsilon}{\pi(v)+\varepsilon}\Bigr]_+\qquad(\texttt{navigation.reaction\_surprise},\ \texttt{surprise\_vector}).
\]

**KS-T06 (PROVED; parent: IDF/degree normalisation; Bayesian surprise).** `a*_Q(v) = π(v) ⇒ ρ_Q(v) = 0` (`log 1 = 0`); a universal hub has zero surprise under a query-independent seed. **KS-T06b (FINITE_CALIBRATION; contract §26 witness).** A query touching hub and specific atom ranks the specific atom first by surprise while the hub is first by popularity; a hub-only query ranks the hub first by both. Ranking: `navigation.rank_by`; mutant control: `navigation.mutant_popularity_rank` (raw activation) must differ. Limitation: the surprise function is a design choice, not a theorem of optimality (the M2 revival lever is the background convention, `results/KSO_M2_SOLVE_OUTCOME_V1.md`).

## 7. KS-T24 — navigation is not truth (D4)

**Statement (PROVED at M1; consolidation of contract §4 and §7).** Let `K°` be `K` with every warrant replaced by the certified-zero interval and all weights unchanged (`revocation.strip_all_warrants`). Then no atom of `K°` is LIVE under any `R`; the warranted matrix, gated seed and fixed point are identically zero; the warranted reacting subgraph is empty; no hyperedge is ENABLED for any activation vector; while the EXPLORATORY matrix and fixed point of `K°` equal those of `K`. *Proof.* `ℓ³_R([0,0]) = DEAD` for every `R` (`ℓ_R(0) = 0`, upper `= 0`), so every warranted gate is 0 (§2) and the unique fixed point of `a = 0 + (1−α)·0` is `0` (KS-T05); `extraction.reacting_subgraph` keeps only LIVE atoms; `firing.enabling_verdict` returns DISABLED when the edge-and-tails liveness is DEAD, before activation is consulted (KS-T02). Exploratory gates are constant 1 and do not read warrants, and denominators depend on weights only. ∎ Mutant: `firing.mutant_enable_ignores_tail_warrant` (activation promoted to truth). A high activation never creates warrant or authority; candidates from navigation enter the store only through `admission.admit` / `admission.compose` (architecture: the solver never writes labels).

## 8. Four-valued outcome, obstruction witness and escalation (KS-T19)

`navigation.navigate(ks, seed, target, budget, alpha, threshold, revoked, relevance)` returns `navigation.NavigationResult` with `outcome ∈` `navigation.NavigationOutcome` = FOUND | GAP_NOT_FOUND | OBSTRUCTION_WITNESSED | CANNOT_CHECK (contract §29). With `C°` = `navigation.ungated_closure` (the ceiling walker: unbounded, ungated, any tail reached) and `C^R` = `navigation.gated_closure` (LIVE atoms, live edges, all tails reached):

- FOUND iff `∃k ≤ steps: a_k(t) ≥ θ` (reason `ACTIVATION_ABOVE_THRESHOLD`);
- GAP_NOT_FOUND with reason `TARGET_ABSENT` (`t ∉ V`; hook `ACQUISITION_CHANNELS`), `WARRANT_GATED_TARGET_CLOSURE_REACHABLE` or `WARRANT_UNKNOWN_TARGET_CLOSURE_REACHABLE` (`t ∈ C° ∖ C^R`; hook `ACQUIRE_WARRANT`), or `BUDGET_EXHAUSTED_TARGET_CLOSURE_REACHABLE` (`t ∈ C^R`; hook `MORE_BUDGET`). **Timeout alone is a gap.**
- OBSTRUCTION_WITNESSED iff `t ∈ V` and `t ∉ C°` (reason `TARGET_OUTSIDE_UNGATED_CLOSURE`), with `navigation.ObstructionWitness(incumbent_mechanism, failed_obligation, witness_atoms = C°, lower_level_dispositions, resource_bound, kind = GLOBAL_OBSTRUCTION)` — contract §14's `Ω = (M, 𝒪, W_fail, D_<j, R_bound)`, the dispositions naming why budget, warrant and restart are not repairs.
- CANNOT_CHECK iff the budget is not positive (`NavigationBudget.validate`).

**KS-T19 (PROVED; parents: CEGAR-style escalation; ME-X2 / H-EXT-1R; V2 `jump.py`).** The four outcomes are exhaustive and pairwise exclusive: case split on `t ∈ V`, `a_k(t) ≥ θ`, `t ∈ C°`, `t ∈ C^R`. ∎ **Escalation rule (H-EXT-1R, finite form).** Escalate to the Jump ladder iff the gated walker fails **and** the ceiling walker is off ceiling. `ObstructionWitness.to_jump_trigger` builds `JumpTrigger(kind, incumbent_level = J1, witness_ids, lower_level_dispositions)` from `jump.py`, which is byte-identical to `src/orion_v2/jump.py` (verified by diff); the trigger must be `JumpTrigger.is_admissible`; a proposal must exceed the incumbent level (`jump.JumpProposal`), and `jump.assess_jump` never adopts (adoption authority stays external). **STRUCTURAL_NONIDENTIFIABILITY** (`navigation.identification_witness`): the target is found but another atom of the same type carries exactly the same activation under the committed seed (ME-X2 `CANNOT_IDENTIFY`); re-atomisation is a J3 proposal, not a lower-level repair.

## 9. Budget clause

`navigation.NavigationBudget(steps, restarts, depth)`; `navigation.assert_matched_budgets(arms)` raises `CannotCheck("UNMATCHED_NAVIGATION_BUDGET…")` when arms differ (contract §33, FM60 / ME-F1): a comparison across unmatched budgets is `CANNOT_CHECK`, never a result. Every navigation reports its `resources.ResourceVector` (`navigation_steps`, `navigation_work`).

## 10. Extraction (KS-T11a, KS-T10a)

**KS-T11a (PROVED; parent: prize-collecting Steiner, Goemans–Williamson family).** The reacting subgraph `G_Q = (V_Q, H_Q)`, `V_Q = {v ∈ C^R_{seed}: ρ_Q(v) > 0} ∪ supp(s_Q)` restricted to LIVE atoms in WARRANTED mode, `H_Q` the live hyperedges inside `V_Q`, is a function of `(K, R, s_Q, α)` because `a*` is (KS-T05) — `extraction.reacting_subgraph` (`extraction.ReactingSubgraph`, records `mode` and `seed_support`). The prize-collecting optimiser of contract §7 is a *different* object: `extraction.pcst_exact_bounded` enumerates every seed-connected subset (bounded to `max_atoms = 12` free atoms, else `CannotCheck`) and reports **every** optimum (`ExtractionResult.optima`, `ties`; a seed that is not live in warranted mode is `CannotCheck`); `extraction.pcst_greedy` is the scalable arm and always carries `approximation = GREEDY_PRIZE_DENSITY` (`extraction.Approximation`) — approximation is reported, never hidden. Both run in WARRANTED or EXPLORATORY mode; exploratory extractions cannot authorise a claim. **KS-T10a (PROVED).** Equal seed vectors yield identical extraction (a function of the seed); unequal seeds must differ. KS-T10 (two codecs agreeing on `s_Q`) stays `OPEN_M5`.

## 11. Parents

| mechanism | parent | status |
|---|---|---|
| restart/local diffusion from seeds | Andersen, Chung & Lang 2006 (PPR / local partitioning) | PARENT_OWNED |
| walks on hypergraphs; conjunctive ≠ clique expansion | Chitra & Raphael 2019 | PARENT_OWNED |
| contraction and unique fixed point | Banach; Neumann series | PARENT_OWNED |
| quotient of the chain (used in representation) | Kemeny & Snell 1976 | PARENT_OWNED |
| connected prize–cost extraction | Goemans–Williamson family (PCST) | PARENT_OWNED |
| conjunctive enabling / firing | Petri nets (Reisig) | PARENT_OWNED |
| label-gated activation with exact-share retraction | (JTMS/ATMS gate) ∘ (spreading activation with frozen denominators) | PARENT_PRODUCT_OWNED (KS-P1; contract §34: 0 of 8 single parents, the product equals the law on the witness) |
| escalation and Jump levels | CEGAR; V2 `jump.py` J0–J8; ME-X2 | PARENT_OWNED |

Inherited numbers are not re-derived here: navigation-only 38/50 (non-significant vs RWR and CBR at n = 50) and `PARENT_SUFFICIENT` stand (`KSO_CORE_V1.md` §9).
