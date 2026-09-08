# 04 — Algorithms: pseudocode, cost, correctness, checker

Notation: `n = |A|`, `m = Σ_h (|tails(h)| + |heads(h)|)`, `ℓ = max |L(x)|`, `k = ⌈log ε / log(1−α)⌉`.
Complexity is measured once on real ME-X1 worlds (50 worlds, 3,492 atoms, 1,629 hyperedges) and the
receipt cites the row; a stated cost without a measurement is a defect. **Measured (#295):** M1
population 29 s / 50 worlds; M2 solve ≤ 123 steps and ≤ 26 hyperedge visits per instance under caps
of 2·atoms / 2·hyperedges / 1 restart, 0 overruns; trace T1 57 steps / 21 visits, T2 88 / 13. All numeric parameters are
in §P and have no literal default in code.

## A1 populate `[MACHINE: kso_m1_mex1_population_v1]`
```
populate(source, split, seed) -> 𝒦
  for world in source.generate(split, seed):
    for structure in decompose(world):             # atoms = claims, constraints, procedures, representations
      a ← Atom(id, kind, label = oracle_label(structure))   # M1: oracle; M2b: certificate label
      admit(a) or reject                             # KS-T08: edges > 0, registered type, reachable-or-quarantine
    for relation in world.relations: add Hyperedge(tails, heads, τ ∈ T, w)
  freeze d(a) for all a at R = ∅
  assert Σ(𝒦); assert no isolated atom
```
Cost `O(n + m)`. Correctness: KS-T00, KS-T08. Checker: planted isolated atom rejected 50/50; planted
`⊕`-merge caught 50/50; genome digest unchanged. Measured: 29 s / 50 worlds.

## A2 atomize `[MACHINE: kso_m0_freeze_checks_v1 (atomisation)] [SPEC: NL codec → M5]`
```
atomize(question) -> (s_Q, request_atoms, η_Q)
  parts ← decompose(question)                       # k parts ⇒ exactly k seeds (exactness criterion)
  for p in parts: a ← bind(p) or typed_reject(p)    # unbound part ⇒ GAP hook, never a guess
  s_Q ← normalise(indicator(bound atoms)); η_Q ← type prior for the question kind
  return committed, deterministic (s_Q, request_atoms, η_Q)
```
Cost `O(|parts| · lookup)`. Correctness: KS-T10a needs `s_Q` committed before navigation. Checker:
non-atomic / unbound input typed rejection; determinism across runs.

## A3 navigate `[MACHINE: navigation_matrix, restart_fixed_point, restart_step]`
```
navigate(𝒦, s_Q, η_Q, R, B) -> (ρ*, converged)
  W ← gated typed transition with frozen d (KS-T03/T04)
  if n ≤ N_exact: ρ* ← solve (I − (1−α) Wᵀ) ρ = α s_Q over ℚ        # exact rational
  else: ρ ← s_Q; repeat ρ ← α s_Q + (1−α) Wᵀ ρ until ‖Δρ‖₁ ≤ ε or B.steps exhausted
  return ρ*, converged (false ⇒ Ω = CANNOT_CHECK)
```
Cost: exact `O(n³)` rational; iterative `O(k · m)`. Correctness: KS-T05. Checker: rational witness
+ 200 random; renormalising mutant caught. `N_exact`, `α`, `ε` ∈ §P.

## A4 fire `[MACHINE: enabled_hyperedges]`
```
fire(𝒦, ρ*, R, θ) -> E_R = { h : g_R(h) ∧ ∀ a ∈ tails(h): g_R(a) ∧ ρ*(a) > θ }
```
Cost `O(m)`. Correctness: KS-T02. Checker: planted firing witness; dead tail disables.

## A5 extract `[MACHINE (uniqueness): kso_m0_freeze_checks_v1] [SPEC (optimiser) → M2]`
```
extract(𝒦, ρ*, E_R, s_Q) -> X_Q
  C ← connected component of supp(s_Q) in (A, E_R)                    # ungated? no: E_R is gated
  X_Q ← supp(ρ*) ∩ C  (unique, KS-T11)
  optional: π* ← argmax over hyperpaths in X_Q of Σ r_Q − λ·cost      # PCST-style; ties REPORTED
```
Cost `O(n + m)` for `X_Q`; optimiser NP-hard in general, bounded by `B`. Checker: planted tie shows
`X_Q` unique while `π*` ties.

## A6 compose `[MACHINE: kso_m0_freeze_checks_v1 (compose)]`
```
compose(parts) -> π with L(π) = ⊗ L(p)   # never ⊕, never a fresh label
```
Cost `O(|π| · ℓ²)`. Correctness: KS-T20. Checker: component revocation kills composite; merge mutant caught.

## A7 retract / cone / reinstate `[MACHINE: dependency_impact_cone; M1 retraction checker]`
```
revoke(c):    R ← R ∪ {c}; affected ← cone({c}) (least fixed point over dependency edges, KS-T09); re-run A3
reinstate(c): R ← R \ {c}; re-run A3; assert ρ == ρ_before(c)   # exact restore
```
Cost `O(|cone| + m)` + A3. Checker: 400/400 both directions; outside-cone atoms unchanged via an
independent ungated closure.

## A8 acquire (per channel) `[MACHINE: acquisition transaction] [SPEC: adapters → M2b/M3]`
```
acquire(t = (A⁺, H⁺, cert)):
  assert cert.kind ∈ KINDS; label ← {FEEDBACK: 0, EXACT_CHECKER: {{c}}, INSTRUCTION|DEMONSTRATION: {{src}}, INTERACTION|EXPERIMENTATION: {{obs}}}[cert.kind]
  for a in A⁺: assert H⁺ has an edge at a with τ ∈ T; assert reachable_from(A) or quarantine(a)
  commit; freeze d for A⁺ only; assert Σ; assert L unchanged on A
```
Cost `O(|A⁺| + |H⁺| + reachability)`. Correctness: KS-T08, KS-T13, KS-T15. Adapters `[SPEC]`:
INSTRUCTION from a registered structured source (M2b: algebra JSON — definitions, theorems, procedure
steps, discriminant cases, each with typed edges); EXACT_CHECKER = SymPy verification returning a
certificate `c` whose assumption is "SymPy `checkeq` at version v"; DEMONSTRATION = a trace
(A11) replayed and its steps admitted; INTERACTION = a dialogue turn; EXPERIMENTATION = an
executed generator query with its oracle answer.

## A9 consolidate `[SPEC → M3]`
```
consolidate(~): assert lumpable(~) (KS-T07) ∧ measurable(~) (S4); 𝒦 ← 𝒦/~; assert navigation commutes (pushforward test)
```
Parent: DreamCoder library learning. Checker: planted non-measurable merge rejected; 80/80 commutation.

## A10 self-revise `[MACHINE: S4/S5 predicates] [SPEC: operator → M3]`
```
self_revise(φ): assert S4(φ) ∧ S5(φ); 𝒦 ← φ(𝒦); assert every previously live label live
```
Parent: Gödel machine (proof-gated self-modification) × ATMS. Checker: planted `T` edit outside Jump rejected.

## A11 solve (the loop) `[MACHINE: kso_m2_solve_v1 (#295) — NAVIGATION_EXACT 38/50, STORE_EXACT 50/50, exact_by recorded per row; traces in 05]`
```
solve(question, B) -> (answer, X_Q, warrant, Ω, B_spent)
  (s_Q, req, η_Q) ← A2;  (ρ*, ok) ← A3;  if not ok: return (⊥, ∅, 0, CANNOT_CHECK, B)
  E_R ← A4;  X_Q ← A5;  π ← A6(path in X_Q to req)
  Ω ← outcome(π, ceiling_walk(𝒦, s_Q, req))        # KS-T19
  if Ω = FOUND: warrant ← L(π); if cert available: warrant ← warrant ⊗ EXACT_CHECKER(answer)
  answer ← render(X_Q, π, warrant, Ω)              # codec side, read-only (M5); M2: structured object scored by the oracle
```
Correctness: the answer is scored by the oracle (M2) / the exact checker (M2b); the codec's fluency
is never the warrant (S7). Cost = A2 + A3 + A4 + A5 + A6 + ceiling walk `O(n + m)`.

## A12 outcome rule `[MACHINE: four-valued outcome]`
```
outcome(π, ceiling):
  if π reaches req with live label: FOUND
  elif not converged or B exhausted: CANNOT_CHECK (or GAP if the ceiling walker reaches req)
  elif ceiling reaches req: GAP_NOT_FOUND (channel hook: which atom/edge is missing)
  elif req non-identifiable under s_Q or ceiling fails: OBSTRUCTION_WITNESSED (JumpTrigger)
```

## A13 Jump-propose `[SPEC → M4]`
```
jump(witness): level ← min j ∈ J0..J8 such that rewrite_j makes ceiling reach req; assert admissible (KS-T14); proposal is an atom with cert ≠ FEEDBACK
```
Benchmark: v1 #558 84 opaque worlds; ME-X2 0 false escalations.

## A14 comparator arms `[MACHINE: kso_m2_comparator_v1 (#298, stacked on #295) — B5 50/50, RWR/PPR 32/50, CBR/KG 34/50, null 5/50, oracle 50/50; KSO_NAVIGATION_ONLY column being added]`
Arms on identical `(𝒦, s_Q, B)`: strongest `mex1_parents` solver; RWR/PPR retrieval (renormalised —
the parent, so the delta is visible); CBR / KG retrieval; (M5) LLM alone; retrieval-QA. Scoring: exact
agreement with the oracle per instance; paired test; overrun ⇒ `CANNOT_CHECK` (KS-T17).
Expected honest result `PARENT_SUFFICIENT`.

## §P Parameters (no literal defaults in code; `os.environ` + registered study, KS-T21)

| name | env | role | default source |
|---|---|---|---|
| `α` | `OCM_RESTART_ALPHA` | restart probability | walk-forward study on ME-X1 dev, all costs |
| `ε` | `OCM_FIXED_POINT_EPS` | iterative stop | same |
| `N_exact` | `OCM_EXACT_MAX_ATOMS` | exact-vs-iterative switch | same (wall-clock crossover) |
| `θ` | `OCM_FIRE_THRESHOLD` | activation to enable a tail | same |
| `λ` | `OCM_EXTRACT_COST_WEIGHT` | optimiser cost weight | same |
| `B.*` | `OCM_BUDGET_STEPS/EDGES/RESTARTS/WALL` | matched budget | same, equal across arms |
| `k` | `OCM_GROWTH_MAX_CYCLES` | growth fixed-point bound | same |
| `η_Q` | `OCM_TYPE_PRIOR_<KIND>` | type prior per question kind | same |

The study is one artifact (`results/KSO_PARAMETER_STUDY_V1.json`, `[SPEC → M2]`); every default in
the receipt cites its row. A default that cannot be traced is a defect.
