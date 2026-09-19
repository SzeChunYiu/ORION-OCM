# AF4 formalization V1 — relative computability and a non-terminal effective frontier

Authority: issue #833, AF addendum comment `5693269426`, section AF4.
Pre-implementation freeze: `FREEZE_V1.md`, commit `3d37a3813ff13085ad5e0e2a7f6374b37bfd2158`.

Claim ceiling:

`GMI_AF4_RELATIVE_COMPUTABILITY_AND_NONTERMINAL_ORACLE_FRONTIER_AT_REGISTERED_STANDARD_ORACLE_MODEL_SCOPE`

AF4 imports classical relative computability; it does not rename it as a GMI discovery.

## Registered standard-oracle substrate

At this scope only,

`S[A]=(ORACLE_TM, oracle=A, access_contract, provenance, raw_resource_contract)`

and

`Comp(S[A]) := deg_T(A)`.

This is a Turing-degree descriptor for a standard oracle model, not a universal scalar intelligence/runtime/energy measure and not a theorem about arbitrary physical systems.

Let `H(A)=K^A={n : phi_n^A(n) halts}`, let `A'=H(A)`, and define `Jump(S[A])=S[A']`.

Oracle access is explicit provenance/resource. Receipts record oracle identity, jump level, `ORACLE_ADVICE_OR_TOOL`, query count and access charge. Infinite oracles are not assigned fabricated finite information-bit counts; finite advice is a separate object.

## Parent theorem: Turing jump

SEP *Recursive Functions*, Proposition 3.7 summarizes the standard parent result: for every set `A`, `A'` is c.e. in `A` but not computable in `A`, hence `deg_T(A) < deg_T(A')`. Finite iteration yields a strict jump chain.

The theorem is machine-labeled `PARENT_OWNED_NOT_PROVED_BY_EXECUTOR`. The executable level table is downstream bookkeeping, not proof evidence.

## AF4-C1 — scoped non-terminal frontier

With `S_n=S[A^(n)]`, the imported theorem gives

`Comp(S_n) < Comp(S_(n+1))`

for every registered finite level. Allowed terminal:

`NO_TERMINAL_EFFECTIVE_FRONTIER_AT_REGISTERED_ORACLE_MODEL_SCOPE`.

This does not quantify over all possible physics, arbitrary transfinite models, or resource-bounded utility.

## Capability-envelope displacement

For each `n`, define `Q_n` as membership in `A^(n+1)=H(A^(n))`. Parent-backed reading:

- `S_n` cannot decide `Q_n` by a total effective procedure relative to `A^(n)`;
- `S_(n+1)` exposes `A^(n+1)` as oracle, so one direct membership query decides `Q_n`;
- `S_(n+1)` still cannot decide `Q_(n+1)`.

The executable census instantiates `n=0..5`, charges one oracle query at unit registered access cost, and preserves the next residual barrier. Unit query charge is a formal microscope coordinate, not wall time or physical energy.

Every displacement records exactly:

```text
S_n -> S_(n+1)
Pi gains ORACLE_ADVICE_OR_TOOL
R gains one charged oracle query
Q_n: UNDECIDABLE_RELATIVE_TO_S -> DECIDABLE
residual: Q_(n+1) remains UNDECIDABLE_RELATIVE_TO_S_(n+1)
```

This is barrier displacement/relativization, not contradiction.

## Hostile: ordinary halting is not universally solved

At `n=0`, `Q_0` is ordinary diagonal halting. A `Q_0` oracle lets `S_1` decide membership in `Q_0`; but `S_1` has its own relativized diagonal halting `Q_1`, which remains noncomputable relative to `S_1` by the parent theorem. Therefore `HALTING_PROBLEM_SOLVED_UNIVERSALLY` is forbidden.

## Proof-system and Gödel-machine audit

A proof-guided self-change claim must register

`ProofContext=(formal_system_id, axioms_id, proof_rules_id, utility_theorem, consistency_or_soundness_assumptions, proof_search_contract)`.

Gödel incompleteness is system-relative under its assumptions. Strengthening/changing axioms changes the formal context; it does not escape the theorem class. Therefore:

- `UNPROVABLE_IN_T` is not `FALSE`;
- `UNPROVABLE_IN_T` is not `UNPROVABLE_IN_ALL_FORMAL_SYSTEMS`;
- changed axioms return `PROOF_SYSTEM_CONTEXT_CHANGED_NOT_INCOMPLETENESS_ESCAPE`;
- missing formal-system/axiom identity returns `CANNOT_AUDIT_PROOF_SYSTEM`.

The Gödel-machine parent is conditional: its proof searcher seeks a proof that a rewrite improves the registered utility according to encoded axioms; its optimality wording is conditional on the target theorem being provable in that setting. AF4 therefore allows only proof-system-relative self-improvement wording.

The tiny `T0={P}` versus `T1={P,R}` fixture demonstrates derivability dependence on axioms only; it is labeled `TOY_CONTEXT_DEPENDENCE_NOT_GODEL_PROOF`.

## Evidence classes

- Strict jump and incompleteness mathematics are parent-owned.
- AF4-C1 is a scoped corollary after registering `Comp(S[A])=deg_T(A)`.
- The executor validates the finite level registry, displacement schema, query/resource/provenance accounting, forbidden terminals and proof-context discipline.
- The independent oracle re-derives the triangular decidability table without importing the main module.
- Neither executable is a halting oracle and neither computes a noncomputable set.

## Falsifiers and open boundary

AF4 fails its contract if an accepted receipt omits oracle provenance/query charge, reports a finite information-bit count for an infinite oracle, erases the next relative barrier, calls a formal oracle model physical hypercomputation, treats changed axioms as incompleteness escape, equates unprovability with falsity, or labels the finite table as proof of the jump theorem.

AF5+ remains open.
