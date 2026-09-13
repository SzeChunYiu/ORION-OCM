# Grand GMI Claim Ledger — Family Frontier Phase V1

Status date: 2026-09-12; corrected 2026-09-13. Additive to the Grand-GMI claim
ledgers. Correction authority: `FAMILY_PHASE_SOUNDNESS_CORRECTION_V1.md`.

| ID | Claim | Status | Scope |
|---|---|---|---|
| GFP1 | A certified feasible family-A witness whose upper resource vector strictly Pareto-dominates a proved lower resource bound for every family-B realization robustly excludes family B. | THEOREM | registered resource coordinates and evidence bounds |
| GFP2 | Under a declared scalar objective on well-formed intervals, `U_A(s) < min_B L_B(s)` uniquely identifies the least-infimum family A; an attained winner additionally needs attainment, and overlapping optimum-cost intervals do not identify a family without additional evidence. | THEOREM | scalar registered selection functional; `L_F <= U_F` validated |
| GFP2a | Malformed certified intervals must be rejected rather than compared: two families registered as `[5,0]` both satisfy the unvalidated robustness test. | INPUT-VALIDATION REQUIREMENT | exact rational/integer bounds |
| GFP3 | SUPERSEDED. The predecessor crossover condition `U_A >= L_B` and/or `U_B >= L_A` is vacuous: it holds at every robust-B parameter of any well-formed register. | WITHDRAWN AS VACUOUS | replaced by GFP3a |
| GFP3a | On a parameter path where the registered intervals are well formed and `L_B - U_A` is continuous, a robust-A to robust-B transition contains a parameter at which neither A nor B is robust. | THEOREM | connected domain; pairwise conclusion only |
| GFP3b | On a discrete scale register a robust transition can occur with no abstaining registered parameter, and no interpolation between adjacent parameters is licensed. | COUNTEREXAMPLE / NO-GO | discrete phase registers |
| GFP3c | A pairwise crossover parameter need not be undecided for the full phase diagram: a third family can be robust there. | COUNTEREXAMPLE | three or more registered families |
| GFP4 | Response semantics alone cannot universally select neural over non-neural realization when both exist and resource ordering is not fixed. | THEOREM / NO-GO | response-equivalent realizations |
| GFP5 | For an obligation with a valid regional decomposition and declared additive resource law, a mixed-family composition inherits the sum of regional upper bounds plus bridge cost. | THEOREM | declared decomposition/additivity |
| GFP5a | A pure-family lower bound is a sum of registered regional *lower* bounds; a registered upper bound may never be a term of it, and an unregistered regional lower bound admits only non-negativity. | THEOREM / BOUND-DIRECTION REQUIREMENT | registered regional bounds |
| GFP5b | A regional sum lower bounds only realizations that factor through the registered regions with additively charged costs; excluding a pure family requires a decomposition-closed candidate class or a whole-obligation proof. | THEOREM / HYPOTHESIS REQUIREMENT | declared candidate class |
| GFP6 | Hybrid morphology is derived only when the selected set is nonempty and every selected morphology contains the required mixed-family decomposition; one constructive hybrid witness is insufficient, and any regional-sum exclusion inherits GFP5a and GFP5b. | DERIVATION CRITERION | registered candidate universe |

| GFP7 | A finite nonempty feasible construction register that weakly dominates every admissible profile supplies a nonempty exact frontier; properties still require all equal-profile realization fibers. | THEOREM | MSC-2; universal coverage premise must be proved |
| GFP8 | A witnessed upper cost below all rival lower bounds excludes rivals; U_A-L_A certifies witness regret, while an exact optimum needs attainment. | THEOREM | MSC-3; finite real bounds, nonempty evidence set |

`CONSTRUCTIVE_SELECTION_ATTAINMENT_BRIDGE_V1.md` supplies GFP7–8 and the
nonvacuity/attainment correction to GFP2/6.

## Exact witness aggregate

- task scales checked: `8`;
- family phases witnessed: `NON_NEURAL`, `NEURAL`, `HYBRID`, and `UNDECIDED_FROM_CURRENT_EVIDENCE`;
- well-formed interval pairs enumerated for the vacuity finding: `225`, of which `35` are robust-B and all satisfy the withdrawn condition;
- integer configurations enumerated for validation: `625`, of which `100` yield more than one unvalidated winner and all `100` contain a malformed interval; well-formed multi-winner configurations: `0`;
- exact crossover root on the connected witness path: `3/10`, where the pair abstains and a third family `[1/2,1]` is nonetheless robust;
- predecessor hybrid arithmetic `4+8=12` and `9+3=12` summed upper bounds into lower bounds; the sound unregistered-bound values are `8` and `9` against a hybrid upper bound of `8`, so the predecessor neural exclusion fails and the non-neural exclusion survives;
- repaired registration (`L_N(R_s)=4`, `L_X(R_x)=3`) restores pure-family bounds `12` and `12` and the hybrid verdict, over decomposition-closed candidates only;
- a monolithic pure-neural realization of cost `6` defeats the hybrid verdict when decomposition closure is dropped;
- opposite legal resource orderings reverse neural/non-neural selection for response-equivalent realizations;
- no empirical hardware cost is claimed.

Terminals: `GRAND_GMI_FAMILY_FRONTIER_PHASE_TRANCHE_ALL_GREEN` for the sector
checker and `GRAND_GMI_FAMILY_PHASE_SOUNDNESS_CORRECTION_GREEN_AT_FINITE_SCOPE`
for the correction checker. Neither supplies `L_F(s)` or `U_F(s)` for a real
substrate.
