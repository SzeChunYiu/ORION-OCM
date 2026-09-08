# 03 — Dynamics: what changes, at which time scale, under which law

Five time scales. Each has: state, update law, invariant, fixed-point/termination statement, checker.
The cross-scale write table at the end says which scale may write which field; the genome `Σ` has
no writer.

## τ1 — Query dynamics (milliseconds; one question) `[MACHINE: navigation_matrix, restart_fixed_point, enabled_hyperedges]`

| | |
|---|---|
| state | `ρ ∈ ℝ₊^A` (activation), `E_R` (enabled edges), `X_Q`, `Ω` |
| inputs | `𝒦` (read-only), `s_Q`, `R` (current revocation set), `B` |
| law | `ρ⁽ᵗ⁺¹⁾ = α s_Q + (1−α) W_Qᵀ ρ⁽ᵗ⁾`; then `E_R` from `ρ*` and `θ`; then `X_Q`; then `Ω` by KS-T19 |
| invariant | `‖ρ‖₁ ≤ 1`; `ρ(a) = 0` for every gated-out atom; `𝒦` unchanged |
| fixed point | unique (KS-T05); exact rational for `\|A\|` small, iterative with `‖ρ⁽ᵗ⁺¹⁾ − ρ⁽ᵗ⁾‖₁ ≤ (1−α)ᵗ` otherwise; stops at `ε` or at budget `B` (then `Ω = CANNOT_CHECK` if not converged) |
| reaction | `r_Q = ρ_Q − ρ_∅`; hubs are ranked by `r`, never by `ρ` (KS-T06b) |
| checker | retraction both directions on 400 planted revocations (M1); renormalising parent must differ |

Terminal outcomes of τ1: `FOUND` (target in `X_Q` with `live(L(π), R)`), `GAP_NOT_FOUND` (target
absent or unreachable under the bounded walker but reachable under the ceiling walker, or timeout),
`OBSTRUCTION_WITNESSED` (KS-T19), `CANNOT_CHECK` (budget/convergence failure). Only τ1 sets `Ω`.

## τ2 — Learning dynamics (seconds–minutes; one acquisition) `[MACHINE: kso_m0_freeze_checks_v1 (acquisition transaction)] [SPEC: channel adapters → M2b/M3]`

| | |
|---|---|
| state | `A`, `H`, `L` (append-only for pre-existing atoms: their labels never change here) |
| inputs | transaction `t = (A⁺, H⁺, cert)`; `cert.kind ∈ {INSTRUCTION, DEMONSTRATION, INTERACTION, EXPERIMENTATION, FEEDBACK, EXACT_CHECKER}` |
| law | admission (KS-T08): types registered; `H⁺ ≠ ∅` for every `a ∈ A⁺`; reachable-by-navigation from some existing atom or quarantined; `L(a) = cert.label` where FEEDBACK ⇒ `0`, EXACT_CHECKER ⇒ `{{c}}`, INSTRUCTION/DEMONSTRATION ⇒ `{{src}}` (the source is the assumption), INTERACTION/EXPERIMENTATION ⇒ `{{obs}}` |
| invariant | `Σ` digest unchanged; `L` of pre-existing atoms unchanged (KS-T13); `d(a)` for pre-existing atoms unchanged (frozen denominators are recomputed only for new atoms) |
| termination | one transaction = one commit; no fixed point needed |
| consolidation | `𝒦 → 𝒦/~` only if `~` lumpable and warrant-measurable (KS-T12); `[SPEC → M3]` |
| active acquisition | choose the next experiment/question maximising expected change of `Ω` from GAP to FOUND per budget; `[SPEC → M3]`; parent: optimal experimental design |
| checker | planted feedback atom cannot enable any edge; planted unregistered type rejected; planted isolated atom rejected; planted label edit of an existing atom rejected |

## τ3 — Revision dynamics (on demand; one revocation or reinstatement) `[MACHINE: dependency_impact_cone; M1 retraction checker]`

| | |
|---|---|
| state | `R` (revocation set), and through it every `g_R`; nothing in `L` changes |
| law | `R ← R ∪ {c}` (revoke) or `R ← R \ {c}` (reinstate); affected atoms = `cone({c})` (KS-T09); `ρ` recomputed under τ1 |
| invariant | exact-share: `ρ_R(a) = 0` for every dead atom; `ρ_R(a) = ρ_∅(a)` for every atom outside `cone` (M1: 400/400); reinstatement restores the pre-vector exactly |
| self-revision | a representation/policy change `φ: 𝒦 → 𝒦'` is admissible iff S4 (measurable) and S5 (signature) hold; `[MACHINE: S4/S5 predicates]`, operator `[SPEC → M3]` |
| termination | immediate; `cone` is a least fixed point over a finite lattice |
| checker | reachability used for "outside cone unchanged" is an **independent ungated closure**, not the navigation matrix (replay FRAME_OK on P3) |

## τ4 — Growth dynamics (hours–days; the stem-cell loop) `[MACHINE: kso_m0_freeze_checks_v1 (stem-cell invariant, three cancers)]`

| | |
|---|---|
| state | the whole of `𝒦` except `Σ` |
| law | repeat: acquire (τ2) → compose (`π` with `⊗` label) → self-revise (τ3 admissible `φ`) → registered revocation (τ3) → check authority preserved |
| invariant (KS-T16) | `Σ` digest unchanged; every pre-existing live label still live after the cycle; no label merged |
| fixed point | the loop reaches a `𝒦*` where the registered revocation set changes nothing further, in ≤ k cycles (k a registered parameter) |
| cancer (must be caught) | growth that edits `Σ`; growth that merges labels to survive revocation; growth from FEEDBACK alone |
| pluripotency | growth is warranted only through τ2 channels ≠ FEEDBACK (KS-T15) |
| apoptosis | the immune system (06) removes atoms whose label is `0` after admission, and quarantined atoms that never became reachable within `k` cycles |

## τ5 — Jump dynamics (rare; after a witnessed obstruction) `[SPEC → M4]`

| | |
|---|---|
| trigger | `Ω = OBSTRUCTION_WITNESSED` (KS-T19) **and** `JumpTrigger.is_admissible` (`src/orion_v2/jump.py`) |
| state | `T` (type vocabulary), atom classes, the quotient `~` — the *shape* of `𝒦`, never `Σ` |
| law | propose the minimum sufficient level `J_j` (J0–J8, v1 ladder; ME-X2 minimum escalation) whose rewrite makes the ceiling walker reach the target; admit only if S4/S5 hold and every existing label survives; the proposal is itself an atom with an EXACT_CHECKER or EXPERIMENTATION certificate — a Jump proposed by a codec has `L = 0` |
| invariant | monotone: the level never exceeds the minimum sufficient one (0 false escalations is the registered ME-X2 result) |
| termination | one rewrite per witnessed obstruction; re-run τ1; if still obstructed at J8 ⇒ `OBSTRUCTION_WITNESSED` is the final, honest answer |
| benchmark | v1 #558's 84 opaque worlds (48 positive zero-error cases, 36 controls) |

## Cross-scale write table

| field | τ1 query | τ2 learn | τ3 revise | τ4 grow | τ5 Jump | codec |
|---|---|---|---|---|---|---|
| `ρ, E_R, X_Q, Ω` | **write** | — | (triggers τ1) | — | (triggers τ1) | read |
| `A, H` (new) | — | **write** | — | via τ2 | via τ2 | — |
| `L` (existing) | — | never | never | never | never | **never** |
| `R` | — | — | **write** | via τ3 | — | — |
| `T`, classes, `~` | — | — | — | — | **write** | — |
| `d(a)` (existing) | — | never | never | never | recompute only on rewrite | — |
| `Σ` | — | — | — | — | — | — |
| `B` (spent) | **write** | write | write | write | write | write (its own) |

Every "never" cell has a planted-violation checker in 06 §forbidden edges.
