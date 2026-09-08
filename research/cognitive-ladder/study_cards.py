"""Study cards: the #144 classification every result-bearing artifact must carry.

Publication constitution SzeChunYiu/ORION-OCM#144 §22 requires each result-bearing
task to declare, before it produces anything: the general scientific question it
answers without project vocabulary, its evidence class E0-E5, its contribution
level L0-L6, its decisive causal question, the strongest parent that could
explain the effect, an audit of where the useful structure actually came from,
its relevance to the lifetime scaling objects, and the outcome that would kill or
narrow the mechanism rather than prompt a friendlier benchmark.

These cards are written to be uncomfortable.  A card whose kill criterion cannot
fire, or whose prior-information audit credits supplied structure as learned
competence, is a defective card and the study should not run.

Generated output: ``STUDY_CARDS_V1.json`` and ``STUDY_CARDS_V1.md``.
"""

from __future__ import annotations

import json
import pathlib

E_CLASSES = ("E0", "E1", "E2", "E3", "E4", "E5")
L_LEVELS = ("L0", "L1", "L2", "L3", "L4", "L5", "L6")

CARDS = [
{
 "study_id": "CL-PROTOCOL-V1",
 "artifact": "docs/spec/COGNITIVE_LADDER_PROTOCOL_V1.md, docs/spec/COGNITIVE_LADDER_SCALING_V1.md",
 "scientific_question": (
   "How can a claim that a machine reuses learned competence be identified causally, rather than "
   "asserted from a benchmark table? The question is general: any system claiming lifelong reuse "
   "faces the same confound between knowledge and infrastructure."),
 "evidence_class": "E0",
 "contribution_level": "L0",
 "level_justification": (
   "A protocol is not a result. It discharges no empirical requirement and may not be cited as "
   "evidence for any mechanism."),
 "decisive_causal_question": "none; a protocol has no treatment",
 "strongest_parent_attack": (
   "Pre-registration, sham controls, MDL model selection and cluster-randomised analysis all "
   "predate this document. The assembly is the only thing offered, and assembly is not novelty."),
 "prior_information_audit": (
   "Entirely authored. Nothing here is learned. The devices are imported from experimental "
   "medicine, information theory and cryptography and are attributed in the protocol's parents table."),
 "scaling_relevance": (
   "Defines N, k, B_N, B_k, D, Q and the five cost coordinates, and introduces the crossover query "
   "count as the endpoint that survives the index-construction hostile."),
 "kill_criterion": (
   "If the placebo and cache arms turn out to be unconstructible for a rung, the identification "
   "strategy fails for that rung and the rung reports no causal claim at all."),
 "discharges_144": ["§4 E-class discipline", "§8 scale variables and growth study", "§10 analysis-plan requirement", "§12 ablation standard (specified, not executed)"],
 "outstanding_144": ["§2 editorial significance packet", "§13 frozen environment before protected execution", "§17 red-team simulation"],
},
{
 "study_id": "CL-ESCALATION-PILOT-V1",
 "artifact": "escalation.py, escalation_worlds.py, escalation_generator.py, escalation_parents.py, run_escalation.py",
 "scientific_question": (
   "When a learning system stops making progress, can it tell the difference between needing more "
   "search, needing different evidence, and needing a different representation? Every adaptive "
   "system faces this, and the common default -- escalate when stuck -- is known to be wrong."),
 "evidence_class": "E2",
 "contribution_level": "L1",
 "level_justification": (
   "A controlled mechanism, not a causal one. The worlds and the diagnosis policy share an author, "
   "so the accuracy figure is calibration. Promoting this to L2 would be exactly the error #144 §3 "
   "forbids."),
 "decisive_causal_question": (
   "Treatment: requiring an exhibited obstruction witness before escalating. Parent: an exact "
   "repair planner that takes the cheapest repair admitting a fit, with no witness requirement. "
   "Outcome: minimum-sufficient-level accuracy and false-escalation rate. Units: generated worlds, "
   "clustered by defect type. Predicted control behaviour: on the budget-exhaustion world the "
   "governed policy must NOT escalate while the timeout parent must."),
 "strongest_parent_attack": (
   "The binary jump-versus-no-jump decision is already closed against a fully-resourced parent: "
   "ORION V1's zero-error Jump study recorded a protected incremental gap of exactly zero, and "
   "ME-X2 recorded the parent federation strictly winning on minimum-escalation accuracy. Only the "
   "false-escalation asymmetry replicated across ME-X2 and its fresh-seed repeat. This pilot is "
   "therefore an attempt on a narrower target, and the exact repair planner is the parent that must "
   "be beaten."),
 "prior_information_audit": (
   "The escalation level ladder is AUTHORED. The registered repairs are AUTHORED. The worlds' "
   "defect types are AUTHORED and the generator instantiates the defect the policy is built to "
   "detect. Nothing in this pilot is learned. The only quantity that is not supplied is which "
   "level a given world carries, and the generator determines that too. This is the FAILURE_LEDGER "
   "pattern STRUCTURALLY_DETERMINED_REGISTERED_CLAUSE and it caps the evidence class at E2."),
 "scaling_relevance": (
   "Escalation decisions are charged as search expansions and checker calls, feeding C_query and "
   "C_revision. A false escalation is a revision-cost event, so the false-escalation rate is a "
   "direct input to the lifetime revision-cost curve."),
 "kill_criterion": (
   "If the exact repair planner matches both minimum-sufficient-level accuracy and false-escalation "
   "rate on worlds generated by a process independent of this policy's author, the governed "
   "escalation mechanism is dropped from the flagship story and reported PARENT_SUFFICIENT. The "
   "response is not a new world family."),
 "discharges_144": ["§4 pilot declared as pilot, not promoted", "§6 strongest parent named and implemented before the claim", "§11 parent-favouring and no-escalation control worlds included", "§12 functional-replacement ablation rather than removal alone"],
 "outstanding_144": ["§4 E3 frozen confirmatory run", "§11 independently authored validation subset -- the binding gap", "§10 effect sizes and intervals", "§15 fresh-host replication"],
},
{
 "study_id": "CL-FAILURE-PILOT-V1",
 "artifact": "failure.py, failure_worlds.py, failure_parents.py, run_failure.py",
 "scientific_question": (
   "Can a system learn from a failure in a way that generalises to related situations without "
   "becoming permanently closed to the possibility that the failure was circumstantial?"),
 "evidence_class": "E2",
 "contribution_level": "L1",
 "level_justification": "Mechanism under control conditions; no causal claim on a protected draw.",
 "decisive_causal_question": (
   "Treatment: keying exclusions on the assumption set rather than on task identity. Parent: a "
   "nogood store that excludes on any failure. Outcome: repeated dead ends avoided AND correct "
   "reopening after a registered regime change. Units: world families. Predicted control "
   "behaviour: after the regime reverts, the transcript parent stays shut and the governed store "
   "reopens."),
 "strongest_parent_attack": (
   "The failure-epistemology closure already assigned this mechanism to TMS nogoods plus "
   "responsibility and froze the strongest-parent incremental gap at 0 of 32 BEFORE execution. Its "
   "own falsifier is that ORION beats the strong parent on a meaningful protected coordinate. The "
   "expectation for this pilot is therefore PARENT_SUFFICIENT."),
 "prior_information_audit": (
   "The failure-cause taxonomy is AUTHORED. The assumption sets are AUTHORED. The checker is an "
   "exact oracle and supplies the refutation; the machine does not discover that a method is wrong, "
   "it is told. Only the exclusion scope and the reopening decision are computed."),
 "scaling_relevance": (
   "Feeds ME-SCALE-5, failure recurrence against experience, and contributes to C_revision through "
   "reopening cost."),
 "kill_criterion": (
   "If the cause-blind nogood parent matches on both repeated-work avoidance and reopening, scoped "
   "failure knowledge is merged into the nogood parent and removed as a separate mechanism."),
 "observed_outcome": (
   "The truth-maintenance parent, given full strength, ties the governed store exactly on four of "
   "seven worlds and separates only on the three where the failure's cause carries no information "
   "about correctness: a spent budget, a probe set that provably could not discriminate, and a "
   "defective checker. The transcript parent, which keys on task identity, is broken shut on both "
   "scope-recovery worlds. Every arm is handed a correct diagnosis by the world, so the harder "
   "question -- whether a machine can tell an evaluator defect from a genuine refutation -- is "
   "untouched."),
 "discharges_144": ["§6 parent named with its prior negative preserved", "§11 hostile families including evaluator defect and non-identifying probe", "§12 replacement-by-parent ablation"],
 "outstanding_144": ["§4 E3 confirmatory run", "§10 independent-unit definition and intervals", "§15 replication"],
},
{
 "study_id": "CL-SCALING-PILOT-V1",
 "artifact": "scaling.py, scaling_arms.py, run_scaling.py",
 "scientific_question": (
   "As a system accumulates competence, does the work it does per task track the part of its "
   "memory it actually uses, or the total size of that memory? This is the question behind every "
   "claim that a large knowledge store can be queried cheaply."),
 "evidence_class": "E1",
 "contribution_level": "L0",
 "level_justification": (
   "Engineering calibration of the meters. It establishes that k is instrumented and that index "
   "construction is charged. It establishes nothing about cognition."),
 "decisive_causal_question": (
   "Treatment: scoped indexing with dependency links. Parent: a plain database index. Outcome: "
   "k(N), total work including build and maintenance, and the crossover query count. Units: scale "
   "points with frozen probe families. Predicted control behaviour: the global-scan ablation's k "
   "must track N."),
 "strongest_parent_attack": (
   "An ordinary database index answers queries without scanning its contents. It is expected to "
   "match on k(N) and on query work. The only coordinate where a residual could survive is stale "
   "detection after a shared support is revoked, which an index does not track."),
 "prior_information_audit": (
   "The index key is family identity, which is SUPPLIED. The store's scoping is AUTHORED. No "
   "routing is learned. Crediting sparse query work to cognition here would be laundering; it is a "
   "property of the supplied key."),
 "scaling_relevance": "This is the ME-SCALE-1 instrument itself: N, k, B_N, B_k, index build and maintenance, crossover.",
 "kill_criterion": (
   "If k grows near-linearly in N, or the crossover query count is not reached within the "
   "registered lifetime, the sparse-cognition claim is dropped and the terminal is "
   "INDEX_MAINTENANCE_DOMINATES."),
 "observed_outcome": (
   "The indexed parent matches the machine arm EXACTLY on k, on k/N, on query work and on bytes at "
   "every registered scale, so the terminal is PARENT_SUFFICIENT and sparse lookup under a supplied "
   "family key is confirmed to be a property of the key. Every hostile fired: the uninstrumented "
   "path returned CANNOT_CHECK, the rebuild hostile showed identical per-query k with far worse "
   "total work, the cache parent answered none of the probes while carrying the largest state, and "
   "the globally shared revocation produced a cone growing with N while the local one stayed "
   "constant at two. The one coordinate on which the parent has no answer at all is which objects "
   "went stale after a support was withdrawn."),
 "discharges_144": ["§8 scale variables instrumented", "§8 hidden index work measured separately", "§12 global-scan functional replacement"],
 "outstanding_144": ["§8 the 1x/3x/10x/30x growth study on the real runtime", "§8 related versus unrelated acquisition arms", "§6 neural memory parent"],
},
{
 "study_id": "CL-ATLAS-V1",
 "artifact": "ORION_CONCEPT_VALIDATION_ATLAS_V1.json and .md",
 "scientific_question": (
   "Which of a research programme's own theoretical concepts survive contact with executable "
   "experiments and strongest-parent subtraction? The general form of this question applies to any "
   "long-running architecture programme."),
 "evidence_class": "E0",
 "contribution_level": "L0",
 "level_justification": "A register of hypotheses and preserved terminals. It grants no status to anything it lists.",
 "decisive_causal_question": "none; the atlas is bookkeeping",
 "strongest_parent_attack": "not applicable",
 "prior_information_audit": (
   "Every preserved terminal is quoted from an existing receipt in ORION, ORION-V2 or ORION-OCM and "
   "is attributed. Nothing in the atlas is a new result. Three concepts are dropped and three merged "
   "on the strength of those existing negatives, not on new evidence."),
 "scaling_relevance": "maps each concept to the lifetime scaling signature it would serve, or to none",
 "kill_criterion": (
   "A concept whose falsifier fires is moved to REFUTED or PARENT_SUFFICIENT and removed from the "
   "flagship story. The atlas exists to make that removal cheap."),
 "discharges_144": ["§7 prior-information audit per concept", "§6 strongest parent per concept", "§18 kill and narrow rules made concept-specific"],
 "outstanding_144": ["§21 PUB-D2, D4, D5, D7, D8, D9, D10 templates"],
},
{
 "study_id": "CL-LIBDISC-E5",
 "artifact": "libdisc.py, libdisc_discovery.py, libdisc_parents.py, libdisc_arms.py, run_libdisc.py",
 "scientific_question": (
   "How does a system discover reusable structure from a handful of successful episodes whose "
   "surfaces all differ? This is the central question behind library learning, and it is the one "
   "place in this programme where a positive result has not yet been ruled out."),
 "evidence_class": "E2",
 "contribution_level": "L1",
 "level_justification": (
   "The world, the schema language and the discovery mechanism share an author. A causal reuse "
   "result here would be a controlled mechanism, not a general one."),
 "decisive_causal_question": (
   "Treatment: anti-unification over normalised proof steps plus semantic-equivalence clustering. "
   "Parent: DreamCoder-style library induction and Stitch-style corpus compression over the same "
   "episodes. Outcome: schemas admitted by an independent checker, and search on fresh tasks after "
   "a real process restart. Units: episode families. Predicted control behaviour: the flat-mining "
   "ablation must find nothing, reproducing the checked NO_METHOD_ACQUIRED negative."),
 "strongest_parent_attack": (
   "Library learning has solved this class of problem since DreamCoder and Stitch. If either finds "
   "the same schemas from the same traces, the terminal is PARENT_SUFFICIENT. The prior in this "
   "programme is that it will."),
 "prior_information_audit": (
   "The clause grammar, the resolution calculus and the step-schema language are AUTHORED. The "
   "checker enumerates assignments and is exact and independent. What is NOT supplied is which "
   "schema recurs, or any task identity that would reveal it; the generator asserts that flat "
   "fragments are pairwise distinct so that no surface shortcut exists."),
 "scaling_relevance": (
   "Feeds ME-SCALE-2 and ME-SCALE-6: whether related-task acquisition cost falls with experience, "
   "and whether transfer benefit is a witnessed invocation rather than retrieval."),
 "kill_criterion": (
   "If a library-learning parent recovers the same schemas, or if no schema survives independent "
   "checking, step-level discovery is dropped as a distinct mechanism and reported "
   "PARENT_SUFFICIENT. Lowering the repeated-support threshold to manufacture a pool is explicitly "
   "forbidden by the diagnosis this experiment is built on."),
 "discharges_144": ["\u00a75 one decisive causal claim", "\u00a76 strongest parent implemented before the claim", "\u00a712 removal and functional-replacement ablation", "\u00a713 real process-boundary custody"],
 "outstanding_144": ["\u00a74 E3 frozen confirmatory run", "\u00a711 independently authored validation subset", "\u00a715 fresh-host replication"],
},
{
 "study_id": "CL-SUPPORT-E6",
 "artifact": "support.py, support_arms.py, run_support.py",
 "scientific_question": (
   "When several pieces of evidence each independently justify a conclusion, how does a system find "
   "out what that conclusion actually rests on? Removing them one at a time cannot tell it."),
 "evidence_class": "E1",
 "contribution_level": "L0",
 "level_justification": (
   "Computing minimal supporting environments is what an ATMS has done since 1986. Anything here is "
   "engineering calibration unless adaptive selection reaches the same answer at materially lower "
   "intervention cost."),
 "decisive_causal_question": (
   "Treatment: adaptive selection of group ablations under a charged budget. Parent: ATMS "
   "minimal-environment labelling, run both given the justifications and required to discover them. "
   "Outcome: support-family precision and recall against a powerset oracle, per intervention spent. "
   "Predicted control behaviour: leave-one-out must fail exactly on the redundant families."),
 "strongest_parent_attack": (
   "An ATMS handed the justifications needs no interventions at all and wins outright; that row is "
   "reported as the gifted ceiling. The only fair comparison is when it must discover them, and "
   "even then minimal-support machinery is parent-owned and no novelty is claimed for it."),
 "prior_information_audit": (
   "The evidence-to-method structure is AUTHORED. The powerset oracle is exhaustive and is used "
   "only by the scorer. What is not supplied is which subsets are minimal supports; that must be "
   "paid for in interventions."),
 "scaling_relevance": (
   "Feeds ME-SCALE-4: whether revision work grows more slowly than N once support is discovered "
   "rather than declared."),
 "kill_criterion": (
   "If the ATMS parent required to discover justifications matches the adaptive arm on precision, "
   "recall and interventions, the mechanism is merged into that parent and reported "
   "PARENT_SUFFICIENT."),
 "discharges_144": ["\u00a76 strongest parent named and run in both its gifted and fair configurations", "\u00a711 negative family where no evidence is load-bearing", "\u00a712 replacement-by-parent ablation"],
 "outstanding_144": ["\u00a74 E3 frozen confirmatory run", "\u00a78 scale sweep beyond the powerset-tractable bound", "\u00a710 intervals on the intervention counts"],
},
]


def main() -> int:
    here = pathlib.Path(__file__).parent
    for c in CARDS:
        assert c["evidence_class"] in E_CLASSES, c["study_id"]
        assert c["contribution_level"] in L_LEVELS, c["study_id"]
        assert c["kill_criterion"], c["study_id"]
        assert c["prior_information_audit"], c["study_id"]
    (here / "STUDY_CARDS_V1.json").write_text(
        json.dumps({"schema": "orion.study-card.v1", "constitution": "SzeChunYiu/ORION-OCM#144",
                    "cards": CARDS}, indent=2) + "\n")
    lines = ["# STUDY_CARDS_V1\n",
             "**GENERATED FILE — edit `study_cards.py`, then run `python study_cards.py`.**\n",
             "Required by publication constitution #144 §22. Every result-bearing artifact in this "
             "lane declares its evidence class, contribution level, decisive causal question, "
             "strongest parent, prior-information audit and kill criterion before it produces "
             "anything.\n",
             "| study | artifact | evidence | level |", "|---|---|---|---|"]
    for c in CARDS:
        lines.append(f"| {c['study_id']} | `{c['artifact'].split(',')[0]}` | "
                     f"**{c['evidence_class']}** | **{c['contribution_level']}** |")
    lines.append("")
    for c in CARDS:
        lines.append(f"## {c['study_id']}\n")
        lines.append(f"**Artifact.** `{c['artifact']}`\n")
        lines.append(f"**Scientific question.** {c['scientific_question']}\n")
        lines.append(f"**Evidence class.** {c['evidence_class']} · "
                     f"**Contribution level.** {c['contribution_level']}\n")
        lines.append(f"**Why not a higher level.** {c['level_justification']}\n")
        lines.append(f"**Decisive causal question.** {c['decisive_causal_question']}\n")
        lines.append(f"**Strongest-parent attack.** {c['strongest_parent_attack']}\n")
        lines.append(f"**Prior-information audit.** {c['prior_information_audit']}\n")
        lines.append(f"**Scaling relevance.** {c['scaling_relevance']}\n")
        if c.get("observed_outcome"):
            lines.append(f"**Observed outcome.** {c['observed_outcome']}\n")
        lines.append(f"**Kill criterion.** {c['kill_criterion']}\n")
        lines.append("**Discharges (#144).** " + "; ".join(c["discharges_144"]) + "\n")
        lines.append("**Still outstanding (#144).** " + "; ".join(c["outstanding_144"]) + "\n")
    (here / "STUDY_CARDS_V1.md").write_text("\n".join(lines))
    print(f"wrote STUDY_CARDS_V1.json and .md: {len(CARDS)} cards")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
