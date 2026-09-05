# Figure plan for main.md (draft V3, 2026-09-05)

No plot was executed. Each figure follows the nature-figure contract: one-sentence conclusion, evidence chain per panel, archetype, backend to be chosen by the operator (Python or R, not yet chosen; the recipes are backend-neutral), and an export contract (vector PDF plus SVG, editable text, source-data CSV written by the same script from the receipt-bound JSON). Every panel is generated from a receipt-bound file; no value is typed by hand. Scripts are to live in tools/paper/ (only the claim-verification and word-count scripts exist there so far).

Display budget: the manuscript carries ten tables. A long-form venue can take eight main figures and two supplementary figures beside them; a six-display venue (Nature Machine Intelligence Article) needs Figures 1, 3, 6 and 7 as main displays, Tables 1, 8 and 9 folded into them, and the rest in Supplementary Information. The venue contract in reviews/venue_contract.md carries that decision.

Colour policy: one neutral family for parents, one signal family for the machine, one accent for the template floor and the reference arm; the reference arm is always drawn in a hatched or outlined style and labelled REFERENCE in the panel, never in the same style as a decision arm. Reopened cells (Figure 5, Figure 6 self-repair rows) are drawn with a dashed outline and a legend entry "reopened for protected re-evaluation (2026-09-05)".

## Figure 1. Programme map: milestones to terminals

Conclusion: thirteen receipts form one chain, their terminals are a mixed table, and two of them now carry a post-freeze revalidation label.

Data: docs/OCM_PROGRAMME_TERMINALS_V1.md (table rows M0–M12 and the post-roadmap additions); each docs/provenance/M*_RECEIPT_V1.json `terminal` field; `bound_files` of each receipt for the chain edges; docs/PROGRAMME_STATUS_RUNTIME_V4.md (on main) for the current M11 and M12 labels.

Fields: milestone id, terminal string, terminal class (GREEN / MIXED / PARENT_SUFFICIENT / CANNOT_CHECK / RESIDUAL_SUPPORTED), binding edges (receipt N binds receipt N−1 by hash), current-label flag for M11 and M12.

Recipe: a left-to-right chain of thirteen nodes (archetype: schematic-led composite). Node fill by terminal class (five classes); M11 and M12 carry a dashed second outline for the revalidation label. Below each node, the one-line content from Table 1. Edges are the hash bindings; V3, V4 and the reference receipt hang off M12 as side nodes. Source-data CSV: milestone, terminal, class, bound_previous_receipt, current_label.

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

## Figure 5. M11 self-reorganisation benchmark (historical cells, reopened)

Conclusion: the self-model diagnosed, repaired, preserved and rolled back in every planted fault and the parents solved two and one; the adoption binding of every cell was found defective after the freeze, so the panel reports a reopened result, not a renewed one.

Data: docs/provenance/M11_RECEIPT_V1.json; docs/RUNTIME_LIFECYCLE_REVALIDATION_V2.md (on main) for the reopened-cell table; research/ocm-m11/M11_SELF_EVAL_LIFECYCLE_V2.json (on main) for the engineering replay summary.

Fields: `deterministic_results.scenarios[*].{scenario, true_layer, diagnosed, proposal_class, target_before, target_after, preservation_before, preservation_after, rollback_exact, architecture_alarm, broad_rewrite.refused}`; `deterministic_results.parents[*].{scenario, parameter_search.solves, reflection_retry.solves}`; `deterministic_results.historical_replay_summary`; the revalidation table's missing-target column per cell.

Recipe (quantitative grid): (a) hero panel, an S0–S7 by outcome tile grid with rows = scenarios and columns = diagnosis correct, minimum class, target restored, preserved, rollback exact, broad rewrite refused; tiles filled for the machine, with the two parents as two extra column groups showing solves; every S1–S7 row carries the dashed reopened outline and its missing-target label (layer.D1 … layer.D2); (b) target before/after as paired 0/6 → 6/6 arrows per scenario; (c) the recorded replay as a bar of 18 rows split into 10 local and 8 escalated-with-witness, labelled "governance audit only"; (d) a small inset stating that the fresh engineering replay reproduced the descriptive summary and is not a protected result. Source data: scenarios CSV; parents CSV; reopened-cells CSV.

## Figure 6. M12 V4 and V3 eight-lifetime paired vectors and the V2 tier matrix

Conclusion: under the re-registered rule the primary family (conversations) rejects with differences that vary across streams, every secondary family rejects but collapses to one coin, and the earlier V3 record shows the same shape under its weaker rule.

Data: docs/provenance/M12_PAIRED_RECEIPT_V4.json (primary); docs/provenance/M12_PAIRED_RECEIPT_V1.json (V3); docs/provenance/M12_RECEIPT_V1.json (V2 tiers).

Fields: V4 `deterministic_results.v4.tests.<family>.{diffs[0..7], ocm_mean, parent_mean, positive, p_one_sided, role, alpha, collapsed_one_coin, verdict}` (16 families), `v4.secondary_rejections`, `v4.collapsed_one_coin_families`, `v4.decision`; V3 `deterministic_results.v3.tests.<family>.{diffs[0..7], p_two_sided, verdict}`; V2 `deterministic_results.v2.tiers.*.{holds, holds_descriptive, inferential}`.

Recipe (quantitative grid): (a) hero panel, V4: per family a strip of eight points (the eight lifetime differences OCM − parent), families grouped by role (primary, six secondaries, descriptive) and ordered by mean difference, zero line drawn, collapsed families marked with a flag glyph and the annotation "identical in all 8", the primary family drawn with its two distinct values (0.3704, 0.3889) visible; the G self-repair and E cross-domain transfer rows carry the dashed reopened / unmatched-cells outline; verdict, role and one-sided p at the right margin; (b) the same strip for V3 under its two-sided rule, to show the record the re-registration replaced, with the S37 caveat in the caption; (c) the V2 tier matrix as a six-row table-figure (tier, holds, basis) with the single inferential family marked. Source data: one CSV per study (study, family, lifetime, diff, role, collapsed).

## Figure 7. Reference arm beside the decision arms

Conclusion: the reference asserts an answer to almost every question the given facts do not settle, is mostly right in the world when it does (which the world-true half makes visible), and learns the nonce lessons unevenly; it is drawn as a reference, not a comparator.

Data: research/ocm-m12/M12_V4_REFERENCE_ARM_V1.json (primary); docs/provenance/M12_REFERENCE_RECEIPT_V1.json and research/ocm-m12/M12_V3_REFERENCE_ARM_V1.json (earlier suites); docs/M12_V4_PAIRED_LIFETIMES_REPORT.md §4 (OCM and parent V4 totals; the 472-question four-class denominator); docs/provenance/M7_RECEIPT_V1.json (the fresh V2-suite decision arms).

Fields: V4 reference `lifetimes[*].{summary.factual_in_scope, summary.honest_unknown, summary.negative_transfer, post_deployment.*, always_attempts, four_class.{licensed, unlicensed_true, unlicensed_false, wrong}, resources.calls}`; V3 reference the same minus `four_class`; V2 reference receipt `deterministic_results.{summary.*, post_deployment.*, always_attempts}`; M7 receipt `deterministic_results.summary.{ocm, matched_parent}`.

Recipe (asymmetric mixed-modality): (a) hero panel, the V4 four-class grading as one stacked bar per stream (licensed, unlicensed-true, unlicensed-false, wrong) with the eight-stream totals printed (233, 199, 38, 2 of 472; the one unverified-source question per stream is drawn as a separate grey segment so the 480 questions are all visible), beside a single bar for the machine (232 of 240 licensed unknowns) and the parent (136 of 240); the caption states that the summary grader counts 7 honest unknowns against the four-class grader's 3 and that the two graders disagree on 4 items in two streams; (b) grouped bars for the phase-A families on V4 (factual, honest unknown, negative transfer, lessons acquired, reuse, retained, revoked-stops, relearned) with three arms, the reference bar hatched and outlined and the panel title carrying the word REFERENCE; (c) per-stream lesson acquisition of the reference on V3 (6, 6, 4, 2, 1, 1, 3, 1 of 6) and V4 (1, 3, 0, 5, 3, 5, 4, 4 of 6) as two dot strips against the machine's 6 of 6 in every stream. Source data: one CSV per panel.

## Figure 8. Self-application ledger timeline

Conclusion: the machine's own discipline caught defects in its builders throughout the build, the ones that mattered for the evaluation were custody and design findings rather than mechanism changes, and the post-freeze adoption-binding defect is of the same kind.

Data: docs/self-application/OCM_SELF_APPLICATION_LEDGER_V1.md (rows S1–S38); src/ocm/selfmodel/intake.py on main (15 INTAKES, 2 EXPORTS); docs/RUNTIME_LIFECYCLE_REVALIDATION_V2.md (on main) for the post-ledger finding.

Fields: per row: id, stage (milestone), outcome token, J-level (where recorded), whether the fix was a mechanism change, whether the row is a theory intake (S10, S20, S21, S28, S34, S35, S37, S38) and the defect count it carries (2, 1, 1, 1, 6, 5, 1, 1); one unnumbered marker for the 2026-09-05 revalidation finding.

Recipe (schematic-led composite): a horizontal timeline ordered by milestone (M0 to M12 V4) with one marker per row; marker shape by outcome class (obstruction witnessed / gap / defect found / custody gap / design finding); theory-intake rows drawn as stacked markers with their defect count; the rows that relabelled a study (S22–S24, S27, S31–S33, S36, S37) connected by a bracket to the study they relabelled; the revalidation finding as a final hollow marker labelled "post-ledger, not a row". Source data: ledger CSV parsed from the markdown table (id, stage, outcome, j_level, intake_batch, defect_count).

## Supplementary figure S1. Acquisition regimes (M5)

Conclusion: information channel, not learner, decides what is acquired.

Data: docs/provenance/M5_RECEIPT_V1.json. Fields: `deterministic_results.acquisition_eval.regimes.<E>.{protected.exact, held_out.exact, information.*}`; `regimes.E4_curricula.<curriculum>.curve[*].{step, exact}`; `retention_after_E1`.

Recipe: (a) protected exact per regime as bars with the information supplied printed under each bar; (b) the four curriculum curves as step lines from 22 to their final value (held-out values are not measured for the curricula and the panel says so); (c) retention as three bars (new gain 93/112, old loss 0/22, unrelated change 0/22).

## Supplementary figure S2. Organisation study (M8)

Conclusion: parents already halve navigation work where the world is hierarchical; nothing learned beats them at the evaluated scale (oracle worlds of four regions of eight atoms; a 167-atom language stream).

Data: docs/provenance/M8_RECEIPT_V1.json. Fields: `deterministic_results.worlds.<family>.<arm>.{navigation_work, exact_regions, task_success, macro_live_over_dead_children}`; `deterministic_results.language_stream.<arm>.{navigation_work, task_success}`.

Recipe: (a) a families × arms heat map of navigation work with exact_regions printed in each cell; (b) the language-stream arms as bars of work with success printed; the all-zero macro-liveness cells stated in the caption. The 10⁵-atom scaling row belongs to the M2 runtime baseline and is not drawn here.
