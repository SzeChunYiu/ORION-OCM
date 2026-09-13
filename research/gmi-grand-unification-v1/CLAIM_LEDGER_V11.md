# Grand GMI Claim Ledger V11 — end-to-end family derivation traces

Status date: 2026-09-12. Additive to V1–V10 and to the independently merged Morphology/Family Selection theorems.

| ID | Claim | Status | Scope |
|---|---|---|---|
| GG60 | For a finite registered GMI problem with exact response semantics, finite exact candidate realizations/families, exact resource profiles and finite developmental reachability, the full chain from semantic quotient through cut/transformation requirements to selected family/property is decidable by finite exact enumeration. | SYNTHESIS THEOREM + EXACT TRACES | finite registered scope |

## Exact end-to-end traces

1. **Neural-selected selector task.** Four exact pre-query semantic states; two-bit temporal cut; fixed routing max `6/8`, dynamic routing `8/8`; registered reachable profiles `N_route=(2,4,2)`, `P_mux=(5,4,3)`, `T_lookup=(7,8,4)` leave the neural realization as the unique Pareto point.
2. **Non-neural running-parity controller.** Two exact semantic states; one-bit temporal cut; four exact XOR state/input transition cells; registered profiles `P_fsm=(1,1,1)`, `N_recur=(4,2,3)`, `T_transition=(3,2,2)` leave the program/FSM as the unique Pareto point.
3. **Hybrid product problem.** Selector region locally favors neural `(1,2)` over program `(5,5)` while exact-controller region favors program `(1,2)` over neural `(5,5)`; additive factorization makes neural+program `(2,4)` strictly dominate all three alternatives.
4. **Substrate inversion.** The same protected semantics select neural on one declared resource model and program on another, proving that family identity is a morphology/resource consequence rather than semantic essence.

Aggregate terminal:

`GRAND_GMI_END_TO_END_DERIVATION_TRACES_ALL_GREEN`.

## Interpretation

These traces establish that Grand GMI can derive neural, non-neural and hybrid family verdicts without privileging any family in the primitive theory, provided the physical/resource/reachability facts needed for the selection theorem are declared or measured.

They do not convert synthetic resource profiles into claims about present hardware. Replacing those profiles by independently measured real profiles is the empirical next step.