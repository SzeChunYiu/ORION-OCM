# Agency and planning: disposition of ledger item 9

Status: **DISPOSITION RECORD, NOT A NEW THEOREM**
Date: 2026-09-13

Ledger row 9 asks to "separate truth/evidence from preference; define policy
value under action-dependent kernels and derive finite Bellman recursion as a
specialization." Most of that is **already proved on main**. Writing a new
"agency theorem" over it would be a renamed parent, which the basis-acceptance
gate kills as `PARENT_FORMALISM_SUFFICIENT`. This record names the discharging
proofs and the residue instead.

## What already discharges row 9

| Row 9 clause | Discharged by | Evidence |
|---|---|---|
| finite Bellman recursion as a specialization | **CA-2**, `CONTROLLED_ACQUISITION_INFORMATION_STATE_THEOREM_V1.md` | exact robust Bellman recursion, compared against an independent explicit history-tree recursion over all `5^8 = 390,625` two-world/two-state/two-test kernels at horizon two, **zero mismatches** |
| policy value under action-dependent kernels | **CA-1** pair-state sufficiency; **CA-4** information replaceable by control; **CA-5** path-dependent resources must be state variables | induction on remaining horizon gives equality of all future feasible policy trees and values |
| unsound shortcuts refused | **CA-3** world-support-only recursion is unsound | pinned counterexample |
| controller state and cost of acting | **BCR-1–4**, `BOUNDED_CONTROLLER_RESOURCE_THEOREM_V1.md` | exact product verification, bounded synthesis, zero retained-action bits with positive controller/program cost, feedback revival |
| planning at the obligation's resolution | `PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md` | plan-prefix resolution law; verifier-search and transition-congruent DP regimes |
| decision value, regret and selector slack | `DECISION_FINITE_SCORES_AUDIT_V1.md` | corrected finite-score regime; regret `2 delta + alpha`; witness showing that omitting selector slack wrongly claims `2` |
| preference is not derivable from process law | `MASTER_CLOSURE_LEDGER_V3.md` §6 | "physics/process law does not choose arbitrary social, moral or preference orderings; viability supplies an endogenous special case, not a universal value theorem" |

CA §9 already performs its own parent subtraction against POMDP belief states,
controlled/active sensing and Decision Region Determination, and labels itself
"parent-assisted synthesis, not a priority claim".

## Residue

1. **Stochastic metalevel value.** CA is finite deterministic and robust/zero-error.
   Its §8 states that under stochastic transitions a support set is generally
   insufficient for expected-risk optimization, and defers to PCA-1–4 for the
   finite known-kernel case. Generic infinite POMDP beliefs remain outside scope.
2. **Preference elicitation.** The boundary is stated (no universal value
   theorem); what is absent is a constructive account of where an admitted
   preference order comes from when viability does not supply one.
3. **Charged deliberation inside the policy.** Closed separately by
   [VOC-1–6](../gmi-value-of-computation-v1/VALUE_OF_COMPUTATION_THEOREM_V1.md),
   which supplies the termination and exactness certificates CA's action
   selection presupposes.

## Why this is filed as a record

The ledger's own authority line says status words carry no authority and the
linked proofs do. Row 9 should therefore be read against CA-1–5, BCR-1–4, the
planning-resolution theorem and the decision-score audit — not against a new
document restating them.
