# -*- coding: utf-8 -*-
import argparse
import json, io, os

HERE = os.path.dirname(os.path.abspath(__file__))
SNAPSHOTS = os.path.join(HERE, "comment_snapshots")
AI, AI8, AF, AJ = 5693666042, 5693704406, 5693269426, 5693954852


def load_bodies(offline=None):
    """Load fresh comment snapshots from JSON (preferred, ratchet-safe) or md."""
    root = offline or os.environ.get("GMI833_FETCH") or SNAPSHOTS
    out = {}
    for c in (AI, AI8, AF, AJ):
        jp = os.path.join(root, "c_%d.json" % c)
        mp = os.path.join(root, "c_%d.md" % c)
        if os.path.exists(jp):
            doc = json.load(io.open(jp, encoding="utf-8"))
            out[c] = doc["body"] if isinstance(doc, dict) else doc
        else:
            out[c] = io.open(mp, encoding="utf-8").read()
    return out


parser = argparse.ArgumentParser()
parser.add_argument("--offline", metavar="PKGDIR", help="read comment_snapshots/ from this package")
args = parser.parse_args()
bodies = load_bodies(os.path.join(args.offline, "comment_snapshots") if args.offline else None)
lines  = {c: b.split("\n") for c, b in bodies.items()}

def anchor_for(c, n):
    """Nearest preceding '###' (or '##') heading line, verbatim."""
    for i in range(n, -1, -1):
        if lines[c][i].startswith("###") or lines[c][i].startswith("## "):
            return lines[c][i]
    raise AssertionError("no anchor for %s:%s" % (c, n))

MARK = []   # (comment, line, pkg, evidence_paths, sentence)
SKIP = []   # (comment, line, status, reason)

def mark(c, n, pkg, ev, sent):
    MARK.append((c, n, pkg, ev, sent))

def skip(c, n, st, reason):
    SKIP.append((c, n, st, reason))

AI0 = "research/gmi-833-ai0-convergence-spine-v1"
AFP = "research/gmi-833-af-barrier-context-v1"
A9A = "research/gmi-833-aj9a-known-family-benchmark-v1"
A9H = "research/gmi-833-aj9h-k07-k11-blind-recovery-v1"
A10 = "research/gmi-833-aj10-prospective-unknown-v1"
A11 = "research/gmi-833-aj11-bounded-completeness-v1"
A12 = "research/gmi-833-aj12-foundation-substrate-relativity-v1"
A13 = "research/gmi-833-aj13-stopping-rule-v1"

# ---------------- AI0 (comment 5693666042) ----------------
mark(AI, 38, AI0, [AI0+"/GMI_CONVERGENCE_SPINE_V1.md"],
     "`GMI_CONVERGENCE_SPINE_V1.md` exists on main and contains only canonical interfaces (GEN/DEV/REQ/REL/CAP/SEL/EVID), the canonical context `Xi=(F,M0,Delta,Pi,E,Q,R,H,V,U)` with its derived objects, the authority map, the five claim classes and the umbrella gate, declaring itself \"governance plus dependency normalization, not a new peer theory\"")
mark(AI, 40, AI0, [AI0+"/GMI_THEORY_DEPENDENCY_DAG.json#nodes", AI0+"/RESULT_V1.json#dag_acyclic"],
     "one machine-readable DAG with 19 material-theory nodes, verified acyclic by `check_ai0.py` (re-run on laptop-billy, exit 0, `registered_material_nodes=19`, `topological_nodes=19`), spanning `ISSUE_833`, `GOV_373`, `BASELINE_602` and `HSG_DEV` (#233)")
mark(AI, 43, AI0, [AI0+"/GMI_THEORY_DEPENDENCY_DAG.json#cross_cutting_only", AI0+"/RESULT_V1.json#barrier_role"],
     "`cross_cutting_only=[\"BARRIER_CALCULUS\"]` and node `BARRIER_CALCULUS` carries role `CROSS_CUTTING_BOUNDARY_CALCULUS` over interfaces GEN/DEV/REL/CAP/SEL, while `check_ai0.py` asserts the sole `INTEGRATION_SPINE` role is `ISSUE_833`, so barrier theory is not a peer layer")
mark(AI, 46, AI0, [AI0+"/GMI_CONVERGENCE_SPINE_V1.md#Duplicate and disagreement rule", AI0+"/RESULT_V1.json#parent_owned_nodes"],
     "duplicate/disagreement rule 2 states parent-owned mathematics is cited and novelty moved upward, and the DAG applies it: `PARENT_BLACKWELL` and `PARENT_NFL` are classed `PARENT_OWNED` with external owners, asserted by `check_ai0.py`")
mark(AI, 47, AI0, [AI0+"/GMI_CONVERGENCE_SPINE_V1.md#Duplicate and disagreement rule", AI0+"/RESULT_V1.json#registered_discriminator"],
     "rules 3-4 require a discriminating theorem/counterexample/experiment and otherwise mark observational indistinguishability at scope; the registered instance is `G0_STRUCTURAL_BIAS_BOUNDARY` (#896 same-semantics/non-isometric counterexample), node role `DISCRIMINATOR_COUNTEREXAMPLE`")
mark(AI, 48, AI0, [AI0+"/GMI_CONVERGENCE_SPINE_V1.md#Gate", AI0+"/RESULT_V1.json#gate", AI0+"/GMI_THEORY_DEPENDENCY_DAG.json#no_new_umbrella_gate"],
     "the gate `NO_NEW_GMI_UMBRELLA_UNTIL_CONVERGENCE_V1` is frozen verbatim with the stated exception (\"unless the dependency audit identifies a genuinely missing unique object\"), and `check_ai0.py` asserts the DAG carries it")
mark(AI, 49, AI0, [AI0+"/GMI_THEORY_DEPENDENCY_DAG.json#authority_reconciliation"],
     "`authority_reconciliation` fixes #833=\"integration/scientific-spine specification\", #233=\"developmental-dynamics formal module\", #373=\"convergence/governance module\", #602=\"historical v1 closure baseline only\", and `check_ai0.py` asserts those exact strings")

skip(AI, 39, "PARTIAL", "NOTATION_CROSSWALK.json is a single frozen crosswalk but carries 12 legacy-symbol entries with no exhaustiveness certificate over the corpus; check_ai0.py only asserts that the 7 canonical interfaces are each covered at least once, not that ALL legacy symbols/theory names are mapped.")
skip(AI, 41, "PARTIAL", "Self-disclaimed by the package: OPEN_GAPS.json#remaining[CORPUS_WIDE_THEOREM_ROW_CLASSIFICATION] says the 19-node registry covers authoritative material theory MODULES and that 'theorem-by-theorem corpus audit remains owned by #833 Section B rather than AI0'. Row asks for EVERY material theory/result.")
skip(AI, 42, "PARTIAL", "6 of the 7 required mappings are present in the DAG (HSG_DEV->DEV, PARENT_BLACKWELL/REL_EQUIVALENCE->REL, CAPABILITY_CORE->CAP, SEL_MORPHOLOGY->SEL, EVID_AA_AD->EVID, REQ_PROVENANCE->REQ). The 'AG/AH lower-substrate work to GEN' mapping is absent: the tokens AG and AH occur nowhere in the package (regex \\bA[GH]\\b over all 7 files returns zero hits); the GEN slot is filled by AJ1-AJ5 instead.")
skip(AI, 44, "PARTIAL", "Same self-disclaimer as row 41. The one-authoritative-owner RULE is frozen and the 19 DAG nodes each carry exactly one owner, but nodes are theory MODULES; no theorem/experiment-level owner assignment exists. Row asks for EVERY theorem/experiment.")
skip(AI, 45, "PARTIAL", "The merge rule is frozen (spine 'Duplicate and disagreement rule' 1) but no duplicate-THEOREM merge was executed. The only applied instance is module-level: #602 classed SUPERSEDED_REDUNDANT (class_histogram SUPERSEDED_REDUNDANT=1). No weaker theorem was retained as a corollary.")

# AI1-AI6 rows -> blocked on open PR #946
for n in [71, 72] + list(range(87, 98)) + list(range(105, 115)) + list(range(138, 147)) + list(range(167, 174)) + list(range(179, 185)):
    skip(AI, n, "BLOCKED_ON_OPEN_PR", "PR #946 'research(#833): execute AI1-AI8 blind neural derivation microscope' is open, not merged. No AI1-AI6 package exists under research/ on main.")

# AI8 comment -> all blocked on #946
for n, l in enumerate(lines[AI8]):
    if l.startswith("- [ ]"):
        skip(AI8, n, "BLOCKED_ON_OPEN_PR", "PR #946 (AI1-AI8 blind neural derivation microscope) is open, not merged. No AI8 package exists under research/ on main.")

# ---------------- AF (comment 5693269426) ----------------
mark(AF, 25, AFP, [AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#repository_pins", AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#issue_comment_authorities"],
     "six #233/HST/HSG parents are pinned by Git blob SHA plus the HSG-T51 authority pinned to #233 comment 5609406015 (updated_at 2026-09-09T22:07:34Z, exact heading); fail-closed verified by mutating one pin to 40 zeroes, which aborts `af_barrier_context_v1.py` with `ValueError: parent pin drift`, while the unmutated run exits 0 (`parent_pin_count=6`)")
mark(AF, 26, AFP, [AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#rows"],
     "`GMI_BARRIER_PARENT_LEDGER_V1` holds 21 parent rows, each carrying exactly the six required fields `theorem_or_result`, `assumptions`, `conclusion`, `relaxations`, `strongest_source` and `af_residual` (parent_census=21)")
mark(AF, 27, AFP, [AFP+"/FORMALIZATION_V1.md#1. AF0", AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#EFFECTIVE_VS_PHYSICAL_CT_BOUNDARY"],
     "FORMALIZATION_V1 section 1 splits the two families explicitly (mathematical effective-computation claims vs empirical physical-computation theses) and the ledger row `EFFECTIVE_VS_PHYSICAL_CT_BOUNDARY` carries residual 'AF0 records PHYSICAL_STATUS_UNKNOWN unless operational physical evidence exists', with `PHYSICAL_STATUS_UNKNOWN` in the AF3 status vocabulary")
mark(AF, 28, AFP, [AFP+"/FORMALIZATION_V1.md#4.3 AF-T03", AFP+"/RESULT_V1.json#af3.broke_changed_premise_hostile_rejected"],
     "AF-T03 admits `BROKE_*` only under five conjunctive conditions (premises retained, same problem contract, same output contract, independently verified contradiction witness, class LITERAL_CONTRADICTION); the hostile relabelling the finite-promise restriction as BROKE_TURING is rejected (`broke_changed_premise_hostile_rejected=true`) and BROKE_TURING/RICE/GODEL/NFL/BLUM sit in `forbidden_promotions`")
mark(AF, 45, AFP, [AFP+"/FORMALIZATION_V1.md#2. AF1", AFP+"/RESULT_V1.json#af1.gamma_object"],
     "`Gamma^S_{M0,Delta}(Pi,R,H,Q,V)` is defined as a set of profiles `(c,r,pi,m,h)` with no architecture name and no scalar intelligence score, and section 2.1 states its relation to each existing object: capability (consumes the #833 external contract), reachability (profile-valued lift), morphology (property of terminal realization m, not a primitive), resources (raw vectors primary), HST/HSG")
mark(AF, 46, AFP, [AFP+"/FORMALIZATION_V1.md#2.2 Current capability is only a slice", AFP+"/RESULT_V1.json#af1.f1_same_current_score"],
     "`Current(M0,Q,V) = { c(g) : g in Gamma and development_steps(g)=0 }` is the zero-development slice, and microscope F1 shows it under-determines Gamma: both systems score current `1/2` on identity while one reaches capability set {1, 1/2} and the frozen one stays {1/2}")
mark(AF, 47, AFP, [AFP+"/FORMALIZATION_V1.md#2.3 Possibility space is not reachability", AFP+"/RESULT_V1.json#af1.possibility_not_reachability_witness"],
     "`M(S)` is defined as the data/history-independent admitted class and `Reach(M0,Delta,Pi,R,H,V) subseteq M(S)` separately; the exact witness is `NOT` in `M(S)\\Reach` with `possibility_set=[C0,C1,ID,NOT]` against `frozen_reachable_set=[C0]`, independently reconstructed by `independent_oracle_v1.py` (`possibility_vs_reachability: true`)")
mark(AF, 48, AFP, [AFP+"/RESULT_V1.json#af1.provenance_tags", AFP+"/FORMALIZATION_V1.md#2.4 Provenance-tagged development"],
     "all eight required channels are registered verbatim as `provenance_tags`: INITIAL_OR_INHERITED_ORGANIZATION, EXTERNAL_OBSERVATION, REWARD_OR_EVALUATOR_SIGNAL, ENDOGENOUS_COMPUTE, STOCHASTIC_VARIATION, ORACLE_ADVICE_OR_TOOL, SOCIAL_OR_CULTURAL_TRANSFER, PHYSICAL_OR_ENVIRONMENTAL_SIGNAL")
mark(AF, 49, AFP, [AFP+"/FORMALIZATION_V1.md#2.4 Provenance-tagged development", AFP+"/RESULT_V1.json#af2.nonuniform_initial_advice"],
     "section 2.4 fixes 'a path cannot omit a consumed channel' and rules that an arbitrary real parameter used as nonuniform advice 'is never free emergence from nothing'; the exact instances are F5 (`IMPORTED_ORACLE_OR_ADVICE_POWER`, 1 bit target MI) and F5b target-correlated initialization (`IMPORTED_INFORMATION_OR_ADVICE`, provenance INITIAL_OR_INHERITED_ORGANIZATION)")
mark(AF, 66, AFP, [AFP+"/RESULT_V1.json#af2.null_condition_hierarchy"],
     "the receipt carries all seven named null conditions in order with their exact forbidden-channel sets: NO_SENSORY_OBSERVATIONS, NO_REWARD_OR_EVALUATOR_FEEDBACK, NO_TASK_SPECIFIC_DATA, NO_EXTERNAL_INTERACTION, NO_ENDOGENOUS_RANDOMNESS, NO_TASK_SPECIFIC_INITIALIZATION, ABSOLUTE_REGISTERED_NULL_EXCEPT_SUBSTRATE_AND_DYNAMICS (`null_condition_count: 7` in the independent oracle)")
mark(AF, 67, AFP, [AFP+"/FORMALIZATION_V1.md#3.2 AF-T01", AFP+"/RESULT_V1.json#af2.af_t01"],
     "AF-T01 states and proves exactly the asked specialization - Theta independent of Z=(M0,W), Mt=f(Z) deterministic, Markov chain Theta->Z->Mt, data-processing inequality gives I(Theta;Mt)<=I(Theta;Z)=0 - with receipt `finite_joint_mutual_information_bits: 0.0` reproduced independently by `independent_oracle_v1.py` (`independent_target_mi_bits: 0.0`)")
mark(AF, 68, AFP, [AFP+"/FORMALIZATION_V1.md#3.3", AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#HSG-T51_AIT_BOUND"],
     "section 3.3 restates HSG-T51 as the parent bound K(s_n)<=K(F)+K(s_0)+K(n)+O(1) and explicitly separates it from the Shannon statement ('That parent is about description length/Kolmogorov complexity. AF-T01 is about mutual information with a registered random target'), with ownership pinned to #233 comment 5609406015 and verified live by `verify_hsg_parent_authority_v1.py` (exit 0)")
mark(AF, 69, AFP, [AFP+"/RESULT_V1.json#af2.compute_unfolding"],
     "control F3 is exactly such an example: with zero external data, deterministic internal compute moves accuracy from `1/2` to `1` while registered target information stays `1 bit -> 1 bit`, terminal `COMPUTATIONAL_UNFOLDING_WITHOUT_EXTERNAL_DATA`")
mark(AF, 70, AFP, [AFP+"/RESULT_V1.json#af2.compute_unfolding", AFP+"/RESULT_V1.json#af2.random_novelty"],
     "the three are machine-separated by distinct terminals with distinct numbers: unfolding (accuracy 1/2->1, target info 1->1 bit), random novelty (output entropy 1.0 bit, target MI 0.0 bit, accuracy 1/2), acquisition (oracle target MI 1.0 bit)")
mark(AF, 71, AFP, [AFP+"/RESULT_V1.json#af2.random_novelty"],
     "hostile F4 supplies an independent fair random bit: `output_entropy_bits: 1.0` but `target_mutual_information_bits: 0.0` and `expected_target_accuracy: 1/2`, terminal `RANDOM_NOVELTY_WITHOUT_TARGET_ALIGNMENT`")
mark(AF, 72, AFP, [AFP+"/RESULT_V1.json#af2.oracle_advice", AFP+"/RESULT_V1.json#af2.nonuniform_initial_advice"],
     "hostiles F5 and F5b do exactly this: a target-correlated oracle bit yields `target_mutual_information_bits: 1.0` and accuracy `1` but only under `ORACLE_ADVICE_OR_TOOL` provenance (`IMPORTED_ORACLE_OR_ADVICE_POWER`), and arbitrary-real/advice content in the initial organization is classified `IMPORTED_INFORMATION_OR_ADVICE`")
mark(AF, 73, AFP, [AFP+"/RESULT_V1.json#af2.terminals"],
     "`af2.terminals` registers all five asked terminals plus IMPORTED_INFORMATION_OR_ADVICE, and FORMALIZATION 3.4 states that neither NO_TARGET_INFORMATION_ACQUIRED nor UNEXERCISED_CAPABILITY is synonymous with INCAPABLE")
mark(AF, 104, AFP, [AFP+"/FORMALIZATION_V1.md#4. AF3", AFP+"/RESULT_V1.json#af3.context", AFP+"/RESULT_V1.json#af3.statuses"],
     "barrier context is `chi=(S,Pi,Q,R,H,eps,delta,V)`, the typed status vocabulary has 10 registered values (DECIDABLE ... PHYSICAL_STATUS_UNKNOWN) and displacement semantics are instantiated by four full transition records, independently counted by the oracle (`f7_record_count: 4`)")
mark(AF, 105, AFP, [AFP+"/RESULT_V1.json#af3.transition_records"],
     "every transition record carries `changed_axes`, `original_premises`, `retained_premises` and `extra_power_or_weakened_requirement` - e.g. F7_ORACLE_RELATIVIZATION changes axes [S,Pi,R] and records 'add an explicitly charged oracle channel deciding the base halting set'")
mark(AF, 106, AFP, [AFP+"/FORMALIZATION_V1.md#4.1 Transition/displacement record"],
     "the frozen transition classes are exactly the thirteen asked: domain restriction, promise problem, approximation, semidecision, abstention, list/set output, certificate, interaction/query, oracle/advice, randomness, resource relaxation, substrate expansion and literal contradiction")
mark(AF, 107, AFP, [AFP+"/FORMALIZATION_V1.md#4.2 AF-T02", AFP+"/RESULT_V1.json#af3.mandatory_overhead_hostile"],
     "AF-T02 proves monotonicity only under optionality + zero mandatory overhead + preserved order; hostile F6 is the counterexample: base net 8, optional strategy leaves optimum at 8, and a mandatory overhead of 12 reverses best net to -4 (`reversal: true`), independently reconstructed by the oracle as `mandatory_overhead_reversal: [8, 8, -4]`")
mark(AF, 108, AFP, [AFP+"/RESULT_V1.json#af3.transition_records", AFP+"/RESULT_V1.json#af3.solved_forever_allowed"],
     "all four transition records carry a non-empty `nearest_residual_barrier` and `solved_forever_allowed: false`, with SOLVED_FOREVER in `forbidden_promotions`")
mark(AF, 153, AFP, [AFP+"/GMI_BARRIER_PARENT_LEDGER_V1.json#CHARIKAR_PABBARAJU_TEWARI_2026_LIST_ID", AFP+"/RESULT_V1.json#af3.transition_records[F7_LIST_OUTPUT]"],
     "the 2026 result is pinned as a parent (Charikar, Pabbaraju & Tewari, COLT/PMLR 336 (2026)) and instantiated as transition record `F7_LIST_OUTPUT`: LANGUAGE_IDENTIFICATION under POSITIVE_TEXT moves from `NOT_IDENTIFIABLE_AT_SCOPE` to `IDENTIFIABLE_IN_LIMIT` with the only changed axis `V` (SINGLE_ANSWER_OUTPUT -> FINITE_LIST_OUTPUT), nearest residual barrier 'single-answer identification is not thereby established'")
mark(AF, 167, A12, [A12+"/RESULT_V1.json#physical_hypercomputation", A12+"/FREEZE_V1.md#Alternative substrate/accounting boundary"],
     "the receipt records `physical_hypercomputation: EMPIRICAL_OPEN__NO_REPRODUCIBLE_EVIDENCE_REGISTERED_HERE` and the freeze makes it mandatory: '`PHYSICAL_HYPERCOMPUTATION_OPEN` is mandatory absent reproducible physical evidence', with PHYSICAL_HYPERCOMPUTATION_PROVED in forbidden_promotions")
mark(AF, 169, AFP, [AFP+"/RESULT_V1.json#forbidden_promotions", AFP+"/FORMALIZATION_V1.md#1. AF0"],
     "`PHYSICAL_CHURCH_TURING_FALSIFIED` is listed in the AF `forbidden_promotions`, and FORMALIZATION section 1 gives the reason in terms the row asks for: 'No simulated oracle or arbitrary-real model is itself evidence that a physical thesis has been falsified'")
mark(AF, 177, A11, [A11+"/THEORY.md#Finite registered universe", A11+"/RESULT_V1.json#bounded_scope"],
     "`check_aj11.py` (re-run on laptop-billy, exit 0) exhaustively enumerates all 260 frozen presentations, collapses them to 148 exact operational classes by all-word reachable-product equivalence over 33,670 pair checks, and computes the capability (5 coordinates over 31 protected words), raw-resource and developmental-distance atlas")
mark(AF, 179, A11, [A11+"/THEORY.md#Unbounded boundary", A11+"/RESULT_V1.json#unbounded_boundary"],
     "the unbounded boundary is stated as exactly that separation: `syntax_programs: EFFECTIVELY_ENUMERABLE_UNDER_REGISTERED_FINITE_ALPHABET` against `semantic_equivalence: UNDECIDABLE_IN_GENERAL_AT_TURING_COMPLETE_SCOPE`, with the explicit argument that a terminating semantic catalogue would decide program equivalence")
mark(AF, 180, AFP, [AFP+"/RESULT_V1.json#af3.statuses"],
     "the AF3 status vocabulary returns exactly the six asked outcome types: DECIDABLE (exact decision), CERTIFIABLE (witness/certificate), SOUND_INCOMPLETE_APPROXIMATION (sound approximation), PROBABILISTIC_APPROXIMATION (probabilistic estimate), NOT_IDENTIFIABLE_AT_SCOPE (unknown/nonidentified) and UNDECIDABLE_RELATIVE_TO_S (relative undecidability)")
mark(AF, 181, A10, [A10+"/POSTHOC_RESULT_V1.json#unknown_policy", A10+"/RESULT_V1.json#unknown_channel_exercised"],
     "the UNKNOWN channel is not merely declared but exercised: candidate T232 gets `registered_family: null` / `registered_taxonomy: UNKNOWN_MORPHOLOGY`, and the frozen policy preserves the pre-taxonomy UNKNOWN record even after strongest-parent reduction rather than forcing a family label")

skip(AF, 50, "BLOCKED_ON_OPEN_PR", "PR #969 'repair AF1 exact G0 microscope and Gamma converse boundary' is open. Its own body states the merged #962 evidence for this row was an overclaim (witness was Boolean-level, not executed through the registered G0-reg-v1 interpreter) and that the literal converse is incompatible with the registered definition; #969 moves this row to deferred_tasks.")
skip(AF, 51, "PARTIAL", "The merged package's own ISSUE_833_AF_RECONCILIATION_V1.json#deferred_tasks lists this row with reason: the #833-L body row is already checked under PR #909/#908 and was not rewritten in the same PR. The upgrade to the response-object view has not been applied to the #833 body.")
for n in range(124, 131):
    skip(AF, n, "BLOCKED_ON_OPEN_PR", "PR #971 'research(#833): formalize AF4 relative computability and non-terminal oracle frontier' is open, not merged. The merged AF package states in FORMALIZATION_V1.md section 6 that AF4+ remains open.")
for n in range(138, 144):
    skip(AF, n, "BLOCKED_ON_OPEN_PR", "PR #973 'research(#833): formalize AF5 verification barrier displacement' is open, not merged. The merged AF package states in FORMALIZATION_V1.md section 6 that verification-lattice experiments remain open.")
skip(AF, 149, "PARTIAL", "The ledger row HST-T14_NFL reconstructs the premises (permutation-closed finite function class, uniform target weighting, same performance accounting) and the relaxations (non-c.u.p. class, nonuniform ecology), and AF forbids BROKE_NFL. Missing: no proof that structured/non-permutation-invariant ecologies lie outside the NFL symmetry regime was executed - the ledger asserts the relaxation, it does not prove it.")
skip(AF, 150, "NO_EVIDENCE", "Nothing on main derives what ecology information/prior is required for a search advantage, and no acquisition/encoding cost is charged for it.")
skip(AF, 151, "PARTIAL", "The ledger row HST-T16_BLUM_SPEEDUP imports Blum correctly at its Blum-complexity-measure premises and forbids BROKE_BLUM from bounded engineering improvements. Missing: no distinction is drawn from proof-restricted speedup results, and finite-budget Pareto selection is not separated from the speedup statement.")
skip(AF, 152, "NO_EVIDENCE", "Worst-case vs average/smoothed/parameterized complexity does not appear as a barrier axis: the AF3 context chi=(S,Pi,Q,R,H,eps,delta,V) has no distributional/parameterization coordinate and no such transition is tested.")
skip(AF, 154, "PARTIAL", "AF3 registers INTERACTION_OR_QUERY as a transition class and the four F7 records include an oracle/query case. Missing: no learnability instance where traces/annotations/active queries change identifiability, and no log of the supplied information channel for such a case.")
skip(AF, 155, "NO_EVIDENCE", "The 21-row parent ledger contains Blackwell, Le Cam, information bottleneck/rate-distortion and bounded optimality, but no DEC/decision-estimation-coefficient or information-ratio parent, and no interactive-learnability parent map.")
skip(AF, 163, "PARTIAL", "FORMALIZATION_V1.md section 1 names the dimensions (precision, preparation, noise, readout, repeatability, time, energy, space, error contracts) when distinguishing physical theses from mathematical ones, but no registered `S_phys` object is defined with those coordinates anywhere on main.")
skip(AF, 164, "PARTIAL", "Only one proposal is audited at its exact assumptions (SIEGELMANN_SONTAG_ANALOG_POWER in the ledger, plus AJ12's oracle/advice and exact-real regimes). No audit of the other major hypercomputation/analog/oracle proposals exists.")
skip(AF, 165, "PARTIAL", "The ledger row SIEGELMANN_SONTAG_ANALOG_POWER pins the real-weight/advice relation at its exact assumptions, and AJ12 charges the mathematical advice content exactly (62/81 -> bits [1,0,1,1], provenance IMPORTED_EXACT_PRECISION_ADVICE). But that same ledger row's own af_residual ends 'AF7 retains physical question', i.e. the cited artifact disclaims AF7 closure; and the row also asks for readout assumptions to be measured/charged, which needs the S_phys contract of row 163 that does not exist on main. Held to the same self-disclaimer rule applied to AI0 rows 41/44.")
skip(AF, 166, "NO_EVIDENCE", "No precision/noise hostile exists. AJ12's real-parameter witness assumes exact ternary-digit readout; nothing constructs the finite operational contract under which apparent super-Turing power disappears.")
skip(AF, 168, "PARTIAL", "The mechanism exists - AF3 types SUBSTRATE_EXPANSION as a displacement and recomputes status with a nearest residual barrier rather than declaring a theorem broken (F7_ORACLE_RELATIVIZATION) - but no physical-substrate instance, and no `Comp(S)` object to update (that object is in the open PR #971).")
skip(AF, 178, "PARTIAL", "AJ11's atlas rows carry candidate_id, presentation, operational_class, capability_exact, resources and development_distance_from_S00. Missing from the row's required schema: provenance and barrier status are absent, and development is recorded as a shortest distance scalar, not as developmental edges. Also the atlas is not committed - only its canonical SHA-256 is pinned.")
skip(AF, 182, "NO_EVIDENCE", "Nothing quantifies how the atlas/frontier expands as budget, information access, interaction, approximation tolerance and substrate power change. AJ11 computes one frontier at one bound; AF3's transition records change status, not atlas extent.")
skip(AF, 183, "PARTIAL", "AJ11 reports quotient statistics at a single bound (148 classes, 6-entry capability histogram, 8-bin distance histogram). No convergence/stabilisation test across bounds exists; AJ11's own OPEN_GAPS#AJ11-LARGER-BOUNDS records larger finite bounds as unscaled.")

# ---------------- AJ (comment 5693954852) ----------------
mark(AJ, 156, A9A, [A9A+"/FREEZE_V1.md", A9A+"/HOLDOUT_CONTRACT_V1.json#benchmark_git_blob"],
     "the 11-family registry was committed alone at freeze commit `aec01b0e`, pinned by Git blob `6b9ac3095c90d74e2717671a70ad7cc18955310c`, with role POSTHOC_ADJUDICATOR_ONLY and generator/search/evaluator access false; every later holdout receipt (aj9b-aj9h) re-asserts that same blob, and each holdout's own freeze commit contains only FREEZE_V1.md + SEARCH_CONFIG_V1.json (verified with /usr/bin/git ls-tree at all five aj9b-aj9f freeze commits)")
mark(AJ, 157, A9A, [A9A+"/KNOWN_FAMILY_BENCHMARK_V1.json#families", A9A+"/RESULT_V1.json#minimum_registered_family_names"],
     "all eleven asked families are registered K01-K11 under exactly those names: neural/feed-forward, recurrent/stateful, local/shared-transform, attention/dynamic-routing, symbolic/rewrite/search, probabilistic/Bayesian, planning/control, retrieval/memory, evolutionary/population search, program synthesis, self-modifying/developmental - each with >=3 required fingerprint clauses, >=3 near-neighbour exclusions, >=2 observation tests and parent anchors")
mark(AJ, 159, A9H, [A9H+"/POSTHOC_RESULT_V1.json#families", A9H+"/RESULT_V1.json#registered_families_recovered_at_their_declared_finite_scopes"],
     "all 11 registered families reach terminal RECOVERED against fingerprints frozen in aj9a before any search, with adjudication run only after the blind outcome (`adjudication_started_after_blind_outcome: true` in every posthoc receipt); re-run on laptop-billy, aj9b-aj9h all exit 0 with `posthoc_terminal: RECOVERED`")
mark(AJ, 160, A9H, [A9H+"/RESULT_V1.json#new_holdouts_two_materially_different_routes_each", A9A+"/HOLDOUT_CONTRACT_V1.json#minimum_search_robustness_for_flagship"],
     "the flagship robustness clause is frozen in the holdout contract and met by every family: K01-K06 receipts each carry `presentations: 2` and `searches: 2` (e.g. K01 TREE_AST vs POSTFIX_STACK_ENCODING under size-layered enumeration vs semantic cost closure, both first exact at operation cost 7), and K07-K11 carry `new_holdouts_two_materially_different_routes_each: true`")
mark(AJ, 161, A9A, [A9A+"/HOLDOUT_CONTRACT_V1.json#outcome_semantics", A9H+"/FREEZE_V1.md"],
     "the frozen contract defines `NOT_RECOVERED_AT_SCOPE` as 'registered search/evidence budget ended without a candidate satisfying the frozen fingerprint; must be preserved as a scientific result', and the aj9h freeze repeats it as binding ('Failure is allowed and must return NOT_RECOVERED_AT_SCOPE'), so no run may force a family match")
mark(AJ, 162, A9A, [A9A+"/HOLDOUT_CONTRACT_V1.json#outcome_semantics", A9H+"/RESULT_V1.json#outcome_terminals_machine_distinct"],
     "all four terminals are separately defined with non-overlapping semantics (COMPILED = deliberately constructed, not blind recovery; RECOVERED = family-hidden search passes the frozen fingerprint; PREDICTED_SELECTED = pressure/regime predicted before reveal, then recovered; NOT_RECOVERED_AT_SCOPE = budget exhausted) and `check_aj9h.py` asserts the terminal set has not drifted; every AJ9 receipt records `predicted_selected: NOT_CLAIMED`")
mark(AJ, 166, A10, [A10+"/RESULT_V1.json#unknown_channel_exercised", A10+"/POSTHOC_RESULT_V1.json#candidates.T232"],
     "the channel exists and is exercised: T232 receives `registered_taxonomy: UNKNOWN_MORPHOLOGY` with `registered_family: null` (`check_aj10.py` re-run on laptop-billy, exit 0)")
mark(AJ, 167, A10, [A10+"/FREEZE_V1.md", A10+"/HELDOUT_ENV_V1.json#created_after_freeze_commit"],
     "FREEZE_V1.md freezes the generative substrate, both search procedures, the post-hoc taxonomy/novelty protocol (five steps), the five novelty levels and the five terminals; the held-out environment records `created_after_freeze_commit: cbd5522018c0c9e8900df27f7b821b51dda897f5`, so the run is prospective")
mark(AJ, 168, A10, [A10+"/HELDOUT_ENV_V1.json#taxonomy_visible_to_search", A10+"/RESULT_V1.json#blind_source_forbidden_hits"],
     "the held-out task H1 carries `family_labels_present: false` and `taxonomy_visible_to_search: false`, and the source audit returns `blind_source_forbidden_hits: []`")
mark(AJ, 169, A10, [A10+"/EVALUATED_CANDIDATES_V1.json#capability_evaluated_before_taxonomy"],
     "`capability_evaluated_before_taxonomy: true`, with capability (8/8 protected cases exact), raw two-coordinate resource vectors and developmental profile (FIXED) committed for both candidates before the registry is read")
mark(AJ, 170, A10, [A10+"/POSTHOC_RESULT_V1.json#strongest_parent_reduction_ran_after_generation_and_evaluation"],
     "`strongest_parent_reduction_ran_after_generation_and_evaluation: true` and `taxonomy_ran_after_pre_taxonomy_evaluation: true`; the reduction then maps T232 to a classical finite truth/lookup table and E4 to finite program synthesis")
mark(AJ, 171, A10, [A10+"/FREEZE_V1.md", A10+"/RESULT_V1.json#novel_replication_policy"],
     "the frozen protocol requires it - 'A claimed novel form would require an independent replication' - and the receipt records `novel_replication_policy: REQUIRED_IF_NOVEL; not triggered because no novel form is claimed`, with `NOVEL_MI_DISCOVERED` in forbidden_promotions")
mark(AJ, 172, A10, [A10+"/POSTHOC_RESULT_V1.json#candidates", A10+"/RESULT_V1.json#novelty_levels_recorded"],
     "both candidates are scored separately on all five asked levels (implementation, morphology_architecture, algorithmic_mechanism, computational_class, capability_profile) - e.g. T232 is PARENT_REDUCED_KNOWN on morphology/mechanism/class but NOT_ESTABLISHED on implementation")
mark(AJ, 173, A10, [A10+"/POSTHOC_RESULT_V1.json#unknown_policy", A10+"/POSTHOC_RESULT_V1.json#overall_morphology_disposition"],
     "the frozen policy preserves the pre-taxonomy UNKNOWN record without retroactive rewriting, and the overall disposition is `CANNOT_IDENTIFY_UNIQUE_MORPHOLOGY_FROM_CAPABILITY_AND_RAW_PARETO_RESOURCES` rather than a forced novelty or family claim")
mark(AJ, 179, A11, [A11+"/RESULT_V1.json#bounded_scope.presentations", A11+"/check_aj11.py"],
     "`check_aj11.py` enumerates all 260 registered organizations (4 stateless plus all 256 one-bit feedback step tables) with `assert len(cs)==260`; re-run on laptop-billy, exit 0")
mark(AJ, 180, A11, [A11+"/RESULT_V1.json#operational_class_size_histogram"],
     "operational duplicates are collapsed by exact reachable-product all-word equivalence over 33,670 pair checks (1,624 equivalent pairs), giving 148 classes: 144 singletons and four 29-member classes")
mark(AJ, 181, A11, [A11+"/RESULT_V1.json#atlas_sha256", A11+"/THEORY.md#Finite registered universe"],
     "the complete atlas has one row per presentation carrying operational class, exact five-coordinate capability vector, raw (state_cells, truth_rows) resources and developmental distance; all 260 are reachable from seed S00 with max shortest distance 7, and the canonical compact JSON SHA-256 `09a99f29d2d349d7f28855d3a32776667c65cd1a707ea89129fd77c3328a16ed` reproduced exactly on laptop-billy")
mark(AJ, 182, A11, [A11+"/RESULT_V1.json#pareto_frontier_candidate_ids", A11+"/RESULT_V1.json#pareto_objective"],
     "the exact Pareto frontier under the seven-coordinate partial order (five task-failure coordinates + state_cells + truth_rows, no scalarization) is [M000, M001, M002, M043, M169], asserted as `front==[0,1,2,43,169]` and reproduced on laptop-billy")
mark(AJ, 183, A11, [A11+"/check_aj11.py", A11+"/RESULT_V1.json#bounded_terminal"],
     "the terminal is gated: `COMPLETE_GMI_ATLAS_AT_BOUND_B` is emitted only after the checker's completeness assertions all pass (260 enumerated, 148 classes, 33,670 pair checks, 1,624 equivalent pairs, capability constant within every class, canonical digest match and exact frontier); any drift aborts before the receipt is written")
mark(AJ, 187, A11, [A11+"/RESULT_V1.json#unbounded_boundary"],
     "`syntax_programs: EFFECTIVELY_ENUMERABLE_UNDER_REGISTERED_FINITE_ALPHABET` is held apart from `semantic_equivalence: UNDECIDABLE_IN_GENERAL_AT_TURING_COMPLETE_SCOPE`, with THEORY.md giving the reason a terminating semantic catalogue would decide program equivalence")
mark(AJ, 188, A11, [A11+"/RESULT_V1.json#unbounded_boundary.nontrivial_semantic_properties", A11+"/THEORY.md#Unbounded boundary"],
     "`nontrivial_semantic_properties: RICE_BOUNDARY_APPLIES_AT_STANDARD_SCOPE` and THEORY.md preserves both the program-equivalence undecidability and Rice barriers as parent mathematics rather than displacing them")
mark(AJ, 189, A11, [A11+"/RESULT_V1.json#unbounded_boundary.required_scientific_policy", A11+"/THEORY.md#Unbounded boundary"],
     "the required policy is recorded as `OPEN_GENERATIVITY_PLUS_BLIND_RECOVERY_PLUS_PROSPECTIVE_UNKNOWN_NOT_TERMINATING_SEMANTIC_CATALOGUE`, itemised in THEORY.md as open-ended generativity, explicit undecidability/unknown terminals, AJ9 blind known-family recovery, AJ10 prospective UNKNOWN discovery and scoped prediction/replication")
mark(AJ, 190, A11, [A11+"/RESULT_V1.json#forbidden_terminal"],
     "`forbidden_terminal: ALL_MACHINE_INTELLIGENCES_COMPLETELY_CLASSIFIED`, with the bounded terminal explicitly restricted to the frozen finite scope in README.md and THEORY.md")
mark(AJ, 194, A12, [A12+"/RESULT_V1.json#assumption_tags"],
     "all five asked classes are used as the tag vocabulary: finite_carriers_and_extensional_equality=MATHEMATICAL_FOUNDATION, classical_decidable_finite_reasoning=LOGIC/METATHEORY, which_processes_are_admitted=PHYSICAL_SUBSTRATE_LAW, unit_and_vector_costs=RESOURCE_MODEL, protected_task_or_utility=VALUE/REQUIREMENT_INPUT (`check_aj12.py` re-run on laptop-billy, exit 0)")
mark(AJ, 195, A12, [A12+"/FREEZE_V1.md#Style A", A12+"/RESULT_V1.json#formalization_styles"],
     "the compact core (carrier B={0,1}, four unary transformations, identity/composition closure, exact observation, operational quotient) is expressed twice - `FINITE_SET_RELATION_STYLE` (graph relations, relational composition) and `EXPLICIT_TYPED_ALGEBRAIC_PROCESS_STYLE` (typed records, tuple substitution) - under an explicit bijection frozen before the run")
mark(AJ, 196, A12, [A12+"/RESULT_V1.json#theorem_invariance", A12+"/RESULT_V1.json#composition_transfer_checks"],
     "invariance is tested at theorem level, not notation: all 16 ordered compositions agree across styles, identity laws agree, and three preparations under two registered tests give identical response signatures and the identical operational quotient [[p0,p2],[p1]]")
mark(AJ, 197, A12, [A12+"/RESULT_V1.json#alternative_substrate_witnesses", A12+"/RESULT_V1.json#standard_effective_substrate"],
     "standard effective computation is the registered baseline and two alternative regimes are charged explicitly: an oracle/advice stream yielding bits [1,0,1,1] tagged `IMPORTED_ORACLE_OR_ADVICE_POWER`, and an exact real parameter `62/81` whose ternary digits recover the same four bits tagged `IMPORTED_EXACT_PRECISION_ADVICE`")
mark(AJ, 198, A12, [A12+"/RESULT_V1.json#physical_hypercomputation", A12+"/FREEZE_V1.md"],
     "`physical_hypercomputation: EMPIRICAL_OPEN__NO_REPRODUCIBLE_EVIDENCE_REGISTERED_HERE`, made mandatory by the freeze and backed by `PHYSICAL_HYPERCOMPUTATION_PROVED` / `SUPER_TURING_POWER_FROM_NOTHING` in forbidden_promotions")
mark(AJ, 199, A12, [A12+"/RESULT_V1.json#metatheory_boundaries", A12+"/THEORY.md#Metatheory boundary"],
     "`metatheory_boundaries: [GODEL_INCOMPLETENESS_SCOPE_PRESERVED, TARSKI_OBJECT_LANGUAGE_METALANGUAGE_BOUNDARY_PRESERVED]`, with `SELF_JUSTIFYING_ALL_TRUTH_FOUNDATION` and `UNIQUE_TRUE_FOUNDATION_PROVED` in forbidden_promotions")
mark(AJ, 214, A13, [A13+"/RESULT_V1.json#terminal", A13+"/THEORY.md"],
     "`terminal: FOUNDATION_RELATIVE_GMI_CORE_STABLE_AT_REGISTERED_SCOPE` with `criteria_satisfied: 6` against the six conjuncts the row's code block states, consuming AJ1's loss witnesses and AJ5/AJ12 presentation-invariance evidence, and rejecting all six one-condition hostiles (`hostile_cases_rejected: 6`); `check_aj13.py` re-run on laptop-billy, exit 0")
mark(AJ, 215, A13, [A13+"/RESULT_V1.json#forbidden_terminal", A13+"/RESULT_V1.json#hostiles.absolute_promotion"],
     "`forbidden_terminal: ABSOLUTE_BOTTOM_OF_MATHEMATICS_OR_REALITY_PROVEN`, enforced rather than merely declared: the `absolute_promotion` hostile is rejected with reason `ABSOLUTE_BOTTOM_PROMOTION_FORBIDDEN`")

skip(AJ, 158, "PARTIAL", "Per-holdout source audits do exist and work: aj9b-aj9h each report blind_source_forbidden_hits: [], and a planted positive ('k08 retrieval/memory' appended to aj9h's blind_recovery_v1.py) is correctly detected (RuntimeError: blind source leaks family knowledge: ['k08','retrieval/memory']) while the clean run exits 0. But the frozen contract's own config auditor is broken: check_aj9a.py exits 1 on main because audit_config() misses 4 of its own 11 hostiles - {'ops':['dense_layer']}, {'ops':['self_attention']}, {'ops':['bayes_update']}, {'ops':['genetic_algorithm']} - since walk() only scans string values held directly under a dict key and never scans strings inside list-valued fields, which is exactly how operator lists are supplied. No CI workflow runs check_aj9a.py, and the committed RESULT_V1.json still asserts hostile_configs_rejected: 11 and status GREEN. Family-specific operator/cost-bonus smuggling is therefore not demonstrably excluded for every holdout.")
for n in range(257, 264):
    skip(AJ, n, "NO_EVIDENCE", "No aj15 package exists under research/ on main and no merged PR title mentions AJ15. AJ9/AJ10/AJ11 are separate microscopes, not an end-to-end flagship experiment; in particular no ecology/resource regime is registered in which a held-out family is predicted not to appear (every AJ9 receipt records predicted_selected: NOT_CLAIMED).")

# ---------------- emit ----------------
reps = []
nots = []
already_closed = []

def fresh_state(c, n):
    """Live state of an adjudicated line: open, or closed (possibly with an
    evidence suffix appended by another lane). Any other line is a defect."""
    l = lines[c][n]
    if l.startswith("- [ ] "):
        return "open", l, None
    if l.startswith("- [x] "):
        base = l[6:].split(u" — ✅ `", 1)[0]
        return "closed", "- [ ] " + base, l
    raise AssertionError("not a checkbox at %s:%s: %r" % (c, n, l))

for c, n, pkg, ev, sent in MARK:
    state, old, live = fresh_state(c, n)
    if state == "closed":
        already_closed.append({"comment_id": c, "old_at_round_1": old,
                               "live_state": live, "round_1_status": "EARNED_BY_MERGED_EVIDENCE",
                               "note": "Round-1 EARNED row; the live comment already shows it checked (with this package's evidence suffix). Recorded rather than re-emitted."})
        continue
    cnt = bodies[c].count(old)
    assert cnt == 1, "old not unique (%d) in %s: %r" % (cnt, c, old)
    new = "- [x] " + old[6:] + " — ✅ `" + pkg.split("/")[-1] + "` " + sent + "."
    anc = anchor_for(c, n)
    acnt = bodies[c].count(anc)
    assert acnt == 1, "anchor not unique (%d) in %s: %r" % (acnt, c, anc)
    reps.append({"comment_id": c, "anchor": anc, "old": old, "new": new,
                 "evidence_paths": ev, "status": "EARNED_BY_MERGED_EVIDENCE"})

for c, n, st, reason in SKIP:
    state, old, live = fresh_state(c, n)
    if state == "closed":
        already_closed.append({"comment_id": c, "old_at_round_1": old,
                               "live_state": live, "round_1_status": st,
                               "note": "Round-1 %s row; the live comment already shows it checked (closed upstream by another lane). Recorded rather than re-emitted." % st})
        continue
    assert bodies[c].count(old) == 1, "skip row not unique in %s: %r" % (c, old)
    nots.append({"comment_id": c, "anchor": anchor_for(c, n), "old": old, "status": st, "reason": reason})

# every currently-open row must be adjudicated exactly once; every adjudicated
# line that is no longer open must be a checked row (recorded above), nothing else
seen = {}
for c, n, *_ in MARK: seen.setdefault(c, set()).add(n)
for c, n, *_ in SKIP:
    assert n not in seen.get(c, set()), "double-adjudicated %s:%s" % (c, n)
    seen.setdefault(c, set()).add(n)
for c in (AI, AI8, AF, AJ):
    openrows = {i for i, l in enumerate(lines[c]) if l.startswith("- [ ]")}
    missing = openrows - seen.get(c, set())
    extra = seen.get(c, set()) - openrows
    assert not missing, "unadjudicated rows in %s: %s" % (c, sorted(missing))
    bad_extra = [i for i in extra if not lines[c][i].startswith("- [x]")]
    assert not bad_extra, "phantom rows in %s: %s" % (c, sorted(bad_extra))

out = {"schema": "GMI_ISSUE_COMMENT_RECONCILIATION_V1", "issue": 833,
       "replacements": reps, "not_marked": nots,
       "already_closed_upstream": already_closed}
dest = os.path.join(HERE, "ISSUE_833_COMMENT_RECONCILIATION_V1.json")
os.makedirs(os.path.dirname(dest), exist_ok=True)
io.open(dest, "w", encoding="utf-8").write(json.dumps(out, indent=2, ensure_ascii=False) + "\n")

from collections import Counter
print("marked %d  not_marked %d  already_closed_upstream %d" % (len(reps), len(nots), len(already_closed)))
for c in (AI, AI8, AF, AJ):
    m = sum(1 for r in reps if r["comment_id"] == c)
    h = Counter(x["status"] for x in nots if x["comment_id"] == c)
    print(c, "EARNED=%d" % m, dict(h))
print("wrote", dest)

