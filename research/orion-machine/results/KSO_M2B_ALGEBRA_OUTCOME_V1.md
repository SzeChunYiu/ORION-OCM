# KSO M2b — elementary algebra through the instruction channel: outcome record V1

Receipt: `KSO_M2B_ALGEBRA_RECEIPT_V1.json` (the **V2 run**; design freeze `KSO_M2B_DESIGN_V2.json`).
Source: `../domains/algebra/ALGEBRA_SOURCE_V1.json` (23 atoms, sha256 `af9e7ed6a98c…`).
**NO NOVELTY CLAIM.** Every produced root is `UNWARRANTED_PENDING_EXACT_CHECKER` until
`kso_exact_checker_sympy_v1` (guards lane, #300) confers EXACT_CHECKER.

## V1 run — `M2B_V1_GATING_DEFECT` (kept, not erased)

The first run used the 21-atom source (reconstruction archived as
`ALGEBRA_SOURCE_V1_SUPERSEDED_RECONSTRUCTED.json`, sha256 `712a33e4ec1c…`) with every constraint on
a target conjoined. Result: **exact 5/30, attribution FIRE on 25/30** — `proc:quadratic_formula`
never fired because the three mutually exclusive Δ-case constraints were conjoined (two of them are
always revoked for a query), and `proc:linear` fired on a = b = 0 (no b ≠ 0 constraint). The five
exact instances were LINEAR_DEGENERATE. **Discipline miss:** V1 was run without a pre-run freeze
(ledger entry in `../OCM_FAILURE_LEDGER.md`).

## Supersession V1 → V2 (changes made after seeing the V1 outcome, named as such)

1. CONSTRAINT rule: constraint atoms carrying a `case` field **disjoin** per target; non-case
   constraints conjoin; the gate lives in the target's label —
   applicability(T) = ⊗ preconditions ⊗ non-case constraints ⊗ (⊕ case constraints).
2. Two constraint atoms added: `con:a_zero` (case "a == 0", constrains `proc:linear`) and
   `con:b_nonzero` (constrains `proc:linear`).

V2 is frozen (`KSO_M2B_DESIGN_V2.json`, source/module/generator digests, instance ids) before its
receipt is cited.

## V2 run — `M2B_POPULATED_AND_SOLVED_ON_DEV`

```text
population       24 atoms / 60 typed hyperedges, 0 isolated; every atom through admit() with INSTRUCTION;
                 meter = 24 admissions; genome (S1, S2, S7, digest) held
G1 exact roots   30/30 vs the registered oracle (two implementations agreeing per instance)
G2 fired == applicable   30/30: RATIONAL_DISTINCT / DOUBLE_ROOT -> formula + square + factor;
                 IRRATIONAL_DISTINCT / COMPLEX_PAIR -> formula + square (factor gated by the Q rule);
                 LINEAR_DEGENERATE -> proc:linear; NO_EQUATION -> nothing (GAP_NOT_FOUND)
G4 planted       revoking con:a_nonzero blocks every quadratic procedure (CAUGHT)
G5 retraction    12/12 both directions on the algebra graph; renormalising parent differs on 11
parameters       alpha = 1/3 PRE_STUDY_PLACEHOLDER (KSO_PARAMETER_STUDY_V1)
```

What this establishes: knowledge enters only through the channel, constraint gating is a label
phenomenon (revocation for the query), the registered procedures compose the roots the oracle
holds, and a non-equation yields a gap rather than a guess. What it does not establish: warrant
(pending the checker), language (M5), any advantage over a parent (no comparator arm on this
domain yet — a direct SymPy `solve` is the ceiling control to register at the comparator step).
