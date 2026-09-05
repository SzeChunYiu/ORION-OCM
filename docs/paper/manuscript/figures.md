# Figure plan for main.md (draft V1, 2026-09-05)

No plot was executed. Each figure follows the nature-figure contract: one-sentence conclusion, evidence chain per panel, archetype, backend to be chosen by the operator (Python or R, not yet chosen; the recipes are backend-neutral), and an export contract (vector PDF plus SVG, editable text, source-data CSV written by the same script from the receipt-bound JSON). Every panel is generated from a receipt-bound file; no value is typed by hand. Scripts are to live in tools/paper/ (not yet present in the worktree).

Colour policy: one neutral family for parents, one signal family for the machine, one accent for the template floor and the reference arm; the reference arm is always drawn in a hatched or outlined style and labelled REFERENCE in the panel, never in the same style as a decision arm.

## Figure 1. Programme map: milestones to terminals

Conclusion: thirteen receipts form one chain, and their terminals are a mixed table, not a run of wins.

Data: docs/OCM_PROGRAMME_TERMINALS_V1.md (table rows M0–M12 and the post-roadmap additions); each docs/provenance/M*_RECEIPT_V1.json `terminal` field; `bound_files` of each receipt for the chain edges (each receipt binds the previous receipt).

Fields: milestone id, terminal string, terminal class (GREEN / MIXED / PARENT_SUFFICIENT / CANNOT_CHECK / RESIDUAL_SUPPORTED), binding edges (receipt N binds receipt N−1 by hash).

Recipe: a left-to-right chain of thirteen nodes (archetype: schematic-led composite). Node fill by terminal class (five classes). Below each node, the one-line content from Table 1. Edges are the hash bindings; V3 and the reference receipt hang off M12 as two side nodes. Source-data CSV: milestone, terminal, class, bound_previous_receipt.

## Figure 2. KnowledgeSpace semantics (schematic)

Conclusion: liveness composes exactly; revocation reopens exactly the changed cone; authority never rises.

Data: docs/spec/KSO_WARRANT_V1.md §3–§5 (definitions); V2:KSO_THREE_VALUED_WARRANT_AND_REOPENING_V1.md §3 witness (REOPEN = {a}, RECHECK = {b, c, d, e}, UNAFFECTED = {x, y, z}); V2 batch 1 §T1 (authority meet).

Fields: the Kleene truth tables for ∧ and ∨ on {LIVE, UNKNOWN, DEAD}; the eight-atom reopening witness with its three sets; a two-input authority meet example with commit = 0.

Recipe: three panels. (a) the interval ⟦L, U⟧ as a band between two antichains with the three liveness regions marked for one revocation set; (b) the eight-atom witness graph with REOPEN, RECHECK and UNAFFECTED coloured, drawn from the checker's fixture; (c) the authority lattice with two inputs and their meet, commit coordinate shown as the bottom. Schematic; no measured values. Source data: the witness adjacency and interval lists as CSV.

## Figure 3. M7 protected comparison: paired outcomes, ablations, terminals

Conclusion: one family carries the inferential residual; the ablations are equivalent on that family; every external family is undetermined by coverage.

Data: docs/provenance/M7_RECEIPT_V1.json.

Fields: `deterministic_results.terminal_table.<RQ>.<arm>.{ocm, other, n, difference, ci_90, test_verdict, terminal}` for RQ1_conversations (arms: matched_parent, template, ocm-no_clarification, ocm-no_revocation, ocm-last_turn_memory), RQ1_factual, RQ3_* (five steps), RQ5_honest_unknown, RQ6_negative_transfer; `deterministic_results.external_families.{BLiMP.covered, BLiMP.pairs, UD_EWT.interpreted, UD_EWT.sentences}`; `deterministic_results.information_budget`.

Recipe (quantitative grid): (a) hero panel, a dot-and-interval plot of the paired rate difference with its 90% interval for every (family, arm) pair, families on the y axis, the δ = 0.05 margin as two vertical rules, points coloured by test_verdict (RESIDUAL_A / EQUIVALENT / INCONCLUSIVE), families with n < 40 shaded as descriptive; (b) success counts as paired bars (OCM vs arm) per family with n printed; (c) external coverage as two bars at 0 of 6,000 and 0 of 800 with the coverage fraction printed. Source data: one CSV row per (family, arm).

## Figure 4. M9 transfer matrix and acquisition cost

Conclusion: success does not discriminate; acquisition cost does; the matrix refuses what should be refused.

Data: docs/provenance/M9_RECEIPT_V1.json.

Fields: `deterministic_results.summary.<arm>.{success, mean_later_domain_acquisition_cost, later_routes}` for the seven arms; `deterministic_results.transfer_matrix.cells.<T0..T13>.{expected, result}`; `deterministic_results.transfer_precision`.

Recipe (asymmetric mixed-modality): (a) hero panel, later-domain acquisition cost per arm as horizontal bars (7, 7, 12, 12, 12, 12, 6) with the route label at the bar end and the unvalidated arm hatched and labelled "not matched"; (b) the 14-cell matrix as a single-column tile strip, each tile coloured by outcome class (TRANSFER / ADAPTER_REQUIRED / REFUSE_TRANSFER / REFINE_REQUIRED / LEARN_NEW) with a tick where result equals expected; (c) success 54/54 for every arm as a small table inset, to make the point that it is flat. Source data: two CSVs (arms; cells).

## Figure 5. M11 self-reorganisation benchmark

Conclusion: the self-model diagnoses, repairs, preserves and rolls back in every planted fault; the parents solve two and one.

Data: docs/provenance/M11_RECEIPT_V1.json.

Fields: `deterministic_results.scenarios[*].{scenario, true_layer, diagnosed, proposal_class, target_before, target_after, preservation_before, preservation_after, rollback_exact, architecture_alarm, broad_rewrite.refused}`; `deterministic_results.parents[*].{scenario, parameter_search.solves, reflection_retry.solves, parameter_search.target, reflection_retry.target}`; `deterministic_results.historical_replay_summary`.

Recipe (quantitative grid): (a) hero panel, an S0–S7 by outcome tile grid with rows = scenarios and columns = diagnosis correct, minimum class, target restored, preserved, rollback exact, broad rewrite refused; tiles filled for the machine, with the two parents as two extra column groups showing solves; (b) target before/after as paired 0/6 → 6/6 arrows per scenario; (c) the recorded replay as a bar of 18 rows split into 10 local and 8 escalated-with-witness, with the label "governance audit only". Source data: scenarios CSV; parents CSV.

## Figure 6. M12 V3 eight-lifetime paired vectors and the V2 tier matrix

Conclusion: ten families win in all eight lifetimes, six tie, and the one family whose differences vary across lifetimes is the conversations family.

Data: docs/provenance/M12_PAIRED_RECEIPT_V1.json; docs/provenance/M12_RECEIPT_V1.json.

Fields: `deterministic_results.v3.tests.<family>.{diffs[0..7], ocm_mean, parent_mean, positive, p_two_sided, verdict}` (16 families); `deterministic_results.v3.scores.{ocm, whole_system_parent}[lifetime][family]`; `deterministic_results.v2.tiers.*.{holds, holds_descriptive, inferential}`; `deterministic_results.v2.claims.<family>.{n, ocm, parent, terminal}`.

Recipe (quantitative grid): (a) hero panel, per family a strip of eight points (the eight lifetime differences OCM − parent), families ordered by verdict then by mean difference, with the zero line, points jittered only where identical differences would overprint (annotate "identical in all 8" where the eight values coincide, which is the collapsed-one-coin exposure named in the text); verdict label and p at the right margin; (b) per-lifetime score vectors as two small heat strips (machine, parent) with families as columns and lifetimes as rows; (c) the V2 tier matrix as a six-row table-figure (tier, holds, basis) with the single inferential family marked. Source data: tests CSV (family, lifetime, diff); scores CSV.

## Figure 7. Reference arm beside the decision arms

Conclusion: the reference answers every out-of-scope question and learns the nonce lessons unevenly; it is drawn as a reference, not a comparator.

Data: docs/provenance/M12_REFERENCE_RECEIPT_V1.json; research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json; docs/provenance/M12_RECEIPT_V1.json (v2 summary O1); docs/provenance/M12_PAIRED_RECEIPT_V1.json (v3 scores).

Fields: reference receipt `deterministic_results.{summary.factual_in_scope, summary.honest_unknown, summary.negative_transfer, post_deployment.*, always_attempts}`; V3 reference `lifetimes[*].{summary.*, post_deployment.*, always_attempts, resources.calls}`; V2 receipt `v2.summary.{ocm, whole_system_parent}.O1.{A_factual, A_honest_unknown, A_negative_transfer, A_post_deployment}`; paired receipt `v3.scores`.

Recipe (asymmetric mixed-modality): (a) hero panel, grouped bars for the phase-A families (factual, honest unknown, negative transfer, lessons acquired, reuse, retained, revoked-stops, relearned) with three arms, the reference bar hatched and outlined and the panel title carrying the word REFERENCE; (b) the eight per-stream acquisition counts of the reference (6, 6, 4, 2, 1, 1, 3, 1 of 6) as a dot strip against the machine's 6 of 6 in every stream; (c) the "answered where unknown was licensed" count as a single annotated bar (20 of 20 for the reference; 0 for the machine; 3 for the parent in V2). Source data: one CSV per panel.

## Figure 8. Self-application ledger timeline

Conclusion: the machine's own discipline caught defects in its builders throughout the build, and the ones that mattered for the evaluation were custody and design findings, not mechanism changes.

Data: docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md (rows S1–S36); src/ocm/selfmodel/intake.py (INTAKES, EXPORTS).

Fields: per row: id, stage (milestone), outcome token, J-level (where recorded), whether the fix was a mechanism change, whether the row is a theory intake (S10, S20, S21, S28, S34, S35) and the defect count it carries (2, 1, 1, 1, 6, 5).

Recipe (schematic-led composite): a horizontal timeline ordered by milestone (M0 to M12 V3) with one marker per row; marker shape by outcome class (obstruction witnessed / gap / defect found / custody gap / design finding); theory-intake rows drawn as stacked markers with their defect count; the rows that relabelled a study (S22–S24, S27, S31–S33, S36) connected by a bracket to the study they relabelled. Source data: ledger CSV parsed from the markdown table (id, stage, outcome, j_level, intake_batch, defect_count).

## Supplementary figure S1. Acquisition regimes (M5)

Conclusion: information channel, not learner, decides what is acquired.

Data: docs/provenance/M5_RECEIPT_V1.json. Fields: `deterministic_results.acquisition_eval.regimes.<E>.{protected.exact, held_out.exact, information.*}`; `regimes.E4_curricula.<curriculum>.curve[*].{step, exact}`; `retention_after_E1`.

Recipe: (a) protected exact per regime as bars with the information supplied printed under each bar; (b) the four curriculum curves as step lines from 22 to their final value; (c) retention as three bars (new gain 93/112, old loss 0/22, unrelated change 0/22).

## Supplementary figure S2. Organisation study (M8)

Conclusion: parents already halve navigation work where the world is hierarchical; nothing learned beats them at this scale.

Data: docs/provenance/M8_RECEIPT_V1.json. Fields: `deterministic_results.worlds.<family>.<arm>.{navigation_work, exact_regions, task_success, macro_live_over_dead_children}`; `deterministic_results.language_stream.<arm>.{navigation_work, task_success}`.

Recipe: (a) a families × arms heat map of navigation work with exact_regions printed in each cell; (b) the language-stream arms as bars of work with success printed; the all-zero macro-liveness cells stated in the caption.
