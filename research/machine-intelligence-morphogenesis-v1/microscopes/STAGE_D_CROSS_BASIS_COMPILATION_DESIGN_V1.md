# Stage D — cross-basis compilation matrix (design freeze candidate; NOT launched)

Status: `DESIGN_FREEZE_CANDIDATE` · runs on ordinary hardware (exhaustive, tiny) · no #221/#220 search,
no HPC. Owner: #377 GMI-D3 (with GMI-D2 residual). Absorbs Codex `EXACT_MICROSCOPE_V1.md` Stage C-v2
and Stage D into one instrument, because Stage C-v2 (`STAGE_C2_PROGRAM_PARENT_IDENTITY_V1.md`) has
already shown that a *representation* comparison against a matched program parent is vacuous by
construction. What is not vacuous is the per-coordinate cost of **update, verification and revision
under charged resource semantics**, and the **direction of frontier change** predicted from label-free
observables before measurement (GMI-T10-A). That is what this instrument measures.

## 0. One question

> For six tiny reference morphologies and four candidate bases plus two parent columns, what is the
> exact per-coordinate overhead vector `κ(M_k, B_c)` of a `Dev`-preserving compilation at a
> resolution `K ≺ K_sim`, and is the matrix flat (universal computation only) or structured by
> coordinate in the frozen, predicted directions?

Decides: GMI-T2 (matrix), GMI-T3 (class separation and encoding band), GMI-T4/T5/T7/T8 constants,
the four `UNIVERSAL_COMPUTATION_ONLY_<basis>` tests (`BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json`),
and supplies the inputs of the GMI-T10 phase model (Stage E). It also answers Codex Stage C-v2's
"why is one update/search geometry developmentally efficient" at the smallest scope where the
question is not vacuous.

## 1. Frozen scope `S`

```text
n_max      = 12 primitive occurrences per composite (raise once to 16 by declared amendment only)
types      = Bool, Fin(4), fixed-point numeric at b = 4 bits (2 integer, 2 fractional)
input      = full finite domain per reference (no sampling)
horizon    = H = 8 feedback events per registered protocol
ladder     = |Θ| ∈ {2, 4, 8}   (three sizes per reference family; needed for GMI-T11 identifiability)
drift      = one registered revocation event at t = 5 (feeds the rev coordinate)
verifier   = exact table check after every event (feeds the ver coordinate)
```

## 2. Rows — reference morphologies (parent formalism, parent accounting)

| row | reference `m` | parent accounting `c_M(m)` | Dev protocol (feedback type) | size ladder |
|---|---|---|---|---|
| M0 | 3/4/8-state Mealy machine | states × alphabet (desc), 1 step (exec), `UNCHARGED` (upd) | none | states |
| M1 | 4-rule production system over a 3-slot store, one chunking event | Rete match cost (exec), rule add (upd), justification revoke (rev) | exact_counterexample | rules 2/4/8 |
| M2 | 5-node program over `{seq, case, loop_2, const}`, one library-append event | AST size (desc), interpreter steps (exec), enumeration count to next candidate (upd) | exact_counterexample + query_access | nodes 3/5/8 |
| M3 | 3-variable finite Bayes net, one conditioning event | CPT entries (desc), variable-elimination ops (exec), normalization ops (upd) | likelihood_score | variables 2/3/4 |
| M4 | 2-2-1 affine+threshold net at b=4, one gradient step | weights (desc), MACs (exec), gradient MACs (upd) — parent charges via Learn-category request maps | scalar_loss | hidden 1/2/4 |
| M5 | indexed exemplar memory, one insert | entries (desc), lookup (exec), insert (upd) | exact_counterexample | entries 2/4/8 |

Optional row (declared amendment): `M1'` = TMS-labelled variant of M1 and `M1''` = blackboard variant,
to decide the multi-occupant cell of `SIGNATURE_HOLE_CENSUS_V1` (prediction P3).

## 3. Columns — targets

| column | target | role |
|---|---|---|
| B0 | local adaptive transducers (`BASIS_CANDIDATES_V1`) | candidate |
| B1 | compositional learner (typed maps + update/request) | candidate |
| B2 | rewritable typed program graph (typed rewrite + store) | candidate |
| B3 | stochastic generative kernel (sample/score/normalize + arithmetic) | candidate |
| U  | reference universal basis: flat table / interpreter with uniform costs (D2-§5.1) | parent (upper band) |
| P3 | compressed program parent with the same low-level ops (Codex Stage C-v2's fair parent) | parent (lower band) |

Each candidate's primitive set, combinator subset, update family `U` and cost algebra `ρ` are frozen in
`BASIS_CANDIDATES_V1.json` + this file's amendment table before any compiler is written (C4 audit needs
them). No candidate may contain `NEURON`, `BACKPROP`, `PRODUCTION_RULE`, `BAYES_UPDATE`,
`PROGRAM_INTERPRETER`, `ATTENTION` as a primitive (hostile `H-ARCHITECTURE-MACRO`).

## 4. Procedure (exhaustive at scope; every step emits a certificate)

1. **Reference tables.** For each `m` on the ladder compute `Q`, `D` (8 events + drift) tables exactly.
2. **Compiler search.** For each `(m, B_c)` find the minimal-`desc` composite in `Gen_{n_max}(B_c)` that
   satisfies C1 (table equality) and C2 (Dev-table equality) by exhaustive enumeration with
   canonicalization (`Gen_n` is finite); record `NOT_DERIVABLE_AT_SCOPE` if none exists at `n_max`.
   Compiler *code* is charged as `C_build` in a separate ledger, never in `κ`.
3. **C4/C6 audit.** Verify the composite uses only `P ∪ C` under `U_B`; charge every run-time constant
   into `desc`. Violations → `SMUGGLED_<op>` / `UNCHARGED_<item>` (row void for that column).
4. **Overhead.** `κ(m, B_c) = R_E(composite) ⊘ c_M(m)` per coordinate; absolute where the parent is
   `UNCHARGED` (rule 2 of `EQUIVALENCE_CONTRACT_V1.md` §4).
5. **Band.** Compute `K_sim` at scope from the `U` column both ways (compile `U`-programs into each
   `B_c` and vice versa for the six references) — this is the resolution ceiling of Prop D2-5.3.
6. **Matrix statistics.** Per coordinate: range across columns for each row; per row: range across
   coordinates. "Flat" = every entry within the frozen band `K_flat = (2×, +4)` of the row's minimum.
7. **Class separation (GMI-T3).** For each pair of rows, minimal mutual overhead within the *same*
   column; pairs mutually compilable within `K = (2×, +4)` on all five coordinates are one class at scope.
8. **Identifiability (GMI-T11).** For each pair of rows, does the ladder + drift probe separate their
   `R` profiles? Emit `SEPARABLE` / `NOT_IDENTIFIABLE_AT_SCOPE` per observable.
9. **Universality tests.** Evaluate the four Def 5.5 tests from
   `BASIS_CANDIDATES_V2_UNIVERSALITY_TESTS.json` against the matrix.

## 5. Frozen predictions (before any compiler exists)

```text
P1  NOT FLAT on upd:  κ_upd(M4, B2) ≥ mult(4) · κ_upd(M4, B1)   (arithmetic-emulation factor, b=4)
                      κ_rev(M1, B0∪B1∪B3) > κ_rev(M1, B2)        (provenance-local revocation only in B2)
P2  COMPRESSION CROSSOVER on desc:  U dominates all candidates at the smallest ladder point of M0/M4,
                      loses to every candidate at the largest ladder point (table growth vs factorization)
P3  ONE CLASS: M1, M1', M1'' mutually K-compilable within (2×, +4) on all coordinates (census multi-occupant cell)
P4  LOCALITY SIGN (GMI-T10-A input): κ_upd(M4, ·) grows with |Θ| at every column; κ_upd(M1, ·), κ_upd(M5, ·) do not
P5  SUB-BAND NON-EMPTY (GMI-T0 witness): at least one row pair has equal tables and minimal mutual
                      overhead outside (2×, +4) but inside K_sim∘K_sim
```

Falsifiers and their terminals:

| observation | terminal |
|---|---|
| matrix flat within `K_flat` on all coordinates | `UNIVERSAL_COMPUTATION_ONLY` at scope (for the whole candidate set) |
| P1 sign reversed on either clause | cost model of GMI-T5/T10-A wrong at scope (revise ρ or Lemma A's premise; ASSAY_DEFECT if ρ does not charge per coordinate) |
| P2 fails (U never loses on desc) | `n_max` too small to show factorization — declared single amendment to 16, else `REPRESENTATION_PRICE_REGIME_ONLY` |
| P3 fails | signature lattice too coarse in the `RULE_SET` direction — split the observable (`SIGNATURE_HOLE_CENSUS_V1.md` §5), do not re-label |
| P4 fails | `update_locality` not identifiable at this ladder — `MORPHOLOGY_NOT_IDENTIFIABLE_AT_SCOPE` for that observable |
| P5 fails | no sub-band regime at scope: every table-equal pair is within the band — Track B's content regime is empty here; raise resolution or report `UNIVERSAL_COMPUTATION_ONLY` |

## 6. Hostiles bound to this instrument (from `HOSTILE_REGISTRY_V1.json` + #377 §14)

- `H-ARCHITECTURE-MACRO`, `H-NEURAL-EMULATOR`, `H-PROGRAM-INTERPRETER` → step 3 audit, per composite.
- `H-STATIC-EQUIVALENCE` → C2 is mandatory; forward-only compilations are recorded as `FORWARD_K_DERIVED`
  and never enter the class-separation step.
- `H-HIDDEN-RESOURCE` → ρ charges every state write (Lemma A premise), every constant (C6), every check (ver).
- `H-ENCODING-BIAS` → the band lemma (proofs §T3) is computed from step 5; any separation inside the band
  is reported as `SEARCH_ENCODING_DOMINATES`, not as a class difference.
- `H-POSTHOC-PRICE` → no scalarization anywhere in Stage D; Stage E freezes prices separately.
- `H-NEURAL-PRIVILEGE` → each reference is compiled by exhaustive minimal-`desc` search in every column; no
  hand-tuned compiler for any row.
- **New: H-LADDER-LEAK** — the size ladder must not be visible to the compiler search as a label (it
  changes `|Θ|` only through the reference).

## 7. Outputs

`microscopes/results/STAGE_D_MATRIX_V1.json` (κ tensor rows×columns×coordinates×ladder, K_sim,
class-separation table, identifiability table, universality verdicts, sha256 chain of frozen inputs),
`STAGE_D_REPORT_V1.md`, and a registry patch touching only the `status`/`evidence` fields of
GMI-T2/T3/T4/T5/T7/T8/T11 in `THEOREM_REGISTRY_V4.json` (statements frozen).

## 8. Execution order

```text
D-0  independent hostile review of this design (fresh-context agent; #377 §20 GMI-D1 list)
D-1  freeze basis definitions B0..B3 primitive/combinator/ρ tables (amendment to BASIS_CANDIDATES_V1)
D-2  implement reference tables + canonical enumerator + C4/C6 auditor + planted-hostile selftests
D-3  run rows × columns × ladder on ordinary hardware; emit certificates
D-4  evaluate P1–P5; write report; registry patch; revival record for every negative (#373 §8)
D-5  only then: Stage E (frontier on ≥2 ecology axes with PH-REV and PH-5 frozen) — still no HPC
```

Estimated cost: enumeration of `Gen_12` over ≤ 10 primitives with canonicalization is ≤ 10^7
composites per column; a laptop-scale exhaustive run. If a column's enumeration exceeds 10^8 at
`n_max = 12` the run stops and reports `CANNOT_CHECK_ENUMERATION_BUDGET` for that column rather than
sampling.
