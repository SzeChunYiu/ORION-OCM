# -*- coding: utf-8 -*-
import json, os, bisect
SNAP = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "RECONCILIATION_SPEC_V1.json")
CIDS = {"AG": 5693520829, "AH": 5693590252, "AJ": 5693954852, "AF": 5693269426}
bodies = {}
for name, cid in CIDS.items():
    bodies[cid] = json.load(open(os.path.join(SNAP, "COMMENT_SNAPSHOT_%d.json" % cid),
                                encoding="utf-8"))["body"]

def line_of(cid, n):
    return bodies[cid].split("\n")[n-1]

def anchor_of(cid, n):
    lines = bodies[cid].split("\n")
    heads = [(i+1, l) for i, l in enumerate(lines) if l.startswith("### ")]
    hn = [h[0] for h in heads]
    return heads[bisect.bisect_right(hn, n) - 1][1]

AG, AH, AJ, AF = CIDS["AG"], CIDS["AH"], CIDS["AJ"], CIDS["AF"]

def rep(cid, n, token, suffix, cites, bucket):
    old = line_of(cid, n)
    assert old.startswith("- [ ] "), old
    stem = old[len("- [ ] "):]
    return {"comment_id": cid, "anchor": anchor_of(cid, n), "old": old,
            "new": "- [x] " + stem + " — ✅ " + suffix,
            "row_meaning_token": token, "bucket": bucket, "cites": cites,
            "status": "EARNED"}

AG5PKG = "gmi-833-ag5-extension-lowering-v1"
AH4PKG = "gmi-833-ah4-organization-ladder-v1"
AH7PKG = "gmi-833-ah7-data-varied-choice-v1"
AJ9PKG = "gmi-833-aj9-holdout-source-audit-v1"

replacements = [
 rep(AG, 101, "G0_INSTRUCTION_STATUS_ADJUDICATED_RELATIVE_TO_THE_AJ5_ROLE_BASIS_AT_REGISTERED_FINITE_SCOPE",
   "`" + AG5PKG + "` AG5X-1/AG5X-2: all 21 registered instructions are adjudicated **relative to the AJ5 lower role basis at the registered finite scope** — 7 derived operations, 12 macros, 1 semantic convenience (`HALT`, crosswalked from AJ5's own `PRESENTATION_ONLY`) and 1 resource-priced implementation primitive (`NEIGHBOR_UPDATE`, whose lowering costs 24/28/33/39 charged roles at 0/1/2/3 edges), with 0 generators relative to that basis, 0 lowering mismatches and 0 resource mismatches over 54,366 registered checks, and every status read off a published measurement rather than assigned.",
   [{"package": AG5PKG, "quoted_fields": {"ledger_size": 21, "generator_count": 0,
      "total_registered_checks": 54366,
      "total_lowering_mismatches": 0, "total_resource_mismatches": 0,
      "resource_priced.0": "NEIGHBOR_UPDATE",
      "graph.neighbor_update_max_roles_by_edge_count.0": 24,
      "graph.neighbor_update_max_roles_by_edge_count.3": 39}}], "EXACT-FORMAL"),
 rep(AG, 186, "STOCHASTIC_UPDATE_LOWERED_TO_EXACT_WEIGHT_PAIRS_OVER_THE_AJ5_ROLE_BASIS",
   "`" + AG5PKG + "` AG5X-1: `UPDATE`, `COMPOSE`, `IDENTITY_KERNEL`, `DETERMINISTIC_KERNEL` and `TRANSPORT` are rebuilt from distributions and kernels as normalized pairs of naturals over the AJ5 role basis — no rational, matrix or distribution object is admitted as a role — and match the merged parent on all 1,296 one-step pairs, all 46,656 composition pairs, 1,296 kernel transports, 36 distribution transports and 27 deterministic maps with 0 mismatches; an audit of all 17 lowering functions finds 0 architecture-family names, and 0 of 200 randomized weight-cell permutations reproduce the semantics.",
   [{"package": AG5PKG, "quoted_fields": {"stochastic.update_checks": 1296,
      "stochastic.update_mismatches": 0, "stochastic.compose_checks": 46656,
      "stochastic.compose_mismatches": 0, "stochastic.transport_kernel_checks": 1296,
      "stochastic.deterministic_checks": 27, "nulls.stochastic.hits": 0,
      "nulls.stochastic.draws": 200, "family_name_audit.functions_scanned": 17}}], "EXACT-FORMAL"),
 rep(AG, 187, "COMMUNICATION_AND_TOOL_CALLS_LOWERED_TO_TYPED_INTERACTION_COMPOSITION",
   "`" + AG5PKG + "` AG5X-1/AG5X-4: `SEND` and `RECV` lower to AJ5's own `APPEND_OUTPUT` and `NEXT_INPUT` on per-channel streams and `CALL` to one request event out and one response event in, matching the merged parent on all 324 send, 648 receive, 324 apply-received, 6 call, 486 apply-external and 648 two-message queue cases with 0 semantic and 0 resource mismatches; the provenance tag changes 0 of 486 well-formed transitions while refusing 24 of 24 forged values that the untagged path admits, so it is a discipline gate and not a state effect.",
   [{"package": AG5PKG, "quoted_fields": {"channels.send_checks": 324,
      "channels.recv_checks": 648, "channels.apply_external_checks": 486,
      "channels.fifo_checks": 648, "channels.call_checks": 6,
      "channels.resource_mismatches": 0,
      "external_data_tag.inert_checks": 486, "external_data_tag.inert_differences": 0,
      "external_data_tag.forged_rejected_with_tag_gate": 24,
      "external_data_tag.forged_accepted_without_tag_gate": 24}}], "EXACT-FORMAL"),
 rep(AG, 188, "GOVERNED_SELF_CHANGE_LOWERED_TO_STATE_TRANSFORM_PLUS_EXTERNAL_ADMISSION_RELATION",
   "`" + AG5PKG + "` AG5X-3/AG5X-6: `PROPOSE`, `VERIFY` and `ADOPT` lower to a store, an external-stream call and a five-guard chain over the AJ5 roles, with 0 terminal and 0 resource mismatches on all 27 registered candidates; the **plus** clause is shown necessary rather than assumed — holding the internal triple and the proposal fixed and varying only the receipt's authority and signature gives 27 of 27 differing terminals and 9 of 27 differing active states — and over 145 registered attempts exactly 1 of the 31 proper guard subsets reproduces the parent, the replay guard being provably not isolable at this scope because adoption strictly increments the version.",
   [{"package": AG5PKG, "quoted_fields": {"self_change.candidate_checks": 27,
      "self_change.terminal_mismatches": 0, "self_change.resource_mismatches": 0,
      "adopt_externality.terminal_witness_pairs": 27,
      "adopt_externality.state_change_witness_pairs": 9,
      "nulls.adopt_guard_subsets_extended_universe.cases": 145,
      "nulls.adopt_guard_subsets_extended_universe.reproducing_subsets": 1,
      "nulls.adopt_guard_subsets_extended_universe.proper_subsets": 31,
      "nulls.adopt_guard_subsets_extended_universe.prediction_matches": True}}], "EXACT-FORMAL"),
 rep(AH, 118, "PER_TRANSITION_INVARIANTS_DEFINED_AND_MEASURED_AT_REGISTERED_FINITE_SCOPE",
   "`" + AH4PKG + "` AH4L-1: eight named invariants, one per transition, each exactly computable and each with passing and failing systems present, over a 260-system space rebuilt here whose 148 behavioural classes and `{1: 144, 29: 4}` size histogram reproduce the merged AJ4 numbers — `I1` 234/26, `I2` 144/116, `I3` 15,680 irreducible of 67,600 composites, `I4` 4 witness sites against 0 for its control, `I5` growth 1 against 0, `I6` and `I7` separating with flat controls, `I8` description delta −7 and search delta −3 at expressive delta 0.",
   [{"package": AH4PKG, "quoted_fields": {"base_organizations": 260,
      "operational_classes": 148, "i1_pass": 234, "i1_fail": 26, "i2_pass": 144,
      "composites_total": 67600, "composites_irreducible": 15680,
      "i4_witness_triples": 4, "i4_negative_witness_triples": 0, "i5_growth": 1,
      "i5_negative_growth": 0, "i8.description_delta": -7,
      "i8.search_distance_delta": -3, "i8.expressive_delta": 0}}], "NEW-SCIENCE"),
 rep(AH, 119, "NEAREST_NEGATIVE_SYSTEMS_CONSTRUCTED_WITH_MEASURED_MINIMUM_EDIT_DISTANCE",
   "`" + AH4PKG + "` AH4L-5: every transition has a system that satisfies the invariants up to `L_i` and fails the step, at the exhaustive minimum Hamming distance in the declared description encoding — 2, 1, 1, 7, 1, 1, 1, 1 for `I1`–`I8` — with flipped positions and resulting descriptions published; the first four are genuine minima searched over 8-, 8-, 16- and 16-bit description spaces, while the four witness-family transitions have single-bit descriptions, so for those a distance of 1 is the only other element rather than a measurement.",
   [{"package": AH4PKG, "quoted_fields": {
      "nearest_negatives.I1_MOTIF_REUSE.distance": 2,
      "nearest_negatives.I2_HISTORY_DEPENDENCE.distance": 1,
      "nearest_negatives.I3_IRREDUCIBLE_COMPOSITION.distance": 1,
      "nearest_negatives.I4_EXPERIENCE_CONDITIONED_UPDATE.distance": 7,
      "nearest_negatives.I8_NEW_EFFECTIVE_UNIT.distance": 1}}], "NEW-SCIENCE"),
 rep(AH, 120, "LEVEL_STRUCTURE_ADJUDICATED_WITH_ONE_INTERMEDIATE_LAYER_AND_A_NON_CUMULATIVE_BASE",
   "`" + AH4PKG + "` AH4L-2/AH4L-3/AH4L-4: only 2 of the 8 transitions separate on visible behaviour (`L1->L2` and `L2->L3`) — `L3->L4` is exhibited to collapse, its adaptive witness reproduced on all 62 registered words by a plain transducer over `(state, experience)`; `L5->L6` and `L6->L7` separate only while the external value is held outside the visible input; `L0->L1` splits 2 of the 148 behavioural classes and `L7->L8` is stated on description and search geometry because a merged parent proved macro libraries add no expressive power — an intermediate layer between `L1` and `L2` **is** required and has 112 members that hold a state cell whose distinction never reaches the word behaviour, against 144 that pass both clauses and 4 that hold no cell with the fourth combination empty, and the base is not cumulative: 14 systems pass `I2` while failing `I1`.",
   [{"package": AH4PKG, "quoted_fields": {
      "i2_intermediate_layer_population": 112,
      "i2_clause_counts.both": 144, "i2_clause_counts.cell_only": 112,
      "i2_clause_counts.neither": 4, "i2_clause_counts.behaviour_only": 0,
      "non_cumulative_base_systems": 14,
      "i1_classes_split_by_description": 2,
      "i4_collapses_under_absorption": True,
      "verdict_counts.SEPARATING_ON_VISIBLE_BEHAVIOUR": 2,
      "verdict_counts.SEPARATING_ONLY_ON_DESCRIPTION": 4,
      "verdict_counts.SEPARATING_UNDER_DECLARED_EXTERNAL_BOUNDARY": 2,
      "verdicts.I2_HISTORY_DEPENDENCE": "SEPARATING_ON_VISIBLE_BEHAVIOUR",
      "verdicts.I3_IRREDUCIBLE_COMPOSITION": "SEPARATING_ON_VISIBLE_BEHAVIOUR",
      "verdicts.I4_EXPERIENCE_CONDITIONED_UPDATE": "SEPARATING_ONLY_ON_DESCRIPTION"}}], "NEW-SCIENCE"),
 rep(AH, 121, "LEVEL_MEMBERSHIP_PROHIBITION_IS_LIVE_AND_TRIPPED",
   "`" + AH4PKG + "` AH4L-6: the prohibition is live rather than vacuous — across the 260 systems and five registered tasks scored as exact rationals over 14 protected words there are 1,914 ordered pairs in which the higher-level system is strictly dominated in capability, the first being `M101` at level 2 with `(0, 3/7, 3/14, 3/14, 0)` against the cell-free `S002` at level 0 with `(0, 1, 3/14, 3/14, 0)` — and the checker refuses an intelligence claim lacking capability **and** development evidence, admits it when both are present, and leaves a plain level statement alone, with hostiles planting a checker that always refuses and one that never does.",
   [{"package": AH4PKG, "quoted_fields": {"level_capability_inversions": 1914,
      "prohibition.trip": "REFUSED__LEVEL_MEMBERSHIP_IS_NOT_INTELLIGENCE",
      "prohibition.admit_with_evidence": "ADMITTED_WITH_EVIDENCE",
      "prohibition.non_intelligence_claim": "NOT_AN_INTELLIGENCE_CLAIM",
      "level_capability_inversion_example.higher_level_system": "M101",
      "level_capability_inversion_example.lower_level_system": "S002"}}], "DISCIPLINE-CONTRACT"),
 rep(AH, 179, "DATA_AXIS_MOVES_THE_PREFERRED_FORM_WITH_SPACE_REQUIREMENT_AND_PRICING_FIXED",
   "`" + AH7PKG + "` AH7D-1/AH7D-2: with one 260-system possibility space, one four-coordinate raw price carrying no scalarization, one requirement and one horizon held fixed under a single published fingerprint identical across every dataset, 20 registered datasets give 7 distinct preferred sets and 162 of 190 pairs disjoint answers; with the delay-by-one behaviour itself fixed and only the observed words varying the preferred system moves `S000` → `M051` → `M043`, and running parity moves `S001` → `M066` → `M064`, while the answer is invariant to pair order (0 failures) and narrowing is monotone (0 of 10).",
   [{"package": AH7PKG, "quoted_fields": {"possibility_space_size": 260,
      "registered_datasets": 20, "distinct_chosen_sets": 7,
      "disjoint_chosen_set_pairs": 162, "disjoint_pairs_sharing_one_target": 10,
      "fixed_input_fingerprint_identical_across_datasets": True,
      "scalarization_used": False, "order_invariance_failures": 0,
      "monotone_narrowing_failures": 0, "monotone_narrowing_checks": 10,
      "per_dataset.DELAY1|LEN1.chosen.0": "S000",
      "per_dataset.DELAY1|UPTO2.chosen.0": "M051",
      "per_dataset.DELAY1|ALL.chosen.0": "M043",
      "per_dataset.PARITY|LEN1.chosen.0": "S001",
      "per_dataset.PARITY|UPTO2.chosen.0": "M066",
      "per_dataset.PARITY|ALL.chosen.0": "M064"}}], "NEW-SCIENCE"),
 rep(AJ, 159, "HOLDOUT_BLIND_ARTIFACTS_CARRY_NO_FORBIDDEN_INPUT_AT_REGISTERED_SCOPE",
   "`" + AJ9PKG + "` AJ9A-1/AJ9A-2: all 21 blind artifacts of the seven holdouts `aj9b`–`aj9h` carry 0 violations against the eight forbidden classes quoted verbatim from the frozen holdout contract, with the whole search vocabulary derived from the registry pinned at blob `6b9ac309` (11 identifiers, 11 names, 27 name tokens, 35 fingerprint clauses, 33 exclusion clauses, 24 observation clauses, 25 parent anchors); the absence is searched rather than empty — the same scanner returns 237 hits on the 20 post-hoc artifacts where family vocabulary is permitted, and 8 of 8 planted positives are detected, one per forbidden class, a validation that caught a real recall defect before this row was claimed.",
   [{"package": AJ9PKG, "quoted_fields": {"violations": 0, "holdouts_audited": 7,
      "blind_files_scanned": 21, "posthoc_files_scanned": 20,
      "control_family_hits_in_posthoc": 237,
      "planted_positives_detected": 8, "planted_positives_declared": 8,
      "vocabulary.blob_matches_pin": True,
      "vocabulary.family_ids": 11, "vocabulary.fingerprint_clauses": 35}}], "HARNESS"),
]

def nc(cid, n, reason, bucket):
    old = line_of(cid, n)
    assert old.startswith("- [ ] "), old
    return {"comment_id": cid, "anchor": anchor_of(cid, n), "old": old,
            "reason": reason, "bucket": bucket}

not_closed = [
 nc(AG, 23, "No merged package exhibits a system whose EXTERNAL description uses a grammar while its MECHANISM contains no grammar object. AJ4's 260 organizations are candidates but no package registers the claim. Named next tranche: gmi-833-ag0-no-internal-grammar-v1.", "NEW-SCIENCE"),
 nc(AG, 124, "Witnesses exist for 3 of the 4 named strengths (syntactic renaming, compiler equivalence with overhead, model equivalence) but no package DEFINES the strength lattice or orders it. Closing on three of four would narrow the row's stated meaning. Named next tranche: gmi-833-ag3-presentation-equivalence-v1.", "EXACT-FORMAL"),
 nc(AG, 152, "The row asks for exact translations among the applicable specializations of the six families A-F, which is 15 pairs. Exact translations exist for 2 (AJ12's two formalization styles, AJ5's P-FUN/P-REL). 13 remain; a partial close would narrow the row.", "NEW-SCIENCE"),
 nc(AG, 195, "Only the register/counter basis exists on main. A combinatory/rewrite basis and a cellular/local basis must be built at bounded executable scope. This is the largest genuine gap in AG/AH and the structural map names it as the one that must not be rushed; this tranche deliberately did not rush it.", "NEW-SCIENCE"),
 nc(AG, 196, "Requires row 195 first: with one basis on main there is nothing to compare compilation overhead, description bias, reachability geometry or developmental search burden against.", "NEW-SCIENCE"),
 nc(AG, 197, "Requires rows 195 and 196. This is the decisive cross-basis invariance test for the whole AG programme; the structural map states it must not be rushed and no partial evidence would license it.", "NEW-SCIENCE"),
 nc(AG, 199, "The terminal UNIVERSAL_COMPUTATION_ONLY appears only as a gap-kill condition in research/machine-intelligence-morphogenesis-v1/GAP_REGISTER_V3.json. No #833 package registers it as an admissible outcome with a checker that can AWARD it on a real configuration and WITHHOLD it where a predictive residual remains. Both branches must be exercised, as the AH4 prohibition checker in this tranche does for its own contract.", "DISCIPLINE-CONTRACT"),
 nc(AG, 213, "Six candidate boundaries are named. Adaptation, history-sensitivity and reusable-operator acquisition have partial coverage; metareasoning and endogenous experiment/search choice have none. Closing on partial coverage would narrow the row's stated meaning.", "NEW-SCIENCE"),
 nc(AG, 236, "Independent formal-logic/foundations review of the stopping point. EXTERNAL-GATE: no model-only route exists. Left open deliberately - a hurried model proxy is exactly the POST_HOC_SUSPECT class this corpus has already had to correct once. Explicitly out of scope for this tranche.", "EXTERNAL-GATE"),
 nc(AH, 66, "AJ1's parent comparison covers 6 of the 7 named candidate descriptions; rewrite/reaction systems (term rewriting, artificial chemistry reaction networks) are absent from the comparison ledger. The residual is exactly one formalism and its exact finite translations; a package adding it would close this row.", "EXACT-FORMAL"),
 nc(AH, 98, "Requires showing memory, routing, search, probabilistic state, symbolic rewriting, learning laws and self-modification EMERGING rather than appearing as primitive macros. AJ9's blind recovery is adjacent but recovers families rather than the emergence of each mechanism from a neutral base. The AG5 tranche in this PR adjudicates those operators as derived relative to the AJ5 role basis, which is a lowering result, not an emergence result, and does not close this row.", "NEW-SCIENCE"),
 nc(AJ, 258, "AJ15 is one end-to-end flagship experiment, not seven independent microscopes; no aj15 package exists. The bounded-universe enumeration exists in AJ4/AJ11 and the family holdouts in AJ9, but no package runs them as a single registered end-to-end falsification.", "NEW-SCIENCE"),
 nc(AJ, 259, "Part of the single AJ15 flagship experiment; AJ9's per-family holdouts are adjacent but are seven separate runs rather than one end-to-end experiment with a family hidden from theory construction as well as from evaluation labels.", "NEW-SCIENCE"),
 nc(AJ, 260, "Part of the single AJ15 flagship experiment. AJ9a registers NOT_RECOVERED_AT_SCOPE as an honest failure terminal, but AJ15's row asks for it inside the flagship run, which does not exist.", "NEW-SCIENCE"),
 nc(AJ, 261, "Part of the single AJ15 flagship experiment. No registered ecology/resource regime predicts the held-out family NOT to appear; AJ9 receipts record predicted_selected: NOT_CLAIMED throughout.", "NEW-SCIENCE"),
 nc(AJ, 262, "Part of the single AJ15 flagship experiment, and conditional on its bounded success. Larger non-enumerable scales with independent search implementations are not reachable from anything merged.", "NEW-SCIENCE"),
 nc(AJ, 263, "Part of the single AJ15 flagship experiment. AJ9 recovers known families and AJ10 maintains an UNKNOWN channel, but no single registered theory is shown to permit both outputs in one run.", "NEW-SCIENCE"),
 nc(AJ, 264, "Part of the single AJ15 flagship experiment; a falsifier contract is vacuous until the experiment it would falsify exists.", "DISCIPLINE-CONTRACT"),
 nc(AF, 52, "Closing this row requires rewriting the #833-L row in the ISSUE BODY, which this tranche is forbidden to edit. The merged gmi-833-af-barrier-context-v1/OPEN_GAPS_V1.json registers exactly this as AF1_L_ROW_UPGRADE and defers it for the same reason. It is not closable by any research package.", "DISCIPLINE-CONTRACT"),
 nc(AF, 150, "Requires reconstructing the sharpened NFL premises exactly, including permutation-closure and the measure-theoretic conditions. No merged #833 package states them; AF6 has no package at all.", "NEW-SCIENCE"),
 nc(AF, 151, "Requires deriving what ecology information or prior is needed for a search advantage. Depends on the reconstructed premises of the preceding row.", "NEW-SCIENCE"),
 nc(AF, 152, "Requires importing Blum speedup correctly, including that some computable functions have no single asymptotically best program. No merged package carries it.", "NEW-SCIENCE"),
 nc(AF, 153, "Requires worst-case versus average, smoothed and parameterized complexity as distinct barrier surfaces. No merged package separates them.", "NEW-SCIENCE"),
 nc(AF, 155, "Requires information-augmentation cases where traces, annotations or active queries move the barrier. No merged package registers them.", "NEW-SCIENCE"),
 nc(AF, 156, "Requires a parent map from interactive learnability to DEC, information ratio and sample complexity. No merged package carries that map.", "NEW-SCIENCE"),
 nc(AF, 164, "Requires an empirical substrate contract S_phys with precision, stability, readout and repeatability. The merged AF package registers EMPIRICAL_PHYSICAL_COMPUTATION as a HIGH-severity open gap and explicitly states AF7 must supply it; AF7 has no package.", "NEW-SCIENCE"),
 nc(AF, 165, "Requires auditing major hypercomputation, analog and oracle proposals at their exact stated premises. No merged package performs that audit.", "NEW-SCIENCE"),
 nc(AF, 166, "Requires the careful treatment of arbitrary-real-weight analog models. No merged package treats them.", "NEW-SCIENCE"),
 nc(AF, 167, "Requires precision and noise hostiles showing when apparent super-Turing power disappears. Depends on the substrate contract of row 164.", "NEW-SCIENCE"),
 nc(AF, 169, "Conditional on a future empirical event - a physical substrate exceeding the current bound. Closable only as a registered conditional protocol, never as a result, and no package registers such a protocol.", "DISCIPLINE-CONTRACT"),
 nc(AF, 179, "Requires an exact finite GMI_INTELLIGENCE_ATLAS_B with machine states, transitions and the declared budget. AJ11 supplies a bounded atlas at its own scope but not the AF8 atlas B; AF8 has no package.", "NEW-SCIENCE"),
 nc(AF, 183, "Requires quantifying how the atlas and frontier expand as budget and information access grow. Depends on the atlas of row 179.", "NEW-SCIENCE"),
 nc(AF, 184, "Requires testing whether the finite atlases converge or stabilize on a useful quotient. Depends on the atlas of row 179.", "NEW-SCIENCE"),
]

af1_line = None
for i, l in enumerate(bodies[AF].split("\n"), 1):
    if l.startswith("- [x] Construct exact finite `G0` microscopes"):
        af1_line = (i, l)
assert af1_line, "AF1 G0 row not found"

spec = {
 "schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1",
 "issue": 833,
 "repository": "SzeChunYiu/ORION-OCM",
 "source_main": "5e57d4292266bccf435136e1f7d72caa32e920a0",
 "branch": "research/833-sec-agaj",
 "comments": sorted(CIDS.values()),
 "packages": [AG5PKG, AH4PKG, AH7PKG, AJ9PKG, "gmi-833-af1-g0-row-determination-v1"],
 "claim_ceilings": {
   AG5PKG: "AG5_G0_EXTENSION_OPERATORS_LOWERED_AND_STATUS_ADJUDICATED_AT_REGISTERED_FINITE_SCOPE",
   AH4PKG: "AH4_ORGANIZATION_LADDER_INVARIANTS_AND_LEVEL_STRUCTURE_AT_REGISTERED_FINITE_SCOPE",
   AH7PKG: "AH7_DATA_AXIS_MOVES_THE_PREFERRED_FORM_WITH_SPACE_REQUIREMENT_AND_PRICING_HELD_FIXED",
   AJ9PKG: "AJ9_HOLDOUT_BLIND_SOURCE_AUDITED_AGAINST_THE_FROZEN_FORBIDDEN_INPUT_LIST"},
 "forbidden_promotions": sorted(set([
   "G0_EXTENSIONS_ARE_THE_OPERATIONAL_BOTTOM","UNIQUE_LOWEST_EXTENSION_BASIS",
   "ALL_G0_EXTENSIONS_ENUMERATED","STOCHASTIC_ARCHITECTURE_DERIVED",
   "BAYESIAN_INFERENCE_DERIVED","GNN_DERIVED","TOOL_USE_INTELLIGENCE_DERIVED",
   "EMERGENT_COMMUNICATION","RECURSIVE_SELF_IMPROVEMENT_PROVED",
   "AUTONOMOUS_SELF_AUTHORITY","VERIFIER_INFALLIBLE",
   "PERIODIC_TABLE_OF_MI_COMPLETE","LEVEL_MEMBERSHIP_IS_INTELLIGENCE",
   "LADDER_IS_TOTAL_ORDER","ALL_ORGANIZATION_LEVELS_ENUMERATED",
   "HIGHER_LEVEL_IMPLIES_HIGHER_CAPABILITY","UNBOUNDED_LEVEL_HIERARCHY_PROVED",
   "DATA_CREATES_THE_POSSIBILITY_SPACE","MORE_DATA_IS_ALWAYS_BETTER",
   "DATA_AXIS_DOMINATES_REQUIREMENTS_OR_PRICING","UNIQUE_PREFERRED_FORM_PER_DATASET",
   "LEARNING_THEORY_DERIVED","ALL_HOLDOUTS_PROVEN_BLIND","BLIND_SEARCH_IS_UNBIASED",
   "NO_LEAKAGE_OF_ANY_KIND","RECOVERY_IS_CONFIRMED_BY_THIS_AUDIT","COMPLETE_GMI"])),
 "do_not_edit": ("The orchestrator performs every issue write. This tranche edited no comment "
                 "and no issue body, and un-checked nothing."),
 "replacements": replacements,
 "not_closed": not_closed,
 "checked_but_unsupported": [{
   "comment_id": AF,
   "anchor": anchor_of(AF, af1_line[0]),
   "current_line": af1_line[1],
   "verdict": "CHECKED_BUT_UNSUPPORTED",
   "finding": ("The only checked row in the AF1 block with no evidence suffix. The check "
               "survives on the comment and nothing on main supports it."),
   "evidence": [
     "The merged gmi-833-af-barrier-context-v1 lists this row in its auto-reconciled tasks; deferred_tasks holds only the #833-L upgrade.",
     "OPEN_GAPS_V1.json lists 'AF1 two exact crossed developmental microscopes' as locally_closed.",
     "The merged package contains no G0 machinery: searched with two control patterns that had to match and did (Gamma in 8 files, 'def ' in 6); G0-reg-v1, G0_RESULT and check_g0_micro appear nowhere; a case-insensitive search for g0 returns exactly one line, the row text itself.",
     "The committed af1 receipt carries the same-current direction only, over the Boolean functions C0/C1/ID/NOT rather than G0 programs; 'convers' appears nowhere but in the row text.",
     "PR #969 repairs exactly this and is OPEN, not merged - verified twice, with gh pr view and the pulls API. Any description of it as merged is a false premise.",
     "Independently of #969, Current is defined on main as the zero-development slice of Gamma, so Gamma_A = Gamma_B forces Current_A = Current_B: the literal converse is unsatisfiable, not merely unevidenced."],
   "package": "gmi-833-af1-g0-row-determination-v1",
   "recommended_action": ("Merge PR #969, which repairs the evidence and moves the row to "
                          "deferred_tasks. Do not check any row of this shape until the "
                          "authoritative wording is repaired."),
   "this_tranche_did_not_uncheck_it": True}],
}
open(OUT, "w", encoding="utf-8").write(json.dumps(spec, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
print("spec written:", len(replacements), "replacements,", len(not_closed), "not_closed")
