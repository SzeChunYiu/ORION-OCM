# Grand GMI Claim Ledger — Morphology Phase Law Derivation V1

Status date: 2026-09-13. Additive to the Grand-GMI claim ledgers. Authority:
`MORPHOLOGY_PHASE_LAW_DERIVATION_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| PL1 | A family-conditioned lower bound is the value of the relaxed accounting program over the proved necessities and the structural family predicate alone. | DEFINITION | finite decidable allocation domain |
| PL2 | Under the accounting-soundness contract, every admitted machine satisfying the structural predicate has scalar cost at least the derived bound, including machines nobody has constructed. | THEOREM | registered necessities, predicate, accounting and scalar functional |
| PL2a | The accounting-soundness contract is load bearing: overcharging destroys the stated monotone transport guarantee and can produce a false bound. | COUNTEREXAMPLE | registered accounting map |
| PL3 | The relaxation can be strictly loose, so loose evidence can cause abstention; independently attained optimum ties are a different cause. These are not exhaustive. | THEOREM / SCOPE SEPARATION | relaxed programs |
| PL3b | If every compared family's derived bound is attained by a registered construction, the interval verdict equals the true-optimum verdict, so abstention is physical. | THEOREM | tight bounds only |
| PL4a | Registering a further valid necessity cannot lower a derived bound, so a robust exclusion is never lost by adding valid evidence. | THEOREM | valid necessities |
| PL4b | Weakening a structural predicate cannot raise a derived bound, so a robust verdict can be lost by enlarging the structure class. | THEOREM / NO-GO | structure-class enlargement |
| PL5 | Lower-bound data do not determine selected families in general: two sound finite worlds share the program but have opposite optimal families. Empty rival relaxation plus independently proved nonempty selection and coverage can still identify the surviving family. | THEOREM / SCOPED INSUFFICIENCY | identical relaxation data; positive exception needs existence and coverage |

## Exact witness aggregate

- allocation domain enumerated exhaustively: `4096`;
- derived bounds from proved necessities only: `L_NEURAL = 15`, `L_NON_NEURAL = 11`, over `135` and `150` feasible allocations;
- after registering the joint necessity `w1 + t1 >= 8`: `L_NEURAL = 18`, `L_NON_NEURAL = 14`, over `119` and `120` feasible allocations;
- a registered non-neural construction of cost `16` abstains against the relaxed bound `15` and robustly excludes the neural class against the refined bound `18`; the abstention was epistemic;
- tight intervals `[14,14]` for both families reproduce the true-optimum verdict `UNDECIDED_FROM_CURRENT_EVIDENCE`, so that abstention is physical;
- enlarging the neural predicate to heterogeneous kernels lowers the derived bound from `18` to `12` and withdraws the non-neural verdict;
- four registered machines with sound accounting each respect their derived bound; the overcharging map claims `18` while the actual machine costs `10`;
- two complete finite worlds with identical relaxed bounds have opposite true optimal families; their interval comparisons alone yield `NON_NEURAL` and `UNDECIDED_FROM_CURRENT_EVIDENCE`;
- empty rival relaxation plus a nonempty attained selection selects the surviving family; the same relaxed sets with no feasible machine abstain, and an uncovered competitor is refused;
- no real substrate bound is measured.

Terminal: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_SCOPE_REPAIRED_V2_GREEN`.
Corrected payload: `GRAND_GMI_MORPHOLOGY_PHASE_LAW_RECEIPT_V2.json`;
historical V1 payload bytes are preserved.
The layer derives lower bounds only. It supplies no `U_F`, no measurement, no
general selection guarantee from necessities alone, and no proof that the registered structure classes
cover the physically legal set.
