# HSG-v4 Semantic-Execution Layer — Definitions V1 (FROZEN)

Additive formal layer under HSG, inside #93's General Epistemic Field factorization.
Source amendment: #233 HSG v4 (semantic/obligation-execution mathematics + exact-checker
bridge + continuous evidence programme). NOT a new cognitive core; does not alter
`M_t=(F_t,O_t,Π_t,C)`; does NOT unlock N2/N4/N5; does not disturb the D15 revival freeze.
Framework is EXPLICITLY_NON_FINAL: stronger mathematics, counterexamples, or empirical
evidence supersede via append-only/RGC discipline — defending this layer against a
stronger formulation is a defect.

## 1. Generalized semantic-execution object

For domain/context `d`, at the most general registered form needed at scope:

```text
E_d = (
  X_d,          external observations / requests / problem statements
  Ω_d,          typed semantic / obligation states
  Y_d,          external outputs / actions / certificates
  M_d,          optional model/world class for satisfaction semantics
  I_d,          interpretation relation/kernel X -> Ω
  T_d,          obligation transformation hypergraph/kernel
  R_d,          realization relation/kernel Ω -> Y
  J_d,          reverse interpretation / certificate-reading relation Y -> Ω
  P_d,          protected semantic projection / decision contract
  |=_d,         domain satisfaction relation where applicable
  V_d,          external checker/evaluator
  C             constitutional authority / commit boundary
)
```

`I_d`, `R_d`, `J_d` are **not assumed to be functions**: finite relations, ambiguity
sets, posteriors, stochastic kernels, or CANNOT_CHECK partial relations. `Ω_d` is NOT
assumed to be one universal interlingua.

## 2. Semantic-execution episode

```text
x
 -> interpret I_d
 -> ambiguity/belief/obligation state μ_0
 -> HSG-guided sequence of legal operations
      DISTINGUISH / DECOMPOSE / REDUCE / REFINE / REWRITE /
      PLAN / PROVE / SYNTHESIZE / VERIFY
 -> verified terminal obligation ω*
 -> realize R_d
 -> output y
 -> reverse-read J_d
 -> protected projection P_d check
 -> C-authorized commitment
```

## 3. Transformation layer

A directed hypergraph of sound rules. A rule

```text
r : {ω_1,...,ω_k} => ω
```

is semantically sound on registered scope iff satisfaction of all premises implies
satisfaction of the conclusion (per the domain's `|=_d`, where applicable).
Search algorithms are SEPARATE from this semantic licence: no search procedure
earns soundness by finding derivations, and no derivation loses soundness by being
expensive to find.

## 4. Complete semantic-execution burden

Vector random variable, never automatically scalarized:

```text
B_exec,t(d,q) = E[
  interpretation
  + ambiguity resolution / information acquisition
  + obligation search / transformation
  + abstraction/refinement
  + external execution/tools
  + verification
  + realization
  + reverse-read/commit
  + rejected/failed attempts
  + provenance/index/storage/maintenance/revision
  + CPU/GPU/wall/IO/human information
  until first C-admissible semantically valid result
  | HSG state at t ]
```

When stage accounting is disjoint, `B_exec` decomposes by linearity of expectation
(T76), but local stage-wise minimization is not generally valid (T75 hostile).

Developmental target, only on fresh registered families: `B_exec,t+1 < B_exec,t`
and/or useful-solution hitting burden falls, while correctness/coverage/
negative-transfer gates hold (measured at D27).

## 5. AGP extension atoms (each walks the existing ladder; never frozen as singletons)

| atom | required generalized forms |
|---|---|
| meaning | equivalence class / ambiguity set / posterior / context-indexed relation |
| interpretation | partial relation → kernel → learned/contextual/meta-updated kernel |
| obligation | set/poset/hypergraph node; exact/approx/risk-bearing forms |
| derivation | tree → DAG/packed forest/e-graph/provenance object → distribution |
| proof | proof equivalence set + proof-strategy distribution + future-reuse neighborhood |
| problem reduction | correspondence/category of sound reductions + cost + reversibility/coverage |
| abstraction | quotient/Galois connection/bisimulation + refinement dynamics |
| counterexample | witness + eliminated hypothesis region + provenance/authority |
| output | equivalence family of valid realizations, not one canonical string |
| reverse-read | relation/kernel with coverage, false-negative and false-positive coordinates |
| dialogue state | dynamic context/belief/commitment state with authority distinctions |
| certificate | proof/test/statistical/empirical evidence object with checker scope |

## 6. Frozen finite worlds (exhaust tiny worlds FIRST; scale only when exhaustive
search is genuinely expensive)

```text
OW1  obligation hypergraphs          parsing/proof/planning-isomorphic structures
OW2  ambiguity + safe-action sets    T68/T69 + clarification/VOI
OW3  round-trip semantics            T66/T67 + omitted-reading hostile
OW4  provenance/support              T71–T73 + revocation/alternate support
OW5  abstraction/refinement          T77–T80 + spurious counterexamples
OW6  reduction/equality              T74/T86 + unsound-rewrite hostile
OW7  heterogeneous logics            T84/T85 + incomplete-model-image hostile
OW8  planning hierarchy              STRIPS/HTN/POMDP/options phase map
OW9  cross-domain same-hypergraph    same abstract derivation, different semantics/checkers
OW10 developmental family stream     continued/reset inheritance burden
```

## 7. Evidence classes (never conflated)

```text
EXPLORATORY_ADAPTIVE       adaptive search; never a headline claim
CONFIRMATORY_FIXED         pre-registered frozen spec/size/seed
CONFIRMATORY_ANYTIME_VALID confidence-sequence/e-process with exact assumptions
```

An adaptive exploratory discovery becomes a headline claim ONLY after a fresh frozen
confirmation or a prospectively valid anytime procedure. Adaptive decisions are written
to the decision ledger BEFORE new submission.

## 8. Reuse bindings (no second campaign-governance system)

- Freeze/checkpoint/adaptivity/receipt machinery: REUSE #221
  (`research/ocm-morphology-zoo-v1/hpc/` submission+freeze+receipt pattern,
  `GRAND_SEARCH_R*_FREEZE.json` conventions, continuous/ scheduler + UNCERTAINTY
  ledger pattern from #268/#269/#271).
- Job identity: campaign_id, theorem_or_atom_id, world_id, domain_id,
  representation_id, operator/rewrite set, search kernel, history condition,
  checker id+digest, fidelity tier, seed, freeze sha.
- Receipt: raw terminal, complete B_exec vector, obligation nodes/hyperedges/
  derivations/SCCs, ambiguity size/entropy where meaningful, protected-coordinate
  round-trip errors, counterexample + version-space shrinkage, abstraction/refinement
  count, provenance supports/alternative supports, reduction/proof/rewrite path,
  operator/library reuse identities, active/touched k and total N, wall/CPU/GPU/IO/
  storage, negative/CANNOT_CHECK status.

## 9. Placement doctrine

CPU for branchy exact semantics, proof/search, provenance, CEGAR, discrete planning,
checker-heavy paths (LUNARC lu partitions; laptop billy / billy-old for spread).
A40 GPU only where measured batched dense work justifies (large response matrices,
surrogate ranking, batched proposal projections). Never change semantics for GPU
utilization.

## 10. Scope locks (hard)

- N2 (language protected outcomes): LOCKED. D23 uses synthetic/frozen semantic
  tuples only.
- N4 (formal proof protected outcomes): LOCKED until roadmap predecessor closes.
  D22 starts finite/exhaustive; Lean/SMT adapters only later; D24 uses legal known
  fixtures + synthetic finite theorem worlds.
- N5: LOCKED; D25/D26 are research laboratories, not adoption tests. #217 owns
  canonical developmental adoption; #221 may explore but never adopt.
- Frozen prior evidence (HST/HSG v1–v3, D12–D15): append-only; never reinterpreted.
