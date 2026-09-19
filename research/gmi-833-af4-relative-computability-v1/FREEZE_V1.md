# AF4 pre-implementation freeze — relative computability and non-terminal oracle frontier

Status: **FROZEN BEFORE EXECUTOR / RESULT / RECONCILIATION JUDGMENTS**

Issue authority: #833 AF addendum comment `5693269426`, section AF4.

Base `main`: `ed736cd332eabfc8d60965e53fce8881627bbdc0`.

This tranche targets **AF4 only**. AF5+ remains open.

## Expert lanes

1. Computability theory: oracle Turing machines, Turing degrees, diagonal halting and jump.
2. Resource/provenance accounting: oracle identity, imported power, query/access cost, finite-advice distinction.
3. Proof theory/self-reference: incompleteness and Gödel-machine claims relative to explicit proof systems/axioms.
4. Hostile review: reject universal-halting, physical-hypercomputation, free-oracle and incompleteness-escape promotions.

Parent mathematics remains parent-owned. Executable evidence may validate registrations, finite corollary tables, provenance/resources and hostiles; it must not be presented as an independent proof of the Turing-jump or incompleteness theorems.

## Frozen repository parents

- `research/gmi-833-af-barrier-context-v1/GMI_BARRIER_PARENT_LEDGER_V1.json` blob `8089a47975ae6ca0489c5198b6a56c14da8d9b65`.
- `research/gmi-833-af-barrier-context-v1/FORMALIZATION_V1.md` blob `de2f2552bb6d5787317921f9c42c82dab2df1952`.
- `research/heritable-search-transformation-v1/HST_THEOREM_REGISTRY_V1.json` blob `5b94d66a8d8d2196a518fd7ac8d1da83663e42a4`.
- `research/heritable-search-transformation-v1/FREEZE_HST_V1.json` blob `8723baf57ac16878edb4dfff45bd7decfa15b6be`.

External strongest-parent anchors:

- SEP, **Recursive Functions**, Proposition 3.7: for every oracle `A`, `A'` is c.e. in `A` but not computable in `A`; therefore `deg_T(A) < deg_T(A')`. Finite iteration yields a strict chain. `https://plato.stanford.edu/entries/recursive-functions/`.
- SEP, **Gödel's Incompleteness Theorems** / Proof Theory: incompleteness is relative to the stated consistent/effectively axiomatized sufficiently strong formal system; changing the system changes the proof relation rather than escaping the theorem class.
- Schmidhuber, **Goedel Machines**, arXiv `cs/0309048`: self-rewrite optimality is conditional on a proof found inside the encoded axiom/proof-search framework and on the relevant claim being provable there.

## Standard-oracle model

Register

`S[A] = (ORACLE_TM, oracle=A, access_contract, provenance, raw_resource_contract)`

and at this scope only define

`Comp(S[A]) := deg_T(A)`.

This is not a universal scalar of computational power and is not a physical-substrate claim.

Let

`H(A)=K^A={n : phi_n^A(n) halts}`

and `A' := H(A)`. Define `Jump(S[A]) := S[A']`.

Oracle/advice channels are explicit in `Pi`. Infinite oracle sets receive no fabricated finite information-bit count. Receipts record oracle identity/jump level, `ORACLE_ADVICE_OR_TOOL` provenance, direct-query count, registered access charge, and finite advice bits only when the advice object is actually finite.

## Parent theorem and AF4 corollary

### AF4-P1 — Turing jump [PARENT_OWNED]

For every set `A` in the standard oracle-Turing model: `A'` is c.e. in `A`, `A'` is not computable in `A`, hence `deg_T(A) < deg_T(A')`.

### AF4-C1 — non-terminal effective frontier [parent corollary]

For finite jump levels `S_n=S[A^(n)]`, every fixed registered level has a strictly stronger next level:

`Comp(S_n) < Comp(S_(n+1))`.

Allowed terminal:

`NO_TERMINAL_EFFECTIVE_FRONTIER_AT_REGISTERED_ORACLE_MODEL_SCOPE`.

This does not quantify over all possible physics, arbitrary transfinite models, or resource-bounded utility.

## Capability-envelope microscope

For each level `n`, define `Q_n` as membership in `A^(n+1)=H(A^(n))`.

Parent-backed reading:

- `S_n` cannot decide `Q_n` by a total effective procedure relative to `A^(n)`.
- `S_(n+1)` has `A^(n+1)` as declared oracle, so a direct membership query decides `Q_n` with one oracle query.
- `S_(n+1)` still cannot decide `Q_(n+1)`.

The executable census freezes levels `n=0..5` only as a theorem-derived registry/corollary table, never as an exhaustive computation of halting sets.

Each adjacent displacement records source status `UNDECIDABLE_RELATIVE_TO_S`, target `DECIDABLE`, changed axes `S,Pi,R`, provenance `ORACLE_ADVICE_OR_TOOL`, target oracle identity, one direct oracle query, unit registered query charge, `finite_advice_bits=null`, and nearest residual `Q_(n+1)` undecidable relative to the target substrate. Classification: `RELATIVIZATION + ORACLE_OR_ADVICE + SUBSTRATE_EXPANSION`.

The unit query charge is only a frozen microscope coordinate, not a physical energy/runtime theorem.

## Universal-halting hostile

For `A=emptyset`, base `S_0` cannot decide ordinary diagonal halting `Q_0`; `S_1=S[K]` can decide `Q_0` by direct oracle query; `S_1` cannot decide its own relative halting `Q_1=K^K`.

`HALTING_PROBLEM_SOLVED_UNIVERSALLY` must fail closed. Correct reading: base halting is displaced by imported oracle power and the relative barrier remains.

## Gödel-machine / proof-system audit

Register

`ProofContext=(formal_system_id, axioms_id, proof_rules_id, utility_theorem, consistency_or_soundness_assumptions, proof_search_contract)`.

Rules:

- stronger axioms/proof system are a changed `S/Pi` context, not an incompleteness escape;
- proof-system and axioms remain provenance-bearing inputs;
- `UNPROVABLE_IN_T` is not `FALSE` or `UNPROVABLE_IN_ALL_SYSTEMS`;
- no Gödel-machine result licenses `UNIVERSAL_SELF_IMPROVEMENT_PROVED`;
- missing proof context returns `CANNOT_AUDIT_PROOF_SYSTEM`.

A finite syntactic toy may show proof-context dependence only; it is never evidence for Gödel's theorem itself.

## Frozen hostiles

The post-freeze suite must reject at least:

1. `HALTING_PROBLEM_SOLVED_UNIVERSALLY` after adding only the base halting oracle;
2. missing nearest oracle-relative residual barrier;
3. oracle-used capability gain with missing `ORACLE_ADVICE_OR_TOOL` provenance;
4. oracle access with omitted query/resource charge;
5. fabricated finite `oracle_information_bits` for an infinite oracle set;
6. non-strict adjacent jump level in the parent-derived chain;
7. physical-hypercomputation promotion from a formal oracle model;
8. `GODEL_INCOMPLETENESS_ESCAPED` after changing axioms/formal system;
9. Gödel-machine claim missing proof-system/axiom identity;
10. treating `UNPROVABLE_IN_T` as `FALSE`;
11. claiming the executable finite level table independently proves the jump theorem;
12. parent/source/pin drift.

## Deliverables

Post-freeze: `FORMALIZATION_V1.md`, `PARENT_LEDGER_V1.json`, stdlib executor, independent oracle, hostile tests, deterministic results, `OPEN_GAPS_V1.json`, AF4 reconciliation registry/checker (check only, no auto mutation), README, dedicated CI.

## Claim ceiling

`GMI_AF4_RELATIVE_COMPUTABILITY_AND_NONTERMINAL_ORACLE_FRONTIER_AT_REGISTERED_STANDARD_ORACLE_MODEL_SCOPE`.

Forbidden promotions:

`HALTING_PROBLEM_SOLVED_UNIVERSALLY`, `ALL_UNDECIDABILITY_BARRIERS_REMOVED`, `PHYSICAL_HYPERCOMPUTATION_ESTABLISHED`, `PHYSICAL_CHURCH_TURING_FALSIFIED`, `NO_FINAL_COMPUTABILITY_BARRIER_IN_ALL_PHYSICS`, `GODEL_INCOMPLETENESS_ESCAPED`, `GODEL_MACHINE_PROVES_UNIVERSAL_SELF_IMPROVEMENT`, `ORACLE_POWER_FREE`, `COMPLETE_GMI`.
