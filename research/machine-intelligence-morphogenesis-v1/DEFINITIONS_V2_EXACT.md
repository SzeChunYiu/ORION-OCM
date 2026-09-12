# Definitions v2 — exact-checkable specialization of `DEFINITIONS_V1.md` (Track B, GMI-D1)

Status: `DRAFT_FOR_HOSTILE_REVIEW` · additive to V1, supersedes nothing · `EXPLICITLY_NON_FINAL`.
Authority: #377 under #233/#373; programme #165. Proof classes P1–P5 and `Σ_t`, `U`, `B_t`,
`Ev_t` are inherited unchanged from `../heritable-search-transformation-v1/HST_DEFINITIONS_V1.md`.

Why a V2: V1 fixes the *shape* of `B = (T,P,C,U,ρ)`, `M = (G,X,Θ,Π,L,K)`, `Φ_E(M) = (Q,R,D,S)`,
`E = (D_τ,O,A,F,V,p,b,H,Δ)`, `Γ`, and the D0–D3 ladder. It leaves four things at prose level that
an exhaustive checker cannot consume: (i) what a composition grammar `C` and update family `U`
may contain without smuggling an architecture; (ii) what the structural observable `S` is, so
that "neural / symbolic / …" become decidable label-free predicates; (iii) at what *resolution*
a bounded-compilation statement stops being universal computation; (iv) which ecology
coordinates already carry a theorem-grade tractability flip. V2 fixes those four, in the V1
symbols. Every V2 definition is checkable by enumeration in a finite tiny world (P2) before it
may appear in a P1 statement.

---

## 0. Resource coordinates and bounds

- `r = 5` registered coordinates on `R`: `desc` (canonical description bits incl. state),
  `exec` (work per query), `upd` (work per feedback event), `ver` (work per registered
  check by `V`), `rev` (work per revocation/repair event under `Δ`). Never scalarized unless
  `p` was frozen prospectively (V1 §3, HST §3).
- `v ⪯_K w` on resource vectors means coordinate-wise `v_i ≤ α_i·w_i + β_i` for a frozen affine
  bound `K = (α, β)`. `K∘K'` is the composed affine bound. `K = poly` denotes any polynomial
  bound and is *sub-resolution* (§5).
- A **finite scope** `S = (n_max, T_fin, D_fin, H)`: max composite size, finite type universe,
  finite input domain per type, horizon. Every P2 row names its scope.

## 1. Basis: what `P`, `C`, `U`, `ρ` may contain

**Def 1.1 (typed primitive, refines V1 §1).** `p = (S_p, I_p, O_p, δ_p, F_p, α_p, c_p)` adds to
V1's `(S_p, I_p, O_p, δ_p)` a feedback type `F_p` (may be the unit type `1`), a local adaptation
contract `α_p : S_p × F_p → D(S_p)`, and a declared cost vector `c_p` (per `δ_p` activation on
`exec`, per `α_p` activation on `upd`, a constant on `desc`). `p` is *inert* iff `F_p = 1`.

**Def 1.2 (registered combinators = the composition grammar `C`).** V2 admits exactly:
```text
seq    : (A→B) × (B→C) → (A→C)                cost: sum
par    : (A→B) × (C→D) → (A×C→B×D)            cost: sum(desc), sum-or-max(exec) declared per basis
case   : (A→B) × (A→B) × (A→Bool) → (A→B)     cost: sum(desc); exec = guard + max(branches)
loop_n : (A×S→B×S) → (A→B)                    bounded n-fold unrolling; cost: n·body + desc(n)
fbk    : (A×F→B×F') → (A→B)                   wires a feedback port to a feedback source; desc only
```
No unbounded fixpoint. A basis needing one declares it and pays the §5 test.

**Def 1.3 (compositional update family `U`, closes the "smuggled update" hostile).** The
feedback reaching a primitive occurrence inside a composite is a function of (a) the feedback at
the composite's output ports and (b) the states/outputs of primitives on the path between them,
and that function is itself computed by primitives of `P` under `C`. A basis whose update law
needs an operation outside `P ∪ C` is *not closed*; the missing operation is named (this is how
`BACKPROP`, `BAYES_UPDATE`, `PROGRAM_SYNTHESIS` are prevented from hiding inside `U`). Hostile
ids: `H-ARCHITECTURE-MACRO`, `H-NEURAL-EMULATOR`, `H-PROGRAM-INTERPRETER` (V1 registry).

**Def 1.4 (generated class).** `Gen_n(B)` = well-typed closed composites with ≤ n primitive
occurrences, modulo the registered syntactic identities (assoc/unit of `seq`/`par`, dead-branch
elimination), canonical form fixed by census code. Finite and exactly enumerable at scope `S`.

**Def 1.5 (composite as machine).** `⟦x⟧ = (Q_x, δ_x, α_x, c_x)`; `Θ_x := Q_x = ∏ S_p` (there is no
mutable state other than local states); `α_x` is induced by `U`; `c_x` by `ρ`.

## 2. Ecology coordinates that already carry a theorem (refines V1 §3)

V1 lists 19 candidate coordinates. V2 registers the subset on which a *parent theorem already
proves a tractability/learnability flip*, so that a Track-B phase claim on that axis is
parent-anchored rather than invented (full table with sources: `ECOLOGY_AXES_V2.json`;
parent verification in `PARENT_LEDGER_V2.json`, family P9B):
```text
verification_strength   passive examples → membership+equivalence queries   (DFA: Gold/Pitt–Warmuth vs Angluin L*)
feedback_type           scalar_loss (gradient/SQ) vs exact counterexample     (parity: Kearns SQ; Abbe et al.)
data_volume × compute   more samples buy less computation                     (comp–stat tradeoff)
noise                   SQ noise tolerance vs exact-consistency learners      (Kearns)
distribution structure  uniform vs arbitrary distributions                    (Valiant evolvability)
task_diversity          memorization → generalizing learning algorithm        (Kirsch et al., empirical)
```
`feedback_type` is a *hard* axis: a morphology whose `fbdep` (§3) misses every feedback type in
`F` cannot develop in `E` at all. `algorithmic_structure = PARITY_LIKE` with `F = {scalar_loss}`
is the registered negative control (`PH-5`): any D5 diagram on which a gradient morphology
"develops" there has an assay defect.

## 3. The structural observable `S`: five label-free coordinates

**Def 3.1.** For any composite or parent reference `x`, `S(x)` is the 5-tuple
```text
theta_type(x)        ∈ {DISCRETE_FINITE, BOUNDED_NUMERIC, MIXED}          type of Θ_x
update_locality(x)   ∈ {NONE, LOCAL_O1, SPARSE_SUBLINEAR, DENSE_LINEAR}   max_e |{occurrences whose state changes on event e}| / |Θ_x|
feedback_dependence  ⊆ {scalar_loss, exact_counterexample, query_access, likelihood_score}   types under which Θ_x changes at all
execution_shape(x)   ∈ {ACYCLIC_FIXED_DEPTH, BOUNDED_LOOP, STORE_MATCH_CYCLE, ENUMERATE_TEST_CYCLE, SAMPLE_SCORE_CYCLE}
store_discipline(x)  ∈ {NONE, INDEXED_EXEMPLARS, RULE_SET, TERM_LIBRARY, TRACE_DISTRIBUTION, PARAMETER_ARRAY}   organization of the growing part of Θ_x
```
Each coordinate is decidable from `⟦x⟧` and the registered feedback protocol at finite scope.
None names a parent architecture. `MORPHOLOGY_SIGNATURES_V2.json` registers seven signatures
`M0…M6` as conjunctions over these coordinates (V1's `known_form_hypotheses`, made decidable).

**Def 3.2 (phenotype, in V1 letters).** `Φ_E(x) = (Q_E(x), R_E(x), D_E(x), S(x))` with `Q` the
full finite outcome table before feedback, `D` the sequence of `Q`-tables after each registered
feedback event, `R` the charged 5-vector over the horizon, `S` as above.

## 4. Bounded compilation and equivalence, exactly

**Def 4.1 (reference implementation).** A parent morphology enters only as a reference `m` in
the parent's own formalism with the parent's own cost accounting `c_M(m)` on the same 5
coordinates; coordinates the parent never charges are `UNCHARGED_BY_PARENT` and Track B reports
absolute cost there instead of a ratio (`EQUIVALENCE_CONTRACT_V1.md` §1–2 tolerances apply).

**Def 4.2 (compiler; D1 clauses C1–C6).** `Compile_B : Ref_M(S) → Gen(B)` is a **K-bounded
Dev-preserving** compiler iff for all `m`, all `E ∈ 𝓔`:
```text
C1  Q_E(Compile_B(m)) = Q_{M,E}(m)                  semantic preservation (exact at finite scope)
C2  D_E(Compile_B(m)) = D_{M,E}(m)                  update-law preservation
C3  R_E(Compile_B(m)) ⪯_K c_M(m)                   per-coordinate overhead
C4  Compile_B(m) ∈ Gen(B) under U — no operation outside P ∪ C   (Def 1.3)
C5  a decompiler exists with decompile∘compile = id on Ref_M(S)  (reported; required where feasible)
C6  every run-time constant/table the composite reads is charged into desc
```
Result vocabulary: `K_DERIVED` (C1–C4,C6), `FORWARD_K_DERIVED` (C2 fails), `REPRESENTABLE_ONLY`
(only at `K ≥ K_sim`, §5), `NOT_DERIVABLE_AT_SCOPE`, `SMUGGLED_<op>`, `UNCHARGED_<item>`.
V1's `BEHAVIORAL_COMPILATION_ONLY` = `FORWARD_K_DERIVED`.

**Def 4.3 (phenotype equivalence `≈_{𝓔,ε,K}`; V1 §2 developmental equivalence made exact).**
`x ≈ y` iff `Q` and `D` tables agree (within `ε`, `ε = 0` default) on every `E ∈ 𝓔` **and**
K-bounded compilers exist in both directions on the singleton classes. The third clause is what
separates a lookup table from a rule set from a parametric approximator when their tables
coincide. One-directional K-bounded compilation is the preorder `x ≼_K y` (V1 §1–2).

**Prop 4.4 (relation type; answers V1 registry GMI-T3 "non-transitivity" attack).** `≈_{𝓔,ε,K}`
is reflexive and symmetric for every `K`; it is transitive with bound `K∘K` (so an equivalence
relation when `K` is closed under composition, e.g. `K = poly`, or any fixed class closed under
`∘`), and a *tolerance* (not transitive) at a fixed affine constant `K`. Every row states which.
Proof: `proofs/GMI_PROOFS_V1.md` §T2.

**Def 4.5 (basis equivalence `B_1 ≡_K B_2`).** Each primitive of `B_1` is `Φ`-equal to a
composite of `B_2` with overhead `⪯_K`, and conversely. Same relation-type remarks as 4.4.

**Def 4.6 (morphology class, label-free).** `𝓜_k(𝓔,ε,K) = { x : ∃ y, Sig_k(y) ∧ x ≈_{𝓔,ε,K} y }`.
Membership in several classes is reported as `HYBRID_OR_AMBIGUOUS`; membership in none is
`NOVELTY_CANDIDATE_AT_K` (subject to `EQUIVALENCE_CONTRACT_V1.md` §6 and #377 §18). Novelty is
relative to the frozen `K`: what is novel at `K` may be a cheap encoding at `K' > K`.

**Def 4.7 (frontier and phase boundary; V1 `Frontier(B,E,H)` made class-valued).**
`M*(E) = { k : some x ∈ 𝓜_k with Q_E(x) ≥ θ_E lies on the R-Pareto frontier among all x with
Q_E(x) ≥ θ_E }`. A phase boundary between `k, k'` on axis `a` is `a*` with `k ∈ M*, k' ∉ M*` on
one side and the reverse on the other, all other axes frozen. Exactly enumerable at finite scope.

## 5. Resolution: where the theory stops being universal computation

**Def 5.1 (reference universal basis `U`).** Bounded-cell mutable memory + finite instruction
set + interpreter loop + uniform costs (instruction counts on `exec/upd/ver/rev`, program+memory
bits on `desc`). By the invariance thesis (P9A ledger, van Emde Boas) every "reasonable" `B`
simulates and is simulated by `U` with polynomial `exec`/`desc` overhead.

**Def 5.2 (self-simulation band).** `K_sim(B)` = the least affine class at which `B ≡_{K_sim} U`.

**Prop 5.3 (GMI-T0 core, P1).** For any basis `B` and any `K ⪰ K_sim(B)∘K_sim(B)`, the quotient
`Gen(B)/≈_{𝓔,0,K}` identifies every pair with equal `Q` and `D` tables; all signatures `M0…M6`
fall into one class and `M*(E)` is the same singleton for every `E`. Proof: at that `K` mutual
compilation through `U` is K-bounded for every pair with equal tables, so clause 3 of Def 4.3
holds vacuously; classes coincide; the frontier is one class (`proofs/GMI_PROOFS_V1.md` §T0).

**Cor 5.4 (content criterion, replaces V1 §5 prose).** A Track-B statement carries
intelligence-specific content only at resolutions `K ≺ K_sim(B)` — explicit constant-factor or
additive per-coordinate bounds — and/or on coordinates (`upd`, `ver`, `rev`) where the parent
simulation theorems are silent. Any row stated at `K ⪰ K_sim∘K_sim` is automatically
`UNIVERSAL_COMPUTATION_ONLY`.

**Def 5.5 (universality test per candidate basis; instantiates V1 `H-UNIVERSAL-COMPUTATION`).**
Candidate `B_c` passes at scope `S` iff there is a registered prediction about `κ` (per
coordinate) or about `M*(E)` for a registered `E` that (i) is stated with `K ≺ K_sim(B_c)`, (ii)
differs from the same claim evaluated under `U` with uniform cost, and (iii) is decidable by the
D2/D3 microscopes. Otherwise `UNIVERSAL_COMPUTATION_ONLY_<B_c>`. Instances per candidate
`B0…B3`: `BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json`.

## 6. Learning-law specialization (V1 `LEARNING_LAW_ATLAS_V1.md`, made checkable)

A learning law at the composite level is `(fbdep(x), α_x)`. A parent law `λ_M` is *specialized
from `B`* iff a Dev-preserving compiler for `Ref_M` exists whose induced `α` uses only `P ∪ C`
under `U` (no update primitive added). The per-law report keeps #377 §10's nine fields; training
objective (`F`) and verification authority (`V`) are distinct coordinates and are never merged.

## 7. Derivation levels (unchanged from V1 §4; restated with V2 objects)

```text
D0  ∃ x ∈ Gen(B): Q_E(x) = Q_{M,E}(m)                         any K; usually parent-owned
D1  ∃ K-bounded Dev-preserving Compile_B with K ≺ K_sim       this lane's exact object
D2  ∃ registered process from x_0 ∉ 𝓜_k reaching 𝓜_k, no label in the process, cost charged
D3  frozen Γ: E ↦ predicted M*(E), verified on held-out E
```

## 8. What V2 still does not define

"Intelligence"; a unique minimal basis (tested by compensation-aware removal, four
irreducibility notions, in `STAGE_C1_STRUCTURED_BASIS_PROTOCOL_V1.md` and
`microscopes/STAGE_D_CROSS_BASIS_COMPILATION_DESIGN_V1.md`); any semantic property of
arbitrary programs (HST-T15); anything outside a registered finite ecology family (GMI-T9).
