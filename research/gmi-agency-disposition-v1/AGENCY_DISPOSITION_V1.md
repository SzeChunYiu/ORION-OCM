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
| robust deterministic policy value under action-dependent kernels | **CA-1** pair-state sufficiency; **CA-4** information replaceable by control; **CA-5** path-dependent resources must be state variables | induction on remaining horizon gives equality of all future feasible policy trees and values |
| finite stochastic planning and discounted control | [AG2/AG3](../gmi-formal-derivation-v1/AGENCY-RESOURCES.md) | known controlled kernels on finite sufficient observed state/action registers; finite horizon, or bounded stationary rewards and discount strictly between zero and one |
| finite stochastic metalevel value | [RES2](../gmi-formal-derivation-v1/AGENCY-RESOURCES.md) | finite reachable metalevel register, known computation kernels, bounded stop values and finite computation horizon; best currently implementable stop action |
| unsound shortcuts refused | **CA-3** world-support-only recursion is unsound | pinned counterexample |
| controller state and cost of acting | **BCR-1–4**, `BOUNDED_CONTROLLER_RESOURCE_THEOREM_V1.md` | exact product verification, bounded synthesis, zero retained-action bits with positive controller/program cost, feedback revival |
| planning at the obligation's resolution | `PLANNING_SEMANTIC_RESOLUTION_THEOREM_V1.md` | plan-prefix resolution law; verifier-search and transition-congruent DP regimes |
| decision value, regret and selector slack | `DECISION_FINITE_SCORES_AUDIT_V1.md` | corrected finite-score regime; regret `2 delta + alpha`; witness showing that omitting selector slack wrongly claims `2` |
| preference is not derivable from process law | `MASTER_CLOSURE_LEDGER_V3.md` §5 item 6; [AG1](../gmi-formal-derivation-v1/AGENCY-RESOURCES.md) | "physics/process law does not choose arbitrary social, moral or preference orderings; viability supplies an endogenous special case, not a universal value theorem" |

CA §9 already performs its own parent subtraction against POMDP belief states,
controlled/active sensing and Decision Region Determination, and labels itself
"parent-assisted synthesis, not a priority claim".

## Residue

1. **Beyond the declared stochastic registers.** CA itself is deterministic
   and robust/zero-error; its §8 directs the finite known-kernel extension to
   PCA-1–4. AG2/AG3 and RES2 additionally cover the finite stochastic objectives
   listed above. Generic infinite POMDP belief spaces, unbounded metalevel
   registers and learned dynamics outside the separate FMT/ARC sampling
   contracts remain outside those results; finite stochastic metalevel value
   is therefore not an undifferentiated open item.
2. **Preference elicitation.** AG1 proves that a preferred objective does not
   follow from environmental facts. A constructive elicitation result would
   need an admitted preference-response/access model and its identification
   assumptions; viability does not supply arbitrary preference orderings.
3. **Implementing charged deliberation.** The linked
   [VOC-1–6](../gmi-value-of-computation-v1/VALUE_OF_COMPUTATION_THEOREM_V1.md)
   applies only under each result's explicit policy, termination, verification,
   access and cost premises. This link is not an unconditional closure
   certificate. RES3 still requires a concrete implementation to charge model
   acquisition, policy evaluation, storage and tool calls, or label the
   recurrence as an oracle bound. Neither naming a recurrence nor a finite
   stopping theorem discharges all physical implementation obligations.

## Why this is filed as a record

The ledger's own authority line says status words carry no authority and the
linked proofs do. Row 9 should therefore be read against CA-1–5, BCR-1–4, the
planning-resolution theorem, AG1–3/RES1–3 and the decision-score audit — not against a new
document restating them.

The original PR572 disposition is retained byte-exact with its
[source bindings](raw/pr572-e2a89dcc/SOURCE_BINDINGS_V1.json). No new theorem or run is added.
