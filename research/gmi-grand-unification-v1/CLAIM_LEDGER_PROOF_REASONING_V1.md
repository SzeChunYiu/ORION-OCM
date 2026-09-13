# Grand GMI Claim Ledger — Formal Reasoning / Proof Search V1

Status date: 2026-09-13. Additive to all earlier Grand-GMI ledgers.

| ID | Claim | Status | Scope |
|---|---|---|---|
| GG-P1 | Formal reasoning/theorem proving is an ordinary Grand-GMI proof process with partial-proof states, tactic actions, verifier observations and proof obligations. | THEOREM / REDUCTION | declared proof system |
| GG-P2 | The canonical exact proof state is the quotient by equality of all obligation-relevant future proof/verifier responses. | THEOREM + EXACT WITNESSES | finite proof process |
| GG-P3 | Dynamic programming/search on a right-congruent semantic proof quotient preserves exact values/actions. | THEOREM + EXACT DAG WITNESS | finite quotient-compatible proof graph |
| GG-P4 | Verification complexity and proof-search complexity are distinct; exact equality-verifier search needs up to `N-1` eliminations although checking a supplied certificate needs one call. | THEOREM + 46,233 EXACT QUERY-ORDER CHECKS | unique-proof black-box verifier |
| GG-P5 | Proof/lemma/tactic communication is an ordinary semantic cut and inherits cut lower bounds. | THEOREM | declared modular proof process |
| GG-P6 | Verifier acceptance does not imply theorem truth unless soundness is part of the declared process/evidence. | EXACT COUNTEREXAMPLE | unsound verifier |
| GG-P7 | Failure to find a proof inside an incomplete/bounded proof system is not a refutation. | BOUNDARY + EXACT WITNESS | bounded sound proof search |
| GG-P8 | Neural, symbolic, retrieval-augmented and hybrid theorem provers are realization families selected by the ordinary reachable resource frontier. | REDUCTION | same protected proof obligation |

Exact receipt: `GRAND_GMI_PROOF_REASONING_RECEIPT_V1.json`.

Aggregate terminal:

`GRAND_GMI_FORMAL_REASONING_PROOF_SEARCH_TRANCHE_ALL_GREEN`.
