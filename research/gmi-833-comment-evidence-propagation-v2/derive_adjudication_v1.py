# -*- coding: utf-8 -*-
"""Derive ADJUDICATION_V2.json (105 rows) from round 1's not_marked list plus
this round's re-adjudication. Keyed on the exact `old` string, never line number."""
import json, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
R1 = os.path.join(ROOT, "research", "gmi-833-comment-evidence-propagation-v1", "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
rows = json.load(io.open(R1, encoding="utf-8"))["not_marked"]
assert len(rows) == 105

A4 = "research/gmi-833-af4-relative-computability-v1"
A5 = "research/gmi-833-af5-verification-barriers-v1"
ULS = "research/gmi-833-update-law-space-v1"
MIM = "research/machine-intelligence-morphogenesis-v1"

EARNED = {}

EARNED[70] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/PARENT_LEDGER_V1.json#AF4-P1-TURING-JUMP", A4+"/RESULT_V1.json#parent_theorem"],
 u"`PARENT_LEDGER_V1.json` row `AF4-P1-TURING-JUMP` imports the jump theorem at its own assumptions (`A'` is c.e. in `A` but not computable in `A`, hence `deg_T(A) < deg_T(A')`) citing SEP *Recursive Functions* Prop. 3.7, and `RESULT_V1.json#parent_theorem.ownership` is `PARENT_OWNED_NOT_PROVED_BY_EXECUTOR` with `evidence_role: REGISTRY_COROLLARY_AND_HOSTILE_VALIDATION_NOT_PARENT_THEOREM_PROOF`, so nothing is renamed as a GMI discovery")

EARNED[71] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#comp_object", A4+"/RESULT_V1.json#jump_chain", A4+"/FORMALIZATION_V1.md#Registered standard-oracle substrate"],
 u"`comp_object: \"Comp(S[A]) := deg_T(A) at registered standard-oracle scope only\"` over the registered substrate `S[A]=(ORACLE_TM, oracle=A, access_contract, provenance, raw_resource_contract)`; all 7 `jump_chain` levels carry `provenance: ORACLE_ADVICE_OR_TOOL`, `access_charge_per_query: 1` and `finite_advice_bits: null`")

EARNED[72] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#nonterminal_frontier_terminal", A4+"/RESULT_V1.json#jump_chain", A4+"/RESULT_V1.json#scope"],
 u"`nonterminal_frontier_terminal: NO_TERMINAL_EFFECTIVE_FRONTIER_AT_REGISTERED_ORACLE_MODEL_SCOPE` at `scope: standard oracle Turing model; finite registered jump levels 0..6`, every `jump_chain` entry recording `parent_relation_to_next: STRICTLY_BELOW_BY_TURING_JUMP_PARENT`")

EARNED[73] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#physical_scope", A4+"/RESULT_V1.json#forbidden_promotions", A4+"/test_af4_relative_computability_v1.py#test_08_physical_promotion_rejected"],
 u"`physical_scope: NO_PHYSICAL_HYPERCOMPUTATION_CLAIM` and `forbidden_promotions` carries `NO_FINAL_COMPUTABILITY_BARRIER_IN_ALL_PHYSICS`, `PHYSICAL_CHURCH_TURING_FALSIFIED` and `PHYSICAL_HYPERCOMPUTATION_ESTABLISHED`; tests 08 and 15 enforce it, 16/16 passing when re-run on laptop-billy at main `349c2e62`")

EARNED[74] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#adjacent_displacements", A4+"/FORMALIZATION_V1.md#Capability-envelope displacement"],
 u"6 `adjacent_displacements` records, each `S_n -> S_(n+1)` with `changed_axes: [S, Pi, R]`, `direct_oracle_queries: 1`, `oracle_access_charge: 1`, `provenance: ORACLE_ADVICE_OR_TOOL`, `Q_n` moving `UNDECIDABLE_RELATIVE_TO_S -> DECIDABLE` and `nearest_residual` preserved; `ORACLE_POWER_FREE` is a forbidden promotion and `finite_advice_bits` is `null` by construction because an infinite oracle is not assigned a fabricated finite bit count (test 06)")

EARNED[75] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#base_halting_hostile", A4+"/RESULT_V1.json#forbidden_promotions"],
 u"`base_halting_hostile` records `S0_Q0: UNDECIDABLE_RELATIVE_TO_S`, `S1_Q0: DECIDABLE_BY_ONE_IMPORTED_ORACLE_QUERY`, `S1_Q1: UNDECIDABLE_RELATIVE_TO_S`, `residual_preserved: true` and `universal_terminal_allowed: false`, with `HALTING_PROBLEM_SOLVED_UNIVERSALLY` in `forbidden_promotions` and test 02 rejecting the promotion")

EARNED[76] = ("gmi-833-af4-relative-computability-v1",
 [A4+"/RESULT_V1.json#godel_machine_audit", A4+"/PARENT_LEDGER_V1.json#AF4-P3-GODEL-MACHINE"],
 u"`godel_machine_audit` demands the full `ProofContext` (formal_system_id, axioms_id, proof_rules_id, utility_theorem, consistency/soundness assumptions, proof_search_contract) and returns `changed_axioms_reading: PROOF_SYSTEM_CONTEXT_CHANGED_NOT_INCOMPLETENESS_ESCAPE`, `unprovable_reading: NOT_DERIVABLE_IN_REGISTERED_T__TRUTH_NOT_INFERRED`, `registered_reading: PROOF_SYSTEM_RELATIVE_SELF_IMPROVEMENT_CLAIM_ONLY`, with `GODEL_INCOMPLETENESS_ESCAPED` and `GODEL_MACHINE_PROVES_UNIVERSAL_SELF_IMPROVEMENT` forbidden and the Schmidhuber parent (arXiv:cs/0309048) pinned as conditional on its provability assumptions")

EARNED[77] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#parent_no_go", A5+"/FORMALIZATION_V1.md#Parent no-go"],
 u"`parent_no_go.reading` states it with its assumptions attached — \"no automatic terminating correct decider for every nontrivial unrestricted semantic program property at the classical parent scope\" — under `ownership: PARENT_OWNED_NOT_PROVED_BY_EXECUTOR`, with `RICE_THEOREM_FALSE` and `UNRESTRICTED_SEMANTIC_VERIFICATION_SOLVED` in `forbidden_promotions`")

EARNED[78] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#guarantee_lattice"],
 u"`guarantee_lattice` is the powerset of 8 atoms ordered by subset with `total_ranking: false`, and every category the row names is a registered named point: `DECIDABLE_RESTRICTED_FRAGMENT`, `SEMI_DECISION_BUG_WITNESS`, `CERTIFIABLE`, `SOUND_INCOMPLETE_APPROXIMATION`, `CEGAR_REFINED_CERTIFIABLE`, `BOUNDED_MODEL_CHECKED`, `PROBABILISTIC_PROPERTY_TEST`, `UNKNOWN_ABSTAIN`, plus `UNRESTRICTED_UNDECIDABLE` as the empty guarantee set")

EARNED[79] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#semidecision", A5+"/RESULT_V1.json#certificate", A5+"/RESULT_V1.json#cegar", A5+"/RESULT_V1.json#bounded", A5+"/RESULT_V1.json#property_test"],
 u"measured on the frozen fixtures: the same `safe` system `s0->s1->s2` moves `UNKNOWN_ABSTAIN` (semidecision, `safe_proved: false`) to `CERTIFIABLE` under the inductive invariant `{s0,s1,s2}` (proof_construct 3 / proof_check 6) and from `UNKNOWN_FALSE_ALARM_POSSIBLE` to `SOUND_INCOMPLETE_APPROXIMATION` after one CEGAR refinement (`spurious_counterexamples: 1`), while BMC on the 4-step bug system moves `NO_BUG_FOUND_WITHIN_BOUND` at k=3 to `BUG_WITNESS_WITHIN_BOUND` at k=4; the `PROBABILISTIC_PROPERTY_TEST` point is reached on a separate frozen 8-bit promise (four ones, three distinct samples) at exact `delta = 1/14`, not on the `s0-s2` fixture")

EARNED[80] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#tradeoff_statement", A5+"/RESULT_V1.json#forbidden_promotions", A5+"/RESULT_V1.json#abstract_coarse"],
 u"each fixture receipt carries the tradeoff as a field rather than as prose — `sound: true` / `complete: false` on both abstractions, `unbounded_safety_proved: false` on both BMC bounds, `safe_proved: false` on both semidecisions, `exact_decider: false` on the property test — and each laundering route is a registered forbidden promotion: `FALSE_ALARM_IS_BUG`, `BOUNDED_NO_BUG_IS_UNBOUNDED_PROOF`, `PROPERTY_TEST_IS_EXACT_DECIDER`, `SOUND_AND_COMPLETE_AUTOMATIC_VERIFICATION_UNIVERSAL`")

EARNED[81] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#verification_selection", A5+"/RESULT_V1.json#certificate"],
 u"`CERTIFICATE_EMITTER` is a candidate in the selection space alongside `DIRECT_REPLAY`, with raw vector `(base 5, direct_verification 0, proof_construct 5, proof_check 1)` keeping construction and checking as separate coordinates (the `safe` fixture's own certificate costs 3 to construct and 6 to check), and `CERTIFICATE_CONSTRUCTION_FREE` is a forbidden promotion")

EARNED[82] = ("gmi-833-af5-verification-barriers-v1",
 [A5+"/RESULT_V1.json#verification_selection", A5+"/af5_verification_barriers_v1.py#SELECTION_CROSSOVER_DRIFT"],
 u"an exact-rational crossover under the preregistered diagnostic `base + w_v * verification_burden`: argmin is `DIRECT_REPLAY` at `w_v=1/10` (19/5 against 28/5), a two-way tie at `w_v=1` (11 against 11) and `CERTIFICATE_EMITTER` at `w_v=2` (17 against 19); the executor hard-fails with `SELECTION_CROSSOVER_DRIFT` if that pattern moves, and `UNIVERSAL_VERIFICATION_MORPHOLOGY` is forbidden so no architecture law is promoted from the fixture")

EARNED[35] = ("gmi-833-update-law-space-v1",
 [MIM+"/PARENT_LEDGER_V2.json#P9A.CHEAP_GRADIENT", MIM+"/PARENT_LEDGER_V2.json#rule",
  ULS+"/PARENT_OWNERSHIP_V1.md#1.1 Reverse accumulation and the cheap-gradient principle",
  ULS+"/MANIFEST_V1.json#CHEAP_GRADIENT_PRINCIPLE_IS_NOVEL_HERE"],
 u"+ `machine-intelligence-morphogenesis-v1` (cross-section citation — the subtraction lives in Section I and the corpus parent ledger, not in an AI package): corpus-scope ledger record `P9A.CHEAP_GRADIENT` is `disposition: ADOPT` and its `kill_scope` reads \"Kills any GMI-T5 claim that 'deriving backprop from the basis' is novel when the basis already contains a reverse-traversable DAG with local derivatives (that is Baur-Strassen 1983 / Linnainmaa 1970-76 / Speelpenning 1980)\", under the ledger `rule` that parent collision does not authorize relabeling the same mechanism as novelty; the one package on main that does reverse-mode work restates it at package scope with DOIs (Linnainmaa 10.1007/BF01931367, Griewank-Walther 10.1137/1.9780898717761, Baur-Strassen 10.1016/0304-3975(83)90110-X, Rumelhart-Hinton-Williams 10.1038/323533a0), declaring the cheap-gradient principle \"PARENT MATHEMATICS\" that the tranche \"does not claim, does not improve, and does not re-derive as a contribution\", and registering `CHEAP_GRADIENT_PRINCIPLE_IS_NOVEL_HERE` and `NAMED_ALGORITHM_DERIVED_AS_NECESSARY` as forbidden promotions")

# ---- re-derived reasons for rows that stay unmarked ----
AI946 = (u" PR #946 (which owns AI1-AI8) is still OPEN with a failing check as of 2026-09-18, "
         u"so no AI package beyond `gmi-833-ai0-convergence-spine-v1` exists on main; that is the secondary reason, not the primary one.")

REASON = {}
REASON[2] = (u"No artifact on main maps AG/AH lower-substrate work into the spine's GEN interface. Re-checked this round against the packages merged since round 1: "
  u"`grep -rl CONVERGENCE_SPINE research/ .github/` returns 9 files and none of them is `gmi-833-agah-map-v1`, `gmi-833-ag1-descent-stack-v1` or `gmi-833-ag2-signature-free-syntax-v1`; the new `gmi-833-agah-map-v1` is a comment-row structural map for comments 5693520829/5693590252 with zero spine references. "
  u"The tokens AG and AH still occur nowhere in the ai0 package (regex \\bA[GH][0-9]?\\b over all its files returns zero hits, against a control grep that resolves). The other 6 of 7 required mappings are present in the DAG.")
REASON[93] = (u"Half of round 1's reason is now resolved and half is not. `Comp(S)` now exists: PR #971 merged and `gmi-833-af4-relative-computability-v1/RESULT_V1.json#comp_object` registers `Comp(S[A]) := deg_T(A)`, and AF4 does demonstrate the update-and-recompute discipline (SUBSTRATE_EXPANSION displacement, frontier recomputed, nearest residual preserved, no theorem declared broken). "
  u"But the row asks this of a PHYSICAL substrate, and the cited artifact disclaims that leg on-subject: `OPEN_GAPS_V1.json#open[AF4_PHYSICAL]` reads \"No oracle is claimed physically realizable and no physical Church-Turing thesis is tested; AF7 remains authority\", and `RESULT_V1.json#physical_scope` is `NO_PHYSICAL_HYPERCOMPUTATION_CLAIM`. No `S_phys` object exists on main (zero hits across the whole research tree).")
REASON[97] = (u"Unchanged and re-verified today rather than restated from round 1: `python3 -I -B check_aj9a.py` run on laptop-billy against main `349c2e62` exits 1 (`AssertionError` at check_aj9a.py:101, `assert all(r for r in hostile_results)`). "
  u"`audit_config()`'s `walk()` scans string values held directly under a dict key and never descends into list elements, so 4 of its own 11 hostiles go undetected - {'ops':['dense_layer']}, {'ops':['self_attention']}, {'ops':['bayes_update']}, {'ops':['genetic_algorithm']} - which is exactly how operator lists are supplied. "
  u"Per-holdout source audits do work (aj9b-aj9h each report `blind_source_forbidden_hits: []`, and a planted leak is detected), but the frozen contract's own config auditor does not, so family-specific operator/cost-bonus smuggling is not demonstrably excluded for every holdout. No CI workflow runs this checker and the committed RESULT_V1.json still asserts `hostile_configs_rejected: 11`, `status: GREEN`.")

AJ15R = (u"No AJ15 package exists on main, proved two independent ways this round: `/usr/bin/find research -iname '*aj15*'` returns 0 paths (control `-iname '*aj14*'` returns 2), and `grep -rl AJ15 research/` returns only two OPEN_GAPS files. "
  u"The second of those is a live on-subject disclaimer from the neighbouring tranche: `research/gmi-833-aj14-establishment-criterion-v1/OPEN_GAPS.json#remaining[AJ15]` reads `severity: critical`, \"flagship end-to-end falsification experiment remains to be executed\", with `full_gmi_supported_now: false`. "
  u"AJ9/AJ10/AJ11 are three separate microscopes, not one end-to-end flagship experiment; in particular no ecology/resource regime is registered in which a held-out family is predicted not to appear (every AJ9 receipt records `predicted_selected: NOT_CLAIMED`).")
for i in range(98, 105):
    REASON[i] = AJ15R

# AI section re-derived scope reasons
REASON_AI = {}
GROUP_LABEL = {}
for i in (5, 6):
    GROUP_LABEL[i] = 'AI1'
    REASON_AI[i] = (u"Scope: no artifact on main defines the NN-D1/NN-D2/NN-D3 trichotomy the row's claims must carry - `grep -rl 'NN_D1|NN-D1|NN_D2|NN-D2|NN_D3' research/` returns zero files (control greps on the same tree resolve), and `NEURAL_NETWORK_DERIVED` occurs once, inside a not-allowed-terminals block in `research/machine-intelligence-morphogenesis-v1/GMI_SEMANTIC_QUOTIENT_REALIZATION_THEOREM_V1.md` (`NEURAL_NETWORK_DERIVED_AS_UNIQUE_OPTIMUM`, scoped \"from this theorem\"), which is not the NN-D1 conditioning the row requires." + AI946)
for i in range(7, 18):
    GROUP_LABEL[i] = 'AI2'
    REASON_AI[i] = (u"Scope: nothing on main compiles a feed-forward neural computation from sub-neural primitives. `NN_D1_EXPRESSIBLE_AT_SCOPE` has zero hits across the research tree, and no package registers a lower-primitive basis together with a semantic-equivalence proof to a supplied finite feed-forward network." + AI946)
for i in range(18, 28):
    GROUP_LABEL[i] = 'AI3'
    REASON_AI[i] = (u"Scope mismatch with the nearest artifact rather than mere ownership: `gmi-833-aj9b-k01-blind-recovery-v1` does run a blind recovery for K01 (the neural family) with two presentations and two searches, but under a different frozen contract - no architecture-name/macro denylist frozen before search, no matched non-neural tasks, no negative controls, and no AutoML-Zero reproduction (`research/g6-evolvability-v1/PARENTS.md` records the AutoML parent as `AUTOML_PARENT_SUFFICIENT_BY_CONSTRUCTION` and `NOT_RUN`). AI3's rows are steps in AI3's own protocol, which does not exist on main." + AI946)
for i in list(range(28, 35)) + [36]:
    GROUP_LABEL[i] = 'AI4'
    REASON_AI[i] = (u"Scope mismatch with the nearest artifact: `gmi-833-update-law-space-v1` IL-4 derives when reverse accumulation wins from graph and resource structure, but explicitly does NOT derive the mechanism this row asks for - its `CORE.md` states \"the adjoint recursion and the elimination view are parent mathematics and are not claimed here\", and `MANIFEST_V1.json#forbidden_promotions` contains `NAMED_ALGORITHM_DERIVED_AS_NECESSARY` and `OPTIMAL_JACOBIAN_ACCUMULATION_SOLVED`, so the row's meaning is forbidden by the parent it would have to cite. No compositional graph, chain-rule derivation or backpropagation-equality instance exists on main." + AI946)
for i in range(37, 44):
    GROUP_LABEL[i] = 'AI5'
    REASON_AI[i] = (u"Scope: no finite regime map comparing neural-like against lookup/direct, rule/program and other morphologies under one external specification exists on main, so there are no predictions, no crossover, no hysteresis test and no Pareto frontier of AI5's to preserve. `gmi-833-aj10-prospective-unknown-v1` does preserve a raw two-candidate Pareto frontier with `unique_morphology_selected: false` and no scalar prices, but on a generic Boolean held-out task, not on a morphology regime map." + AI946)
for i in range(44, 50):
    GROUP_LABEL[i] = 'AI6'
    REASON_AI[i] = (u"Scope: no artifact on main derives any of the recurrent/convolutional/attention/MoE/memory motifs from lower structure, and the row's NN-D1/D2/D3 separation has no definition on main (zero hits for the trichotomy tokens)." + AI946)
for i in range(50, 53):
    GROUP_LABEL[i] = 'AI8.1'
    REASON_AI[i] = (u"Mechanism similarity across a section boundary, not satisfaction. `gmi-833-aj10-prospective-unknown-v1` does enforce the ordering mechanically (`taxonomy_visible_to_search: false`, `capability_evaluated_before_taxonomy: true`, `family_labels_present: false`, a token audit proving `discover_v1.py` contains none of k01-k11 / `unknown_morphology`, and a separate `posthoc_taxonomy_v1.py`), and aj9b-aj9h each report `blind_source_forbidden_hits: []`. But the row is a constraint on a running blind derivation of NEURAL structure; aj10 exercises it on a generic Boolean substrate with family labels drawn from AJ9a's eleven-family catalogue, and aj9a's own config auditor fails on main (check_aj9a.py exit 1), so the extension to search heuristics, priors, stopping rules and evaluator features is not demonstrated for the AI8.1 contract." + AI946)
for i in range(53, 57):
    GROUP_LABEL[i] = 'AI8.2'
    REASON_AI[i] = (u"Scope: `DISCOVER_GMI` has zero hits across the research tree, and so do all five of the status tokens the row's sibling requires (`NOT_GENERATED`, `GENERATED_NOT_REACHED`, `REACHED_NOT_SELECTED`, `SELECTED_UNKNOWN`, `POSTHOC_MATCH`). `UNKNOWN_MORPHOLOGY` exists only as a post-hoc taxonomy status inside `gmi-833-aj10-prospective-unknown-v1`, i.e. an output of a family classifier, not of a discovery operator." + AI946)
for i in range(57, 60):
    GROUP_LABEL[i] = 'AI8.3'
    REASON_AI[i] = (u"Scope: no artifact on main turns environmental-pressure arrows into theorems or prospectively falsifiable hypotheses for neural-like structure, and no nearest counterexample ecology per pressure is registered." + AI946)
for i in range(60, 63):
    GROUP_LABEL[i] = 'AI8.4'
    REASON_AI[i] = (u"Scope: no P1-P6 structural fingerprint exists on main, so there is nothing to prove non-collapsing, nothing for non-neural negative controls to satisfy subsets of, and nothing to audit for smuggled modern conventions." + AI946)
for i in range(63, 66):
    GROUP_LABEL[i] = 'AI8.5'
    REASON_AI[i] = (u"Scope: no co-optimal/Pareto-incomparable control and no absent/dominated regime is registered for neural-like organization. On the prohibition row specifically, main carries only package-local forbiddens - `NEURAL_NETWORK_DERIVED_AS_UNIQUE_OPTIMUM` scoped \"from this theorem\" in `machine-intelligence-morphogenesis-v1`, `NEURAL_NECESSARY` inside `functional-neural-absorption-v1/fna4_library_synthesis/fna4.py` and `rv8-h1-horizon-v1/RV8_FREEZE.json` - and none of them states the row's condition (forbidden absent an actual uniqueness theorem under explicit assumptions) or binds the corpus." + AI946)
for i in range(66, 68):
    GROUP_LABEL[i] = 'AI8.6'
    REASON_AI[i] = (u"Scope: no discovery ladder with L1-L5 levels is registered on main, so it is applied to no family and no L4 threshold exists to reach." + AI946)
# A bulk reason must land on a row of its own section. Each anchor carries the
# section label, so assert containment: an off-by-one in any index range would
# otherwise pass every downstream gate (old/anchor stay byte-exact and unique)
# while carrying a neighbouring section's reason.
for i in (98, 99, 100, 101, 102, 103, 104):
    GROUP_LABEL[i] = 'AJ15'
GROUP_LABEL[2] = 'AI0'; GROUP_LABEL[93] = 'AF7'; GROUP_LABEL[97] = 'AJ9'
GROUP_LABEL[69] = 'AF1'
for i, lbl in sorted(GROUP_LABEL.items()):
    assert lbl in rows[i]["anchor"], (i, lbl, rows[i]["anchor"])
print("section-label containment: %d/%d reason groups land in their own section" % (len(GROUP_LABEL), len(GROUP_LABEL)))
REASON.update(REASON_AI)

REASON[68] = (u"PR #969 'repair AF1 exact G0 microscope and Gamma converse boundary' is still OPEN (re-checked 2026-09-18, failing check, not merged). Its own body states the merged #962 evidence for this row was an overclaim (the witness was Boolean-level, not executed through the registered G0-reg-v1 interpreter) and that the literal converse is incompatible with the registered definition; #969 moves this row to deferred_tasks. Nothing merged since round 1 supplies a G0-interpreter-level microscope.")
REASON[69] = (u"Unchanged. The merged package's own `ISSUE_833_AF_RECONCILIATION_V1.json#deferred_tasks` lists this row: the #833-L body row is already checked under PR #909/#908 and was not rewritten in the same PR. PR #924 (merged since round 1) edits four other Section L body rows but not this one, so the upgrade to the response-object view still has not been applied.")

DELTA = (u" Re-checked against every package merged since round 1: the tokens this row turns on return zero hits across the 19 new packages, against a validated control grep.")
for i in range(83, 97):
    if i in REASON: continue
    REASON[i] = rows[i]["reason"] + DELTA

SKIP_ALREADY_CLOSED = {68}
out = []
for i, r in enumerate(rows):
    if i in SKIP_ALREADY_CLOSED:
        continue
    e = {"comment_id": r["comment_id"], "old": r["old"]}
    if i in EARNED:
        pkg, ev, sent = EARNED[i]
        e.update({"verdict": "EARNED_BY_MERGED_EVIDENCE", "package": pkg,
                  "evidence_paths": ev, "evidence": sent})
    else:
        e.update({"verdict": r["status"], "reason": REASON.get(i, r["reason"])})
    out.append(e)

dest = os.path.join(HERE, "ADJUDICATION_V2.json")
payload = {"schema": "GMI_833_COMMENT_ADJUDICATION_V2", "rows": out,
 "already_closed_upstream": [{
   "comment_id": rows[68]["comment_id"],
   "old_at_round_1": rows[68]["old"],
   "live_state": "- [x] Construct exact finite `G0` microscopes where two machines have the same current capability but different `Gamma`, and conversely.",
   "note": "Checked in the live comment by another lane with NO evidence suffix, unlike every sibling row in the AF1 block. Out of this round's scope because it is no longer open. Flagged rather than silently dropped: the open repair PR #969 states the merged #962 evidence for exactly this row was an overclaim (the witness was Boolean-level, not executed through the registered G0-reg-v1 interpreter), that the literal converse is incompatible with the registered definition, and it moves the row to deferred_tasks."}]}
io.open(dest, "w", encoding="utf-8").write(json.dumps(payload, indent=1, ensure_ascii=False) + "\n")
from collections import Counter
print("rows", len(out), Counter(x["verdict"] for x in out))
print("wrote", dest)
